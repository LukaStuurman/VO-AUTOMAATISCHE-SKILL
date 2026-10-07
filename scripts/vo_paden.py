"""Fysiek einde en laatste aansluiting met dezelfde belastingen/vertakkingen."""
from reken_richtingen import calculate_path,CATALOGUE

def geometry_checks(d,main):
 from shapely.geometry import Point,shape
 from vo_materialen import segments_between
 physical=[];last=[];coverage=[]
 def add(target,name,segments):
  if sum(s['length_m'] for s in segments)>.001:target.append({'id':name,'segments':segments})
 def segment(name,kind,length):return {'id':name,'type':kind,'length_m':length}
 new_records=[r for r in d['records'] if r['code'] in d['new_codes'] or r.get('new_connection')]
 if new_records:
  add(physical,'new-main',[segment('new-main','150Al',main.length)])
  taps=[main.project(Point(r.get('new_tap',r['tap']))) for r in new_records]
  add(last,'new-last-connection',[segment('new-main','150Al',max(taps))]);coverage.extend(r['id'] for r in new_records)
 if d.get('feed'):
  feeder=main.project(Point(d['feed']['xy']));root=d['feed']['position_m'];parent=next(p for p in d['retained'] if p['code']==d['primary_code'])
  for part in d['retained']:
   code=part['code'];records=[r for r in d['records'] if r['code']==code and not r.get('new_connection')];positions=[r['chain_position_m'] for r in records]
   if code==d['primary_code']:
    joins=[d['parent_child_positions'][p['code']]['parent_position'] for p in d['retained'] if p['code']!=code];positions+=joins
    for side,end in [(-1,part['lo']),(1,part['hi'])]:
     values=[q for q in positions if (q-root)*side>=-.001];L=abs(end-root)
     add(physical,code+f'-{side}',[segment('feed','150Al',feeder)]+segments_between(part,root,end,'main'))
     if values:add(last,code+f'-last-{side}',[segment('feed','150Al',feeder)]+segments_between(part,root,max(values,key=lambda q:abs(q-root)),'main'))
   else:
    join=d['parent_child_positions'][code];g=shape(part['geometry']) if isinstance(part['geometry'],dict) else part['geometry'];branch_root=g.project(Point(join['xy']))+part['lo'];parent_length=abs(join['parent_position']-root)
    for side,end in [(-1,part['lo']),(1,part['hi'])]:
     prefix=[segment('feed','150Al',feeder)]+segments_between(parent,root,join['parent_position'],'parent');L=abs(end-branch_root);values=[q for q in positions if (q-branch_root)*side>=-.001]
     if L>.001:add(physical,code+f'-{side}',prefix+segments_between(part,branch_root,end,'branch'))
     if values:add(last,code+f'-last-{side}',prefix+segments_between(part,branch_root,max(values,key=lambda q:abs(q-branch_root)),'branch'))
   coverage.extend(r['id'] for r in records)
 def check(paths):
  checks=[calculate_path(p,d['profile'],CATALOGUE) for p in paths];limit=min(checks,key=lambda c:(c['max_fuse_A'],-c['Z_ohm']));return {'paths':paths,'checks':checks,'limiting':limit,'passes':d['load_A']<=limit['max_design_A']+1e-8}
 physical_check=check(physical);last_check=check(last)
 if set(coverage)!={r['id'] for r in d['records']}:raise ValueError('Laatste-aansluitingvariant mist toegewezen aansluitingen.')
 selected=physical_check if physical_check['passes'] else last_check
 return {'physical':physical_check,'last_connection':last_check,'selected_endpoint':'physical' if physical_check['passes'] else 'last_connection','same_connection_ids':sorted(coverage),'selected':selected}
