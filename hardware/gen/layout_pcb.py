# -*- coding: utf-8 -*-
"""Platzierung, Sperrflaechen und Beschriftung der Leiterplatte.
Koordinaten in Platinen-Millimetern, Nullpunkt links oben, y nach unten.
Die Leiterbahnen selbst entstehen in gen/autoroute.py und liegen in routes.py.

Aufteilung der Platine
    oberer Streifen   USB-C-Breakout, Laderegler, Akku, Schalter, Regler
    Mitte links       Piezo, Anzeige, Tastereingabe
    Mitte             Funkmodul, Antenne an der Unterkante
    Mitte rechts      Abblockung, Reset, Serienterminierung, Displaykabel
    unterer Streifen  0-Ohm-Trennstelle und Pruefpunkte neben der Antenne
"""

BX, BY = 30.0, 30.0        # Versatz der Platine auf dem Zeichnungsblatt
W, H = 72.0, 51.0          # Platinenmass

# Handbestueckung: geforderter freier Abstand zwischen zwei Bauteilumrissen
# und zum Platinenrand. Der Umriss (F.CrtYd) liegt bei den Handloet-Footprints
# schon 0,25 mm ausserhalb der Pads; 0,8 mm Umrissabstand ergeben also rund
# 1,3 mm freies Kupfer zwischen zwei Pads - genug fuer eine 1,6-mm-Meisselspitze.
LOETABSTAND = 0.8
RANDABSTAND = 0.5

# ref -> (x, y, drehung)
PLACE = {
    # --- Funkmodul, Antenne buendig mit der Unterkante (Projektplan 4.5.7) ---
    'U1':   ( 36.00,  37.90, 180),

    # --- oberer Streifen, links: USB-C-Breakout und ESD-Schutz ---
    'J1':   ( 13.50,  11.00,   0),
    'D1':   ( 19.50,  16.00,   0),
    'R17':  ( 21.00,  20.50,   0),
    'R18':  ( 21.00,  24.00,   0),

    # --- oberer Streifen, Mitte: VBUS, Laderegler, Ladeanzeige ---
    'C1':   ( 25.00,   9.00,  90),
    'C2':   ( 28.50,   9.00,  90),
    'TP1':  ( 25.00,   4.50,   0),
    'TP10': ( 28.50,   4.50,   0),
    'U2':   ( 34.00,   9.00, 180),
    'R1':   ( 33.00,  13.50,   0),
    'R2':   ( 33.00,   4.50,   0),
    'D2':   ( 39.00,   4.00,   0),
    'C3':   ( 39.50,   8.50,   0),
    'C4':   ( 44.50,   8.50,   0),
    'TP2':  ( 47.00,  12.00,   0),

    # --- oberer Streifen, rechts: Akkupfad, Schalter, Spannungsregler ---
    'F1':   ( 53.00,   4.00,   0),
    'D3':   ( 53.00,   9.00,   0),
    'J2':   ( 60.00,   4.50,   0),
    'SW1':  ( 61.50,  12.00,   0),
    'U3':   ( 52.00,  19.00, 180),
    'C5':   ( 57.50,  19.00,   0),
    'C7':   ( 52.50,  23.50,   0),
    'C6':   ( 57.50,  23.50,   0),

    # --- Mitte links: Piezo, Anzeige, Tastereingabe ---
    'LS1':  (  4.60,  37.00,   0),
    'R13':  ( 22.00,  42.00,  90),
    'C11':  ( 22.00,  37.40,  90),
    'R15':  ( 22.00,  32.80,  90),
    'R10':  ( 22.00,  28.20,  90),
    'TP5':  ( 18.40,  42.00,   0),
    'R11':  ( 18.40,  37.40,  90),
    'R12':  ( 18.40,  32.80,  90),
    'J4':   (  7.50,  46.50,   0),
    'R14':  ( 16.00,  46.50,   0),
    'D4':   ( 16.00,  49.50,   0),
    'TP11': ( 19.85,  47.50,   0),
    
    # --- Mitte rechts, Spalte A: Abblockung, Reset, Strapping ---
    'C9':   ( 49.40,  42.80,   0),
    'C8':   ( 49.40,  40.00,   0),
    'R4':   ( 49.40,  36.60,   0),
    'C10':  ( 49.40,  33.20,   0),
    'R16':  ( 49.40,  30.00,   0),
    'TP7':  ( 49.40,  26.80,   0),

    # --- Mitte rechts, Spalte B: Serienterminierung zum Display ---
    'R5':   ( 53.95,  40.00,   0),
    'R6':   ( 53.95,  37.20,   0),
    'R7':   ( 53.95,  34.40,   0),
    'R8':   ( 53.95,  31.60,   0),
    'R9':   ( 53.95,  28.80,   0),

    # --- rechter Rand: Displaykabel ---
    'J3':   ( 66.00,  43.50,  90),

    # --- unterer Streifen neben der Antenne: Trennstelle und Pruefpunkte ---
    'TP4':  ( 52.20,  48.40,   0),
    'R3':   ( 56.40,  48.40,   0),
    'TP3':  ( 60.50,  48.40,   0),
    'TP12': ( 64.00,  48.40,   0),
    'TP6':  ( 67.50,  48.40,   0),

    # --- Befestigung ---
    'H1':   (  3.00,   2.00,   0),
    'H2':   ( 69.00,   3.00,   0),
    'H3':   ( 69.00,  21.00,   0),
    'H4':   (  2.20,  47.00,   0),
}


def _rel(ref, dx1, dy1, dx2, dy2):
    """Rechteck relativ zu einem platzierten Bauteil."""
    x, y, _ = PLACE[ref]
    return (x + dx1, y + dy1, x + dx2, y + dy2)


# Sperrflaeche um die Modulantenne: x1, y1, x2, y2, Name.
# Kein Kupfer auf beiden Lagen, keine Bauteile.
KEEPOUTS = [_rel('U1', -14.25, 6.85, 14.25, 13.10)
            + ('Antennen-Sperrflaeche ESP32-C3-WROOM-02',)]

# Flaechen ohne Bauteile und ohne Leiterbahnen der Oberseite (Projektplan
# 4.5.2). Aus der Platzierung abgeleitet, damit sie beim Verschieben von
# Modul oder Breakout mitwandern.
BAUTEILFREI = [_rel('J1', -12.9, -6.6, -0.9, 14.6) + ('Flaeche unter dem USB-C-Breakout',)]
NO_TRACK_F = [_rel('U1', -7.8, -7.9, 7.8, 13.1)] + [b[:4] for b in BAUTEILFREI]

# Kupferflaeche zur Waermeabfuhr des Ladereglers (>= 100 mm^2, Projektplan 5.2)
NETZONES = [(35.5, 7.0, 49.0, 16.0, 'VBAT')]

# Beschriftungen: x, y, Text, Groesse, Lage, Drehung
TEXTS = [
    # Rueckseite: nur im kupferfreien Antennenbereich, dort stoert nichts.
    # Gespiegelter Text laeuft in Platinenkoordinaten nach links, deshalb
    # sitzt der Ankerpunkt am rechten Rand der Sperrflaeche.
    (49.5, 47.0, 'FLAPPY BIRD ESP32-C3   REV. B', 1.3, 'B.SilkS', 0),
    (49.5, 49.3, 'HAW HAMBURG   BACHELORPROJEKT 2026', 0.9, 'B.SilkS', 0),
    # Vorderseite: Anschlussbelegung des USB-C-Breakouts, Zeile fuer Zeile
    # neben dem zugehoerigen Stift von J1
    (15.5, 11.00, 'VBUS', 0.8, 'F.SilkS', 0),
    (15.5, 13.54, 'GND',  0.8, 'F.SilkS', 0),
    (15.5, 16.08, 'D-',   0.8, 'F.SilkS', 0),
    (15.5, 18.62, 'D+',   0.8, 'F.SilkS', 0),
    (15.5, 21.16, 'CC1',  0.8, 'F.SilkS', 0),
    (15.5, 23.70, 'CC2',  0.8, 'F.SilkS', 0),
    # Vorderseite: Hinweise im bauteilfreien Band oberhalb des Funkmoduls
    (24.5, 21.5, 'R17/R18 nur ohne CC am Breakout', 0.8, 'F.SilkS', 0),
    (24.5, 27.0, 'J3: GND VCC SCLK MOSI RES DC CS', 0.8, 'F.SilkS', 0),
    (24.5, 29.0, 'Laden nur ausgeschaltet', 0.8, 'F.SilkS', 0),
    (59.6,  1.9, '+',    0.9, 'F.SilkS', 0),
    (61.6,  1.9, '-',    0.9, 'F.SilkS', 0),
    (5.0,  43.0, 'TASTER', 0.8, 'F.SilkS', 0),
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
