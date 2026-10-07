"""Reuse a short planned trench approach before routing a distant new feed."""
import math

def shorten_via_shared_feeds(data,router):
 from shapely.geometry import shape,Point,LineString
 from vo_paden import geometry_checks
 directions=data['directions'];changed=[];trials=[]
 conflicts={r['new_direction'] for r in data.get('checks',{}).get('new_retained_intersections',[])}
 conflicts.update(n for row in data.get('checks',{}).get('new_new_crossings',[]) for n in [row['a'],row['b']])
 for d in directions:
  if d['id'] not in conflicts or not d.get('feed') or d['new_codes']:continue
  old=shape(d['display_main']);options=[]
  for other in directions:
   if other is d or not other.get('feed'):continue
   goal=d['feed']['xy'];joint=other['feed']['xy']
   if math.dist(goal[:2],joint[:2])<2:continue
   try:
    prefix=router.path(joint);section=router.between(joint,goal)
   except ValueError as error:trials.append({'direction':d['id'],'via':other['id'],'reason':str(error)});continue
   coords=list(prefix.coords)+list(section.coords)[1:];clean=[coords[0]]
   for p in coords[1:]:
    if math.dist(clean[-1][:2],p[:2])>.001:clean.append(p[:2])
   while len(clean)>2:
    a,b=clean[-2:];u=(b[0]-a[0],b[1]-a[1]);v=(goal[0]-b[0],goal[1]-b[1])
    if u[0]*v[0]+u[1]*v[1]>=0 or LineString([a,goal[:2]]).intersects(router.physical_obstacles):break
    clean.pop()
   if math.dist(clean[-1][:2],goal[:2])>.001:clean.append(tuple(goal[:2]))
   candidate=LineString(clean)
   hit=candidate.intersection(router.physical_obstacles).difference(router.station)
   trials.append({'direction':d['id'],'via':other['id'],'length_m':candidate.length,'old_length_m':old.length,'simple':candidate.is_simple,'obstacle_length_m':hit.length})
   if candidate.length>=old.length*.85 or not candidate.is_simple or not hit.is_empty:continue
   trial=dict(d,profile='laatste_helft');calc=geometry_checks(trial,candidate)
   if not calc['selected']['passes']:continue
   options.append((candidate.length,candidate,other['id'],calc))
  if not options:continue
  _,g,via,calc=min(options,key=lambda row:row[0]);d['new_paths']=[g.__geo_interface__];d['feed']['path']=g.__geo_interface__;d['display_main']=g.__geo_interface__;d['profile']='laatste_helft';d['profile_evidence']={'basis':'Conservatief laatste-helftprofiel bij verkorte bronaanloop'};d['limiting']=calc['selected']['limiting'];d['passes']=True
  changed.append({'direction':d['id'],'via_short_feed':via,'old_length_m':old.length,'new_length_m':g.length,'basis':'Nieuwe verbinding over dezelfde korte openbare aanloop; BGT/obstakels en volledige padbelasting opnieuw getoetst'})
 data['shortened_shared_approaches']=changed
 data['shared_approach_trials']=trials
 return data
