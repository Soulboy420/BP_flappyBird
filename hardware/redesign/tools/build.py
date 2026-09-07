"""Build a self-contained KiCad 10 revision from explicit, auditable design data."""
import copy,json,uuid,math,csv,os,subprocess,sys,xml.etree.ElementTree as ET
from pathlib import Path
import pcbnew as p
from sexpr import *
from design import *
def uid(s):return str(uuid.uuid5(uuid.NAMESPACE_URL,'flappy-revb://'+s))
def q(s):return Q(str(s))
def effect(size=1.0,justify=None,hide=False):
 x=['effects',['font',['size',size,size]]]
 if justify:x.append(['justify',justify])
 if hide:x.append(['hide','yes'])
 return x
cache={}
def load_sym(libid):
 if libid in cache:return copy.deepcopy(cache[libid])
 lib,name=libid.split(':'); alias=None
 if lib=='custom':alias={'XC6220B331PR':'Regulator_Linear:XC6220B331MR'}.get(name)
 if lib=='custom' and name=='74LVC125A':
  names=['1OE_N','1A','1Y','2OE_N','2A','2Y','GND','3Y','3A','3OE_N','4Y','4A','4OE_N','VCC']
  s=['symbol',q(name),['pin_names',['offset',0.508]],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['property',q('Reference'),q('U'),['at',0,22.86,0],effect()],['property',q('Value'),q(name),['at',0,20.32,0],effect()],['symbol',q(name+'_0_1'),['rectangle',['start',-10.16,19.05],['end',10.16,-19.05],['stroke',['width',0.254],['type','default']],['fill',['type','background']]]],['symbol',q(name+'_1_1')]]
  for i,nm in enumerate(names,1):
   x=-15.24 if i<=7 else 15.24;y=(4-i)*5.08 if i<=7 else (i-11)*5.08;a=0 if i<=7 else 180
   kind='power_in' if i in [7,14] else 'tri_state' if i in [3,6,8,11] else 'input'
   s[-1].append(['pin',kind,'line',['at',x,y,a],['length',5.08],['name',q(nm),effect()],['number',q(i),effect()]])
  cache[libid]=copy.deepcopy(s);return s
 if lib=='custom' and name=='TPD2E2U06DCK':
  s=['symbol',q(name),['pin_names',['offset',0.508]],['exclude_from_sim','no'],['in_bom','yes'],['on_board','yes'],['property',q('Reference'),q('D'),['at',0,6.35,0],effect()],['property',q('Value'),q(name),['at',0,3.81,0],effect()],['symbol',q(name+'_0_1'),['rectangle',['start',-3.81,3.81],['end',3.81,-3.81],['stroke',['width',0.254],['type','default']],['fill',['type','background']]]],['symbol',q(name+'_1_1')]]
  for num,nm,x,y,a in [(1,'IO1',-7.62,2.54,0),(2,'IO2',-7.62,-2.54,0),(3,'GND',0,-7.62,90)]:
   s[-1].append(['pin','passive','line',['at',x,y,a],['length',3.81],['name',q(nm),effect()],['number',q(num),effect()]])
 else:
  if alias:base=load_sym(alias)
  else:
   tree=parse((KICAD/'symbols'/(lib+'.kicad_sym')).read_text());base=copy.deepcopy(next(x for x in allof(tree,'symbol') if x[1]==name))
  ext=get(base,'extends')
  if ext:
   parent=load_sym(lib+':'+ext[1]); ownprops={z[1] for z in allof(base,'property')}
   for z in parent[2:]:
    if isinstance(z,list) and ((z[0]=='symbol') or (z[0]=='property' and z[1] not in ownprops) or (z[0]!='property' and not get(base,z[0]))):base.append(copy.deepcopy(z))
   base.remove(ext)
  s=base
  for un in allof(s,'symbol'):
   un[1]=q(name+'_'+str(un[1]).split('_')[-2]+'_'+str(un[1]).split('_')[-1])
  s[1]=q(name)
  if alias:
   for pin in walk(s,'pin'):get(pin,'number')[1]=q({'1':'4','2':'2','3':'1','4':'3','5':'5'}[str(get(pin,'number')[1])])
 cache[libid]=copy.deepcopy(s);return s
# Independent project library; source files intentionally deleted by user are never read here.
syms={}; fpnames={}
for ref,d in C.items():
 name=d['sym'].split(':')[1];d['libid']='RevB:'+name
 if name not in syms:
  print('Symbol',ref,d['sym']);syms[name]=load_sym(d['sym'])
 lib,fn=d['fp'].split(':');local=lib+'__'+fn;d['footprint']='RevB:'+local;fpnames[d['fp']]=local
libdir=ROOT/'lib/RevB.pretty';libdir.mkdir(parents=True,exist_ok=True)
for source,local in fpnames.items():
 lib,name=source.split(':');fpnode=parse((KICAD/'footprints'/(lib+'.pretty')/(name+'.kicad_mod')).read_text());fpnode[1]=q(local)
 if name.startswith('USB_C_Receptacle_GCT_USB4105'):
  for pad in allof(fpnode,'pad'):
   if pad[1]=='SH':pad[1]=q('SH')
 if name=='ESP32-C3-WROOM-02':
  for pad in allof(fpnode,'pad'):
   dr=get(pad,'drill')
   if dr and dr[1]=='0.2':dr[1]='0.3'
 (libdir/(local+'.kicad_mod')).write_text(dumps(fpnode))
# Normalize symbol footprint fields/filters to locally shipped geometry.
for name,s in syms.items():
 refs=[d for d in C.values() if d['libid']=='RevB:'+name];fp=refs[0]['footprint']
 for prop in allof(s,'property'):
  if prop[1]=='Footprint':prop[2]=q(fp)
  if prop[1]=='ki_fp_filters':prop[2]=q('*')
(ROOT/'lib/RevB.kicad_sym').write_text(dumps(['kicad_symbol_lib',['version',20250114],['generator',q('flappy-revb')]]+list(syms.values())))
(ROOT/'sym-lib-table').write_text('(sym_lib_table (version 7) (lib (name "RevB") (type "KiCad") (uri "${KIPRJMOD}/lib/RevB.kicad_sym") (options "") (descr "Self-contained revision B symbols")))')
(ROOT/'fp-lib-table').write_text('(fp_lib_table (version 7) (lib (name "RevB") (type "KiCad") (uri "${KIPRJMOD}/lib/RevB.pretty") (options "") (descr "Verified local footprints")))')
# Multi-sheet schematic, functional groups, readable pin stubs and globally named interconnections.
titles=['USB-C / ESD / Eingang','PowerPath / Akku / Regler','ESP32 / Reset / Straps / ADC','OLED / schaltbare Versorgung','Taster / Piezo','Testpunkte / Mechanik']
rootid=uid('root');schroot=['kicad_sch',['version',20250114],['generator',q('flappy-revb')],['uuid',q(rootid)],['paper',q('A3')],['title_block',['title',q('Flappy Bird / HAW Hamburg')],['rev',q('B')],['date',q('2026-09-05')]],['lib_symbols']]
placements={}
for group,title in enumerate(titles):
 sid=uid('sheet'+str(group));refs=[r for r,d in C.items() if d['group']==group]
 # All components represented, including mechanical and DNP items.
 sch=['kicad_sch',['version',20250114],['generator',q('flappy-revb')],['uuid',q(sid)],['paper',q('A3')],['title_block',['title',q(title)],['rev',q('B')],['date',q('2026-09-05')],['company',q('HAW Hamburg / Bachelorprojekt')],['comment',1,q('Rev B - Freigabe siehe doc/freigabe-checkliste.md')]]]
 libs=['lib_symbols']
 for name in sorted({C[r]['libid'].split(':')[1] for r in refs}):
  s=copy.deepcopy(syms[name]);s[1]=q('RevB:'+name);libs.append(s)
 sch.append(libs)
 annotations=['USB-C: one 5.1k Rd per CC. Native USB FS. 100mA at reset; firmware selects 500mA after enumeration.', 'CHARGING DISABLED by default: R39 DNP. R12 bench option only / NO BATTERY. See battery temperature release gate.', 'IO2 high = normal USB mode; low = suspend request. IO21 boot UART only drives LED. IO8 drives inverted OLED CS.', 'J3: 1 GND, 2 switched 3V3, 3 SCK, 4 GND, 5 MOSI, 6 RESET, 7 DC, 8 CS. Verify real cable before connection.', 'External dry contact and floating passive piezo. Cable ESD clamps are component ratings, not system certification.', 'Bare test pads and mounting holes are listed as DNP; they are physical PCB features, not fitted parts.']
 sch.append(['text',q(annotations[group]),['at',18,20,0],effect(1.27,'left'),['uuid',q(uid('annotation'+str(group)))]])
 cursorx=18; cursory=35; rowheight=0
 for idx,ref in enumerate(refs):
  d=C[ref];sym=syms[d['libid'].split(':')[1]];coords=[list(map(float,get(pin,'at')[1:3])) for pin in walk(sym,'pin')]
  maxx=max([abs(a) for a,b in coords]+[3.81]);maxy=max([abs(b) for a,b in coords]+[3.81])
  cw=max(51,2*maxx+35);ch=max(33,2*maxy+20)
  if cursorx+cw>402:cursorx=18;cursory+=rowheight+6;rowheight=0
  x=round((cursorx+cw/2)/1.27)*1.27;y=round((cursory+ch/2)/1.27)*1.27
  cursorx+=cw+3;rowheight=max(rowheight,ch)
  if y+maxy>263:raise RuntimeError('sheet overflow '+title)
  path='/'+rootid+'/'+sid
  d['uuid']=uid(ref);d['path']=path+'/'+d['uuid']
  s=syms[d['libid'].split(':')[1]]
  pins=list(walk(s,'pin'));actual={str(get(z,'number')[1]) for z in pins}
  if actual!=set(d['pins']):raise RuntimeError((ref,'pin mapping mismatch',actual,set(d['pins'])))
  inst=['symbol',['lib_id',q(d['libid'])],['at',x,y,0],['unit',1],['in_bom','yes'],['on_board','yes'],['dnp','yes' if d['dnp'] else 'no'],['uuid',q(d['uuid'])]]
  vals={'Reference':ref,'Value':d['value'],'Footprint':d['footprint'],'Manufacturer':d['mfr'],'MPN':d['mpn'],'Package':d['package'],'DNP':'YES' if d['dnp'] else 'NO','Note':d['note']}
  for n,(k,v) in enumerate(vals.items()):
   inst.append(['property',q(k),q(v),['at',x,y-maxy-12+n*2.54 if n<2 else y,0],effect(1.27 if n<2 else 0.8,hide=n>=2)])
  for pin in pins:inst.append(['pin',q(get(pin,'number')[1]),['uuid',q(uid(ref+'pin'+get(pin,'number')[1]))]])
  inst.append(['instances',['project',q(PROJECT),['path',q(path),['reference',q(ref)],['unit',1]]]])
  sch.append(inst)
  seen=set()
  for pin in pins:
   num=str(get(pin,'number')[1]);at=get(pin,'at');px,py,ang=map(float,at[1:4]);sx,sy=round(x+px,4),round(y-py,4)
   net=d['pins'][num]
   if (sx,sy,net) in seen:continue
   seen.add((sx,sy,net))
   if net is None:
    sch.append(['no_connect',['at',sx,sy],['uuid',q(uid(ref+'nc'+num))]]);continue
   # extend away from symbol body
   dx,dy=-math.cos(math.radians(ang))*2.54,math.sin(math.radians(ang))*2.54
   ex,ey=round(sx+dx,4),round(sy+dy,4)
   sch.append(['wire',['pts',['xy',sx,sy],['xy',ex,ey]],['stroke',['width',0],['type','default']],['uuid',q(uid(ref+'wire'+num))]])
   la=0 if dx<=0 else 180
   lab=['global_label',q(net),['shape','bidirectional'],['at',ex,ey,la],effect(0.9,'right' if la==0 else 'left'),['uuid',q(uid(ref+'label'+num))]]
   lab.append(['property',q('Intersheetrefs'),q('${INTERSHEET_REFS}'),['at',ex,ey,la],effect(0.8,hide=True)])
   sch.append(lab)
  # Power flags only on externally driven rails, one per net across all sheets.
 # Add documented power source declarations, avoiding altered electrical pin types.
 if group==0:
  power=load_sym('power:PWR_FLAG');power[1]=q('RevB:PWR_FLAG');libs.append(power)
  pl=copy.deepcopy(power);pl[1]=q('PWR_FLAG');syms['PWR_FLAG']=pl
  for idx,net in enumerate(['GND','VBUS','3V3','VBUS_RAW']):
   x=round((40+idx*80)/1.27)*1.27;y=262.89;ref='#FLG0'+str(idx)
   sch.append(['symbol',['lib_id',q('RevB:PWR_FLAG')],['at',x,y,0],['unit',1],['in_bom','no'],['on_board','yes'],['dnp','no'],['uuid',q(uid(ref))],['property',q('Reference'),q(ref),['at',x,y,0],effect(hide=True)],['property',q('Value'),q('PWR_FLAG'),['at',x,y-5.08,0],effect()],['instances',['project',q(PROJECT),['path',q('/'+rootid+'/'+sid),['reference',q(ref)],['unit',1]]]]])
   sch.append(['global_label',q(net),['shape','bidirectional'],['at',x,y,0],effect(0.9,'right'),['uuid',q(uid(ref+'label'))]])
 fname=f'{group+1:02d}-{["usb","power","esp32","oled","controls","test"][group]}.kicad_sch'
 (ROOT/fname).write_text(dumps(sch))
 bx=30+(group%2)*190;by=40+(group//2)*65
 schroot.append(['sheet',['at',bx,by],['size',170,45],['stroke',['width',0.254],['type','default']],['fill',['color',0,0,0,0]],['uuid',q(sid)],['property',q('Sheetname'),q(title),['at',bx,by-2,0],effect(1.4,'left')],['property',q('Sheetfile'),q(fname),['at',bx,by+47,0],effect(1,'left')],['instances',['project',q(PROJECT),['path',q('/'+rootid),['page',q(group+2)]]]]])
schroot.append(['sheet_instances',['path',q('/'),['page',q('1')]]])
(ROOT/(PROJECT+'.kicad_sch')).write_text(dumps(schroot))
(ROOT/'lib/RevB.kicad_sym').write_text(dumps(['kicad_symbol_lib',['version',20250114],['generator',q('flappy-revb')]]+list(syms.values())))
# Export with KiCad itself, so automatically named NC nets also match exactly.
subprocess.run(['/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli','sch','export','netlist','--format','kicadxml','-o',str(ROOT/'verification/netlist.xml'),str(ROOT/(PROJECT+'.kicad_sch'))],check=True)
xml=ET.parse(ROOT/'verification/netlist.xml'); pin_nets={}
for net in xml.findall('.//nets/net'):
 for node in net.findall('node'):pin_nets[(node.get('ref'),node.get('pin'))]=net.get('name')
for ref,d in C.items():
 for pin,net in d['pins'].items():
  if net is not None and pin_nets.get((ref,pin))!=net:raise RuntimeError(('schematic connectivity',ref,pin,net,pin_nets.get((ref,pin))))
# PCB placement and all explicit net/pad assignments. Router is a separate stage.
updating='--update-board' in sys.argv
b=p.LoadBoard(str(ROOT/(PROJECT+'.kicad_pcb'))) if updating else p.BOARD()
b.SetCopperLayerCount(2);b.GetDesignSettings().SetBoardThickness(p.FromMM(1.6))
existing={f.GetReference():f for f in b.GetFootprints()}
netobjs={n.GetNetname():n for n in b.GetNetInfo().NetsByNetcode().values()}
for name in sorted(set(pin_nets.values())):
 if name not in netobjs:n=p.NETINFO_ITEM(b,name);b.Add(n);netobjs[name]=n
def v(x,y):return p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for ref,d in C.items():
 f=existing.get(ref)
 if f is None:
  f=p.FootprintLoad(str(libdir),d['footprint'].split(':')[1]);f.SetReference(ref);f.SetFPID(p.LIB_ID('RevB',d['footprint'].split(':')[1]));b.Add(f)
 f.SetValue(d['value'])
 f.SetExcludedFromBOM(False)
 f.SetFields({'Manufacturer':d['mfr'],'MPN':d['mpn'],'Package':d['package'],'DNP':'YES' if d['dnp'] else 'NO','Note':d['note']})
 for field in f.GetFields():
  if field.GetName() not in ['Reference','Value']:field.SetVisible(False)
 f.SetPosition(v(*d['xy'][:2]));f.SetOrientationDegrees(d['xy'][2]);f.SetPath(p.KIID_PATH(d['path']));f.SetDNP(d['dnp'])
 # Board UUID is independent; schematic association uses the exact hierarchical path.
 for pad in f.Pads():
  num=pad.GetNumber()
  if num:
   if num not in d['pins']:raise RuntimeError((ref,'unknown footprint pad',num))
   net=pin_nets.get((ref,num))
   if net is not None:pad.SetNet(netobjs[net])
 f.Reference().SetTextSize(v(.8,.8));f.Reference().SetTextThickness(p.FromMM(.13));f.Reference().SetTextAngle(p.EDA_ANGLE(0,p.DEGREES_T))
 f.Reference().SetPosition(v(d['xy'][0],d['xy'][1]-2.8));f.Value().SetVisible(False)
 if ref.startswith('TP'):f.Reference().SetVisible(False)
for a,bb in ([] if updating else [((0,0),(90,0)),((90,0),(90,60)),((90,60),(0,60)),((0,60),(0,0))]):
 s=p.PCB_SHAPE();s.SetShape(p.SHAPE_T_SEGMENT);s.SetStart(v(*a));s.SetEnd(v(*bb));s.SetLayer(p.Edge_Cuts);s.SetWidth(p.FromMM(.05));b.Add(s)
p.SaveBoard(str(ROOT/(PROJECT+'.kicad_pcb')),b)
# Conservative rules. No ERC or DRC rule is globally disabled.
pro={'meta':{'filename':PROJECT+'.kicad_pro','version':3},'board':{'design_settings':{'rules':{'min_clearance':.15,'min_track_width':.15,'min_via_diameter':.5,'min_through_hole_diameter':.25,'min_copper_edge_clearance':.3,'min_hole_clearance':.15},'rule_severities':{},'drc_exclusions':[]}},'erc':{'erc_exclusions':[],'rule_severities':{}},'net_settings':{'meta':{'version':5},'classes':[{'name':'Default','clearance':.15,'track_width':.25,'via_diameter':.6,'via_drill':.3,'diff_pair_width':1.5,'diff_pair_gap':.2}],'netclass_patterns':[]},'sheets':[[rootid,PROJECT]],'text_variables':{'RELEASE':'NO-GO pending verification'}}
(ROOT/(PROJECT+'.kicad_pro')).write_text(json.dumps(pro,indent=2))
(ROOT/'tools/design-resolved.json').write_text(json.dumps(C,indent=2))
with (ROOT/'output/stueckliste.csv').open('w') as f:
 w=csv.writer(f,delimiter=';');w.writerow(['Referenz','Wert','Hersteller','Herstellerteilenummer','Gehaeuse','Footprint','DNP','Anmerkung'])
 for ref,d in C.items():w.writerow([ref,d['value'],d['mfr'],d['mpn'],d['package'],d['footprint'],'YES' if d['dnp'] else 'NO',d['note']])
print('Built',len(C),'parts',len(NETS),'nets')
