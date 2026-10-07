"""Kabelstijl, bronmoffen op afgedopte aftakken en einden van buren."""
import math,re

def cable_layer(layer):
 return bool(re.match(r'LBK\d',layer) or layer=='01 - Bestaande kabel' or re.match(r'^K\d+.*kabel',layer,re.I) or ('E_LV_' in layer and 'CABLE' in layer and 'JOINT' not in layer))

def apply_cable_style(doc,new_handles=(),new_layers=(),scope_handles=None):
 if 'DASHED' not in doc.linetypes:doc.linetypes.new('DASHED',dxfattribs={'description':'Dashed','pattern':[19.05,12.7,-6.35]})
 handles=set(new_handles);layers=set(new_layers);count=0;new_count=0
 for e in doc.modelspace().query('LWPOLYLINE POLYLINE'):
  if scope_handles is not None and e.dxf.handle not in scope_handles:continue
  if not (cable_layer(e.dxf.layer) or e.dxf.layer in layers or e.dxf.handle in handles):continue
  if e.dxftype()=='LWPOLYLINE':
   e.set_points([(p[0],p[1],0,0,p[4]) for p in e.get_points('xyseb')],format='xyseb');e.dxf.const_width=.1
  else:
   e.dxf.default_start_width=.1;e.dxf.default_end_width=.1
   for v in e.vertices:v.dxf.start_width=0;v.dxf.end_width=0
  count+=1
  if e.dxf.handle in handles or e.dxf.layer in layers or 'nieuwe kabel' in e.dxf.layer.lower():e.dxf.linetype='DASHED';e.dxf.ltscale=.0035;new_count+=1
 return {'cable_polylines':count,'new_cable_polylines':new_count,'global_width':.1,'new_linetype':'DASHED','new_linetype_scale':.0035,'scoped_to_generated':scope_handles is not None}

def supplemental_work(data,joints,host_doc,stub_length=.9,previous_parts=None):
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import substring
 from vo_mofverbindingen import existing_branch_evidence
 work=[];trims=[];chains={c:shape(g) for c,g in data['existing_chains'].items()}
 for d in data['directions']:
  for code in d['new_codes']:
   join=d.get('parent_child_positions',{}).get(code)
   if not join or code not in chains:continue
   primary=next((p for p in d['retained'] if p['code']==d['primary_code'] and shape(p['geometry']).distance(Point(join['xy']))<.1),None)
   if not primary:continue
   evidence=existing_branch_evidence(join['xy'],[j for j in joints if j['kind']=='branch'])
   if not evidence:raise ValueError('Afgedopte bron-aftak mist bronmof: '+code)
   branch=chains[code];root=branch.project(Point(join['xy']))
   if min(root,branch.length-root)>.1:raise ValueError('Afgedopte aftak heeft twee armen; afzonderlijke gebruiksanalyse nodig: '+code)
   end=min(branch.length,root+stub_length) if root<branch.length/2 else max(0,root-stub_length)
   stub=substring(branch,root,end)
   # All original branch loads have been assigned to the replacement cable.
   if any(code==p['code'] for other in data['directions'] for p in other['retained']):raise ValueError('Afgedopte aftak wordt nog door een andere richting gebruikt.')
   if any(r['code']==code and not r['overzetter'] for r in data['connections']):raise ValueError('Afgedopte aftak heeft een achterblijvende aansluiting.')
   work.append({'kind':'capped_existing_branch','direction':d['id'],'layer':d['layer'],'code':code,'xy':evidence['xy'],'source_joint':evidence,'stub_geometry':stub.__geo_interface__,'new_end_xy':list(stub.coords[-1])})
   cut=substring(branch,end,branch.length if root<branch.length/2 else 0)
   if cut.length>.01:trims.append({'code':code,'geometry':cut.__geo_interface__,'protected_used_geometry':stub.__geo_interface__,'reason':'Vervangen aftak na bestaand bronmof afdoppen'})
 # A verified removed VM arm may leave a still-used neighbour cable endpoint.
 vm_cuts=[r for r in data.get('klic_display_removals',[]) if r['code'] not in {w['code'] for w in work}]
 for d in data['directions']:
  if not previous_parts or d.get('splice_kind')!='VM':continue
  before=next(p for p in previous_parts[d['id']] if p['code']==d['primary_code']);after=next(p for p in d['retained'] if p['code']==d['primary_code'])
  for a,b in [(before['lo'],after['lo']),(after['hi'],before['hi'])]:
   if b>a+.001:vm_cuts.append({'code':d['primary_code'],'geometry':substring(chains[d['primary_code']],a,b).__geo_interface__,'protected_used_geometry':after['geometry']})
 for row in vm_cuts:
  removed=shape(row['geometry']);used=shape(row['protected_used_geometry'])
  for xy in [removed.coords[0],removed.coords[-1]]:
   if Point(xy).distance(used)<.05:continue
   matches=[]
   for e in host_doc.modelspace().query('LWPOLYLINE'):
    if row['code'] not in e.dxf.layer or len(e)<2:continue
    g=LineString(e.get_points('xy'))
    if min(math.dist(xy,g.coords[0]),math.dist(xy,g.coords[-1]))<.05 and g.intersection(removed.buffer(.001)).length<.02:matches.append(e.dxf.handle)
   if matches and not any(w['kind']=='neighbour_cut_end' and w['code']==row['code'] and math.dist(w['xy'],xy)<.01 for w in work):
    owner=min((d for d in data['directions'] if d['primary_code']==row['code'] and d.get('splice_kind')=='VM'),key=lambda d:Point(d['feed']['xy']).distance(removed))
    work.append({'kind':'neighbour_cut_end','direction':owner['id'],'layer':owner['layer'],'code':row['code'],'xy':list(xy),'source_endpoint_handles':matches})
 data['supplemental_mof_work']=work;data['additional_display_removals']=trims
 return work

def draw_supplemental(data,symbol,text,line):
 from shapely.geometry import shape
 for w in data['supplemental_mof_work']:
  p=w['xy'];layer='01 - Bestaande kabel'
  if w['kind']=='capped_existing_branch':
   line(shape(w['stub_geometry']),layer);symbol('BESTAANDE MOF',p,layer);text('Bestaand',(p[0]-3,p[1]+1),layer)
   p=w['new_end_xy']
  symbol('NIEUWE MOF',p,w['layer']);text('EM (was '+w['code'][3:]+')',(p[0]+.8,p[1]-.8),w['layer'])

def restore_source_xrefs(doc,data):
 """Behoud oorspronkelijke xrefs; wijzig kabelstijl uitsluitend in de host."""
 import ezdxf,hashlib
 from pathlib import Path
 base=ezdxf.readfile(data['config']['base_dxf']);source={b.name:b.block.dxf.get('xref_path','') for b in base.blocks if b.block.dxf.flags&4};restored=[]
 declared={str(Path(data['config'][k]).resolve()) for k in ['base_dxf','klic_dxf','topo_dxf'] if k in data['config']}
 for block in doc.blocks:
  if block.block.dxf.flags&4 and block.name in source:
   block.block.dxf.xref_path=source[block.name];raw=Path(source[block.name]);restored.append({'block':block.name,'path':source[block.name],'sha256':hashlib.sha256(raw.read_bytes()).hexdigest() if raw.is_absolute() and str(raw.resolve()) in declared and raw.is_file() else None,'external_content_read':str(raw.resolve()) in declared})
 data['config'].pop('klic_display_dxf',None);data.pop('klic_cable_style',None);data['klic_display_edits']=[];data['klic_display_reference']={'original_references':restored,'source_unchanged':True,'project_copy_used':False}
 return restored

def extend_past_last_connection(d,line,clearance=.6):
 """Voorkom dat geklemde projecties aansluitingen voorbij het einde verbergen."""
 from shapely.geometry import LineString
 a,b=line.coords[-2],line.coords[-1];length=math.dist(a,b)
 if length<.01:raise ValueError('Geen betrouwbare richting van kabeluiteinde: '+d['id'])
 u=((b[0]-a[0])/length,(b[1]-a[1])/length);records=[r for r in d['records'] if r['code'] in d['new_codes'] or r.get('new_connection')]
 at=[((r['tap'][0]-b[0])*u[0]+(r['tap'][1]-b[1])*u[1],r) for r in records];needed=max([q for q,r in at],default=-clearance)+clearance
 if needed<=.001:return line,None
 if needed>30:raise ValueError('Nieuwe hoofdkabel eindigt te ver voor laatste aansluiting; tracé opnieuw ontwerpen: '+d['id'])
 end=(b[0]+u[0]*needed,b[1]+u[1]*needed);result=LineString(list(line.coords[:-1])+[end])
 return result,{'direction':d['id'],'old_end':list(b),'new_end':list(end),'extended_m':needed,'clearance_past_last_tap_m':clearance,'last_connection_ids':[r['id'] for q,r in at if abs(q-(needed-clearance))<1]}

def splice_after_crossing(d,main,chain,road,obstacles):
 """Verplaats een AM naar bronkabel vlak na de laatste oversteek vóór de voeding."""
 from shapely.geometry import Point,LineString,shape
 from shapely.ops import substring
 root=main.project(Point(d['feed']['xy']));q=substring(main,0,root).intersection(road)
 parts=list(q.geoms) if hasattr(q,'geoms') else [q];parts=[p for p in parts if p.geom_type=='LineString' and p.length>=1]
 if not parts:return main,None
 crossing=max(parts,key=lambda p:main.project(Point(p.coords[-1])));exit_at=max(main.project(Point(p)) for p in [crossing.coords[0],crossing.coords[-1]])
 vertices=list(main.coords);positions=[main.project(Point(p)) for p in vertices];i=next(i for i,p in enumerate(positions) if p>=exit_at-.001);contact=chain.interpolate(chain.project(Point(vertices[i])));position=chain.project(contact)
 if contact.distance(Point(vertices[i]))>2 or contact.distance(road)<.05:return main,None
 parent=next(p for p in d['retained'] if p['code']==d['primary_code']);requirements=[r['chain_position_m'] for r in d['records'] if r['code']==d['primary_code'] and not r.get('new_connection')]
 if any(min(position,d['feed']['position_m'])+.001<v<max(position,d['feed']['position_m'])-.001 for v in requirements):return main,None
 prefix=vertices[:i]+[tuple(contact.coords[0])];tail=list(substring(main,root,main.length).coords);candidate=LineString(prefix+tail)
 if not candidate.is_simple or candidate.intersection(obstacles).length>main.intersection(obstacles).length+1e-6:return main,None
 if candidate.intersection(road).hausdorff_distance(main.intersection(road))>.01:return main,None
 if requirements and min(requirements)>position:parent['lo']=position
 elif requirements and max(requirements)<position:parent['hi']=position
 else:return main,None
 old=d['feed']['xy'];d['feed']['xy']=list(contact.coords[0]);d['feed']['position_m']=position
 parent['geometry']=substring(chain,parent['lo'],parent['hi']).__geo_interface__
 return candidate,{'direction':d['id'],'old_xy':old,'new_xy':d['feed']['xy'],'reason':'AM direct na haakse oversteek op bestaande kabel'}
