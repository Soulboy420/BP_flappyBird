"""Explicit final USB routing; short local crossover for reversible receptacle."""
from pathlib import Path
from design import ROOT,PROJECT
from sexpr import *
fpath=ROOT/(PROJECT+'.kicad_pcb');tree=parse(fpath.read_text())
for node in list(tree):
 if not isinstance(node,list):continue
 net=get(node,'net')
 if node[0] in ['segment','via'] and net and net[1] in ['USB_CONN_D+','USB_CONN_D-']:tree.remove(node)
 elif node[0]=='segment' and net and net[1]=='GND':
  pts=[tuple(map(float,get(node,k)[1:3])) for k in ['start','end']]
  if any(abs(x-80.8875)<.02 and abs(y-12)<.02 for x,y in pts):tree.remove(node)
fpath.write_text(dumps(tree))
exec(Path(__file__).with_name('route.py').read_text().split('# Deliberately planned')[0])
f=next(f for f in b.GetFootprints() if f.GetReference()=='D2');f.SetPosition(vec((79,14.3)))
# USB main pair: 1.50mm width / 0.25mm gap. Neck downs are kept short.
poly('USB_CONN_D+',[(63,6.5),(63.25,6.5),(63.5,6.75)],.25)
poly('USB_CONN_D+',[(63.5,6.75),(75,6.75)],1.5)
poly('USB_CONN_D+',[(75,6.75),(77,8.75),(77,12.5375),(78.1125,13.65)],.25)
poly('USB_CONN_D-',[(63,8.75),(63.25,8.75),(63.5,8.5)],.25)
poly('USB_CONN_D-',[(63.5,8.5),(75,8.5)],1.5)
poly('USB_CONN_D-',[(75,8.5),(76,9.5),(76,12.8375),(78.1125,14.95)],.25)
def microvia(net,a):
 t=p.PCB_VIA(b);t.SetPosition(vec(a));t.SetWidth(p.FromMM(.55));t.SetDrill(p.FromMM(.25));t.SetViaType(p.VIATYPE_THROUGH);t.SetLayerPair(F,B);t.SetNet(netobjs[net]);b.Add(t)
# 16-pin GCT connector alternates the two USB2 duplicates. Join D+ on B.Cu.
for y in [11.25,12.25]:poly('USB_CONN_D+',[(82.62,y),(81.65,y)],.15);microvia('USB_CONN_D+',(81.65,y))
poly('USB_CONN_D+',[(81.65,11.25),(81.65,12.25)],.2,1)
poly('USB_CONN_D+',[(81.65,11.25),(81,10.6),(80.2,10.6)],.2,1);microvia('USB_CONN_D+',(80.2,10.6))
poly('USB_CONN_D+',[(80.2,10.6),(78.1125,12.6875),(78.1125,13.65)],.15)
for y in [11.75,12.75]:poly('USB_CONN_D-',[(82.62,y),(80.9,y)],.15)
poly('USB_CONN_D-',[(80.9,11.75),(80.9,14.95),(78.1125,14.95)],.15)
track('GND',(79.8875,14.3),(79.9,15.9),0,.25);via('GND',(79.9,15.9))
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNetname()=='GND' and f.GetReference() in ['U2','J1','SW1','U4','C17']:pad.SetLocalZoneConnection(p.ZONE_CONNECTION_FULL)
p.SaveBoard(str(PTH),b)
