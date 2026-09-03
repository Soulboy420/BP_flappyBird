# -*- coding: utf-8 -*-
"""Platzierung der Symbole und Drahtfuehrung im Schaltplan (A3, 420 x 297 mm).
Alle Koordinaten sind Vielfache von 1,27 mm (KiCad-Standardraster)."""

# ref -> (x, y, rotation, mirror)
PLACE = {
    # --- A  USB-Anschluss und ESD-Schutz -------------------------------------
    'J1':  (320.04,  45.72,   0, 'y'),
    'D1':  (368.30,  45.72,   0, None),
    'R17': (331.47,  50.80,  90, None),
    'R18': (331.47,  53.34,  90, None),
    # --- B  Ladeschaltung -----------------------------------------------------
    'TP1': (302.26, 107.95, 180, None),
    'C1':  (313.69, 107.95,   0, None),
    'C2':  (325.12, 107.95,   0, None),
    'R2':  (337.82, 107.95,   0, None),
    'D2':  (337.82, 118.11,  90, None),
    'U2':  (368.30, 113.03,   0, None),
    'R1':  (358.14, 124.46,   0, None),
    'TP2': (392.43, 100.33, 180, None),
    'C3':  (392.43, 118.11,   0, None),
    'C4':  (403.86, 118.11,   0, None),
    # --- C  Akku, Verpolungsschutz, Ein/Aus-Schalter ---------------------------
    'J2':  (321.31, 173.99,   0, 'y'),
    'F1':  (342.90, 173.99,  90, None),
    'D3':  (355.60, 180.34, 270, None),
    'SW1': (392.43, 173.99,   0, None),
    # --- D  Spannungsregler 3,3 V ---------------------------------------------
    'C5':  (322.58, 232.41,   0, None),
    'U3':  (350.52, 231.14,   0, None),
    'TP3': (365.76, 222.25,   0, None),
    'C6':  (373.38, 232.41,   0, None),
    'C7':  (383.54, 232.41,   0, None),
    # --- E  Mikrocontroller ----------------------------------------------------
    'U1':  (245.11, 106.68,   0, None),
    'R3':  (245.11,  60.96,   0, None),
    'TP4': (205.74,  58.42,   0, None),
    'C8':  (215.90,  71.12,   0, None),
    'C9':  (226.06,  71.12,   0, None),
    'R4':  (223.52,  81.28, 180, None),
    'TP6': (203.20,  88.90,  90, None),
    'C10': (210.82,  92.71,   0, None),
    'R15': (223.52,  99.06,  90, None),
    'R16': (203.20, 133.35,  90, None),
    'TP7': (219.71, 116.84,  90, None),
    # --- F  Displayanbindung ---------------------------------------------------
    'R5':  (120.65,  63.50,  90, None),
    'R6':  (120.65,  68.58,  90, None),
    'R7':  (120.65,  73.66,  90, None),
    'R8':  (120.65,  78.74,  90, None),
    'R9':  (120.65,  83.82,  90, None),
    'J3':  (140.97,  69.85,   0, None),
    # --- G  Tastereingabe ------------------------------------------------------
    'R10': ( 63.50, 138.43,   0, None),
    'TP5': ( 55.88, 140.97,   0, None),
    'C11': ( 76.20, 149.86,   0, None),
    'R11': ( 95.25, 146.05,  90, None),
    'R12': (110.49, 146.05,  90, None),
    'J4':  (127.00, 146.05,   0, None),
    # --- H  Tonausgabe und Anzeigen -------------------------------------------
    'R13': ( 53.34, 205.74,  90, None),
    'J5':  ( 69.85, 205.74,   0, None),
    'R14': ( 53.34, 222.25,  90, None),
    'D4':  ( 68.58, 222.25, 180, None),
    'TP10':(146.05, 205.74,   0, None),
    'TP11':(146.05, 215.90,   0, None),
    'TP12':(146.05, 226.06,   0, None),
    # --- Bohrungen (nur Stueckliste) -------------------------------------------
    'H1':  ( 30.48, 262.89,   0, None),
    'H2':  ( 45.72, 262.89,   0, None),
    'H3':  ( 60.96, 262.89,   0, None),
    'H4':  ( 76.20, 262.89,   0, None),
}

# Drahtzuege: Liste von Pfaden. Ein Pfad ist eine Liste aus
#   ('ref','pin')  -> Pinkoordinate      oder   (x, y) -> fester Punkt
WIRES = [
    # --- A: USB-Breakout -> ESD-Array -> Mikrocontroller ----------------------
    [('J1', '3'), ('D1', '1')],                      # USB_DM_CON
    [('J1', '4'), ('D1', '3')],                      # USB_DP_CON
    [('J1', '5'), ('R17', '1')],                     # USB_CC1
    [('J1', '6'), ('R18', '1')],                     # USB_CC2
    [('D1', '6'), (381.00, 45.72)],                  # USB_DM  -> Bezeichner
    [('D1', '4'), (381.00, 48.26)],                  # USB_DP  -> Bezeichner
    # --- B: Ladeschaltung -----------------------------------------------------
    [('TP1', '1'), (302.26, 102.87)],                # VBUS-Pruefpunkt
    [('U2', '5'), ('R1', '1')],                      # PROG
    [('R2', '2'), ('D2', '2')],                      # CHG_A
    [('D2', '1'), (337.82, 133.35), (378.46, 133.35), ('U2', '1')],   # LED_CHG
    [('TP2', '1'), (392.43, 95.25)],                 # VBAT-Pruefpunkt
    # --- C: Akku und Verpolungsschutz -----------------------------------------
    [('J2', '1'), ('F1', '1')],                      # BATT_P
    # --- D: Spannungsregler ----------------------------------------------------
    [('U3', '1'), (316.23, 228.60)],                 # VBAT_SW-Knoten (ueber C5)
    [('U3', '3'), (334.01, 231.14), (334.01, 228.60)],
    [('U3', '5'), (392.43, 228.60)],                 # +3V3-Knoten (ueber C6, C7)
    [('TP3', '1'), (365.76, 228.60)],
    # --- E: Modulbeschaltung ---------------------------------------------------
    [('R3', '2'), ('U1', '1')],                      # +3V3_MCU -> Modul
    [('TP4', '1'), (205.74, 66.04), (245.11, 66.04)],
    [('C8', '1'), (215.90, 66.04)],
    [('C9', '1'), (226.06, 66.04)],
    [(236.22, 66.04), (236.22, 60.96)],
    [('R4', '1'), (223.52, 88.90), ('TP6', '1')],    # EN
    [(223.52, 88.90), ('U1', '2')],
    [('C10','1'), (210.82, 88.90)],
    [('R15','2'), ('U1', '16')],                     # IO2
    [('R16','2'), (212.09, 133.35)],                 # Pull-up an OLED_CS_MCU
    [('TP7','1'), ('U1', '8')],                      # BOOT (IO9)
    # --- F: Serienterminierung -> Displaysteckverbinder ------------------------
    [('R5', '2'), (125.73, 63.50), (125.73, 67.31), ('J3', '3')],
    [('R6', '2'), (127.00, 68.58), (127.00, 69.85), ('J3', '4')],
    [('R7', '2'), (128.27, 73.66), (128.27, 72.39), ('J3', '5')],
    [('R8', '2'), (129.54, 78.74), (129.54, 74.93), ('J3', '6')],
    [('R9', '2'), (130.81, 83.82), (130.81, 77.47), ('J3', '7')],
    [('R5', '1'), (104.14, 63.50)],
    [('R6', '1'), (104.14, 68.58)],
    [('R7', '1'), (104.14, 73.66)],
    [('R8', '1'), (104.14, 78.74)],
    [('R9', '1'), (104.14, 83.82)],
    # --- G: Tastereingabe ------------------------------------------------------
    [( 44.45, 146.05), ('R11', '1')],                # BTN-Knoten
    [('R10','2'), ( 63.50, 146.05)],
    [('C11','1'), ( 76.20, 146.05)],
    [('TP5','1'), ( 55.88, 146.05)],
    [('R11','2'), ('R12', '1')],                     # BTN_SW
    [('R12','2'), ('J4',  '1')],                     # BTN_CON
    # --- H: Ton und Anzeigen ---------------------------------------------------
    [( 41.91, 205.74), ('R13', '1')],                # BUZZ
    [('R13','2'), ( 62.23, 205.74), ( 62.23, 203.20), ('J5', '1')],
    [( 41.91, 222.25), ('R14', '1')],                # LED_G
    [('R14','2'), ('D4',  '2')],                     # LED_G_A
    # --- Netzflaggen -----------------------------------------------------------
    [(196.85, 262.89), (196.85, 257.81)],
    [(215.90, 262.89), (215.90, 257.81)],
    [(254.00, 262.89), (254.00, 257.81)],
    [(273.05, 262.89), (273.05, 257.81)],
]

# zusaetzliche Versorgungssymbole an freien Drahtenden: (netz, x, y, richtung)
EXTRA_POWER = [
    ('+3V3_MCU', 236.22,  60.96, 'up'),
    ('VBUS',     302.26, 102.87, 'up'),
    ('VBAT',     392.43,  95.25, 'up'),
    ('VBAT_SW',  316.23, 228.60, 'left'),
    ('+3V3',     392.43, 228.60, 'right'),
    ('GND',      196.85, 262.89, 'down'),
    ('VBUS',     215.90, 257.81, 'up'),
    ('VBAT_SW',  254.00, 257.81, 'up'),
    ('+3V3_MCU', 273.05, 257.81, 'up'),
]

# Netzflaggen (PWR_FLAG): (x, y, richtung des Symbols)
PWR_FLAGS = [
    (196.85, 257.81, 'up'),
    (215.90, 262.89, 'down'),
    (254.00, 262.89, 'down'),
    (273.05, 262.89, 'down'),
]

# Globale Bezeichner: (netz, x, y, rotation, form)
LABELS = [
    ('USB_DM', 381.00,  45.72,   0, 'output'),
    ('USB_DP', 381.00,  48.26,   0, 'output'),
    ('SCLK_MCU', 104.14, 63.50, 180, 'input'),
    ('MOSI_MCU', 104.14, 68.58, 180, 'input'),
    ('OLED_RES_MCU', 104.14, 73.66, 180, 'input'),
    ('OLED_DC_MCU', 104.14, 78.74, 180, 'input'),
    ('OLED_CS_MCU', 104.14, 83.82, 180, 'input'),
    ('BTN',   44.45, 146.05, 180, 'input'),
    ('BUZZ',  41.91, 205.74, 180, 'input'),
    ('LED_G', 41.91, 222.25, 180, 'input'),
    ('OLED_CS_MCU', 212.09, 133.35, 0, 'input'),
]

# Pins des Mikrocontrollers, die nur ueber einen Stichleitungs-Bezeichner gehen
# ref, pin, laenge, netzname
STUB_LABELS = [
    ('U1', '14', 15.24, 'USB_DP'),
    ('U1', '13', 15.24, 'USB_DM'),
    ('U1', '3',  15.24, 'SCLK_MCU'),
    ('U1', '4',  15.24, 'MOSI_MCU'),
    ('U1', '5',  15.24, 'OLED_RES_MCU'),
    ('U1', '6',  15.24, 'OLED_DC_MCU'),
    ('U1', '7',  15.24, 'OLED_CS_MCU'),
    ('U1', '15', 15.24, 'BTN'),
    ('U1', '17', 15.24, 'BUZZ'),
    ('U1', '18', 15.24, 'LED_G'),
]

# Rahmen: (x1, y1, x2, y2, titel)
FRAMES = [
    ( 20.32,  30.48, 172.72, 100.33, 'F  Displayanbindung: Serienterminierung 68 R + JST-XH 7-polig'),
    ( 20.32, 116.84, 172.72, 172.72, 'G  Tastereingabe: Entprellung, ESD-Begrenzung, JST-XH 2-polig'),
    ( 20.32, 186.69, 172.72, 245.11, 'H  Tonausgabe (JST-XH 2-polig), Betriebsanzeige, Pruefpunkte'),
    (185.42,  40.64, 302.26, 140.97, 'E  Mikrocontroller ESP32-C3-WROOM-02-N4'),
    (185.42, 246.38, 302.26, 271.78, 'Netzflaggen (nur fuer die ERC-Pruefung)'),
    (297.18,  20.32, 415.29,  71.12, 'A  USB-Anschluss und ESD-Schutz'),
    (297.18,  90.17, 415.29, 154.94, 'B  Ladeschaltung MCP73831, I_chg = 147 mA'),
    (297.18, 158.75, 415.29, 205.74, 'C  Akku, Verpolungsschutz, Ein/Aus-Schalter'),
    (297.18, 209.55, 415.29, 254.00, 'D  Spannungsregler AP2112K-3.3'),
]

# freie Beschriftungen: (text, x, y, groesse)
NOTES = [
    ('R5..R9: unmittelbar am Mikrocontroller, nicht am Steckverbinder (5.7)', 24.13, 92.71, 1.27),
    ('Z0 ca. 120 R (Flachbandkabel) - R_aus ca. 40 R  ->  68 R (E12)', 24.13, 95.25, 1.27),
    ('Aderfolge des Moduls: GND, VCC, D0=SCLK, D1=MOSI, RES, DC, CS', 24.13, 88.90, 1.27),
    ('tau = R10 * C11 = 10 k * 100 n = 1,0 ms;  Sperrzeit in Software 20 ms', 24.13, 160.02, 1.27),
    ('R11 + R12 begrenzen den Kontaktstrom auf 3,3 V / 320 R = 10 mA', 24.13, 162.56, 1.27),
    ('R12 zusaetzlich als ESD-Strombegrenzung am Steckverbinder', 24.13, 165.10, 1.27),
    ('LS1 (CEP-1114) ist D30 mm / RM 20 mm und sitzt abgesetzt am Kabel an J5 (K-1).', 24.13, 209.55, 1.27),
    ('R13 begrenzt den GPIO-Strom auf 3,3 V / 220 R = 15 mA; C_Piezo = 45 nF typ.', 24.13, 212.09, 1.27),
    ('D4 wird vom GPIO getrieben, damit sie im Tiefschlaf abschaltbar ist (NF-04)', 24.13, 232.41, 1.27),
    ('R14 = 330 R -> 4,1 mA: die GaP-Gruene ist bei 1,3 mA praktisch unsichtbar (M-9).', 24.13, 234.95, 1.27),
    ('IO10, RXD und TXD bleiben frei - die Konsole laeuft ueber USB-Serial-JTAG.', 24.13, 236.22, 1.27),
    ('R3 = 0 R: Trennstelle fuer die Strommessung der Modulversorgung (M3, 4.5.6)', 189.23, 55.88, 1.27),
    ('IO2 und IO8 sind Strapping-Pins: R15 bzw. R16 halten sie beim Start hoch.', 189.23, 143.51, 1.27),
    ('IO18/IO19 fuehren direkt zur USB-Serial-JTAG-Einheit - keine Serienwiderstaende.', 189.23, 146.05, 1.27),
    ('IO3 ist RTC-faehig und weckt das Geraet aus dem Tiefschlaf (F-13).', 189.23, 148.59, 1.27),
    ('Pinbelegung J1 pruefen! VBUS/GND/D-/D+/CC1/CC2 - siehe README.', 300.99, 60.96, 1.27),
    ('R17/R18 ab Werk NICHT bestueckt (K-2): hat das Breakout eigene 5k1, ergeben', 300.99, 63.50, 1.27),
    ('2,55 k an CC bei 80 uA nur 0,204 V - Totzone zwischen vRa und vRd-Connect.', 300.99, 66.04, 1.27),
    ('C1 4u7 + C2 100n: USB-seitige Abblockung (Einschaltstrom < 10 uF-Grenze).', 300.99, 146.05, 1.27),
    ('R1 = 6k8  ->  I_chg = 1000 V / 6k8 = 147 mA = 0,3 C  (5.2)', 300.99, 148.59, 1.27),
    ('Keine Lastpfadumschaltung: zum Laden wird das Geraet ausgeschaltet (4.1).', 300.99, 151.13, 1.27),
    ('F1 + D3: Crowbar-Verpolungsschutz. Bei verpolter Zelle leitet D3 und F1 loest aus.', 300.99, 193.04, 1.27),
    ('Sperrstrom von D3 geht in das Tiefschlafbudget ein - wird in M3 gemessen.', 300.99, 195.58, 1.27),
    ('Beleg fuer D3 fehlt (K-4): das echte B5819W-Datenblatt ist noch abzulegen.', 300.99, 198.12, 1.27),
    ('C6 = 22u/10V X5R + C8 = 10u/16V X7R stuetzen die Sendespitze. Wirksame', 300.99, 243.84, 1.27),
    ('Kapazitaet bei 3,3 V DC-Bias im Datenblatt des gewaehlten Typs pruefen (K-3):', 300.99, 246.38, 1.27),
    ('nominell 32 uF, derated eher 15..18 uF -> Droop 350 mA * 10 us / 16 uF = 220 mV.', 300.99, 248.92, 1.27),
    ('U3 EN fest auf VBAT_SW: der Schiebeschalter schaltet die gesamte Versorgung.', 300.99, 251.46, 1.27),
]

# Feinplatzierung von Referenz und Wert, wo es eng wird:
# (Referenz dx, dy), (Wert dx, dy) relativ zum Symbolmittelpunkt
FIELD_OFF = {
    # Serienterminierung: fuenf Widerstaende im 2,54-mm-Raster -> beide Felder
    # in eine Zeile oberhalb des Bauteils
    'R5': ((2.54, -2.54), (-2.54, 2.54)),
    'R6': ((2.54, -2.54), (-2.54, 2.54)),
    'R7': ((2.54, -2.54), (-2.54, 2.54)),
    'R8': ((2.54, -2.54), (-2.54, 2.54)),
    'R9': ((2.54, -2.54), (-2.54, 2.54)),
    'R17':((2.54, -2.54), (-2.54, 2.54)),
    'R18':((2.54, -2.54), (-2.54, 2.54)),
    'R4':  ((0.0, -2.54), (0.0, 2.54)),
    'R15': ((0.0, -2.54), (0.0, 2.54)),
    'R16': ((0.0, -2.54), (0.0, 2.54)),
    'D2':  ((3.81, -1.27), (3.81, 1.27)),
    'D3':  ((3.81, -1.27), (3.81, 1.27)),
    'D4':  ((0.0, -2.54), (0.0, 2.54)),
    'F1':  ((0.0, -3.81), (0.0, 3.81)),
    'J5':  ((-6.35, -5.08), (-6.35, -2.54)),
    'SW1': ((0.0, -6.35), (0.0, 6.35)),
    'J1':  ((-3.81, -10.16), (-3.81, -7.62)),
    'J2':  ((-3.81, -5.08), (-3.81, -2.54)),
    'J3':  ((6.35, -11.43), (6.35, -8.89)),
    'J4':  ((-6.35, -5.08), (-6.35, -2.54)),
    'U1':  ((0.0, -25.4), (0.0, 25.4)),
    'U2':  ((0.0, -10.16), (0.0, 10.16)),
    'U3':  ((0.0, -10.16), (0.0, 10.16)),
    'D1':  ((0.0, -8.89), (0.0, 8.89)),
}

# Wert ausgeblendet, wo fuenf gleiche Bauteile im 2,54-mm-Raster stehen;
# der Wert steht im Blocktitel und in der Anmerkung.
HIDE_VALUE = set()

# Netzbezeichner, die nicht am Pin, sondern auf einem freien Drahtstueck stehen
LBL_AT = {
    'SCLK':     (132.08, 67.31, 180),
    'MOSI':     (133.35, 69.85, 180),
    'OLED_RES': (134.62, 72.39, 180),
    'OLED_DC':  (134.62, 74.93, 180),
    'OLED_CS':  (134.62, 77.47, 180),
}
