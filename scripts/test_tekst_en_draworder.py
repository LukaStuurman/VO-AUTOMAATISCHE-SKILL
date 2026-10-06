import io,unittest

class TekstEnTekenvolgorde(unittest.TestCase):
 def setup_cad(self):
  import ezdxf
  doc=ezdxf.new();doc.blocks.new('NIEUWE MOF').add_circle((0,0),.5)
  return doc,{'drawing':{'new_entity_handles':[],'symbol_types':{}},'directions':[],'connections':[]}

 def label(self,doc,data,layer,text,xy):
  e=doc.modelspace().add_text(text,dxfattribs={'layer':layer,'height':.7,'insert':xy})
  data['drawing']['new_entity_handles'].append(e.dxf.handle);return e

 def test_bent_cable_label_follows_local_segment_not_endpoint_chord(self):
  from vo_tekst_en_draworder import apply_text_layout,validate_text_layout
  doc,data=self.setup_cad();doc.modelspace().add_lwpolyline([(0,0),(20,0),(20,30)],dxfattribs={'layer':'Aansluiting LS K03'})
  text=self.label(doc,data,'Aansluiting LS K03','150Al / ????-00',(20,12))
  apply_text_layout(doc,data);self.assertAlmostEqual(abs(text.dxf.rotation),90);self.assertEqual(validate_text_layout(doc,data),[])

 def test_bundle_labels_keep_geometric_lane_order_and_clear_spacing(self):
  from vo_tekst_en_draworder import apply_text_layout,validate_text_layout
  doc,data=self.setup_cad();handles=[]
  for layer,y in [('Aansluiting LS K04',0),('Aansluiting LS K05',.2)]:
   doc.modelspace().add_lwpolyline([(0,y),(60,y)],dxfattribs={'layer':layer});handles.append(self.label(doc,data,layer,'150Al / ????-00',(25,1)).dxf.handle)
  apply_text_layout(doc,data);self.assertEqual(data['cable_text_stacks'][0]['handles_in_cable_order'],handles)
  self.assertGreaterEqual(doc.entitydb[handles[1]].dxf.insert.y-doc.entitydb[handles[0]].dxf.insert.y,1.5-1e-6);self.assertEqual(validate_text_layout(doc,data),[])

 def test_nearly_parallel_cables_still_receive_one_text_stack(self):
  from vo_tekst_en_draworder import apply_text_layout,validate_text_layout
  doc,data=self.setup_cad()
  for layer,start,end in [('Aansluiting LS K04',(0,0),(100,-100)),('Aansluiting LS K05',(.14,.14),(100.14,-99.76))]:
   doc.modelspace().add_lwpolyline([start,end],dxfattribs={'layer':layer});self.label(doc,data,layer,'150Al / ????-00',(50,-49))
  apply_text_layout(doc,data);self.assertEqual(len(data['cable_text_stacks']),1);self.assertEqual(validate_text_layout(doc,data),[])

 def test_left_hand_bestaand_text_is_linked_by_visible_edge_and_actual_mof(self):
  from vo_tekst_en_draworder import mof_label_matches
  doc,data=self.setup_cad();mof=doc.modelspace().add_blockref('NIEUWE MOF',(0,0));e=self.label(doc,data,'0','Bestaand',(-3.4,.3));data['text_layout']=[{'handle':e.dxf.handle,'kind':'mof','mof_handle':mof.dxf.handle}]
  self.assertTrue(mof_label_matches(doc,data,e,(0,0)));self.assertFalse(mof_label_matches(doc,data,e,(5,0)))

 def test_mof_text_is_clear_and_redraw_order_survives_serialization(self):
  import ezdxf
  from vo_tekst_en_draworder import apply_text_layout,validate_text_layout,text_footprint
  from shapely.geometry import LineString
  doc,data=self.setup_cad();mof=doc.modelspace().add_blockref('NIEUWE MOF',(0,0),dxfattribs={'layer':'Aansluiting LS K01'});data['drawing']['symbol_types'][mof.dxf.handle]='NIEUWE MOF'
  cable=doc.modelspace().add_lwpolyline([(-5,0),(20,0)],dxfattribs={'layer':'Aansluiting LS K01'});points=cable.get_points();text=self.label(doc,data,'Aansluiting LS K01','EM',(0,.05))
  apply_text_layout(doc,data);self.assertFalse(text_footprint(text).intersects(LineString([(-5,0),(20,0)])));self.assertEqual(cable.get_points(),points)
  stream=io.StringIO();doc.write(stream);stream.seek(0);saved=ezdxf.read(stream);self.assertEqual(list(saved.modelspace().entities_in_redraw_order())[-1].dxf.handle,mof.dxf.handle);self.assertEqual(validate_text_layout(saved,data),[])

 def test_xref_definition_and_insert_are_preserved(self):
  from vo_tekst_en_draworder import moffen_to_front
  doc,data=self.setup_cad();doc.add_xref_def('original.dwg','KLIC');ref=doc.blocks.get('KLIC');insert=doc.modelspace().add_blockref('KLIC',(10,20));before=(ref.block.dxfattribs(),insert.dxfattribs());doc.modelspace().add_blockref('NIEUWE MOF',(0,0))
  moffen_to_front(doc,data);self.assertEqual(before,(ref.block.dxfattribs(),insert.dxfattribs()))

 def test_saved_validation_rejects_text_moved_onto_wire(self):
  from vo_tekst_en_draworder import apply_text_layout,validate_text_layout
  doc,data=self.setup_cad();doc.modelspace().add_lwpolyline([(0,0),(60,0)],dxfattribs={'layer':'Aansluiting LS K04'});e=self.label(doc,data,'Aansluiting LS K04','150Al / ????-00',(25,1));apply_text_layout(doc,data);e.dxf.insert=(25,0,0)
  self.assertTrue(any(r['reason']=='Tekst overlapt kabelpolyline' for r in validate_text_layout(doc,data)))

if __name__=='__main__':unittest.main()
