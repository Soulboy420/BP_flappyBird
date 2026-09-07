"""Export review artifacts from already verified native files; does not regenerate CAD."""
import subprocess,json,hashlib
from pathlib import Path
from design import ROOT,PROJECT
CLI='/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli'
sch=ROOT/(PROJECT+'.kicad_sch');pcb=ROOT/(PROJECT+'.kicad_pcb');out=ROOT/'output';out.mkdir(exist_ok=True)
assert not json.loads((ROOT/'verification/final-drc.json').read_text())['violations']
assert not json.loads((ROOT/'verification/final-drc.json').read_text())['unconnected_items']
before=hashlib.sha256(pcb.read_bytes()).hexdigest()
commands=[
 ['sch','export','pdf','-o',str(out/'schaltplan.pdf'),str(sch)],
 ['pcb','export','pdf','--mode-single','--layers','F.Cu,F.SilkS,Edge.Cuts','--scale','2.5','--exclude-value','-o',str(out/'pcb-oberseite.pdf'),str(pcb)],
 ['pcb','export','pdf','--mode-single','--layers','B.Cu,B.SilkS,Edge.Cuts','--scale','2.5','--mirror','--exclude-value','-o',str(out/'pcb-unterseite.pdf'),str(pcb)],
 ['pcb','export','pdf','--mode-single','--layers','F.Fab,F.SilkS,Edge.Cuts','--black-and-white','--scale','2.5','--exclude-value','--sketch-pads-on-fab-layers','--crossout-DNP-footprints-on-fab-layers','-o',str(out/'bestueckungsplan.pdf'),str(pcb)],
 ['pcb','export','gerbers','--layers','F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Paste,B.Paste,Edge.Cuts','--exclude-value','--no-protel-ext','-o',str(out/'fertigung')+'/',str(pcb)],
 ['pcb','export','drill','--format','excellon','--excellon-units','mm','--excellon-separate-th','--generate-report','--report-path',str(out/'fertigung/bohrbericht.txt'),'--generate-map','--map-format','svg','-o',str(out/'fertigung')+'/',str(pcb)],
 ['pcb','export','pos','--format','csv','--units','mm','--exclude-dnp','-o',str(out/'bestueckungspositionen.csv'),str(pcb)]
]
log=[]
for cmd in commands:
 p=subprocess.run([CLI]+cmd,capture_output=True,text=True);log.append({'command':[CLI]+cmd,'returncode':p.returncode,'stdout':p.stdout,'stderr':p.stderr});print(cmd[0:3],p.returncode,flush=True)
 if p.returncode:raise RuntimeError(p.stderr)
assert hashlib.sha256(pcb.read_bytes()).hexdigest()==before,'Export mutated board'
(ROOT/'verification/export-log.json').write_text(json.dumps(log,indent=2)+'\n')
print('Exports complete; PCB unchanged:',before)
