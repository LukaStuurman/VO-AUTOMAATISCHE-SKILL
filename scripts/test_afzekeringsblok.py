import io,unittest

class Afzekeringsblok(unittest.TestCase):
 def setup_cad(self):
  import ezdxf
  doc=ezdxf.new();block=doc.blocks.new('RT template');ref=doc.modelspace().add_blockref(block.name,(10,20));used=[1,2,3,4,5,9,10,11,12]
  for n in range(1,13):
   layer=f'Aansluiting LS K{n:02}';block.add_circle((n*.03,n*1.25),.5,dxfattribs={'layer':layer});text=f'RT {n:02}: '+('80A Tamp / / 150Al EXTRA LONG TEXT' if n==12 else '250A / / 150Al' if n in used else '')
   ref.add_attrib(f'RT_{n:02}:',text,(12,20+n*1.25),dxfattribs={'layer':layer,'height':1})
  return doc,{'drawing':{'symbol_types':{ref.dxf.handle:'RT 1-12'}}},block,used

 def test_exact_vertical_alignment_pluses_and_original_template_preserved(self):
  from vo_afzekeringsblok import apply_fuse_legend,validate_fuse_legend
  doc,data,original,used=self.setup_cad();before=[e.dxfattribs() for e in original];apply_fuse_legend(doc,data);self.assertEqual(data['fuse_legend_layout']['used_slots'],used);self.assertEqual([e.dxfattribs() for e in original],before);self.assertEqual(validate_fuse_legend(doc,data),[])

 def test_wipeout_covers_longest_attribute_after_save(self):
  import ezdxf
  from vo_afzekeringsblok import apply_fuse_legend,validate_fuse_legend
  doc,data,_,_=self.setup_cad();apply_fuse_legend(doc,data);stream=io.StringIO();doc.write(stream);stream.seek(0);saved=ezdxf.read(stream);self.assertEqual(validate_fuse_legend(saved,data),[]);self.assertGreater(data['fuse_legend_layout']['wipeout_world_bounds'][2],25)

 def test_missing_plus_is_reported(self):
  from vo_afzekeringsblok import apply_fuse_legend,validate_fuse_legend
  doc,data,_,_=self.setup_cad();apply_fuse_legend(doc,data);row=data['fuse_legend_layout'];block=doc.blocks.get(row['block']);block.delete_entity(doc.entitydb[row['plus_handles']['2'][0]]);self.assertTrue(any(r.get('slot')==2 for r in validate_fuse_legend(doc,data)))

 def test_all_plus_endpoints_reach_circle_edge_and_short_plus_fails(self):
  from vo_afzekeringsblok import apply_fuse_legend,validate_fuse_legend
  doc,data,_,_=self.setup_cad();apply_fuse_legend(doc,data);row=data['fuse_legend_layout'];block=doc.blocks.get(row['block']);circle=next(e for e in block.query('CIRCLE') if e.dxf.layer=='Aansluiting LS K02');line=doc.entitydb[row['plus_handles']['2'][0]]
  self.assertAlmostEqual(line.dxf.start.distance(circle.dxf.center),circle.dxf.radius);self.assertAlmostEqual(line.dxf.end.distance(circle.dxf.center),circle.dxf.radius)
  line.dxf.start=circle.dxf.center+(line.dxf.start-circle.dxf.center)*.8;self.assertTrue(any(r.get('slot')==2 and 'cirkelrand' in r['reason'] for r in validate_fuse_legend(doc,data)))

if __name__=='__main__':unittest.main()
