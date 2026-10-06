"""Leesbare hostannotaties langs lokale kabelstukken; moffen als laatste tekenen.

Werkt uitsluitend op modelspace-objecten in de hoofdtekening. Xrefs worden niet
geopend, gewijzigd of geëxplodeerd. Kabels en symbolen worden niet verplaatst.
"""
import math,re

CABLE_TEXT=re.compile(r'^\d+(?:Al|Cu)?(?:\+\d+)?\+?\s*/\s*(?:\?+-\d+|\(was\s+[^)]+\))$')
_LOCAL_FOOTPRINTS={}

def text_footprint(entity,padding=.18):
 from ezdxf import bbox
 from shapely.geometry import box,GeometryCollection
 from shapely.affinity import rotate,translate
 key=(id(entity.doc),entity.dxf.text,padding)+tuple(entity.dxf.get(k) for k in ['height','style','width','oblique','halign','valign','text_generation_flag'])
 local=_LOCAL_FOOTPRINTS.get(key)
 if local is None:
  copy=entity.copy();copy.dxf.rotation=0;copy.dxf.insert=(0,0,0)
  if copy.dxf.hasattr('align_point'):copy.dxf.align_point=(0,0,0)
  ext=bbox.extents([copy])
  if not ext.has_data:return GeometryCollection()
  local=box(ext.extmin.x-padding,ext.extmin.y-padding,ext.extmax.x+padding,ext.extmax.y+padding);_LOCAL_FOOTPRINTS[key]=local
 return translate(rotate(local,entity.dxf.rotation,origin=(0,0)),entity.dxf.insert.x,entity.dxf.insert.y)

def cable_lines(doc):
 from shapely.geometry import LineString
 result=[]
 for e in doc.modelspace().query('LWPOLYLINE'):
  layer=e.dxf.layer
  if layer.startswith(('Aansluiting LS K','LBK')) or layer=='01 - Bestaande kabel':
   points=e.get_points('xy')
   if len(points)>1:result.append((e,LineString(points)))
 return result

def straight_runs(line):
 """Merge collinear vertices, without using the cable's endpoint chord."""
 from shapely.geometry import LineString
 points=list(line.simplify(.10,preserve_topology=True).coords);runs=[];start=points[0];last=start;axis=None
 for point in points[1:]:
  dx,dy=point[0]-last[0],point[1]-last[1];length=math.hypot(dx,dy)
  if length<1e-8:continue
  u=(dx/length,dy/length)
  if axis is not None and (abs(axis[0]*u[1]-axis[1]*u[0])>1e-5 or axis[0]*u[0]+axis[1]*u[1]<0):
   runs.append(LineString([start,last]));start=last
  axis=u;last=point
 if math.dist(start,last)>1e-8:runs.append(LineString([start,last]))
 return runs

def mof_handles(doc,data):
 known=data.get('drawing',{}).get('symbol_types',{})
 return {e.dxf.handle for e in doc.modelspace().query('INSERT') if 'MOF' in known.get(e.dxf.handle,e.dxf.name).upper() and not (doc.blocks.get(e.dxf.name).block.dxf.flags&4)}

def moffen_to_front(doc,data):
 msp=doc.modelspace();mofs=mof_handles(doc,data);order=list(msp.entities_in_redraw_order());ordered=[e for e in order if e.dxf.handle not in mofs]+[e for e in order if e.dxf.handle in mofs]
 msp.set_redraw_order([(e.dxf.handle,format(i+1,'X')) for i,e in enumerate(ordered)])
 doc.header['$SORTENTS']=doc.header.get('$SORTENTS',0)|16|32|64
 data['mof_draw_order']={'handles':sorted(mofs),'top_of_modelspace':True}

def apply_text_layout(doc,data):
 from ezdxf import bbox
 from shapely.geometry import Point,box,LineString
 from shapely.ops import unary_union
 msp=doc.modelspace();generated=set(data['drawing']['new_entity_handles']);cables=cable_lines(doc);cable_blocker=unary_union([g.buffer(.14) for _,g in cables]);texts=[e for e in msp.query('TEXT') if e.dxf.handle in generated]
 labels=[e for e in texts if CABLE_TEXT.fullmatch(e.dxf.text.strip())];moflabels=[e for e in texts if re.match(r'^(?:EM|AM|VM)(?:\s|$)',e.dxf.text) or e.dxf.text=='Bestaand'];selected={e.dxf.handle for e in labels+moflabels};fixed=[]
 for e in msp.query('TEXT MTEXT INSERT'):
  if e.dxf.handle in selected:continue
  if e.dxftype()=='INSERT' and doc.blocks.get(e.dxf.name).block.dxf.flags&4:continue
  if e.dxftype()=='TEXT':foot=text_footprint(e,.12)
  else:
   ext=bbox.extents([e])
   if not ext.has_data:continue
   foot=box(ext.extmin.x-.12,ext.extmin.y-.12,ext.extmax.x+.12,ext.extmax.y+.12)
  fixed.append(foot)
 fixed.extend(Point(r['xy']).buffer(1.15) for r in data['connections'])
 boundary=doc.entitydb.get(data.get('config',{}).get('boundary_handle',''))
 if boundary is not None and boundary.dxftype()=='LWPOLYLINE':fixed.append(LineString(boundary.get_points('xy')).buffer(boundary.dxf.get('const_width',0)/2+.2))
 occupied=unary_union(fixed);rows=[]
 for e in labels:
  p=Point(e.dxf.insert.x,e.dxf.insert.y);original=list(e.dxf.insert);oldangle=e.dxf.rotation;e.dxf.rotation=0;foot=text_footprint(e);width=foot.bounds[2]-foot.bounds[0];e.dxf.rotation=oldangle
  if e.dxf.layer.startswith('Aansluiting LS K'):matches=[(c,g) for c,g in cables if c.dxf.layer==e.dxf.layer]
  else:
   code=re.search(r'\(was\s+([^)]+)\)',e.dxf.text)
   parts=[r for d in data['directions'] for r in d['retained'] if code and r['code'].endswith(code[1])]
   from shapely.geometry import shape
   matching=[shape(r['geometry']) for r in parts]
   matches=[(c,g) for c,g in cables if c.dxf.layer=='01 - Bestaande kabel' and any(g.hausdorff_distance(v)<.01 for v in matching)]
  if not matches:raise ValueError('Geen eigen kabel voor tekst '+e.dxf.text)
  options=[(c,g,run) for c,g in matches for run in straight_runs(g)]
  adequate=[v for v in options if v[2].length>=width+.5]
  c,g,run=min(adequate or options,key=lambda v:(v[2].distance(p),-v[2].length));a,b=run.coords;dx,dy=b[0]-a[0],b[1]-a[1];angle=math.degrees(math.atan2(dy,dx));angle=(angle+90)%180-90;u=(math.cos(math.radians(angle)),math.sin(math.radians(angle)));n=(-u[1],u[0]);e.dxf.rotation=angle
  rows.append({'e':e,'run':run,'u':u,'n':n,'old':original,'cable_handle':c.dxf.handle,'width':width})
 # Nearby labels on parallel lanes share one text station. Rank by geometry,
 # not by colour or direction number; readable angle reversal reverses normals.
 groups=[]
 def shared_space(group,row):
  u=group[0]['u'];members=group+[row];dot=lambda p:p[0]*u[0]+p[1]*u[1]
  lo=max(min(dot(p) for p in r['run'].coords) for r in members);hi=min(max(dot(p) for p in r['run'].coords) for r in members)
  return hi-lo>=max(r['width'] for r in members)+.5
 for row in rows:
  group=next((group for group in groups if abs(group[0]['u'][0]*row['u'][1]-group[0]['u'][1]*row['u'][0])<math.sin(math.radians(.1)) and group[0]['run'].distance(row['run'])<1.01 and math.dist(group[0]['old'][:2],row['old'][:2])<max(group[0]['width'],row['width'])+3 and shared_space(group,row)),None)
  if group is None:groups.append([row])
  else:group.append(row)
 layout=[];bundle_rows=[]
 for group in groups:
  u=group[0]['u'];n=group[0]['n'];dot=lambda p,v:p[0]*v[0]+p[1]*v[1]
  lo=max(min(dot(p,u) for p in r['run'].coords) for r in group);hi=min(max(dot(p,u) for p in r['run'].coords) for r in group);width=max(r['width'] for r in group)
  if hi-lo<width+.4:raise ValueError('Onvoldoende gezamenlijk recht kabelstuk voor teksten: '+', '.join(r['e'].dxf.text+' '+r['e'].dxf.handle for r in group))
  group.sort(key=lambda r:dot(r['run'].coords[0],n));base=min(hi-width-.2,max(lo+.2,sum(dot(r['old'],u) for r in group)/len(group)));linepos=[dot(r['run'].coords[0],n) for r in group];gap=max(1.5,2*max(r['e'].dxf.height for r in group));choices=[]
  for r in group:r['e'].dxf.rotation=math.degrees(math.atan2(u[1],u[0]))
  for side in [1,-1]:
   for margin in [.65,1,1.5,2,3,4,5,6,8]:
    for delta in [0,-2,2,-4,4]:
     t=min(hi-width-.2,max(lo+.2,base+delta));positions=[];feet=[]
     for i,r in enumerate(group):
      q=max(linepos)+margin+i*gap if side==1 else min(linepos)-margin-(len(group)-i)*gap
      p=(t*u[0]+q*n[0],t*u[1]+q*n[1]);r['e'].dxf.insert=(*p,0);foot=text_footprint(r['e']);positions.append(p);feet.append(foot)
     combined=unary_union(feet);overlap=combined.intersection(cable_blocker).area+combined.intersection(occupied).area
     if overlap<1e-9:choices.append((margin+.08*abs(t-base)+(0 if side==1 else .1),positions,feet))
  if not choices:raise ValueError('Geen vrije plaats voor kabelteksten: '+', '.join(r['e'].dxf.text for r in group))
  _,positions,feet=min(choices,key=lambda v:v[0]);occupied=unary_union([occupied,*feet]);handles=[]
  for r,p in zip(group,positions):
   e=r['e'];e.dxf.insert=(*p,0);handles.append(e.dxf.handle);layout.append({'handle':e.dxf.handle,'kind':'cable','cable_handle':r['cable_handle'],'local_segment':list(r['run'].coords),'xy':list(p),'rotation':e.dxf.rotation,'layer':e.dxf.layer})
  if len(group)>1:bundle_rows.append({'handles_in_cable_order':handles,'normal':list(n),'minimum_row_spacing_m':gap})
 # Mof annotations stay close to their actual symbols; look on either side
 # using real rotated text extents. Never fix overlap by covering the wires.
 mofs=[doc.entitydb[h] for h in mof_handles(doc,data)]
 centers={e.dxf.handle:Point(bbox.extents([e]).center.xy) for e in mofs}
 known_mofs={r['handle']:r['mof_handle'] for r in data.get('text_layout',[]) if r['kind']=='mof'}
 for e in moflabels:
  original=Point(e.dxf.insert.x,e.dxf.insert.y);candidates=[(h,p) for h,p in centers.items() if doc.entitydb[h].dxf.layer==e.dxf.layer]
  if known_mofs.get(e.dxf.handle) in centers:h=known_mofs[e.dxf.handle];anchor=centers[h]
  else:h,anchor=min(candidates or list(centers.items()),key=lambda v:v[1].distance(original))
  e.dxf.rotation=0
  width=text_footprint(e).bounds[2]-text_footprint(e).bounds[0];choices=[]
  positions=[(original.x,original.y)]
  for distance in [1.1,1.6,2.2,3,4,5,6,8,10,12]:
   for i in range(16):
    angle=2*math.pi*i/16;cx=anchor.x+distance*math.cos(angle);cy=anchor.y+distance*math.sin(angle)
    positions.extend([(cx,cy),(cx-width,cy),(cx-width/2,cy)])
  for p in positions:
   e.dxf.insert=(*p,0);foot=text_footprint(e)
   if foot.intersection(cable_blocker).area>1e-9 or foot.intersection(occupied).area>1e-9:continue
   choices.append((foot.distance(anchor)+.05*Point(p).distance(original),p,foot))
  if not choices:raise ValueError('Geen vrije plaats voor moftekst '+e.dxf.text)
  _,p,foot=min(choices,key=lambda v:v[0]);e.dxf.insert=(*p,0);occupied=unary_union([occupied,foot]);layout.append({'handle':e.dxf.handle,'kind':'mof','mof_handle':h,'xy':list(p),'rotation':0,'layer':e.dxf.layer})
 data['text_layout']=layout;data['cable_text_stacks']=bundle_rows;moffen_to_front(doc,data)
 return data

def validate_text_layout(doc,data):
 from shapely.geometry import Point,LineString
 from shapely.ops import unary_union
 errors=[];blocker=unary_union([g.buffer(.14) for _,g in cable_lines(doc)]);feet={}
 for row in data.get('text_layout',[]):
  e=doc.entitydb.get(row['handle'])
  if e is None:errors.append({'handle':row['handle'],'reason':'Tekst ontbreekt'});continue
  foot=text_footprint(e);feet[row['handle']]=foot
  if foot.intersection(blocker).area>1e-8:errors.append({'handle':row['handle'],'reason':'Tekst overlapt kabelpolyline'})
  if Point(e.dxf.insert.x,e.dxf.insert.y).distance(Point(row['xy']))>.001 or e.dxf.layer!=row['layer']:errors.append({'handle':row['handle'],'reason':'Tekstplaatsing of laag wijkt af'})
  if row['kind']=='cable':
   a,b=row['local_segment'];angle=math.degrees(math.atan2(b[1]-a[1],b[0]-a[0]));difference=abs((e.dxf.rotation-angle+90)%180-90)
   if difference>.1:errors.append({'handle':row['handle'],'reason':'Kabeltekst volgt lokaal kabelstuk niet'})
 for group in data.get('cable_text_stacks',[]):
  handles=group['handles_in_cable_order'];n=group['normal'];positions=[feet[h].centroid.x*n[0]+feet[h].centroid.y*n[1] for h in handles]
  if any(b-a<group['minimum_row_spacing_m']-.01 for a,b in zip(positions,positions[1:])):errors.append({'handles':handles,'reason':'Kabeltekstvolgorde of regelafstand onjuist'})
  if any(feet[a].intersects(feet[b]) for a,b in zip(handles,handles[1:])):errors.append({'handles':handles,'reason':'Gestapelde kabelteksten overlappen'})
 for row in data.get('direction_info_layout',[]):
  for key in ['amp_handle','length_handle']:
   e=doc.entitydb[row[key]]
   if text_footprint(e).intersection(blocker).area>1e-8:errors.append({'handle':e.dxf.handle,'reason':'Richtinginfo overlapt kabelpolyline'})
 mofs=mof_handles(doc,data);order=[e.dxf.handle for e in doc.modelspace().entities_in_redraw_order()]
 if mofs and set(order[-len(mofs):])!=mofs:errors.append({'reason':'Moffen staan niet bovenaan draw order'})
 if mofs and doc.header.get('$SORTENTS',0)&(16|32|64)!=(16|32|64):errors.append({'reason':'Tekenvolgorde niet actief voor regenereren/plotten'})
 return errors

def mof_label_matches(doc,data,entity,xy,max_distance=2):
 """Distance to the visible text, with explicit mof association when present.

 A left-hand label may begin several metres away while its right edge is
 immediately beside the mof. Insertion-point distance is not visual distance.
 """
 from shapely.geometry import Point
 from ezdxf import bbox
 row=next((r for r in data.get('text_layout',[]) if r['handle']==entity.dxf.handle and r['kind']=='mof'),None)
 if row:
  mof=doc.entitydb.get(row['mof_handle'])
  if mof is None or Point(bbox.extents([mof]).center.xy).distance(Point(xy))>.05:return False
  return text_footprint(entity).distance(Point(xy))<max_distance
 return Point(entity.dxf.insert.xy).distance(Point(xy))<max_distance
