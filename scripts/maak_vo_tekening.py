"""Teken een expliciet VO-projectplan op de oorspronkelijke DXF met een goedgekeurde stijl-/plaatsingsreferentie.

Dit is een referentiegestuurde assembler, geen zelfstandig ontwerpalgoritme.
Benodigd: ezdxf en shapely. De ontwerpbeslissingen staan traceerbaar in het projectplan.
"""
import argparse,json,math,re,sys,hashlib,collections,csv
from pathlib import Path

def main():
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument('plan',type=Path);parser.add_argument('--workspace',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
 args=parser.parse_args();workspace=args.workspace.resolve()
 # Task-local CAD dependencies may be supplied by the workspace.
 if (workspace/'.analysis/deps').is_dir():sys.path.insert(0,str(workspace/'.analysis/deps'))
 import ezdxf
 from ezdxf import bbox
 from ezdxf.lldxf.tagwriter import TagCollector
 from shapely.geometry import Polygon,box,LineString
 from reken_richtingen import calculate_station
 plan=json.loads(args.plan.read_text(encoding='utf8'));original_path=workspace/plan['original_dxf'];reference_path=workspace/plan['approved_reference_dxf']
 original_hash=hashlib.sha256(original_path.read_bytes()).hexdigest();reference_hash=hashlib.sha256(reference_path.read_bytes()).hexdigest()
 doc=ezdxf.readfile(original_path);ref=ezdxf.readfile(reference_path);msp=doc.modelspace();source={e.dxf.handle:e for e in ref.modelspace()};baseline={e.dxf.handle:e for e in msp}
 region=Polygon(doc.entitydb[plan['boundary_handle']].get_points('xy'));scope=region.buffer(4)
 calculation=calculate_station(plan['calculation']['station'])
 if not calculation['all_directions_pass'] or not calculation['trafo_passes']:raise ValueError('Het ingevoerde ontwerp voldoet niet aan de rekencontrole.')
 assert len(plan['connections'])==len({r['id'] for r in plan['connections']})
 for d in calculation['directions']:
  rs=[r for r in plan['connections'] if r['direction']==d['id']]
  assert math.isclose(sum(r['kabel_verbruik_A'] for r in rs),d['verbruik_A'])
 route_by_handle={r['source_route_handle']:r for r in plan['routes']}
 def in_scope(e):
  try:
   b=bbox.extents([e]);return b.has_data and box(b.extmin.x,b.extmin.y,b.extmax.x,b.extmax.y).intersects(scope)
  except Exception:return False
 def signature(e):
  ignored={5,105,330,331,340,350,360}
  return [(t.code,str(t.value)) for t in TagCollector.dxftags(e) if t.code not in ignored and t.code<1000]
 selected=[];modified=[];deleted=[]
 for h,e in source.items():
  old=baseline.get(h)
  if old is None:
   if in_scope(e):selected.append((h,e,'added'))
  elif signature(old)!=signature(e) and (in_scope(e) or in_scope(old)):
   selected.append((h,e,'updated'));modified.append(h)
 for h,e in baseline.items():
  if h not in source and in_scope(e):msp.delete_entity(e);deleted.append(h)
 added=[];mapping={};copied_annotations=[]
 for h,e,action in selected:
  if action=='updated':msp.delete_entity(baseline[h])
  if h in route_by_handle:
   r=route_by_handle[h]
   new=msp.add_lwpolyline(r['points'],dxfattribs={'layer':r['layer'],'color':256,'const_width':0,'linetype':'BYLAYER'})
   r['output_handle']=new.dxf.handle
  else:
   # Reuse approved annotation anchors and established symbols; not the entire reference file.
   new=e.copy();msp.add_entity(new);copied_annotations.append(h)
  if action=='updated':
   # New handles for substituted entities are recorded; original references remain in the source file.
   mapping[h]=new.dxf.handle
  added.append(new)
 # Recompute result text instead of copying old electrical results.
 checks={d['id']:d for d in calculation['directions']}
 def dec(n,digits):return f'{n:.{digits}f}'.replace('.',',')
 for e in added:
  if e.dxftype()=='TEXT' and e.dxf.layer.startswith('Aansluiting LS K'):
   key='R'+str(int(e.dxf.layer[-2:]))
   if key in checks:
    d=checks[key];length=next(p['length_m'] for p in d['path_checks'] if p['id']==d['limiting_path'])
    if e.dxf.text.endswith('Amp.'):e.dxf.text=dec(d['design_load_A'],1)+'Amp.'
    elif e.dxf.text.endswith('Met.'):e.dxf.text=dec(length,2)+'Met.'
  if e.dxftype()=='INSERT' and e.dxf.name=='RT 1-12':
   for a in e.attribs:
    match=re.search(r'RT_(\d+)',a.dxf.tag)
    if match and 'R'+str(int(match.group(1))) in checks:
     n=int(match.group(1));d=checks['R'+str(n)]
     # Preserve the approved legend width and number fields; longer placeholders can collide with its glyphs.
     a.dxf.text=re.sub(r'\d+A',str(d['chosen_fuse_A'])+'A',a.dxf.text,count=1)
 # Keep references resolvable after moving the new drawing to its own folder.
 xrefs=[]
 for block in doc.blocks:
  if not block.block.dxf.flags&4:continue
  raw=block.block.dxf.get('xref_path','');p=Path(raw.replace('\\','/'));candidate=p if p.is_absolute() else original_path.parent/p
  if not candidate.exists():
   candidates=[p for p in original_path.parent.rglob(Path(raw.replace('\\','/')).name) if p.is_file()]
   if len(candidates)==1:candidate=candidates[0]
  exists=candidate.exists()
  if exists:block.block.dxf.xref_path=str(candidate.resolve())
  xrefs.append({'name':block.name,'path':block.block.dxf.get('xref_path',''),'resolved':exists})
 doc.header['$INSUNITS']=6;doc.header['$INSBASE']=(0,0,0);doc.set_modelspace_vport(height=360,center=(171680,393298))
 audit=doc.audit();args.output.parent.mkdir(parents=True,exist_ok=True);doc.saveas(args.output)
 saved=ezdxf.readfile(args.output);saved_audit=saved.audit()
 assert not saved_audit.errors
 assert hashlib.sha256(original_path.read_bytes()).hexdigest()==original_hash and hashlib.sha256(reference_path.read_bytes()).hexdigest()==reference_hash
 counts=collections.Counter(e.dxf.name for e in added if e.dxftype()=='INSERT')
 assert counts['OVERZETTER']==plan['overzetter_count']
 result={'status':'reference_guided_concept','output_dxf':str(args.output.resolve()),'source_dxf':str(original_path),'reference_dxf':str(reference_path),'source_sha256':original_hash,'reference_sha256':reference_hash,'normal_routes':plan['routes'],'connection_count':len(plan['connections']),'new_cable_connections':counts['OVERZETTER'],'retained_connections':len(plan['connections'])-counts['OVERZETTER'],'calculation':calculation,'modified_original_handles':modified,'removed_original_handles':deleted,'replacement_handles':mapping,'new_entity_count':len(added),'reference_annotation_handles':copied_annotations,'saved_audit_errors':len(saved_audit.errors),'save_audit_fixes':len(audit.fixes),'xrefs':xrefs,'limitations':plan['source_limitations']}
 (args.output.parent/'Controle nieuwe tekening.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 with (args.output.parent/'Aansluitregister nieuwe regels.csv').open('w',encoding='utf-8-sig',newline='') as f:
  fields=list(plan['connections'][0]);writer=csv.DictWriter(f,fieldnames=fields,delimiter=';');writer.writeheader();writer.writerows(plan['connections'])
 print(json.dumps({'file':str(args.output),'normal_routes':len(plan['routes']),'overzetters':counts['OVERZETTER'],'all_direction_checks':calculation['all_directions_pass'],'trafo':calculation['trafo_opwek_A'],'audit_errors':len(saved_audit.errors),'changed_source_entities':len(modified),'added':len(added),'unresolved_xrefs':[x['name'] for x in xrefs if not x['resolved']]},ensure_ascii=False))

if __name__=='__main__':main()
