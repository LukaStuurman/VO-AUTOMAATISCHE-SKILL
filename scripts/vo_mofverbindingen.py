"""Moffen volgen echte verbindingen en reeds aanwezige bronobjecten."""
import math

def align_splice_contacts(directions,lines,original_chains,tolerance=.01,obstacles=None,region=None):
 from shapely.geometry import Point,shape
 from shapely.ops import substring
 log=[]
 def points(g):
  if g.geom_type=='Point':return [g]
  if g.geom_type=='LineString':return [] if g.is_empty else [Point(g.coords[0]),Point(g.coords[-1])]
  return [p for part in getattr(g,'geoms',[]) for p in points(part)]
 for d in directions:
  if not d.get('feed'):continue
  main=lines[d['id']];original=original_chains[d['primary_code']];old=Point(d['feed']['xy']);part=next(p for p in d['retained'] if p['code']==d['primary_code'])
  if not d['new_codes'] and len(main.coords)>=3:
   from shapely.geometry import LineString
   others=[g for name,g in lines.items() if name!=d['id']]
   requirements=[r['chain_position_m'] for r in d['records'] if r['code']==d['primary_code'] and not r.get('new_connection')]+[d['parent_child_positions'][p['code']]['parent_position'] for p in d['retained'] if p['code']!=d['primary_code']]
   # Stop at the first usable contact rather than crossing the same retained
   # cable and then returning to an earlier provisional splice location.
   for contact in sorted(points(main.intersection(shape(part['geometry']))),key=main.project):
    root=original.project(contact);at=main.project(contact)
    if contact.distance(old)>10 or main.length-at<.2 or not requirements:continue
    if min(requirements)>root+.01 and old.distance(Point(original.interpolate(part['lo'])))<.02:lo,hi=root,part['hi']
    elif max(requirements)<root-.01 and old.distance(Point(original.interpolate(part['hi'])))<.02:lo,hi=part['lo'],root
    else:continue
    new=substring(main,0,at);retained=substring(original,lo,hi)
    if not new.is_simple or any(not new.intersection(g).is_empty or not retained.intersection(g).is_empty for g in others):continue
    main=new;lines[d['id']]=main;part.update(lo=lo,hi=hi,geometry=retained.__geo_interface__);d['feed'].update(xy=list(contact.coords[0]),position_m=root)
    log.append({'direction':d['id'],'old_xy':list(old.coords[0]),'new_xy':d['feed']['xy'],'reason':'Eerste bruikbare kabelcontact voorkomt kruisen en teruglopen; alle aansluitingen blijven gevoed'});old=contact;break
   def conflicts(new,retained):return sum(not new.intersection(g).is_empty for g in others)+sum(not retained.intersection(g).is_empty for g in others)
   initial=conflicts(main,shape(part['geometry']));choices=[];coords=list(main.coords)
   if initial:
    for i in range(1,len(coords)-1):
     if main.length-main.project(Point(coords[i]))>20:continue
     a,b=coords[i-1],coords[i];length=math.dist(a,b)
     if length<.2:continue
     u=((b[0]-a[0])/length,(b[1]-a[1])/length);ray=LineString([(b[0]-u[0]*15,b[1]-u[1]*15),(b[0]+u[0]*15,b[1]+u[1]*15)])
     for contact in points(ray.intersection(original)):
      if contact.distance(old)>10:continue
      root=original.project(contact)
      if not part['lo']-.001<=root<=part['hi']+.001:continue
      lo=min(part['lo'],root);hi=max(part['hi'],root)
      if requirements and min(requirements)>=root-.001:lo=root
      if requirements and max(requirements)<=root+.001:hi=root
      retained=substring(original,lo,hi);new=LineString(coords[:i]+[tuple(contact.coords[0])]);score=conflicts(new,retained)
      if score>=initial or not new.is_simple or (region is not None and not region.buffer(.2).covers(new)):continue
      if obstacles is not None and new.intersection(obstacles).length>main.intersection(obstacles).length+1e-6:continue
      used=[shape(p['geometry']) for other in directions if other is not d for p in other['retained'] if p['code']==d['primary_code']]
      if any(retained.intersection(g).length>1e-6 for g in used):continue
      choices.append((score,new.length+retained.length,new,contact,root,lo,hi))
   if choices:
    _,_,main,contact,root,lo,hi=min(choices,key=lambda c:c[:2]);lines[d['id']]=main;part.update(lo=lo,hi=hi,geometry=substring(original,lo,hi).__geo_interface__);d['feed'].update(xy=list(contact.coords[0]),position_m=root);log.append({'direction':d['id'],'old_xy':list(old.coords[0]),'new_xy':d['feed']['xy'],'reason':'Mof op lokale doorlopende kabeltangent; aansluitingen behouden en kruisingen verminderd'});old=contact
  if main.distance(old)>tolerance:
   candidates=points(main.intersection(original))
   if not candidates:raise ValueError('Nieuwe richting raakt bestaande kabel niet bij de mof: '+d['id'])
   contact=min(candidates,key=lambda p:p.distance(old))
   if contact.distance(old)>10:raise ValueError('Mofcontact te ver van eerdere locatie: '+d['id'])
   d['feed']['xy']=list(contact.coords[0]);d['feed']['position_m']=original.project(contact);part['lo']=min(part['lo'],d['feed']['position_m']);part['hi']=max(part['hi'],d['feed']['position_m'])
   log.append({'direction':d['id'],'old_xy':list(old.coords[0]),'new_xy':d['feed']['xy'],'reason':'Mof op werkelijk snijpunt van nieuwe en bestaande hoofdkabel'})
  root=d['feed']['position_m'];requirements=[r['chain_position_m'] for r in d['records'] if r['code']==d['primary_code'] and not r.get('new_connection')]+[d['parent_child_positions'][p['code']]['parent_position'] for p in d['retained'] if p['code']!=d['primary_code']]
  # A VM has one retained arm; an unserved arm on the other side is not
  # retained solely because an earlier interval extended beyond the splice.
  before=(part['lo'],part['hi'])
  if requirements and min(requirements)>=root-.001:part['lo']=root
  if requirements and max(requirements)<=root+.001:part['hi']=root
  part['geometry']=substring(original,part['lo'],part['hi']).__geo_interface__
  if before!=(part['lo'],part['hi']):log.append({'direction':d['id'],'code':part['code'],'old_interval':list(before),'new_interval':[part['lo'],part['hi']],'reason':'Ongebruikte arm afknippen bij voedingsmof; alle eigen hoofd-/aftaklast behouden'})
  d['feed']['path']=substring(main,0,main.project(Point(d['feed']['xy']))).__geo_interface__
  arms=int(part['lo']<root-.001)+int(part['hi']>root+.001)+1
  if d['new_codes'] and main.length-main.project(Point(d['feed']['xy']))>.1:arms+=1
  d['splice_kind']='AM' if arms>=3 else 'VM';d['splice_arms']=arms
 return log

def existing_branch_evidence(point,joints,tolerance=.1):
 matches=[j for j in joints if math.dist(point,j['xy'])<=tolerance]
 return matches[0] if matches else None
