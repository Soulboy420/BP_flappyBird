"""Make copied KiCad library models project-relative; add explicit provisional stack-up."""
from pathlib import Path
import shutil,json
from sexpr import *
from design import ROOT,PROJECT,KICAD
board=ROOT/(PROJECT+'.kicad_pcb')
paths=[board]+list((ROOT/'lib/RevB.pretty').glob('*.kicad_mod'))
copied=set()
for path in paths:
 t=parse(path.read_text())
 for m in walk(t,'model'):
  raw=m[1]
  if raw.startswith('${KIPRJMOD}'):continue
  tail=raw.split('}/',1)[-1]
  if tail.endswith('VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm.step'):
   tail=tail.replace('VQFN-16','WQFN-16')
  if tail.endswith('SOT-89-5.step'):
   m[1]=Q('${KIPRJMOD}/lib/3dmodels/custom/SOT-89-5-envelope.step');continue
  src=KICAD/'3dmodels'/tail
  if not src.exists():raise FileNotFoundError(src)
  dst=ROOT/'lib/3dmodels'/tail;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);copied.add(str(dst.relative_to(ROOT)))
  m[1]=Q('${KIPRJMOD}/lib/3dmodels/'+tail)
 if path==board:
  setup=get(t,'setup')
  old=get(setup,'stackup')
  if old:setup.remove(old)
  setup.append(parse('''(stackup
    (layer "F.SilkS" (type "Top Silk Screen") (color "White"))
    (layer "F.Paste" (type "Top Solder Paste"))
    (layer "F.Mask" (type "Top Solder Mask") (color "Green") (thickness 0.01))
    (layer "F.Cu" (type "copper") (thickness 0.035))
    (layer "dielectric 1" (type "core") (thickness 1.51) (material "FR4 - provisional") (epsilon_r 4.2) (loss_tangent 0.02))
    (layer "B.Cu" (type "copper") (thickness 0.035))
    (layer "B.Mask" (type "Bottom Solder Mask") (color "Green") (thickness 0.01))
    (layer "B.Paste" (type "Bottom Solder Paste"))
    (layer "B.SilkS" (type "Bottom Silk Screen") (color "White"))
    (copper_finish "ENIG") (dielectric_constraints no))'''))
 path.write_text(dumps(t))
print('Copied',len(copied),'3D models')
