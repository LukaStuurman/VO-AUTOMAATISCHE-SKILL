import unittest

class MaterielePaden(unittest.TestCase):
 def test_two_materials_are_summed_over_actual_intervals(self):
  from vo_materialen import segments_between
  from reken_richtingen import calculate_path,CATALOGUE
  part={'type':'50Cu','material_segments':[{'lo':0,'hi':100,'type':'95Al'},{'lo':100,'hi':200,'type':'50Cu'}]}
  segments=segments_between(part,50,150);result=calculate_path({'id':'p','segments':segments},'evenredig',CATALOGUE)
  self.assertAlmostEqual(result['R_ohm'],.05*.320+.05*.387);self.assertEqual(result['length_m'],100)

 def test_thin_copper_branch_controls_direction(self):
  from reken_richtingen import calculate_path,CATALOGUE
  result=calculate_path({'id':'branch','segments':[{'id':'new','type':'150Al','length_m':50},{'id':'branch','type':'35Cu','length_m':50}]},'evenredig',CATALOGUE)
  self.assertEqual(result['max_fuse_A'],160);self.assertAlmostEqual(result['ampacity_A'],152.0127)

 def test_material_hole_is_rejected(self):
  from vo_materialen import segments_between
  with self.assertRaises(ValueError):segments_between({'type':'95Al','material_segments':[{'lo':0,'hi':50,'type':'95Al'},{'lo':60,'hi':100,'type':'50Cu'}]},0,100)

 def test_combi_function_distinguishes_same_code(self):
  from shapely.geometry import LineString
  from vo_materialen import material_intervals
  from reken_richtingen import CATALOGUE
  chain=LineString([(0,0),(100,0),(200,0)])
  features=[{'id':'LS','geometry':LineString([(0,0),(100,0)]).__geo_interface__,'properties':{'omschrijving':'functie LS'}},{'id':'COMBI','geometry':LineString([(100,0),(200,0)]).__geo_interface__,'properties':{'omschrijving':'functie LS/OV'}}]
  labels=[{'type':'95Al','combo':False,'xy':[50,5]},{'type':'50Cu','combo':True,'xy':[150,5]}]
  rows=material_intervals('SOURCE',chain,features,labels,CATALOGUE);self.assertEqual([(r['type'],r['combo']) for r in rows],[('95Al',False),('50Cu',True)])

 def test_only_the_retained_material_at_contact_controls_combi_label(self):
  from vo_materialen import contact_material
  part={'lo':0,'hi':100,'type':'50Cu','combo':True,'material_segments':[{'lo':0,'hi':100,'type':'95Al','combo':False},{'lo':100,'hi':200,'type':'50Cu','combo':True}]}
  self.assertEqual(contact_material(part,100),{'type':'95Al','combo':False})

if __name__=='__main__':unittest.main()
