"""Zoek gezamenlijke tracés uit BGT en stationsgeometrie, zonder voorbeeldtracés."""
import math

class SurfaceRouter:
 def __init__(self,sources,config,read,build_grid=True):
  import numpy as np
  from shapely.geometry import shape,box,Point
  from shapely.ops import unary_union
  from shapely import contains_xy
  from vo_terrein import vegetation_class
  self.np=np;self.cfg=config;self.rules=config['rules'];self.s=sources;self.step=self.rules['grid_m']
  def fs(n):return [f for f in read(config['bgt'][n])['features'] if not f['properties'].get('eind_registratie') and not f['properties'].get('termination_date')]
  roads=fs('wegdeel');self.walk=unary_union([shape(f['geometry']) for f in roads if f['properties'].get('functie') in ['voetpad','voetgangersgebied','voetpad op trap','inrit']]);self.road=unary_union([shape(f['geometry']) for f in roads if f['properties'].get('functie')=='rijbaan lokale weg']);self.parking=unary_union([shape(f['geometry']) for f in roads if f['properties'].get('functie')=='parkeervlak'])
  green=fs('begroeidterreindeel');self.woody=unary_union([shape(f['geometry']) for f in green if vegetation_class(f['properties'])=='woody']+[shape(f['geometry']) for f in fs('vegetatieobject_vlak')]);self.unknown_green=unary_union([shape(f['geometry']) for f in green if vegetation_class(f['properties'])=='green_unknown']);self.trees=unary_union([shape(f['geometry']) for f in fs('vegetatieobject_punt')]);self.buildings=unary_union([shape(f['geometry']) for f in fs('pand')]);self.station=box(*sources['station_bbox'])
  from vo_topografie import topography_obstacles
  self.topo=topography_obstacles(config,sources['region']);self.topo_obstacles=unary_union([self.topo['trees'],self.topo['uncertain_contours']])
  self.erf=unary_union([shape(f['geometry']) for f in fs('onbegroeidterreindeel') if f['properties'].get('fysiek_voorkomen')=='erf']).difference(self.station)
  self.erf=self.erf.difference(self.walk)
  clearance=self.rules['route_clearance_m'];self.physical_obstacles=unary_union([self.woody,self.trees.buffer(self.rules['tree_body_radius_m']),self.buildings,self.topo_obstacles]).difference(self.station);self.blocked=unary_union([self.woody.buffer(clearance),self.trees.buffer(self.rules['tree_body_radius_m']+clearance),self.buildings.buffer(clearance),self.topo_obstacles.buffer(clearance)]).difference(self.station)
  self.natural_obstacles=self.physical_obstacles
  erf_margin=self.rules.get('bundle_erf_margin_m',.1)
  self.physical_obstacles=unary_union([self.physical_obstacles,self.erf]);self.blocked=unary_union([self.blocked,self.erf.buffer(erf_margin)])
  grass=unary_union([shape(f['geometry']) for f in green if vegetation_class(f['properties'])=='open_green']);paving=unary_union([shape(f['geometry']) for f in fs('onbegroeidterreindeel') if f['properties'].get('fysiek_voorkomen')!='erf']);self.allowed_surface=unary_union([self.walk,self.road,self.parking,grass,paving,self.station]).difference(self.erf)
  if not build_grid:return
  area=sources['region'].buffer(7);xmin,ymin,xmax,ymax=area.bounds;self.x0=math.floor(xmin/self.step)*self.step;self.y0=math.floor(ymin/self.step)*self.step
  self.xs=self.x0+np.arange(math.ceil((xmax-self.x0)/self.step)+1)*self.step;self.ys=self.y0+np.arange(math.ceil((ymax-self.y0)/self.step)+1)*self.step;self.X,self.Y=np.meshgrid(self.xs,self.ys);self.height,self.width=self.X.shape
  weights=np.full(self.X.shape,20.0)
  weights[contains_xy(grass,self.X,self.Y)]=self.rules['grass_cost'];weights[contains_xy(self.unknown_green,self.X,self.Y)]=10;weights[contains_xy(paving,self.X,self.Y)]=3
  weights[contains_xy(self.parking,self.X,self.Y)]=3;weights[contains_xy(self.road,self.X,self.Y)]=self.rules['road_cost'];weights[contains_xy(self.walk.buffer(.05),self.X,self.Y)]=self.rules['pavement_cost']
  # Prefer the centre of a pavement strip so the parallel bundle has room.
  weights[contains_xy(self.walk.buffer(-clearance),self.X,self.Y)]=self.rules['pavement_cost']*.85
  weights[~contains_xy(area,self.X,self.Y)]=np.inf;weights[contains_xy(self.blocked,self.X,self.Y)]=np.inf;weights[contains_xy(self.station,self.X,self.Y)]=1
  self.base_weights=weights;self.weights=weights.copy();self.root=self.index(sources['station_center']);self.path_cache={};self.solve()
 def index(self,p):return int(round((p[1]-self.y0)/self.step))*self.width+int(round((p[0]-self.x0)/self.step))
 def xy(self,node):return float(self.xs[node%self.width]),float(self.ys[node//self.width])
 def solve(self):
  from scipy.sparse import coo_matrix
  from scipy.sparse.csgraph import dijkstra
  from shapely.geometry import LineString
  np=self.np;grid=np.arange(self.height*self.width).reshape(self.height,self.width);rows=[];cols=[];costs=[]
  for dy,dx in [(0,1),(1,0),(1,1),(1,-1)]:
   y1=slice(0,self.height-dy);y2=slice(dy,self.height)
   x1=slice(max(0,-dx),self.width-max(0,dx));x2=slice(max(0,dx),self.width-max(0,-dx))
   a=grid[y1,x1];b=grid[y2,x2];wa=self.weights[y1,x1];wb=self.weights[y2,x2];ok=np.isfinite(wa)&np.isfinite(wb)
   if dx and dy:
    ok&=np.isfinite(self.weights[y1,x2])&np.isfinite(self.weights[y2,x1])
   aa=a[ok];bb=b[ok];cc=(wa[ok]+wb[ok])*.5*self.step*(math.sqrt(2) if dx and dy else 1)
   # A full bundle must leave the station through a free gate. Allowing the
   # centreline through the footprint alone can put an outer lane into a hedge.
   bounds=self.station.bounds;xa=self.X[y1,x1][ok];ya=self.Y[y1,x1][ok];xb=self.X[y2,x2][ok];yb=self.Y[y2,x2][ok]
   ina=(xa>=bounds[0])&(xa<=bounds[2])&(ya>=bounds[1])&(ya<=bounds[3]);inb=(xb>=bounds[0])&(xb<=bounds[2])&(yb>=bounds[1])&(yb<=bounds[3]);gate=np.flatnonzero(ina!=inb);keep=np.ones(len(aa),dtype=bool)
   width=self.rules['lane_pitch_m']*max(1,len(self.cfg['direction_slots'])-1)/2
   for j in gate:
    corridor=LineString([(xa[j],ya[j]),(xb[j],yb[j])]).buffer(width).difference(self.station)
    if corridor.intersects(self.physical_obstacles):keep[j]=False
   aa=aa[keep];bb=bb[keep];cc=cc[keep]
   rows.extend([aa,bb]);cols.extend([bb,aa]);costs.extend([cc,cc])
  graph=coo_matrix((np.concatenate(costs),(np.concatenate(rows),np.concatenate(cols))),shape=(grid.size,grid.size)).tocsr()
  self.dist,self.parent=dijkstra(graph,directed=False,indices=self.root,return_predecessors=True);self.path_cache={}
 def target(self,p):
  from shapely.geometry import Point,LineString
  i=self.index(p);y=i//self.width;x=i%self.width;options=[];radius=math.ceil(4/self.step)
  for yy in range(max(0,y-radius),min(self.height,y+radius+1)):
   for xx in range(max(0,x-radius),min(self.width,x+radius+1)):
    n=yy*self.width+xx
    if not math.isfinite(self.dist[n]):continue
    xy=self.xy(n);gap=math.dist(xy,p)
    # Street contact positions are source geometry, independent of routing discounts.
    options.append((gap*8+self.base_weights[yy,xx]*.15,n))
  if not options:raise ValueError('Geen bereikbare straatroute bij '+str(p))
  return min(options)[1]
 def path(self,p):
  from shapely.geometry import LineString
  goal=self.target(p)
  if goal in self.path_cache:return self.path_cache[goal]
  ids=[goal]
  while ids[-1]!=self.root:
   parent=int(self.parent[ids[-1]])
   if parent<0:raise ValueError('Geen verbonden route naar het station.')
   ids.append(parent)
  points=[self.s['station_center']]+[self.xy(i) for i in ids[::-1]]
  cleaned=[]
  for x in points:
   if not cleaned or math.dist(x,cleaned[-1])>.01:cleaned.append(x)
  # Search/calculation paths need cheap deterministic simplification. The shared
  # drawing backbone is simplified once per chain after all directions are known.
  raw=LineString(cleaned);g=raw.simplify(.25)
  if g.intersects(self.blocked):g=raw
  self.path_cache[goal]=g;return g
 def smooth(self,line):
  from shapely.geometry import LineString,Point
  points=list(line.coords);coarse=list(line.simplify(.28).coords);out=[coarse[0]];i=0
  while i<len(coarse)-1:
   best=i+1
   # Inspect local corners plus exponentially spaced long chords, rather than every suffix.
   candidates=set(range(i+2,min(len(coarse),i+15)))
   reach=16
   while i+reach<len(coarse):candidates.add(i+reach);reach*=2
   candidates.add(len(coarse)-1)
   for j in sorted(candidates):
    chord=LineString([coarse[i],coarse[j]]);original=LineString(coarse[i:j+1])
    if chord.intersects(self.blocked):continue
    # A straight line cannot buy a shortcut through planting or off the pavement.
    if chord.difference(self.walk.buffer(.2)).length>original.difference(self.walk.buffer(.2)).length+.35:continue
    if chord.intersection(self.road).length>original.intersection(self.road).length+.4:continue
    if chord.length>original.length+.01:continue
    best=j
   out.append(coarse[best]);i=best
  g=LineString(out)
  if g.intersects(self.blocked):return line
  return g
 def discount(self,lines):
  from shapely.ops import unary_union
  from shapely import contains_xy
  network=unary_union(lines).buffer(self.step*.85);self.weights=self.base_weights.copy();mask=contains_xy(network,self.X,self.Y)&self.np.isfinite(self.weights)
  # Excavation and a road crossing are paid once per trench, not again per wire.
  self.weights[mask]=self.rules['pavement_cost']*self.rules['shared_trench_discount'];self.solve()
 def between(self,a,b):
  """Connect adjacent main-cable taps along their street, without routing a house lead."""
  import heapq
  from shapely.geometry import LineString
  start=self.target(a);goal=self.target(b);dist={start:0};parent={};queue=[(0,start)];np=self.np
  ay,ax=start//self.width,start%self.width;by,bx=goal//self.width,goal%self.width;pad=math.ceil(max(12,math.dist(a,b)*.4)/self.step)
  minx=max(0,min(ax,bx)-pad);maxx=min(self.width-1,max(ax,bx)+pad);miny=max(0,min(ay,by)-pad);maxy=min(self.height-1,max(ay,by)+pad)
  while queue:
   _,u=heapq.heappop(queue)
   if u==goal:break
   y,x=u//self.width,u%self.width
   for dy,dx in [(0,1),(0,-1),(1,0),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]:
    yy=y+dy;xx=x+dx
    if not(minx<=xx<=maxx and miny<=yy<=maxy):continue
    wa=self.base_weights[y,x];wb=self.base_weights[yy,xx]
    if not math.isfinite(wb):continue
    if dx and dy and (not math.isfinite(self.base_weights[y,xx]) or not math.isfinite(self.base_weights[yy,x])):continue
    v=yy*self.width+xx;cost=dist[u]+(wa+wb)*.5*self.step*(math.sqrt(2) if dx and dy else 1)
    if cost<dist.get(v,math.inf):dist[v]=cost;parent[v]=u;heur=math.hypot(xx-bx,yy-by)*self.step*.85;heapq.heappush(queue,(cost+heur,v))
  if goal not in dist:raise ValueError('Geen doorlopend hoofdtracé tussen opeenvolgende straatcontacten.')
  ids=[goal]
  while ids[-1]!=start:ids.append(parent[ids[-1]])
  coordinates=[self.xy(i) for i in ids[::-1]]
  if len(coordinates)==1:coordinates.append(coordinates[0])
  path=LineString(coordinates);chord=LineString([coordinates[0],coordinates[-1]])
  # A short, straight street crossing can prevent a long pavement detour.
  # It is considered only between public street contacts and never through trees.
  if (chord.length<30 and path.length>chord.length*1.35
      and not chord.intersects(self.physical_obstacles)
      and chord.difference(self.allowed_surface.buffer(.2)).length<1):return chord
  return path
