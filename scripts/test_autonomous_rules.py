import unittest
from vo_terrein import vegetation_class,unused_parts

class SourceOnlyRules(unittest.TestCase):
 def test_plus_field_changes_green_classification(self):
  self.assertEqual(vegetation_class({'fysiek_voorkomen':'groenvoorziening','plus_fysiek_voorkomen':'bomen'}),'woody')
  self.assertEqual(vegetation_class({'fysiek_voorkomen':'groenvoorziening','plus_fysiek_voorkomen':'heesters'}),'woody')
  self.assertEqual(vegetation_class({'fysiek_voorkomen':'groenvoorziening','plus_fysiek_voorkomen':'gras'}),'open_green')
  self.assertEqual(vegetation_class({'fysiek_voorkomen':'groenvoorziening'}),'green_unknown')
 def test_other_direction_and_external_feed_protect_existing_cable(self):
  from shapely.geometry import LineString
  whole=LineString([(0,0),(30,0)])
  removal=unused_parts([whole],{'A':[LineString([(0,0),(10,0)])],'B':[LineString([(10,0),(20,0)])]},[LineString([(25,0),(30,0)])])[0]
  self.assertAlmostEqual(removal.length,5)
  self.assertEqual(list(removal.coords),[(20.,0.),(25.,0.)])
 def test_all_directions_assessed_before_removal(self):
  from shapely.geometry import LineString
  whole=LineString([(0,0),(20,0)])
  removal=unused_parts([whole],{'A':[whole],'B':[LineString([(8,0),(15,0)])]},[])[0]
  self.assertTrue(removal.is_empty)

 def test_split_code_removal_protects_both_direction_intervals(self):
  from shapely.geometry import LineString,box,shape
  from vo_verwijderen import removal_ledger
  whole=LineString([(0,0),(30,0)]);a=LineString([(0,0),(10,0)]);b=LineString([(15,0),(25,0)])
  source={'region':box(-1,-1,31,1),'groups':{'CODE-00':{'geometry':whole,'outside_taps':[],'combo':False}}}
  directions=[{'id':'A','retained':[{'code':'CODE-00','geometry':a}]},{'id':'B','retained':[{'code':'CODE-00','geometry':b}]}]
  row=removal_ledger(source,directions)[0];removed=shape(row['proposed_removal'])
  self.assertAlmostEqual(removed.length,10);self.assertAlmostEqual(removed.intersection(a).length,0);self.assertAlmostEqual(removed.intersection(b).length,0)
  source['groups']['CODE-00']['combo']=True
  self.assertEqual(removal_ledger(source,directions)[0]['proposed_removal_m'],0)

 def test_last_connection_fallback_keeps_all_load_and_physical_end(self):
  from shapely.geometry import LineString
  from vo_paden import geometry_checks
  records=[{'id':'first','code':'C','current_A':7.8,'tap':[100,0],'new_tap':[100,0]},{'id':'last','code':'C','current_A':7.8,'tap':[200,0],'new_tap':[200,0]}]
  d={'records':records,'new_codes':['C'],'retained':[],'feed':None,'profile':'laatste_helft','load_A':150}
  main=LineString([(0,0),(500,0)]);result=geometry_checks(d,main)
  self.assertFalse(result['physical']['passes']);self.assertTrue(result['last_connection']['passes']);self.assertEqual(result['selected_endpoint'],'last_connection');self.assertEqual(result['same_connection_ids'],['first','last']);self.assertEqual(main.length,500)

 def test_thin_branch_controls_full_direction(self):
  from shapely.geometry import LineString
  from vo_paden import geometry_checks
  d={'primary_code':'MAIN','new_codes':[],'feed':{'xy':[100,0],'position_m':50},'parent_child_positions':{'BRANCH':{'parent_position':60,'xy':[110,0]}},'retained':[{'code':'MAIN','type':'95Al','lo':0,'hi':100,'geometry':LineString([(50,0),(150,0)])},{'code':'BRANCH','type':'50Al','lo':0,'hi':100,'geometry':LineString([(110,0),(110,100)])}],'records':[{'id':'a','code':'MAIN','chain_position_m':55,'tap':[105,0]},{'id':'b','code':'BRANCH','chain_position_m':80,'tap':[110,80]}],'profile':'evenredig','load_A':120}
  result=geometry_checks(d,LineString([(0,0),(100,0)]));self.assertEqual(result['selected']['limiting']['max_fuse_A'],125);self.assertFalse(result['selected']['passes']);self.assertEqual(result['same_connection_ids'],['a','b'])

if __name__=='__main__':unittest.main()
