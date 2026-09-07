from pathlib import Path
import sys
sys.path.insert(0,'hardware/redesign/tools')
s=Path('hardware/redesign/tools/finish_route.py').read_text();exec(s.split('errors=json.loads')[0])
for net,pt in [('USB_500',(22.75,25.1))]:
 i,j=idx(*pt);print(net,pt)
 for n,ls,kind,data in obsitems:
  if n==net:continue
  tmp=np.zeros((NY,NX),bool);geom_fill(tmp,kind,data,.25+.1501)
  if tmp[j,i]:print('OBSTACLE',n,ls,kind,data)
 for f in b.GetFootprints():
  for pad in f.Pads():
   if pad.GetDrillSize().x>0 and math.dist(xy(pad.GetPosition()),pt)<mm(max(pad.GetDrillSize().x,pad.GetDrillSize().y))/2+.41: print('HOLE',f.GetReference(),pad.GetNumber(),xy(pad.GetPosition()))
