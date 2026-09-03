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
 'U2': ('Battery_Management:MCP73831-2-OT', 'MCP73831T-2ACI/OT', SOT5, 'LiPo-Laderegler 4,20 V, 10 % Vorkond., 7,5 % Abschaltung'),
 'U3': ('Regulator_Linear:AP2112K-3.3', 'AP2112K-3.3', SOT5, 'LDO 3,3 V / 600 mA'),
 'D1': ('Power_Protection:USBLC6-2SC6', 'USBLC6-2SC6', SOT6, 'ESD-Schutzarray USB'),
 'D2': ('Device:LED', 'LED rot', L0805, 'Ladeanzeige'),
 'D3': ('Device:D_Schottky', 'B5819W', 'Diode_SMD:D_SOD-123', 'Verpolungsschutz (Crowbar)'),
 'D4': ('Device:LED', 'LED gruen', L0805, 'Betriebsanzeige, GPIO-gesteuert'),
 'F1': ('Device:Polyfuse', '500 mA PTC', R0805, 'Rueckstellsicherung Akkupfad'),
 'SW1':('Switch:SW_SPDT', 'Ein/Aus', 'Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q', 'Schiebeschalter SPDT'),
 'J1': ('Connector_Generic:Conn_01x06', 'USB-C-Breakout 16P',
        'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical', 'VBUS/GND/D-/D+/CC1/CC2'),
 'J2': ('Connector_Generic:Conn_01x02', 'LiPo 1S 500 mAh',
        'Connector_JST:JST_PH_B2B-PH-K_1x02_P2.00mm_Vertical', 'Akkubuchse JST-PH'),
 'J3': ('Connector_Generic:Conn_01x07', 'OLED SSD1306 SPI',
        'Connector_JST:JST_XH_B7B-XH-A_1x07_P2.50mm_Vertical', 'Displaykabel JST-XH 7-polig'),
 'J4': ('Connector_Generic:Conn_01x02', 'Arcade-Taster',
        'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical', 'Tasterkabel JST-XH 2-polig'),
 # Befund K-1: Der CEP-1114 ist laut Datenblatt (Maßzeichnung S. 2) 30,0 mm im
 # Durchmesser mit 20,0 mm Rastermass - er passt auf keinen 12-mm-Footprint und
 # nicht auf diese Platine. Der Wandler wird deshalb wie Display und Taster
 # abgesetzt am Kabel montiert; auf der Platine sitzt nur die Buchse.
 'J5': ('Connector_Generic:Conn_01x02', 'Piezo CEP-1114',
        'Connector_JST:JST_XH_B2B-XH-A_1x02_P2.50mm_Vertical', 'Buzzerkabel JST-XH 2-polig'),
 'R1': ('Device:R', '6k8',  R0805, 'R_prog -> I_chg = 147 mA'),
 'R2': ('Device:R', '560R', R0805, 'Vorwiderstand Lade-LED: (5,0-1,8-0,4)/560 = 5,0 mA'),
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
 'R14':('Device:R', '330R', R0805, 'Vorwiderstand Betriebs-LED: (3,3-1,95)/330 = 4,1 mA'),
 'R15':('Device:R', '10k',  R0805, 'Pull-up Strapping IO2'),
 'R16':('Device:R', '10k',  R0805, 'Pull-up Strapping IO8'),
 'R17':('Device:R', '5k1',  R0805, 'NICHT BESTUECKEN (DNP) - Pull-down CC1, nur wenn Breakout ohne Rd'),
 'R18':('Device:R', '5k1',  R0805, 'NICHT BESTUECKEN (DNP) - Pull-down CC2, nur wenn Breakout ohne Rd'),
 'C1': ('Device:C', '4u7 25V X7R', C0805, 'Eingangskondensator VBUS (VBUS 5,25 V -> >= 2x Derating)'),
 'C2': ('Device:C', '100n 50V X7R', C0805, 'HF-Abblockung VBUS'),
 'C3': ('Device:C', '10u 25V X7R', C0805, 'Ausgangskondensator Laderegler: >= 4,7 uF wirksam bei 4,2 V'),
 'C4': ('Device:C', '100n 50V X7R', C0805, 'HF-Abblockung VBAT'),
 'C5': ('Device:C', '2u2 16V X7R', C0805, 'Eingangskondensator LDO: >= 1 uF wirksam bei 4,2 V'),
 'C6': ('Device:C', '22u 10V X5R', C0805, 'Ausgangskondensator LDO (5.4)'),
 'C7': ('Device:C', '100n 50V X7R', C0805, 'HF-Abblockung 3V3'),
 'C8': ('Device:C', '10u 16V X7R', C0805, 'Stuetzkondensator am Modul (5.4)'),
 'C9': ('Device:C', '100n 50V X7R', C0805, 'HF-Abblockung am Modul'),
 'C10':('Device:C', '100n 50V X7R', C0805, 'Reset-Zeitkonstante EN'),
 'C11':('Device:C', '100n 50V X7R', C0805, 'Entprellkondensator Taster'),
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
         ('J4','2'),('J5','2'),('D4','1'),('TP10','1'),('TP11','1'),('TP12','1'),
         ('R17','2'),('R18','2')],
 'VBUS':      [('J1','1'),('D1','5'),('C1','1'),('C2','1'),('U2','4'),('R2','1'),('TP1','1')],
 'USB_DP_CON':[('J1','4'),('D1','3')],
 'USB_DM_CON':[('J1','3'),('D1','1')],
 'USB_CC1':   [('J1','5'),('R17','1')],
 'USB_CC2':   [('J1','6'),('R18','1')],
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
 'BUZZ_P':    [('R13','2'),('J5','1')],
 'LED_G':     [('U1','18'),('R14','1')],  # IO0
 'LED_G_A':   [('R14','2'),('D4','2')],
}

# Pins ohne Netz -> No-Connect-Markierung im Schaltplan
NO_CONNECT = [('U3','4'), ('SW1','3'),
              ('U1','10'), ('U1','11'), ('U1','12')]   # IO10, RXD, TXD frei

# Netze, die als reine "nicht angeschlossen"-Pads gelten (nur ein Pin)
SINGLE_PIN_OK = []

POWER_NETS = {'GND':'GND', 'VBUS':'VBUS', 'VBAT':'VBAT', 'VBAT_SW':'VBAT_SW',
              '+3V3':'+3V3', '+3V3_MCU':'+3V3_MCU'}

# =====================================================================
#  Bestueckungsvarianten (Befund K-2)
# =====================================================================
# USB-C-Senke: Rd = 5,1 kOhm je CC-Leitung ist fuer eine UFP korrekt - aber nur
# EINMAL im Pfad. Bringt das aufgesteckte Breakout eigene Pull-downs mit (die
# grosse Mehrheit tut das), liegen 5k1 || 5k1 = 2,55 kOhm an CC:
#
#   Quelle "Default USB Power" (80 uA):  V_CC = 80 uA * 2550 R = 0,204 V
#   vRa_max = 0,20 V  <  0,204 V  <  vRd-Connect_min = 0,25 V
#   -> Totzone der Quellenerkennung, VBUS wird u. U. nie eingeschaltet.
#   Quelle 3,0 A mit Rp -20 %:  264 uA * 2550 R = 0,673 V < 0,80 V -> ebenfalls
#   nicht als Senke erkannt.
#
# Deshalb sind R17/R18 ab Werk NICHT bestueckt. Sie werden nur eingeloetet, wenn
# das Breakout nachweislich keine eigenen 5k1 hat. Ein fehlendes Rd faellt sofort
# auf (kein Laden), ein doppeltes Rd erzeugt einen sporadischen Feldfehler.
DNP = {'R17', 'R18'}

# =====================================================================
#  Datenblattbelege (Befund K-4)
# =====================================================================
# ref -> (Dateiname in doc/datenblaetter, Kennung, die auf Seite 1 stehen muss)
# oder None mit Begruendung, wenn der Beleg fehlt. Prueflauf T12 vergleicht den
# Inhalt der PDF gegen die Kennung - ein falsch abgelegtes Datenblatt kann so
# nicht mehr unbemerkt als Nachweis durchgehen.
DATENBLATT = {
 'U1': ('U1_ESP32-C3-WROOM-02-N4_Espressif.pdf',     'ESP32-C3-WROOM-02'),
 'U2': ('U2_MCP73831-2-OT_Microchip.pdf',            'MCP73831'),
 'U3': ('U3_AP2112K-3.3_DiodesInc.pdf',              'AP2112'),
 'D1': ('D1_USBLC6-2SC6_STMicroelectronics.pdf',     'USBLC6-2'),
 'D2': ('D2_LED-0805-Rot_Kingbright-APT2012EC.pdf',  'APT2012EC'),
 'D4': ('D4_LED-0805-Gruen_Kingbright-APT2012SGC.pdf','APT2012SGC'),
 'F1': ('F1_MF-PSMF050X-2_500mA-PTC_Bourns.pdf',     'MF-PSMF'),
 'SW1':('SW1_OS102011MS2Q_CK-Littelfuse.pdf',        'OS Series'),
 'J1': ('J1_PinHeader-1x06-P2.54mm_Wuerth-61300611121.pdf', None),
 'J2': ('J2_JST-PH_B2B-PH-K_JST.pdf',                'PH'),
 'J3': ('J3_J4_JST-XH_B7B-XH-A_B2B-XH-A_JST.pdf',    'XH'),
 'J4': ('J3_J4_JST-XH_B7B-XH-A_B2B-XH-A_JST.pdf',    'XH'),
 'J5': ('J3_J4_JST-XH_B7B-XH-A_B2B-XH-A_JST.pdf',    'XH'),
 # Der Piezo selbst sitzt am Kabel und ist kein Platinenbauteil mehr (K-1),
 # sein Beleg bleibt aber Teil der Dokumentation.
 'LS1_extern': ('LS1_CEP-1114_Piezo-Buzzer-12mm-RM7.6_CUIDevices.pdf', 'CEP-1114'),
}

# Bauteile ohne gueltigen Beleg - jede Zeile ist eine offene Beschaffungsaufgabe
# und wird bei jedem Prueflauf ausgegeben.
BELEG_FEHLT = {
 'D3': 'B5819W: die Datei D3_B5819W_DiodesInc.pdf enthielt das Datenblatt der '
       '1N4148WS/BAV16WS (SOD-323, I_FM = 300 mA) und war damit kein Nachweis '
       'fuer die Schottky-Diode. Sie ist auf ihren wahren Inhalt umbenannt; das '
       'echte B5819W-Datenblatt (SOD-123) muss noch abgelegt werden.',
 'C1':  'MLCC: die abgelegte Reihe Vishay VJ Commercial fuehrt in 0805 nur bis '
        '470 nF X7R. Fuer 2u2/4u7/10u/22u ist ein Datenblatt der tatsaechlich '
        'beschafften Reihe (z. B. Murata GRM21) mit DC-Bias-Kurve noetig.',
 'R1':  'Dickschichtwiderstaende: Vishay CRCW0805 ist abgelegt, die Toleranz '
        '(1 %) muss noch je Position in die Bestellung uebernommen werden.',
}
