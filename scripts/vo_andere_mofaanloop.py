"""Try feeding the same retained consumers from the other cable end."""
import copy,math

def alternate_feed_end(data,sources,router):
 from shapely.geometry import Point,LineString,shape
 from shapely.ops import substring
 from vo_paden import geometry_checks
 names={r['new_direction'] for r in data.get('checks',{}).get('new_retained_intersections',[])};log=[];trials=[]
 for d in data['directions']:
  if d['id'] not in names or not d.get('feed') or d['new_codes']:continue
  part=next(p for p in d['retained'] if p['code']==d['primary_code']);chain=sources['groups'][d['primary_code']]['geometry'];root=d['feed']['position_m'];required=[r['chain_position_m'] for r in d['records'] if r['code']==d['primary_code'] and not r.get('new_connection')]+[d['parent_child_positions'][p['code']]['parent_position'] for p in d['retained'] if p['code']!=d['primary_code']]
  if not required:continue
  clearance=data['config']['rules'].get('connection_end_clearance_m',.6)
  positions=[part['hi'],min(part['hi'],max(required)+clearance)] if root<=min(required)+.001 else [part['lo'],max(part['lo'],min(required)-clearance)] if root>=max(required)-.001 else []
  options=[]
  for pos in positions:
   p=chain.interpolate(pos)
   if p.intersects(router.physical_obstacles) or not sources['region'].buffer(.2).covers(p):trials.append({'direction':d['id'],'position_m':pos,'reason':'Mofpunt raakt bronobstakel of ligt buiten gebied'});continue
   try:g=router.path(p.coords[0])
   except ValueError as error:trials.append({'direction':d['id'],'position_m':pos,'reason':str(error)});continue
   coords=list(g.coords)
   while len(coords)>2:
    a,b=coords[-2:];u=(b[0]-a[0],b[1]-a[1]);v=(p.x-b[0],p.y-b[1])
    if u[0]*v[0]+u[1]*v[1]>=0 or LineString([a,p.coords[0]]).intersects(router.physical_obstacles):break
    coords.pop()
   if math.dist(coords[-1][:2],p.coords[0][:2])>.001:coords.append(tuple(p.coords[0][:2]))
   g=LineString(coords)
   if not g.is_simple or not g.intersection(router.physical_obstacles).difference(router.station).is_empty:trials.append({'direction':d['id'],'position_m':pos,'reason':'Aanloop raakt bronobstakel'});continue
   trial=copy.deepcopy(d);tp=next(p for p in trial['retained'] if p['code']==d['primary_code']);tp['hi' if root<=min(required)+.001 else 'lo']=pos;tp['geometry']=substring(chain,tp['lo'],tp['hi']).__geo_interface__;trial['feed']={'position_m':pos,'xy':list(p.coords[0][:2]),'path':g.__geo_interface__};trial['new_paths']=[g.__geo_interface__];trial['display_main']=g.__geo_interface__;trial['profile']='laatste_helft';calc=geometry_checks(trial,g);trials.append({'direction':d['id'],'position_m':pos,'length_m':g.length,'capacity_pass':calc['selected']['passes']})
   if not calc['selected']['passes']:continue
   conflicts=sum(not g.intersection(shape(other['geometry'])).is_empty for owner in data['directions'] if owner is not d for other in owner['retained']);options.append((conflicts,g.length,trial,calc))
  if options:
   _,_,trial,calc=min(options,key=lambda row:row[:2]);oldroot=d['feed']['position_m'];d.update(trial);d['limiting']=calc['selected']['limiting'];d['passes']=True;log.append({'direction':d['id'],'old_position_m':oldroot,'new_position_m':d['feed']['position_m'],'basis':'Dezelfde bestaande aansluitingen vanaf de andere kabelzijde voeden om kruisende aanloop te vermijden'})
 data['alternate_feed_end_changes']=log;data['alternate_feed_end_trials']=trials
 return data
