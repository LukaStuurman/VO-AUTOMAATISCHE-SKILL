"""Houd lanevolgorde door lokaal een gedeelde offset-as door te trekken."""
import itertools,math

def straighten(line,obstacles,max_deviation=.9):
 from shapely.geometry import LineString
 points=list(line.coords);out=[points[0]];i=0
 while i<len(points)-1:
  best=i+1
  for j in range(i+2,len(points)):
   chord=LineString([points[i],points[j]]);old=LineString(points[i:j+1])
   if old.hausdorff_distance(chord)>max_deviation:break
   if chord.intersects(obstacles):continue
   best=j
  out.append(points[best]);i=best
 return LineString(out)

def crossing_pairs(lines,excluded,ignored=None):
 ignored=ignored or set()
 return [(a,b,g.intersection(h).difference(excluded)) for (a,g),(b,h) in itertools.combinations(lines.items(),2) if frozenset([a,b]) not in ignored and not g.intersection(h).difference(excluded).is_empty]

def repair_bundle(lines,pitch,excluded,obstacles=None,fixed=None,ignored=None):
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 lines=dict(lines);log=[];fixed=fixed or set();ignored=ignored or set()
 def score(candidate):
  pairs=crossing_pairs(candidate,excluded,ignored)
  return len(pairs),sum(len(q.geoms) if hasattr(q,'geoms') else 1 for _,_,q in pairs)
 for iteration in range(30):
  initial=score(lines)
  if initial[0]==0:return lines,log
  best=None
  for a,b,q in crossing_pairs(lines,excluded,ignored):
   parts=list(q.geoms) if hasattr(q,'geoms') else [q]
   points=[]
   for part in parts:
    if part.geom_type=='Point':points.append(part)
    elif part.geom_type=='LineString':points.extend([Point(part.coords[0]),Point(part.coords[-1])])
   if not points:continue
   for reference,changed in [(a,b),(b,a)]:
    if changed in fixed:continue
    axis=lines[reference];old=lines[changed];positions=[old.project(p) for p in points]
    for margin in [2,4,8,12,20]:
     lo=max(.01,min(positions)-margin);hi=min(old.length-.01,max(positions)+margin)
     if hi<=lo:continue
     start=old.interpolate(lo);end=old.interpolate(hi)
     for side in [sign*multiple for multiple in range(1,len(lines)+1) for sign in [-1,1]]:
      offset=axis.offset_curve(side*pitch,join_style=2,mitre_limit=2)
      if offset.geom_type!='LineString':continue
      x=offset.project(start);y=offset.project(end)
      if y<=x:continue
      middle=substring(offset,x,y)
      prefix=substring(old,0,lo);suffix=substring(old,hi,old.length)
      coords=list(prefix.coords)+list(middle.coords)+list(suffix.coords)
      clean=[coords[0]]
      for p in coords[1:]:
       if math.dist(clean[-1],p)>.001:clean.append(p)
      candidate=LineString(clean)
      if not candidate.is_simple or candidate.hausdorff_distance(old)>pitch*8:continue
      if obstacles is not None and candidate.intersection(obstacles).length>old.intersection(obstacles).length+.001:continue
      changed_lines=dict(lines);changed_lines[changed]=candidate;newscore=score(changed_lines)
      if newscore>=initial:continue
      cost=(newscore,candidate.hausdorff_distance(old),abs(candidate.length-old.length))
      if best is None or cost<best[0]:best=(cost,changed,candidate,reference,margin,side)
  if best is None:break
  _,changed,candidate,reference,margin,side=best
  log.append({'direction':changed,'axis_direction':reference,'offset_m':side*pitch,'transition_margin_m':margin,'length_delta_m':candidate.length-lines[changed].length})
  lines[changed]=candidate
 return lines,log

def straight_road_crossings(line,road,obstacles):
 from shapely.geometry import LineString
 from shapely.ops import substring
 q=line.intersection(road);parts=list(q.geoms) if hasattr(q,'geoms') else [q];intervals=[]
 for p in parts:
  if p.geom_type!='LineString' or p.length<1:continue
  chord=LineString([p.coords[0],p.coords[-1]])
  if p.hausdorff_distance(chord)<.01 or chord.intersects(obstacles):continue
  lo=line.project(__import__('shapely').geometry.Point(p.coords[0]));hi=line.project(__import__('shapely').geometry.Point(p.coords[-1]))
  if hi>lo:intervals.append((lo,hi,chord))
 if not intervals:return line
 result=[];at=0
 for lo,hi,chord in sorted(intervals):
  result+=list(substring(line,at,lo).coords)+list(chord.coords);at=hi
 result+=list(substring(line,at,line.length).coords);clean=[result[0]]
 for p in result[1:]:
  if math.dist(p,clean[-1])>.001:clean.append(p)
 return LineString(clean)
