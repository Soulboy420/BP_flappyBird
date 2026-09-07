from pathlib import Path
import pcbnew as p
from design import ROOT,PROJECT,C
PTH=ROOT/(PROJECT+'.kicad_pcb');b=p.LoadBoard(str(PTH))
for f in b.GetFootprints():
 if f.GetReference() in ['R23','R24']:
  d=C[f.GetReference()];f.SetPosition(p.VECTOR2I(p.FromMM(d['xy'][0]),p.FromMM(d['xy'][1])))
 if f.GetReference()=='U5':
  for pad in f.Pads():
   if pad.GetNetname()=='GND':pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.SaveBoard(str(PTH),b)
s=Path(__file__).with_name('finish_route.py').read_text();exec(s.split('errors=json.loads')[0])
for net in ['RES_M','SCK_BUF','SCK','MOSI_BUF','MOSI','RES_BUF','OLED_RESET_N','OLED_3V3','USB_500','VBUS','3V3','BAT_ADC','BUZZ_GATE']:
 try:route_one(net,pads[net],.15 if net not in ['VBUS','3V3'] else .25);print('repaired',net,flush=True)
 except Exception as e:print('FAILED',e,flush=True)
 p.SaveBoard(str(PTH),b)
