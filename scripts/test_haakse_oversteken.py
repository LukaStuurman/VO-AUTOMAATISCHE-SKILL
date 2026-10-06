import unittest

class HaakseOversteken(unittest.TestCase):
 def test_straight_diagonal_is_not_a_valid_crossing(self):
  from shapely.geometry import box,LineString
  from vo_oversteken import crossing_angle
  road=box(-10,-2,10,2);cross=LineString([(-2,-2),(2,2)])
  self.assertAlmostEqual(crossing_angle(cross,road),45)

 def test_repair_crosses_perpendicularly_and_turns_outside_road(self):
  from shapely.geometry import box,LineString,Polygon
  from vo_oversteken import perpendicular_crossings,crossing_angle
  road=box(-10,-2,10,2);old=LineString([(-4,-4),(4,4)]);new,changes=perpendicular_crossings(old,road,Polygon(),box(-20,-20,20,20))
  self.assertTrue(changes);inside=new.intersection(road);self.assertAlmostEqual(crossing_angle(inside,road),90);self.assertEqual(len(inside.coords),2);self.assertTrue(new.is_simple)

 def test_turn_does_not_overshoot_retained_main_in_pavement(self):
  from shapely.geometry import box,LineString,Polygon
  from vo_oversteken import perpendicular_crossings,crossing_angle
  road=box(-10,-2,10,2);old=LineString([(-4,-4),(2,2.4),(4,2.4)]);retained=LineString([(-10,2.6),(10,2.6)])
  new,changes=perpendicular_crossings(old,road,Polygon(),box(-20,-20,20,20),retained=retained)
  self.assertTrue(changes);self.assertAlmostEqual(crossing_angle(new.intersection(road),road),90);self.assertTrue(new.intersection(retained).is_empty);self.assertLess(changes[0]['outside_turn_margin_m'],.6)

if __name__=='__main__':unittest.main()
