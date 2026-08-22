# -*- coding: utf-8 -*-
"""Prueflauf fuer die Entwurfswerkzeuge.

Stufe 1  Grundbausteine einzeln (S-Expression, Koordinatentransformationen,
         Entwurfsdaten, erzeugte Bibliotheken, Verdrahter)
Stufe 2  Erzeugnisse einzeln (Schaltplandateien, Platinendatei)
Stufe 3  Gesamtlauf (ERC, DRC, Abgleich) - macht erzeugen.sh

Aufruf:  python3 tests.py [stufe1|stufe2|alles]
Rueckgabewert 0, wenn alle Pruefungen bestanden sind.
"""
import math, os, subprocess, sys, copy

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
WURZEL = os.path.abspath(os.path.join(HIER, '..'))

from sexp import parse, dump, find, findall, Str
import design, libs

_fehler, _geprueft = [], 0


def pruefe(bedingung, name, detail=''):
    global _geprueft
    _geprueft += 1
    if not bedingung:
        _fehler.append((name, detail))
        print('  FEHLER  %s%s' % (name, ('  -> ' + detail) if detail else ''))
    return bool(bedingung)


def nah(a, b, eps=1e-6):
    return abs(a - b) < eps


# =====================================================================
#  T1  S-Expression: parse und dump muessen verlustfrei sein
# =====================================================================
def t1_sexp():
    print('T1  S-Expression')
    proben = [
        os.path.join(design.FPLIB, 'Resistor_SMD.pretty',
                     'R_0805_2012Metric_Pad1.20x1.40mm_HandSolder.kicad_mod'),
        os.path.join(design.FPLIB, 'RF_Module.pretty', 'ESP32-C3-WROOM-02.kicad_mod'),
        os.path.join(WURZEL, 'flappy-esp32c3.kicad_sch'),
        os.path.join(WURZEL, 'flappy-esp32c3.kicad_pcb'),
    ]
    for p in proben:
        if not os.path.exists(p):
            pruefe(False, 'Datei vorhanden', p)
            continue
        roh = open(p, encoding='utf-8').read()
        a = parse(roh)
        b = parse(dump(a))
        pruefe(a == b, 'Umlauf parse/dump gleich', os.path.basename(p))

    # Sonderzeichen muessen die Anfuehrungszeichen ueberleben
    for text in ['a"b', 'c\\d', 'e f', '', 'ae oe ue']:
        knoten = ['x', Str(text)]
        zurueck = parse(dump(knoten))
        pruefe(str(zurueck[1]) == text, 'Sonderzeichen erhalten', repr(text))

    # Atome ohne Anfuehrungszeichen bleiben Atome
    z = parse('(a b 1.5 (c "d e"))')
    pruefe(z == ['a', 'b', '1.5', ['c', Str('d e')]], 'Struktur korrekt', repr(z))
    pruefe(find(z, 'c') == ['c', Str('d e')], 'find findet Unterknoten')
    pruefe(len(findall(z, 'c')) == 1, 'findall zaehlt richtig')


# =====================================================================
#  T2  Koordinatentransformationen
# =====================================================================
def t2_transformationen():
    print('T2  Koordinatentransformationen')
    # Symbolkoordinaten: Bibliothek ist Y-hoch, Blatt ist Y-runter
    faelle = [
        # (px, py, rot, spiegel, erwartet_dx, erwartet_dy)
        (0, 3.81, 0, None, 0, -3.81),      # Pin 1 eines Widerstands: oben
        (0, -3.81, 0, None, 0, 3.81),      # Pin 2: unten
        (0, 3.81, 90, None, -3.81, 0),     # 90 Grad gegen den Uhrzeigersinn: links
        (0, 3.81, 180, None, 0, 3.81),
        (0, 3.81, 270, None, 3.81, 0),
        (-5.08, 0, 0, 'y', 5.08, 0),       # gespiegelt: Pin wandert nach rechts
        (-5.08, 2.54, 0, 'y', 5.08, -2.54),
    ]
    for px, py, rot, mir, ex, ey in faelle:
        x, y = libs.sym_transform(px, py, 100.0, 100.0, rot, mir)
        pruefe(nah(x - 100.0, ex) and nah(y - 100.0, ey),
               'sym_transform (%g,%g) rot%d %s' % (px, py, rot, mir),
               'ergibt (%+.2f,%+.2f), erwartet (%+.2f,%+.2f)' % (x-100, y-100, ex, ey))

    # Pinrichtung: Einheitsvektor, und er zeigt vom Bauteilkoerper weg
    for lib, ref in [('Device:R', 'R'), ('Device:C', 'C'), ('Device:LED', 'LED'),
                     ('RF_Module:ESP32-C3-WROOM-02', 'U')]:
        for num, name, et, px, py, pa, pl in libs.symbol_pins(lib):
            for rot in (0, 90, 180, 270):
                for mir in (None, 'y'):
                    d = libs.pin_dir(pa, rot, mir)
                    pruefe(nah(math.hypot(*d), 1.0),
                           'pin_dir ist Einheitsvektor', '%s Pin %s rot%d' % (lib, num, rot))
                    # ein Schritt nach aussen vergroessert den Abstand zum Symbolmittelpunkt
                    p0 = libs.sym_transform(px, py, 0, 0, rot, mir)
                    p1 = (p0[0] + d[0], p0[1] + d[1])
                    pruefe(math.hypot(*p1) >= math.hypot(*p0) - 1e-9,
                           'pin_dir zeigt nach aussen',
                           '%s Pin %s rot%d %s' % (lib, num, rot, mir))

    # Footprintkoordinaten: Y laeuft nach unten, Drehung gegen den Uhrzeigersinn
    ffaelle = [
        (1.0, 0.0, 0, 1.0, 0.0),
        (1.0, 0.0, 90, 0.0, -1.0),     # rechts wird oben
        (1.0, 0.0, 180, -1.0, 0.0),
        (1.0, 0.0, 270, 0.0, 1.0),
        (0.0, 1.0, 90, 1.0, 0.0),
    ]
    for px, py, rot, ex, ey in ffaelle:
        x, y = libs.fp_transform(px, py, 50.0, 50.0, rot)
        pruefe(nah(x - 50.0, ex) and nah(y - 50.0, ey),
               'fp_transform (%g,%g) rot%d' % (px, py, rot),
               'ergibt (%+.2f,%+.2f), erwartet (%+.2f,%+.2f)' % (x-50, y-50, ex, ey))

    # Drehung erhaelt Abstaende (Starrkoerper)
    import random
    random.seed(7)
    for _ in range(200):
        ax, ay = random.uniform(-10, 10), random.uniform(-10, 10)
        bx, by = random.uniform(-10, 10), random.uniform(-10, 10)
        rot = random.choice((0, 90, 180, 270))
        A = libs.fp_transform(ax, ay, 3, 4, rot)
        B = libs.fp_transform(bx, by, 3, 4, rot)
        pruefe(nah(math.dist(A, B), math.dist((ax, ay), (bx, by)), 2e-4),
               'fp_transform ist abstandstreu')
        A = libs.sym_transform(ax, ay, 3, 4, rot)
        B = libs.sym_transform(bx, by, 3, 4, rot)
        pruefe(nah(math.dist(A, B), math.dist((ax, ay), (bx, by)), 2e-4),
               'sym_transform ist abstandstreu')



# =====================================================================
#  T3  Entwurfsdaten: Bauteile, Netze, Symbol/Footprint-Paarung
# =====================================================================
def t3_entwurfsdaten():
    print('T3  Entwurfsdaten')
    for ref, (symbol, wert, fp, beschr) in sorted(design.COMPONENTS.items()):
        try:
            pins = libs.symbol_pins(symbol)
        except Exception as e:
            pruefe(False, 'Symbol ladbar', '%s %s (%s)' % (ref, symbol, e)); continue
        try:
            pads = libs.fp_pads(fp)
        except Exception as e:
            pruefe(False, 'Footprint ladbar', '%s %s (%s)' % (ref, fp, e)); continue
        pruefe(bool(beschr), 'Beschreibung vorhanden', ref)
        if symbol.startswith('Mechanical'):
            pruefe(not pins, 'Bohrung hat keine Pins', ref)
            continue
        pinnr = {p[0] for p in pins}
        padnr = set(pads)
        # jeder Symbolpin muss ein Pad im Footprint haben
        pruefe(pinnr <= padnr, 'jeder Pin hat ein Pad',
               '%s: Pins ohne Pad %s' % (ref, sorted(pinnr - padnr)))
        # Pads ohne Pin sind nur bei Befestigungslaschen erlaubt
        ueber = padnr - pinnr
        pruefe(not ueber or ref in ('SW1',), 'keine unbelegten Pads',
               '%s: %s' % (ref, sorted(ueber)))

    # jeder Pin genau einmal: entweder in einem Netz oder als "nicht angeschlossen"
    belegung = {}
    doppelt = []
    for netz, pins in design.NETS.items():
        for rp in pins:
            if rp in belegung:
                doppelt.append((rp, belegung[rp], netz))
            belegung[rp] = netz
    pruefe(not doppelt, 'kein Pin in zwei Netzen', str(doppelt))
    for rp in design.NO_CONNECT:
        if rp in belegung:
            doppelt.append((rp, belegung[rp], 'NO_CONNECT'))
        belegung[rp] = 'NC'
    pruefe(not doppelt, 'kein Pin gleichzeitig verdrahtet und offen', str(doppelt))

    fehlend = []
    for ref, (symbol, *_rest) in design.COMPONENTS.items():
        if symbol.startswith('Mechanical'):
            continue
        for p in libs.symbol_pins(symbol):
            if (ref, p[0]) not in belegung:
                fehlend.append((ref, p[0]))
    pruefe(not fehlend, 'jeder Pin ist versorgt', str(fehlend))

    unbekannt = [rp for rp in belegung if rp[0] not in design.COMPONENTS]
    pruefe(not unbekannt, 'keine Netze auf unbekannte Bauteile', str(unbekannt))

    einzeln = [n for n, l in design.NETS.items() if len(l) < 2]
    pruefe(not einzeln, 'kein Netz mit nur einem Pin', str(einzeln))

    # Versorgungsnetze muessen genau eine Quelle oder eine Netzflagge haben
    pruefe('GND' in design.NETS and len(design.NETS['GND']) > 10,
           'Massenetz vorhanden und gross')

    # Widerstands- und Kondensatorwerte plausibel
    import re
    for ref, (symbol, wert, *_r) in design.COMPONENTS.items():
        if symbol == 'Device:R':
            pruefe(re.fullmatch(r'\d+[kMR]?\d*|0R', wert.replace(' ', '')),
                   'Widerstandswert lesbar', '%s = %s' % (ref, wert))
        if symbol == 'Device:C':
            pruefe(re.fullmatch(r'\d+[unp]\d*', wert.replace(' ', '')),
                   'Kondensatorwert lesbar', '%s = %s' % (ref, wert))


# =====================================================================
#  T4  erzeugte Bibliotheken
# =====================================================================
def t4_bibliotheken():
    print('T4  erzeugte Bibliotheken')
    for name in ('VBAT', 'VBAT_SW', '+3V3_MCU'):
        try:
            pins = libs.symbol_pins('flappy:' + name)
        except Exception as e:
            pruefe(False, 'Versorgungssymbol ladbar', '%s (%s)' % (name, e)); continue
        pruefe(len(pins) == 1, 'genau ein Pin', name)
        pruefe(pins[0][1] == name, 'Pinname ist der Netzname',
               '%s hat %s' % (name, pins[0][1]))
        pruefe(pins[0][2] == 'power_in', 'Pin ist power_in', name)
        blk, _ = libs.get_symbol('flappy:' + name)
        pruefe(find(blk, 'power') is not None, 'als Versorgungssymbol markiert', name)

    # Handloet-Footprint des Funkmoduls
    fp = 'flappy:ESP32-C3-WROOM-02_HandSolder'
    orig = libs.load_footprint('RF_Module:ESP32-C3-WROOM-02')
    neu = libs.load_footprint(fp)
    def pads(node):
        out = {}
        for p in findall(node, 'pad'):
            nr = str(p[1])
            at, sz = find(p, 'at'), find(p, 'size')
            dr = find(p, 'drill')
            out.setdefault(nr, []).append((float(at[1]), float(at[2]),
                                           float(sz[1]), float(sz[2]),
                                           float(dr[1]) if dr else None))
        return out
    po, pn = pads(orig), pads(neu)
    pruefe(set(po) == set(pn), 'gleiche Padnummern wie im Original')
    for nr in [str(i) for i in range(1, 19)]:
        (xo, yo, wo, ho, _), = po[nr]
        (xn, yn, wn, hn, _), = pn[nr]
        pruefe(nah(wn - wo, 1.0), 'Pad %s ist 1 mm laenger' % nr,
               '%.2f statt %.2f' % (wn, wo))
        pruefe(nah(abs(xn) - abs(xo), 0.5), 'Pad %s 0,5 mm nach aussen' % nr)
        pruefe(nah(yn, yo), 'Pad %s unveraendert in y' % nr)
        pruefe(nah(hn, ho), 'Pad %s unveraendert in der Breite' % nr)
        # Innenkante bleibt gleich: das Pad waechst nur nach aussen
        innen_o = abs(xo) - wo / 2
        innen_n = abs(xn) - wn / 2
        pruefe(nah(innen_o, innen_n), 'Pad %s waechst nur nach aussen' % nr,
               '%.3f -> %.3f' % (innen_o, innen_n))
    bohr = [d for e in pn['19'] for d in (e[4],) if d is not None]
    pruefe(bohr and min(bohr) >= 0.3, 'Waermevias mindestens 0,3 mm',
           str(sorted(set(bohr))))
    # Siebdruck an der Antennenkante entfernt
    kanten = [find(l, 'start') for l in findall(neu, 'fp_line')
              if find(l, 'layer') is not None and str(find(l, 'layer')[1]) == 'F.SilkS']
    pruefe(all(float(k[2]) > -12.9 for k in kanten if k),
           'kein Siebdruck auf der Platinenkante')



# =====================================================================
#  T5  Rasterverdrahter
# =====================================================================
def t5_verdrahter():
    print('T5  Rasterverdrahter')
    from router import Router, GRID

    # 5a  einfacher Weg um eine Wand herum
    R = Router(40, 20, margin=0.4)
    R.block_rect(0, 18, 0, 22, 15)            # Wand von oben bis y=15
    R.add_pad('N', (0,), 5, 10, 0.5, 0.5)
    R.add_pad('N', (0,), 35, 10, 0.5, 0.5)
    segs, vias = R.route('N', [(5, 10, (0,)), (35, 10, (0,))], 0.125, 0.2)
    pruefe(segs, 'Weg um Hindernis gefunden')
    pruefe(not vias, 'kein Lagenwechsel noetig', str(vias))
    # der Weg muss unter der Wand hindurchgehen
    unten = [s for s in segs if max(s[0][1], s[1][1]) > 15.0]
    pruefe(unten, 'Weg fuehrt unter der Wand hindurch')

    # 5b  kein Weg, wenn die Wand durchgeht
    R2 = Router(40, 20, margin=0.4)
    R2.block_rect(None, 18, 0, 22, 20)        # beide Lagen sperren
    R2.add_pad('N', (0,), 5, 10, 0.5, 0.5)
    R2.add_pad('N', (0,), 35, 10, 0.5, 0.5)
    try:
        R2.route('N', [(5, 10, (0,)), (35, 10, (0,))], 0.125, 0.2, via_cost=1e9)
        pruefe(False, 'unmoeglicher Weg wird gemeldet')
    except RuntimeError:
        pruefe(True, 'unmoeglicher Weg wird gemeldet')

    # 5c  Lagenwechsel, wenn die Oberseite blockiert ist
    R3 = Router(40, 20, margin=0.4)
    R3.block_rect(0, 18, 0, 22, 20)           # F.Cu komplett gesperrt
    R3.add_pad('N', (0, 1), 5, 10, 0.5, 0.5)
    R3.add_pad('N', (0, 1), 35, 10, 0.5, 0.5)
    segs, vias = R3.route('N', [(5, 10, (0, 1)), (35, 10, (0, 1))], 0.125, 0.2,
                          via_cost=10.0)
    pruefe(len(vias) >= 2, 'Lagenwechsel mit zwei Vias', str(len(vias)))
    lagen = {s[2] for s in segs}
    pruefe(1 in lagen, 'Rueckseite wird benutzt')

    # 5d  jeder Lagenwechsel hat eine Durchkontaktierung an genau dieser Stelle
    for segs_, vias_ in ((segs, vias),):
        wechsel = []
        for a, b in zip(segs_, segs_[1:]):
            if a[2] != b[2]:
                wechsel.append(a[1])
        for w in wechsel:
            pruefe(any(nah(w[0], v[0], 1e-6) and nah(w[1], v[1], 1e-6) for v in vias_),
                   'Via am Lagenwechsel', str(w))

    # 5e  erzeugte Segmente sind waagerecht, senkrecht oder 45 Grad
    import routes
    schraeg = []
    for netz, lage, breite, a, b in routes.TRACKS:
        dx, dy = abs(a[0] - b[0]), abs(a[1] - b[1])
        if not (nah(dx, 0, 1e-6) or nah(dy, 0, 1e-6) or nah(dx, dy, 1e-6)):
            schraeg.append((netz, a, b))
    pruefe(not schraeg, 'nur H/V/45-Segmente', str(schraeg[:3]))

    # 5f  keine Segmente der Laenge null
    null = [t for t in routes.TRACKS if t[3] == t[4]]
    pruefe(not null, 'keine Segmente der Laenge null', str(null[:3]))

    # 5g  alle Segmente und Vias liegen innerhalb der Platine
    import layout_pcb as P
    raus = [t for t in routes.TRACKS
            if not (0 <= t[3][0] <= P.W and 0 <= t[3][1] <= P.H
                    and 0 <= t[4][0] <= P.W and 0 <= t[4][1] <= P.H)]
    pruefe(not raus, 'alle Bahnen auf der Platine', str(raus[:2]))
    rausv = [v for v in routes.VIAS if not (0 <= v[1] <= P.W and 0 <= v[2] <= P.H)]
    pruefe(not rausv, 'alle Vias auf der Platine', str(rausv[:2]))

    # 5h  Netznamen in routes.py existieren wirklich
    unbekannt = ({t[0] for t in routes.TRACKS} | {v[0] for v in routes.VIAS}) - set(design.NETS)
    pruefe(not unbekannt, 'nur bekannte Netze verdrahtet', str(unbekannt))

    # 5i  jedes Netz mit mehr als einem Pin ist auch verdrahtet oder haengt an der Flaeche
    verdrahtet = {t[0] for t in routes.TRACKS}
    fehlt = [n for n in design.NETS if n != 'GND' and n not in verdrahtet]
    pruefe(not fehlt, 'jedes Signalnetz hat Leiterbahnen', str(fehlt))


# =====================================================================
#  T6  unabhaengige Abstandspruefung auf der Platine
# =====================================================================
def _seg_abstand(a1, a2, b1, b2):
    def punkt_seg(p, s1, s2):
        dx, dy = s2[0]-s1[0], s2[1]-s1[1]
        L = dx*dx + dy*dy
        t = 0.0 if L == 0 else max(0.0, min(1.0, ((p[0]-s1[0])*dx + (p[1]-s1[1])*dy)/L))
        return math.hypot(p[0]-s1[0]-t*dx, p[1]-s1[1]-t*dy)
    def kreuzt(p1, p2, p3, p4):
        def o(a, b, c):
            v = (b[1]-a[1])*(c[0]-b[0]) - (b[0]-a[0])*(c[1]-b[1])
            return 0 if abs(v) < 1e-12 else (1 if v > 0 else 2)
        o1, o2, o3, o4 = o(p1,p2,p3), o(p1,p2,p4), o(p3,p4,p1), o(p3,p4,p2)
        return o1 != o2 and o3 != o4
    if kreuzt(a1, a2, b1, b2):
        return 0.0
    return min(punkt_seg(a1, b1, b2), punkt_seg(a2, b1, b2),
               punkt_seg(b1, a1, a2), punkt_seg(b2, a1, a2))


def t6_abstaende():
    print('T6  Abstaende auf der Platine (unabhaengig von KiCad)')
    import routes, layout_pcb as P
    KLASSE = {n: (0.6 if n in ('VBUS','VBAT','VBAT_SW','BATT_P','+3V3','+3V3_MCU') else 0.3)
              for n in design.NETS}
    MIN = 0.2                                   # kleinster Abstand laut Entwurfsregeln
    # Kupfer einsammeln: (netz, lage, art, geometrie, halbe_breite)
    stuecke = []
    for netz, lage, breite, a, b in routes.TRACKS:
        stuecke.append((netz, lage, 'seg', (a, b), breite/2))
    for netz, x, y, dia, drill in routes.VIAS:
        stuecke.append((netz, 'both', 'kreis', (x, y), dia/2))
    padnet = {(r, p): n for n, l in design.NETS.items() for r, p in l}
    for ref, (x, y, rot) in P.PLACE.items():
        node = libs.load_footprint(design.COMPONENTS[ref][2])
        for pad in findall(node, 'pad'):
            nr = str(pad[1])
            at, sz = find(pad, 'at'), find(pad, 'size')
            w, h = float(sz[1])/2, float(sz[2])/2
            prot = float(at[3]) if len(at) > 3 else 0.0
            if round((prot + rot) % 180) == 90:
                w, h = h, w
            cx, cy = libs.fp_transform(float(at[1]), float(at[2]), x, y, rot)
            lage = 'both' if pad[2] != 'smd' else 'F.Cu'
            stuecke.append((padnet.get((ref, nr)), lage, 'rect', (cx, cy, w, h), 0.0))

    def lagen_treffen(a, b):
        return a == b or a == 'both' or b == 'both'

    def abstand(A, B):
        _, _, ta, ga, ra = A
        _, _, tb, gb, rb = B
        if ta == 'seg' and tb == 'seg':
            return _seg_abstand(ga[0], ga[1], gb[0], gb[1]) - ra - rb
        if ta == 'rect' or tb == 'rect':
            if ta != 'rect':
                A, B = B, A
                _, _, ta, ga, ra = A
                _, _, tb, gb, rb = B
            cx, cy, w, h = ga
            ecken = [(cx-w, cy-h), (cx+w, cy-h), (cx+w, cy+h), (cx-w, cy+h)]
            kanten = list(zip(ecken, ecken[1:] + ecken[:1]))
            if tb == 'seg':
                d = min(_seg_abstand(k[0], k[1], gb[0], gb[1]) for k in kanten)
                if (cx-w <= gb[0][0] <= cx+w and cy-h <= gb[0][1] <= cy+h):
                    d = 0.0
                return d - rb
            if tb == 'kreis':
                dx = max(abs(gb[0]-cx) - w, 0.0)
                dy = max(abs(gb[1]-cy) - h, 0.0)
                return math.hypot(dx, dy) - rb
            dxr = max(abs(gb[0]-cx) - w - gb[2], 0.0)
            dyr = max(abs(gb[1]-cy) - h - gb[3], 0.0)
            return math.hypot(dxr, dyr)
        if ta == 'kreis' and tb == 'kreis':
            return math.hypot(ga[0]-gb[0], ga[1]-gb[1]) - ra - rb
        if ta == 'kreis':
            A, B = B, A
            _, _, ta, ga, ra = A
            _, _, tb, gb, rb = B
        return _seg_abstand(ga[0], ga[1], (gb[0], gb[1]), (gb[0], gb[1])) - ra - rb

    verstoss = []
    n = len(stuecke)
    for i in range(n):
        A = stuecke[i]
        if A[0] is None:
            continue
        for j in range(i+1, n):
            B = stuecke[j]
            if B[0] is None or A[0] == B[0] or not lagen_treffen(A[1], B[1]):
                continue
            # grobe Vorpruefung ueber Huellrechtecke
            d = abstand(A, B)
            if d < MIN - 1e-6:
                verstoss.append((A[0], B[0], round(d, 3), A[2], B[2]))
    pruefe(not verstoss, 'kein Abstand unter %.2f mm' % MIN,
           '%d Verstoesse, z.B. %s' % (len(verstoss), verstoss[:3]))
    print('     %d Kupferstuecke geprueft' % n)



# =====================================================================
#  T7  erzeugte Schaltplandateien
# =====================================================================
def _sch_lesen(pfad):
    return parse(open(pfad, encoding='utf-8').read())


def t7_schaltplan(datei, layoutmodul):
    print('T7  Schaltplan %s' % os.path.basename(datei))
    import importlib
    L = importlib.import_module(layoutmodul)
    n = _sch_lesen(datei)

    # --- Bauteile: jedes genau einmal, Wert und Footprint stimmen -----------
    gefunden = {}
    pwr = {}
    for s in findall(n, 'symbol'):
        lid = find(s, 'lib_id')
        if lid is None:
            continue
        props = {str(p[1]): str(p[2]) for p in findall(s, 'property')}
        ref = props.get('Reference', '')
        at = find(s, 'at')
        pos = (round(float(at[1]), 3), round(float(at[2]), 3))
        if ref.startswith('#'):
            pwr.setdefault(pos, []).append(props.get('Value', ''))
            continue
        pruefe(ref not in gefunden, 'Referenz nur einmal vergeben', ref)
        gefunden[ref] = (str(lid[1]), props, pos, find(s, 'mirror'))
    pruefe(set(gefunden) == set(design.COMPONENTS), 'alle Bauteile im Schaltplan',
           'fehlt %s / zuviel %s' % (sorted(set(design.COMPONENTS) - set(gefunden)),
                                     sorted(set(gefunden) - set(design.COMPONENTS))))
    for ref, (lid, props, pos, mir) in gefunden.items():
        symbol, wert, fp, beschr = design.COMPONENTS[ref]
        pruefe(lid == symbol, 'Symbol stimmt', '%s: %s statt %s' % (ref, lid, symbol))
        pruefe(props.get('Value') == wert, 'Wert stimmt',
               '%s: %s statt %s' % (ref, props.get('Value'), wert))
        pruefe(props.get('Footprint') == fp, 'Footprint stimmt',
               '%s: %s statt %s' % (ref, props.get('Footprint'), fp))
        soll = L.PLACE[ref][:2]
        pruefe(nah(pos[0], soll[0], 1e-3) and nah(pos[1], soll[1], 1e-3),
               'Position stimmt mit dem Layoutmodul', '%s %s statt %s' % (ref, pos, soll))

    # --- zwei verschiedene Versorgungssymbole duerfen nicht aufeinander liegen
    for p, namen in pwr.items():
        pruefe(len(set(namen)) == 1, 'kein Versorgungskurzschluss',
               '%s: %s' % (p, namen))

    # --- Draehte: keine Laenge null, alles im 1,27-Raster -------------------
    draehte = []
    for w in findall(n, 'wire'):
        pts = findall(find(w, 'pts'), 'xy')
        a = (round(float(pts[0][1]), 3), round(float(pts[0][2]), 3))
        b = (round(float(pts[1][1]), 3), round(float(pts[1][2]), 3))
        draehte.append((a, b))
    pruefe(all(a != b for a, b in draehte), 'kein Draht der Laenge null')
    ausserraster = [p for a, b in draehte for p in (a, b)
                    if abs(p[0] / 1.27 - round(p[0] / 1.27)) > 1e-6
                    or abs(p[1] / 1.27 - round(p[1] / 1.27)) > 1e-6]
    pruefe(not ausserraster, 'alle Drahtenden im 1,27-mm-Raster',
           str(sorted(set(ausserraster))[:4]))

    # --- jeder Pin ist angebunden -------------------------------------------
    endpunkte = {}
    for a, b in draehte:
        endpunkte[a] = endpunkte.get(a, 0) + 1
        endpunkte[b] = endpunkte.get(b, 0) + 1

    def auf_draht(p):
        if p in endpunkte:
            return True
        for a, b in draehte:                      # Punkt liegt mitten im Draht
            if abs((b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])) < 1e-6:
                if (min(a[0], b[0]) - 1e-6 <= p[0] <= max(a[0], b[0]) + 1e-6 and
                        min(a[1], b[1]) - 1e-6 <= p[1] <= max(a[1], b[1]) + 1e-6):
                    return True
        return False

    marken = set()
    for tag in ('label', 'global_label', 'hierarchical_label'):
        for l in findall(n, tag):
            at = find(l, 'at')
            marken.add((round(float(at[1]), 3), round(float(at[2]), 3)))
    nc = set()
    for k in findall(n, 'no_connect'):
        at = find(k, 'at')
        nc.add((round(float(at[1]), 3), round(float(at[2]), 3)))

    offen = []
    for ref, (lid, props, pos, mir) in gefunden.items():
        if lid.startswith('Mechanical'):
            continue
        rot = float(find(_sym_of(n, ref), 'at')[3])
        m = 'y' if mir is not None and str(mir[1]) == 'y' else \
            ('x' if mir is not None and str(mir[1]) == 'x' else None)
        for num, name, et, px, py, pa, pl in libs.symbol_pins(lid):
            p = libs.sym_transform(px, py, pos[0], pos[1], rot, m)
            p = (round(p[0], 3), round(p[1], 3))
            if not (auf_draht(p) or p in marken or p in nc or p in pwr):
                offen.append((ref, num, p))
    pruefe(not offen, 'jeder Pin ist angebunden', str(offen[:5]))

    # --- Verknuepfungspunkte: ueberall, wo drei Draehte zusammenkommen -------
    junc = set()
    for j in findall(n, 'junction'):
        at = find(j, 'at')
        junc.add((round(float(at[1]), 3), round(float(at[2]), 3)))
    noetig = {p for p, c in endpunkte.items() if c >= 3}
    pruefe(noetig <= junc, 'Verknuepfungspunkt an jeder T-Stelle',
           str(sorted(noetig - junc)[:4]))


def _sym_of(n, ref):
    for s in findall(n, 'symbol'):
        for p in findall(s, 'property'):
            if str(p[1]) == 'Reference' and str(p[2]) == ref:
                return s
    return None


# =====================================================================
#  T8  erzeugte Platinendatei
# =====================================================================
def t8_platine(datei):
    print('T8  Platine %s' % os.path.basename(datei))
    import layout_pcb as P
    import routes
    n = _sch_lesen(datei)

    # KiCad 9 fuehrt oben eine Netztabelle, KiCad 10 nicht mehr - beides zulassen
    tabelle = {int(x[1]): str(x[2]) for x in findall(n, 'net') if len(x) > 2}
    if tabelle:
        pruefe(tabelle.get(0) == '', 'Netz 0 ist das leere Netz')
        for netz in design.NETS:
            pruefe(netz in tabelle.values(), 'Netz in der Platine bekannt', netz)

    def padnetz(pad):
        """Netzname eines Pads, unabhaengig von der KiCad-Fassung."""
        k = find(pad, 'net')
        if k is None:
            return None
        if len(k) > 2:                       # (net 5 "GND")
            return str(k[2])
        wert = k[1]
        if isinstance(wert, Str):            # (net "GND")
            return str(wert)
        return None                          # (net 0)

    padnet = {(r, p): net for net, l in design.NETS.items() for r, p in l}
    gefunden = set()
    falsch = []
    for fp in findall(n, 'footprint'):
        props = {str(p[1]): str(p[2]) for p in findall(fp, 'property')}
        ref = props.get('Reference', '')
        gefunden.add(ref)
        at = find(fp, 'at')
        soll = P.PLACE.get(ref)
        if soll:
            pruefe(nah(float(at[1]) - P.BX, soll[0], 1e-3)
                   and nah(float(at[2]) - P.BY, soll[1], 1e-3),
                   'Bauteil an der geplanten Stelle', ref)
            rot = float(at[3]) if len(at) > 3 else 0.0
            pruefe(nah(rot % 360, soll[2] % 360), 'Drehung stimmt',
                   '%s: %g statt %g' % (ref, rot, soll[2]))
        for pad in findall(fp, 'pad'):
            nr = str(pad[1])
            ist = padnetz(pad)
            soll_netz = padnet.get((ref, nr))
            if soll_netz and ist != soll_netz:
                falsch.append((ref, nr, ist, soll_netz))
            if soll_netz is None and ist is not None and not ist.startswith('unconnected-'):
                falsch.append((ref, nr, ist, 'kein Netz'))
    pruefe(set(design.COMPONENTS) == gefunden, 'alle Bauteile auf der Platine',
           'fehlt %s' % sorted(set(design.COMPONENTS) - gefunden))
    pruefe(not falsch, 'jedes Pad hat das richtige Netz', str(falsch[:5]))

    # Leiterbahnen und Vias
    lagen = set()
    breiten = set()
    for seg in findall(n, 'segment'):
        lagen.add(str(find(seg, 'layer')[1]))
        breiten.add(float(find(seg, 'width')[1]))
    pruefe(lagen <= {'F.Cu', 'B.Cu'}, 'nur die beiden Kupferlagen benutzt', str(lagen))
    pruefe(min(breiten) >= 0.2, 'kleinste Leiterbahn mindestens 0,2 mm', str(sorted(breiten)))

    bohrungen = []
    for v in findall(n, 'via'):
        bohrungen.append(float(find(v, 'drill')[1]))
    for fp in findall(n, 'footprint'):
        for pad in findall(fp, 'pad'):
            d = find(pad, 'drill')
            if d is not None and pad[2] != 'np_thru_hole':
                bohrungen.append(float(d[1]))
    pruefe(bohrungen and min(bohrungen) >= 0.3, 'kleinste Bohrung mindestens 0,3 mm',
           str(sorted(set(bohrungen))[:4]))

    # Platinenumriss geschlossen
    kanten = [(find(l, 'start'), find(l, 'end')) for l in findall(n, 'gr_line')
              if str(find(l, 'layer')[1]) == 'Edge.Cuts']
    pruefe(len(kanten) == 4, 'Umriss aus vier Kanten', str(len(kanten)))
    punkte = {}
    for a, b in kanten:
        for q in (a, b):
            k = (round(float(q[1]), 3), round(float(q[2]), 3))
            punkte[k] = punkte.get(k, 0) + 1
    pruefe(all(v == 2 for v in punkte.values()), 'Umriss ist geschlossen', str(punkte))

    # Masseflaechen muessen gefuellt sein - sonst fehlt in den Gerbern die
    # gesamte Massefläche, ohne dass es irgendwo auffaellt
    zonen = findall(n, 'zone')
    kupferzonen = [z for z in zonen if find(z, 'keepout') is None]
    pruefe(kupferzonen, 'Kupferzonen vorhanden', str(len(zonen)))
    gefuellt = [z for z in kupferzonen if findall(z, 'filled_polygon')]
    pruefe(len(gefuellt) == len(kupferzonen),
           'alle Kupferzonen sind gefuellt',
           '%d von %d gefuellt - erzeugen.sh muss den Fuellschritt ausfuehren'
           % (len(gefuellt), len(kupferzonen)))

    # Antennensperrflaeche: kein Kupfer darin
    kx1, ky1, kx2, ky2, _ = P.KEEPOUTS[0]
    drin = []
    for netz, lage, br, a, b in routes.TRACKS:
        for p in (a, b):
            if kx1 <= p[0] <= kx2 and ky1 <= p[1] <= ky2:
                drin.append(('Bahn', netz, p))
    for netz, x, y, dia, drill in routes.VIAS:
        if kx1 <= x <= kx2 and ky1 <= y <= ky2:
            drin.append(('Via', netz, (x, y)))
    pruefe(not drin, 'kein Kupfer in der Antennensperrflaeche', str(drin[:4]))



# =====================================================================
#  T9  Schaltungstopologie und Ruhestrom
# =====================================================================
def _wert(text):
    """'6k8' -> 6800.0, '100R' -> 100.0, '0R' -> 0.0"""
    t = text.replace(' ', '')
    for e, f in (('k', 1e3), ('M', 1e6), ('R', 1.0)):
        if e in t:
            a, _, b = t.partition(e)
            return (float(a) + (float(b) / 10 ** len(b) if b else 0)) * f
    return float(t)


def t9_topologie():
    print('T9  Schaltungstopologie und Ruhestrom')
    netz_von = {(r, p): n for n, l in design.NETS.items() for r, p in l}

    # --- Widerstandsgraph: nur echte Widerstaende und die Sicherung ---------
    kanten = []
    for ref, (symbol, wert, fp, _b) in design.COMPONENTS.items():
        if symbol not in ('Device:R', 'Device:Polyfuse'):
            continue
        a, b = netz_von.get((ref, '1')), netz_von.get((ref, '2'))
        if a and b:
            kanten.append((a, b, ref, _wert(wert) if symbol == 'Device:R' else 1.0))

    from collections import defaultdict
    nachbar = defaultdict(list)
    for a, b, ref, w in kanten:
        nachbar[a].append((b, ref, w))
        nachbar[b].append((a, ref, w))

    def pfade(start, ziel, gesehen=None, weg=None):
        gesehen = gesehen or {start}
        weg = weg or []
        for nx, ref, w in nachbar[start]:
            if nx in gesehen:
                continue
            if nx == ziel:
                yield weg + [(ref, w)]
            else:
                yield from pfade(nx, ziel, gesehen | {nx}, weg + [(ref, w)])

    # 9a  kein rein ohmscher Pfad von einer Versorgung nach Masse
    #     (der waere ein Dauerstrom und wuerde NF-04 sprengen)
    for rail in ('VBUS', 'VBAT', 'VBAT_SW', '+3V3', '+3V3_MCU'):
        gefunden = list(pfade(rail, 'GND'))
        pruefe(not gefunden, 'kein Dauerstrompfad %s -> GND' % rail,
               str([[r for r, _ in p] for p in gefunden]))

    # 9b  +3V3 und +3V3_MCU haengen ausschliesslich ueber R3 zusammen
    wege = list(pfade('+3V3', '+3V3_MCU'))
    pruefe(len(wege) == 1 and wege[0] == [('R3', 0.0)],
           '+3V3 und +3V3_MCU nur ueber R3 = 0 R verbunden', str(wege))

    # 9c  Tasterstrom: Pull-up und Kontaktstrombegrenzung
    tast = list(pfade('+3V3_MCU', 'BTN_CON'))
    pruefe(len(tast) == 1, 'genau ein Weg vom Netz zum Tasteranschluss', str(tast))
    if tast:
        R = sum(w for _, w in tast[0])
        pruefe(nah(R, 10000 + 100 + 220, 1.0), 'Gesamtwiderstand 10,32 kOhm',
               '%.0f Ohm ueber %s' % (R, [r for r, _ in tast[0]]))
        print('     Taster gedrueckt: %.2f mA aus dem Netz' % (3.3 / R * 1000))
        # Entladestrom des Entprellkondensators ueber den Kontakt
        rk = sum(w for r, w in tast[0] if r in ('R11', 'R12'))
        i_kontakt = 3.3 / rk * 1000
        pruefe(5.0 <= i_kontakt <= 15.0, 'Kontaktstrom im Bereich 5..15 mA',
               '%.1f mA' % i_kontakt)
        print('     Kontaktstrom beim Entladen: %.1f mA' % i_kontakt)

    # 9d  Ladestrom des MCP73831
    r1 = _wert(design.COMPONENTS['R1'][1])
    pruefe(nah(r1, 6800.0), 'R_prog = 6,8 kOhm', str(r1))
    i_chg = 1000.0 / r1 * 1000
    pruefe(140 <= i_chg <= 155, 'Ladestrom 147 mA', '%.0f mA' % i_chg)
    print('     Ladestrom: %.0f mA  (0,%d C bei 500 mAh)' % (i_chg, round(i_chg/500*10)))

    # 9e  LED-Stroeme
    r2 = _wert(design.COMPONENTS['R2'][1])
    i_lade = (5.0 - 2.0) / r2 * 1000
    pruefe(1.0 <= i_lade <= 10.0, 'Lade-LED 1..10 mA', '%.1f mA' % i_lade)
    r14 = _wert(design.COMPONENTS['R14'][1])
    i_betrieb = (3.3 - 2.0) / r14 * 1000
    pruefe(0.5 <= i_betrieb <= 5.0, 'Betriebs-LED 0,5..5 mA', '%.1f mA' % i_betrieb)
    print('     Lade-LED %.1f mA, Betriebs-LED %.1f mA' % (i_lade, i_betrieb))

    # 9f  Piezo: Spitzenstrom aus dem GPIO gegen das Datenblatt
    r13 = _wert(design.COMPONENTS['R13'][1])
    i_piezo = 3.3 / r13 * 1000
    pruefe(i_piezo <= 28.0, 'Piezostrom hoechstens 28 mA (I_OL des ESP32-C3)',
           '%.1f mA bei R13 = %s' % (i_piezo, design.COMPONENTS['R13'][1]))
    pruefe(i_piezo <= 20.0, 'Piezostrom auch unter der Voreinstellung 20 mA',
           '%.1f mA' % i_piezo)
    print('     Piezo-Spitzenstrom: %.1f mA' % i_piezo)

    # 9g  Entprellzeitkonstante
    r10 = _wert(design.COMPONENTS['R10'][1])
    c11 = 100e-9
    tau = r10 * c11 * 1000
    pruefe(0.5 <= tau <= 2.0, 'Entprellzeitkonstante 0,5..2 ms', '%.2f ms' % tau)
    print('     Entprellung: tau = %.2f ms' % tau)

    # 9h  Reset-Zeitkonstante
    r4 = _wert(design.COMPONENTS['R4'][1])
    pruefe(0.5 <= r4 * 100e-9 * 1000 <= 2.0, 'Reset-Zeitkonstante 0,5..2 ms')

    # 9i  Displaypfad: genau ein Serienwiderstand je Signal, alle gleich gross
    paare = [('SCLK_MCU', 'SCLK'), ('MOSI_MCU', 'MOSI'),
             ('OLED_RES_MCU', 'OLED_RES'), ('OLED_DC_MCU', 'OLED_DC'),
             ('OLED_CS_MCU', 'OLED_CS')]
    werte = set()
    for a, b in paare:
        w = [p for p in pfade(a, b)]
        pruefe(len(w) == 1 and len(w[0]) == 1,
               'genau ein Serienwiderstand zwischen %s und %s' % (a, b), str(w))
        if w:
            werte.add(w[0][0][1])
            # MCU-Seite haengt am Modul, Displayseite am Steckverbinder
            mcu = [r for r, p in design.NETS[a] if r == 'U1']
            con = [r for r, p in design.NETS[b] if r == 'J3']
            pruefe(mcu and con, 'Widerstand liegt zwischen Modul und Steckverbinder',
                   '%s/%s' % (a, b))
    pruefe(len(werte) == 1 and nah(werte.pop(), 68.0), 'alle fuenf mit 68 Ohm')

    # 9j  Strapping-Pins haben einen Pull-up nach +3V3_MCU
    for pin, netz in (('16', 'IO2'), ('7', 'OLED_CS_MCU')):
        w = list(pfade('+3V3_MCU', netz))
        pruefe(len(w) == 1 and 8000 <= w[0][0][1] <= 12000,
               'Strapping-Pin %s hat 10-k-Pull-up' % netz, str(w))

    # 9k  Akkupfad: Sicherung liegt zwischen Buchse und allem anderen
    pruefe(('F1', '1') in [(r, p) for r, p in design.NETS['BATT_P']],
           'Sicherung liegt direkt an der Akkubuchse')
    pruefe({r for r, p in design.NETS['BATT_P']} == {'J2', 'F1'},
           'am Buchsennetz haengt nur die Sicherung',
           str(sorted({r for r, p in design.NETS['BATT_P']})))
    pruefe(('D3', '1') in design.NETS['VBAT'], 'Schutzdiode liegt hinter der Sicherung')

    # 9l  Abblockung: jeder Versorgungspin eines ICs hat einen Kondensator im Netz
    for ref, pin, netz in (('U1', '1', '+3V3_MCU'), ('U2', '4', 'VBUS'),
                           ('U3', '1', 'VBAT_SW'), ('U3', '5', '+3V3'),
                           ('D1', '5', 'VBUS')):
        kond = [r for r, p in design.NETS[netz]
                if design.COMPONENTS[r][0] == 'Device:C']
        pruefe(kond, 'Abblockkondensator an %s.%s (%s)' % (ref, pin, netz), str(kond))


# =====================================================================
#  T10  Abstaende, die die Funktion bestimmen
# =====================================================================
def t10_kritische_abstaende():
    print('T10 funktionskritische Abstaende')
    import layout_pcb as P
    pos = {}
    for ref, (x, y, rot) in P.PLACE.items():
        for nr, (px, py) in libs.fp_pads(design.COMPONENTS[ref][2]).items():
            pos[(ref, nr)] = libs.fp_transform(px, py, x, y, rot)
    d = lambda a, b: math.hypot(pos[a][0] - pos[b][0], pos[a][1] - pos[b][1])

    grenzen = [
        (('C9', '1'), ('U1', '1'), 5.0, 'HF-Abblockung am Funkmodul'),
        (('C8', '1'), ('U1', '1'), 15.0, 'Stuetzkondensator am Funkmodul'),
        (('C7', '1'), ('U3', '5'), 8.0, 'HF-Abblockung am Reglerausgang'),
        (('C6', '1'), ('U3', '5'), 10.0, 'Stuetzkondensator am Reglerausgang'),
        (('C5', '1'), ('U3', '1'), 10.0, 'Eingangskondensator des Reglers'),
        (('C2', '1'), ('U2', '4'), 15.0, 'Abblockung am Laderegler'),
        (('C11', '1'), ('U1', '15'), 10.0, 'Entprellkondensator am Eingang'),
        (('R5', '1'), ('U1', '3'), 12.0, 'Serienterminierung SCLK'),
        (('R6', '1'), ('U1', '4'), 12.0, 'Serienterminierung MOSI'),
        (('R7', '1'), ('U1', '5'), 12.0, 'Serienterminierung RES'),
        (('R8', '1'), ('U1', '6'), 12.0, 'Serienterminierung DC'),
        (('R9', '1'), ('U1', '7'), 12.0, 'Serienterminierung CS'),
    ]
    for a, b, grenze, name in grenzen:
        ist = d(a, b)
        pruefe(ist <= grenze, '%s hoechstens %.0f mm' % (name, grenze),
               '%.1f mm' % ist)
    print('     C9 %.1f mm, C8 %.1f mm, R5..R9 %.1f..%.1f mm'
          % (d(('C9', '1'), ('U1', '1')), d(('C8', '1'), ('U1', '1')),
             min(d((r, '1'), ('U1', p)) for r, p in
                 (('R5','3'),('R6','4'),('R7','5'),('R8','6'),('R9','7'))),
             max(d((r, '1'), ('U1', p)) for r, p in
                 (('R5','3'),('R6','4'),('R7','5'),('R8','6'),('R9','7')))))

    # Strombelastbarkeit nach IPC-2221, Aussenlage, 35 um Kupfer, 10 K Erwaermung
    #   I = k * dT^0.44 * A^0.725   mit k = 0.048 und A in mil^2
    def ipc_strom(breite_mm, dicke_um=35.0, dT=10.0):
        A_mil2 = breite_mm * (dicke_um / 1000.0) * 1550.0
        return 0.048 * dT ** 0.44 * A_mil2 ** 0.725

    import routes
    strom = {'VBUS': 0.25, 'VBAT': 0.35, 'BATT_P': 0.35, 'VBAT_SW': 0.35,
             '+3V3': 0.35, '+3V3_MCU': 0.35}
    for netz, i_max in sorted(strom.items()):
        b = min(t[2] for t in routes.TRACKS if t[0] == netz)
        i_zul = ipc_strom(b)
        pruefe(i_zul >= i_max, 'Querschnitt reicht fuer %s' % netz,
               '%.2f mm breit traegt %.2f A, gebraucht %.2f A' % (b, i_zul, i_max))
        print('     %-9s %.2f mm -> %.2f A zulaessig, %.2f A gebraucht'
              % (netz, b, i_zul, i_max))
    # die duennste Signalbahn muss den Dauerstrom des Moduls tragen koennen
    duennste = min(t[2] for t in routes.TRACKS)
    pruefe(ipc_strom(duennste) >= 0.05, 'auch die duennste Bahn traegt genug',
           '%.2f mm -> %.2f A' % (duennste, ipc_strom(duennste)))



# =====================================================================
#  T11  Fertigungsunterlagen gegen die Platine
# =====================================================================
def t11_fertigung():
    print('T11 Fertigungsunterlagen')
    import re
    fert = os.path.join(WURZEL, 'fertigung')
    if not os.path.isdir(fert):
        pruefe(False, 'Fertigungsordner vorhanden'); return
    pcb = parse(open(os.path.join(WURZEL, 'flappy-esp32c3.kicad_pcb'),
                     encoding='utf-8').read())

    # Bohrungen zaehlen: Platine gegen Excellon-Datei
    pth_soll = len(findall(pcb, 'via'))
    npth_soll = 0
    for fp in findall(pcb, 'footprint'):
        for pad in findall(fp, 'pad'):
            if pad[2] == 'thru_hole':
                pth_soll += 1
            elif pad[2] == 'np_thru_hole':
                npth_soll += 1

    def bohrungen(datei):
        if not os.path.exists(datei):
            return None
        n, im_koerper = 0, False
        for zeile in open(datei):
            z = zeile.strip()
            if z == 'M30':
                break
            if z.startswith('T') and z[1:].isdigit():
                im_koerper = True
                continue
            if im_koerper and z.startswith('X'):
                n += 1
        return n

    pth = bohrungen(os.path.join(fert, 'flappy-esp32c3-PTH.drl'))
    npth = bohrungen(os.path.join(fert, 'flappy-esp32c3-NPTH.drl'))
    pruefe(pth == pth_soll, 'Zahl der durchkontaktierten Bohrungen stimmt',
           '%s in der Datei, %d auf der Platine' % (pth, pth_soll))
    pruefe(npth == npth_soll == 4, 'vier Befestigungsbohrungen ohne Kupfer',
           '%s / %d' % (npth, npth_soll))

    # Umriss-Gerber muss die Platinengroesse abbilden
    import layout_pcb as P
    gm1 = os.path.join(fert, 'flappy-esp32c3-Edge_Cuts.gm1')
    if os.path.exists(gm1):
        koord = re.findall(r'X(-?\d+)Y(-?\d+)D0[12]\*', open(gm1).read())
        if koord:
            xs = [int(a) for a, b in koord]
            ys = [int(b) for a, b in koord]
            br = (max(xs) - min(xs)) / 1e6
            ho = (max(ys) - min(ys)) / 1e6
            pruefe(nah(br, P.W, 0.05) and nah(ho, P.H, 0.05),
                   'Umriss im Gerber ist %g x %g mm' % (P.W, P.H),
                   '%.2f x %.2f mm' % (br, ho))
        else:
            pruefe(False, 'Umriss-Gerber enthaelt Koordinaten')

    # Kupferlagen muessen gefuellte Bereiche enthalten (Masseflaeche)
    for name, datei in (('Oberseite', 'flappy-esp32c3-F_Cu.gtl'),
                        ('Rueckseite', 'flappy-esp32c3-B_Cu.gbl')):
        p = os.path.join(fert, datei)
        if os.path.exists(p):
            inhalt = open(p).read()
            pruefe(inhalt.count('G36*') >= 1, 'Masseflaeche im Gerber (%s)' % name,
                   '%d Flaechen' % inhalt.count('G36*'))

    # Stueckliste: alle bestueckten Bauteile, keine Pruefpunkte oder Bohrungen
    sl = os.path.join(WURZEL, 'ausgabe', 'stueckliste.csv')
    if os.path.exists(sl):
        text = open(sl, encoding='utf-8').read()
        refs = set()
        for zeile in text.splitlines()[1:]:
            feld = zeile.split(';')[0].strip('"')
            for teil in feld.split(','):
                teil = teil.strip()
                if '-' in teil and teil[0].isalpha():
                    praefix = re.match(r'[A-Za-z]+', teil).group(0)
                    a, b = teil.split('-')
                    for i in range(int(a[len(praefix):]), int(b[len(praefix):]) + 1):
                        refs.add('%s%d' % (praefix, i))
                elif teil:
                    refs.add(teil)
        soll = {r for r in design.COMPONENTS
                if not r.startswith('TP') and not r.startswith('H')}
        pruefe(refs == soll, 'Stueckliste enthaelt genau die bestueckten Bauteile',
               'fehlt %s / zuviel %s' % (sorted(soll - refs), sorted(refs - soll)))
        pruefe(not [r for r in refs if r.startswith('TP')],
               'keine Pruefpunkte in der Stueckliste')

    # Bestueckungsdatei: eine Zeile je bestuecktem Bauteil
    pos = os.path.join(fert, 'flappy-esp32c3-bestueckung.csv')
    if os.path.exists(pos):
        zeilen = [z for z in open(pos, encoding='utf-8').read().splitlines()[1:] if z.strip()]
        pruefe(len(zeilen) >= 40, 'Bestueckungsdatei enthaelt alle Bauteile',
               '%d Zeilen' % len(zeilen))


if __name__ == '__main__':
    t1_sexp()
    t2_transformationen()
    t3_entwurfsdaten()
    t4_bibliotheken()
    t5_verdrahter()
    t6_abstaende()
    t7_schaltplan(os.path.join(WURZEL, 'flappy-esp32c3.kicad_sch'), 'layout_sch')
    t8_platine(os.path.join(WURZEL, 'flappy-esp32c3.kicad_pcb'))
    t9_topologie()
    t10_kritische_abstaende()
    t11_fertigung()
    print('\n%d Pruefungen, %d Fehler' % (_geprueft, len(_fehler)))
    sys.exit(1 if _fehler else 0)
