import unittest

class Herverdeling(unittest.TestCase):
 def test_existing_services_keep_their_wire_and_are_assigned_once(self):
  from shapely.geometry import LineString,box
  from vo_herverdeel_bestaand import redistribute_at_crossings
  chain=LineString([(0,0),(100,0)])
  def direction(name,lo,hi,root,positions):
   from shapely.ops import substring
   records=[{'id':name+str(i),'code':'MAIN','chain_position_m':p,'current_A':10,'direction':name} for i,p in enumerate(positions)]
   return {'id':name,'primary_code':'MAIN','new_codes':[],'profile':'laatste_helft','load_A':len(records)*10,'records':records,'parent_child_positions':{},'feed':{'position_m':root,'xy':[root,0]},'display_main':LineString([(root,20),(root,0)]).__geo_interface__,'retained':[{'code':'MAIN','type':'95Al','lo':lo,'hi':hi,'geometry':substring(chain,lo,hi).__geo_interface__}]}
  a=direction('R2',20,100,90,[25,30,60,70]);b=direction('R3',0,15,10,[5]);data={'directions':[a,b],'connections':[dict(r) for d in [a,b] for r in d['records']],'config':{'rules':{'joint_separation_m':2}},'checks':{'new_retained_intersections':[{'new_direction':'R5','retained_direction':'R2','code':'MAIN','geometry':{'type':'Point','coordinates':[40,0]}},{'new_direction':'R6','retained_direction':'R2','code':'MAIN','geometry':{'type':'Point','coordinates':[42,0]}}]}}
  redistribute_at_crossings(data,{'groups':{'MAIN':{'geometry':chain,'outside_taps':[]}}})
  self.assertEqual(len(a['records']),2);self.assertEqual(len(b['records']),3);self.assertEqual(len({r['id'] for d in data['directions'] for r in d['records']}),5);self.assertEqual(a['retained'][0]['lo'],43);self.assertEqual(b['retained'][0]['hi'],39);self.assertFalse(any(r.get('new_connection') for d in data['directions'] for r in d['records']))

 def test_door_geometry_controls_front_when_route_points_behind_station(self):
  import ezdxf
  from shapely.geometry import LineString
  from vo_stationsuitloop import station_frame
  doc=ezdxf.new();b=doc.blocks.new('Station');b.add_lwpolyline([(-2,0),(2,0),(2,2),(-2,2)],close=True);b.add_arc((-1,2),1,0,90);b.add_arc((1,2),1,90,180);s=doc.modelspace().add_blockref('Station',(0,0))
  f=station_frame(s,{'R2':LineString([(0,1),(0,-10)])});self.assertAlmostEqual(f['front_center'][1],2);self.assertGreater(f['outward_axis'][1],.99)

if __name__=='__main__':unittest.main()
