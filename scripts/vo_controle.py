"""Controleer opgeslagen lijnen, paden, vegetatie en gedeeld bestaand gebruik."""
import itertools

def validate_saved(data,sources,router):
 import ezdxf
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import unary_union
 cfg=data['config'];doc=ezdxf.readfile(data['drawing']['file']);lines={d['id']:shape(d['display_main']) for d in data['directions']};vegetation=[];reuse_intersections=[];roads=[];private_hits=[]
 for d in data['directions']:
  g=lines[d['id']];obstacle=g.intersection(router.natural_obstacles).difference(router.station)
  private=g.intersection(router.erf).difference(router.walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0)))
  if not private.is_empty:private_hits.append({'direction':d['id'],'geometry':private.__geo_interface__,'length_m':private.length})
  if not obstacle.is_empty:vegetation.append({'direction':d['id'],'length_m':obstacle.length,'geometry':obstacle.__geo_interface__})
  # BGT pavement and carriageway edges can overlap. Limited graphical lane
  # overshoot at the pavement edge is not a physical crossing of the road.
  effective_road=router.road.difference(router.walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0))).buffer(-.000001)
  q=g.intersection(effective_road);parts=list(q.geoms) if hasattr(q,'geoms') else [q]
  for p in parts:
   if p.geom_type!='LineString' or p.length<1:continue
   chord=LineString([p.coords[0],p.coords[-1]]);roads.append({'direction':d['id'],'geometry':p.__geo_interface__,'length_m':p.length,'straightness_deviation_m':p.hausdorff_distance(chord),'straight':p.hausdorff_distance(chord)<.05})
   from vo_oversteken import crossing_angle
   site=min(data['crossing_sites'],key=lambda s:Point(s['xy']).distance(p.interpolate(.5,normalized=True)));angle=crossing_angle(p,router.road,site['road_axis']);roads[-1].update(site=site['id'],angle_to_road_deg=angle,perpendicular=angle>=89.999)
  for other in data['directions']:
   for part in other['retained']:
    intersection=g.intersection(shape(part['geometry'])).difference(router.station)
    if other['id']==d['id'] and d['feed']:intersection=intersection.difference(Point(d['feed']['xy']).buffer(.2))
    if not intersection.is_empty:reuse_intersections.append({'new_direction':d['id'],'retained_direction':other['id'],'code':part['code'],'geometry':intersection.__geo_interface__})
 removal_errors=[]
 for row in data.get('removal_ledger',[]):
  proposed=shape(row['proposed_removal']);used=unary_union([shape(g) for g in row['used_by_directions'].values()])
  if proposed.intersection(used).length>1e-6:removal_errors.append(row['code'])
 ids=[r['id'] for d in data['directions'] for r in d['records']];assignment_ok=len(ids)==len(set(ids))==len(data['connections']);trafo=data['trafo'];trafo_ok=max(trafo['verbruik_A'],trafo['opwek_A'])<=trafo['limit_A']+1e-8
 parcels=[]
 if cfg.get('parcels_geojson'):
  import json
  fs=json.loads(__import__('pathlib').Path(cfg['parcels_geojson']).read_text(encoding='utf8'))['features'];network=unary_union(list(lines.values()))
  for f in fs:
   g=shape(f['geometry']);p=network.intersection(g)
   if p.length>0:parcels.append({'id':f.get('id'),'properties':f['properties'],'new_route_length_m':p.length,'ownership':'unknown; parcel geometry does not establish public ownership'})
 owned=set(data['drawing']['new_entity_handles'])
 saved_polylines={e.dxf.layer:LineString(e.get_points('xy')) for e in doc.modelspace().query('LWPOLYLINE') if e.dxf.handle in owned and e.dxf.layer in {d['layer'] for d in data['directions']} and len(e)>1}
 saved_match=all(d['layer'] in saved_polylines and saved_polylines[d['layer']].equals_exact(lines[d['id']],1e-6) for d in data['directions'])
 from collections import Counter
 symbols=Counter(name for handle,name in data['drawing']['symbol_types'].items() if doc.entitydb.get(handle) is not None and doc.entitydb[handle].dxftype()=='INSERT')
 symbols_ok=symbols['OVERZETTER']==sum(r['overzetter'] for r in data['connections'])
 data['drawing']['saved_symbol_counts']=dict(symbols)
 data['drawing']['nonperpendicular_crossings']=[r for r in roads if not r['perpendicular']]
 data['drawing']['erf_intersections']=private_hits
 feed_errors=[];mof_errors=[]
 from ezdxf import bbox
 from vo_tekst_en_draworder import mof_label_matches
 for d in data['directions']:
  if d.get('feed'):
   p=Point(d['feed']['xy']);primary=next(part for part in d['retained'] if part['code']==d['primary_code']);old=shape(primary['geometry'])
   if lines[d['id']].distance(p)>.01 or old.distance(p)>.01:feed_errors.append({'direction':d['id'],'new_gap_m':lines[d['id']].distance(p),'retained_gap_m':old.distance(p)})
   if d.get('splice_kind')=='VM' and min(p.distance(Point(old.coords[0])),p.distance(Point(old.coords[-1])))>.01:feed_errors.append({'direction':d['id'],'reason':'VM ligt midden op behouden kabel; ongebruikte arm of verkeerde mofsoort'})
  for work in d.get('retained_end_work',[]):
   matches=[name for handle,name in data['drawing']['symbol_types'].items() if name in ['NIEUWE MOF','BESTAANDE MOF'] and doc.entitydb.get(handle) is not None and Point(bbox.extents([doc.entitydb[handle]]).center.xy).distance(Point(work['xy']))<.05]
   expected='NIEUWE MOF' if work['new_required'] else 'BESTAANDE MOF'
   if matches!=[expected]:mof_errors.append({'direction':d['id'],'xy':work['xy'],'expected':expected,'found':matches})
  for work in d.get('existing_end_mofs',[])+d.get('existing_branch_mofs',[]):
   labels=[e for e in doc.modelspace().query('TEXT') if e.dxf.text=='Bestaand' and mof_label_matches(doc,data,e,work['xy'])]
   if not labels:mof_errors.append({'direction':d['id'],'xy':work['xy'],'reason':'Werkelijk bestaande mof mist Bestaand-tekst'})
 data['drawing']['feed_contact_errors']=feed_errors;data['drawing']['mof_status_errors']=mof_errors
 for work in data.get('supplemental_mof_work',[]):
  expected=[('NIEUWE MOF',work.get('new_end_xy',work['xy']))]
  if work['kind']=='capped_existing_branch':
   expected.append(('BESTAANDE MOF',work['xy']))
   if not any(e.dxf.text=='Bestaand' and mof_label_matches(doc,data,e,work['xy'],4) for e in doc.modelspace().query('TEXT')):mof_errors.append({'code':work['code'],'reason':'Afgedopte bestaande aftakmof mist Bestaand'})
   stub=shape(work['stub_geometry']);primary=next(d for d in data['directions'] if d['id']==work['direction'])
   if not any(shape(p['geometry']).distance(Point(work['xy']))<.1 for p in primary['retained']):mof_errors.append({'code':work['code'],'reason':'Aftakmof mist behouden hoofdkabelcontact'})
   for name,g in lines.items():
    if not g.intersection(stub).is_empty:reuse_intersections.append({'new_direction':name,'code':work['code'],'reason':'Nieuwe kabel kruist afgedopte aftak'})
  for name,xy in expected:
   matches=[n for h,n in data['drawing']['symbol_types'].items() if n in ['NIEUWE MOF','BESTAANDE MOF'] and doc.entitydb.get(h) is not None and Point(bbox.extents([doc.entitydb[h]]).center.xy).distance(Point(xy))<.05]
   if matches!=[name]:mof_errors.append({'code':work['code'],'xy':xy,'expected':name,'found':matches})
   if name=='NIEUWE MOF':
    for handle,n in data['drawing']['symbol_types'].items():
     e=doc.entitydb.get(handle)
     if n==name and e is not None and Point(bbox.extents([e]).center.xy).distance(Point(xy))<.05 and e.dxf.layer!=work['layer']:mof_errors.append({'code':work['code'],'reason':'Nieuwe eindmof op verkeerde richtingslaag'})
    if not any(e.dxf.layer==work['layer'] and e.dxf.text=='EM (was '+work['code'][3:]+')' and mof_label_matches(doc,data,e,xy) for e in doc.modelspace().query('TEXT')):mof_errors.append({'code':work['code'],'reason':'Eindmoftekst mist juiste richtingslaag'})
 from vo_kabelafwerking import cable_layer
 style_errors=[];new_layers={d['layer'] for d in data['directions']}|{r['layer'] for r in data.get('station_tamps',[])}
 for title,cad in [('ontwerp',doc)]:
  for e in cad.modelspace().query('LWPOLYLINE'):
   if data['drawing'].get('cable_style',{}).get('scoped_to_generated') and e.dxf.handle not in data['drawing']['new_entity_handles']:continue
   if not (cable_layer(e.dxf.layer) or e.dxf.layer in new_layers):continue
   if abs(e.dxf.const_width-.1)>1e-9:style_errors.append({'file':title,'handle':e.dxf.handle,'reason':'Global width is niet 0.1'})
   if title=='ontwerp' and (e.dxf.layer in new_layers or 'nieuwe kabel' in e.dxf.layer.lower()) and (e.dxf.linetype!='DASHED' or abs(e.dxf.ltscale-.0035)>1e-9):style_errors.append({'file':title,'handle':e.dxf.handle,'reason':'Nieuwe kabel mist DASHED / 0.0035'})
 data['drawing']['cable_style_errors']=style_errors
 import hashlib
 from pathlib import Path
 base=ezdxf.readfile(cfg['base_dxf']);xref_errors=[];original={b.name:b.block.dxf.get('xref_path','') for b in base.blocks if b.block.dxf.flags&4}
 from vo_bronbehoud import check_source_preservation,check_neighbour_crossings
 preservation_errors=check_source_preservation(base,doc,data);neighbour_crossings=check_neighbour_crossings(base,lines,router.station)
 data['drawing']['source_preservation_errors']=preservation_errors;data['drawing']['neighbour_crossings']=neighbour_crossings
 for b in doc.blocks:
  if b.block.dxf.flags&4 and b.name in original and b.block.dxf.get('xref_path','')!=original[b.name]:xref_errors.append({'block':b.name,'reason':'Externe verwijzing gewijzigd'})
 for r in data.get('klic_display_reference',{}).get('original_references',[]):
  if r['sha256'] and hashlib.sha256(Path(r['path']).read_bytes()).hexdigest()!=r['sha256']:xref_errors.append({'block':r['block'],'reason':'Inhoud externe verwijzing gewijzigd'})
 data['drawing']['xref_errors']=xref_errors
 import math
 end_errors=[]
 for d in data['directions']:
  if d['id'] not in cfg['rules'].get('extend_past_last_connection',[x['id'] for x in data['directions'] if not x.get('feed')]):continue
  g=lines[d['id']];a,b=g.coords[-2],g.coords[-1];length=math.dist(a,b);u=((b[0]-a[0])/length,(b[1]-a[1])/length);clearance=cfg['rules'].get('connection_end_clearance_m',.6)
  for r in d['records']:
   if r['code'] not in d['new_codes'] and not r.get('new_connection'):continue
   beyond=(r['tap'][0]-b[0])*u[0]+(r['tap'][1]-b[1])*u[1]
   if beyond>-clearance+.001:end_errors.append({'direction':d['id'],'connection':r['id'],'short_of_required_end_m':beyond+clearance})
 data['drawing']['connection_end_errors']=end_errors
 offset_errors=[]
 for row in data.get('shared_offset_failures',[]):
  if shape(row['geometry']).difference(lines[row['direction']].buffer(.01)).length>.05:offset_errors.append(row)
 for row in data.get('shared_offset_rebuild',[]):
  piece=shape(row['geometry']);expected=lines[row['reference']].offset_curve(row['offset_m'],join_style=2,mitre_limit=10)
  if piece.difference(expected.buffer(.000001)).length>.00001 or piece.difference(lines[row['direction']].buffer(.000001)).length>.00001:offset_errors.append({'direction':row['direction'],'reference':row['reference'],'reason':'Opgeslagen gezamenlijke lijn wijkt van exacte offset af'})
 data['drawing']['shared_offset_errors']=offset_errors
 from vo_annotaties import validate_annotation_layout
 annotation_errors=validate_annotation_layout(doc,data);data['drawing']['annotation_errors']=annotation_errors
 from vo_tekst_en_draworder import validate_text_layout
 text_errors=validate_text_layout(doc,data);data['drawing']['text_layout_errors']=text_errors
 from vo_afzekeringsblok import validate_fuse_legend
 legend_errors=validate_fuse_legend(doc,data);data['drawing']['fuse_legend_errors']=legend_errors
 from vo_stationsuitloop import validate_station_exit
 station_errors=validate_station_exit(doc,data);data['drawing']['station_exit_errors']=station_errors
 for row in data.get('station_tamps',[]):
  g=shape(row['geometry']);hit=g.intersection(router.natural_obstacles).difference(router.station)
  if not hit.is_empty:vegetation.append({'direction':row['id'],'geometry':hit.__geo_interface__,'length_m':hit.length})
  private=g.intersection(router.erf).difference(router.walk.buffer(cfg['rules'].get('drawing_stoep_tolerance_m',0)))
  if not private.is_empty:private_hits.append({'direction':row['id'],'geometry':private.__geo_interface__,'length_m':private.length})
 crossing_groups=[];crossing_group_errors=[]
 for site in data['crossing_sites']:
  members=[r for r in roads if r['site']==site['id']];u=site['road_axis'];positions=sorted([(shape(r['geometry']).interpolate(.5,normalized=True).x*u[0]+shape(r['geometry']).interpolate(.5,normalized=True).y*u[1],r['direction']) for r in members]);gaps=[positions[i+1][0]-positions[i][0] for i in range(len(positions)-1)]
  crossing_groups.append({'site':site['id'],'directions':[n for _,n in positions],'adjacent_distances_m':gaps,'width_m':positions[-1][0]-positions[0][0] if positions else 0})
  if any(abs(gap-cfg['rules']['lane_pitch_m'])>.01 for gap in gaps):crossing_group_errors.append({'site':site['id'],'reason':'Wegoversteek is niet één compacte bundel met 0.20 m afstand'})
 data['drawing']['crossing_group_errors']=crossing_group_errors;data['drawing']['crossing_groups']=crossing_groups
 passed=assignment_ok and trafo_ok and all(d['passes'] for d in data['directions']) and not data['drawing']['crossings'] and not data['drawing']['self_crossings'] and not vegetation and not private_hits and not reuse_intersections and all(r['straight'] and r['perpendicular'] for r in roads) and not removal_errors and not feed_errors and not mof_errors and not style_errors and not xref_errors and not preservation_errors and not neighbour_crossings and not end_errors and not offset_errors and not annotation_errors and not text_errors and not legend_errors and not station_errors and not crossing_group_errors and saved_match and symbols_ok and not len(doc.audit().errors)
 passed=passed and not data.get('station_ground_coverage_questions')
 return {'calculation_and_new_bundle_pass':passed,'saved_geometry_matches_checked_geometry':saved_match,'each_connection_once':assignment_ok,'direction_checks':[{'id':d['id'],'connections':len(d['records']),'current_A':d['load_A'],'fuse_A':d['limiting']['max_fuse_A'],'endpoint':d['geometry_calculation']['selected_endpoint'],'passes':d['passes']} for d in data['directions']],'trafo_pass':trafo_ok,'trafo':trafo,'new_new_crossings':data['drawing']['crossings'],'new_retained_intersections':reuse_intersections,'vegetation_intersections':vegetation,'road_segments':roads,'nonstraight_road_segments':sum(not r['straight'] for r in roads),'removal_overlaps_used_parts':removal_errors,'parcels_touched':parcels,'ownership_verified':False,'root_zones_verified':router.topo['root_zones_verified'],'original_unresolved_xrefs':data['drawing']['unresolved_original_xrefs'],'source_questions':[{'id':r['id'],'question':r['source_issue']} for r in data['connections'] if r.get('source_issue')],'execution_ready':False}
