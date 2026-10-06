"""Bronontwerp: geen uitgewerkt doelstation als runtime-invoer."""
import argparse,json,sys,hashlib,time,copy
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output',required=True);ap.add_argument('--dependency-path',action='append',default=[]);args=ap.parse_args()
 sys.path[:0]=args.dependency_path
 cfg=json.loads(Path(args.input).read_text(encoding='utf8'));out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True);package=Path(__file__).resolve().parent.parent
 forbidden={'reference_dxf','solution_dxf','directions','routes','new_paths','desired_fuses','assigned_connections','reference_plan'}
 if forbidden&cfg.keys():raise ValueError('Uitgewerkte keuzes zijn geen broninvoer: '+str(forbidden&cfg.keys()))
 if cfg['kader']!=2024:raise ValueError('Deze catalogus is voor kader 2024; laad eerst gecontroleerde waarden voor een ander kader.')
 for correction in cfg.get('source_corrections',[]):
  if not correction.get('provenance'):raise ValueError('Broncorrectie vereist expliciete herkomst.')
 keys=['base_dxf','klic_dxf','topo_dxf','wfs_map','wfs_conn','wfs_service'];inputs={str(Path(cfg[k]).resolve()) for k in keys}|{str(Path(p).resolve()) for p in cfg['bgt'].values()}
 if cfg.get('parcels_geojson'):inputs.add(str(Path(cfg['parcels_geojson']).resolve()))
 blocked=[Path(p).resolve() for p in cfg.get('solution_paths_to_block',[])];readlog=set()
 hashes={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in inputs}
 script_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.joinpath('scripts').glob('*.py')}
 resources={str(p.resolve()) for folder in ['references','assets'] for p in package.joinpath(folder).glob('*') if p.is_file()}
 def guard(event,arguments):
  if event!='open' or not isinstance(arguments[0],(str,bytes)):return
  p=Path(arguments[0]).resolve();mode=arguments[1]
  if isinstance(mode,str) and any(flag in mode for flag in ['w','a','+']):return
  if any(p==b or b in p.parents for b in blocked):raise PermissionError('Oplossing is uitgesloten van bronontwerp: '+str(p))
  if str(p) in inputs:readlog.add(str(p))
  elif p.suffix.lower() in ['.dxf','.dwg','.geojson','.xlsx'] and str(p) not in resources and out not in p.parents:raise PermissionError('Niet gedeclareerde CAD/GIS/rekenbron: '+str(p))
 sys.addaudithook(guard)
 from vo_bronnen import read_sources
 from vo_router import SurfaceRouter
 from vo_ontwerp import design
 from vo_verwijderen import removal_ledger
 from vo_tekenen_bron import draw_source_design
 from vo_controle import validate_saved
 from vo_preview import preview
 from shapely.geometry import LineString,Point
 def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
 started=time.monotonic();sources=read_sources(cfg,read)
 for e in sources['doc'].modelspace().query('LWPOLYLINE'):
  if e.dxf.layer.startswith('Aansluiting LS K') and len(e)>1:
   if LineString(e.get_points('xy')).distance(Point(sources['station_center']))<2:raise ValueError('Doelstation bevat al nieuwe kabelroutes; kies de oorspronkelijke lege bron.')
 missing=[r['id'] for r in sources['records'] if not r['code'] and not r.get('planned_connection')]
 if missing:raise ValueError('Niet gekoppelde bestaande aansluitingen: '+str(missing))
 print('Broninventarisatie:',len(sources['records']),'aansluitingen',flush=True)
 router=SurfaceRouter(sources,cfg,read);directions,transfers=design(sources,router,cfg)
 def serial(obj):
  if hasattr(obj,'geom_type'):return obj.__geo_interface__
  if isinstance(obj,dict):return {k:serial(v) for k,v in obj.items()}
  if isinstance(obj,(list,tuple)):return [serial(v) for v in obj]
  if hasattr(obj,'item'):return obj.item()
  return obj
 trafo={'verbruik_A':sum(r['trafo_verbruik_A'] for r in sources['records']),'opwek_A':sum(r['trafo_opwek_A'] for r in sources['records']),'limit_A':cfg['kva']/.23/3}
 result={'station':cfg['station_id'],'config':cfg,'directions':serial(directions),'connections':sources['records'],'transfers':transfers,'trafo':trafo,'removal_ledger':removal_ledger(sources,directions),'all_direction_checks':all(d['passes'] for d in directions),'input_hashes':hashes,'script_hashes':script_hashes,'solution_access':'Only declared original sources; solution paths blocked by runtime audit hook','reference_used_in_generator':False}
 (out/'Broninvoer gebruikt.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8');(out/'Ontwerp uit brongegevens.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 result['existing_chains']=serial({c:g['geometry'] for c,g in sources['groups'].items()})
 result=draw_source_design(result,out);result['checks']=validate_saved(result,sources,router);result['all_direction_checks']=all(d['passes'] for d in result['directions']);result['all_source_files_read']=sorted(readlog);result['elapsed_seconds']=time.monotonic()-started
 result['previews']=preview(result,out)
 import csv
 with (out/'Aansluitregister.csv').open('w',encoding='utf-8-sig',newline='') as stream:
  fields=['id','direction','code','current_A','category','trafo_verbruik_A','trafo_opwek_A','overzetter','source_issue'];writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(result['connections'])
 (out/'Ontwerp met CAD-controle.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8');(out/'Controleblad.json').write_text(json.dumps(result['checks'],ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'drawing':result['drawing'],'passes':result['checks']['calculation_and_new_bundle_pass'],'directions':result['checks']['direction_checks'],'vegetation_intersections':result['checks']['vegetation_intersections'],'new_retained_intersections':result['checks']['new_retained_intersections'],'nonstraight_road_segments':result['checks']['nonstraight_road_segments'],'elapsed_seconds':result['elapsed_seconds']},ensure_ascii=False,indent=2),flush=True)
 if not result['checks']['calculation_and_new_bundle_pass']:raise SystemExit('Kandidaat vereist herstel: controleblad toont de redenen.')

if __name__=='__main__':main()
