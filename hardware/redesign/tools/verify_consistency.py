"""Read-only cross-check of native XML, PCB, local libraries, design and assembly BOM."""
import csv,json,xml.etree.ElementTree as ET
from collections import Counter
from design import ROOT,PROJECT,C,NETS
from sexpr import *
root=ET.parse(ROOT/'verification/final-netlist.xml').getroot()
xml={c.attrib['ref']:c for c in root.findall('./components/comp')}
b=parse((ROOT/(PROJECT+'.kicad_pcb')).read_text())
def props(f):return {x[1]:x[2] for x in allof(f,'property')}
fps={props(f)['Reference']:f for f in allof(b,'footprint')}
with (ROOT/'output/stueckliste.csv').open() as f:bom={r['Referenz']:r for r in csv.DictReader(f,delimiter=';')}
assert set(xml)==set(fps)==set(bom)==set(C),'Reference mismatch'
pins={};functions={}
for net in root.findall('./nets/net'):
 for n in net.findall('node'):
  k=(n.attrib['ref'],n.attrib['pin']);pins[k]=net.attrib['name'];functions[k]=n.attrib.get('pinfunction','')
def norm(n):return None if not n or n.startswith('unconnected-(') else n
rows=[];dnp=[];model_count=0
for ref in sorted(C,key=lambda r:(r.rstrip('0123456789'),int(''.join(filter(str.isdigit,r))))):
 x=xml[ref];f=fps[ref];pr=props(f);d=C[ref];row=bom[ref];fields={z.attrib['name']:z.text or '' for z in x.findall('./fields/field')}
 assert pr['Value']==x.findtext('value')==row['Wert']==d['value'],ref+' value'
 assert f[1]==x.findtext('footprint')==row['Footprint'],ref+' footprint'
 assert (ROOT/'lib/RevB.pretty'/(f[1].split(':')[1]+'.kicad_mod')).is_file(),ref+' footprint missing'
 for key,bkey,dkey in [('Manufacturer','Hersteller','mfr'),('MPN','Herstellerteilenummer','mpn'),('Package','Gehaeuse','package')]:assert pr[key]==fields[key]==row[bkey]==d[dkey],ref+' '+key
 isdnp='dnp' in (get(f,'attr') or []);xdnp=x.find('./property[@name="dnp"]') is not None
 assert isdnp==xdnp==(row['DNP']=='YES')==d['dnp'],ref+' DNP'
 if isdnp:dnp.append(ref)
 numbered=[pad for pad in allof(f,'pad') if pad[1]]
 assert {p[1] for p in numbered}==set(d['pins']),ref+' pad number set'
 for pad in numbered:
  num=pad[1];net=(get(pad,'net') or ['',None])[-1];xn=pins.get((ref,num))
  assert net==xn,repr((ref,num,'PCB/XML',net,xn))
  assert norm(net)==d['pins'][num],repr((ref,num,'design',net,d['pins'][num]))
  rows.append([ref,d['mpn'],num,functions.get((ref,num),''),net or 'NC','YES' if isdnp else 'NO',f[1]])
 for m in allof(f,'model'):
  assert m[1].startswith('${KIPRJMOD}/'),m[1]
  assert (ROOT/m[1][len('${KIPRJMOD}/'):]).is_file(),m[1];model_count+=1
# Every sheet link and local symbol resolves, including definitions cached in each sheet.
lib=parse((ROOT/'lib/RevB.kicad_sym').read_text());symbols={z[1] for z in allof(lib,'symbol')}
for path in ROOT.glob('*.kicad_sch'):
 s=parse(path.read_text())
 for sh in allof(s,'sheet'):assert (ROOT/props(sh)['Sheetfile']).is_file()
 for sy in allof(s,'symbol'):
  lid=get(sy,'lib_id')[1];assert lid.startswith('RevB:') and lid.split(':',1)[1] in symbols,lid
with (ROOT/'output/pinmapping.csv').open('w') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Referenz','MPN','Pad','Symbolfunktion','Netz','DNP','Footprint']);w.writerows(rows)
report={'result':'PASS','references':len(C),'fitted':len(C)-len(dnp),'dnp_count':len(dnp),'dnp_references':dnp,'functional_nets':len(NETS),'native_nets_including_explicit_NC':len(root.findall('./nets/net')),'physical_numbered_pads':len(rows),'local_model_references':model_count,'front_zone_filled_polygons':sum(len(allof(z,'filled_polygon')) for z in allof(b,'zone') if get(z,'layer') and get(z,'layer')[1]=='F.Cu'),'back_zone_filled_polygons':sum(len(allof(z,'filled_polygon')) for z in allof(b,'zone') if get(z,'layer') and get(z,'layer')[1]=='B.Cu'),'scope':'Exact PCB/XML/BOM/design field, pin, net, DNP and local-file reference comparison. Does not certify electronics or real modules.'}
(ROOT/'verification/consistency.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
