"""Conservatieve obstakels uit eigen topografie; symbolen zijn geen wortelzones."""
def topography_obstacles(config,region):
 import ezdxf,re
 from ezdxf import path,bbox
 from ezdxf.disassemble import recursive_decompose
 from shapely.geometry import Polygon,Point,GeometryCollection
 from shapely.ops import unary_union
 doc=ezdxf.readfile(config['topo_dxf']);features=[];area=region.buffer(7);building_rows=[]
 flattened=list(recursive_decompose(doc.modelspace()));labels=[]
 for e in flattened:
  if e.dxftype() not in ['TEXT','MTEXT']:continue
  text=e.plain_text() if e.dxftype()=='MTEXT' else e.dxf.text;height=e.dxf.char_height if e.dxftype()=='MTEXT' else e.dxf.height
  if height>=.5 and re.fullmatch(r'\d{1,4}[a-zA-Z]?(?:\s*[-/]\s*\d{1,4}[a-zA-Z]?)?',text.strip()):labels.append((text,Point(e.dxf.insert.xy)))
 for index,e in enumerate(flattened):
  if e.dxftype() not in ['LWPOLYLINE','POLYLINE']:continue
  try:points=[tuple(v)[:2] for v in path.make_path(e).flattening(.04)]
  except (ValueError,TypeError):continue
  closed=e.closed if e.dxftype()=='LWPOLYLINE' else e.is_closed
  if len(points)<4 or (not closed and Point(points[0]).distance(Point(points[-1]))>.01):continue
  g=Polygon(points)
  if not g.is_valid:g=g.buffer(0)
  if not 3<g.area<5000 or not g.intersects(area):continue
  inside=[text for text,p in labels if g.covers(p)];semantic='BEBOUWING' in e.dxf.layer.upper() or 'BUILDING' in e.dxf.layer.upper() or 'PAND' in e.dxf.layer.upper()
  if semantic or inside:building_rows.append({'source':config['topo_dxf'],'source_contour_index':index,'layer':e.dxf.layer,'house_labels':inside,'basis':'Building layer' if semantic else 'Closed topographic contour containing house-number label','geometry':g.__geo_interface__});features.append(('building',g))
 def visit(e,depth=0):
  if e.dxftype()=='INSERT':
   if e.dxf.name.startswith('SGR-BOOM'):
    bb=bbox.extents([e]);g=Point(bb.center.x,bb.center.y).buffer(max(bb.size.x,bb.size.y)/2)
    if g.intersects(area):features.append(('tree_symbol',g))
   elif depth<3:
    for v in e.virtual_entities():visit(v,depth+1)
  elif e.dxftype()=='LWPOLYLINE' and e.closed and sum(abs(p[4])>1e-8 for p in e.get_points())>=3:
   g=Polygon([tuple(v)[:2] for v in path.make_path(e).flattening(.08)])
   if not g.is_valid:g=g.buffer(0)
   if .5<g.area<200 and g.intersects(area):features.append(('unclassified_curved_contour',g))
 for e in doc.modelspace():visit(e)
 return {'trees':unary_union([g for kind,g in features if kind=='tree_symbol']), 'uncertain_contours':unary_union([g for kind,g in features if kind=='unclassified_curved_contour']), 'buildings':unary_union([g for kind,g in features if kind=='building']),'building_evidence':building_rows,'count':len(features),'root_zones_verified':False}
