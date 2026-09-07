"""Follow DRC-identified dead track branches to their first real junction."""
import json,math
import pcbnew as p
from design import ROOT,PROJECT
from sexpr import *
path=ROOT/(PROJECT+'.kicad_pcb');b=p.LoadBoard(str(path));t=parse(path.read_text())
r=json.loads((ROOT/'verification/routing-drc.json').read_text())
tracks={x.m_Uuid.AsString():x for x in b.GetTracks()}
remove={i['uuid'] for v in r['violations'] if v['type'] in ['track_dangling','via_dangling'] for i in v['items']}
seeds=list(remove)
def xy(v):return p.ToMM(v.x),p.ToMM(v.y)
def online(pt,tr):
 x,y=xy(pt);a,c=xy(tr.GetStart());z,d=xy(tr.GetEnd());dx,dy=z-a,d-c
 if dx*dx+dy*dy==0:return False
 u=((x-a)*dx+(y-c)*dy)/(dx*dx+dy*dy)
 return -.001<=u<=1.001 and math.hypot(x-a-max(0,min(1,u))*dx,y-c-max(0,min(1,u))*dy)<.012
while seeds:
 uid=seeds.pop();tr=tracks.get(uid)
 if tr is None:continue
 for pt,layer in ([(tr.GetStart(),p.F_Cu),(tr.GetStart(),p.B_Cu)] if isinstance(tr,p.PCB_VIA) else [(tr.GetStart(),tr.GetLayer()),(tr.GetEnd(),tr.GetLayer())]):
  if any(pad.GetNetname()==tr.GetNetname() and pad.IsOnLayer(layer) and pad.HitTest(pt) for f in b.GetFootprints() for pad in f.Pads()):continue
  touching=[]
  for key,x in tracks.items():
   if key in remove or x.GetNetname()!=tr.GetNetname():continue
   if isinstance(x,p.PCB_VIA):
    if x.HitTest(pt):touching.append(key)
   elif x.GetLayer()==layer and online(pt,x):touching.append(key)
  if len(touching)==1:
   nxt=tracks[touching[0]]
   # A via or the interior of a through-track is a junction, not a dead continuation.
   if isinstance(nxt,p.PCB_VIA):continue
   if min(math.dist(xy(pt),xy(nxt.GetStart())),math.dist(xy(pt),xy(nxt.GetEnd())))>.015:continue
   remove.add(touching[0]);seeds.append(touching[0])
t[:]=[x for x in t if not isinstance(x,list) or not get(x,'uuid') or get(x,'uuid')[1] not in remove]
path.write_text(dumps(t));print('Removed DRC dead-branch segments:',len(remove))
