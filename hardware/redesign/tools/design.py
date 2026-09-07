"""Revision B engineering source. All pin assignments are explicit and reviewable."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
PROJECT='flappy-esp32c3-revb'
KICAD=Path('/Applications/KiCad/KiCad.app/Contents/SharedSupport')
C={}
RFP='Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
CFP='Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
BIG='Capacitor_SMD:C_1206_3216Metric_Pad1.33x1.80mm_HandSolder'
SOT='Package_TO_SOT_SMD:SOT-23'
XH2='Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical'
PH2='Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical'
def add(ref,sym,value,fp,pins,xy,group,mfr,mpn,package,dnp=False,note=''):
 C[ref]=dict(sym=sym,value=value,fp=fp,pins={str(p):n for p,n in pins.items()},xy=xy,group=group,mfr=mfr,mpn=mpn,package=package,dnp=dnp,note=note)
def r(ref,v,a,b,xy,g,mpn=None,dnp=False,note=''):
 # Panasonic ERJ, 1%, 0805; exact order codes supplied below.
 codes={'0':'0R00','22':'22R0','68':'68R0','100':'1000','220':'2200','1k':'1001','2.2k':'2201','3.3k':'3301','5.1k':'5101','6.19k':'6191','10k':'1002','100k':'1003','330k':'3303','1M':'1004','46.4k':'4642','3.24k':'3241'}
 add(ref,'Device:R',v,RFP,{1:a,2:b},xy,g,'Panasonic',mpn or ('ERJ-6GEY0R00V' if v=='0' else 'ERJ-6ENF'+codes[v]+'V'),'0805',dnp,note)
def c(ref,v,a,xy,g,b='GND',dnp=False):
 big=v=='22u'; val={'22u':'22u 16V X5R','100n':'100n 50V X7R','1u':'1u 25V X7R','18p':'18p 50V C0G'}[v]
 mpn={'22u':'C3216X5R1C226M160AB','100n':'C2012X7R1H104K085AA','1u':'C2012X7R1E105K125AB','18p':'C0805C180J5GACTU'}[v]
 add(ref,'Device:C',val,BIG if big else CFP,{1:a,2:b},xy,g,'TDK',mpn,'1206' if big else '0805',dnp,'22u: effective capacitance qualification required; no substitution by nominal value only' if big else '')
def fet(ref,kind,pins,xy,g,mpn=None):
 pm=kind=='P'; add(ref,'Transistor_FET:AO3401A' if pm else 'Transistor_FET:2N7002',mpn or ('DMP2035U-7' if pm else '2N7002-7-F'),SOT,pins,xy,g,'Diodes Incorporated',mpn or ('DMP2035U-7' if pm else '2N7002-7-F'),'SOT-23')
def tp(ref,net,xy,g=5): add(ref,'Connector:TestPoint',net,'TestPoint:TestPoint_Pad_D1.5mm',{1:net},xy,g,'PCB fabrication','N/A - bare copper pad','PCB pad',True,'Bare copper test point; no assembly item')
add('U1','RF_Module:ESP32-C3-WROOM-02','ESP32-C3-WROOM-02-N4','RF_Module:ESP32-C3-WROOM-02',
{1:'3V3',2:'RESET_N',3:'SCK_M',4:'MOSI_M',5:'RES_M',6:'DC_M',7:'CS_INVERT',8:'BOOT_N',9:'GND',10:'OLED_EN',11:'USB_500',12:'LED_N',13:'USB_D-',14:'USB_D+',15:'BUTTON',16:'SUSPEND_N',17:'BUZZ_GATE',18:'BAT_ADC',19:'GND'},(50,7,0),2,'Espressif','ESP32-C3-WROOM-02-N4','18x20mm module')
add('U2','Battery_Management:BQ24074RGT','BQ24074RGTR','Package_DFN_QFN:VQFN-16-1EP_3x3mm_P0.5mm_EP1.6x1.6mm',
{1:'NTC',2:'VBAT',3:'VBAT',4:'CHG_DISABLE',5:'USB_SUSPEND',6:'USB_500',7:'USB_GOOD_N',8:'GND',9:'CHG_N',10:'VSYS',11:'VSYS',12:'ILIM',13:'VBUS',14:'TMR',15:None,16:'ISET',17:'GND'},(23,23,0),1,'Texas Instruments','BQ24074RGTR','VQFN-16 3x3mm EP1.6',note='Local reflow mandatory; solder exposed pad; NTC required')
add('U3','custom:XC6220B331PR','XC6220B331PR-G','Package_TO_SOT_SMD:SOT-89-5',
{1:'RUN_EN',2:'GND',3:None,4:'VSYS',5:'3V3_REG'},(36,23,0),1,'Torex','XC6220B331PR-G','SOT-89-5')
add('U4','Power_Management:TPS22919DCK','TPS22919DCKR','Package_TO_SOT_SMD:SOT-363_SC-70-6',
{1:'3V3',2:'GND',3:'OLED_EN',4:None,5:'OLED_DISCHARGE',6:'OLED_3V3'},(61,32,0),3,'Texas Instruments','TPS22919DCKR','SC70-6')
add('J1','Connector:USB_C_Receptacle_USB2.0_16P','USB4105-GF-A','Connector_USB:USB_C_Receptacle_GCT_USB4105-xx-A_16P_TopMnt_Horizontal',
{'A1':'GND','A4':'VBUS_RAW','A5':'CC1','A6':'USB_CONN_D+','A7':'USB_CONN_D-','A8':None,'A9':'VBUS_RAW','A12':'GND','B1':'GND','B4':'VBUS_RAW','B5':'CC2','B6':'USB_CONN_D+','B7':'USB_CONN_D-','B8':None,'B9':'VBUS_RAW','B12':'GND','SH':'GND'},(86.3,12,90),0,'GCT','USB4105-GF-A','USB-C 16 SMT + shell THT')
add('J2','Connector_Generic:Conn_01x02','BAT 1S protected',PH2,{1:'PACK_POS',2:'GND'},(6,31,270),1,'JST','B2B-PH-K-S(LF)(SN)','PH 2mm THT',note='Pin 1 POSITIVE; independently verify cable, protected 4.2V Li-ion pack only')
add('J3','Connector_Generic:Conn_01x08','OLED 8 pin','Connector_JST:JST_XH_B8B-XH-A_1x08_P2.50mm_Vertical',
{1:'GND',2:'OLED_3V3',3:'SCK',4:'GND',5:'MOSI',6:'OLED_RESET_N',7:'OLED_DC',8:'OLED_CS_N'},(63,54,180),3,'JST','B8B-XH-A(LF)(SN)','XH 2.5mm THT',note='Board pin sequence is fixed; real OLED cable is a release gate')
add('J4','Connector_Generic:Conn_01x02','BUTTON dry contact',XH2,{1:'BUTTON_EXT',2:'GND'},(77,53,0),4,'JST','B2B-XH-A(LF)(SN)','XH 2.5mm THT')
add('J5','Connector_Generic:Conn_01x02','PASSIVE PIEZO',XH2,{1:'PIEZO_P',2:'PIEZO_N'},(26,54,0),4,'JST','B2B-XH-A(LF)(SN)','XH 2.5mm THT',note='Floating passive piezo only; no magnetic buzzer; two-wire isolated from chassis')
add('J6','Connector_Generic:Conn_01x02','PACK NTC 10k',PH2,{1:'NTC_EXT',2:'GND'},(6,40,270),1,'JST','B2B-PH-K-S(LF)(SN)','PH 2mm THT',note='External Semitec 103AT-2 attached to pack; open cable inhibits charging')
add('SW1','Switch:SW_SPDT','RUN / OFF','Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q',
{1:'VSYS',2:'RUN_EN',3:'GND'},(5,18,270),1,'C&K (Littelfuse)','OS102011MS2QN1','SPDT 2mm THT',note='Only enable current; verify exact switch drawing and cable-free mechanical fit')
# USB: one Rd per CC, upstream fast fuse, high-energy VBUS TVS; charging input is 28V tolerant.
r('R1','5.1k','CC1','GND',(78,5,90),0);r('R2','5.1k','CC2','GND',(78,19,90),0)
add('F1','Device:Fuse','1A fast','Fuse:Fuse_1206_3216Metric',{1:'VBUS_RAW',2:'VBUS'},(76,25,0),0,'Littelfuse','0466001.NRHF','1206')
add('D1','Device:D_TVS','SMBJ6.0A','Diode_SMD:D_SMB',{1:'VBUS',2:'GND'},(81,32,90),0,'Littelfuse','SMBJ6.0A','SMB')
c('C1','1u','VBUS',(25,18,0),1);c('C2','100n','VBUS',(21,18,0),1)
for ref,ns,xy,g in [('D2',('USB_CONN_D+','USB_CONN_D-'),(80,12,0),0),('D3',('CC1','CC2'),(81,19,0),0),('D4',('SCK','MOSI'),(54,47,0),3),('D5',('OLED_RESET_N','OLED_DC'),(45,47,0),3),('D6',('OLED_CS_N','OLED_3V3'),(38,47,0),3),('D7',('BUTTON_EXT','GND'),(80,47,0),4),('D8',('PIEZO_P','PIEZO_N'),(27,47,0),4),('D9',('NTC_EXT','GND'),(10,40,0),1)]:
 add(ref,'custom:TPD2E2U06DCK','TPD2E2U06DCKR','Package_TO_SOT_SMD:SOT-323_SC-70',{1:ns[0],2:ns[1],3:'GND'},xy,g,'Texas Instruments','TPD2E2U06DCKR','SC70-3')
r('R3','22','USB_D+','USB_CONN_D+',(65,7,0),0);r('R4','22','USB_D-','USB_CONN_D-',(65,10,0),0)
c('C17','18p','USB_D+',(62,4,0),0,dnp=True);c('C18','18p','USB_D-',(62,14,0),0,dnp=True)
# Reverse battery: AN-171 fig 7, bidirectional pass path with active reverse detection.
add('F2','Device:Fuse','1A fast','Fuse:Fuse_1206_3216Metric',{1:'PACK_POS',2:'PACK_FUSED'},(11,29,0),1,'Littelfuse','0466001.NRHF','1206')
fet('Q1','P',{1:'BAT_GATE',2:'VBAT',3:'PACK_FUSED'},(16,29,90),1)
fet('Q2','P',{1:'PACK_FUSED',2:'VBAT',3:'BAT_GATE'},(16,35,90),1,mpn='BSS84-7-F')
r('R5','100k','BAT_GATE','GND',(12,35,90),1)
r('R6','1M','PACK_FUSED','VBAT',(21,34,90),1,dnp=True,note='DNP: eliminates DC injection on reverse battery; connect battery before USB, then cycle USB if charge path stays off')
c('C3','22u','VBAT',(18,23,90),1);c('C4','22u','VBAT',(15,23,90),1)
c('C5','22u','VSYS',(27,26,90),1);c('C6','22u','VSYS',(30,26,90),1)
c('C7','22u','VSYS',(41,26,90),1);c('C8','22u','VSYS',(44,26,90),1)
c('C9','22u','3V3_REG',(40,19,90),1);c('C10','22u','3V3_REG',(43,19,90),1)
r('R7','6.19k','ISET','GND',(27,20,90),1,note='143.8mA nominal; 127.5..159.1mA with 1% resistor and KISET limits')
r('R8','3.24k','ILIM','GND',(28,31,90),1,note='Required even in USB mode; programmable mode unused')
r('R9','46.4k','TMR','GND',(24,31,90),1,note='6.19h nominal fast-charge safety timer')
r('R10','100k','CHG_DISABLE','VSYS',(20,29,90),1,note='Default charging DISABLED. Populate R39 only after battery/temperature release')
r('R11','100','NTC_EXT','NTC',(10,44,90),1)
r('R12','10k','NTC','GND',(15,43,90),1,dnp=True,note='BENCH ONLY / NO BATTERY: defeats pack temperature sensing')
r('R13','1M','RUN_EN','GND',(8,23,90),1)
r('R14','0','3V3_REG','3V3',(45,15,0),1,note='Remove for total switched-system current measurement; pads accessible')
# Charge LED uses protected system output; no current during battery-only operation.
r('R15','3.3k','VSYS','CHG_LED_A',(32,35,0),1)
add('D10','Device:LED','CHARGE red','LED_SMD:LED_0805_2012Metric',{1:'CHG_N',2:'CHG_LED_A'},(37,35,0),1,'Kingbright','APT2012EC','0805')
# Module power, straps, reset and boot access.
c('C11','22u','3V3',(37,3,90),2);c('C12','100n','3V3',(37,6,0),2)
r('R16','10k','3V3','RESET_N',(36,10,90),2);c('C13','1u','RESET_N',(32,10,90),2)
r('R17','10k','3V3','BOOT_N',(36,15,0),2)
r('R18','10k','3V3','CS_INVERT',(31,15,0),2)
r('R19','10k','3V3','SUSPEND_N',(63,2,0),2)
r('R20','3.3k','3V3','RUN_LED_A',(68,2,0),2)
add('D11','Device:LED','RUN green active low','LED_SMD:LED_0805_2012Metric',{1:'LED_N',2:'RUN_LED_A'},(72,2,0),2,'Kingbright','APT2012SGC','0805')
r('R21','100k','USB_500','GND',(65,18,90),2);r('R22','100k','USB_SUSPEND','GND',(69,18,90),2,dnp=True,note='Omit: EN2 has internal pulldown; R38 high level checked against 10uA input current')
# SPI: same eight-wire connector convention as current source; MOSFET-isolated CS on strap IO8.
for ref,ns,xy in [('R23',('SCK_BUF','SCK'),(34,4,0)),('R24',('MOSI_BUF','MOSI'),(31,7,0)),('R25',('RES_BUF','OLED_RESET_N'),(28,10,0)),('R26',('DC_BUF','OLED_DC'),(25,13,0))]:r(ref,'220',*ns,xy,3)
fet('Q3','N',{1:'CS_INVERT',2:'GND',3:'OLED_CS_N'},(39,41,0),3)
r('R27','10k','OLED_3V3','OLED_CS_N',(43,41,90),3,note='CS physical low when IO8 is high; firmware must invert CS')
r('R28','100k','OLED_EN','GND',(65,31,90),3)
r('R29','100','OLED_3V3','OLED_DISCHARGE',(62,37,0),3)
c('C14','1u','OLED_3V3',(58,36,0),3)
# High-side gated battery sense: no GPIO injection with RUN switch OFF.
fet('Q4','P',{1:'SENSE_GATE',2:'VBAT',3:'BAT_SAMPLED'},(23,39,0),2,mpn='BSS84-7-F')
fet('Q5','N',{1:'3V3',2:'GND',3:'SENSE_GATE'},(23,44,0),2)
r('R30','1M','VBAT','SENSE_GATE',(27,39,90),2)
r('R31','1M','BAT_SAMPLED','BAT_ADC',(30,42,90),2)
r('R32','330k','BAT_ADC','GND',(34,42,90),2)
c('C16','100n','BAT_ADC',(34,46,90),2)
# Button: IO3 deep-sleep wake, external surge clamp before series resistor.
r('R33','100k','3V3','BUTTON',(72,29,90),4)
r('R34','1k','BUTTON_EXT','BUTTON',(76,41,90),4)
c('C15','100n','BUTTON',(72,36,90),4)
# Passive piezo: current through transistor, bounded by resistors; rail flyback clamp.
fet('Q6','N',{1:'BUZZ_GATE',2:'GND',3:'PIEZO_N'},(19,50,0),4,mpn='DMN2056U-7')
r('R35','100k','BUZZ_GATE','GND',(14,49,90),4)
r('R36','100','3V3','PIEZO_P',(30,50,0),4)
r('R37','1k','PIEZO_P','PIEZO_N',(23,50,90),4)
add('D12','Device:D','BAV19W-7-F','Diode_SMD:D_SOD-123',{1:'PIEZO_P',2:'PIEZO_N'},(23,46,0),4,'Diodes Incorporated','BAV19W-7-F','SOD-123')
for i,(net,xy) in enumerate([('VBUS',(72,24,0)),('VBAT',(10,32,0)),('VSYS',(33,29,0)),('3V3_REG',(46,21,0)),('3V3',(48,16,0)),('GND',(48,20,0)),('RESET_N',(31,4,0)),('BOOT_N',(38,13,0)),('BAT_ADC',(37,46,0)),('USB_GOOD_N',(18,17,0)),('CHG_DISABLE',(20,32,0)),('NTC',(7,46,0)),('GND',(75,22,0)),('GND',(69,47,0)),('BUTTON',(69,40,0)),('ISET',(27,17,0))],1):tp('TP'+str(i),net,xy)
for i,xy in enumerate([(3,3,0),(87,3,0),(3,57,0),(87,57,0)],1):
 add('H'+str(i),'Mechanical:MountingHole','M2','MountingHole:MountingHole_2.2mm_M2',{},xy,5,'PCB fabrication','N/A - mounting hole','NPTH 2.2mm',True,'Do not populate; 5mm screw head keepout')
# GPIO2 strap high holds EN2 low through Q7; UART TX GPIO21 may only flash the LED.
fet('Q7','N',{1:'SUSPEND_N',2:'GND',3:'USB_SUSPEND'},(66,39,0),2)
r('R38','100k','3V3','USB_SUSPEND',(65,44,90),2,note='Q7 inversion: IO2 high=active, IO2 low=USB suspend after EN1 high')
r('R39','0','CHG_DISABLE','GND',(7,50,0),1,dnp=True,note='CHARGE ENABLE option: fit only with independently temperature-protected pack after release checklist')
add('U5','custom:74LVC125A','74LVC125AD,118','Package_SO:SOIC-14_3.9x8.7mm_P1.27mm',{1:'GND',2:'SCK_M',3:'SCK_BUF',4:'GND',5:'MOSI_M',6:'MOSI_BUF',7:'GND',8:'RES_BUF',9:'RES_M',10:'GND',11:'DC_BUF',12:'DC_M',13:'GND',14:'OLED_3V3'},(49,29,0),3,'Nexperia','74LVC125AD,118','SOIC-14',note='Ioff isolation with OLED rail OFF; no boot backfeed through SPI inputs')
c('C19','100n','OLED_3V3',(55.5,23,0),3)
NETS={}
for ref,d in C.items():
 for pin,net in d['pins'].items():
  if net is not None:NETS.setdefault(net,[]).append((ref,pin))

# Placement refinements from KiCad courtyard and pad-clearance checks.
for ref,xy in {'TP11':(19,37,0),'TP10':(18,15,0),'C11':(37,2.5,90),'C12':(36,6.5,0),'R14':(46,17,0),'TP5':(52,18,0),'TP4':(48,23,0),'TP6':(52,23,0),'TP8':(40,16,0),'TP7':(31,1.7,0),'R37':(22,50,0),'TP16':(23,15,0),'C1':(25,16,0),'TP9':(36,50,0),'Q5':(20,41,0),'D12':(21,45,0)}.items():C[ref]['xy']=xy
for ref,xy in {'C11':(37,3,90),'TP8':(34,18,0),'TP16':(30,17,0),'Q5':(18,40,0),'R37':(33,53,90)}.items():C[ref]['xy']=xy
for ref,xy in {'R3':(61.5,6.75,0),'R4':(61.5,8.5,0),'C17':(64.5,4.25,0),'C18':(64,13,0)}.items():C[ref]['xy']=xy

for ref,xy in {'R3':(62,6.5,0),'R4':(62,8.75,0),'TP16':(29.5,18.5,0)}.items():C[ref]['xy']=xy

C['D2']['xy']=(79,14.3,0)

C['TP15']['xy']=(70,42,0)

C['R13']['xy']=(9.5,23,90)
C['C7']['xy']=(41,26,270)

for ref in ['C17','C18']:C[ref]['mfr']='KEMET (Yageo)'

for ref,xy in {'R23':(43.5,30.5,0),'R24':(45,34,0),'R25':(55.5,26,0),'R26':(55.5,30,0)}.items():C[ref]['xy']=xy

C['R23']['xy']=(42.8,30.5,0)
C['R24']['xy']=(44,35.5,0)
