"""Stijlblokken zonder stationslocaties, kabelroutes of gekozen richtingwaarden."""
import json
from pathlib import Path

def style_templates(doc):
 from ezdxf.entities import Insert
 assets=json.loads((Path(__file__).parent.parent/'assets/cad-stijl.json').read_text(encoding='utf8'))['symbols'];templates={}
 for name,asset in assets.items():
  existing=next((e for e in doc.modelspace().query('INSERT') if e.dxf.name==name),None)
  if existing is not None and name!='RT 1-12':templates[name]=existing;continue
  blockname='VO_STYLE_'+name.replace(' ','_');block=doc.blocks.get(blockname) if blockname in doc.blocks else doc.blocks.new(blockname)
  if not len(block):
   for p in asset['primitives']:
    attrs={'layer':p['layer'],'color':p['color']}
    if p['layer'] not in doc.layers:doc.layers.new(p['layer'])
    if p['type']=='LINE':block.add_line(p['start'],p['end'],dxfattribs=attrs)
    elif p['type']=='CIRCLE':block.add_circle(p['center'],p['radius'],dxfattribs=attrs)
    elif p['type']=='ARC':block.add_arc(p['center'],p['radius'],p['start_angle'],p['end_angle'],dxfattribs=attrs)
    elif p['type']=='LWPOLYLINE':block.add_lwpolyline(p['points'],close=p['closed'],dxfattribs=attrs)
  e=Insert.new(dxfattribs={'name':blockname,'insert':(0,0,0)},doc=doc)
  for a in asset['attributes']:
   attrs={k:v for k,v in a.items() if k not in ['tag','insert']}
   position=a['insert']
   if name=='RT 1-12':
    circles=[p for p in asset['primitives'] if p['type']=='CIRCLE' and p['layer']==a['layer']]
    if len(circles)!=1:raise ValueError('RT-rij mist eenduidig stijlrondje: '+a['tag'])
    p=circles[0]['center'];position=[p[0]+.85,p[1]-.35,0];attrs.update(halign=0,valign=0,rotation=0,align_point=position)
   if a['layer'] not in doc.layers:doc.layers.new(a['layer'])
   e.add_attrib(a['tag'],'',position,dxfattribs=attrs)
  templates[name]=e
 return templates
