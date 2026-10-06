"""Twaalf fysieke posities, haakse vertrekstukken en tampen aan de buitenzijde."""
import math

ALLOCATION_ORDER=[2,11,3,10,4,9,5,8,6,7]

def allocation_order(config):
 allowed=set(config.get('direction_slots',ALLOCATION_ORDER));return [n for n in ALLOCATION_ORDER if n in allowed]

def station_frame(station,lines):
 from shapely.geometry import Polygon,Point
 from ezdxf import bbox
 rects=[]
 for e in station.virtual_entities():
  if e.dxftype()!='LWPOLYLINE' or len(e)!=4:continue
  p=Polygon(e.get_points('xy'))
  if p.is_valid and p.area>3:rects.append(p)
 if not rects:raise ValueError('Stationsfront ontbreekt; leg lokale aansluitposities vast.')
 body=min(rects,key=lambda p:p.area);center=body.centroid;coords=list(body.exterior.coords);edges=[];bound=bbox.extents([station]);inside=lambda p:bound.extmin.x<=p[0]<=bound.extmax.x and bound.extmin.y<=p[1]<=bound.extmax.y
 reference=max(lines,key=lambda n:lines[n].length);g=lines[reference];outside=next((p for p in g.coords if not inside(p)),None)
 if outside is None:raise ValueError('Stationsuitloop heeft geen terreinroute.')
 for a,b in zip(coords[:-1],coords[1:]):
  length=math.dist(a,b);mid=((a[0]+b[0])/2,(a[1]+b[1])/2);normal=(mid[0]-center.x,mid[1]-center.y);norm=math.hypot(*normal);normal=(normal[0]/norm,normal[1]/norm);score=normal[0]*(outside[0]-mid[0])+normal[1]*(outside[1]-mid[1]);edges.append((length,score,a,b,mid,normal))
 longest=max(e[0] for e in edges);_,_,a,b,mid,normal=max((e for e in edges if e[0]>longest-.05),key=lambda e:e[1]);u=((b[0]-a[0])/longest,(b[1]-a[1])/longest)
 names=sorted(lines,key=lambda n:int(n[1:]));p,q=lines[names[0]].coords[0],lines[names[-1]].coords[0]
 if u[0]*(q[0]-p[0])+u[1]*(q[1]-p[1])<0:u=(-u[0],-u[1]);a,b=b,a
 perpendicular=(u[1],-u[0])
 if perpendicular[0]*normal[0]+perpendicular[1]*normal[1]<0:raise ValueError('Richtingnummers lopen tegengesteld aan het stationsfront.')
 normal=perpendicular
 # Positive CAD offset of the outward departure must point to increasing slots.
 if (-normal[1])*u[0]+normal[0]*u[1]<0:raise ValueError('Stationsposities lopen tegengesteld; controleer frontoriëntatie.')
 return {'front_center':list(mid),'front_a':list(a),'front_b':list(b),'port_axis':list(u),'outward_axis':list(normal),'body_geometry':body.__geo_interface__,'reference_direction':reference}

def build_station_exit(data,doc,obstacles=None,surfaces=None,region=None,road=None,_search=True):
 from shapely.geometry import shape,Point,LineString,box
 from shapely.ops import substring
 from ezdxf import bbox
 lines={d['id']:shape(d['display_main']) for d in data['directions']};prior=data.get('station_exit_layout')
 if prior and all(math.dist(lines[n].coords[0],r['port_xy'])<.00001 and math.dist(lines[n].coords[1],r['first_corner_xy'])<.00001 for n,r in prior['active_ports'].items()):return lines
 if obstacles is not None and _search:
  import copy
  original=copy.deepcopy(data);trials=sorted([(a,b) for a in [0,-.2,-.4,-.6,-.8,-1,-1.2] for b in [0,.2,.4,.6,.8,1,1.2]],key=lambda p:abs(p[0])+abs(p[1]))
  for lateral,outward in trials:
   candidate=copy.deepcopy(original);candidate['config']['rules']['station_corner_lateral_adjust_m']=lateral;candidate['config']['rules']['station_corner_outward_adjust_m']=outward
   try:result=build_station_exit(candidate,doc,_search=False)
   except ValueError:continue
   paths=list(result.values())+[shape(r['geometry']) for r in candidate['station_tamps']]
   if any(g.intersects(obstacles) or (region is not None and not region.buffer(.2).covers(g)) for g in paths):continue
   if surfaces is not None and any(g.difference(surfaces.buffer(.2)).length>lines[name].difference(surfaces.buffer(.2)).length+.01 for name,g in result.items()):continue
   if road is not None and (any(g.intersection(road).length>lines[name].intersection(road).length+.01 for name,g in result.items()) or any(shape(r['geometry']).intersection(road).length>.01 for r in candidate['station_tamps'])):continue
   data.clear();data.update(candidate);return result
  raise ValueError('Geen boomvrije stationsuitloop met correcte poorten en tampen gevonden.')
 station=doc.entitydb[data['config']['station_handle']];frame=station_frame(station,lines);c=frame['front_center'];u=frame['port_axis'];normal=frame['outward_axis'];pitch=data['config']['rules']['lane_pitch_m'];straight=data['config']['rules'].get('station_straight_departure_m',1.8);cut=data['config']['rules'].get('station_exit_join_m',16);occupied={int(d['id'][1:]):d for d in data['directions']};left=[n for n in occupied if n<=6];right=[n for n in occupied if n>=7]
 if not left or not right:raise ValueError('Uitloop met één gebruikte bank vraagt een expliciete corridorbeoordeling.')
 bb=bbox.extents([station]);station_box=box(bb.extmin.x,bb.extmin.y,bb.extmax.x,bb.extmax.y);reference=lines[frame['reference_direction']];b=next(p for p in reference.coords if not station_box.covers(Point(p)));depth=(b[0]-c[0])*normal[0]+(b[1]-c[1])*normal[1];along=(b[0]-c[0])*u[0]+(b[1]-c[1])*u[1]
 if depth<straight+.2 or along<.5:raise ValueError('Geen bruikbare haakse stationscorridor met kort vertrekstuk.')
 along+=data['config']['rules'].get('station_corner_lateral_adjust_m',0);depth+=data['config']['rules'].get('station_corner_outward_adjust_m',0);corner=(c[0]+along*u[0]+depth*normal[0],c[1]+along*u[1]+depth*normal[1]);p=(c[0]+straight*normal[0],c[1]+straight*normal[1]);q=(p[0]+along*u[0],p[1]+along*u[1]);suffix=substring(reference,reference.project(Point(b)),min(reference.length,cut+10));spine=LineString([c,p,q,corner]+list(suffix.coords)[1:]);phase=min(3.5,spine.length-2);banks={};ports={};new_lines=dict(lines);join_points={}
 for bank,representative in [('left',max(left)),('right',min(right))]:
  delta=(representative-6.5)*pitch;physical=spine.offset_curve(delta,join_style=2,mitre_limit=10);at=physical.project(spine.interpolate(phase));guide=lines['R'+str(representative)];join=guide.project(Point(b));tail=substring(guide,join,min(guide.length,cut+10));bank_axis=LineString(list(substring(physical,0,at).coords)+list(tail.coords));banks[bank]={'representative':representative,'geometry':bank_axis.__geo_interface__}
  for slot in ([n for n in occupied if n<=6] if bank=='left' else [n for n in occupied if n>=7]):
   name='R'+str(slot);old=lines[name];lane=bank_axis.offset_curve((slot-representative)*pitch,join_style=2,mitre_limit=10);old_join=old.project(guide.interpolate(join+2));target=old.interpolate(old_join);end=lane.project(target)
   if lane.distance(target)>.001:raise ValueError('Stationsbank sluit niet exact aan op bestaande bundel: '+name)
   head=substring(lane,0,end);tail_line=substring(old,old_join,old.length);coords=list(head.coords)+list(tail_line.coords)[1:];new=LineString(coords)
   if not new.is_simple:raise ValueError('Stationsuitloop vormt lus: '+name)
   new_lines[name]=new;ports[name]={'slot':slot,'port_xy':list(new.coords[0]),'first_corner_xy':list(new.coords[1]),'straight_m':math.dist(new.coords[0],new.coords[1]),'bank':bank};occupied[slot]['station_exit_protected_m']=head.length+1;join_points[name]=head.length
 tamps=[]
 for slot,bank,neighbour in [(1,'left',2),(12,'right',11)]:
  bank_axis=shape(banks[bank]['geometry']);representative=banks[bank]['representative'];lane=bank_axis.offset_curve((slot-representative)*pitch,join_style=2,mitre_limit=10);stub=substring(lane,0,data['config']['rules'].get('tamp_length_m',5));tamps.append({'id':'R'+str(slot),'layer':'Aansluiting LS K'+str(slot).zfill(2),'geometry':stub.__geo_interface__,'length_m':stub.length,'port_xy':list(stub.coords[0]),'end_xy':list(stub.coords[-1]),'neighbour':neighbour,'slot':slot,'new_cable_label':'150Al'})
 all_ports=[{'slot':slot,'xy':[c[0]+(slot-6.5)*pitch*u[0],c[1]+(slot-6.5)*pitch*u[1]],'status':'tamp' if slot in [1,12] else 'used' if slot in occupied else 'free'} for slot in range(1,13)]
 data['station_tamps']=tamps;data['station_exit_layout']=dict(frame,position_count=12,pitch_m=pitch,allocation_order=allocation_order(data['config']),physical_positions=all_ports,active_ports=ports,banks=banks,join_positions_m=join_points);data['config']['direction_slots']=allocation_order(data['config'])
 # Keep prior offset evidence only where the old shared CAD is retained.
 proof=[]
 for row in data.get('shared_offset_rebuild',[]):
  piece=shape(row['geometry']);d=next(d for d in data['directions'] if d['id']==row['direction']);tail=substring(new_lines[row['direction']],d['station_exit_protected_m'],new_lines[row['direction']].length);remaining=piece.intersection(tail.buffer(.000001));parts=list(remaining.geoms) if hasattr(remaining,'geoms') else [remaining]
  for part in parts:
   if part.geom_type=='LineString' and part.length>1:proof.append(dict(row,geometry=part.__geo_interface__))
 data['shared_offset_rebuild']=proof
 for d in data['directions']:d['display_main']=new_lines[d['id']].__geo_interface__
 return new_lines

def draw_tamps(data,doc,symbol,text,line):
 for row in data.get('station_tamps',[]):
  from shapely.geometry import shape
  wire=line(shape(row['geometry']),row['layer']);row['polyline_handle']=wire.dxf.handle;e=symbol('NIEUWE MOF',row['end_xy'],row['layer']);row['end_mof_handle']=e.dxf.handle;text('EM',(row['end_xy'][0]+.8,row['end_xy'][1]+.8),row['layer'])

def validate_station_exit(doc,data):
 from shapely.geometry import shape,Point
 from shapely.ops import substring
 from ezdxf import bbox
 frame=data.get('station_exit_layout');errors=[]
 if not frame:return errors
 c=frame['front_center'];u=frame['port_axis'];n=frame['outward_axis'];pitch=frame['pitch_m'];by={d['id']:d for d in data['directions']}
 for name,row in frame['active_ports'].items():
  g=shape(by[name]['display_main']);a,b=g.coords[0],g.coords[1];expected=(c[0]+(row['slot']-6.5)*pitch*u[0],c[1]+(row['slot']-6.5)*pitch*u[1]);v=(b[0]-a[0],b[1]-a[1]);length=math.hypot(*v)
  if math.dist(a,expected)>.001 or abs(v[0]*u[0]+v[1]*u[1])>.001 or v[0]*n[0]+v[1]*n[1]<.5:errors.append({'direction':name,'reason':'Geen juiste positie met kort haaks recht vertrekstuk'})
  bank=frame['banks'][row['bank']];guide=shape(bank['geometry']).offset_curve((row['slot']-bank['representative'])*pitch,join_style=2,mitre_limit=10);head=substring(g,0,by[name]['station_exit_protected_m']-1)
  if head.difference(guide.buffer(.000001)).length>.00001:errors.append({'direction':name,'reason':'Stationsbank wijkt af van juiste gedeelde 0.20 m offset'})
 for row in data.get('station_tamps',[]):
  g=shape(row['geometry']);handle=row.get('end_mof_handle');e=doc.entitydb.get(handle) if handle else None
  expected=(c[0]+(row['slot']-6.5)*pitch*u[0],c[1]+(row['slot']-6.5)*pitch*u[1])
  if math.dist(g.coords[0],expected)>.001 or data['drawing']['symbol_types'].get(handle)!='NIEUWE MOF':errors.append({'direction':row['id'],'reason':'Tamp heeft verkeerde stationspositie of mofstatus'})
  if abs(g.length-data['config']['rules'].get('tamp_length_m',5))>.001 or e is None or e.dxf.layer!=row['layer'] or Point(bbox.extents([e]).center.xy).distance(Point(row['end_xy']))>.001:errors.append({'direction':row['id'],'reason':'Tamp mist juiste lengte/eindmof/richtinglaag'})
  wire=doc.entitydb.get(row.get('polyline_handle',''))
  if wire is None or not __import__('shapely').geometry.LineString(wire.get_points('xy')).equals_exact(g,.000001):errors.append({'direction':row['id'],'reason':'Opgeslagen tampgeometrie klopt niet'})
 return errors
