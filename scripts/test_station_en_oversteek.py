import unittest

class StationEnOversteek(unittest.TestCase):
 def test_outside_in_allocation_keeps_tamp_slots_reserved(self):
  from vo_stationsuitloop import allocation_order
  self.assertEqual(allocation_order({'direction_slots':list(range(2,12))}),[2,11,3,10,4,9,5,8,6,7])

 def test_departures_are_normal_to_front_and_tamps_are_five_metres(self):
  import ezdxf,math
  from shapely.geometry import LineString,shape
  from vo_stationsuitloop import build_station_exit
  doc=ezdxf.new();body=doc.blocks.new('Station');body.add_lwpolyline([(-2,0),(2,0),(2,2),(-2,2)],close=True);station=doc.modelspace().add_blockref('Station',(0,0));base=LineString([(0,1),(2,-3),(6,-3),(100,-3)]);numbers=[2,3,4,5,9,10,11];data={'directions':[{'id':'R'+str(n),'display_main':base.offset_curve((i-3)*.2,join_style=2).__geo_interface__} for i,n in enumerate(numbers)],'config':{'station_handle':station.dxf.handle,'direction_slots':list(range(2,12)),'rules':{'lane_pitch_m':.2}}}
  lines=build_station_exit(data,doc);frame=data['station_exit_layout']
  for name,row in frame['active_ports'].items():
   a,b=lines[name].coords[:2];self.assertAlmostEqual(a[0],(row['slot']-6.5)*.2,places=6);self.assertAlmostEqual(a[1],0,places=6);self.assertAlmostEqual(b[0],a[0],places=6);self.assertLess(b[1],a[1]-.5)
  self.assertEqual([r['id'] for r in data['station_tamps']],['R1','R12']);self.assertTrue(all(abs(shape(r['geometry']).length-5)<.000001 for r in data['station_tamps']))

 def test_nearby_crossings_merge_into_one_parallel_crossing(self):
  from shapely.geometry import LineString,Polygon,box,shape
  from vo_gedeelde_oversteek import merge_nearby_crossings
  old=LineString([(0,6),(0,-2),(-10,-2),(-10,-10)]);reference=LineString([(10,6),(10,-2),(20,-2),(20,-10)]);lines={'R2':old,'R3':old.offset_curve(.2,join_style=2),'R4':reference,'R5':reference.offset_curve(.2,join_style=2)};data={'directions':[{'id':n} for n in lines],'crossing_sites':[{'id':'left','xy':[.1,1],'road_axis':[1,0],'lane_centres':{'R2':[0,1],'R3':[.2,1]}},{'id':'right','xy':[10.1,1],'road_axis':[1,0],'lane_centres':{'R4':[10,1],'R5':[10.2,1]}}]}
  road=box(-5,0,25,2);result,changes=merge_nearby_crossings(data,lines,road,Polygon(),box(-20,-20,30,20),box(-20,-20,30,20));self.assertEqual(len(changes),1);self.assertEqual(len(data['crossing_sites']),1);self.assertEqual(len(data['crossing_sites'][0]['lane_centres']),4)
  positions=sorted(g.intersection(road).interpolate(.5,normalized=True).x for g in result.values());self.assertTrue(all(abs(positions[i+1]-positions[i]-.2)<.000001 for i in range(3)))

if __name__=='__main__':unittest.main()
