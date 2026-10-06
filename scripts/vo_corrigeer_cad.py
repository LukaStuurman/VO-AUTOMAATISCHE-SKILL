"""Werk opgeslagen CAD bij op basis van herziene lijnen en echte mofstatus."""
import math,re,itertools,json,copy
from pathlib import Path

def write_corrected_candidate(data,previous,out):
 import ezdxf
 from ezdxf import bbox
 from shapely.geometry import shape,Point,LineString
 from shapely.ops import unary_union,nearest_points
 from vo_stijl import style_templates
 from vo_eindmoffen import existing_joint_objects,retained_end_status
 from vo_mofverbindingen import align_splice_contacts,existing_branch_evidence
 from vo_paden import geometry_checks
 from vo_kabelafwerking import supplemental_work,draw_supplemental,apply_cable_style,restore_source_xrefs
 out=Path(out).resolve();out.mkdir(exist_ok=True);doc=ezdxf.readfile(previous['drawing']['file']);msp=doc.modelspace();cfg=data['config'];templates={k:v.copy() for k,v in style_templates(doc).items()};lines={d['id']:shape(d['display_main']) for d in data['directions']};chains={c:shape(g) for c,g in data['existing_chains'].items()};old_parts={d['id']:copy.deepcopy(d['retained']) for d in previous['directions']}
 data['splice_contact_adjustments']=align_splice_contacts(data['directions'],lines,chains);joints=existing_joint_objects(cfg['klic_dxf']);end_joints=[j for j in joints if j['kind']=='end'];generated=list(previous['drawing']['new_entity_handles']);symbol_types=dict(previous['drawing']['symbol_types'])
 # Reproject source taps after geometry changes, instead of carrying a former
 # endpoint-clamped new_tap into the last-connection calculation.
 connection_index={r['id']:r for r in data['connections']}
 for d in data['directions']:
  for r in d['records']:
   if r['code'] in d['new_codes'] or r.get('new_connection'):
    r['new_tap']=list(lines[d['id']].interpolate(lines[d['id']].project(Point(r['tap']))).coords[0]);connection_index[r['id']]['new_tap']=r['new_tap']
 for d in data['directions']:
  layer=d['layer'];g=lines[d['id']];old=next(p for p in previous['directions'] if p['id']==d['id']);old_met=f'{old["limiting"]["length_m"]:.2f}'.replace('.',',')+'Met.';d['geometry_calculation']=geometry_checks(d,g);d['limiting']=d['geometry_calculation']['selected']['limiting'];d['passes']=d['geometry_calculation']['selected']['passes'];d['display_main_length_m']=g.length
  for handle in list(generated):
   e=doc.entitydb.get(handle)
   if e is None:continue
   if e.dxftype()=='LWPOLYLINE' and e.dxf.layer==layer and LineString(e.get_points('xy')).length>20:e.set_points(list(g.coords),format='xy')
   elif e.dxftype()=='TEXT' and e.dxf.layer==layer and e.dxf.text==old_met:e.dxf.text=f'{d["limiting"]["length_m"]:.2f}'.replace('.',',')+'Met.'
 # Remove previous generated mof objects and their annotations together.
 for handle in list(generated):
  e=doc.entitydb.get(handle)
  if e is None:continue
  mof=e.dxftype()=='INSERT' and symbol_types.get(handle) in ['NIEUWE MOF','BESTAANDE MOF','MOF bestaand-nieuw']
  label=e.dxftype()=='TEXT' and (re.match(r'^(?:AM|VM|EM)(?:\s|$)',e.dxf.text) or e.dxf.text=='Bestaand' or (e.dxf.layer=='01 - Bestaande kabel' and '(was ' in e.dxf.text))
  old_tamp=e.dxftype()=='LWPOLYLINE' and any(e.dxf.handle==r.get('polyline_handle') for r in previous.get('station_tamps',[]))
  if mof or label or old_tamp or (e.dxftype()=='LWPOLYLINE' and e.dxf.layer=='01 - Bestaande kabel'):
   msp.delete_entity(e);generated.remove(handle);symbol_types.pop(handle,None)
 def symbol(name,p,layer):
  e=templates[name].copy();msp.add_entity(e);e.dxf.layer=layer;e.dxf.color=256;center=bbox.extents([e]).center;e.translate(p[0]-center.x,p[1]-center.y,0);generated.append(e.dxf.handle);symbol_types[e.dxf.handle]=name;return e
 def text(label,p,layer,angle=0):
  e=msp.add_text(label,dxfattribs={'layer':layer,'insert':p,'height':.7,'style':'ARIAL','rotation':angle,'color':256});generated.append(e.dxf.handle)
 def line(g,layer):
  e=msp.add_lwpolyline(list(g.coords),dxfattribs={'layer':layer,'color':256});generated.append(e.dxf.handle);return e
 for d in data['directions']:
  g=lines[d['id']];feed=d.get('feed');layer=d['layer'];d['end_mof_positions']=[];d['existing_end_mofs']=[];d['retained_end_work']=[];d['existing_branch_mofs']=[]
  if feed:
   p=feed['xy'];kind=d['splice_kind'];symbol('MOF bestaand-nieuw',p,layer);ret=next(p for p in d['retained'] if p['code']==d['primary_code']);text(kind+' 150Al->'+ret['type']+' (was '+d['primary_code'][3:]+')',(p[0]+1,p[1]+1),layer)
  for part in d['retained']:
   rg=shape(part['geometry']);line(rg,'01 - Bestaande kabel');mid=rg.interpolate(.5,normalized=True);a,b=rg.coords[0],rg.coords[-1];angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));angle=angle if -90<=angle<=90 else angle+180;text(part['type']+' / (was '+part['code'][3:]+')',(mid.x+.6,mid.y+.6),'01 - Bestaande kabel',angle)
   for p in [rg.coords[0],rg.coords[-1]]:
    if feed and math.dist(p,feed['xy'])<.1:continue
    if any(other is not part and shape(other['geometry']).distance(Point(p))<.05 for other in d['retained']):continue
    status=retained_end_status(p,chains[part['code']],end_joints);name='NIEUWE MOF' if status['new_required'] else 'BESTAANDE MOF';d['retained_end_work'].append(dict(status,code=part['code'],xy=list(p),symbol=name));symbol(name,p,layer if status['new_required'] else '01 - Bestaande kabel')
    if status['new_required']:text('EM (was '+part['code'][3:]+')',(p[0]+.8,p[1]+.8),layer);d['end_mof_positions'].append(list(p))
    else:text('Bestaand',(p[0]+.8,p[1]+.8),'01 - Bestaande kabel');d['existing_end_mofs'].append(dict(status,code=part['code'],xy=list(p)))
  for first,second in itertools.combinations(d['retained'],2):
   if first['code']==second['code']:continue
   pa,pb=nearest_points(shape(first['geometry']),shape(second['geometry']))
   if pa.distance(pb)>.1:continue
   p=list(pa.coords[0]);evidence=existing_branch_evidence(p,joints)
   if not evidence:raise ValueError('Bestaande aftakmof niet met KLIC onderbouwd: '+d['id'])
   symbol('BESTAANDE MOF',p,'01 - Bestaande kabel');text('Bestaand',(p[0]+.8,p[1]+.8),'01 - Bestaande kabel');d['existing_branch_mofs'].append({'xy':p,'codes':[first['code'],second['code']],'source_joint':evidence})
  if d['new_codes']:
   p=list(g.coords[-1]);symbol('NIEUWE MOF',p,layer);text('EM',(p[0]+.8,p[1]+.8),layer);d['end_mof_positions'].append(p)
 supplemental_work(data,joints,doc,previous_parts=old_parts);draw_supplemental(data,symbol,text,line)
 from vo_stationsuitloop import draw_tamps
 draw_tamps(data,doc,symbol,text,line)
 # Preserve circles/assignments; place symbols behind the balls, away from cable.
 from vo_annotaties import overzetter_position
 overzetters=[h for h,name in symbol_types.items() if name=='OVERZETTER'];records=[r for r in data['connections'] if r['overzetter']]
 if len(overzetters)!=len(records):raise ValueError('Overzetterregister en CAD verschillen.')
 for handle,r in zip(overzetters,records):
  e=doc.entitydb[handle];p,_=overzetter_position(r['xy'],lines[r['direction']],cfg['rules'].get('overzetter_circle_offset_m',2.6));center=bbox.extents([e]).center;e.translate(p[0]-center.x,p[1]-center.y,0)
 restore_source_xrefs(doc,data);removals=[]
 # Native cable text attached only to the removed arm must not remain orphaned.
 data['removed_native_labels']=[]
 for e in list(msp.query('TEXT MTEXT')):
  if e.dxf.handle in generated:continue
  label=e.dxf.text if e.dxftype()=='TEXT' else e.plain_text();point=Point(e.dxf.insert.xy)
  for code,original,removed,used in removals:
   if re.fullmatch(r'\s*\d+(?:Al|Cu)?\s*/\s*\(was\s+'+re.escape(code[3:])+r'\)\s*',label) and point.distance(removed)<2 and point.distance(used)>2:
    data['removed_native_labels'].append({'handle':e.dxf.handle,'text':label});msp.delete_entity(e);break
 for handle,name in symbol_types.items():
  if name!='RT 1-12':continue
  for attribute in doc.entitydb[handle].attribs:
   match=re.search(r'RT_(\d+)',attribute.dxf.tag)
   if not match:continue
   number=int(match.group(1));direction=next((d for d in data['directions'] if int(d['id'][1:])==number),None)
   if direction:attribute.dxf.text=f'RT {number:02}: {direction["limiting"]["max_fuse_A"]}A / / '+direction.get('new_cable_label','150Al')
   elif str(number) in cfg['special_slots']:attribute.dxf.text=f'RT {number:02}: '+cfg['special_slots'][str(number)]+' / / 150Al'
 data['drawing']['cable_style']=apply_cable_style(doc,new_layers=[d['layer'] for d in data['directions']]+[r['layer'] for r in data.get('station_tamps',[])]);data['drawing']['new_entity_handles']=generated;data['drawing']['symbol_types']=symbol_types
 from vo_annotaties import apply_annotation_layout
 apply_annotation_layout(doc,data)
 data['drawing']['file']=str(out/(data['station']+' - LS VO rechte straten en moffen.dxf'));doc.saveas(data['drawing']['file']);data['drawing']['audit_errors']=len(ezdxf.readfile(data['drawing']['file']).audit().errors)
 return data
