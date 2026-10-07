"""Materiële WFS-delen onderbouwen met KLIC-geulenteksten, zonder ontwerpvoorbeeld."""
import re

def material_intervals(code,chain,features,evidence,catalogue):
 from shapely.geometry import shape,Point
 parts=[]
 for f in features:
  full=shape(f['geometry'])
  for index,g in enumerate(full.geoms if full.geom_type=='MultiLineString' else [full]):
   ends=[chain.project(Point(p)) for p in [g.coords[0],g.coords[-1]]]
   if max(ends)-min(ends)<1e-7:continue
   parts.append({'feature_id':f['id']+f'#{index}','lo':min(ends),'hi':max(ends),'geometry':g,'combo':'LS/OV' in f['properties']['omschrijving'],'evidence':[]})
 for label in evidence:
  eligible=[p for p in parts if p['combo']==label['combo']]
  if not eligible:continue
  p=min(eligible,key=lambda p:p['geometry'].distance(Point(label['xy'])));p['evidence'].append(label)
 for p in parts:
  kinds={e['type'] for e in p['evidence']}
  if len(kinds)>1:raise ValueError('Niet eenduidige KLIC-types op WFS-deel '+p['feature_id'])
  if kinds:p['type']=next(iter(kinds));p['material_basis']='KLIC-label gekoppeld aan WFS-deel met dezelfde LS/combi-functie'
 # Unlabelled short connector pieces cannot silently invent a type boundary.
 # Use a conservative documented bound; retain that uncertainty in the output.
 known={p['type'] for p in parts if 'type' in p}
 if not known:raise ValueError('Geen bruikbare KLIC-materiaalbron voor '+code)
 for p in parts:
  if 'type' not in p:
   adjacent=[q for q in parts if 'type' in q and q['geometry'].distance(p['geometry'])<.02 and q['combo']==p['combo']]
   kinds={q['type'] for q in adjacent} or known
   if len(kinds)==1:p['type']=next(iter(kinds));p['material_basis']='Zelfde bronmateriaal op aangrenzende WFS-delen'
   else:
    worst=max(kinds,key=lambda k:catalogue[k]['R']);minimum=min(catalogue[k]['Imax'] for k in kinds)
    if catalogue[worst]['Imax']>minimum or catalogue[worst]['X']<max(catalogue[k]['X'] for k in kinds):raise ValueError('Geen enkel conservatief kabeltype voor onbevestigd tussendeel '+p['feature_id'])
    p['type']=worst;p['material_basis']='Conservatieve berekening van onbevestigd materiaalgrensstuk';p['material_question']=True
 return [{k:v for k,v in p.items() if k!='geometry'} for p in sorted(parts,key=lambda p:p['lo'])]

def segments_between(part,start,end,prefix='old'):
 lo,hi=sorted([start,end]);rows=part.get('material_segments')
 if not rows:return [{'id':prefix,'type':part['type'],'length_m':hi-lo}]
 result=[]
 for i,row in enumerate(rows):
  length=max(0,min(hi,row['hi'])-max(lo,row['lo']))
  if length>1e-7:result.append({'id':f'{prefix}-{i}','type':row['type'],'length_m':length})
 if abs(sum(r['length_m'] for r in result)-(hi-lo))>.02:raise ValueError('Materiële delen dekken kabelpad niet volledig')
 return result

def drawing_parts(part,chain):
 from shapely.ops import substring
 rows=part.get('material_segments')
 if not rows:return [part]
 result=[];merged=[]
 for row in rows:
  lo=max(part['lo'],row['lo']);hi=min(part['hi'],row['hi'])
  if hi-lo<=.000001:continue
  if merged and merged[-1]['type']==row['type'] and merged[-1]['combo']==row['combo'] and abs(merged[-1]['hi']-lo)<.02:merged[-1]['hi']=hi
  else:merged.append(dict(row,lo=lo,hi=hi))
 for row in merged:
  if row['hi']-row['lo']>.05:result.append(dict(part,type=row['type'],combo=row['combo'],geometry=substring(chain,row['lo'],row['hi']),lo=row['lo'],hi=row['hi']))
 return result

def contact_material(part,position):
 """Use only material intervals actually retained at this physical contact."""
 rows=[r for r in part.get('material_segments',[]) if min(part['hi'],r['hi'])-max(part['lo'],r['lo'])>1e-5 and r['lo']-1e-5<=position<=r['hi']+1e-5]
 if not rows:return {'type':part['type'],'combo':part.get('combo',False)}
 return {'type':' / '.join(sorted({r['type'] for r in rows})),'combo':any(r['combo'] for r in rows)}

def source_notation(code,kind,combo,xy,evidence):
 """Keep the actual KLIC conductor notation, including its OV conductor."""
 import math
 choices=[e for e in evidence.get(code,[]) if e['type']==kind and e['combo']==combo]
 if not choices:return kind
 e=min(choices,key=lambda e:math.dist(e['xy'][:2],xy[:2]))
 match=re.search(r'(\d+\s*(?:Al|Cu)?(?:\s*\+\s*\d+)?)\s+'+re.escape(code[3:]),e['text'],re.I)
 return match[1].replace(' ','') if match else kind
