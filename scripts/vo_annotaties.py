"""Overzetters achter stroombollen; richtinginformatie bij eerste gevoede aansluiting."""
import math,re

def first_connection(direction,main,chains):
 from shapely.geometry import Point
 def distance(r):
  if r['code'] in direction['new_codes'] or r.get('new_connection'):
   return main.project(Point(r.get('new_tap',r['tap'])))
  feed=direction['feed'];prefix=main.project(Point(feed['xy']))
  if r['code']==direction['primary_code']:return prefix+abs(r['chain_position_m']-feed['position_m'])
  join=direction['parent_child_positions'][r['code']];root=chains[r['code']].project(Point(join['xy']))
  return prefix+abs(join['parent_position']-feed['position_m'])+abs(r['chain_position_m']-root)
 record=min(direction['records'],key=lambda r:(distance(r),r['id']))
 return record,distance(record)

def overzetter_position(circle,main,offset=2.6):
 from shapely.geometry import Point
 from shapely.ops import nearest_points
 p=Point(circle);_,contact=nearest_points(p,main);dx=p.x-contact.x;dy=p.y-contact.y;length=math.hypot(dx,dy)
 if length<.01:raise ValueError('Stroombol ligt op kabel; bepaal annotatiezijde uit aansluitgeometrie.')
 return [p.x+offset*dx/length,p.y+offset*dy/length],list(contact.coords[0])

def apply_annotation_layout(doc,data):
 from ezdxf import bbox
 from shapely.geometry import shape,Point,box
 from shapely.ops import unary_union
 msp=doc.modelspace();lines={d['id']:shape(d['display_main']) for d in data['directions']};chains={c:shape(g) for c,g in data['existing_chains'].items()};handles=data['drawing']['new_entity_handles'];symbol_types=data['drawing']['symbol_types'];records=[r for r in data['connections'] if r['overzetter']];symbols=[h for h,n in symbol_types.items() if n=='OVERZETTER'];offset=data['config']['rules'].get('overzetter_circle_offset_m',2.6)
 if len(symbols)!=len(records):raise ValueError('Overzetterregister wijkt af van CAD.')
 known={r['connection_id']:r['handle'] for r in data.get('overzetter_layout',[])}
 data['overzetter_layout']=[]
 for fallback,r in zip(symbols,records):
  handle=known.get(r['id'],fallback);e=doc.entitydb[handle];p,contact=overzetter_position(r['xy'],lines[r['direction']],offset);center=bbox.extents([e]).center;e.translate(p[0]-center.x,p[1]-center.y,0)
  data['overzetter_layout'].append({'connection_id':r['id'],'direction':r['direction'],'handle':handle,'circle_xy':r['xy'],'cable_contact_xy':contact,'xy':p,'circle_offset_m':offset})
 # Treat actual symbols, all current balls, cables and other annotations as
 # blockers. The first ball anchors the text; it is never moved to another house.
 blockers=[Point(r['xy']).buffer(1.15) for r in data['connections']]+[g.buffer(.3) for g in lines.values()]
 for h in symbol_types:
  e=doc.entitydb.get(h)
  if e is None:continue
  ext=bbox.extents([e]);blockers.append(box(ext.extmin.x-.2,ext.extmin.y-.2,ext.extmax.x+.2,ext.extmax.y+.2))
 labels={}
 for d in data['directions']:
  candidates=[doc.entitydb[h] for h in handles if doc.entitydb.get(h) is not None and doc.entitydb[h].dxftype()=='TEXT' and doc.entitydb[h].dxf.layer==d['layer']]
  amp=[e for e in candidates if re.fullmatch(r'\d+(?:,\d+)?Amp\.',e.dxf.text)];met=[e for e in candidates if re.fullmatch(r'\d+(?:,\d+)?Met\.',e.dxf.text)]
  if len(amp)!=1 or len(met)!=1:raise ValueError('Richtinginformatie niet eenduidig: '+d['id'])
  labels[d['id']]=(amp[0],met[0])
 excluded={e.dxf.handle for pair in labels.values() for e in pair}
 for e in msp.query('TEXT MTEXT'):
  if e.dxf.handle in excluded:continue
  # Avoid expensive font extents on distant background text.
  if min(Point(e.dxf.insert.xy).distance(Point(r['xy'])) for r in data['connections'])>15:continue
  ext=bbox.extents([e]);blockers.append(box(ext.extmin.x-.2,ext.extmin.y-.2,ext.extmax.x+.2,ext.extmax.y+.2))
 data['direction_info_layout']=[]
 for d in data['directions']:
  r,at=first_connection(d,lines[d['id']],chains);x,y=r['xy'];amp,met=labels[d['id']];amp.dxf.text=f'{d["load_A"]:.1f}'.replace('.',',')+'Amp.';met.dxf.text=f'{d["limiting"]["length_m"]:.2f}'.replace('.',',')+'Met.'
  extents=[bbox.extents([e]) for e in [amp,met]];width=max(e.size.x for e in extents);height=max(amp.dxf.height,met.dxf.height);row=height*1.5;options=[];near=[g for g in blockers if g.distance(Point(x,y))<18];occupied=unary_union(near)
  for dx in [-width-1.8,1.8,-width-3,3]:
   for dy in [row*.5,2.8,-2.8,4.2,-4.2]:
    p=(x+dx,y+dy);foot=box(p[0]-.25,p[1]-row-.3,p[0]+width+.25,p[1]+height+.3);overlap=foot.intersection(occupied).area;distance=foot.distance(Point(x,y));options.append((overlap*1000+distance+abs(dy)*.05,p,foot))
  _,p,foot=min(options,key=lambda v:v[0]);amp.dxf.insert=(p[0],p[1],0);met.dxf.insert=(p[0],p[1]-row,0);blockers.append(foot)
  data['direction_info_layout'].append({'direction':d['id'],'first_connection_id':r['id'],'first_circle_xy':r['xy'],'distance_from_station_m':at,'amp_handle':amp.dxf.handle,'length_handle':met.dxf.handle,'amp_xy':list(p),'length_xy':[p[0],p[1]-row]})
 return data

def validate_annotation_layout(doc,data):
 from ezdxf import bbox
 from shapely.geometry import Point,shape
 lines={d['id']:shape(d['display_main']) for d in data['directions']};chains={c:shape(g) for c,g in data['existing_chains'].items()};errors=[]
 for row in data.get('overzetter_layout',[]):
  e=doc.entitydb[row['handle']];center=bbox.extents([e]).center;p=Point(center.xy);circle=Point(row['circle_xy']);contact=Point(row['cable_contact_xy']);u=(circle.x-contact.x,circle.y-contact.y);v=(p.x-circle.x,p.y-circle.y)
  if u[0]*v[0]+u[1]*v[1]<=0 or lines[row['direction']].distance(p)<=lines[row['direction']].distance(circle) or p.distance(Point(row['xy']))>.001:errors.append({'connection':row['connection_id'],'reason':'Overzetter staat niet achter de stroombol, van de kabel af'})
 for row in data.get('direction_info_layout',[]):
  d=next(d for d in data['directions'] if d['id']==row['direction']);r,_=first_connection(d,lines[d['id']],chains)
  if r['id']!=row['first_connection_id']:errors.append({'direction':d['id'],'reason':'Richtinginfo staat bij verkeerde eerste aansluiting'})
  for key,position in [('amp_handle','amp_xy'),('length_handle','length_xy')]:
   e=doc.entitydb[row[key]]
   if e.dxf.layer!=d['layer'] or Point(e.dxf.insert.xy).distance(Point(row[position]))>.001:errors.append({'direction':d['id'],'reason':'Richtingtekst wijkt af van vastgelegde plaatsing'})
 return errors
