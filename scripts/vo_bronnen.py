"""Broninventarisatie; leest geen voorbeeldontwerp of gekozen richtingen."""
import json,re,math,collections,hashlib
from pathlib import Path

def code(text):
 m=re.search(r'([A-Z]{2,4}\d+-\d+)',text or '')
 return m.group(1) if m else None

def read_sources(config, read):
 import ezdxf
 from ezdxf import bbox
 from shapely.geometry import Point,Polygon,shape,LineString
 from shapely.ops import unary_union,linemerge,nearest_points
 doc=ezdxf.readfile(config['base_dxf']);boundary=doc.entitydb[config['boundary_handle']];region=Polygon(boundary.get_points('xy'))
 station=next(e for e in doc.modelspace().query('INSERT') if e.dxf.handle==config['station_handle']);bb=bbox.extents([station]);center=(bb.center.x,bb.center.y)
 maps=read(config['wfs_map'])['features'];conns=read(config['wfs_conn'])['features'];services=read(config['wfs_service'])['features']
 active=[f for f in maps if f['properties'].get('currentstatus')=='functional' and re.search(r'functie\s+LS',f['properties'].get('omschrijving',''),re.I)]
 bycode=collections.defaultdict(list)
 for f in active:
  c=code(f['properties'].get('label'))
  if c:bycode[c].append(f)
 chains={}
 for c,fs in bycode.items():
  union=unary_union([shape(f['geometry']) for f in fs]);g=union if union.geom_type=='LineString' else linemerge(union)
  if g.geom_type=='LineString' and g.intersects(region.buffer(10)):chains[c]=g
 # Material and combo state come from KLIC trench text, not WFS descriptions.
 klic=ezdxf.readfile(config['klic_dxf']);types={};evidence=collections.defaultdict(list);variants=collections.defaultdict(set)
 for e in klic.modelspace().query('TEXT MTEXT'):
  text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text
  for m in re.finditer(r'(\d+\s*(?:Al|Cu)?(?:\s*\+\s*\d+)?)\s+(\d{4,}-\d+)',text,re.I):
   raw=m.group(1).replace(' ','');c=config['network_prefix']+m.group(2)
   if c not in chains:continue
   if '+' in raw:
    size=raw.split('+')[0];kind=re.sub(r'[^\d]','',size)+('Al' if 'al' in size.lower() else 'Cu');combo=True
   else:kind=re.sub(r'[^\d]','',raw)+('Al' if 'al' in raw.lower() else 'Cu');combo=False
   if kind not in ['150Al','95Al','50Al','50Cu']:continue
   types[c]={'type':kind,'combo':combo};variants[c].add((kind,combo));evidence[c].append({'text':text,'handle':e.dxf.handle})
 circles=[e for e in doc.modelspace().query('INSERT') if e.dxf.name=='KA_K01' and region.covers(Point(e.dxf.insert.xy))]
 texts=list(doc.modelspace().query('TEXT[layer=="Aansluiting LS_OntwerpstroomKabel"]'));records=[]
 corrections={c['source_circle_handle']:c for c in config.get('source_corrections',[])}
 catalogue=json.loads((Path(__file__).parent.parent/'references/kader2024-categorieen.json').read_text(encoding='utf8'))['rows']
 for e in circles:
  p=Point(tuple(e.dxf.insert)[:2]);t=min(texts,key=lambda t:Point(tuple(t.dxf.insert)[:2]).distance(p));current=float(t.dxf.text.replace(',','.'));correction=corrections.get(e.dxf.handle)
  if correction:p=Point(correction['xy']);current=correction['cable_current_A']
  explicit=config.get('connection_categories',{}).get(e.dxf.handle) or (correction or {}).get('category')
  matches=[row for row in catalogue if abs(row[1]-current)<1e-9 and (not explicit or row[0]==explicit)]
  if len(matches)!=1:raise ValueError('Geef een eenduidige aansluitcategorie voor '+e.dxf.handle+' / '+str(current)+' A')
  category,_,kg,tv,tg=matches[0];rec={'id':e.dxf.handle,'xy':list(p.coords)[0],'original_text_handle':t.dxf.handle,'current_A':current,'category':category,'trafo_verbruik_A':tv,'trafo_opwek_A':tg,'kabel_opwek_A':kg,'code':None,'source_issue':None}
  if correction and correction.get('planned_connection'):
   rec['planned_connection']=True;rec['tap']=rec['xy'];rec['source_issue']='Geplande aansluiting: categorie en locatie zijn projectinvoer, geen bestaand WFS-aansluitpunt.';records.append(rec);continue
  sf=min(services,key=lambda f:shape(f['geometry']).distance(p));sp=shape(sf['geometry']);rec['service_id']=sf['id'];rec['service_distance_m']=sp.distance(p)
  candidates=[f for f in conns if re.search(r'functie\s+LS',f['properties'].get('omschrijving',''),re.I) and shape(f['geometry']).distance(sp)<.05]
  options=[]
  for f in candidates:
   c=code(f['properties'].get('label'));cg=shape(f['geometry'])
   if c in chains:options.append((cg.distance(chains[c]),c,f,chains[c]))
  if not options and candidates:
   # Explicitly uncertain: an LS service label points at an OV-only group.
   for f in candidates:
    cg=shape(f['geometry']);c,g=min(chains.items(),key=lambda item:cg.distance(item[1]));options.append((cg.distance(g),c,f,g))
   rec['source_issue']='LS-aansluitlabel ontbreekt op LS-hoofdkabel of wijst naar OV; geometrische kandidaat blijft te verifiëren.'
  if options and rec['service_distance_m']<1:
   gap,c,f,g=min(options,key=lambda x:x[0]);_,tap=nearest_points(shape(f['geometry']),g);rec.update(code=c,conn_id=f['id'],tap=list(tap.coords)[0],chain_position_m=g.project(tap),main_gap_m=gap)
  else:rec['source_issue']='Geen betrouwbare bronkoppeling; categorie/positie controleren.';rec['tap']=rec['xy']
  records.append(rec)
 needed={r['code'] for r in records if r['code']}
 for c in needed:
  if c not in types:raise ValueError('KLIC-kabeltype ontbreekt: '+c)
  if len(variants[c])>1:raise ValueError('Kabelcode bevat verschillende materiaalnotaties: splits gecontroleerde materiële stukken voor '+c)
 groups={c:{'code':c,'geometry':chains[c],'type':types[c]['type'],'combo':types[c]['combo'],'records':[r for r in records if r['code']==c],'source_evidence':evidence[c]} for c in needed}
 for c,g in groups.items():
  assigned={r.get('conn_id') for r in g['records']};outside=[]
  for f in conns:
   if f['id'] in assigned or code(f['properties'].get('label'))!=c or not re.search(r'functie\s+LS',f['properties'].get('omschrijving',''),re.I):continue
   cg=shape(f['geometry'])
   if cg.distance(g['geometry'])>.05:continue
   _,p=nearest_points(cg,g['geometry']);outside.append({'conn_id':f['id'],'position_m':g['geometry'].project(p)})
  g['outside_taps']=outside
 return {'doc':doc,'station_entity':station,'station_center':center,'station_bbox':(bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y),'region':region,'records':records,'groups':groups,'chains':chains,'types':types}
