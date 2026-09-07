"""Place readable labels outside masks and bodies; library edits are mirrored exactly."""
from pathlib import Path
import sys,uuid,math,json,copy
import numpy as np
import pcbnew as p
from design import ROOT,PROJECT
from sexpr import *
fpath=ROOT/(PROJECT+'.kicad_pcb');tree=parse(fpath.read_text())
libpath=ROOT/'lib/RevB.pretty/RF_Module__ESP32-C3-WROOM-02.kicad_mod'
lib=parse(libpath.read_text())
# The antenna protrudes from the board; no ink can be printed in that area.
for f in [lib]+[f for f in allof(tree,'footprint') if any(v[1]=='Reference' and v[2]=='U1' for v in allof(f,'property'))]:
 for x in list(f):
  if not isinstance(x,list) or not x[0].startswith('fp_') or not get(x,'layer') or get(x,'layer')[1]!='F.SilkS':continue
  coords=list(walk(x,'xy'))+[z for z in [get(x,'start'),get(x,'end')] if z]
  if any(float(z[2])<-6.4 for z in coords):f.remove(x)
libpath.write_text(dumps(lib));fpath.write_text(dumps(tree))
b=p.LoadBoard(str(fpath));G=.05;NX=1801;NY=1201
mm=p.ToMM
def vec(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
def rect(box,grow=0):return (mm(box.GetX())-grow,mm(box.GetY())-grow,mm(box.GetRight())+grow,mm(box.GetBottom())+grow)
occ=np.zeros((NY,NX),bool)
def indexes(r):
 x1,y1,x2,y2=r;return max(0,int(x1/G)),max(0,int(y1/G)),min(NX-1,int(math.ceil(x2/G))),min(NY-1,int(math.ceil(y2/G)))
def reserve(r):
 if r[2]<0 or r[3]<0 or r[0]>90 or r[1]>60:return
 a,c,z,d=indexes(r);occ[c:d+1,a:z+1]=True
def free(r):
 x1,y1,x2,y2=r
 if min(x1,y1)<.6 or x2>89.4 or y2>59.4:return False
 a,c,z,d=indexes(r);return not occ[c:d+1,a:z+1].any()
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.IsOnLayer(p.F_Mask) or pad.GetDrillSize().x>0:reserve(rect(pad.GetBoundingBox(),.2))
 for gr in f.GraphicalItems():
  if gr.GetLayer() in [p.F_SilkS,p.F_Fab] and isinstance(gr,p.PCB_SHAPE):reserve(rect(gr.GetBoundingBox(),.18))
 f.Reference().SetVisible(False)
# Physical package interiors also stay clear so printing isn't hidden under parts.
for f in b.GetFootprints():
 shapes=[gr for gr in f.GraphicalItems() if gr.GetLayer()==p.F_Fab and isinstance(gr,p.PCB_SHAPE)]
 if shapes:
  rr=[rect(gr.GetBoundingBox()) for gr in shapes];reserve((min(r[0] for r in rr),min(r[1] for r in rr),max(r[2] for r in rr),max(r[3] for r in rr)))
# Banners use the open left corner and lower edge, followed by component labels.
def place(item,origin,size=.8,maxdist=9):
 item.SetTextSize(vec(size,size));item.SetTextThickness(p.FromMM(.13));item.SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 candidates=[(0,0)]+[(dx*.2,dy*.2) for dx in range(-int(maxdist/.2),int(maxdist/.2)+1) for dy in range(-int(maxdist/.2),int(maxdist/.2)+1)]
 candidates=sorted(set(candidates),key=lambda t:math.hypot(*t)+.05*abs(t[0]))
 for dx,dy in candidates:
  item.SetPosition(vec(origin[0]+dx,origin[1]+dy));r=rect(item.GetBoundingBox(),.16)
  if free(r):reserve(r);item.SetVisible(True);return True
 return False
for label,pos,size in [('FLAPPY / REV B',(12,7),1.15),('HAW HAMBURG',(12,9),.8),('1',(39.5,1.2),.8)]:
 t=p.PCB_TEXT(b);t.SetText(label);t.SetLayer(p.F_SilkS);b.Add(t)
 if not place(t,pos,size,4):raise RuntimeError('cannot place title '+label)
for f in sorted(b.GetFootprints(),key=lambda f:(0 if f.GetReference().startswith(('J','U','SW','TP')) else 1,f.GetReference())):
 ref=f.GetReference()
 if ref.startswith('H'):continue
 x,y=mm(f.GetPosition().x),mm(f.GetPosition().y)
 if not place(f.Reference(),(50,15.8) if ref=='U1' else (x,y-2.4),.8,10):raise RuntimeError('cannot place '+ref)
# Back-side pin legend avoids crowded front-side connector pads.
occ[:]=False
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.IsOnLayer(p.B_Mask) or pad.GetDrillSize().x>0:reserve(rect(pad.GetBoundingBox(),.22))
labels=[('DNP: C17 C18 R6 R12 R22 R39',(43,40),.8),('REV B / 90 x 60 mm / 2L / 1.6 mm',(44,34),1.2),('CHARGING OFF: R39 DNP',(44,37),1.1),('J3: 1 GND  2 3V3  3 SCK  4 GND',(49,44),.9),('5 MOSI  6 RESET  7 DC  8 CS',(49,46),.9),('CHECK CABLE PINOUT BEFORE CONNECTING',(48,49),.9),('J2: 1 BAT+ / 2 GND',(15,31),.9),('J6: 1 NTC / 2 GND',(15,40),.9),('J4: 1 KEY / 2 GND',(75,49),.9),('J5: 1 PIEZO+ / 2 PIEZO-',(24,50),.9)]
for f in b.GetFootprints():
 if f.GetReference().startswith('TP'):labels.append((f.GetReference()+' '+f.GetValue(),(mm(f.GetPosition().x),mm(f.GetPosition().y)-1.6),.8))
for label,pos,size in labels:
 t=p.PCB_TEXT(b);t.SetText(label);t.SetLayer(p.B_SilkS);t.SetMirrored(True);b.Add(t)
 if not place(t,pos,size,8):raise RuntimeError('cannot place back label '+label)
p.SaveBoard(str(fpath),b)
print('Silkscreen complete')
