"""Herzie een eigen opgeslagen bronkandidaat met behoud van netstructuur."""
import argparse,json,sys,copy,hashlib
from pathlib import Path

def main():
 ap=argparse.ArgumentParser();ap.add_argument('previous');ap.add_argument('input');ap.add_argument('--output',required=True);ap.add_argument('--dependency-path',action='append',default=[]);a=ap.parse_args();sys.path[:0]=a.dependency_path
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import substring
 from vo_bronnen import read_sources
 from vo_router import SurfaceRouter
 from vo_tekenen_bron import draw_source_design
 from vo_controle import validate_saved
 from vo_preview import preview
 cfg=json.loads(Path(a.input).read_text(encoding='utf8'));previous=Path(a.previous).resolve()
 if any(previous==Path(p).resolve() or Path(p).resolve() in previous.parents for p in cfg.get('solution_paths_to_block',[])):raise ValueError('De uitgewerkte gebruikersoplossing is geen revisie-invoer.')
 data=json.loads(previous.read_text(encoding='utf8'))
 if data.get('reference_used_in_generator') is not False or data.get('drawing',{}).get('reference_file_used') is not False:raise ValueError('Revisie vereist een eigen aantoonbaar uit bronnen gemaakte kandidaat.')
 if any(previous==Path(p).resolve() or Path(p).resolve() in previous.parents for p in cfg.get('solution_paths_to_block',[])):raise ValueError('De uitgewerkte gebruikersoplossing is geen revisie-invoer.')
 read=lambda p:json.loads(Path(p).read_text(encoding='utf8'));sources=read_sources(cfg,read);router=SurfaceRouter(sources,cfg,read)
 if {r['id'] for r in sources['records']}!={r['id'] for r in data['connections']}:raise ValueError('Aansluitinventaris gewijzigd: herontwerp vereist.')
 data['config']=cfg;data['source_revision']={'previous_candidate':str(previous),'sha256':hashlib.sha256(previous.read_bytes()).hexdigest(),'basis':'Eigen bronkandidaat; alleen tracés en tekenconventies herzien, geen gebruikersoplossing gelezen'}
 data['pavement_revisions']=[]
 for d in data['directions']:
  g=max((shape(p) for p in d['new_paths']),key=lambda p:p.length);hit=shape(d['display_main']).intersection(router.erf).union(g.intersection(router.erf))
  d['layout_priority_length_m']=g.length
  if hit.is_empty:continue
  parts=list(hit.geoms) if hasattr(hit,'geoms') else [hit];points=[Point(xy) for p in parts if hasattr(p,'coords') for xy in p.coords];positions=[g.project(p) for p in points]
  if not positions:continue
  lo=max(0,min(positions)-5);hi=min(g.length,max(positions)+5);start=g.interpolate(lo);end=g.interpolate(hi)
  patch=router.between(start.coords[0],end.coords[0]);points=list(substring(g,0,lo).coords)+list(patch.coords)
  if hi<g.length-.01:points+=list(substring(g,hi,g.length).coords)
  clean=[points[0]]
  for p in points[1:]:
   if Point(p).distance(Point(clean[-1]))>.001:clean.append(p)
  replacement=LineString(clean);d['new_paths']=[replacement.__geo_interface__]
  data['pavement_revisions'].append({'direction':d['id'],'replaced_old_span_m':hi-lo,'old_erf_length_m':hit.length,'new_erf_length_m':replacement.intersection(router.erf).length})
 package=Path(__file__).resolve().parent;data['script_hashes']={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in package.glob('*.py')}
 data['input_hashes'][str(Path(cfg['base_dxf']).resolve())]=hashlib.sha256(Path(cfg['base_dxf']).read_bytes()).hexdigest()
 out=Path(a.output).resolve();out.mkdir(exist_ok=True);data=draw_source_design(data,out);data['checks']=validate_saved(data,sources,router);data['all_direction_checks']=all(d['passes'] for d in data['directions']);data['previews']=preview(data,out)
 (out/'Broninvoer gebruikt.json').write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')
 import csv
 with (out/'Aansluitregister.csv').open('w',encoding='utf-8-sig',newline='') as stream:
  fields=['id','direction','code','current_A','category','trafo_verbruik_A','trafo_opwek_A','overzetter','source_issue'];writer=csv.DictWriter(stream,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(data['connections'])
 (out/'Ontwerp met CAD-controle.json').write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding='utf8');(out/'Controleblad.json').write_text(json.dumps(data['checks'],ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps({'passes':data['checks']['calculation_and_new_bundle_pass'],'crossings':data['drawing']['crossings'],'obstacles':data['checks']['vegetation_intersections'],'erf':data['drawing']['erf_intersections'],'retained':data['checks']['new_retained_intersections'],'nonperpendicular':data['drawing']['nonperpendicular_crossings'],'directions':data['checks']['direction_checks']},ensure_ascii=False,indent=2))
 if not data['checks']['calculation_and_new_bundle_pass']:raise SystemExit('Revisie vereist herstel.')

if __name__=='__main__':main()
