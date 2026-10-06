"""Moffen volgen echte verbindingen en reeds aanwezige bronobjecten."""
import math

def align_splice_contacts(directions,lines,original_chains,tolerance=.01):
 from shapely.geometry import Point,shape
 from shapely.ops import substring
 log=[]
 def points(g):
  if g.geom_type=='Point':return [g]
  if g.geom_type=='LineString':return [Point(g.coords[0]),Point(g.coords[-1])]
  return [p for part in getattr(g,'geoms',[]) for p in points(part)]
 for d in directions:
  if not d.get('feed'):continue
  main=lines[d['id']];original=original_chains[d['primary_code']];old=Point(d['feed']['xy']);part=next(p for p in d['retained'] if p['code']==d['primary_code'])
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
