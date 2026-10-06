"""Een oversteek is recht én haaks op de lokale wegstrekking."""
import math

def road_axis(crossing,road):
 from shapely.geometry import LineString,Point
 polygons=list(road.geoms) if hasattr(road,'geoms') else [road];mid=crossing.interpolate(.5,normalized=True);edges=[]
 for poly in polygons:
  if poly.distance(mid)>3:continue
  rings=[poly.exterior]+list(poly.interiors)
  for ring in rings:
   points=list(LineString(ring.coords).simplify(.15).coords)
   for a,b in zip(points,points[1:]):
    L=math.dist(a,b);edge=LineString([a,b])
    if L<2 or edge.distance(mid)>15:continue
    edges.append((edge,(b[0]-a[0],b[1]-a[1]),L))
 vectors=[]
 for endpoint in [crossing.coords[0],crossing.coords[-1]]:
  point=Point(endpoint)
  if not edges:raise ValueError('Geen onderbouwde lokale wegrichting voor oversteek.')
  edge,v,L=min(edges,key=lambda e:e[0].distance(point)+.01/max(1,e[2]));vectors.append((v[0]/L,v[1]/L))
 a,b=vectors
 if a[0]*b[0]+a[1]*b[1]<0:b=(-b[0],-b[1])
 u=(a[0]+b[0],a[1]+b[1]);L=math.hypot(*u)
 if L<.1:raise ValueError('Ambigue lokale wegstrekking.')
 return (u[0]/L,u[1]/L)

def crossing_angle(crossing,road,axis=None):
 u=axis or road_axis(crossing,road);a,b=crossing.coords[0],crossing.coords[-1];v=(b[0]-a[0],b[1]-a[1]);L=math.hypot(*v);dot=abs((v[0]*u[0]+v[1]*u[1])/L)
 return math.degrees(math.acos(min(1,dot)))

def crossing_sites(lines,road,pitch=.2):
 from shapely.geometry import Point
 groups=[]
 for name,line in lines.items():
  q=line.intersection(road);parts=list(q.geoms) if hasattr(q,'geoms') else [q]
  for p in parts:
   if p.geom_type!='LineString' or p.length<1:continue
   mid=p.interpolate(.5,normalized=True);group=next((g for g in groups if g[0][2].distance(mid)<3),None)
   if group is None:group=[];groups.append(group)
   group.append((name,p,mid,road_axis(p,road)))
 sites=[]
 for i,group in enumerate(groups):
  ref=group[0][3];vectors=[u if u[0]*ref[0]+u[1]*ref[1]>=0 else (-u[0],-u[1]) for _,_,_,u in group];x=sum(u[0] for u in vectors);y=sum(u[1] for u in vectors);L=math.hypot(x,y);u=(x/L,y/L);mid=Point(sum(p.x for _,_,p,_ in group)/len(group),sum(p.y for _,_,p,_ in group)/len(group));ordered=sorted(group,key=lambda item:(item[2].x-mid.x)*u[0]+(item[2].y-mid.y)*u[1]);centres={name:[mid.x+u[0]*(rank-(len(group)-1)/2)*pitch,mid.y+u[1]*(rank-(len(group)-1)/2)*pitch] for rank,(name,_,_,_) in enumerate(ordered)}
  sites.append({'id':f'oversteek-{i+1}','xy':[mid.x,mid.y],'road_axis':list(u),'lane_centres':centres})
 return sites

def perpendicular_crossings(line,road,obstacles,region=None,name=None,sites=None,retained=None):
 from shapely.geometry import LineString,Point
 from shapely.ops import substring
 q=line.intersection(road);parts=list(q.geoms) if hasattr(q,'geoms') else [q];changes=[];current=line
 for p in parts:
  if p.geom_type!='LineString' or p.length<1:continue
  old_mid=p.interpolate(.5,normalized=True);site=min(sites,key=lambda s:Point(s['xy']).distance(old_mid)) if sites else None;axis=tuple(site['road_axis']) if site else road_axis(p,road)
  if crossing_angle(p,road,axis)>=89.999:continue
  normal=(-axis[1],axis[0]);mid=Point(site['lane_centres'][name]) if site and name in site['lane_centres'] else old_mid
  ideal=LineString([(mid.x-normal[0]*25,mid.y-normal[1]*25),(mid.x+normal[0]*25,mid.y+normal[1]*25)]);inside=ideal.intersection(road);pieces=list(inside.geoms) if hasattr(inside,'geoms') else [inside];pieces=[g for g in pieces if g.geom_type=='LineString' and g.distance(mid)<.1]
  if not pieces:continue
  crossing=min(pieces,key=lambda g:g.distance(mid));a,b=Point(crossing.coords[0]),Point(crossing.coords[-1]);start,end=Point(p.coords[0]),Point(p.coords[-1])
  if a.distance(start)+b.distance(end)>b.distance(start)+a.distance(end):a,b=b,a
  # Connect to the pavements OUTSIDE the carriageway; no diagonal lead-ins in it.
  v=(b.x-a.x,b.y-a.y);L=math.hypot(*v);v=(v[0]/L,v[1]/L);lo=current.project(start);hi=current.project(end);before=max(0,lo-3);after=min(current.length,hi+3)
  # A wide turn margin may overshoot a retained main in the pavement. Use
  # the largest safe margin, with both bends still outside the carriageway.
  for margin in [1,.75,.5,.35,.2,.1]:
   pa=(a.x-v[0]*margin,a.y-v[1]*margin);pb=(b.x+v[0]*margin,b.y+v[1]*margin)
   coords=list(substring(current,0,before).coords)+[pa,pb]+list(substring(current,after,current.length).coords);candidate=LineString(coords)
   replacement=LineString([current.interpolate(before),pa,pb,current.interpolate(after)])
   if not candidate.is_simple or replacement.intersects(obstacles) or (retained is not None and replacement.intersects(retained)) or (region is not None and not region.buffer(.2).covers(replacement)):continue
   check=candidate.intersection(road);segments=list(check.geoms) if hasattr(check,'geoms') else [check]
   local=[g for g in segments if g.geom_type=='LineString' and g.distance(mid)<3 and g.length>1]
   if not local or any(crossing_angle(g,road,axis)<89.999 or g.hausdorff_distance(LineString([g.coords[0],g.coords[-1]]))>.02 for g in local):continue
   changes.append({'site':site['id'] if site else None,'before_angle_deg':crossing_angle(p,road,axis),'after_angle_deg':crossing_angle(local[0],road,axis),'outside_turn_margin_m':margin,'geometry':crossing.__geo_interface__});current=candidate;break
 return current,changes
