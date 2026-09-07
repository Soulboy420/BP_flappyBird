"""Complete residual nets on the saved board using 0.15mm pin escapes."""
from pathlib import Path
src=Path(__file__).with_name('route.py').read_text()
exec(src.split('# Deliberately planned')[0].replace('+.18','+.1501').replace('(.3 if via','(.25 if via').replace('p.FromMM(.6)','p.FromMM(.5)').replace('p.FromMM(.3)','p.FromMM(.25)'))
# Import only the path search definitions, not the main generation routine.
search=src[src.index('moves=[(1,0,1)'):src.index("power={'VBUS'")]
search=search.replace('pts=list(dict.fromkeys(targets));nodes=[]', '''for v0 in b.GetTracks():
  if isinstance(v0,p.PCB_VIA) and v0.GetNetname()==net:
   vi,vj=idx(*xy(v0.GetPosition()));vblock[vj,vi]=False
 pts=list(dict.fromkeys(targets));nodes=[]''')
exec(search)
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA):obsitems.append((t.GetNetname(),(0,1),'circle',(*xy(t.GetPosition()),mm(t.GetWidth(F))/2)))
 else:obsitems.append((t.GetNetname(),(0 if t.GetLayer()==F else 1,),'seg',(*xy(t.GetStart()),*xy(t.GetEnd()),mm(t.GetWidth()))))

for f in b.GetFootprints():
 if f.GetReference()=='C3':
  for pad in f.Pads():
   if pad.GetNetname()=='GND':pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
# Each front fill island gets a bridge directly into the main back plane.
zones=[z for z in b.Zones() if not z.GetIsRuleArea()]
front=next(z for z in zones if z.IsOnLayer(F));back=next(z for z in zones if z.IsOnLayer(B))
fp=front.GetFilledPolysList(F);bp=back.GetFilledPolysList(B)
main=bp.COutline(max(range(bp.OutlineCount()),key=lambda i:bp.COutline(i).BBox().GetWidth()*bp.COutline(i).BBox().GetHeight()))
for k in range(fp.OutlineCount()):
 poly0=fp.COutline(k);box=poly0.BBox();existing=[]
 for t in b.GetTracks():
  if isinstance(t,p.PCB_VIA) and t.GetNetname()=='GND' and poly0.PointInside(t.GetPosition()) and main.PointInside(t.GetPosition()):existing.append(t)
 if existing:continue
 vo=obstacles('GND',.15,True);found=None
 for y in np.arange(mm(box.GetY()),mm(box.GetBottom()),.10):
  for x in np.arange(mm(box.GetX()),mm(box.GetRight()),.10):
   i,j=idx(x,y);pt=vec((i*G,j*G))
   if vo[j,i] or not poly0.PointInside(pt) or not main.PointInside(pt) or not back.HitTestFilledArea(B,pt):continue
   found=(i*G,j*G);break
  if found:break
 if found:via('GND',found);print('bridge',k,found,flush=True)
 else:print('NO BRIDGE',k,flush=True)
p.SaveBoard(str(PTH),b)
