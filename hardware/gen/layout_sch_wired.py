# -*- coding: utf-8 -*-
"""Verdrahtete Schaltplanvariante (A3).

Alle Signale sind als Draht durchgezeichnet - es gibt keinen einzigen
Netzbezeichner. Nur die Versorgungsnetze laufen, wie in der Schaltungstechnik
ueblich, ueber Versorgungssymbole; sie waeren als Draht quer ueber das Blatt
nicht mehr lesbar.

Der Mikrocontroller steht in der Mitte, die Peripherie links in der Reihenfolge
seiner Anschluesse, der Versorgungszweig rechts. Dadurch kreuzt sich keine
einzige Signalleitung.
"""

PAPER = 'A3'
NO_AUTO_LABELS = True

UX, UY = 228.60, 151.13
PL = UX - 15.24
def py(off):
    return round(UY - off, 2)

P_3V3, P_EN = py(22.86), py(17.78)
P_IO0, P_IO1, P_IO2, P_IO3 = py(12.7), py(10.16), py(7.62), py(5.08)
P_IO4, P_IO5, P_IO6, P_IO7, P_IO8 = py(2.54), py(0), py(-2.54), py(-5.08), py(-7.62)
P_IO9, P_IO18, P_IO19 = py(-10.16), py(-15.24), py(-17.78)

RY = [137.16, 142.24, 147.32, 152.40, 157.48]     # Serienwiderstaende R5..R9
F1X = [196.85, 195.58, 194.31, 193.04, 191.77]    # Faecher Modul -> R5..R9
F2X = [149.86, 152.40, 154.94, 157.48, 160.02]    # Faecher R5..R9 -> J3
JP = [143.51, 146.05, 148.59, 151.13, 153.67, 156.21, 158.75]   # J3-Pins
UFX = [209.55, 207.01, 204.47, 201.93, 199.39]    # Faecher EN, IO0..IO3

PLACE = {
    'U1':  (UX, UY, 0, None),
    # --- Modulversorgung ----------------------------------------------------
    'R3':  (228.60, 106.68,   0, None),
    'C9':  (247.65, 119.38,   0, None),
    'C8':  (260.35, 119.38,   0, None),
    'TP4': (273.05, 115.57, 270, None),
    # --- Reset ---------------------------------------------------------------
    'R4':  (173.99,  40.64, 270, None),
    'C10': (186.69,  44.45,   0, None),
    'TP6': (191.77,  35.56, 180, None),
    # --- Betriebsanzeige ------------------------------------------------------
    'R14': (173.99,  62.23, 270, None),
    'D4':  (160.02,  62.23,   0, None),
    # --- Tonausgabe ------------------------------------------------------------
    'R13': (173.99,  85.09, 270, None),
    'LS1': (156.21,  87.63,   0, None),
    # --- Strapping IO2 ---------------------------------------------------------
    'R15': (173.99, 107.95,  90, None),
    # --- Tastereingabe ----------------------------------------------------------
    'R10': (173.99, 123.19,   0, None),
    'C11': (162.56, 119.38, 180, None),
    'TP5': (180.34, 120.65, 180, None),
    'R11': (151.13, 127.00, 270, None),
    'R12': (135.89, 127.00, 270, None),
    'J4':  (121.92, 127.00,   0, 'y'),
    # --- Displayanbindung --------------------------------------------------------
    'R5':  (180.34, RY[0], 270, None),
    'R6':  (180.34, RY[1], 270, None),
    'R7':  (180.34, RY[2], 270, None),
    'R8':  (180.34, RY[3], 270, None),
    'R9':  (180.34, RY[4], 270, None),
    'R16': (187.96, 168.91, 180, None),
    'J3':  (121.92, 151.13,   0, 'y'),
    # --- Downloadmodus -------------------------------------------------------------
    'TP7': (199.39, 161.29,  90, None),
    # --- USB-Anschluss und ESD-Schutz -------------------------------------------------
    'D1':  (161.29, 195.58,   0, None),
    'J1':  (129.54, 194.31,   0, 'y'),
    # --- Ladeschaltung ------------------------------------------------------------------
    'TP1': (287.02,  39.37, 180, None),
    'C1':  (298.45,  39.37,   0, None),
    'C2':  (309.88,  39.37,   0, None),
    'R2':  (322.58,  39.37,   0, None),
    'D2':  (322.58,  49.53,  90, None),
    'U2':  (353.06,  44.45,   0, None),
    'R1':  (342.90,  55.88,   0, None),
    'TP2': (377.19,  31.75, 180, None),
    'C3':  (377.19,  49.53,   0, None),
    'C4':  (388.62,  49.53,   0, None),
    # --- Akku, Verpolungsschutz, Schalter ------------------------------------------------
    'J2':  (287.02, 100.33,   0, 'y'),
    'F1':  (308.61, 100.33,  90, None),
    'D3':  (321.31, 106.68, 270, None),
    'SW1': (358.14, 100.33,   0, None),
    # --- Spannungsregler -------------------------------------------------------------------
    'C5':  (293.37, 160.02,   0, None),
    'U3':  (321.31, 158.75,   0, None),
    'TP3': (336.55, 149.86,   0, None),
    'C6':  (344.17, 160.02,   0, None),
    'C7':  (354.33, 160.02,   0, None),
    # --- Massepruefpunkte und Bohrungen --------------------------------------------------------
    'TP10':( 30.48, 209.55,   0, None),
    'TP11':( 43.18, 209.55,   0, None),
    'TP12':( 55.88, 209.55,   0, None),
    'H1':  ( 30.48, 226.06,   0, None),
    'H2':  ( 43.18, 226.06,   0, None),
    'H3':  ( 55.88, 226.06,   0, None),
    'H4':  ( 68.58, 226.06,   0, None),
}

WIRES = [
    # Modulversorgung: R3 (0 R) -> Modul, Abblockung, Pruefpunkt
    [('R3', '2'), ('U1', '1')],
    [(228.60, 115.57), (273.05, 115.57)],
    [('C9', '1'), (247.65, 115.57)],
    [('C8', '1'), (260.35, 115.57)],
    # Reset
    [('U1', '2'), (UFX[0], P_EN), (UFX[0], 40.64), ('R4', '1')],
    [('C10', '1'), (186.69, 40.64)],
    [('TP6', '1'), (191.77, 40.64)],
    # Betriebsanzeige
    [('U1', '18'), (UFX[1], P_IO0), (UFX[1], 62.23), ('R14', '1')],
    [('R14', '2'), ('D4', '2')],
    # Tonausgabe
    [('U1', '17'), (UFX[2], P_IO1), (UFX[2], 85.09), ('R13', '1')],
    [('R13', '2'), ('LS1', '1')],
    # Strapping IO2
    [('U1', '16'), (UFX[3], P_IO2), (UFX[3], 107.95), ('R15', '2')],
    # Tastereingabe
    [('U1', '15'), (UFX[4], P_IO3), (UFX[4], 127.00), ('R11', '1')],
    [('R10', '2'), (173.99, 127.00)],
    [('C11', '1'), (162.56, 127.00)],
    [('TP5', '1'), (180.34, 127.00)],
    [('R11', '2'), ('R12', '1')],
    [('R12', '2'), ('J4', '1')],
    # Modul -> Serienterminierung
    [('U1', '3'), (F1X[0], P_IO4), (F1X[0], RY[0]), ('R5', '1')],
    [('U1', '4'), (F1X[1], P_IO5), (F1X[1], RY[1]), ('R6', '1')],
    [('U1', '5'), (F1X[2], P_IO6), (F1X[2], RY[2]), ('R7', '1')],
    [('U1', '6'), (F1X[3], P_IO7), (F1X[3], RY[3]), ('R8', '1')],
    [('U1', '7'), (F1X[4], P_IO8), (F1X[4], RY[4]), ('R9', '1')],
    [(187.96, RY[4]), ('R16', '2')],
    # Serienterminierung -> Displaysteckverbinder
    [('R5', '2'), (F2X[0], RY[0]), (F2X[0], JP[2]), ('J3', '3')],
    [('R6', '2'), (F2X[1], RY[1]), (F2X[1], JP[3]), ('J3', '4')],
    [('R7', '2'), (F2X[2], RY[2]), (F2X[2], JP[4]), ('J3', '5')],
    [('R8', '2'), (F2X[3], RY[3]), (F2X[3], JP[5]), ('J3', '6')],
    [('R9', '2'), (F2X[4], RY[4]), (F2X[4], JP[6]), ('J3', '7')],
    [('J3', '1'), (128.27, JP[0]), (128.27, 133.35)],
    [('J3', '2'), (130.81, JP[1]), (130.81, 130.81)],
    # Downloadmodus
    [('U1', '8'), ('TP7', '1')],
    # USB
    [('U1', '13'), (191.77, P_IO18), (191.77, 195.58), ('D1', '6')],
    [('U1', '14'), (194.31, P_IO19), (194.31, 198.12), ('D1', '4')],
    [('J1', '3'), (144.78, 194.31), (144.78, 195.58), ('D1', '1')],
    [('J1', '4'), (142.24, 196.85), (142.24, 198.12), ('D1', '3')],
    # Ladeschaltung
    [('TP1', '1'), (287.02, 34.29)],
    [('U2', '5'), ('R1', '1')],
    [('R2', '2'), ('D2', '2')],
    [('D2', '1'), (322.58, 64.77), (363.22, 64.77), ('U2', '1')],
    [('TP2', '1'), (377.19, 26.67)],
    # Akkupfad
    [('J2', '1'), ('F1', '1')],
    # Spannungsregler
    [('U3', '1'), (287.02, 156.21)],
    [('U3', '3'), (304.80, 158.75), (304.80, 156.21)],
    [('U3', '5'), (363.22, 156.21)],
    [('TP3', '1'), (336.55, 156.21)],
    # Netzflaggen
    [(287.02, 209.55), (287.02, 204.47)],
    [(299.72, 209.55), (299.72, 204.47)],
    [(312.42, 209.55), (312.42, 204.47)],
    [(325.12, 209.55), (325.12, 204.47)],
]

EXTRA_POWER = [
    ('VBUS',     287.02,  34.29, 'up'),
    ('VBAT',     377.19,  26.67, 'up'),
    ('VBAT_SW',  287.02, 156.21, 'left'),
    ('+3V3',     363.22, 156.21, 'right'),
    ('GND',      128.27, 133.35, 'up'),
    ('+3V3',     130.81, 130.81, 'up'),
    ('GND',      287.02, 209.55, 'down'),
    ('VBUS',     299.72, 204.47, 'up'),
    ('VBAT_SW',  312.42, 204.47, 'up'),
    ('+3V3_MCU', 325.12, 204.47, 'up'),
]

PWR_FLAGS = [
    (287.02, 204.47, 'up'),
    (299.72, 209.55, 'down'),
    (312.42, 209.55, 'down'),
    (325.12, 209.55, 'down'),
]

LABELS, STUB_LABELS, LBL_AT, HIDE_VALUE = [], [], {}, set()

FRAMES = [
    (144.78,  27.94, 214.63, 111.76, 'Reset, Betriebsanzeige, Tonausgabe, Strapping IO2'),
    (110.49, 116.84, 214.63, 130.81, 'Tastereingabe: Entprellung und ESD-Begrenzung'),
    (110.49, 133.35, 214.63, 179.07, 'Displayanbindung mit Serienterminierung 68 R'),
    (110.49, 186.69, 214.63, 209.55, 'USB-Anschluss und ESD-Schutz'),
    (278.13,  20.32, 401.32,  73.66, 'Ladeschaltung MCP73831, I_chg = 147 mA'),
    (278.13,  87.63, 401.32, 118.11, 'Akku, Verpolungsschutz, Ein/Aus-Schalter'),
    (278.13, 140.97, 401.32, 176.53, 'Spannungsregler AP2112K-3.3'),
    (278.13, 196.85, 337.82, 219.71, 'Netzflaggen (nur fuer die ERC-Pruefung)'),
]

NOTES = [
    ('Verdrahtete Fassung: alle Signale sind durchgezeichnet, es gibt keine Netzbezeichner.', 25.4, 240.03, 1.6),
    ('Nur die Versorgungsnetze laufen - wie ueblich - ueber Versorgungssymbole.', 25.4, 245.11, 1.6),
    ('Die Peripherie steht links in der Reihenfolge der Modulanschluesse; dadurch', 25.4, 252.73, 1.4),
    ('kreuzt sich keine einzige Signalleitung.', 25.4, 256.54, 1.4),
    ('R5..R9 sitzen unmittelbar am Mikrocontroller (Projektplan 5.7).', 25.4, 262.89, 1.4),
    ('IO2 und IO8 sind Strapping-Pins; R15 bzw. R16 halten sie beim Start hoch.', 25.4, 266.70, 1.4),
    ('IO3 ist RTC-faehig und weckt das Geraet aus dem Tiefschlaf (F-13).', 25.4, 270.51, 1.4),
    ('IO10, RXD und TXD bleiben frei - die Konsole laeuft ueber USB-Serial-JTAG.', 25.4, 274.32, 1.4),
    ('D4 haengt am GPIO, damit sie im Tiefschlaf abschaltbar ist (NF-04).', 152.4, 262.89, 1.4),
    ('R13 = 220 R begrenzt den Piezostrom auf 15 mA (I_OL des ESP32-C3: 28 mA).', 152.4, 266.70, 1.4),
    ('R3 = 0 R: Trennstelle fuer die Strommessung der Modulversorgung (M3).', 152.4, 270.51, 1.4),
    ('Pinbelegung von J1 am gekauften Breakout pruefen - siehe README.', 152.4, 274.32, 1.4),
]

FIELD_OFF = {
    'U1':  ((0.0, -26.67), (0.0, 26.67)),
    'U2':  ((0.0, -10.16), (0.0, 10.16)),
    'U3':  ((0.0, -10.16), (0.0, 10.16)),
    'D1':  ((0.0, -8.89), (0.0, 8.89)),
    'D2':  ((3.81, -1.27), (3.81, 1.27)),
    'D3':  ((3.81, -1.27), (3.81, 1.27)),
    'D4':  ((0.0, -2.54), (0.0, 2.54)),
    'F1':  ((0.0, -3.81), (0.0, 3.81)),
    'LS1': ((5.08, -3.81), (5.08, -1.27)),
    'SW1': ((0.0, -6.35), (0.0, 6.35)),
    'J1':  ((-3.81, 8.89), (-3.81, 11.43)),
    'J2':  ((-3.81, -5.08), (-3.81, -2.54)),
    'J3':  ((-3.81, 12.7), (-3.81, 15.24)),
    'J4':  ((-3.81, -5.08), (-3.81, -2.54)),
    'R5':  ((2.54, -2.54), (-2.54, 2.54)),
    'R6':  ((2.54, -2.54), (-2.54, 2.54)),
    'R7':  ((2.54, -2.54), (-2.54, 2.54)),
    'R8':  ((2.54, -2.54), (-2.54, 2.54)),
    'R9':  ((2.54, -2.54), (-2.54, 2.54)),
    'R10': ((-4.45, -1.905), (-4.45, 0.635)),
    'C11': ((-3.81, -1.905), (-3.81, 0.635)),
}
