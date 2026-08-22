# -*- coding: utf-8 -*-
"""Zentrale Entwurfsdaten: Bauteile und Netzliste.
Einzige Wahrheitsquelle fuer Schaltplan und Layout."""

SYMLIB = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols'
FPLIB  = '/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints'

R0805 = 'Resistor_SMD:R_0805_2012Metric_Pad1.20x1.40mm_HandSolder'
C0805 = 'Capacitor_SMD:C_0805_2012Metric_Pad1.18x1.45mm_HandSolder'
L0805 = 'LED_SMD:LED_0805_2012Metric_Pad1.15x1.40mm_HandSolder'
SOT5  = 'Package_TO_SOT_SMD:SOT-23-5_HandSoldering'
SOT6  = 'Package_TO_SOT_SMD:SOT-23-6_Handsoldering'
TP    = 'TestPoint:TestPoint_Pad_D1.5mm'

# ref -> (symbol_libid, value, footprint, datasheet-ish description)
COMPONENTS = {
 'U1': ('RF_Module:ESP32-C3-WROOM-02', 'ESP32-C3-WROOM-02-N4',
        'flappy:ESP32-C3-WROOM-02_HandSolder', 'Funkmodul, RISC-V, WLAN/BLE, USB-Serial-JTAG'),
 'U2': ('Battery_Management:MCP73831-2-OT', 'MCP73831-2-OT', SOT5, 'LiPo-Laderegler 4,20 V'),
 'U3': ('Regulator_Linear:AP2112K-3.3', 'AP2112K-3.3', SOT5, 'LDO 3,3 V / 600 mA'),
 'D1': ('Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', SOT6, 'ESD-Schutzarray USB'),
 'D2': ('Device:LED', 'LED rot', L0805, 'Ladeanzeige'),
 'D3': ('Device:D_Schottky', 'B5819W', 'Diode_SMD:D_SOD-123', 'Verpolungsschutz (Crowbar)'),
 'D4': ('Device:LED', 'LED gruen', L0805, 'Betriebsanzeige, GPIO-gesteuert'),
 'F1': ('Device:Polyfuse', '500 mA PTC', R0805, 'Rueckstellsicherung Akkupfad'),
 'SW1':('Switch:SW_SPDT', 'Ein/Aus', 'Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q', 'Schiebeschalter SPDT'),
 'LS1':('Device:Buzzer', 'Piezo 12 mm', 'Buzzer_Beeper:Buzzer_12x9.5RM7.6', 'passiver Schallwandler'),
 'J1': ('Connector_Generic:Conn_01x06', 'USB-C-Breakout 16P',
        'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 'VBUS/GND/D-/D+/CC1/CC2'),
 'J2': ('Connector_Generic:Conn_01x02', 'LiPo 1S 500 mAh',
        'Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical', 'Akkubuchse JST-PH'),
 'J3': ('Connector_Generic:Conn_01x07', 'OLED SSD1306 SPI',
        'Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical', 'Displaykabel JST-XH 7-polig'),
 'J4': ('Connector_Generic:Conn_01x02', 'Arcade-Taster',
        'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical', 'Tasterkabel JST-XH 2-polig'),
 'R1': ('Device:R', '6k8',  R0805, 'R_prog -> I_chg = 147 mA'),
 'R2': ('Device:R', '1k',   R0805, 'Vorwiderstand Lade-LED'),
 'R3': ('Device:R', '0R',   R0805, 'Trennstelle Strommessung Modul (M3)'),
 'R4': ('Device:R', '10k',  R0805, 'Pull-up EN'),
 'R5': ('Device:R', '68R',  R0805, 'Serienterminierung SCLK'),
 'R6': ('Device:R', '68R',  R0805, 'Serienterminierung MOSI'),
 'R7': ('Device:R', '68R',  R0805, 'Serienterminierung RES'),
 'R8': ('Device:R', '68R',  R0805, 'Serienterminierung DC'),
 'R9': ('Device:R', '68R',  R0805, 'Serienterminierung CS'),
 'R10':('Device:R', '10k',  R0805, 'Pull-up Taster, tau = 1,0 ms'),
 'R11':('Device:R', '100R', R0805, 'Entladestrombegrenzung Tasterkontakt'),
 'R12':('Device:R', '220R', R0805, 'ESD-Strombegrenzung am Steckverbinder'),
 'R13':('Device:R', '220R', R0805, 'Strombegrenzung Piezo: 3,3 V / 220 R = 15 mA < 28 mA (I_OL)'),
 'R14':('Device:R', '1k',   R0805, 'Vorwiderstand Betriebs-LED'),
 'R15':('Device:R', '10k',  R0805, 'Pull-up Strapping IO2'),
 'R16':('Device:R', '10k',  R0805, 'Pull-up Strapping IO8'),
 'C1': ('Device:C', '4u7',  C0805, 'Eingangskondensator VBUS'),
 'C2': ('Device:C', '100n', C0805, 'HF-Abblockung VBUS'),
 'C3': ('Device:C', '4u7',  C0805, 'Ausgangskondensator Laderegler'),
 'C4': ('Device:C', '100n', C0805, 'HF-Abblockung VBAT'),
 'C5': ('Device:C', '1u',   C0805, 'Eingangskondensator LDO'),
 'C6': ('Device:C', '22u',  C0805, 'Ausgangskondensator LDO (5.4)'),
 'C7': ('Device:C', '100n', C0805, 'HF-Abblockung 3V3'),
 'C8': ('Device:C', '10u',  C0805, 'Stuetzkondensator am Modul (5.4)'),
 'C9': ('Device:C', '100n', C0805, 'HF-Abblockung am Modul'),
 'C10':('Device:C', '100n', C0805, 'Reset-Zeitkonstante EN'),
 'C11':('Device:C', '100n', C0805, 'Entprellkondensator Taster'),
 'TP1':('Connector:TestPoint','VBUS',    TP, 'Pruefpunkt'),
 'TP2':('Connector:TestPoint','VBAT',    TP, 'Pruefpunkt'),
 'TP3':('Connector:TestPoint','3V3',     TP, 'Pruefpunkt'),
 'TP4':('Connector:TestPoint','3V3_MCU', TP, 'Pruefpunkt'),
 'TP5':('Connector:TestPoint','BTN',     TP, 'Pruefpunkt Tasterknoten (M1)'),
 'TP6':('Connector:TestPoint','EN',      TP, 'Pruefpunkt Reset'),
 'TP7':('Connector:TestPoint','BOOT',    TP, 'Pruefpunkt IO9 Downloadmodus'),
 'TP10':('Connector:TestPoint','GND',    TP, 'Massepunkt Tastkopf'),
 'TP11':('Connector:TestPoint','GND',    TP, 'Massepunkt Tastkopf'),
 'TP12':('Connector:TestPoint','GND',    TP, 'Massepunkt Tastkopf'),
 'H1': ('Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', 'Befestigung'),
 'H2': ('Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', 'Befestigung'),
 'H3': ('Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', 'Befestigung'),
 'H4': ('Mechanical:MountingHole', 'M2', 'MountingHole:MountingHole_2.2mm_M2', 'Befestigung'),
}

# Netzname -> Liste von (Referenz, Pin-Nummer)
NETS = {
 'GND': [('J1','2'),('D1','2'),('C1','2'),('C2','2'),('U2','2'),('C3','2'),('C4','2'),
         ('R1','2'),('J2','2'),('D3','2'),('C5','2'),('U3','2'),('C6','2'),('C7','2'),
         ('C8','2'),('C9','2'),('U1','9'),('U1','19'),('C10','2'),('J3','1'),('C11','2'),
         ('J4','2'),('LS1','2'),('D4','1'),('TP10','1'),('TP11','1'),('TP12','1')],
 'VBUS':      [('J1','1'),('D1','5'),('C1','1'),('C2','1'),('U2','4'),('R2','1'),('TP1','1')],
 'USB_DP_CON':[('J1','4'),('D1','3')],
 'USB_DM_CON':[('J1','3'),('D1','1')],
 'USB_DP':    [('D1','4'),('U1','14')],   # IO19
 'USB_DM':    [('D1','6'),('U1','13')],   # IO18
 'PROG':      [('U2','5'),('R1','1')],
 'CHG_A':     [('R2','2'),('D2','2')],
 'LED_CHG':   [('D2','1'),('U2','1')],
 'VBAT':      [('U2','3'),('C3','1'),('C4','1'),('F1','2'),('D3','1'),('SW1','2'),('TP2','1')],
 'BATT_P':    [('J2','1'),('F1','1')],
 'VBAT_SW':   [('SW1','1'),('U3','1'),('U3','3'),('C5','1')],
 '+3V3':      [('U3','5'),('C6','1'),('C7','1'),('R3','1'),('TP3','1'),('J3','2')],
 '+3V3_MCU':  [('R3','2'),('C8','1'),('C9','1'),('U1','1'),('R4','2'),
               ('R10','1'),('R15','1'),('R16','1'),('TP4','1')],
 'EN':        [('U1','2'),('R4','1'),('C10','1'),('TP6','1')],
 'SCLK_MCU':  [('U1','3'),('R5','1')],    # IO4
 'SCLK':      [('R5','2'),('J3','3')],
 'MOSI_MCU':  [('U1','4'),('R6','1')],    # IO5
 'MOSI':      [('R6','2'),('J3','4')],
 'OLED_RES_MCU':[('U1','5'),('R7','1')],  # IO6
 'OLED_RES':  [('R7','2'),('J3','5')],
 'OLED_DC_MCU':[('U1','6'),('R8','1')],   # IO7
 'OLED_DC':   [('R8','2'),('J3','6')],
 'OLED_CS_MCU':[('U1','7'),('R9','1'),('R16','2')],  # IO8, mit Pull-up fuer den Bootzustand
 'OLED_CS':   [('R9','2'),('J3','7')],
 'BOOT':      [('U1','8'),('TP7','1')],   # IO9
 'IO2':       [('U1','16'),('R15','2')],
 'BTN':       [('U1','15'),('R10','2'),('C11','1'),('R11','1'),('TP5','1')],  # IO3
 'BTN_SW':    [('R11','2'),('R12','1')],
 'BTN_CON':   [('R12','2'),('J4','1')],
 'BUZZ':      [('U1','17'),('R13','1')],  # IO1
 'BUZZ_P':    [('R13','2'),('LS1','1')],
 'LED_G':     [('U1','18'),('R14','1')],  # IO0
 'LED_G_A':   [('R14','2'),('D4','2')],
}

# Pins ohne Netz -> No-Connect-Markierung im Schaltplan
NO_CONNECT = [('U3','4'), ('SW1','3'), ('J1','5'), ('J1','6'),
              ('U1','10'), ('U1','11'), ('U1','12')]   # IO10, RXD, TXD frei

# Netze, die als reine "nicht angeschlossen"-Pads gelten (nur ein Pin)
SINGLE_PIN_OK = []

POWER_NETS = {'GND':'GND', 'VBUS':'VBUS', 'VBAT':'VBAT', 'VBAT_SW':'VBAT_SW',
              '+3V3':'+3V3', '+3V3_MCU':'+3V3_MCU'}
