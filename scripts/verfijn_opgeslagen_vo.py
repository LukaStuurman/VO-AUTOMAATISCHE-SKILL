"""Controleerbare revisie van een eigen bron-VO; geen gebruikersoplossing als invoer."""
import argparse,json,sys,hashlib,itertools,csv
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('previous');ap.add_argument('input');ap.add_argument('--output',required=True);ap.add_argument('--straight',nargs='+',default=[]);ap.add_argument('--dependency-path',action='append',default=[]);a=ap.parse_args();sys.path[:0]=a.dependency_path
 from shapely.geometry import shape,Point
 from shapely.ops import unary_union
 from vo_bronnen import read_sources
 from vo_router import SurfaceRouter
 from vo_rechte_straat import straighten_street_bundle
 from vo_oversteken import perpendicular_crossings
 from vo_corrigeer_cad import write_corrected_candidate
 from vo_verwijderen import removal_ledger
 from vo_controle import validate_saved
 from vo_preview import preview
 cfg=json.loads(Path(a.input).read_text(encoding='utf8'));previous=Path(a.previous).resolve()
 if any(previous==Path(p).resolve() or Path(p).resolve() in previous.parents for p in cfg.get('solution_paths_to_block',[])):raise ValueError('Gebruikersoplossing is geen revisie-invoer.')
 old=json.loads(previous.read_text(encoding='utf8'))
 if old.get('reference_used_in_generator') is not False or old.get('drawing',{}).get('reference_file_used') is not False:raise ValueError('Alleen een eigen bronkandidaat is toegestaan.')
 data=json.loads(json.dumps(old));data['config']=cfg;data['config'].pop('klic_display_dxf',None);read=lambda p:json.loads(Path(p).read_text(encoding='utf8'));sources=read_sources(cfg,read);router=SurfaceRouter(sources,cfg,read,build_grid=False)
 if {r['id'] for r in data['connections']}!={r['id'] for r in sources['records']}:raise ValueError('Aansluitinventaris veranderd; herontwerp nodig.')
 lines={d['id']:shape(d['display_main']) for d in data['directions']};tolerance=cfg['rules'].get('drawing_stoep_tolerance_m',0);obstacles=unary_union([router.natural_obstacles,router.erf.difference(router.walk.buffer(tolerance))]);road=router.road.difference(router.walk.buffer(tolerance));surfaces=router.allowed_surface.union(router.walk.buffer(tolerance));trees=list(router.trees.geoms) if hasattr(router.trees,'geoms') else [router.trees];anchors={d['id']:[d['feed']['xy']] for d in data['directions'] if d.get('feed') and lines[d['id']].distance(Point(d['feed']['xy']))<.01}
 lines,change=straighten_street_bundle(lines,a.straight,obstacles,surfaces,road,sources['region'],cfg['rules']['lane_pitch_m'],trees,anchors);data['straight_street_bundle']=change
 if a.straight and change is None:raise ValueError('Geen veilige langere rechte bundel gevonden; beoordeel de straatcorridor.')
 print('Rechte bundel:',change,flush=True)
 from vo_trace_verfijnen import straight_frontage
 data['house_side_frontage_changes']=[]
 for d in data['directions']:
  if d['id'] not in cfg['rules'].get('straight_frontage_house_side',[]):continue
  lines[d['id']],change=straight_frontage(lines[d['id']],obstacles,surfaces,road,sources['region'],margin=.3,house_points=[Point(r['xy']) for r in d['records']],other_lines=[g for n,g in lines.items() if n!=d['id']])
  if not change:raise ValueError('Geen veilig recht tracé aan huizenzijde: '+d['id'])
  data['house_side_frontage_changes'].append(dict(change,direction=d['id']));print('Huizenzijde:',change,flush=True)
 for name,g in lines.items():
  protected=unary_union([shape(p['geometry']).difference(Point(d['feed']['xy']).buffer(.2)) if d['id']==name and d.get('feed') else shape(p['geometry']) for d in data['directions'] for p in d['retained']]);lines[name],_=perpendicular_crossings(g,road,obstacles,sources['region'],name,data['crossing_sites'],protected)
 for d in data['directions']:d['display_main']=lines[d['id']].__geo_interface__
 from vo_kabelafwerking import extend_past_last_connection
 data['connection_end_extensions']=[]
 for d in data['directions']:
  if d['id'] not in cfg['rules'].get('extend_past_last_connection',[x['id'] for x in data['directions'] if not x.get('feed')]):continue
  lines[d['id']],change=extend_past_last_connection(d,lines[d['id']],cfg['rules'].get('connection_end_clearance_m',.6))
  d['display_main']=lines[d['id']].__geo_interface__
  if change:data['connection_end_extensions'].append(change)
 from vo_kabelafwerking import splice_after_crossing
 data['splice_after_crossing_changes']=[]
 for d in data['directions']:
  if d['id'] not in cfg['rules'].get('splice_after_crossing',[]):continue
  lines[d['id']],change=splice_after_crossing(d,lines[d['id']],shape(data['existing_chains'][d['primary_code']]),road,obstacles)
  d['display_main']=lines[d['id']].__geo_interface__
  if change:data['splice_after_crossing_changes'].append(change)
  else:raise ValueError('AM niet veilig direct na oversteek geplaatst: '+d['id'])
 from vo_gedeelde_offsets import shared_offsets
 lines,data['shared_offset_rebuild']=shared_offsets(lines,data['directions'],obstacles,sources['region'],cfg['rules']['lane_pitch_m'])
 for d in data['directions']:
  if not d.get('feed'):lines[d['id']],_=extend_past_last_connection(d,lines[d['id']],cfg['rules'].get('connection_end_clearance_m',.6))
  d['display_main']=lines[d['id']].__geo_interface__
 from vo_gedeelde_oversteek import merge_nearby_crossings
 lines,_=merge_nearby_crossings(data,lines,road,obstacles,surfaces,sources['region'],cfg['rules']['lane_pitch_m'])
 for d in data['directions']:d['display_main']=lines[d['id']].__geo_interface__
 import ezdxf
 from vo_stationsuitloop import build_station_exit
 lines=build_station_exit(data,ezdxf.readfile(old['drawing']['file']),obstacles,surfaces,sources['region'],road);cfg=data['config'];network=dict(lines,**{r['id']:shape(r['geometry']) for r in data.get('station_tamps',[])})
 out=Path(a.output).resolve();data=write_corrected_candidate(data,old,out);data['removal_ledger']=removal_ledger(sources,data['directions']);data['drawing']['crossings']=[{'a':x,'b':y,'geometry':g.intersection(h).difference(router.station).__geo_interface__} for (x,g),(y,h) in itertools.combinations(network.items(),2) if not g.intersection(h).difference(router.station).is_empty];data['drawing']['self_crossings']=[n for n,g in network.items() if not g.is_simple];data['checks']=validate_saved(data,sources,router);data['all_direction_checks']=all(d['passes'] for d in data['directions']);data['revision_provenance']={'previous_candidate':str(previous),'previous_sha256':hashlib.sha256(previous.read_bytes()).hexdigest(),'reference_solution_read':False,'scope':'Stationspoorten, tampen, gezamenlijke oversteken, aansluitbereik en offsets; oorspronkelijke xrefs behouden'};data['script_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in Path(__file__).parent.glob('*.py')}
 for name,value in [('Ontwerp met CAD-controle.json',data),('Controleblad.json',data['checks']),('Broninvoer gebruikt.json',cfg)]:out.joinpath(name).write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8')
 print('Opgeslagen CAD-controles:',data['checks']['calculation_and_new_bundle_pass'],flush=True)
 if not data['checks']['calculation_and_new_bundle_pass']:raise SystemExit('Revisie vereist herstel: zie controleblad en mof/contactfouten in CAD-controle.')
 data['previews']=preview(data,out);out.joinpath('Ontwerp met CAD-controle.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8')
 with out.joinpath('Aansluitregister.csv').open('w',encoding='utf-8-sig',newline='') as stream:
  fields=['id','direction','code','current_A','category','trafo_verbruik_A','trafo_opwek_A','overzetter','source_issue'];writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(data['connections'])

if __name__=='__main__':main()
