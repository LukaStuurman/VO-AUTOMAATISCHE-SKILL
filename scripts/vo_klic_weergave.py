"""Historische projectkopie; de actuele VO-workflow wijzigt geen externe referenties."""
import math,re,json,subprocess,os
from pathlib import Path

def make_clipped_klic_view(data,previous_parts,out):
 import ezdxf
 from ezdxf import bbox
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import substring,unary_union
 cfg=data['config'];doc=ezdxf.readfile(cfg['klic_dxf']);msp=doc.modelspace();logs=[];removals=[]
 # Reapply cumulative cuts to a fresh project copy; a revision must never
 # resurrect an arm removed in a preceding saved candidate.
 for row in data.get('klic_display_removals',[])+data.get('additional_display_removals',[]):
  original=shape(data['existing_chains'][row['code']]);removed=shape(row['geometry']);used=shape(row['protected_used_geometry'])
  if not any(code==row['code'] and prior.equals(removed) for code,_,prior,_ in removals):removals.append((row['code'],original,removed,used))
 for d in data['directions']:
  if not d.get('feed') or d.get('splice_kind')!='VM':continue
  original=shape(data['existing_chains'][d['primary_code']]);old=next(p for p in previous_parts[d['id']] if p['code']==d['primary_code']);new=next(p for p in d['retained'] if p['code']==d['primary_code']);used=unary_union([shape(p['geometry']) for other in data['directions'] for p in other['retained'] if p['code']==d['primary_code']])
  intervals=[]
  if new['lo']>old['lo']+.001:intervals.append((old['lo'],new['lo']))
  if new['hi']<old['hi']-.001:intervals.append((new['hi'],old['hi']))
  for lo,hi in intervals:
   removed=substring(original,lo,hi)
   if removed.difference(used.buffer(.00001)).length<.001:continue
   if removed.intersection(used).length>.001:raise ValueError('VM-arm deels in gebruik door andere richting; bepaal eerst afzonderlijke ongebruikte deelstukken.')
   # Only the verified connection-free arm between the previous own end and
   # the VM is edited; the rest of the cable group remains protected.
   if any(lo+.01<r['chain_position_m']<hi-.01 for other in data['directions'] for r in other['records'] if r['code']==d['primary_code']):raise ValueError('VM-verwijdering raakt een toegewezen aansluiting.')
   if not any(code==d['primary_code'] and removed.equals(prior) for code,_,prior,_ in removals):removals.append((d['primary_code'],original,removed,used))
 for code,original,removed,used in removals:
   protected=unary_union([shape(p['geometry']) for other in data['directions'] for p in other['retained'] if p['code']==code])
   if removed.intersection(protected).length>.001:raise ValueError('Projectknip raakt behouden kabel: '+code)
   for e in list(msp.query('LWPOLYLINE')):
    if e.dxf.layer not in ['E_LV_MAP_CABLE_LS','E_LV_MAP_CABLE_LSOV'] or len(e)<2:continue
    g=LineString(e.get_points('xy'))
    if g.intersection(removed.buffer(.001)).length<.02:continue
    a=g.project(Point(removed.coords[0]));b=g.project(Point(removed.coords[-1]));left,right=sorted([a,b]);cut=substring(g,left,right)
    if cut.geom_type!='LineString' or cut.difference(removed.buffer(.02)).length>max(.001,cut.length*.01) or cut.intersection(used.buffer(.00001)).length>.001:continue
    pieces=[substring(g,0,left),substring(g,right,g.length)];pieces=[p for p in pieces if p.geom_type=='LineString' and p.length>.01]
    handle=e.dxf.handle;attrs=e.dxfattribs();attrs.pop('handle',None);attrs.pop('owner',None);msp.delete_entity(e)
    for p in pieces:msp.add_lwpolyline(list(p.coords),dxfattribs=attrs)
    logs.append({'code':code,'source_handle':handle,'removed_display_m':g.length-sum(p.length for p in pieces),'kind':'LS-hoofdkabel','original_source_modified':False})
   for e in list(msp.query('INSERT CIRCLE')):
    if 'MAP_CABLE_END_JOINT_LS' not in e.dxf.layer:continue
    bb=bbox.extents([e]);p=Point(bb.center.xy)
    if p.distance(removed)<.02 and p.distance(used)>.02:
     handle=e.dxf.handle;msp.delete_entity(e);logs.append({'code':code,'source_handle':handle,'kind':'Eindmof op verwijderd armdeel','original_source_modified':False})
 out=Path(out);out.mkdir(exist_ok=True);file=out/'KLIC LS - ontwerpweergave.dxf';doc.saveas(file);data['klic_display_edits']=logs;data['klic_display_removals']=[{'code':code,'geometry':removed.__geo_interface__,'protected_used_geometry':used.__geo_interface__} for code,original,removed,used in removals];data['config']['klic_display_dxf']=str(file.resolve());return file,removals

def convert_klic_dwg(dxf_path):
 dxf=Path(dxf_path).resolve();output=dxf.with_suffix('.dwg');versions=Path('C:/Program Files/Autodesk');consoles=sorted(versions.glob('AutoCAD */accoreconsole.exe'),reverse=True)
 if not consoles:raise RuntimeError('Geen AutoCAD Core Console voor de project-xref; DXF-weergave is bewaard.')
 previous_stamp=output.stat().st_mtime_ns if output.exists() else None
 overwrite=' "_Yes"' if output.exists() else ''
 script=dxf.parent/'KLIC weergave opslaan.scr';script.write_text('(setvar "FILEDIA" 0)\n(setvar "CMDDIA" 0)\n(command "_.DXFIN" '+json.dumps(dxf.as_posix())+')\n(command "_.SAVEAS" "_2018" '+json.dumps(output.as_posix())+overwrite+')\n_.QUIT\n',encoding='ascii')
 flags=subprocess.CREATE_NO_WINDOW if os.name=='nt' else 0
 run=subprocess.run([str(consoles[0]),'/s',str(script),'/l','en-US'],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,creationflags=flags,timeout=120)
 (dxf.parent/'KLIC conversie.log').write_text(run.stdout.decode('utf-16-le',errors='replace'),encoding='utf8')
 if run.returncode or not output.exists() or output.read_bytes()[:6]!=b'AC1032' or (previous_stamp is not None and output.stat().st_mtime_ns<=previous_stamp):raise RuntimeError('KLIC-projectweergave niet als nieuwe DWG bevestigd; zie conversielog.')
 return output
