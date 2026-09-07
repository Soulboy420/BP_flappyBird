"""Check exported regions, positions, drill counts and source preservation."""
import csv,json,re,math,hashlib,subprocess
from pathlib import Path
from design import ROOT,PROJECT,C
from sexpr import *
b=parse((ROOT/(PROJECT+'.kicad_pcb')).read_text());fps={next(p[2] for p in allof(f,'property') if p[1]=='Reference'):f for f in allof(b,'footprint')}
with (ROOT/'output/bestueckungspositionen.csv').open() as f:positions=list(csv.DictReader(f))
assert {r['Ref'] for r in positions}=={r for r,d in C.items() if not d['dnp']}
for row in positions:
 ref=row['Ref'];at=get(fps[ref],'at');rot=float(at[3]) if len(at)>3 else 0
 assert abs(float(row['PosX'])-float(at[1]))<.00001
 assert abs(float(row['PosY'])+float(at[2]))<.00001
 assert abs((float(row['Rot'])-rot+180)%360-180)<.00001
 assert row['Side']=='top'
regions={}
for layer in ['F_Cu','B_Cu']:
 s=(ROOT/f'output/fertigung/{PROJECT}-{layer}.gbr').read_text();assert '%TF.FileFunction,Copper,' in s;assert '%TO.N,GND*%' in s
 blocks=re.findall(r'G36\*(.*?)G37\*',s,re.S);areas=[]
 for block in blocks:
  pts=[];x=y=None
  for line in block.splitlines():
   mx=re.search(r'X(-?\d+)',line);my=re.search(r'Y(-?\d+)',line)
   if mx:x=int(mx[1])/1e6
   if my:y=int(my[1])/1e6
   if (mx or my) and x is not None and y is not None:pts.append((x,y))
  if len(pts)>2:areas.append(abs(sum(a[0]*bb[1]-bb[0]*a[1] for a,bb in zip(pts,pts[1:]+pts[:1])))/2)
 assert max(areas)>1000,(layer,'large ground fill missing')
 regions[layer]={'regions':len(blocks),'largest_region_mm2':round(max(areas),2)}
pth=len(allof(b,'via'))+sum(p[2]=='thru_hole' for f in fps.values() for p in allof(f,'pad'))
npth=sum(p[2]=='np_thru_hole' for f in fps.values() for p in allof(f,'pad'))
drill=(ROOT/'output/fertigung/bohrbericht.txt').read_text()
assert int(re.search(r'Total plated holes count (\d+)',drill)[1])==pth
assert int(re.search(r'Total unplated holes count (\d+)',drill)[1])==npth
initial=(ROOT/'verification/initial-git-status.txt').read_text().splitlines()
current=subprocess.check_output(['git','status','--short'],cwd=ROOT.parents[1],text=True).splitlines()
# Tracked changes and deliberate deletions must remain exactly as initially observed.
assert {s for s in initial if not s.startswith('??')}=={s for s in current if not s.startswith('??')}
(ROOT/'verification/final-git-status.txt').write_text('\n'.join(current)+'\n')
report={'result':'PASS','pcb_sha256':hashlib.sha256((ROOT/(PROJECT+'.kicad_pcb')).read_bytes()).hexdigest(),'position_count':len(positions),'positions_units':'mm','positions_origin':'KiCad absolute; X right, Y up (negative for board positive Y)','copper_gerber_regions':regions,'plated_holes_including_slots':pth,'unplated_holes':npth,'initial_tracked_status_preserved':True,'additional_untracked_outside_redesign':[s for s in current if s.startswith('??') and 'hardware/redesign/' not in s and s not in initial]}
(ROOT/'verification/artifact-check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
