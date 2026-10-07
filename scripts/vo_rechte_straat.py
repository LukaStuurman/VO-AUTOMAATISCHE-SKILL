"""Eén lange rechte bundel langs een bomenrij, met constante lanevolgorde."""
import math

def straighten_street_bundle(lines,names,obstacles,surfaces,road,region,pitch=.2,tree_points=(),anchors=None):
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 chosen=[n for n in lines if n in names]
 if len(chosen)<2:return lines,None
 reference=chosen[(len(chosen)-1)//2];axis=lines[reference];coords=list(axis.coords);positions=[axis.project(Point(p)) for p in coords];options=[]
 for i in range(1,len(coords)-2):
  for j in range(i+2,len(coords)):
   a,b=coords[i],coords[j];length=math.dist(a,b)
   if length<45:continue
   old=substring(axis,positions[i],positions[j]);chord=LineString([a,b])
   if old.length>length*1.15 or old.hausdorff_distance(chord)>4:continue
   # Consider only a shared street. Shorter directions may end within it.
   companions=[n for n in chosen if lines[n].distance(chord.interpolate(.5,normalized=True))<2]
   if len(companions)<2:continue
   options.append((-length,i,j,companions))
 local_obstacles=obstacles.intersection(axis.envelope.buffer(5));allowed=surfaces.buffer(.2);best=None
 anchors=anchors or {}
 for neg_length,i,j,companions in sorted(options)[:80]:
  a,b=coords[i],coords[j];L=-neg_length;u=((b[0]-a[0])/L,(b[1]-a[1])/L);normal=(-u[1],u[0]);pair_best=None
  for offset in [0]+[sign*k*.1 for k in range(1,31) for sign in [-1,1]]:
   replacements={};changed=[];valid=True
   for n in chosen:
    g=lines[n];lo=g.project(Point(a));hi=g.project(Point(b))
    if hi-lo<10:continue
    old=substring(g,lo,hi)
    if old.hausdorff_distance(LineString([a,b]))>max(4,L-(hi-lo)+4):continue
    pa=g.interpolate(lo);pb=g.interpolate(hi);ta=max(0,min(L,(pa.x-a[0])*u[0]+(pa.y-a[1])*u[1]));tb=max(0,min(L,(pb.x-a[0])*u[0]+(pb.y-a[1])*u[1]));lane=offset+(chosen.index(n)-chosen.index(reference))*pitch
    start=(a[0]+ta*u[0]+lane*normal[0],a[1]+ta*u[1]+lane*normal[1]);end=(a[0]+tb*u[0]+lane*normal[0],a[1]+tb*u[1]+lane*normal[1]);middle=LineString([start,end]);patch=LineString([pa,start,end,pb]);prefix=list(substring(g,0,lo).coords);suffix=list(substring(g,hi,g.length).coords)[1:] if hi<g.length-.001 else [];candidate=LineString(prefix+[start,end]+suffix)
    if not candidate.is_simple or any(candidate.distance(Point(p))>.01 for p in anchors.get(n,[])) or patch.intersects(local_obstacles) or not region.buffer(.2).covers(patch) or not allowed.covers(patch):valid=False;break
    if patch.intersection(road).length>old.intersection(road).length+.02:valid=False;break
    nearby=[p for p in tree_points if middle.distance(p)<4]
    signs=[(p.x-start[0])*normal[0]+(p.y-start[1])*normal[1] for p in nearby]
    if signs and min(signs)<-.05 and max(signs)>.05:valid=False;break
    replacements[n]=candidate;changed.append(middle)
   if not valid or len(replacements)!=len(chosen):continue
   if all(g.hausdorff_distance(lines[n])<.001 for n,g in replacements.items()):continue
   trial=dict(lines,**replacements)
   # Local changes must not introduce any cable crossings.
   if any(not g.intersection(h).difference(lines[n].intersection(lines[m]).buffer(.01)).is_empty for n,g in replacements.items() for m,h in trial.items() if n!=m):continue
   clearance=min(g.distance(local_obstacles) for g in changed);road_length=sum(g.intersection(road).length for g in changed);score=L+min(clearance,1.5)*5-abs(offset)*.1-road_length*100
   if pair_best is None or score>pair_best[0]:pair_best=(score,trial,{'directions':list(replacements),'straight_length_m':L,'offset_m':offset,'clearance_m':clearance,'start':list(a),'end':list(b),'old_vertices':j-i+1,'new_vertices':2})
  if pair_best:
   best=pair_best;break
 return (best[1],best[2]) if best else (lines,None)
