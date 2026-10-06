"""Bestaande eindmoffen behouden en vervallen ontwerpannotaties samen opruimen."""
import re,math

def existing_joint_objects(path):
 import ezdxf
 from ezdxf import bbox
 result=[]
 for e in ezdxf.readfile(path).modelspace().query('INSERT CIRCLE'):
  layer=e.dxf.layer.upper()
  kind='end' if 'MAP_CABLE_END_JOINT_LS' in layer else 'branch' if 'MAP_CABLE_JOINT_LS' in layer else None
  if kind is None:continue
  bb=bbox.extents([e]);result.append({'handle':e.dxf.handle,'xy':[bb.center.x,bb.center.y],'layer':e.dxf.layer,'kind':kind})
 return result

def existing_end_joints(path):
 return [j for j in existing_joint_objects(path) if j['kind']=='end']

def retained_end_status(point,original,joints,tolerance=.10):
 from shapely.geometry import Point
 unchanged=min(math.dist(point,original.coords[0]),math.dist(point,original.coords[-1]))<=tolerance
 matching=[j for j in joints if math.dist(point,j['xy'])<=tolerance]
 return {'new_required':not (unchanged and matching),'reason':'Ongewijzigd bestaand kabeluiteinde met KLIC-eindmof' if unchanged and matching else 'Nieuwe fysieke scheiding/eindlocatie','existing_joint':matching[0] if unchanged and matching else None}

def clean_obsolete_end_annotations(doc,directions,region,original_chains):
 from ezdxf import bbox
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 used_codes={p['code'] for d in directions for p in d['retained']};protected_ends=[Point(p) for d in directions for p in d.get('end_mof_positions',[])];log=[];msp=doc.modelspace()
 for e in list(msp.query('TEXT MTEXT')):
  label=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text();m=re.fullmatch(r'\s*EM\s*\(was\s+(\d+-\d+)\)\s*',label,re.I)
  if not m:continue
  codes=[c for c in used_codes if c.endswith(m.group(1))]
  if len(codes)!=1:continue
  code=codes[0];original=original_chains[code];near=[]
  for ins in msp.query('INSERT'):
   if ins.dxf.name!='NIEUWE MOF' or ins.dxf.layer!=e.dxf.layer:continue
   bb=bbox.extents([ins]);p=Point(bb.center.x,bb.center.y)
   if p.distance(Point(e.dxf.insert.xy))<2:near.append((p.distance(Point(e.dxf.insert.xy)),ins,p))
  if not near:continue
  _,symbol,p=min(near,key=lambda x:x[0])
  if not region.covers(p) or original.distance(p)>1:continue
  if any(p.distance(end)<1 for end in protected_ends):continue
  retained=[__import__('shapely').geometry.shape(part['geometry']) for d in directions for part in d['retained'] if part['code']==code]
  # Only matching prior DESIGN objects. The KLIC source and other stations'
  # endpoints outside this area remain intact.
  clipped=[]
  for cable in list(msp.query('LWPOLYLINE')):
   if code not in cable.dxf.layer or len(cable)<2:continue
   old=LineString(cable.get_points('xy'))
   at_start=Point(old.coords[0]).distance(p)<.15;at_end=Point(old.coords[-1]).distance(p)<.15
   if not (at_start or at_end):continue
   ends=[Point(xy) for g in retained for xy in [g.coords[0],g.coords[-1]]];cuts=[q for q in ends if old.distance(q)<.2 and p.distance(q)>1]
   if not cuts:continue
   cut=min(cuts,key=lambda q:p.distance(q));at=old.project(cut);replacement=substring(old,at,old.length) if at_start else substring(old,0,at)
   if replacement.geom_type!='LineString':continue
   cable.set_points(list(replacement.coords),format='xy');clipped.append({'handle':cable.dxf.handle,'new_endpoint':list(cut.coords)[0],'overlay_removed_length_m':old.length-replacement.length})
  log.append({'code':code,'symbol_handle':symbol.dxf.handle,'text_handle':e.dxf.handle,'xy':list(p.coords)[0],'text':label,'trimmed_prior_design_overlays':clipped,'reason':'Vorige ontwerpeindlocatie vervangen; huidige fysieke eindlocaties en alle gebruikte kabeldelen behouden'})
  msp.delete_entity(symbol);msp.delete_entity(e)
 return log
