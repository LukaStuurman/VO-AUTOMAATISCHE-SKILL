import unittest,tempfile,json
from pathlib import Path

class MofEnStraat(unittest.TestCase):
 def test_a_splice_is_placed_on_both_actual_cables(self):
  from shapely.geometry import LineString,Point,shape
  from vo_mofverbindingen import align_splice_contacts
  old=LineString([(0,0),(100,0)]);line=LineString([(10,-20),(10,20)]);d={'id':'R1','primary_code':'MAIN','new_codes':['BRANCH'],'feed':{'xy':[11,0],'position_m':11},'retained':[{'code':'MAIN','lo':11,'hi':90,'geometry':LineString([(11,0),(90,0)]).__geo_interface__}],'records':[{'code':'MAIN','chain_position_m':80}],'parent_child_positions':{}}
  align_splice_contacts([d],{'R1':line},{'MAIN':old});p=Point(d['feed']['xy'])
  self.assertEqual(d['feed']['xy'],[10,0]);self.assertEqual(d['splice_kind'],'AM');self.assertEqual(line.distance(p),0);self.assertEqual(shape(d['retained'][0]['geometry']).distance(p),0)

 def test_vm_removes_the_unserved_arm_and_keeps_all_connections(self):
  from shapely.geometry import LineString,shape
  from vo_mofverbindingen import align_splice_contacts
  old=LineString([(0,0),(100,0)]);d={'id':'R1','primary_code':'MAIN','new_codes':[],'feed':{'xy':[20,0],'position_m':20},'retained':[{'code':'MAIN','lo':0,'hi':100,'geometry':old.__geo_interface__}],'records':[{'id':'a','code':'MAIN','chain_position_m':60}],'parent_child_positions':{}}
  align_splice_contacts([d],{'R1':LineString([(20,-20),(20,0)])},{'MAIN':old})
  self.assertEqual(d['splice_kind'],'VM');self.assertEqual(d['retained'][0]['lo'],20);self.assertEqual(shape(d['retained'][0]['geometry']).length,80);self.assertEqual(d['records'][0]['id'],'a')

 def test_a_real_existing_branch_requires_matching_source_evidence(self):
  from vo_mofverbindingen import existing_branch_evidence
  joints=[{'xy':[10,0],'handle':'real'}]
  self.assertIsNotNone(existing_branch_evidence([10,0],joints));self.assertIsNone(existing_branch_evidence([11,0],joints))

 def test_a_shared_frontage_is_straightened_as_one_bundle(self):
  from shapely.geometry import LineString,Point,Polygon,box
  from vo_rechte_straat import straighten_street_bundle
  from shapely.affinity import translate
  center=LineString([(0,0),(10,0),(20,.7),(30,.7),(40,0),(50,0),(60,0)]);lines={'A':translate(center,yoff=-.2),'B':center,'C':translate(center,yoff=.2)};tree=Point(30,2)
  result,change=straighten_street_bundle(lines,['A','B','C'],tree.buffer(.5),box(-5,-2,70,3),Polygon(),box(-10,-3,80,4),tree_points=[tree])
  self.assertIsNotNone(change);self.assertEqual(change['new_vertices'],2);self.assertGreater(change['straight_length_m'],45);self.assertTrue(all(g.intersection(tree.buffer(.5)).is_empty for g in result.values()))

 def test_klic_copy_removes_only_matching_local_main_piece(self):
  import ezdxf
  from shapely.geometry import LineString
  from vo_klic_weergave import make_clipped_klic_view
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);doc=ezdxf.new();doc.layers.new('E_LV_MAP_CABLE_LS');main=doc.modelspace().add_lwpolyline([(0,0),(20,0),(20,30)],dxfattribs={'layer':'E_LV_MAP_CABLE_LS'});other=doc.modelspace().add_lwpolyline([(5,-5),(5,5)],dxfattribs={'layer':'E_LV_MAP_CABLE_LS'});source=p/'source.dxf';doc.saveas(source)
   original=LineString([(0,0),(100,0)]);data={'config':{'klic_dxf':str(source)},'existing_chains':{'MAIN':original.__geo_interface__},'directions':[{'id':'R1','primary_code':'MAIN','feed':{'xy':[10,0]},'splice_kind':'VM','retained':[{'code':'MAIN','lo':10,'hi':100,'geometry':LineString([(10,0),(100,0)]).__geo_interface__}],'records':[{'code':'MAIN','chain_position_m':50}]}]};before={'R1':[{'code':'MAIN','lo':0,'hi':100,'geometry':original.__geo_interface__}]}
   view,_=make_clipped_klic_view(data,before,p/'view');new=ezdxf.readfile(view);lines=[LineString(e.get_points('xy')) for e in new.modelspace().query('LWPOLYLINE')];self.assertTrue(any(g.equals(LineString([(10,0),(20,0),(20,30)])) for g in lines));self.assertTrue(any(g.equals(LineString([(5,-5),(5,5)])) for g in lines));self.assertEqual(len(ezdxf.readfile(source).modelspace()),2)

if __name__=='__main__':unittest.main()
