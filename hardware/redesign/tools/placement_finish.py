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

for net in ['RUN_EN','VSYS']:
 route_one(net,pads[net],.15 if net=='RUN_EN' else .25);print('repaired',net,flush=True)
 p.SaveBoard(str(PTH),b)
