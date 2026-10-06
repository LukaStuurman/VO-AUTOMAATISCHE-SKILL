"""Rechte RT-kolom, richtingsplusjes en wipeout voor symbolen én attributen."""
import re

def slot(layer):
 match=re.search(r'K(\d{2})$',layer)
 return int(match[1]) if match else None

def apply_fuse_legend(doc,data):
 from ezdxf import bbox
 from ezdxf.math import Vec3
 for handle,name in data['drawing']['symbol_types'].items():
  if name!='RT 1-12':continue
  ref=doc.entitydb[handle];old=doc.blocks.get(ref.dxf.name);circles=[e.copy() for e in old.query('CIRCLE') if slot(e.dxf.layer)];numbers={slot(e.dxf.layer) for e in circles}
  if numbers!=set(range(1,13)):raise ValueError('Afzekeringsblok mist twaalf richtingrondjes')
  # Create a private block: neighbouring stations and original templates remain.
  blockname='LSVO_RT_'+handle
  if blockname in doc.blocks:blockname=doc.blocks.anonymous_block_name('U')
  block=doc.blocks.new(blockname);matrix=ref.matrix44();inverse=matrix.copy();inverse.inverse();world={slot(e.dxf.layer):matrix.transform(e.dxf.center) for e in circles};x=sum(p.x for p in world.values())/12;y0=world[1].y;pitch=1.25
  for e in circles:
   number=slot(e.dxf.layer);e.dxf.center=inverse.transform(Vec3(x,y0+(number-1)*pitch,0));block.add_entity(e)
  ref.dxf.name=blockname;used=set()
  for attr in ref.attribs:
   match=re.search(r'RT_(\d+)',attr.dxf.tag)
   if not match:continue
   number=int(match[1]);attr.dxf.insert=(x+1.2,y0+(number-1)*pitch-.35,0);attr.dxf.rotation=0
   if attr.dxf.hasattr('align_point'):attr.dxf.align_point=attr.dxf.insert
   if re.search(r'\b\d+A\b',attr.dxf.text):used.add(number)
  pluses={}
  for e in circles:
   number=slot(e.dxf.layer)
   if number not in used:continue
   cy=y0+(number-1)*pitch;size=e.dxf.radius;attrs={'layer':e.dxf.layer,'color':256}
   pair=[block.add_line(inverse.transform(Vec3(x-size,cy,0)),inverse.transform(Vec3(x+size,cy,0)),dxfattribs=attrs),block.add_line(inverse.transform(Vec3(x,cy-size,0)),inverse.transform(Vec3(x,cy+size,0)),dxfattribs=attrs)];pluses[str(number)]=[v.dxf.handle for v in pair]
  ext=bbox.extents([ref]);margin=.45;bounds=[ext.extmin.x-margin,ext.extmin.y-margin,ext.extmax.x+margin,ext.extmax.y+margin];x0,y1,x1,y2=bounds
  polygon=[inverse.transform(Vec3(a,b,0)).xy for a,b in [(x0,y1),(x1,y1),(x1,y2),(x0,y2)]];wipeout=block.add_wipeout(polygon,dxfattribs={'layer':'0'})
  block.set_redraw_order([(wipeout.dxf.handle,'1')]+[(e.dxf.handle,format(i+2,'X')) for i,e in enumerate(block) if e is not wipeout]);doc.header['$SORTENTS']=doc.header.get('$SORTENTS',0)|16|32|64
  data['fuse_legend_layout']={'insert_handle':handle,'block':blockname,'circle_x':x,'first_circle_y':y0,'row_spacing_m':pitch,'used_slots':sorted(used),'plus_handles':pluses,'wipeout_handle':wipeout.dxf.handle,'wipeout_world_bounds':bounds}
 return data

def validate_fuse_legend(doc,data):
 from ezdxf import bbox
 from shapely.geometry import Polygon,box
 row=data.get('fuse_legend_layout')
 if not row:return []
 ref=doc.entitydb.get(row['insert_handle']);errors=[]
 if ref is None:return [{'reason':'Afzekeringsblok ontbreekt'}]
 block=doc.blocks.get(ref.dxf.name);matrix=ref.matrix44();circles={slot(e.dxf.layer):e for e in block.query('CIRCLE') if slot(e.dxf.layer)}
 if set(circles)!=set(range(1,13)):errors.append({'reason':'Niet twaalf rondjes'})
 for number,e in circles.items():
  p=matrix.transform(e.dxf.center)
  if abs(p.x-row['circle_x'])>.000001 or abs(p.y-row['first_circle_y']-(number-1)*row['row_spacing_m'])>.000001:errors.append({'slot':number,'reason':'Rondje staat niet in rechte kolom'})
  lines=[v for v in block.query('LINE') if v.dxf.layer==e.dxf.layer]
  if number in row['used_slots']:
   if len(lines)!=2:errors.append({'slot':number,'reason':'Afgezekerde richting mist plusje op eigen laag'})
   else:
    for v in lines:
     a=matrix.transform(v.dxf.start);b=matrix.transform(v.dxf.end)
     if ((a+b)*.5-p).magnitude>.000001 or abs(a.distance(p)-e.dxf.radius)>.000001 or abs(b.distance(p)-e.dxf.radius)>.000001:errors.append({'slot':number,'reason':'Plusje loopt niet gecentreerd tot de cirkelrand'})
    vectors=[matrix.transform(v.dxf.end)-matrix.transform(v.dxf.start) for v in lines]
    if not (any(abs(v.x)<.000001 for v in vectors) and any(abs(v.y)<.000001 for v in vectors)):errors.append({'slot':number,'reason':'Plusje is niet horizontaal en verticaal'})
  elif lines:errors.append({'slot':number,'reason':'Vrije richting heeft plusje'})
 wipeout=doc.entitydb.get(row['wipeout_handle'])
 if wipeout is None or wipeout.dxftype()!='WIPEOUT':errors.append({'reason':'Wipeout ontbreekt'})
 else:
  polygon=Polygon([tuple(matrix.transform(p))[:2] for p in wipeout.boundary_path_wcs()])
  for e in list(circles.values()):
   ext=bbox.extents([e.copy().transform(matrix)])
   if not polygon.covers(box(ext.extmin.x,ext.extmin.y,ext.extmax.x,ext.extmax.y)):errors.append({'reason':'Wipeout dekt rondjes niet'})
  for attr in ref.attribs:
   ext=bbox.extents([attr])
   if ext.has_data and not polygon.covers(box(ext.extmin.x,ext.extmin.y,ext.extmax.x,ext.extmax.y)):errors.append({'slot':attr.dxf.tag,'reason':'Wipeout dekt tekst niet'})
  if list(block.entities_in_redraw_order())[0].dxf.handle!=wipeout.dxf.handle:errors.append({'reason':'Wipeout niet achter blokinhoud'})
 return errors
