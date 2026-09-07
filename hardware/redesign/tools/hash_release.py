"""Hash the native handoff, source evidence, final reports and derived outputs."""
from pathlib import Path
import hashlib
from design import ROOT
manifest=ROOT/'verification/SHA256SUMS'
files=[]
for p in sorted(ROOT.rglob('*')):
 if not p.is_file() or p==manifest:continue
 rel=p.relative_to(ROOT)
 if any(part in ['__pycache__','pdf-render','development'] for part in rel.parts):continue
 if p.name=='.DS_Store' or p.suffix in ['.pyc','.lck','.kicad_prl']:continue
 files.append(p)
manifest.write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(ROOT).as_posix()+'\n' for p in files))
for line in manifest.read_text().splitlines():
 digest,path=line.split('  ',1);assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest
print('Verified',len(files),'SHA-256 hashes')
