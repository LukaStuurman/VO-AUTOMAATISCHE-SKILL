"""Vervang een kort, dun belast hoofdkabeldeel door een nieuwe straatvoeding."""

def replace_short_primary(direction,router):
 from shapely.geometry import LineString
 from vo_harde_voorwaarden import short_reuse
 if not short_reuse([direction]):return False
 # Branch replacement needs its own topology; never concatenate branches here.
 if len(direction['retained'])!=1 or direction['retained'][0]['code']!=direction['primary_code']:return False
 records=sorted(direction['records'],key=lambda r:r['chain_position_m'])
 if not records:return False
 choices=[]
 for ordered in [records,records[::-1]]:
  points=list(router.path(ordered[0]['tap']).coords);paths=[];contacts={}
  for i,r in enumerate(ordered):
   if i:points.extend(list(router.between(ordered[i-1]['tap'],r['tap']).coords)[1:])
   contacts[r['id']]=list(points[-1]);paths.append(LineString(points))
  if paths[-1].is_simple:choices.append((paths[-1].length,paths,contacts))
 if not choices:return False
 _,paths,contacts=min(choices,key=lambda q:q[0]);part=direction['retained'][0]
 direction['short_reuse_replacement']={'old_code':part['code'],'old_length_m':part['geometry'].length if hasattr(part['geometry'],'length') else __import__('shapely').geometry.shape(part['geometry']).length,'connections':len(records),'new_type':'150Al'}
 direction['retained']=[];direction['new_codes']=list(dict.fromkeys(direction['new_codes']+[part['code']]));direction['feed']=None;direction['new_paths']=paths
 for r in records:r['new_tap']=contacts[r['id']]
 return True
