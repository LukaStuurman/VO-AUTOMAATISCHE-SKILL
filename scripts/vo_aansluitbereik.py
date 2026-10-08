"""Controleer welke richting een aansluiting eerst bereikt in een bundel."""

def intervening_directions(directions,lines):
 from shapely.geometry import Point,LineString,shape
 from shapely.ops import nearest_points
 errors=[]
 for d in directions:
  for r in d['records']:
   if r['code'] in d['new_codes'] or r.get('new_connection'):
    _,target=nearest_points(Point(r['xy']),lines[d['id']])
   else:
    parts=[shape(p['geometry']) if isinstance(p['geometry'],dict) else p['geometry'] for p in d['retained'] if p['code']==r['code']]
    if not parts:continue
    _,target=nearest_points(Point(r['tap']),min(parts,key=lambda g:g.distance(Point(r['tap']))))
   lead=LineString([r['xy'],target.coords[0]])
   if lead.length<.05:continue
   hits=[]
   for other in directions:
    if other is d:continue
    networks=[('new',lines[other['id']])]+[('retained',shape(p['geometry']) if isinstance(p['geometry'],dict) else p['geometry']) for p in other['retained']]
    for kind,g in networks:
     hit=lead.intersection(g)
     if hit.is_empty:continue
     _,q=nearest_points(Point(r['xy']),hit);at=lead.project(q)
     if .05<at<lead.length-.05:hits.append((at,other['id'],kind,list(q.coords[0])))
   if hits:
    at,name,kind,xy=min(hits)
    errors.append({'connection':r['id'],'assigned_direction':d['id'],'nearest_accessible_direction':name,'contact_kind':kind,'contact_xy':xy,'lead_distance_m':at,'reason':'Een tussenliggende hoofdkabel ligt vóór de toegewezen richting; toewijzing en beide berekeningen herzien'})
 return errors
