import unittest, tempfile, json, hashlib
from pathlib import Path
from shapely.geometry import LineString,box
from vo_harde_voorwaarden import short_reuse,retained_outside,bgt_coverage
from vo_aansluitbereik import intervening_directions

class PhysicalConditions(unittest.TestCase):
 def direction(self,length,count):
  return {'id':'R2','primary_code':'A','new_codes':[],'retained':[{'code':'A','lo':0,'hi':length,'geometry':LineString([(0,0),(length,0)]).__geo_interface__}],'records':[{'id':str(i),'code':'A','chain_position_m':i} for i in range(count)]}
 def test_short_sparse_retained_is_replacement_candidate(self):
  self.assertEqual(len(short_reuse([self.direction(24.9,4)])),1)
  self.assertFalse(short_reuse([self.direction(25,4)]))
  self.assertFalse(short_reuse([self.direction(24.9,6)]))
 def test_counts_actual_downstream_not_entire_source_code(self):
  d=self.direction(20,3);d['records'].append({'id':'elsewhere','code':'A','chain_position_m':100})
  self.assertEqual(short_reuse([d])[0]['connections'],3)
  d['retained'].append({'code':'B','lo':0,'hi':30,'geometry':LineString([(10,0),(10,30)]).__geo_interface__});d['parent_child_positions']={'B':{'parent_position':10}};d['records'] += [{'id':'branch'+str(i),'code':'B','chain_position_m':i} for i in range(3)]
  self.assertFalse(short_reuse([d]))
 def test_connected_old_loop_outside_with_inside_endpoints_fails(self):
  d=self.direction(10,2);d['retained'][0]['geometry']=LineString([(1,1),(12,1),(12,9),(1,9)]).__geo_interface__
  self.assertGreater(retained_outside([d],box(0,0,10,10))[0]['length_m'],10)
 def test_house_must_not_cross_nearer_main(self):
  a={'id':'R2','new_codes':['A'],'retained':[],'records':[{'id':'house','code':'A','xy':[0,0]}]};b={'id':'R3','new_codes':['B'],'retained':[],'records':[]}
  lines={'R2':LineString([(3,-5),(3,5)]),'R3':LineString([(1,-5),(1,5)])}
  self.assertEqual(intervening_directions([a,b],lines)[0]['nearest_accessible_direction'],'R3')
  b['records']=a['records'];a['records']=[];b['new_codes']=['A'];self.assertFalse(intervening_directions([a,b],lines))
 def test_short_replacement_changes_main_and_preserves_source_records(self):
  from vo_kort_hergebruik import replace_short_primary
  class Router:
   def path(self,p):return LineString([(-5,0),p])
   def between(self,a,b):return LineString([a,b])
  d=self.direction(20,3);d.pop('id');d['feed']={'xy':[0,0]}
  for r in d['records']:r['tap']=[r['chain_position_m'],0]
  ids=[r['id'] for r in d['records']]
  self.assertTrue(replace_short_primary(d,Router()));self.assertFalse(d['retained']);self.assertIsNone(d['feed']);self.assertEqual(d['new_codes'],['A']);self.assertEqual(ids,[r['id'] for r in d['records']]);self.assertTrue(all('new_tap' in r for r in d['records']))
 def test_source_extent_and_pagination_are_required(self):
  with tempfile.TemporaryDirectory() as tmp:
   p=Path(tmp);source=p/'road.geojson';source.write_text('{}');register=p/'register.json';row={'bbox_RD':[0,0,5,5],'pagination_complete':True,'sha256':hashlib.sha256(source.read_bytes()).hexdigest()};register.write_text(json.dumps({'sources':{'wegdeel':row}}));cfg={'bgt':{'wegdeel':str(source)},'bgt_source_register':str(register)}
   self.assertTrue(bgt_coverage(cfg,box(0,0,10,10)));self.assertFalse(bgt_coverage(cfg,box(1,1,4,4)))
   row['pagination_complete']=False;register.write_text(json.dumps({'sources':{'wegdeel':row}}));self.assertTrue(bgt_coverage(cfg,box(1,1,4,4)))
 def test_topo_house_is_obstacle_but_annotation_frame_is_not(self):
  import ezdxf
  from vo_topografie import topography_obstacles
  with tempfile.TemporaryDirectory() as tmp:
   doc=ezdxf.new();m=doc.modelspace();m.add_lwpolyline([(0,0),(5,0),(5,5),(0,5)],close=True);m.add_text('12',dxfattribs={'insert':(2,2),'height':1});m.add_lwpolyline([(10,0),(15,0),(15,5),(10,5)],close=True);m.add_text('LS - 001518 (verwijderen)',dxfattribs={'insert':(12,2),'height':1});file=Path(tmp)/'topo.dxf';doc.saveas(file)
   obstacles=topography_obstacles({'topo_dxf':str(file)},box(-1,-1,16,6))
   self.assertTrue(obstacles['buildings'].covers(box(1,1,4,4)));self.assertFalse(obstacles['buildings'].intersects(box(11,1,14,4)))
 def test_bgt_fetch_follows_all_pages_and_records_source_hash(self):
  import io
  from haal_bgt import fetch_collection
  pages=[{'type':'FeatureCollection','features':[{'id':'one'}],'links':[{'rel':'next','href':'?cursor=2'}]},{'type':'FeatureCollection','features':[{'id':'two'}],'links':[]}]
  def read_page(request,timeout):return io.StringIO(json.dumps(pages.pop(0)))
  with tempfile.TemporaryDirectory() as tmp:
   row=fetch_collection('pand',[0,0,20,20],tmp,read_page)
   self.assertEqual(row['count'],2);self.assertEqual(len(row['pages']),2);self.assertTrue(row['pagination_complete']);self.assertEqual(row['sha256'],hashlib.sha256(Path(row['file']).read_bytes()).hexdigest())

if __name__=='__main__':unittest.main()
