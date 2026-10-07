import unittest

class GeplandeAansluitingen(unittest.TestCase):
 def fixture(self,old_type='150Al',load=7.8):
  from shapely.geometry import LineString
  old=LineString([(25,10),(100,10)]);feed=LineString([(0,0),(25,10)]);new=LineString([(0,0),(100,0)])
  rows=[{'id':'old','code':'OLD','tap':[50,10],'chain_position_m':25,'current_A':load,'kabel_opwek_A':0},{'id':'new','code':'NEW','tap':[60,0],'new_tap':[60,0],'current_A':7.8,'kabel_opwek_A':0},{'id':'planned','code':None,'xy':[75,11],'tap':[75,11],'current_A':4.6,'kabel_opwek_A':0,'planned_connection':True}]
  directions=[{'id':'R2','primary_code':'NEW','new_codes':['NEW'],'new_paths':[new],'display_main':new,'feed':None,'retained':[],'records':[rows[1]],'load_A':7.8,'profile':'laatste_helft'},{'id':'R3','primary_code':'OLD','new_codes':[],'new_paths':[feed],'display_main':feed,'feed':{'xy':[25,10],'position_m':0},'retained':[{'code':'OLD','type':old_type,'lo':0,'hi':75,'geometry':old}],'records':[rows[0]],'parent_child_positions':{},'load_A':load,'profile':'laatste_helft'}]
  return rows,directions,{'OLD':old}

 def test_nearby_retained_main_is_considered_without_fake_wfs_or_overzetter(self):
  from vo_geplande_aansluitingen import assign_planned
  rows,directions,chains=self.fixture();log=assign_planned(rows,directions,chains);planned=rows[-1]
  self.assertEqual(planned['code'],'OLD');self.assertEqual(planned['direction'],'R3');self.assertFalse(planned['overzetter']);self.assertTrue(planned['planned_connection']);self.assertFalse(log[0]['wfs_service_created']);self.assertEqual(planned['xy'],[75,11]);self.assertAlmostEqual(planned['planned_contact_distance_m'],1);self.assertEqual(sum(len(d['records']) for d in directions),3)

 def test_closest_retained_main_is_rejected_when_added_load_does_not_fit(self):
  from vo_geplande_aansluitingen import assign_planned
  rows,directions,chains=self.fixture('50Al',110);assign_planned(rows,directions,chains)
  self.assertEqual(rows[-1]['direction'],'R2');self.assertTrue(rows[-1]['overzetter']);self.assertIsNone(rows[-1]['code'])

if __name__=='__main__':unittest.main()
