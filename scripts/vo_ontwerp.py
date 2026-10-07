"""Maak groepen en tracés uit bronkabels, ruimtelijke verbindingen en capaciteit."""
import math,collections,copy
from reken_richtingen import calculate_path,CATALOGUE,STEPS

def design(s,router,cfg,_partitions=None,_depth=0):
 from shapely.geometry import Point,LineString
 from shapely.ops import substring,nearest_points,unary_union,linemerge
 groups=s['groups'];parents={};attachment={};rules=cfg['rules']
 if _depth:
  router.weights=router.base_weights.copy();router.solve()
 def connect_joint(path,point):
  points=list(path.coords);xy=tuple(point.coords)[0]
  while len(points)>2:
   a,b=points[-2:];u=(b[0]-a[0],b[1]-a[1]);v=(xy[0]-b[0],xy[1]-b[1])
   if u[0]*v[0]+u[1]*v[1]>=0:break
   shortcut=LineString([a,xy])
   if shortcut.intersects(router.physical_obstacles):break
   points.pop()
  if math.dist(points[-1],xy)>.01:points.append(xy)
  return LineString(points)
 for c,g in groups.items():
  options=[]
  for p,main in groups.items():
   if p==c or not p.endswith('-00') or c.rsplit('-',1)[0]!=p.rsplit('-',1)[0] or main['geometry'].length<=g['geometry'].length:continue
   for xy in [g['geometry'].coords[0],g['geometry'].coords[-1]]:
    pos=main['geometry'].project(Point(xy));gap=main['geometry'].distance(Point(xy))
    if gap<.2 and 1<pos<main['geometry'].length-1:options.append((gap,p,pos,xy))
  if options:
   _,p,pos,xy=min(options);parents[c]=p;attachment[c]={'parent_position':pos,'xy':list(groups[p]['geometry'].interpolate(pos).coords)[0]}
 directions=[]
 def build(primary,mainrecords,children,lo,hi):
  pieces=[{'code':primary,'records':mainrecords,'lo':lo,'hi':hi}]+[{'code':c,'records':groups[c]['records'],'lo':0,'hi':groups[c]['geometry'].length} for c in children]
  records=mainrecords+[r for c in children for r in groups[c]['records']];load=sum(r['current_A'] for r in records)
  retained=[];newcodes=[]
  for part in pieces:
   c=part['code'];g=groups[c];cap=max(step[1] for step in STEPS if step[1]<=CATALOGUE[g['type']]['Imax'])
   retain=g['type']=='95Al' or load<=cap
   if retain:retained.append(dict(part,type=g['type'],combo=g['combo'],geometry=substring(g['geometry'],part['lo'],part['hi']),**({'material_segments':g['material_segments']} if 'material_segments' in g else {})))
   else:newcodes.append(c)
  directions.append({'primary_code':primary,'records':records,'new_codes':newcodes,'retained':retained,'source_children':children,'load_A':load,'lo':lo,'hi':hi,'parent_child_positions':attachment})
 for c,g in sorted(groups.items()):
  if c in parents:continue
  children=[x for x,p in parents.items() if p==c];allrecords=g['records']+[r for child in children for r in groups[child]['records']];load=sum(r['current_A'] for r in allrecords)
  if _partitions and c in _partitions:
   boundaries=[0]+sorted(_partitions[c])+[g['geometry'].length]
   for lo,hi in zip(boundaries,boundaries[1:]):
    own=[r for r in g['records'] if lo-.000001<=r['chain_position_m']<hi-.000001 or hi==g['geometry'].length and r['chain_position_m']>=lo];child=[x for x in children if lo<=attachment[x]['parent_position']<hi]
    if own or child:build(c,own,child,lo,hi)
   continue
  capacity=max(step[1] for step in STEPS if step[1]<=CATALOGUE[g['type']]['Imax'])
  if load>capacity and (g['type']=='95Al' or children):
   choices=[]
   cuts=[attachment[child]['parent_position'] for child in children]+[(a['chain_position_m']+b['chain_position_m'])/2 for a,b in zip(sorted(g['records'],key=lambda r:r['chain_position_m']),sorted(g['records'],key=lambda r:r['chain_position_m'])[1:])]
   for junction in cuts:
    for side in [-1,1]:
     cut=junction+side*rules.get('joint_separation_m',2)
     left=[r for r in g['records'] if r['chain_position_m']<=cut];right=[r for r in g['records'] if r['chain_position_m']>cut];lc=[x for x in children if attachment[x]['parent_position']<=cut];rc=[x for x in children if x not in lc]
     ll=sum(r['current_A'] for r in left)+sum(r['current_A'] for x in lc for r in groups[x]['records']);rl=load-ll
     if not left or not right or max(ll,rl)>capacity:continue
     choices.append(((ll-rl)**2,cut,left,right,lc,rc))
   if not choices:raise ValueError('Meer dan twee deelrichtingen nodig: '+c)
   _,cut,left,right,lc,rc=min(choices,key=lambda x:x[0]);build(c,left,lc,0,cut);build(c,right,rc,cut,g['geometry'].length)
  else:build(c,g['records'],children,0,g['geometry'].length)
 # Route replacement main cables from station, through their real LS tap neighbourhoods.
 core=[];code_paths={};codes={c for d in directions for c in d['new_codes']}
 def frontage_reach(c):
  records=sorted(groups[c]['records'],key=lambda r:r['chain_position_m']);return math.dist(records[0]['tap'],records[-1]['tap'])
 # Start with the longest straight housing frontage, then grow ONE trench.
 # Seeding every independently-shortest route would make redundant parallel trunks cheap.
 if rules.get('shared_trench_strategy')=='combined_candidates':
  core=[router.path(r['tap']) for d in directions for r in d['records'] if r['code'] in d['new_codes']];router.discount(core)
 for c in sorted(codes,key=frontage_reach,reverse=True):
  if core and rules.get('shared_trench_strategy')!='combined_candidates':router.discount(core)
  base_order=sorted(groups[c]['records'],key=lambda r:r['chain_position_m']);options=[];required=next(d['load_A'] for d in directions if c in d['new_codes'])
  for ordered in [base_order,base_order[::-1]]:
   points=list(router.path(ordered[0]['tap']).coords);paths=[LineString(points)];contacts={ordered[0]['id']:points[-1]}
   for previous,current in zip(ordered,ordered[1:]):
    section=router.between(previous['tap'],current['tap']);points.extend(list(section.coords)[1:]);contacts[current['id']]=points[-1];paths.append(LineString(points))
   check=calculate_path({'id':'orientation','segments':[{'id':'main','type':'150Al','length_m':paths[-1].length}]},'laatste_helft',CATALOGUE)
   deficit=max(0,required-check['max_design_A']);score=deficit*1000+router.dist[router.target(ordered[0]['tap'])]+paths[-1].length*.1;options.append((score,paths,contacts))
  _,paths,contacts=min(options,key=lambda x:x[0])
  for r in groups[c]['records']:r['new_tap']=contacts[r['id']]
  code_paths[c]=paths;core.append(paths[-1])
 router.discount(core)
 # A retained cable with loads on both sides of a transverse shared trench
 # cannot be kept as a continuous crossing. Split it into independent feeds
 # in the connection gap when another physical position is available.
 if core and len(directions)<len(cfg['direction_slots']) and _depth<4:
  options=[]
  for d in directions:
   if d['primary_code'] in d['new_codes']:continue
   chain=groups[d['primary_code']]['geometry'];own=sorted(r['chain_position_m'] for r in d['records'] if r['code']==d['primary_code'])
   if len(own)<2:continue
   for route in core:
    hit=chain.intersection(route);points=list(hit.geoms) if hasattr(hit,'geoms') else [hit]
    for point in points:
     if point.geom_type!='Point':continue
     pos=chain.project(point)
     if not own[0]+.1<pos<own[-1]-.1:continue
     a,b=chain.interpolate(max(0,pos-1)),chain.interpolate(min(chain.length,pos+1));at=route.project(point);c,e=route.interpolate(max(0,at-1)),route.interpolate(min(route.length,at+1));u=(b.x-a.x,b.y-a.y);v=(e.x-c.x,e.y-c.y);den=math.hypot(*u)*math.hypot(*v)
     if not den or abs(u[0]*v[1]-u[1]*v[0])/den<.55:continue
     left=max(p for p in own if p<pos);right=min(p for p in own if p>pos)
     if right-left<rules.get('joint_separation_m',2):continue
     options.append((min(pos-left,right-pos),d['primary_code'],(left+right)/2))
  if options:
   partitions=copy.deepcopy(_partitions or {})
   for d in directions:
    if d['lo']>0:partitions.setdefault(d['primary_code'],[]).append(d['lo'])
    if d['hi']<groups[d['primary_code']]['geometry'].length:partitions.setdefault(d['primary_code'],[]).append(d['hi'])
   _,code,cut=max(options);partitions.setdefault(code,[]).append(cut);partitions={c:sorted(set(v)) for c,v in partitions.items()}
   return design(s,router,cfg,partitions,_depth+1)
 for d in directions:
  # Recompute after the joint trench is available, to favour shared excavation.
  d['new_paths']=[p for c in d['new_codes'] for p in code_paths[c]]
  d['feed']=None
  if d['retained']:
   primary=next(part for part in d['retained'] if part['code']==d['primary_code']);g=groups[d['primary_code']]['geometry'];candidates=[]
   # Replacing an old branch removes its attachment constraint. The new cable
   # may splice anywhere suitable on the retained main, not at the old joint.
   own=[r['chain_position_m'] for r in primary['records']]
   retained_joins=[attachment[p['code']]['parent_position'] for p in d['retained'] if p['code']!=d['primary_code']]
   low=primary['lo'];high=primary['hi'];positions=[low+(high-low)*i/80 for i in range(81)]
   for pos in positions:
    p=g.interpolate(pos)
    if p.intersects(router.physical_obstacles) or not s['region'].buffer(.2).covers(p):continue
    try:n=router.target(p.coords[0]);feed_candidate=router.path(p.coords[0])
    except ValueError:continue
    if math.dist(feed_candidate.coords[-1],p.coords[0])>.01:
     connection=LineString([feed_candidate.coords[-1],p.coords[0]])
     if connection.intersects(router.physical_obstacles):continue
     feed_candidate=connect_joint(feed_candidate,p)
    reuse=max(abs(x-pos) for x in own+retained_joins)+rules.get('joint_separation_m',2)
    check=calculate_path({'id':'joint-candidate','segments':[{'id':'feed','type':'150Al','length_m':feed_candidate.length},{'id':'retained','type':primary['type'],'length_m':reuse}]},'laatste_helft',CATALOGUE)
    score=router.dist[n]*.5+feed_candidate.length+reuse*.1
    # A cheap early joint can leave an old curb loop crossing the new common
    # trench several times. Move the joint along the old main before replacing
    # all that cable; compare the retained downstream piece as a fixed route.
    retained_run=substring(g,min(own+retained_joins+[pos]),max(own+retained_joins+[pos]))
    other_feeds=[other['feed']['path'] for other in directions if other is not d and other.get('feed')]
    for route in core+other_feeds:
     hit=retained_run.intersection(route)
     if not hit.is_empty:score+=40*(len(hit.geoms) if hasattr(hit,'geoms') else 1)
    if check['max_design_A']<d['load_A']:score+=1000
    for child in d['new_codes']:
     records=sorted(groups[child]['records'],key=lambda r:r['chain_position_m']);first=min([records[0],records[-1]],key=lambda r:Point(r['tap']).distance(p))
     try:approach=router.between(p.coords[0],first['tap'])
     except ValueError:score+=1000;continue
     # One continuous main may not go to a splice and then retrace its own stem.
     # That would require two parallel cables or another branch joint.
     common=feed_candidate.intersection(approach).length
     if common>rules.get('joint_separation_m',2):score+=5000
     prefixes=[path for path in d['new_paths']];span=max(path.length for path in prefixes)-min(path.length for path in prefixes)
     L=feed_candidate.length+approach.length+span+math.dist(p.coords[0],approach.coords[0])
     branch_check=calculate_path({'id':'new-branch','segments':[{'id':'main','type':'150Al','length_m':L}]},'laatste_helft',CATALOGUE)
     if branch_check['max_design_A']<d['load_A']:score+=1000
     score+=L*.05
    candidates.append((score,pos,p))
   if not candidates:raise ValueError('Geen geschikte vrije moflocatie op '+d['primary_code'])
   _,pos,p=min(candidates,key=lambda x:x[0]);feed=router.path(p.coords[0])
   if math.dist(feed.coords[-1],p.coords[0])>.01:feed=connect_joint(feed,p)
   d['feed']={'position_m':pos,'xy':list(p.coords)[0],'path':feed};d['new_paths'].append(feed)
   # Limit the fed interval to this circuit and cut in the gap before another consumer.
   for part in d['retained']:
    if part['code']!=d['primary_code']:continue
    positions=[r['chain_position_m'] for r in part['records']]+[pos]+[attachment[p['code']]['parent_position'] for p in d['retained'] if p['code']!=d['primary_code']]
    low=min(positions);high=max(positions);external=[r['position_m'] for r in groups[part['code']]['outside_taps']]
    before=[x for x in external if x<low-.05];after=[x for x in external if x>high+.05]
    newlo=max(part['lo'],(max(before)+low)/2 if before else min(pos,low))
    newhi=min(part['hi'],(min(after)+high)/2 if after else high+rules.get('joint_separation_m',2))
    if rules.get('remove_unused_existing_parts') and d['new_codes']:
     # A midpoint in the gap is a possible isolation location, not a demand
     # to keep an unserved arm attached to the new joint.
     newlo=max(part['lo'],min(pos,low));newhi=min(part['hi'],max(pos,high)+rules.get('joint_separation_m',2))
    d['separated_existing_intervals']=[{'code':part['code'],'lo':part['lo'],'hi':newlo},{'code':part['code'],'lo':newhi,'hi':part['hi']}]
    part['lo']=newlo;part['hi']=newhi;part['geometry']=substring(g,newlo,newhi)
   if d['new_codes']:
    # A replacement branch and retained main are one real topology: route the
    # new main through the selected joint, rather than drawing a second feeder.
    rebuilt=[feed]
    for c in d['new_codes']:
     ordered=sorted([r for r in d['records'] if r['code']==c],key=lambda r:r['chain_position_m'])
     if Point(ordered[-1]['tap']).distance(p)<Point(ordered[0]['tap']).distance(p):ordered.reverse()
     points=list(feed.coords);previous=p.coords[0]
     for r in ordered:
      section=router.between(previous,r['tap']);section_points=list(section.coords)
      if math.dist(points[-1],section_points[0])>.01:points.append(section_points[0])
      points.extend(section_points[1:]);r['new_tap']=points[-1];rebuilt.append(LineString(points));previous=r['tap']
    d['new_paths']=rebuilt
 # A planned service can connect to a retained LS main as well as a new main.
 from vo_geplande_aansluitingen import assign_planned
 assign_planned(s['records'],directions,{c:g['geometry'] for c,g in groups.items()},rules.get('connection_end_clearance_m',.6))
 def assess(d):
  paths=[];new=[p for p in d['new_paths'] if p.length>0];lengths=[]
  for i,p in enumerate(new):
   paths.append({'id':f'new-{i}','segments':[{'id':f'new-{i}','type':'150Al','length_m':p.length}]});lengths.append(p.length)
  if d['feed']:
   from vo_materialen import segments_between
   feeder=d['feed']['path'].length;root=d['feed']['position_m'];parent=groups[d['primary_code']]['geometry']
   parent_part=next(p for p in d['retained'] if p['code']==d['primary_code'])
   for part in d['retained']:
    if part['code']==d['primary_code']:
     endpoint_paths=[segments_between(part,root,end,'main') for end in [part['lo'],part['hi']]]
    else:
     join=attachment[part['code']]['parent_position'];branch=groups[part['code']]['geometry'];ap=branch.project(Point(attachment[part['code']]['xy']));endpoint_paths=[segments_between(parent_part,root,join,'parent')+segments_between(part,ap,end,'branch') for end in [part['lo'],part['hi']]]
    for j,segments in enumerate(endpoint_paths):
     L=sum(s['length_m'] for s in segments)
     if L<=.01:continue
     paths.append({'id':part['code']+f'-end-{j}','segments':[{'id':'feed','type':'150Al','length_m':feeder}]+segments});lengths.append(feeder+L)
  longest=max(lengths)
  demand_dist=[]
  for r in d['records']:
   if r['code'] in d['new_codes'] or r.get('new_connection'):
    if r.get('new_tap'):
     point=Point(r['new_tap']);nearest=min(d['new_paths'],key=lambda path:path.distance(point));demand_dist.append(nearest.project(point))
    else:demand_dist.append(router.path(r['tap']).length)
   elif d['feed']:
    g=groups[r['code']]['geometry'];pos=g.project(Point(r['tap']));extra=abs(pos-d['feed']['position_m']) if r['code']==d['primary_code'] else abs(attachment[r['code']]['parent_position']-d['feed']['position_m'])+pos
    demand_dist.append(d['feed']['path'].length+extra)
  first=min(demand_dist)/longest;mean=sum(L*r['current_A'] for L,r in zip(demand_dist,d['records']))/sum(r['current_A'] for r in d['records'])/longest
  profile='evenredig' if first<=rules['profile_first_ratio'] and mean<=rules['profile_mean_ratio'] else 'laatste_helft'
  checks=[calculate_path(p,profile,CATALOGUE) for p in paths];limiting=min(checks,key=lambda x:(x['max_fuse_A'],-x['Z_ohm']));load=max(sum(r['current_A'] for r in d['records']),sum(r['kabel_opwek_A'] for r in d['records']));fits=load<=limiting['max_design_A']
  d.update(profile=profile,profile_evidence={'first_connection_ratio':first,'weighted_mean_ratio':mean},paths=paths,checks=checks,limiting=limiting,load_A=load,passes=fits)
  if not fits:
   from vo_paden import geometry_checks
   full=geometry_checks(d,max(d['new_paths'],key=lambda p:p.length));d['endpoint_variants']=full
   if full['selected']['passes']:
    d.update(paths=full['selected']['paths'],checks=full['selected']['checks'],limiting=full['selected']['limiting'],passes=True);fits=True
  return fits
 for d in directions:assess(d)
 reroute_short_feeds_first(directions,router,connect_joint,assess)
 # If the feed length, branch or material transition limits a reused circuit,
 # partition that source interval again. This uses current source taps and
 # computed capacity, never an example direction number or expected fuse.
 failed=[d for d in directions if not d['passes'] and d['retained'] and not d['new_codes']]
 if failed and _depth<3:
  partitions=copy.deepcopy(_partitions or {})
  for d in directions:
   if d['lo']>0:partitions.setdefault(d['primary_code'],[]).append(d['lo'])
   if d['hi']<groups[d['primary_code']]['geometry'].length:partitions.setdefault(d['primary_code'],[]).append(d['hi'])
  for d in failed:
   records=sorted([r for r in d['records'] if r['code']==d['primary_code']],key=lambda r:r['chain_position_m']);options=[]
   for i in range(1,len(records)):
    a,b=records[i-1]['chain_position_m'],records[i]['chain_position_m']
    if b-a<.1:continue
    left=sum(r['current_A'] for r in records[:i]);right=sum(r['current_A'] for r in records[i:]);options.append((max(left,right),-abs(b-a),(a+b)/2))
   if not options:raise ValueError('Kabelpad past niet en heeft geen bruikbare bronscheiding: '+d['primary_code'])
   partitions.setdefault(d['primary_code'],[]).append(min(options)[2])
  partitions={c:sorted(set(v)) for c,v in partitions.items()}
  if sum(len(v) for v in partitions.values())+len([c for c in groups if c not in parents])>len(cfg['direction_slots']):raise ValueError('Onvoldoende stationsposities voor noodzakelijke kabelpadverdeling')
  return design(s,router,cfg,partitions,_depth+1)
 # Move only an endpoint cluster to an adjacent circuit when length lowers a circuit's capacity.
 transfers=[]
 for d in directions:
  if d['passes']:continue
  best=None;excess=d['load_A']-d['limiting']['max_design_A']
  for c in d['new_codes']:
   ordered=sorted([r for r in d['records'] if r['code']==c],key=lambda r:r.get('chain_position_m',0))
   for sequence in [ordered,ordered[::-1]]:
    cluster=[];removed=0
    for r in sequence:
     cluster.append(r);removed+=r['current_A']
     if removed+1e-8>=excess:break
    if removed<excess:continue
    for target in directions:
     if target is d:continue
     network=unary_union(target['new_paths']);candidates=[];score=0
     for r in cluster:
      _,contact=nearest_points(Point(r['xy']),network);gap=contact.distance(Point(r['xy']))
      if gap>rules.get('transfer_radius_m',30):break
      candidates.append(dict(r,new_connection=True,new_tap=list(contact.coords)[0]));score+=gap
     if len(candidates)!=len(cluster):continue
     test=copy.copy(target);test['records']=target['records']+candidates
     if not assess(test):continue
     if best is None or score<best[0]:best=(score,cluster,candidates,target)
  if best:
   _,cluster,candidates,target=best
   for r,candidate in zip(cluster,candidates):
    d['records'].remove(r);r.update(new_connection=True,new_tap=candidate['new_tap']);target['records'].append(r);transfers.append({'connection':r['id'],'from_code':d['primary_code'],'to_code':target['primary_code']})
   assess(d);assess(target)
 for d in directions:
  paths=list(d['new_paths'])
  if d.get('feed'):
   parent=groups[d['primary_code']]['geometry'];part=next(p for p in d['retained'] if p['code']==d['primary_code']);prefix=list(d['feed']['path'].coords)
   for end in [part['lo'],part['hi']]:
    tail=list(substring(parent,d['feed']['position_m'],end).coords)
    if len(tail)>1:paths.append(LineString(prefix+[p[:2] for p in tail[1:]]))
  d['layout_order_path']=max(paths,key=lambda p:p.length)
 return order_and_allocate(directions,s,cfg),transfers

def reroute_short_feeds_first(directions,router,connect_joint,assess=None):
 from shapely.geometry import Point
 core=[max(d['new_paths'],key=lambda p:p.length) for d in directions if d['new_codes']];completed=[]
 for d in sorted([d for d in directions if d.get('feed') and not d['new_codes']],key=lambda d:d['feed']['path'].length):
  router.discount(core+completed);p=Point(d['feed']['xy']);path=connect_joint(router.path(d['feed']['xy']),p)
  if path.length<d['feed']['path'].length-.1:
   candidate=copy.copy(d);candidate['feed']=dict(d['feed'],path=path);candidate['new_paths']=[path]
   if assess is None or assess(candidate):d.update(candidate)
  completed.append(d['feed']['path'])

def order_and_allocate(directions,s,cfg):
 # Draw order follows spatial terminal order, with free slots grouped in the middle.
 from functools import cmp_to_key
 def before(a,b):
  left=a.get('layout_order_path',max(a['new_paths'],key=lambda p:p.length));right=b.get('layout_order_path',max(b['new_paths'],key=lambda p:p.length));last=(left.coords[0][0],left.coords[0][1])
  corridor_width=max(2.5,cfg['rules']['lane_pitch_m']*(len(directions)-1)+cfg['rules'].get('grid_m',.65))
  for distance in range(cfg['rules'].get('station_exit_join_m',16),int(min(left.length,right.length)),2):
   p=left.interpolate(distance);q=right.interpolate(distance)
   if p.distance(q)>corridor_width:
    mid=((p.x+q.x)/2,(p.y+q.y)/2);v=(mid[0]-last[0],mid[1]-last[1]);side=v[0]*(q.y-p.y)-v[1]*(q.x-p.x)
    if abs(side)>.001:return -1 if side>0 else 1
   last=((p.x+q.x)/2,(p.y+q.y)/2)
  return -1 if left.length<right.length else 1
 from vo_stationsuitloop import allocation_order
 from vo_stationsuitloop import station_frame
 frame=station_frame(s['station_entity'],{f'R{i+2}':max(d['new_paths'],key=lambda p:p.length) for i,d in enumerate(directions)});c=frame['front_center'];u=frame['port_axis'];normal=frame['outward_axis']
 def angle(d):
  route=max(d['new_paths'],key=lambda p:p.length);p=route.interpolate(min(12,route.length));return math.atan2((p.x-c[0])*u[0]+(p.y-c[1])*u[1],(p.x-c[0])*normal[0]+(p.y-c[1])*normal[1])
 def spatial(a,b):
  difference=angle(a)-angle(b)
  return (-1 if difference<0 else 1) if abs(difference)>.45 else before(a,b)
 directions=sorted(directions,key=cmp_to_key(spatial));slots=allocation_order(cfg);cfg['direction_slots']=slots;n=len(directions)
 if n>len(slots):raise ValueError('Te weinig vrije richtingen.')
 # Select occupied positions outside-in, then keep spatial route order on
 # those physical number positions. Using the priority list as lane order
 # would permute banks and introduce avoidable cable crossings.
 chosen=sorted(slots[:n])
 for d,slot in zip(directions,chosen):
  from vo_materialen import contact_material
  contact=contact_material(next(p for p in d['retained'] if p['code']==d['primary_code']),d['feed']['position_m']) if d.get('feed') else {'combo':False}
  d['id']=f'R{slot}';d['layer']=f'Aansluiting LS K{slot:02}';d['new_cable_label']='150Al+' if contact['combo'] else '150Al'
  for r in d['records']:r['direction']=d['id'];r['overzetter']=r['code'] in d['new_codes'] or r.get('new_connection',False)
 return directions
