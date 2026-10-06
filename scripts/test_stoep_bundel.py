import unittest

class StoepBundel(unittest.TestCase):
 def test_shared_frontage_can_replace_a_wider_crossing_detour(self):
  from shapely.geometry import LineString,Polygon
  from vo_bundel import repair_bundle,crossing_pairs
  lines={'fixed':LineString([(0,0),(100,0)]),'moving':LineString([(0,1),(20,1),(30,-2),(70,-2),(80,1),(100,1)])}
  repaired,log=repair_bundle(lines,.2,Polygon(),Polygon(),{'fixed'})
  self.assertTrue(log);self.assertFalse(crossing_pairs(repaired,Polygon()));self.assertTrue(repaired['moving'].is_simple)

 def test_repairs_cannot_disconnect_a_required_splice(self):
  from shapely.geometry import LineString,Point,Polygon
  from vo_bundel import repair_bundle
  lines={'fixed':LineString([(0,0),(20,0)]),'moving':LineString([(0,2),(8,-1),(20,2)])}
  repaired,log=repair_bundle(lines,.2,Polygon(),Polygon(),{'fixed'},anchors={'moving':[[8,-1]]})
  self.assertLess(repaired['moving'].distance(Point(8,-1)),1e-6)

 def test_free_end_contact_is_removed_without_cutting_interior_contacts(self):
  from shapely.geometry import LineString
  from vo_bundel import separate_free_ends
  lines={'new':LineString([(0,0),(10,0)]),'other':LineString([(9.98,-5),(9.98,5)])}
  result,log=separate_free_ends(lines,[{'id':'new','new_codes':['new'],'feed':None}],.2)
  self.assertTrue(log);self.assertTrue(result['new'].intersection(result['other']).is_empty);self.assertAlmostEqual(result['new'].length,9.58)
  interior={'new':lines['new'],'other':LineString([(5,-5),(5,5)])};result,log=separate_free_ends(interior,[{'id':'new','new_codes':['new'],'feed':None}],.2)
  self.assertFalse(log);self.assertEqual(result['new'].length,10)

 def test_an_existing_splice_endpoint_is_never_trimmed(self):
  from shapely.geometry import LineString
  from vo_bundel import separate_free_ends
  lines={'new':LineString([(0,0),(10,0)]),'other':LineString([(9.98,-5),(9.98,5)])}
  result,log=separate_free_ends(lines,[{'id':'new','new_codes':['new'],'feed':{'xy':[10,0]}}],.2)
  self.assertFalse(log);self.assertEqual(result['new'].length,10)

if __name__=='__main__':unittest.main()
