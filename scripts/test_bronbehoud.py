import unittest

class Bronbehoud(unittest.TestCase):
 def test_changed_original_width_is_detected(self):
  import ezdxf
  from vo_bronbehoud import check_source_preservation
  from io import StringIO
  base=ezdxf.new();e=base.modelspace().add_lwpolyline([(0,0),(1,0)])
  stream=StringIO();base.write(stream);stream.seek(0);saved=ezdxf.read(stream)
  data={'config':{},'connections':[]}
  self.assertEqual(check_source_preservation(base,saved,data),[])
  saved.entitydb[e.dxf.handle].dxf.const_width=.1
  self.assertEqual(len(check_source_preservation(base,saved,data)),1)

 def test_crossing_neighbour_direction_is_detected(self):
  import ezdxf
  from shapely.geometry import LineString,box
  from vo_bronbehoud import check_neighbour_crossings
  base=ezdxf.new();base.modelspace().add_lwpolyline([(0,-5),(0,5)],dxfattribs={'layer':'Aansluiting LS K03'})
  self.assertEqual(len(check_neighbour_crossings(base,{'R2':LineString([(-5,0),(5,0)])},box(10,10,11,11))),1)

 def test_new_handle_gets_style_without_touching_neighbour_same_layer(self):
  import ezdxf
  from vo_kabelafwerking import apply_cable_style
  doc=ezdxf.new();m=doc.modelspace();old=m.add_lwpolyline([(0,0),(1,0)],dxfattribs={'layer':'Aansluiting LS K03'});new=m.add_lwpolyline([(0,1),(1,1)],dxfattribs={'layer':'Aansluiting LS K03'})
  apply_cable_style(doc,new_handles=[new.dxf.handle],scope_handles={new.dxf.handle})
  self.assertEqual(old.dxf.const_width,0);self.assertEqual(new.dxf.const_width,.1);self.assertEqual(new.dxf.linetype,'DASHED');self.assertEqual(new.dxf.ltscale,.0035)

if __name__=='__main__':unittest.main()
