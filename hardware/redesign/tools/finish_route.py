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
errors=json.loads((ROOT/'verification/router-log.json').read_text())['failed']
names=[e.split('pad ')[-1].split(':')[0] if e.startswith('blocked') else e.split('route ')[1].split(':')[0] for e in errors]
failed=[]
for net in ['USB_500','CHG_N','LED_N','USB_SUSPEND','SUSPEND_N']:
 try:route_one(net,pads[net],.15);print('repaired',net,flush=True)
 except Exception as e:failed.append(str(e));print('FAILED',str(e),flush=True)
 p.SaveBoard(str(PTH),b)
# Ground pin in the SC70 footprint needs a short escape between its two neighbours.
for f in b.GetFootprints():
 if f.GetReference()=='U4':
  pad=next(z for z in f.Pads() if z.GetNumber()=='2');a=xy(pad.GetPosition());target=(58.8,32)
  track('GND',a,target,0,.15);via('GND',target)
# Set solid pad connections where thermal spokes were starved, without changing clearance.
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNetname()=='GND' and (f.GetReference() in ['U2','J1'] or (f.GetReference()=='SW1' and pad.GetNumber()=='3')):
   pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.SaveBoard(str(PTH),b)
(ROOT/'verification/finish-router-log.json').write_text(json.dumps({'failed':failed},indent=2))
