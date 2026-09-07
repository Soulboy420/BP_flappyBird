"""Synchronize procurement fields only; preserve verified geometry, routing and labels."""
import csv,json
from pathlib import Path
from design import *
from sexpr import *
fields={'Value':'value','Manufacturer':'mfr','MPN':'mpn','Package':'package','Note':'note'}
for path in list(ROOT.glob('*.kicad_sch'))+[ROOT/(PROJECT+'.kicad_pcb')]:
 s=parse(path.read_text())
 for n in s:
  if not isinstance(n,list) or n[0] not in ['symbol','footprint']:continue
  props={z[1]:z for z in allof(n,'property')};ref=props.get('Reference')
  if not ref or ref[2] not in C:continue
  d=C[ref[2]]
  if 'DNP' in props:props['DNP'][2]=Q('YES' if d['dnp'] else 'NO')
  if n[0]=='symbol':get(n,'dnp')[1]='yes' if d['dnp'] else 'no'
  elif d['dnp']:
   at=get(n,'attr')
   if at is None:n.append(['attr','dnp'])
   elif 'dnp' not in at:at.append('dnp')
  for k,v in fields.items():
   if k in props:props[k][2]=Q(d[v])
 path.write_text(dumps(s))
resolved=json.loads((ROOT/'tools/design-resolved.json').read_text())
for ref,d in C.items():resolved[ref].update(d)
(ROOT/'tools/design-resolved.json').write_text(json.dumps(resolved,indent=2))
with (ROOT/'output/stueckliste.csv').open('w') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Referenz','Wert','Hersteller','Herstellerteilenummer','Gehaeuse','Footprint','DNP','Anmerkung'])
 for ref,d in resolved.items():w.writerow([ref,d['value'],d['mfr'],d['mpn'],d['package'],d['footprint'],'YES' if d['dnp'] else 'NO',d['note']])
