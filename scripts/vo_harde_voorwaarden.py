"""Brondekking, trafogrens en zinvol kort hergebruik vóór vormgeving."""
import json,hashlib
from pathlib import Path

def bgt_coverage(config,region):
 from shapely.geometry import box
 register=config.get('bgt_source_register')
 if not register:return [{'reason':'BGT-selectiegebied en volledige paginering zijn niet vastgelegd; brondekking eerst verifiëren'}]
 data=json.loads(Path(register).read_text(encoding='utf8'));errors=[]
 for name,file in config['bgt'].items():
  row=data.get('sources',{}).get(name)
  if not row:errors.append({'source':name,'reason':'Bron ontbreekt in BGT-selectieregister'});continue
  if not row.get('pagination_complete') or not box(*row['bbox_RD']).buffer(.001).covers(region):errors.append({'source':name,'reason':'BGT-selectie/paginering dekt het volledige doelgebied niet'})
  if row.get('sha256') and hashlib.sha256(Path(file).read_bytes()).hexdigest()!=row['sha256']:errors.append({'source':name,'reason':'BGT-snapshot wijkt af van vastgelegde bronhash'})
 return errors

def retained_outside(directions,region):
 from shapely.geometry import shape
 errors=[]
 for d in directions:
  for part in d['retained']:
   g=shape(part['geometry']) if isinstance(part['geometry'],dict) else part['geometry'];outside=g.difference(region.buffer(.001))
   if outside.length>.001:errors.append({'direction':d['id'],'code':part['code'],'length_m':outside.length,'geometry':outside.__geo_interface__,'reason':'Gebruikt bestaand deel loopt buiten eigen trafogebied'})
 return errors

def short_reuse(directions,max_length=25,min_connections=5):
 from shapely.geometry import shape
 rows=[]
 for d in directions:
  for part in d['retained']:
   g=shape(part['geometry']) if isinstance(part['geometry'],dict) else part['geometry'];ids={r['id'] for r in d['records'] if r['code']==part['code'] and not r.get('new_connection') and part.get('lo',0)-.001<=r.get('chain_position_m',0)<=part.get('hi',g.length)+.001}
   if part['code']==d['primary_code']:
    children={p['code'] for p in d['retained'] if p['code']!=part['code']}
    ids.update(r['id'] for r in d['records'] if r['code'] in children and r['code'] in d.get('parent_child_positions',{}) and part.get('lo',0)-.001<=d['parent_child_positions'][r['code']]['parent_position']<=part.get('hi',g.length)+.001 and not r.get('new_connection'))
   if g.length<max_length and len(ids)<min_connections:rows.append({'direction':d.get('id',d['primary_code']),'code':part['code'],'length_m':g.length,'connections':len(ids),'reason':'Kort bestaand deel met minder dan vijf aansluitingen: nieuw 150Al heeft voorkeur'})
 return rows
