"""Kies een ruim recht straattracé en een doorgaande aanloop naar een mof."""
import math

def straight_frontage(line,obstacles,surfaces,road,region,margin=1.0,house_points=(),other_lines=()):
 from shapely.geometry import LineString
 from shapely.ops import substring
 obstacles=obstacles.intersection(line.envelope.buffer(7));expanded=obstacles.buffer(margin);body=obstacles.buffer(.35);allowed=surfaces.buffer(.25);area=region.buffer(.2)
 points=list(line.coords);positions=[line.project(__import__('shapely').geometry.Point(p)) for p in points];best=None;options=[]
 for i in range(1,len(points)-3):
  for j in range(i+3,len(points)):
   old=substring(line,positions[i],positions[j]);a,b=points[i],points[j];L=math.dist(a,b)
   if L<45 or old.length>L*1.12:continue
   chord=LineString([a,b])
   if old.hausdorff_distance(chord)>4:continue
   options.append((-L,i,j,old,a,b))
 accepted_pairs=0
 for neg_length,i,j,old,a,b in sorted(options)[:160]:
   L=-neg_length;old_off=old.difference(allowed).length;old_road=old.intersection(road).length;normal=(-(b[1]-a[1])/L,(b[0]-a[0])/L);pair_accepted=False
   for offset in [0]+[s*m*.5 for m in range(1,9) for s in [-1,1]]:
    start=(a[0]+normal[0]*offset,a[1]+normal[1]*offset);end=(b[0]+normal[0]*offset,b[1]+normal[1]*offset)
    middle=LineString([start,end]);prefix=list(substring(line,0,positions[i]).coords)
    suffix=list(substring(line,positions[j],line.length).coords)[1:] if j<len(points)-1 else []
    candidate=LineString(prefix+[start,end]+suffix)
    changed=LineString([a,start,end]+([points[j+1]] if j<len(points)-1 else []))
    if not candidate.is_simple or middle.intersects(expanded) or changed.intersects(body):continue
    if any(not candidate.intersection(g).difference(line.intersection(g).buffer(.01)).is_empty for g in other_lines):continue
    if not area.covers(changed) or changed.difference(allowed).length>old_off+.3:continue
    if changed.intersection(road).length>old_road+.25:continue
    # Prefer sufficient room and few bends; do not keep pushing a cable out of
    # the public pavement merely to maximise an arbitrary clearance score.
    clearance=min(margin+.5,middle.distance(obstacles));house_distance=sum(middle.distance(p) for p in house_points)/len(house_points) if house_points else 0;score=L+clearance*8-(abs(offset)*.3)-house_distance*3
    pair_accepted=True
    if best is None or score>best[0]:best=(score,candidate,{'old_length_m':old.length,'straight_length_m':middle.length,'offset_m':offset,'vegetation_clearance_m':middle.distance(obstacles),'mean_distance_to_houses_m':house_distance,'old_vertices':j-i+1,'new_vertices':2,'start':list(start),'end':list(end)})
   accepted_pairs+=pair_accepted
   if accepted_pairs>=4:break
 if best is None:return line,None
 return best[1],best[2]

def earlier_joint_approach(line,joint,obstacles,surfaces,region,margin=.6,road=None,guide=None):
 from shapely.geometry import Point,LineString
 from shapely.ops import substring
 at=line.project(Point(joint));point=line.interpolate(at)
 if point.distance(Point(joint))>.1 or at<20 or at>line.length-2:return line,None
 after=line.interpolate(min(line.length,at+6));out=(after.x-point.x,after.y-point.y);norm=math.hypot(*out)
 if norm<.1:return line,None
 direction=(out[0]/norm,out[1]/norm)
 if guide is not None:
  root=guide.project(point);choices=[guide.interpolate(max(0,root-12)),guide.interpolate(min(guide.length,root+12))];far=max(choices,key=lambda p:p.distance(point));L=far.distance(point)
  if L>3:direction=((point.x-far.x)/L,(point.y-far.y)/L)
 obstacles=obstacles.intersection(line.envelope.buffer(7));expanded=obstacles.buffer(margin);allowed=surfaces.buffer(.25);area=region.buffer(.2);best=None
 for back in range(8,65,2):
  q=max(1,at-back);start=line.interpolate(q);chord=LineString([start,point]);old=substring(line,q,at)
  if guide is not None:
   normal=(-direction[1],direction[0]);side=1 if (start.x-point.x)*normal[0]+(start.y-point.y)*normal[1]>=0 else -1
   near=(point.x-direction[0]*1.5+normal[0]*side*.2,point.y-direction[1]*1.5+normal[1]*side*.2);along=(start.x-near[0])*direction[0]+(start.y-near[1])*direction[1]
   if along>=-2:continue
   contact=(near[0]+along*direction[0],near[1]+along*direction[1]);chord=LineString([start,contact,near,point])
  incoming=(point.x-start.x,point.y-start.y);den=math.hypot(*incoming)*norm;cos=(incoming[0]*out[0]+incoming[1]*out[1])/den if den else -1
  if (guide is None and cos<.1) or chord.length>=old.length-.5:continue
  if chord.intersects(expanded) or not area.covers(chord):continue
  if chord.difference(allowed).length>old.difference(allowed).length+.3:continue
  if road is not None and chord.intersection(road).length>old.intersection(road).length+.5:continue
  if guide is not None and not chord.intersection(guide).difference(point.buffer(.2)).is_empty:continue
  prefix=list(substring(line,0,q).coords);suffix=list(substring(line,at,line.length).coords)[1:];candidate=LineString(prefix+list(chord.coords)[1:]+suffix)
  if not candidate.is_simple:continue
  saving=line.length-candidate.length
  score=saving-back*.02
  if best is None or score>best[0]:best=(score,candidate,{'earlier_crossing_by_m':back,'length_saved_m':saving,'turn_cosine':cos if guide is None else 1,'new_crossing':chord.__geo_interface__})
 return (best[1],best[2]) if best else (line,None)
