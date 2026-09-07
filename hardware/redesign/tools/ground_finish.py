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
 if f.GetReference() not in ['C7','C19','U5','R13','R39']:continue
 for pad in f.Pads():
  if pad.GetNetname()!='GND':continue
  pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
  x,y=xy(pad.GetPosition());i,j=idx(x,y);vo=obstacles('GND',.15,True);candidates=[]
  for dy in range(-40,41):
   for dx in range(-40,41):
    if not vo[j+dy,i+dx]:candidates.append((math.hypot(dx,dy),((i+dx)*G,(j+dy)*G)))
  for _,target in sorted(candidates)[:20]:
   try:
    route_one('GND',[(x,y,(0,)),(*target,(0,))],.15);via('GND',target);print('ground',f.GetReference(),pad.GetNumber(),target,flush=True);break
   except Exception:pass
p.SaveBoard(str(PTH),b)
