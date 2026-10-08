"""Haal volledige BGT-dekking voor de gedeclareerde oorspronkelijke CAD-grens."""
import argparse,datetime,hashlib,json,math
from pathlib import Path
from urllib.parse import urlencode,urljoin
from urllib.request import Request,urlopen

COLLECTIONS=['wegdeel','begroeidterreindeel','vegetatieobject_punt','vegetatieobject_vlak','pand','onbegroeidterreindeel']

def fetch_collection(name,bounds,folder,open_url=urlopen):
 params={'f':'json','bbox':','.join(str(v) for v in bounds),'bbox-crs':'http://www.opengis.net/def/crs/EPSG/0/28992','crs':'http://www.opengis.net/def/crs/EPSG/0/28992','limit':1000}
 first='https://api.pdok.nl/kadaster/bgt/ogc/v1/collections/'+name+'/items?'+urlencode(params);url=first;seen=set();features=[];pages=[]
 while url:
  if url in seen:raise ValueError('Herhaalde BGT-paginalink: '+name)
  seen.add(url)
  with open_url(Request(url,headers={'User-Agent':'LS-VO-source-check/1.0'}),timeout=50) as response:page=json.load(response)
  if page.get('type')!='FeatureCollection':raise ValueError('Geen BGT FeatureCollection: '+name)
  features.extend(page['features']);pages.append({'url':url,'count':len(page['features'])});url=next((urljoin(url,l['href']) for l in page.get('links',[]) if l.get('rel')=='next'),None)
 file=Path(folder)/(name+'.geojson');file.write_text(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False),encoding='utf8')
 return {'file':str(file.resolve()),'bbox_RD':list(bounds),'url':first,'pages':pages,'pagination_complete':True,'count':len(features),'sha256':hashlib.sha256(file.read_bytes()).hexdigest()}

def main():
 ap=argparse.ArgumentParser();ap.add_argument('input');ap.add_argument('--output',required=True);ap.add_argument('--output-config',required=True);ap.add_argument('--margin-m',type=float,default=25);args=ap.parse_args()
 import ezdxf
 from shapely.geometry import Polygon
 cfg=json.loads(Path(args.input).read_text(encoding='utf8'));source=Path(cfg['base_dxf']).resolve()
 if any(source==Path(p).resolve() or Path(p).resolve() in source.parents for p in cfg.get('solution_paths_to_block',[])):raise ValueError('Doeloplossing is geen toegestane BGT-selectiebron.')
 doc=ezdxf.readfile(source);region=Polygon(doc.entitydb[cfg['boundary_handle']].get_points('xy'));xmin,ymin,xmax,ymax=region.buffer(args.margin_m).bounds;bounds=[math.floor(xmin*1000)/1000,math.floor(ymin*1000)/1000,math.ceil(xmax*1000)/1000,math.ceil(ymax*1000)/1000];folder=Path(args.output).resolve();folder.mkdir(parents=True,exist_ok=True);rows={}
 for name in COLLECTIONS:
  rows[name]=fetch_collection(name,bounds,folder);print(name,rows[name]['count'],'objecten',len(rows[name]['pages']),'pagina(s)',flush=True)
 register=folder/'Bronregister.json';register.write_text(json.dumps({'fetched_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'station':cfg['station_id'],'declared_bbox_RD':bounds,'selection_source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'sources':rows},ensure_ascii=False,indent=2),encoding='utf8');cfg['bgt']={n:r['file'] for n,r in rows.items()};cfg['bgt_source_register']=str(register);Path(args.output_config).write_text(json.dumps(cfg,ensure_ascii=False,indent=2),encoding='utf8')

if __name__=='__main__':main()
