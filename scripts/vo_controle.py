"""Controleer opgeslagen lijnen, paden, vegetatie en gedeeld bestaand gebruik."""
import itertools

def validate_saved(data,sources,router):
 import ezdxf
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import unary_union
 cfg=data['config'];doc=ezdxf.readfile(data['drawing']['file']);lines={d['id']:shape(d['display_main']) for d in data['directions']};vegetation=[];reuse_intersections=[];roads=[]
 for d in data['directions']:
  g=lines[d['id']];obstacle=g.intersection(router.physical_obstacles).difference(router.station)
  if not obstacle.is_empty:vegetation.append({'direction':d['id'],'length_m':obstacle.length,'geometry':obstacle.__geo_interface__})
  q=g.intersection(router.road);parts=list(q.geoms) if hasattr(q,'geoms') else [q]
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
 saved_polylines={e.dxf.layer:LineString(e.get_points('xy')) for e in doc.modelspace().query('LWPOLYLINE') if e.dxf.layer in {d['layer'] for d in data['directions']} and len(e)>1 and LineString(e.get_points('xy')).distance(Point(sources['station_center']))<2}
 saved_match=all(d['layer'] in saved_polylines and saved_polylines[d['layer']].equals_exact(lines[d['id']],1e-6) for d in data['directions'])
 from collections import Counter
 symbols=Counter(name for handle,name in data['drawing']['symbol_types'].items() if doc.entitydb.get(handle) is not None and doc.entitydb[handle].dxftype()=='INSERT')
 symbols_ok=symbols['OVERZETTER']==sum(r['overzetter'] for r in data['connections'])
 data['drawing']['saved_symbol_counts']=dict(symbols)
 data['drawing']['nonperpendicular_crossings']=[r for r in roads if not r['perpendicular']]
 passed=assignment_ok and trafo_ok and all(d['passes'] for d in data['directions']) and not data['drawing']['crossings'] and not data['drawing']['self_crossings'] and not vegetation and not reuse_intersections and all(r['straight'] and r['perpendicular'] for r in roads) and not removal_errors and saved_match and symbols_ok and not len(doc.audit().errors)
 return {'calculation_and_new_bundle_pass':passed,'saved_geometry_matches_checked_geometry':saved_match,'each_connection_once':assignment_ok,'direction_checks':[{'id':d['id'],'connections':len(d['records']),'current_A':d['load_A'],'fuse_A':d['limiting']['max_fuse_A'],'endpoint':d['geometry_calculation']['selected_endpoint'],'passes':d['passes']} for d in data['directions']],'trafo_pass':trafo_ok,'trafo':trafo,'new_new_crossings':data['drawing']['crossings'],'new_retained_intersections':reuse_intersections,'vegetation_intersections':vegetation,'road_segments':roads,'nonstraight_road_segments':sum(not r['straight'] for r in roads),'removal_overlaps_used_parts':removal_errors,'parcels_touched':parcels,'ownership_verified':False,'root_zones_verified':router.topo['root_zones_verified'],'original_unresolved_xrefs':data['drawing']['unresolved_original_xrefs'],'source_questions':[{'id':r['id'],'question':r['source_issue']} for r in data['connections'] if r.get('source_issue')],'execution_ready':False}
