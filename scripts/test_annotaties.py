import unittest

class Annotaties(unittest.TestCase):
 def test_overzetter_is_behind_circle_not_towards_cable(self):
  from shapely.geometry import LineString
  from vo_annotaties import overzetter_position
  p,contact=overzetter_position([10,5],LineString([(0,0),(20,0)]))
  self.assertEqual(contact,[10,0]);self.assertAlmostEqual(p[0],10);self.assertAlmostEqual(p[1],7.6)

 def test_first_connection_uses_feed_and_existing_branch_path(self):
  from shapely.geometry import LineString
  from vo_annotaties import first_connection
  main=LineString([(0,0),(30,0)]);old=LineString([(30,0),(130,0)]);branch=LineString([(70,0),(70,50)])
  d={'primary_code':'MAIN','new_codes':[],'feed':{'xy':[30,0],'position_m':0},'parent_child_positions':{'BRANCH':{'parent_position':40,'xy':[70,0]}},'records':[{'id':'late_branch','code':'BRANCH','chain_position_m':2,'xy':[1,1]},{'id':'early_main','code':'MAIN','chain_position_m':10,'xy':[100,100]}]}
  r,distance=first_connection(d,main,{'MAIN':old,'BRANCH':branch});self.assertEqual(r['id'],'early_main');self.assertEqual(distance,40)

if __name__=='__main__':unittest.main()
