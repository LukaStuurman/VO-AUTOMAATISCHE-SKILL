"""Redistribute a retained cable at crossings, preserving each service once."""
import copy

def redistribute_at_crossings(data,sources):
 from shapely.geometry import shape,Point
 from shapely.ops import substring
 from vo_paden import geometry_checks
 rows=data.get('checks',{}).get('new_retained_intersections',[]);grouped={};log=[]
 for row in rows:grouped.setdefault((row['retained_direction'],row['code']),[]).append(row)
 for (owner_id,code),hits in grouped.items():
  owner=next(d for d in data['directions'] if d['id']==owner_id);part=next(p for p in owner['retained'] if p['code']==code);chain=sources['groups'][code]['geometry'];points=[]
  for row in hits:
   g=shape(row['geometry']);points.extend(list(g.geoms) if hasattr(g,'geoms') else [g])
  positions=[chain.project(p) for p in points if p.geom_type=='Point']
  if not positions:continue
  margin=data['config']['rules'].get('joint_separation_m',2)/2;lo=min(positions)-margin;hi=max(positions)+margin;root=owner['feed']['position_m'] if owner.get('feed') and owner['primary_code']==code else None
  edge_cut=lo<=part['lo'] or hi>=part['hi'];lo=max(lo,part['lo']);hi=min(hi,part['hi'])
  if root is None or hi<=lo or lo<=root<=hi:continue
  own=[r for r in owner['records'] if r['code']==code and not r.get('new_connection')]
  if not edge_cut and any(lo<r['chain_position_m']<hi for r in own):continue
  if any(lo<x['position_m']<hi for x in sources['groups'][code]['outside_taps']):continue
  lower=root>hi;moving=[r for r in own if r['chain_position_m']<(hi if edge_cut else lo)] if lower else [r for r in own if r['chain_position_m']>(lo if edge_cut else hi)]
  if not moving:continue
  candidates=[]
  for recipient in data['directions']:
   if edge_cut:continue
   if recipient is owner or not recipient.get('feed') or recipient['primary_code']!=code:continue
   target=next(p for p in recipient['retained'] if p['code']==code)
   if not (target['hi']<=part['lo'] if lower else target['lo']>=part['hi']):continue
   trial=copy.deepcopy(recipient);testpart=next(p for p in trial['retained'] if p['code']==code)
   testpart['hi' if lower else 'lo']=lo if lower else hi;testpart['geometry']=substring(chain,testpart['lo'],testpart['hi']).__geo_interface__;trial['records']+=moving;trial['load_A']+=sum(r['current_A'] for r in moving)
   calc=geometry_checks(trial,shape(recipient['display_main']))
   if not calc['selected']['passes']:continue
   otherparts=[shape(p['geometry']) for d in data['directions'] if d not in [owner,recipient] for p in d['retained'] if p['code']==code]
   if any(shape(testpart['geometry']).intersection(g).length>1e-6 for g in otherparts):continue
   candidates.append((abs(target['hi' if lower else 'lo']-(lo if lower else hi)),recipient,testpart,calc))
  if not candidates:
   # If no adjacent retained feed exists, transfer only the endpoint cluster
   # to a new main that already passes it, then cut back the obsolete tail.
   tail_lo,tail_hi=(part['lo'],hi) if lower else (lo,part['hi'])
   if any(tail_lo<x['position_m']<tail_hi for x in sources['groups'][code]['outside_taps']):continue
   from shapely.ops import nearest_points
   replacements=[]
   for name in {row['new_direction'] for row in hits}:
    target_direction=next(d for d in data['directions'] if d['id']==name);g=shape(target_direction['display_main']);newrecords=[]
    for r in moving:
     _,tap=nearest_points(Point(r['tap']),g)
     if tap.distance(Point(r['tap']))>data['config']['rules'].get('transfer_radius_m',30):break
     newrecords.append(dict(r,new_connection=True,new_tap=list(tap.coords[0]),overzetter=True,direction=name))
    if len(newrecords)!=len(moving):continue
    trial=dict(target_direction,records=target_direction['records']+newrecords,load_A=target_direction['load_A']+sum(r['current_A'] for r in moving),profile='laatste_helft');calc=geometry_checks(trial,g)
    if calc['selected']['passes']:replacements.append((sum(Point(r['tap']).distance(Point(n['new_tap'])) for r,n in zip(moving,newrecords)),target_direction,newrecords,calc))
   if not replacements:continue
   _,target_direction,newrecords,calc=min(replacements,key=lambda r:r[0]);target_direction['records']+=newrecords;target_direction['load_A']+=sum(r['current_A'] for r in moving);target_direction['profile']='laatste_helft';target_direction['limiting']=calc['selected']['limiting'];owner['records']=[r for r in owner['records'] if r not in moving];owner['load_A']-=sum(r['current_A'] for r in moving);part['lo' if lower else 'hi']=hi if lower else lo;part['geometry']=substring(chain,part['lo'],part['hi']).__geo_interface__;part['records']=[r for r in owner['records'] if r['code']==code]
   owner['limiting']=geometry_checks(owner,shape(owner['display_main']))['selected']['limiting'];log.append({'code':code,'from_direction':owner_id,'to_direction':target_direction['id'],'connection_ids':[r['id'] for r in moving],'cut_gap_m':[tail_lo,tail_hi],'overzetters_required':True,'basis':'Alleen het eindcluster gaat naar de passerende nieuwe hoofdkabel; ongebruikte oude staart vervalt'})
   continue
  _,recipient,newpart,calc=min(candidates,key=lambda r:r[0]);target=next(p for p in recipient['retained'] if p['code']==code);target.update(newpart);recipient['records']+=moving;recipient['load_A']+=sum(r['current_A'] for r in moving);owner['records']=[r for r in owner['records'] if r not in moving];owner['load_A']-=sum(r['current_A'] for r in moving)
  part['lo' if lower else 'hi']=hi if lower else lo;part['geometry']=substring(chain,part['lo'],part['hi']).__geo_interface__;part['records']=[r for r in owner['records'] if r['code']==code];target['records']=[r for r in recipient['records'] if r['code']==code]
  for r in moving:r['direction']=recipient['id']
  recipient['limiting']=calc['selected']['limiting'];owner['limiting']=geometry_checks(owner,shape(owner['display_main']))['selected']['limiting']
  log.append({'code':code,'from_direction':owner_id,'to_direction':recipient['id'],'connection_ids':[r['id'] for r in moving],'cut_gap_m':[lo,hi],'basis':'Bestaande aansluitingen blijven op hun kabel; ongebruikte opening voorkomt kruisingen met nieuwe aanlopen'})
 assigned={r['id']:r for d in data['directions'] for r in d['records']}
 for r in data['connections']:
  update=assigned[r['id']]
  for key in ['direction','new_connection','new_tap','overzetter']:
   if key in update:r[key]=update[key]
 data['existing_cable_redistributions']=log
 return data
