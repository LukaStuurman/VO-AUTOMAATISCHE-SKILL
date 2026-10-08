"""Voeg nabijgelegen oversteken van dezelfde weg samen vóór het aftakken."""
import math,heapq

def sidewalk_connection(a,b,free,region):
 from shapely.geometry import Point,LineString,box
 area=box(min(a[0],b[0])-6,min(a[1],b[1])-6,max(a[0],b[0])+6,max(a[1],b[1])+6);allowed=free.intersection(area).intersection(region.buffer(.2));direct=LineString([a,b])
 if allowed.buffer(.005).covers(direct):return direct
 nodes=[a,b];pieces=list(allowed.geoms) if hasattr(allowed,'geoms') else [allowed]
 for p in pieces:
  if p.geom_type!='Polygon':continue
  for ring in [p.exterior]+list(p.interiors):nodes+=list(ring.simplify(.08).coords)[:-1]
 nodes=list(dict.fromkeys(tuple(p) for p in nodes));graph=[[] for _ in nodes]
 for i,p in enumerate(nodes):
  for j in range(i):
   q=nodes[j];g=LineString([p,q])
   if allowed.buffer(.005).covers(g):graph[i].append((j,g.length));graph[j].append((i,g.length))
 dist={0:0};parent={};queue=[(0,0)]
 while queue:
  cost,i=heapq.heappop(queue)
  if i==1:break
  if cost>dist[i]+.001:continue
  for j,length in graph[i]:
   score=cost+length+.1
   if score<dist.get(j,math.inf):dist[j]=score;parent[j]=i;heapq.heappush(queue,(score,j))
 if 1 not in dist:raise ValueError('Geen voetpadverbinding na gezamenlijke oversteek.')
 chain=[1]
 while chain[-1]!=0:chain.append(parent[chain[-1]])
 return LineString([nodes[i] for i in chain[::-1]])

def merge_nearby_crossings(data,lines,road,obstacles,surfaces,region,pitch=.2):
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import substring
 sites=data['crossing_sites'];components=list(road.geoms) if hasattr(road,'geoms') else [road];order=[d['id'] for d in data['directions']];result=dict(lines);changes=[];rejected=[]
 clusters=[];assigned=set()
 for i,a in enumerate(sites):
  if i in assigned:continue
  group=[i]
  for j,b in enumerate(sites):
   if j<=i or j in assigned or math.dist(a['xy'],b['xy'])>25:continue
   dot=sum(x*y for x,y in zip(a['road_axis'],b['road_axis']))
   if abs(dot)<.98:continue
   normal=(-a['road_axis'][1],a['road_axis'][0]);across=abs((b['xy'][0]-a['xy'][0])*normal[0]+(b['xy'][1]-a['xy'][1])*normal[1])
   if across>2.5:continue
   if any(g.buffer(.1).covers(Point(a['xy'])) and g.buffer(.1).covers(Point(b['xy'])) for g in components):group.append(j)
  if len(group)>1:clusters.append(group);assigned.update(group)
 for group in clusters:
  keep=max(group,key=lambda i:len(sites[i]['lane_centres']));target=sites[keep];reference=min(target['lane_centres'],key=lambda n:order.index(n));axis=result[reference];moving=[n for i in group if i!=keep for n in sites[i]['lane_centres']]
  if len(set(moving))!=len(moving) or set(moving)&set(target['lane_centres']):continue
  moving.sort(key=lambda n:order.index(n));base=moving[0];old=result[base];delta=(order.index(base)-order.index(reference))*pitch
  def cross_interval(g,site):
   pieces=g.intersection(road);parts=list(pieces.geoms) if hasattr(pieces,'geoms') else [pieces];parts=[p for p in parts if p.geom_type=='LineString' and p.length>1];p=min(parts,key=lambda p:Point(site['xy']).distance(p));return sorted([g.project(Point(p.coords[0])),g.project(Point(p.coords[-1]))])
  _,ref_end=cross_interval(axis,target);guide=substring(axis,0,min(axis.length,ref_end+6)).offset_curve(delta,join_style=2,mitre_limit=10)
  if guide.geom_type!='LineString':continue
  _,end=cross_interval(guide,target);head=substring(guide,0,end+.7);old_site=next(sites[i] for i in group if base in sites[i]['lane_centres']);_,old_end=cross_interval(old,old_site);join=old_end+4;a=tuple(head.coords[-1]);b=tuple(old.interpolate(join).coords[0]);free=surfaces.buffer(.2).difference(road.buffer(.05)).difference(obstacles.buffer(.25));
  try:connector=sidewalk_connection(a,b,free,region)
  except ValueError as error:
   rejected.append({'site':target['id'],'directions':moving,'reason':str(error)});continue
  candidate=LineString(list(head.coords)+list(connector.coords)[1:]+list(substring(old,join,old.length).coords)[1:]);proposal={base:candidate};valid=True
  for name in moving[1:]:
   g=result[name];lane=candidate.offset_curve((order.index(name)-order.index(base))*pitch,join_style=2,mitre_limit=10);at=g.project(old.interpolate(join+2));p=g.interpolate(at);q=lane.project(p)
   if lane.geom_type!='LineString' or lane.distance(p)>.01:
    rejected.append({'site':target['id'],'directions':moving,'reason':'Parallelle aftak sluit niet exact aan: '+name});valid=False;break
   proposal[name]=LineString(list(substring(lane,0,q).coords)+list(substring(g,at,g.length).coords)[1:])
  if not valid:continue
  for name,g in proposal.items():
   if not g.is_simple or g.intersects(obstacles):
    rejected.append({'site':target['id'],'directions':moving,'reason':'Gezamenlijke oversteek raakt obstakel of maakt lus: '+name});valid=False;break
  if not valid:continue
  result.update(proposal)
  for name in moving:
   center=Point(target['xy']);shift=(order.index(name)-order.index(reference))*pitch;ref_center=target['lane_centres'][reference];target['lane_centres'][name]=[ref_center[0]+target['road_axis'][0]*shift,ref_center[1]+target['road_axis'][1]*shift]
  changes.append({'retained_site':target['id'],'removed_sites':[sites[i]['id'] for i in group if i!=keep],'directions':list(target['lane_centres']),'moved_directions':moving,'pitch_m':pitch,'branch_after_road':True})
 data['shared_crossing_failures']=rejected
 if changes:
  removed={n for c in changes for n in c['removed_sites']};data['crossing_sites']=[s for s in sites if s['id'] not in removed];data['shared_crossing_changes']=changes
  # Remove stale proofs for the replaced sections of moving directions.
  moved={n for c in changes for n in c['moved_directions']};proof=[]
  for row in data.get('shared_offset_rebuild',[]):
   piece=shape(row['geometry']);remaining=piece.intersection(result[row['direction']].buffer(.000001));parts=list(remaining.geoms) if hasattr(remaining,'geoms') else [remaining]
   for p in parts:
    if p.geom_type=='LineString' and p.length>1:proof.append(dict(row,geometry=p.__geo_interface__))
  data['shared_offset_rebuild']=proof
 return result,changes
