import unittest,tempfile
from pathlib import Path

class KabelAfwerking(unittest.TestCase):
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
