"""Read-back evidence that blank-source objects and external blocks are intact."""

def check_source_preservation(base,doc,data):
 from ezdxf.lldxf.tagwriter import TagCollector
 exceptions={r['source_circle_handle'] for r in data['config'].get('source_corrections',[])}
 exceptions.update(r['original_text_handle'] for r in data['connections'] if r['id'] in exceptions)
 def tags(entity):return [(t.code,str(t.value)) for t in TagCollector.dxftags(entity)]
 errors=[]
 for original in base.modelspace():
  if original.dxf.handle in exceptions:continue
  saved=doc.entitydb.get(original.dxf.handle)
  if saved is None or not saved.is_alive or tags(original)!=tags(saved):errors.append({'handle':original.dxf.handle,'layer':original.dxf.layer,'reason':'Oorspronkelijk hoofdtekeningobject gewijzigd of verdwenen'})
 for block in base.blocks:
  if not block.block.dxf.flags&4:continue
  saved=doc.blocks.get(block.name)
  if tags(block.block)!=tags(saved.block) or [tags(e) for e in block]!=[tags(e) for e in saved]:errors.append({'block':block.name,'reason':'Xref-definitie of inhoud gewijzigd'})
 return errors

def check_neighbour_crossings(base,lines,station):
 from shapely.geometry import LineString
 errors=[]
 for e in base.modelspace().query('LWPOLYLINE'):
  if not e.dxf.layer.startswith('Aansluiting LS K') or len(e)<2:continue
  g=LineString(e.get_points('xy'))
  for name,new in lines.items():
   hit=new.intersection(g).difference(station)
   if not hit.is_empty:errors.append({'direction':name,'source_handle':e.dxf.handle,'source_layer':e.dxf.layer,'geometry':hit.__geo_interface__})
 return errors
