"""Herstel gezamenlijke bochten door één referentielijn exact te offsetten."""
import math,itertools

def shared_offsets(lines,directions,obstacles,region,pitch=.2,_secondary=True):
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 backbones=[d['id'] for d in directions if not d.get('feed') and d.get('new_codes')]
 reference=max(backbones or list(lines),key=lambda n:lines[n].length);axis=lines[reference];order=[d['id'] for d in directions];result=dict(lines);log=[]
 for name,g in lines.items():
  if name==reference:continue
  delta=(order.index(name)-order.index(reference))*pitch;offset=axis.offset_curve(delta,join_style=2,mitre_limit=10)
  if offset.geom_type!='LineString':raise ValueError('Gedeelde offset valt uiteen: '+name)
  d=next(d for d in directions if d['id']==name);anchor=Point(d['feed']['xy']) if d.get('feed') else None
  positions=sorted(set([0,g.length]+[min(g.length,i) for i in range(1,math.ceil(g.length))]));runs=[];current=[]
  for at in positions:
   p=g.interpolate(at);q=axis.project(p);near=axis.interpolate(q);ga=g.interpolate(max(0,at-1));gb=g.interpolate(min(g.length,at+1));aa=axis.interpolate(max(0,q-1));ab=axis.interpolate(min(axis.length,q+1));u=(gb.x-ga.x,gb.y-ga.y);v=(ab.x-aa.x,ab.y-aa.y);den=math.hypot(*u)*math.hypot(*v);cos=(u[0]*v[0]+u[1]*v[1])/den if den else -1
   close=at>=d.get('station_exit_protected_m',0) and p.distance(near)<1.5 and cos>.7 and (anchor is None or p.distance(anchor)>3)
   if close and (not current or q>=current[-1][1]-.05):current.append((at,q))
   else:
    if current and current[-1][1]-current[0][1]>8:runs.append(current)
    current=[(at,q)] if close else []
  if current and current[-1][1]-current[0][1]>8:runs.append(current)
  intervals=[]
  for run in runs:
   lo,qa=run[0];hi,qb=run[-1];pa=axis.interpolate(qa);pb=axis.interpolate(qb);oa=offset.project(pa);ob=offset.project(pb);middle=substring(offset,oa,ob)
   patch=LineString([tuple(g.interpolate(lo).coords[0])]+list(middle.coords)+[tuple(g.interpolate(hi).coords[0])])
   if patch.intersects(obstacles) or not region.buffer(.2).covers(patch):
    log.append({'direction':name,'reference':reference,'offset_m':delta,'pitch_m':pitch,'reference_interval_m':[qa,qb],'geometry':middle.__geo_interface__,'rejected':True,'reason':'Gedeelde offset kan hier niet zonder terreinobstakel worden opgebouwd'})
    continue
   intervals.append((lo,hi,middle));log.append({'direction':name,'reference':reference,'offset_m':delta,'pitch_m':pitch,'reference_interval_m':[qa,qb],'geometry':middle.__geo_interface__})
  if intervals:
   coords=[];at=0
   for lo,hi,middle in intervals:coords+=list(substring(g,at,lo).coords)+list(middle.coords);at=hi
   if at<g.length-.000001:coords+=list(substring(g,at,g.length).coords)
   clean=[coords[0]]
   for p in coords[1:]:
    if math.dist(clean[-1],p)>.000001:clean.append(p)
   candidate=LineString(clean)
   if not candidate.is_simple:
    for row in log:
     if row['direction']==name:row.update(rejected=True,reason='Gedeelde offset kan hier niet zonder lus worden aangesloten')
    continue
   result[name]=candidate
 if _secondary:
  pure=[d for d in directions if not d.get('feed')]
  for first,second in itertools.combinations(pure,2):
   a,b=first['id'],second['id'];outside=result[a].intersection(result[b].buffer(1)).difference(axis.buffer(2))
   if outside.length<8:continue
   pair,extra=shared_offsets({a:result[a],b:result[b]},[first,second],obstacles,region,pitch,False)
   for row in extra:
    changed=__import__('shapely').geometry.shape(row['geometry'])
    log=[prior for prior in log if not (prior['direction']==row['direction'] and __import__('shapely').geometry.shape(prior['geometry']).intersection(changed.buffer(.01)).length>.001)]
   result.update(pair);log+=extra
 return result,log
