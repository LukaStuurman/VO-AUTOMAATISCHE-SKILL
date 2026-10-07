"""Herstel eigen bronkandidaten langs openbare grond, zonder doeltekening.

De agent kiest betrokken richtingen uit het controleblad. De functies veranderen
geen aansluitingstoewijzing, bronkabel of stationspoort. Iedere aanloop wordt
met dezelfde volledige belasting opnieuw berekend.
"""
import itertools,math

def retained_barriers(directions,except_name,clearance=.12):
 from shapely.geometry import shape
 from shapely.ops import unary_union
 return unary_union([shape(p['geometry']).buffer(clearance) for d in directions if d['id']!=except_name for p in d['retained']])

def conflicts(new,name,lines,directions):
 from shapely.geometry import shape
 old=sum(not new.intersection(shape(p['geometry'])).is_empty for d in directions if d['id']!=name for p in d['retained'])
 other=sum(not new.intersection(g).is_empty for n,g in lines.items() if n!=name)
 return old,other

def public_feeder_tail(direction,lines,directions,obstacles,surfaces,region,windows=(12,20,35,50,65,80)):
 """Ga om een behouden kabeluiteinde heen via een toegestane straatcorridor."""
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 from vo_gedeelde_oversteek import sidewalk_connection
 from vo_paden import geometry_checks
 if not direction.get('feed') or direction.get('new_codes'):return None
 name=direction['id'];g=lines[name];initial=conflicts(g,name,lines,directions);free=surfaces.buffer(.2).difference(obstacles.buffer(.05)).difference(retained_barriers(directions,name,.25));options=[]
 for window in windows:
  at=max(direction.get('station_exit_protected_m',0),g.length-window)
  if at>=g.length-.1:continue
  try:tail=sidewalk_connection(g.interpolate(at).coords[0],direction['feed']['xy'],free,region)
  except ValueError:continue
  new=LineString(list(substring(g,0,at).coords)+list(tail.coords)[1:]);score=conflicts(new,name,lines,directions)
  if score>=initial or not new.is_simple:continue
  calc=geometry_checks(direction,new)
  if calc['selected']['passes']:options.append((score,new.length,new,calc))
 if not options:return None
 score,_,new,calc=min(options,key=lambda r:r[:2]);return {'geometry':new,'calculation':calc,'conflicts':score,'basis':'Openbare omloop langs beschermd bestaand kabeluiteinde'}

def shared_feeder(reference,direction,lines,directions,obstacles,surfaces,region,offset_m):
 """Eén as tot de laatste echte aftak; verbind daarna de eigen voedingsmof."""
 from shapely.geometry import Point,LineString
 from shapely.ops import substring,unary_union
 from vo_gedeelde_oversteek import sidewalk_connection
 from vo_paden import geometry_checks
 name=direction['id'];axis=lines[reference];lane=axis.offset_curve(offset_m,join_style=2,mitre_limit=10)
 if lane.geom_type!='LineString' or not direction.get('feed'):return None
 barriers=unary_union([retained_barriers(directions,name),axis.buffer(.12)]+[g.buffer(.12) for n,g in lines.items() if n not in [reference,name]])
 free=surfaces.buffer(.2).difference(obstacles.buffer(.02)).difference(barriers);end=Point(direction['feed']['xy']);near=lane.project(end);options=[]
 for back in [0,1,2,4,6,8,12,18,25]:
  at=max(direction.get('station_exit_protected_m',0),near-back)
  if at>=lane.length:continue
  try:tail=sidewalk_connection(lane.interpolate(at).coords[0],end.coords[0],free,region)
  except ValueError:continue
  common=substring(lane,0,at);new=LineString(list(common.coords)+list(tail.coords)[1:]);score=conflicts(new,name,lines,directions)
  if any(score) or not new.is_simple or new.intersects(obstacles):continue
  calc=geometry_checks(direction,new)
  if calc['selected']['passes']:options.append((new.length,new,common,calc))
 if not options:return None
 _,new,common,calc=min(options,key=lambda r:r[0]);return {'geometry':new,'common_geometry':common,'reference':reference,'offset_m':offset_m,'calculation':calc}

def pavement_corner(lines,names,center,road,obstacles,surfaces,region,pitch=.2):
 """Vereenvoudig één bundelbocht; verplaats alle lanes samen binnen de stoep."""
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 names=list(names);axis=lines[names[0]];at=axis.project(Point(center));options=[]
 for window in [3,4,5,6,8,10]:
  for shift in [0]+[sign*k*.1 for k in range(1,11) for sign in [-1,1]]:
   lo,hi=max(0,at-window),min(axis.length,at+window);a,b=axis.interpolate(lo),axis.interpolate(hi);middle=LineString([a,b]).offset_curve(shift,join_style=2)
   if middle.geom_type!='LineString':continue
   spine=LineString([a]+list(middle.coords)+[b]);trial=dict(lines);proof=[];valid=True
   for rank,name in enumerate(names):
    g=lines[name];start,end=g.project(a),g.project(b);lane=spine.offset_curve(rank*pitch,join_style=2,mitre_limit=10)
    if end<=start or lane.geom_type!='LineString':valid=False;break
    patch=LineString([g.interpolate(start)]+list(lane.coords)+[g.interpolate(end)]);new=LineString(list(substring(g,0,start).coords)+list(lane.coords)+list(substring(g,end,g.length).coords))
    if not new.is_simple or patch.intersects(obstacles) or patch.intersection(road.buffer(-.000001)).length>.01 or not surfaces.buffer(.2).covers(patch) or not region.buffer(.2).covers(patch):valid=False;break
    trial[name]=new;proof.append({'direction':name,'geometry':lane.__geo_interface__,'offset_m':rank*pitch})
   if not valid or any(not trial[a].intersection(trial[b]).is_empty for a,b in itertools.combinations(trial,2)):continue
   options.append((window,abs(shift),trial,spine,proof))
 if not options:return None
 window,shift,result,spine,proof=min(options,key=lambda r:r[:2]);return {'lines':result,'reference_geometry':spine,'proof':proof,'window_m':window,'shift_m':shift}
