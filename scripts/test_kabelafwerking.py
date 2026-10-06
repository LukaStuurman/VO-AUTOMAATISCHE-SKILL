import unittest,tempfile
from pathlib import Path

class KabelAfwerking(unittest.TestCase):
 def test_shared_corner_uses_one_exact_cad_offset(self):
  from shapely.geometry import LineString,Polygon,box,Point,shape
  from vo_gedeelde_offsets import shared_offsets
  axis=LineString([(0,0),(60,0),(60,30)]);bow=LineString([(0,.2),(30,.2),(31,.35),(59.8,.2),(59.8,20)]);directions=[{'id':'A','feed':None},{'id':'B','feed':None}]
  lines,log=shared_offsets({'A':axis,'B':bow},directions,Polygon(),box(-5,-5,80,40))
  self.assertTrue(log);self.assertAlmostEqual(lines['B'].distance(Point(40,0)),.2,places=6)
  expected=axis.offset_curve(.2,join_style=2,mitre_limit=10)
  self.assertTrue(all(shape(row['geometry']).difference(expected.buffer(.000001)).length<.00001 for row in log))

 def test_clamped_tap_does_not_hide_unserved_last_house(self):
  from shapely.geometry import LineString
  from vo_kabelafwerking import extend_past_last_connection
  d={'id':'R1','new_codes':['MAIN'],'records':[{'id':'house','code':'MAIN','tap':[25,2],'new_tap':[20,0]}]};g,log=extend_past_last_connection(d,LineString([(0,0),(20,0)]),.6)
  self.assertAlmostEqual(g.coords[-1][0],25.6);self.assertEqual(log['last_connection_ids'],['house'])

 def test_new_end_and_text_use_the_direction_layer(self):
  from vo_kabelafwerking import draw_supplemental
  calls=[];data={'supplemental_mof_work':[{'kind':'neighbour_cut_end','xy':[10,0],'code':'LBK1234-00','layer':'R10'}]}
  draw_supplemental(data,lambda n,p,l:calls.append((n,l)),lambda t,p,l:calls.append((t,l)),lambda g,l:None)
  self.assertEqual(calls,[('NIEUWE MOF','R10'),('EM (was 1234-00)','R10')])

 def test_external_reference_is_restored_without_modifying_its_contents(self):
  import ezdxf
  from vo_kabelafwerking import restore_source_xrefs,apply_cable_style
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);external=p/'original.dxf';ext=ezdxf.new();ext.modelspace().add_lwpolyline([(0,0),(10,0)],dxfattribs={'const_width':0});ext.saveas(external);before=external.read_bytes();base=ezdxf.new();base.blocks.new('KLIC',dxfattribs={'flags':4,'xref_path':str(external)});source=p/'base.dxf';base.saveas(source);doc=ezdxf.readfile(source);doc.blocks.get('KLIC').block.dxf.xref_path='modified.dwg';data={'config':{'base_dxf':str(source),'klic_display_dxf':'modified.dxf'}}
   restore_source_xrefs(doc,data);apply_cable_style(doc);self.assertEqual(doc.blocks.get('KLIC').block.dxf.xref_path,str(external));self.assertEqual(external.read_bytes(),before);self.assertNotIn('klic_display_dxf',data['config'])
 def test_cable_style_preserves_boundary_and_geometry(self):
  import ezdxf
  from vo_kabelafwerking import apply_cable_style
  doc=ezdxf.new();old=doc.modelspace().add_lwpolyline([(0,0),(10,0)],dxfattribs={'layer':'01 - Bestaande kabel'});new=doc.modelspace().add_lwpolyline([(0,1),(10,1)],dxfattribs={'layer':'K01 - Nieuwe kabel'});boundary=doc.modelspace().add_lwpolyline([(0,2),(10,2)],dxfattribs={'layer':'01 - Stationsgebied','const_width':.7})
  apply_cable_style(doc,new_layers=[new.dxf.layer]);self.assertEqual(old.dxf.const_width,.1);self.assertEqual(new.dxf.const_width,.1);self.assertEqual(new.dxf.linetype,'DASHED');self.assertEqual(new.dxf.ltscale,.0035);self.assertEqual(boundary.dxf.const_width,.7);self.assertEqual(old.get_points('xy'),[(0,0),(10,0)])

 def test_prior_project_cut_does_not_resurrect_in_revision(self):
  import ezdxf
  from shapely.geometry import LineString
  from vo_klic_weergave import make_clipped_klic_view
  with tempfile.TemporaryDirectory() as folder:
   p=Path(folder);doc=ezdxf.new();doc.layers.new('E_LV_MAP_CABLE_LS');doc.modelspace().add_lwpolyline([(0,0),(30,0)],dxfattribs={'layer':'E_LV_MAP_CABLE_LS'});source=p/'source.dxf';doc.saveas(source)
   main=LineString([(0,0),(30,0)]);used=LineString([(10,0),(30,0)]);data={'config':{'klic_dxf':str(source)},'existing_chains':{'MAIN':main.__geo_interface__},'directions':[],'klic_display_removals':[{'code':'MAIN','geometry':LineString([(0,0),(10,0)]).__geo_interface__,'protected_used_geometry':used.__geo_interface__}]}
   view,_=make_clipped_klic_view(data,{},p/'first');a=ezdxf.readfile(view).modelspace().query('LWPOLYLINE')[0];self.assertEqual(a.get_points('xy'),[(10,0),(30,0)])
   view,_=make_clipped_klic_view(data,{},p/'second');b=ezdxf.readfile(view).modelspace().query('LWPOLYLINE')[0];self.assertEqual(b.get_points('xy'),a.get_points('xy'));self.assertEqual(ezdxf.readfile(source).modelspace().query('LWPOLYLINE')[0].get_points('xy'),[(0,0),(30,0)])

 def test_branch_cap_is_blocked_if_other_direction_uses_branch(self):
  import ezdxf
  from shapely.geometry import LineString
  from vo_kabelafwerking import supplemental_work
  main=LineString([(0,0),(20,0)]);branch=LineString([(10,0),(10,10)])
  data={'existing_chains':{'MAIN':main.__geo_interface__,'BRANCH':branch.__geo_interface__},'connections':[{'code':'BRANCH','overzetter':True}], 'directions':[{'id':'R1','primary_code':'MAIN','new_codes':['BRANCH'],'parent_child_positions':{'BRANCH':{'xy':[10,0]}},'retained':[{'code':'MAIN','geometry':main.__geo_interface__}]},{'id':'R2','new_codes':[],'retained':[{'code':'BRANCH','geometry':branch.__geo_interface__}]}]}
  with self.assertRaisesRegex(ValueError,'andere richting'):supplemental_work(data,[{'kind':'branch','xy':[10,0]}],ezdxf.new())

if __name__=='__main__':unittest.main()
