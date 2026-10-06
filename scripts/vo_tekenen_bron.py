"""Teken alleen uit het nieuwe bronontwerp en de oorspronkelijke stijlblokken."""
import json,math,re,collections,itertools,copy
from pathlib import Path

def draw_source_design(data,out):
 import ezdxf
 from ezdxf import bbox
 from ezdxf.math import Matrix44
 from shapely.geometry import LineString,Point,Polygon,box,shape
 from shapely.ops import unary_union,substring
 from reken_richtingen import calculate_path,CATALOGUE
 from vo_terrein import unused_parts
 cfg=data['config'];doc=ezdxf.readfile(cfg['base_dxf']);msp=doc.modelspace();region=Polygon(doc.entitydb[cfg['boundary_handle']].get_points('xy'));station=bbox.extents([doc.entitydb[cfg['station_handle']]]);station_box=box(station.extmin.x,station.extmin.y,station.extmax.x,station.extmax.y)
 from vo_stijl import style_templates
 templates=style_templates(doc)
 generated=[];symbol_types={}
 from vo_eindmoffen import existing_end_joints,existing_joint_objects,retained_end_status,clean_obsolete_end_annotations
 from vo_mofverbindingen import align_splice_contacts,existing_branch_evidence
 original_chains={c:shape(g) for c,g in data['existing_chains'].items()};all_source_joints=existing_joint_objects(cfg['klic_dxf']);existing_joints=[j for j in all_source_joints if j['kind']=='end']
 # Geometry filters use source vegetation and topo, never the author drawing.
 from vo_terrein import vegetation_class
 from vo_topografie import topography_obstacles
 from vo_bundel import straighten
 def active_features(name):
  return [f for f in json.loads(Path(cfg['bgt'][name]).read_text(encoding='utf8'))['features'] if not f['properties'].get('eind_registratie') and not f['properties'].get('termination_date')]
 topo=topography_obstacles(cfg,region)
 obstacles=unary_union([shape(f['geometry']) for f in active_features('begroeidterreindeel') if vegetation_class(f['properties'])=='woody']+[shape(f['geometry']).buffer(cfg['rules']['tree_body_radius_m']) for f in active_features('vegetatieobject_punt')]+[shape(f['geometry']) for f in active_features('vegetatieobject_vlak')]+[topo['trees'],topo['uncertain_contours']]).difference(station_box)
 erf=unary_union([shape(f['geometry']) for f in active_features('onbegroeidterreindeel') if f['properties'].get('fysiek_voorkomen')=='erf']).difference(station_box)
 walk=unary_union([shape(f['geometry']) for f in active_features('wegdeel') if f['properties'].get('functie') in ['voetpad','voetgangersgebied','voetpad op trap','inrit']])
 erf=erf.difference(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0)))
 obstacles=unary_union([obstacles,erf])
 def symbol(name,p,layer,rotation=None):
  e=templates[name].copy();msp.add_entity(e);e.dxf.layer=layer;e.dxf.color=256
  if rotation is not None:
   center=bbox.extents([e]).center;e.transform(Matrix44.translate(-center.x,-center.y,0)@Matrix44.z_rotate(math.radians(rotation-e.dxf.rotation))@Matrix44.translate(center.x,center.y,0))
  center=bbox.extents([e]).center;e.translate(p[0]-center.x,p[1]-center.y,0);generated.append(e);symbol_types[e.dxf.handle]=name;return e
 def text(label,p,layer,h=.75,angle=0):
  e=msp.add_text(label,dxfattribs={'layer':layer,'insert':p,'height':h,'style':'ARIAL','rotation':angle,'color':256});generated.append(e);return e
 def dec(value,n):return f'{value:.{n}f}'.replace('.',',')
 def line(g,layer):
  e=msp.add_lwpolyline(list(g.coords),dxfattribs={'layer':layer,'linetype':'BYLAYER','color':256,'const_width':0});generated.append(e);return e
 for correction in cfg.get('source_corrections',[]):
  e=doc.entitydb[correction['source_circle_handle']];old=e.dxf.insert;new=correction['xy'];dx=new[0]-old.x;dy=new[1]-old.y;e.translate(dx,dy,0)
  r=next(x for x in data['connections'] if x['id']==correction['source_circle_handle']);t=doc.entitydb[r['original_text_handle']];t.translate(dx,dy,0);t.dxf.text=dec(correction['cable_current_A'],1)
 # Simplify each physical main, retaining street corners. House leads are not drawn.
 masters={d['id']:shape(max(d['new_paths'],key=lambda p:shape(p).length)) for d in data['directions']}
 # One simplification per shared backbone chain prevents small independent
 # simplification differences from turning parallel wires into crossings.
 trie={'point':None,'children':{},'terminal':set()}
 for name,g in masters.items():
  node=trie
  for p in g.coords:
   key=tuple(round(float(v),5) for v in p[:2]);node=node['children'].setdefault(key,{'point':key,'children':{},'terminal':set()})
  node['terminal'].add(name)
 rebuilt={}
 def rebuild(node,prefix):
  points=[node['point']]
  while len(node['children'])==1 and not node['terminal']:
   node=next(iter(node['children'].values()));points.append(node['point'])
  g=LineString(points).simplify(cfg['rules'].get('drawing_simplification_m',.45)) if len(points)>1 else None
  if g is not None and g.intersects(obstacles):g=LineString(points)
  if cfg['rules'].get('drawing_simplification_mode')=='visibility' and g is not None:g=straighten(LineString(points),obstacles.buffer(.7),cfg['rules'].get('drawing_simplification_m',.9))
  result=prefix+(list(g.coords)[1:] if prefix and g is not None else list(g.coords) if g is not None else points)
  for name in node['terminal']:rebuilt[name]=LineString(result)
  for child in node['children'].values():rebuild(child,result+[child['point']])
 for child in trie['children'].values():rebuild(child,[])
 masters=rebuilt
 ordering_lengths={d['id']:d.get('layout_priority_length_m',masters[d['id']].length) for d in data['directions']}
 from vo_trace_verfijnen import straight_frontage,earlier_joint_approach
 roads=active_features('wegdeel');road=unary_union([shape(f['geometry']) for f in roads if f['properties'].get('functie')=='rijbaan lokale weg'])
 from vo_terrein import vegetation_class
 surfaces=unary_union([shape(f['geometry']) for f in roads]+[shape(f['geometry']) for f in active_features('begroeidterreindeel') if vegetation_class(f['properties'])=='open_green']+[shape(f['geometry']) for f in active_features('onbegroeidterreindeel')]+[station_box])
 frontage_surfaces=unary_union([shape(f['geometry']) for f in roads]+[shape(f['geometry']) for f in active_features('begroeidterreindeel') if vegetation_class(f['properties'])=='open_green']+[shape(f['geometry']) for f in active_features('onbegroeidterreindeel') if f['properties'].get('fysiek_voorkomen')!='erf']+[station_box])
 data['trace_refinements']=[]
 for d in data['directions']:
  g=masters[d['id']]
  scopes=cfg['rules'].get('refinement_scope',{})
  if not d['feed'] and d['id'] in scopes.get('straight_frontage',[d['id']]):
   g,change=straight_frontage(g,obstacles,frontage_surfaces,road,region,cfg['rules'].get('straight_frontage_clearance_m',1.0))
  elif d['new_codes'] and d['feed'] and d['id'] in scopes.get('earlier_joint',[d['id']]):
   guide=shape(next(p['geometry'] for p in d['retained'] if p['code']==d['primary_code']))
   g,change=earlier_joint_approach(g,d['feed']['xy'],obstacles,surfaces,region,road=road,guide=guide)
  else:change=None
  if change:data['trace_refinements'].append(dict(change,direction=d['id']))
  masters[d['id']]=g
 # Existing source contacts may sit on adjacent old cables in the same street.
 # Canonicalise close, forward-running guides to ONE generated trench axis.
 canonical=[];snap_distance=max(.8,cfg['rules']['lane_pitch_m']*(len(masters)-1)+.2)
 for name,g in sorted(masters.items(),key=lambda item:ordering_lengths[item[0]],reverse=True):
  for axis in canonical:
   original=list(g.coords);positions=[g.project(Point(p)) for p in original];projected=[];good=[]
   for p,at in zip(original,positions):
    point=Point(p);q=axis.project(point);near=axis.interpolate(q);a0=axis.interpolate(max(0,q-8));a1=axis.interpolate(min(axis.length,q+8));b0=g.interpolate(max(0,at-8));b1=g.interpolate(min(g.length,at+8));u=(a1.x-a0.x,a1.y-a0.y);v=(b1.x-b0.x,b1.y-b0.y);den=math.hypot(*u)*math.hypot(*v);cos=(u[0]*v[0]+u[1]*v[1])/den if den else 0;projected.append(q);good.append(point.distance(near)<=snap_distance and cos>.7)
   points=[];i=0
   while i<len(original):
    j=i
    if good[i]:
     while j+1<len(original) and good[j+1] and projected[j+1]>=projected[j]-.01:j+=1
    if j>i and projected[j]-projected[i]>5:
     replacement=list(substring(axis,projected[i],projected[j]).coords);i=j+1
    else:replacement=[original[i]];i+=1
    for p in replacement:
     if not points or math.dist(points[-1],p)>.001:points.append(p)
   candidate=LineString(points)
   if candidate.intersection(obstacles).length<=g.intersection(obstacles).length+1e-6:g=candidate
  masters[name]=g;canonical.append(g)
 display={};pitch=cfg['rules']['lane_pitch_m'];ordered=data['directions'];count=len(ordered)
 for rank,d in enumerate(ordered):
  original=masters[d['id']];g=original
  lane=g.offset_curve((rank-(count-1)/2)*pitch,join_style=2,mitre_limit=2)
  if lane.geom_type!='LineString':lane=max(lane.geoms,key=lambda p:p.length)
  # All original points for retained joins are independent source-derived coordinates.
  if d['feed'] and not d['new_codes']:
   points=list(lane.coords);points[-1]=tuple(d['feed']['xy']);lane=LineString(points)
  display[d['id']]=lane
 from vo_bundel import repair_bundle,straight_road_crossings
 road=unary_union([shape(f['geometry']) for f in active_features('wegdeel') if f['properties'].get('functie')=='rijbaan lokale weg'])
 display={name:straight_road_crossings(g,road,obstacles) for name,g in display.items()}
 from vo_oversteken import crossing_sites,perpendicular_crossings
 def retained_obstacles(name):
  own=next(d for d in ordered if d['id']==name)
  return unary_union([shape(p['geometry']).difference(Point(own['feed']['xy']).buffer(.2)) if d['id']==name and own['feed'] else shape(p['geometry']) for d in ordered for p in d['retained']])
 sites=crossing_sites(display,road,pitch);data['crossing_sites']=sites;data['perpendicular_crossing_changes']=[]
 for name,g in display.items():
  display[name],changes=perpendicular_crossings(g,road,obstacles,region,name,sites,retained_obstacles(name));data['perpendicular_crossing_changes']+=changes
 retained_lines={f'OLD_{d["id"]}_{i}':shape(p['geometry']) for d in ordered for i,p in enumerate(d['retained'])};fixed=set(retained_lines)
 ignored={frozenset([a,b]) for a,b in itertools.combinations(fixed,2)}|{frozenset([d['id'],name]) for d in ordered for name in fixed if name.startswith('OLD_'+d['id']+'_')}
 anchors={d['id']:[d['feed']['xy']] for d in ordered if d['feed']}
 joined,bundle_repairs=repair_bundle(dict(display,**retained_lines),pitch,station_box,obstacles,fixed,ignored,anchors)
 display={name:joined[name] for name in display}
 display={name:straight_road_crossings(g,road,obstacles) for name,g in display.items()}
 for name,g in display.items():
  display[name],changes=perpendicular_crossings(g,road,obstacles,region,name,sites,retained_obstacles(name));data['perpendicular_crossing_changes']+=changes
 # Road normalisation can change joins outside the carriageway. Resolve any
 # resulting bundle conflicts and restore the common 90-degree crossing plane.
 for iteration in range(5):
  from vo_bundel import crossing_pairs
  if not crossing_pairs(dict(display,**retained_lines),station_box,ignored):break
  joined,repairs=repair_bundle(dict(display,**retained_lines),pitch,station_box,obstacles,fixed,ignored,anchors)
  if not repairs:break
  bundle_repairs+=repairs;display={name:joined[name] for name in display}
  for name,g in display.items():
   display[name],changes=perpendicular_crossings(g,road,obstacles,region,name,sites,retained_obstacles(name));data['perpendicular_crossing_changes']+=changes
 data['bundle_repairs']=bundle_repairs
 from vo_bundel import separate_free_ends
 display,data['free_end_adjustments']=separate_free_ends(display,ordered,pitch)
 from vo_rechte_straat import straighten_street_bundle
 data['straight_street_bundles']=[]
 for names in cfg['rules'].get('straight_bundle_groups',[]):
  lane_surfaces=surfaces.union(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0)));lane_road=road.difference(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0)));tree_points=[shape(f['geometry']) for f in active_features('vegetatieobject_punt')]
  display,change=straighten_street_bundle(display,names,obstacles,lane_surfaces,lane_road,region,pitch,tree_points,anchors)
  if change:data['straight_street_bundles'].append(change)
  for name,g in display.items():display[name],_=perpendicular_crossings(g,lane_road,obstacles,region,name,sites,retained_obstacles(name))
 previous_retained={d['id']:copy.deepcopy(d['retained']) for d in ordered}
 from vo_kabelafwerking import splice_after_crossing,supplemental_work,draw_supplemental,apply_cable_style,restore_source_xrefs
 data['splice_after_crossing_changes']=[]
 for d in ordered:
  if d['id'] not in cfg['rules'].get('splice_after_crossing',[]):continue
  display[d['id']],change=splice_after_crossing(d,display[d['id']],original_chains[d['primary_code']],road.difference(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0))),obstacles)
  if not change:raise ValueError('AM niet veilig direct na haakse oversteek geplaatst: '+d['id'])
  data['splice_after_crossing_changes'].append(change)
 for d in ordered:
  if d['id'] not in cfg['rules'].get('straight_frontage_house_side',[]):continue
  display[d['id']],change=straight_frontage(display[d['id']],obstacles,surfaces.union(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0))),road.difference(walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0))),region,margin=.3,house_points=[Point(r['xy']) for r in d['records']],other_lines=[g for n,g in display.items() if n!=d['id']])
  if not change:raise ValueError('Geen veilig recht tracé aan huizenzijde: '+d['id'])
  data.setdefault('house_side_frontage_changes',[]).append(dict(change,direction=d['id']))
 from vo_kabelafwerking import extend_past_last_connection
 data['connection_end_extensions']=[]
 for d in ordered:
  if d['id'] not in cfg['rules'].get('extend_past_last_connection',[x['id'] for x in ordered if not x.get('feed')]):continue
  display[d['id']],change=extend_past_last_connection(d,display[d['id']],cfg['rules'].get('connection_end_clearance_m',.6))
  if change:data['connection_end_extensions'].append(change)
 from vo_gedeelde_offsets import shared_offsets
 display,data['shared_offset_rebuild']=shared_offsets(display,ordered,obstacles,region,pitch)
 for d in ordered:
  if not d.get('feed'):display[d['id']],_=extend_past_last_connection(d,display[d['id']],cfg['rules'].get('connection_end_clearance_m',.6))
 data['splice_contact_adjustments']=align_splice_contacts(ordered,display,original_chains)
 for d in ordered:
  lane=display[d['id']];line(lane,d['layer']);d['display_main']=lane.__geo_interface__;d['display_main_length_m']=lane.length
  for r in d['records']:
   if r['code'] in d['new_codes'] or r.get('new_connection'):r['new_tap']=list(lane.interpolate(lane.project(Point(r['tap']))).coords[0])
  from vo_paden import geometry_checks
  d['geometry_calculation']=geometry_checks(d,lane)
  d['search_limiting']=d['limiting'];d['limiting']=d['geometry_calculation']['selected']['limiting'];d['passes']=d['geometry_calculation']['selected']['passes']
 # Symbol decisions come from final assignments, never from all circles in the area.
 from vo_annotaties import overzetter_position
 for r in data['connections']:
  if r.get('overzetter'):
   point,_=overzetter_position(r['xy'],display[r['direction']],cfg['rules'].get('overzetter_circle_offset_m',2.6));symbol('OVERZETTER',point,'Aansluiting LS K'+r['direction'][1:].zfill(2))
 for d in ordered:
  layer=d['layer'];g=display[d['id']];feed=d['feed'];ends=[];d['existing_end_mofs']=[];d['retained_end_work']=[]
  if feed:
   p=feed['xy'];symbol('MOF bestaand-nieuw',p,layer);kind=d['splice_kind'];retained_type=next(part['type'] for part in d['retained'] if part['code']==d['primary_code']);text(kind+' 150Al->'+retained_type+' (was '+d['primary_code'][3:]+')',(p[0]+1.0,p[1]+1.0),layer,.7)
   for part in d['retained']:
    rg=shape(part['geometry']);line(rg,'01 - Bestaande kabel')
    for p in [rg.coords[0],rg.coords[-1]]:
     if math.dist(p,feed['xy'])<1.0:continue
     if any(other is not part and shape(other['geometry']).distance(Point(p))<.05 for other in d['retained']):continue
     status=retained_end_status(p,original_chains[part['code']],existing_joints)
     d['retained_end_work'].append(dict(status,code=part['code'],xy=list(p),symbol='NIEUWE MOF' if status['new_required'] else 'BESTAANDE MOF'))
     if not status['new_required']:
      symbol('BESTAANDE MOF',p,'01 - Bestaande kabel');text('Bestaand',(p[0]+.8,p[1]+.8),'01 - Bestaande kabel',.7);d['existing_end_mofs'].append(dict(status,code=part['code'],xy=list(p)));continue
     symbol('NIEUWE MOF',p,layer);text('EM (was '+part['code'][3:]+')',(p[0]+.8,p[1]+.8),layer,.7);ends.append(list(p))
    midpoint=rg.interpolate(.5,normalized=True);a,b=rg.coords[0],rg.coords[-1];angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));angle=angle if -90<=angle<=90 else angle+180;text(part['type']+' / (was '+part['code'][3:]+')',(midpoint.x+.6,midpoint.y+.6),'01 - Bestaande kabel',.75,angle)
  if d['new_codes']:
   endpoint=g.coords[-1];symbol('NIEUWE MOF',endpoint,layer);text('EM',(endpoint[0]+.8,endpoint[1]+.8),layer,.7);ends.append(list(endpoint))
  d['end_mof_positions']=ends
  # Existing main/branch joints, not individual house connection taps.
  d['existing_branch_mofs']=[]
  for first,second in itertools.combinations(d['retained'],2):
   if first['code']==second['code']:continue
   a,b=shape(first['geometry']),shape(second['geometry']);pa,pb=__import__('shapely').ops.nearest_points(a,b)
   if pa.distance(pb)>.1:continue
   p=(pa.x,pa.y)
   if feed and math.dist(p,feed['xy'])<.2:continue
   evidence=existing_branch_evidence(p,all_source_joints)
   if not evidence:raise ValueError('Bestaande hoofd-/aftakmof zonder bronbewijs: '+d['id'])
   symbol('BESTAANDE MOF',p,'01 - Bestaande kabel');text('Bestaand',(p[0]+.8,p[1]+.8),'01 - Bestaande kabel',.7);d['existing_branch_mofs'].append({'xy':list(p),'codes':[first['code'],second['code']],'source_joint':evidence})
  # Label long street segments, in compact rows separated by direction offset.
  longest=max(zip(g.coords[:-1],g.coords[1:]),key=lambda p:math.dist(*p));a,b=longest;angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));angle=angle if -90<=angle<=90 else angle+180;mid=((a[0]+b[0])/2,(a[1]+b[1])/2);label=d.get('new_cable_label','150Al')+' / ????-00';text(label,(mid[0]+1.0,mid[1]+1.0),layer,.75,angle)
  p=g.interpolate(.8,normalized=True);text(dec(d['load_A'],1)+'Amp.',(p.x+1,p.y+2),layer);text(dec(d['limiting']['length_m'],2)+'Met.',(p.x+1,p.y+.9),layer)
 supplemental_work(data,all_source_joints,doc,previous_parts=previous_retained);draw_supplemental(data,symbol,text,line)
 data['obsolete_end_cleanup']=clean_obsolete_end_annotations(doc,ordered,region,original_chains)
 # Place the RT legend by empty-space scoring, not a reference coordinate.
 occupied=unary_union([g.buffer(2) for g in display.values()]+[Point(r['xy']).buffer(2) for r in data['connections']]);cx,cy=station.center.x,station.center.y;bounds=region.bounds;candidates=[]
 for x in range(math.ceil(bounds[0])+10,math.floor(bounds[2])-10,4):
  for y in range(math.ceil(bounds[1])+12,math.floor(bounds[3])-12,4):
   panel=box(x-9,y-11,x+9,y+11)
   if not region.buffer(-2).covers(panel):continue
   penalty=panel.intersection(occupied).area*100+math.hypot(x-cx,y-cy);candidates.append((penalty,x,y))
 if not candidates:raise ValueError('Geen leesbare positie voor richtingoverzicht.')
 _,x,y=min(candidates);rt=symbol('RT 1-12',(x,y),'0');checks={int(d['id'][1:]):d for d in ordered}
 for a in rt.attribs:
  m=re.search(r'RT_(\d+)',a.dxf.tag)
  if not m:continue
  n=int(m.group(1))
  if n in checks:a.dxf.text=f'RT {n:02}: {checks[n]["limiting"]["max_fuse_A"]}A / / '+checks[n].get('new_cable_label','150Al')
  elif str(n) in cfg['special_slots']:a.dxf.text=f'RT {n:02}: '+cfg['special_slots'][str(n)]+' / / 150Al'
  else:a.dxf.text=f'RT {n:02}:'
 center=bbox.extents([rt]).center;rt.translate(x-center.x,y-center.y,0)
 # Resolve existing references in the new output folder.
 unresolved=[];base=Path(cfg['base_dxf']).parent
 for block in doc.blocks:
  if not block.block.dxf.flags&4:continue
  raw=block.block.dxf.get('xref_path','');p=Path(raw.replace('\\','/'));candidate=p if p.is_absolute() else base/p
  if not candidate.exists():
   found=list(base.rglob(p.name))
   if len(found)==1:candidate=found[0]
  if candidate.exists():block.block.dxf.xref_path=str(candidate.resolve())
  else:unresolved.append(block.name)
 crossings=[]
 for (a,g),(b,h) in itertools.combinations(display.items(),2):
  q=g.intersection(h).difference(station_box)
  if not q.is_empty:crossings.append({'a':a,'b':b,'geometry':q.__geo_interface__})
 cable_style=apply_cable_style(doc,new_layers=[d['layer'] for d in ordered])
 doc.header['$INSUNITS']=6;doc.set_modelspace_vport(height=360,center=region.centroid.coords[0]);audit=doc.audit();out=Path(out);out.mkdir(exist_ok=True);file=out/(cfg['station_id']+' - LS VO uit brongegevens.dxf');doc.saveas(file)
 restore_source_xrefs(doc,data);doc.saveas(file)
 data['drawing']={'file':str(file),'crossings':crossings,'self_crossings':[n for n,g in display.items() if not g.is_simple],'legend_center':[x,y],'audit_errors':len(ezdxf.readfile(file).audit().errors),'unresolved_original_xrefs':unresolved,'new_model_entities':len(generated),'reference_file_used':False}
 data['drawing']['new_entity_handles']=[e.dxf.handle for e in generated];data['drawing']['symbol_types']=symbol_types;data['drawing']['cable_style']=cable_style
 from vo_annotaties import apply_annotation_layout
 apply_annotation_layout(doc,data);doc.saveas(file)
 (out/'Ontwerp met CAD-controle.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');return data
