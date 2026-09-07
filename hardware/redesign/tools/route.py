"""Geometry-aware two-layer maze router; all results must pass native KiCad DRC.
No successful connection is inferred from this router's status: final connectivity
is checked by KiCad after copper fill. 0.1mm routing grid, conservative 0.20mm
obstacle inflation for 0.15mm manufacturing clearance.
"""
import json,math,heapq,time
from pathlib import Path
import numpy as np
import pcbnew as p
from design import ROOT,PROJECT
PTH=ROOT/(PROJECT+'.kicad_pcb');b=p.LoadBoard(str(PTH));G=.05;NX=1801;NY=1201
F=p.F_Cu;B=p.B_Cu
netobjs={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
def mm(v):return p.ToMM(v)
def xy(v):return (mm(v.x),mm(v.y))
def vec(a):return p.VECTOR2I(p.FromMM(a[0]),p.FromMM(a[1]))
obsitems=[];pads={};fixed=np.zeros((2,NY,NX),bool)
fixed[:,:12,:]=True;fixed[:,-12:,:]=True;fixed[:,:,:12]=True;fixed[:,:,-12:]=True
for f in b.GetFootprints():
 for pad in f.Pads():
  x,y=xy(pad.GetPosition());bb=pad.GetBoundingBox();sx,sy=xy(bb.GetPosition());ex,ey=sx+mm(bb.GetWidth()),sy+mm(bb.GetHeight())
  layers=tuple(l for l,ki in [(0,F),(1,B)] if pad.IsOnLayer(ki))
  if not layers:continue
  net=pad.GetNetname() or '_NC_'+f.GetReference()+pad.GetNumber()
  if pad.GetAttribute()==p.PAD_ATTRIB_NPTH:
   net='_HOLE';layers=(0,1)
   # Screw-head mechanical keepout, no components/traces inside 2.6mm radius.
   if f.GetReference().startswith('H'):sx=x-2.65;ex=x+2.65;sy=y-2.65;ey=y+2.65
  obsitems.append((net,layers,'rect',(sx,sy,ex,ey)))
  if pad.GetNetCode()>0 and not net.startswith('unconnected-'):
   pads.setdefault(net,[]).append((x,y,layers))
# No tracks in the antenna area on either layer; module antenna is outside board.
fixed[:,:10,700:1300]=True
# Bottom reference under the main USB pair stays continuous.
fixed[1,86:220,1250:1542]=True

def geom_fill(a,kind,data,grow):
 if kind=='rect':
  x1,y1,x2,y2=data;x1-=grow;y1-=grow;x2+=grow;y2+=grow
 else:
  if kind=='circle':x,y,r=data;x1=x-r-grow;y1=y-r-grow;x2=x+r+grow;y2=y+r+grow
  else:
   ax,ay,bx,by,w=data;x1=min(ax,bx)-w/2-grow;y1=min(ay,by)-w/2-grow;x2=max(ax,bx)+w/2+grow;y2=max(ay,by)+w/2+grow
 i1=max(0,int(math.floor(x1/G)));j1=max(0,int(math.floor(y1/G)));i2=min(NX-1,int(math.ceil(x2/G)));j2=min(NY-1,int(math.ceil(y2/G)))
 if i2<i1 or j2<j1:return
 xx=np.arange(i1,i2+1)[None,:]*G;yy=np.arange(j1,j2+1)[:,None]*G
 if kind=='rect':mask=np.maximum(np.maximum(x1+grow-xx,xx-(x2-grow)),0)**2+np.maximum(np.maximum(y1+grow-yy,yy-(y2-grow)),0)**2<=grow**2
 elif kind=='circle':mask=(xx-x)**2+(yy-y)**2<=(r+grow)**2
 else:
  dx=bx-ax;dy=by-ay;t=np.clip(((xx-ax)*dx+(yy-ay)*dy)/max(dx*dx+dy*dy,1e-9),0,1)
  mask=(xx-ax-t*dx)**2+(yy-ay-t*dy)**2<=(w/2+grow)**2
 a[j1:j2+1,i1:i2+1]|=mask

def obstacles(net,width,via=False):
 arr=fixed.copy();grow=(.3 if via else width/2)+.18
 for n,ls,kind,data in obsitems:
  if n!=net:
   for l in ls:geom_fill(arr[l],kind,data,grow)
 if via:
  combined=arr[0]|arr[1]
  for item in list(b.GetTracks())+[pad for f in b.GetFootprints() for pad in f.Pads()]:
   if isinstance(item,p.PCB_VIA):rad=mm(item.GetDrillValue())/2
   elif isinstance(item,p.PAD) and item.GetDrillSize().x>0:rad=mm(max(item.GetDrillSize().x,item.GetDrillSize().y))/2
   else:continue
   x,y=xy(item.GetPosition());geom_fill(combined,'circle',(x,y,rad),.15+.26)
  return combined
 return arr

def track(net,a,z,l,w=.2):
 if math.dist(a,z)<1e-5:return
 t=p.PCB_TRACK(b);t.SetStart(vec(a));t.SetEnd(vec(z));t.SetLayer(F if l==0 else B);t.SetWidth(p.FromMM(w));t.SetNet(netobjs[net]);b.Add(t)
 obsitems.append((net,(l,),'seg',(*a,*z,w)))
def via(net,a):
 for v0 in b.GetTracks():
  if isinstance(v0,p.PCB_VIA) and v0.GetNetname()==net and math.dist(xy(v0.GetPosition()),a)<.01:return
 t=p.PCB_VIA(b);t.SetPosition(vec(a));t.SetWidth(p.FromMM(.6));t.SetDrill(p.FromMM(.3));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(F,B);t.SetNet(netobjs[net]);b.Add(t)
 obsitems.append((net,(0,1),'circle',(*a,.3)))
def poly(net,pts,w=.2,l=0):
 for a,z in zip(pts,pts[1:]):track(net,a,z,l,w)
# Deliberately planned full-speed USB trunk, wide geometry over uninterrupted B.Cu.
poly('USB_CONN_D+',[(63,6.5),(63.25,6.5),(63.5,6.75)],.25)
poly('USB_CONN_D+',[(63.5,6.75),(75,6.75)],1.5)
poly('USB_CONN_D+',[(75,6.75),(78,9.75),(79.1125,10.8625),(79.1125,11.35)],.25)
poly('USB_CONN_D-',[(63,8.75),(63.25,8.75),(63.5,8.5)],.25)
poly('USB_CONN_D-',[(63.5,8.5),(75,8.5)],1.5)
poly('USB_CONN_D-',[(75,8.5),(78,11.5),(78,12.65),(79.1125,12.65)],.25)
# Short module-side stubs to series resistors.
poly('USB_D+',[(58.75,7),(60.5,7),(61,6.5)],.25)
poly('USB_D-',[(58.75,8.5),(60.75,8.5),(61,8.75)],.25)

# Reserve short, narrow outward escapes before routing adjacent fine-pitch pins.
for f in b.GetFootprints():
 if f.GetReference() not in ['U2','J1','U4']:continue
 fx,fy=xy(f.GetPosition())
 for pad in f.Pads():
  net=pad.GetNetname();x,y=xy(pad.GetPosition())
  if net not in pads or net=='GND' or pad.GetAttribute()!=p.PAD_ATTRIB_SMD:continue
  if f.GetReference()=='J1':end=(x-1.0,y)
  elif f.GetReference()=='U2':
   if abs(x-fx)>abs(y-fy):end=(x+math.copysign(.9,x-fx),y)
   else:end=(x,y+math.copysign(.9,y-fy))
  else:end=(x+math.copysign(.6,x-fx),y)
  track(net,(x,y),end,0,.15)
  old=(x,y,(0,))
  if old in pads[net]:pads[net].remove(old);pads[net].append((*end,(0,)))

moves=[(1,0,1),(-1,0,1),(0,1,1),(0,-1,1),(1,1,1.414214),(1,-1,1.414214),(-1,1,1.414214),(-1,-1,1.414214)]
def idx(x,y):return int(round(x/G)),int(round(y/G))
def route_one(net,targets,width):
 blocks=obstacles(net,width);vblock=obstacles(net,width,True)
 pts=list(dict.fromkeys(targets));nodes=[]
 for x,y,ls in pts:
  i,j=idx(x,y);ok=[l for l in ls if 0<=i<NX and 0<=j<NY and not blocks[l,j,i]]
  if not ok:raise RuntimeError(f'blocked pad {net}: {(x,y,ls)}')
  nodes.append([(l,j,i) for l in ok])
 tree=set(nodes.pop(0));remaining=list(zip(nodes,pts[1:]));paths=[]
 # Include already laid manual tracks as legal routing-tree copper, by components.
 # Still explicitly connect all pads; duplicate same-net segments are harmless and removed later.
 while remaining:
  # choose nearest remaining target to current tree
  ti=min(range(len(remaining)),key=lambda k:min(abs(n[1]-t[1])+abs(n[2]-t[2]) for n in remaining[k][0] for t in tree))
  goals,exact=remaining.pop(ti);goalset=set(goals);gy,gx=goals[0][1:]
  def h(n):dx=abs(n[2]-gx);dy=abs(n[1]-gy);return max(dx,dy)+.414214*min(dx,dy)
  pq=[];dist={};prev={}
  for n in tree:dist[n]=0;heapq.heappush(pq,(h(n),0,n))
  end=None
  while pq:
   _,d,n=heapq.heappop(pq)
   if d!=dist.get(n):continue
   if n in goalset:end=n;break
   l,j,i=n
   for di,dj,cost in moves:
    a=i+di;z=j+dj
    if a<0 or a>=NX or z<0 or z>=NY or blocks[l,z,a]:continue
    if di and dj and (blocks[l,j,a] or blocks[l,z,i]):continue
    nn=(l,z,a);nd=d+cost*(1 if l==0 else 3)
    if nd<dist.get(nn,1e30):dist[nn]=nd;prev[nn]=n;heapq.heappush(pq,(nd+h(nn),nd,nn))
   if not vblock[j,i]:
    nn=(1-l,j,i);nd=d+65
    if nd<dist.get(nn,1e30):dist[nn]=nd;prev[nn]=n;heapq.heappush(pq,(nd+h(nn),nd,nn))
  if end is None:raise RuntimeError(f'no route {net}: {exact}')
  path=[end]
  while path[-1] in prev:path.append(prev[path[-1]])
  path.reverse();tree.update(path);tree.update(goals);paths.append(path)
 # Compress into straight segments without altering path geometry.
 for path in paths:
  if len(path)<2:continue
  start=last=path[0];direction=None
  for n in path[1:]:
   dd=(n[0]-last[0],n[1]-last[1],n[2]-last[2])
   if n[0]!=last[0]:
    track(net,(start[2]*G,start[1]*G),(last[2]*G,last[1]*G),last[0],width)
    via(net,(n[2]*G,n[1]*G));start=n;direction=None
   elif dd!=direction:
    if direction is not None:track(net,(start[2]*G,start[1]*G),(last[2]*G,last[1]*G),last[0],width)
    start=last;direction=dd
   last=n
  track(net,(start[2]*G,start[1]*G),(last[2]*G,last[1]*G),last[0],width)
 # Exact off-grid pad centers attach to grid; DRC remains the final authority.
 for x,y,ls in pts:
  i,j=idx(x,y)
  if abs(i*G-x)+abs(j*G-y)>.00001:track(net,(x,y),(i*G,j*G),ls[0],width)

power={'VBUS','VBUS_RAW','VSYS','VBAT','PACK_POS','PACK_FUSED','3V3_REG','3V3','OLED_3V3'}
# Dense interface nets first; ground is completed with vias and copper zones.
order=sorted([n for n in pads if n!='GND'],key=lambda n:(0 if n.startswith(('USB_','CC')) else 1 if n in power else 2,len(pads[n]),sum(math.dist(pads[n][0][:2],t[:2]) for t in pads[n])))
failed=[]
for num,net in enumerate(order):
 t0=time.time()
 try:route_one(net,pads[net],.30 if net in power else .20)
 except RuntimeError as e:failed.append(str(e));print(str(e),flush=True)
 print(num+1,len(order),net,'FAILED' if failed and net in failed[-1] else 'done',round(time.time()-t0,2),flush=True)
 p.SaveBoard(str(PTH),b)
# Connect each ground SMD pad to a close, safe ground via on the continuous reference plane.
grounds=list(dict.fromkeys(pads['GND']));gv=obstacles('GND',.2,True);gb=obstacles('GND',.2)
for x,y,ls in grounds:
 if 1 in ls:continue
 i,j=idx(x,y);best=None
 for radius in range(0,51):
  cand=[(i+dx,j+dy) for dx in range(-radius,radius+1) for dy in range(-radius,radius+1) if max(abs(dx),abs(dy))==radius]
  for a,z in sorted(cand,key=lambda t:(t[0]-i)**2+(t[1]-j)**2):
   if not(0<a<NX-1 and 0<z<NY-1) or gv[z,a]:continue
   steps=max(abs(a-i),abs(z-j),1);line=[(int(round(i+(a-i)*k/steps)),int(round(j+(z-j)*k/steps))) for k in range(steps+1)]
   if any(gb[0,q,r] for r,q in line):continue
   best=(a*G,z*G);break
  if best:break
 if best:
  track('GND',(x,y),best,0,.25);via('GND',best);geom_fill(gv,'circle',(*best,.15),.41)
 else:print('Ground relies on fill',x,y,flush=True)
# Thermal vias adjacent to BQ24074 exposed pad, connected by solid ground fill.
for pt in [(22.65,22.65),(23.35,22.65),(22.65,23.35),(23.35,23.35)]:
 if not obstacles('GND',.2,True)[idx(*pt)[1],idx(*pt)[0]]:via('GND',pt)
# Distributed stitching, excluding antenna, holes, and USB reference reservation.
vo=obstacles('GND',.2,True)
for y in np.arange(3,59,5):
 for x in np.arange(3,89,5):
  i,j=idx(x,y)
  if not vo[j,i]:
   via('GND',(float(x),float(y)));geom_fill(vo,'circle',(float(x),float(y),.15),.41)
for layer in [F,B]:
 z=p.ZONE(b);z.SetLayer(layer);z.SetNet(netobjs['GND']);z.SetLocalClearance(p.FromMM(.2));z.SetPadConnection(p.ZONE_CONNECTION_THERMAL);z.SetThermalReliefGap(p.FromMM(.25));z.SetThermalReliefSpokeWidth(p.FromMM(.25));z.SetMinThickness(p.FromMM(.2));z.SetIslandRemovalMode(p.ISLAND_REMOVAL_MODE_ALWAYS)
 z.Outline().NewOutline()
 for a in [(0.4,.4),(89.6,.4),(89.6,59.6),(.4,59.6)]:z.Outline().Append(int(p.FromMM(a[0])),int(p.FromMM(a[1])))
 b.Add(z)
# Front copper-pour exclusion keeps the USB calculation a microstrip approximation.
z=p.ZONE(b);z.SetLayer(F);z.SetIsRuleArea(True);z.SetDoNotAllowZoneFills(True);z.SetDoNotAllowTracks(False);z.SetDoNotAllowVias(False);z.SetDoNotAllowPads(False);z.SetDoNotAllowFootprints(False);z.Outline().NewOutline()
for a in [(62.8,4),(76,4),(76,11),(62.8,11)]:z.Outline().Append(int(p.FromMM(a[0])),int(p.FromMM(a[1])))
b.Add(z)
p.SaveBoard(str(PTH),b)
(ROOT/'verification/router-log.json').write_text(json.dumps({'failed':failed,'tracks':len(b.GetTracks()),'note':'Run native DRC and fill before any release'},indent=2))
print('ROUTING FINISHED',len(failed),'failed nets; not a DRC result',flush=True)
