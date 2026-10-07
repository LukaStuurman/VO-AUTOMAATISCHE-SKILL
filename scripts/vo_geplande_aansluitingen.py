"""Geplande service naar de dichtstbijzijnde passende nieuwe of behouden main.

De nieuwe aansluitkabel is een ontwerpkeuze, geen fictieve WFS-aansluiting.
"""
import copy

def assign_planned(records,directions,chains,clearance=.6):
 from shapely.geometry import shape,Point
 from shapely.ops import nearest_points
 from vo_paden import geometry_checks
 def geometry(g):return shape(g) if isinstance(g,dict) else g
 def load(rows):return max(sum(r['current_A'] for r in rows),sum(r.get('kabel_opwek_A',0) for r in rows))
 planned=[r for r in records if r.get('planned_connection')];log=[]
 for d in directions:
  d['records']=[r for r in d['records'] if not r.get('planned_connection')];d['load_A']=load(d['records'])
 for r in planned:
  point=Point(r['xy']);options=[]
  for i,d in enumerate(directions):
   main=geometry(d.get('display_main') or max(d['new_paths'],key=lambda p:geometry(p).length));contacts=[]
   for part in d['retained']:
    chain=geometry(chains[part['code']]);_,tap=nearest_points(point,geometry(part['geometry']));at=chain.project(tap)
    at=min(part['hi']-clearance,max(part['lo']+clearance,at)) if part['hi']-part['lo']>2*clearance else (part['lo']+part['hi'])/2;tap=chain.interpolate(at)
    contacts.append((tap,{'code':part['code'],'tap':list(tap.coords[0][:2]),'chain_position_m':at,'new_connection':False,'overzetter':False,'planned_main_status':'retained'}))
   _,tap=nearest_points(point,main);contacts.append((tap,{'code':None,'tap':list(tap.coords[0][:2]),'new_tap':list(tap.coords[0][:2]),'new_connection':True,'overzetter':True,'planned_main_status':'new'}))
   for tap,values in contacts:
    candidate=dict(r,**values);candidate.update(planned_contact_distance_m=tap.distance(point),planned_contact_basis='Nieuwe geplande aansluitkabel naar gekozen actieve LS-hoofdkabel; geen bestaande WFS-aansluiting',direction=d.get('id'))
    if not values['new_connection']:candidate.pop('new_tap',None)
    trial=copy.copy(d);trial.update(records=d['records']+[candidate],load_A=load(d['records']+[candidate]),profile=d.get('profile','laatste_helft'));calc=geometry_checks(trial,main)
    if calc['selected']['passes']:options.append((tap.distance(point),i,values['new_connection'],candidate,calc))
  if not options:raise ValueError('Geen passende hoofdkabel voor geplande aansluiting '+r['id'])
  _,i,_,candidate,calc=min(options,key=lambda item:item[:3]);d=directions[i];r.clear();r.update(candidate);d['records'].append(r);d['load_A']=load(d['records']);d['limiting']=calc['selected']['limiting'];d['passes']=True
  log.append({'connection_id':r['id'],'direction':d.get('id'),'main_status':r['planned_main_status'],'code':r['code'],'tap':r['tap'],'distance_m':r['planned_contact_distance_m'],'wfs_service_created':False})
 return log
