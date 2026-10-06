"""Preview van expliciet opgeslagen CAD, met oorspronkelijke topo en KLIC."""
import math
from pathlib import Path

def preview(data,out):
 import ezdxf,numpy as np,matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 from matplotlib.collections import LineCollection
 from matplotlib.patches import Polygon as MplPolygon
 from ezdxf import path as ep,bbox
 from shapely.geometry import Polygon
 cfg=data['config'];main=ezdxf.readfile(data['drawing']['file']);klic=ezdxf.readfile(cfg.get('klic_display_dxf',cfg['klic_dxf']));topo=ezdxf.readfile(cfg['topo_dxf']);region=Polygon(main.entitydb[cfg['boundary_handle']].get_points('xy'));station=bbox.extents([main.entitydb[cfg['station_handle']]])
 x0,y0,x1,y1=region.bounds;cx,cy=station.center.x,station.center.y
 bounds={'Overzicht':(x0-5,x1+5,y0-5,y1+5),'Stationsdetail':(cx-16,cx+104,cy-50,cy+50),'Stationsuitloop':(cx-10,cx+42,cy-36,cy+14)};out=Path(out)
 for name,bb in bounds.items():
  fig,ax=plt.subplots(figsize=(16,12),dpi=190);ax.set_xlim(bb[:2]);ax.set_ylim(bb[2:]);ax.set_aspect('equal');ax.ticklabel_format(useOffset=False,style='plain');ax.tick_params(labelsize=6)
  def inside(p):return bb[0]<=p[0]<=bb[1] and bb[2]<=p[1]<=bb[3]
  def draw(doc,source):
   lines=[];colors=[];widths=[];texts=[];front={}
   def walk(e,inherit=7,depth=0,parent_layer=None,foreground=False):
    typ=e.dxftype();layer=e.dxf.layer
    if layer=='0' and parent_layer:layer=parent_layer
    if source=='topo':col='#c5c9cc';lw=.4
    elif source=='klic':
     if layer in ['E_LV_MAP_CABLE_LS','E_LV_MAP_CABLE_LSOV']:col='#697078';lw=.8
     elif layer=='E_LV_CONNECTION_CABLE_LS':col='#adb1b5';lw=.35
     elif layer in ['E_LV_MAP_CABLE_JOINT_LS','E_LV_MAP_CABLE_END_JOINT_LS','E_LV_STATION','LVM_STATION_LOCATION','E_LV_REFERENCE']:col='#727579';lw=.5
     else:return
    else:
     ci=e.dxf.get('color',256)
     if ci==256:ci=doc.layers.get(layer).color
     if ci==0:ci=inherit
     rgb=ezdxf.colors.aci2rgb(ci if 0<ci<256 else 7);col='#%02x%02x%02x'%rgb
     if ci in [7,250]:col='#444' if ci==7 else '#92969a'
     lw=2 if layer=='01 - Stationsgebied' else 1.2 if layer.startswith('Aansluiting LS K') else .6
    if typ=='INSERT':
     name=data['drawing']['symbol_types'].get(e.dxf.handle,e.dxf.name)
     if source=='main' and 'MOF' in name.upper():foreground=9
     elif source=='main' and name=='RT 1-12':foreground=6
     if depth<4:
      try:
       for v in e.virtual_entities():walk(v,ci if source=='main' else inherit,depth+1,layer,foreground)
      except (ValueError,TypeError):pass
     for a in e.attribs:walk(a,inherit,depth+1,layer,foreground)
    elif typ in ['LINE','LWPOLYLINE','POLYLINE','ARC','CIRCLE','ELLIPSE','SPLINE']:
     try:
      pts=np.array([list(v)[:2] for v in ep.make_path(e).flattening(.12)])
      if len(pts)<2 or max(pts[:,0])<bb[0] or min(pts[:,0])>bb[1] or max(pts[:,1])<bb[2] or min(pts[:,1])>bb[3]:return
      if foreground:
       group=front.setdefault(foreground,([],[],[]));group[0].append(pts);group[1].append(col);group[2].append(lw)
      else:lines.append(pts);colors.append(col);widths.append(lw)
     except (ValueError,TypeError):pass
    elif typ=='HATCH' and foreground and e.dxf.solid_fill:
     for path in ep.from_hatch(e):
      pts=np.array([list(v)[:2] for v in path.flattening(.03)])
      if len(pts)>=3 and max(pts[:,0])>=bb[0] and min(pts[:,0])<=bb[1] and max(pts[:,1])>=bb[2] and min(pts[:,1])<=bb[3]:ax.add_patch(MplPolygon(pts,closed=True,facecolor=col,edgecolor='none',zorder=foreground-.1))
    elif typ=='WIPEOUT' and source=='main':
     pts=np.array([list(v)[:2] for v in e.boundary_path_wcs()]);ax.add_patch(MplPolygon(pts,closed=True,facecolor='white',edgecolor='none',zorder=5))
    elif typ in ['TEXT','MTEXT','ATTRIB'] and source=='main':
     if e.dxf.get('invisible',0):return
     p=e.dxf.insert
     if typ!='MTEXT' and e.dxf.get('halign',0) and e.dxf.hasattr('align_point'):p=e.dxf.align_point
     if not inside(p):return
     t=e.plain_text() if typ=='MTEXT' else e.dxf.text;h=e.dxf.char_height if typ=='MTEXT' else e.dxf.height;size=max(2.6,h*min(16/(bb[1]-bb[0]),12/(bb[3]-bb[2]))*72*.85);rotation=e.dxf.get('rotation',0) if typ!='MTEXT' else 0
     texts.append((p,t,col,size,rotation,foreground))
   for e in doc.modelspace():walk(e)
   ax.add_collection(LineCollection(lines,colors=colors,linewidths=widths,zorder=1 if source=='topo' else 2 if source=='klic' else 3))
   for z,(fl,fc,fw) in front.items():ax.add_collection(LineCollection(fl,colors=fc,linewidths=fw,zorder=z))
   for p,t,c,size,rotation,foreground in texts:ax.text(p[0],p[1],t,color=c,fontsize=size,fontfamily='Arial',rotation=rotation if rotation<90 or rotation>270 else rotation-180,rotation_mode='anchor',va='baseline',clip_on=True,zorder=7 if foreground==6 else 4)
  draw(topo,'topo');draw(klic,'klic');draw(main,'main');ax.set_title(cfg['station_id']+' | '+name+' | ontwerp uit brongegevens',fontsize=12);fig.tight_layout();fig.savefig(out/(name+'.png'));plt.close(fig)
 return [str(out/(name+'.png')) for name in bounds]
