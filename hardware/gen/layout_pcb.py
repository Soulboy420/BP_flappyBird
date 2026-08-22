# -*- coding: utf-8 -*-
"""Platzierung, Sperrflaechen und Beschriftung der Leiterplatte.
Koordinaten in Platinen-Millimetern, Nullpunkt links oben, y nach unten.
Die Leiterbahnen selbst entstehen in gen/autoroute.py und liegen in routes.py."""

BX, BY = 30.0, 30.0        # Versatz der Platine auf dem Zeichnungsblatt
W, H = 90.0, 60.0          # Platinenmass

# ref -> (x, y, drehung)
PLACE = {
    'U1':   ( 41.00,  46.90, 180),
    'J1':   ( 13.50,   8.00,   0),
    'D1':   ( 24.00,  20.00,   0),
    'TP1':  ( 32.00,  12.50,   0),
    'C1':   ( 32.00,   8.00, 270),
    'C2':   ( 36.00,   8.00, 270),
    'U2':   ( 44.00,  10.00,   0),
    'R1':   ( 40.00,  15.00,   0),
    'R2':   ( 52.00,   8.00,   0),
    'D2':   ( 58.00,   8.00,   0),
    'C3':   ( 52.00,  14.00, 270),
    'C4':   ( 56.00,  14.00, 270),
    'TP2':  ( 62.00,  14.00,   0),
    'F1':   ( 68.00,   8.00,   0),
    'J2':   ( 76.00,   8.00,   0),
    'D3':   ( 68.00,  14.00,   0),
    'SW1':  ( 72.00,  22.00,   0),
    'LS1':  ( 14.00,  30.00,   0),
    'R13':  ( 26.00,  30.00,   0),
    'D4':   ( 10.00,  40.00,   0),
    'R14':  ( 16.00,  40.00,   0),
    'R15':  ( 22.00,  40.00,   0),
    'J4':   (  4.00,  55.00,   0),
    'R12':  ( 12.00,  55.00,   0),
    'R11':  ( 18.00,  55.00,   0),
    'C11':  ( 28.00,  43.00,  90),
    'R10':  ( 10.00,  50.00,   0),
    'TP5':  ( 24.00,  50.00,   0),
    'TP7':  ( 53.50,  38.00,   0),
    'R9':   ( 56.00,  43.90,   0),
    'R8':   ( 61.00,  45.40,   0),
    'R7':   ( 56.00,  46.90,   0),
    'R6':   ( 61.00,  48.40,   0),
    'R5':   ( 56.00,  49.90,   0),
    'R16':  ( 70.00,  44.00,   0),
    'J3':   ( 84.00,  56.00,  90),
    'U3':   ( 74.50,  51.50,   0),
    'C6':   ( 79.50,  50.50, 270),
    'C7':   ( 79.50,  55.00, 270),
    'C5':   ( 70.00,  57.50,   0),
    'TP3':  ( 75.00,  57.50,   0),
    'R4':   ( 56.00,  40.50,   0),
    'TP6':  ( 66.00,  40.50,   0),
    'C10':  ( 61.00,  40.50,   0),
    'R3':   ( 66.00,  52.60, 180),
    'C8':   ( 61.00,  51.60,  90),
    'C9':   ( 53.00,  51.60,  90),
    'TP4':  ( 66.00,  57.20,   0),
    'TP10': ( 36.00,  12.50,   0),
    'TP11': ( 24.00,  46.00,   0),
    'TP12': (  8.00,  46.00,   0),
    'H1':   (  3.50,   3.50,   0),
    'H2':   ( 85.00,   3.50,   0),
    'H3':   ( 85.00,  33.00,   0),
    'H4':   (  3.50,  45.00,   0),
}

# Sperrflaeche um die Modulantenne: x1, y1, x2, y2, Name
KEEPOUTS = [(26.75, 53.75, 55.25, 60.0, 'Antennen-Sperrflaeche ESP32-C3-WROOM-02')]

# Kupferflaeche zur Waermeabfuhr des Ladereglers (>= 100 mm^2, Projektplan 5.2)
NETZONES = [(48.0, 16.5, 66.0, 23.0, 'VBAT')]

# Beschriftungen: x, y, Text, Groesse, Lage, Drehung
TEXTS = [
    # Rueckseite: nur im kupferfreien Antennenbereich, dort stoert nichts
    (54.0, 56.0, 'FLAPPY BIRD ESP32-C3   REV. A', 1.6, 'B.SilkS', 0),
    (54.0, 58.6, 'HAW HAMBURG   BACHELORPROJEKT 2026', 1.1, 'B.SilkS', 0),
    # Vorderseite: Anschlussbelegung des USB-C-Breakouts
    (15.3,  8.00, 'VBUS', 0.8, 'F.SilkS', 0),
    (15.3, 10.54, 'GND',  0.8, 'F.SilkS', 0),
    (15.3, 13.08, 'D-',   0.8, 'F.SilkS', 0),
    (15.3, 15.62, 'D+',   0.8, 'F.SilkS', 0),
    (15.3, 18.16, 'CC1',  0.8, 'F.SilkS', 0),
    (15.3, 20.70, 'CC2',  0.8, 'F.SilkS', 0),
    # Vorderseite: Legende im bauteilfreien Mittelfeld
    (28.0, 27.0, 'J3 Display:  1 GND  2 VCC  3 SCLK  4 MOSI  5 RES  6 DC  7 CS', 1.1, 'F.SilkS', 0),
    (28.0, 30.5, 'Laden nur im ausgeschalteten Zustand (kein Lastpfad)', 1.1, 'F.SilkS', 0),
    (74.6,  4.6, '+',    0.9, 'F.SilkS', 0),
    (79.0,  4.6, '-',    0.9, 'F.SilkS', 0),
    (1.5,  48.6, 'TASTER', 0.8, 'F.SilkS', 0),
]

try:
    from labels import LABEL_OFF
except ImportError:
    LABEL_OFF = {}


def tracks():
    """Leiterbahnen aus dem Verdrahtungslauf (gen/autoroute.py)."""
    import routes
    return routes.TRACKS


def vias():
    import routes
    return routes.VIAS
