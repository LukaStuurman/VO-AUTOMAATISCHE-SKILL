"""Conservatieve obstakels uit eigen topografie; symbolen zijn geen wortelzones."""
def topography_obstacles(config,region):
 import ezdxf
 from ezdxf import path,bbox
 from shapely.geometry import Polygon,Point,GeometryCollection
 from shapely.ops import unary_union
 doc=ezdxf.readfile(config['topo_dxf']);features=[];area=region.buffer(7)
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
 return {'trees':unary_union([g for kind,g in features if kind=='tree_symbol']), 'uncertain_contours':unary_union([g for kind,g in features if kind=='unclassified_curved_contour']), 'count':len(features),'root_zones_verified':False}
