import unittest

class AanloopHerstel(unittest.TestCase):
 def test_entire_corner_bundle_stays_parallel_and_outside_road(self):
  from shapely.geometry import LineString,Point,box,Polygon
  from vo_aanloop_herstel import pavement_corner
  axis=LineString([(0,3),(4,3),(4,0),(6,0),(6,3),(10,3)]);lines={'R2':axis,'R3':axis.offset_curve(.2,join_style=2)};road=box(3,-.1,7,1)
  result=pavement_corner(lines,['R2','R3'],[5,0],road,Polygon(),box(-2,1.1,12,6),box(-2,-2,12,6))
  self.assertIsNotNone(result)
  for name,g in result['lines'].items():
   self.assertTrue(g.is_simple);self.assertTrue(g.intersection(road).is_empty);self.assertEqual(g.coords[0],lines[name].coords[0]);self.assertEqual(g.coords[-1],lines[name].coords[-1])
  self.assertAlmostEqual(result['lines']['R2'].distance(result['lines']['R3']),.2,places=6)

if __name__=='__main__':unittest.main()
