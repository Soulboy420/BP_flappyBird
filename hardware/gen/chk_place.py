# -*- coding: utf-8 -*-
"""Prueft die Platzierung: Umrissabstaende (Handloeten), Randabstand,
Antennensperrflaeche und die bauteilfreien Flaechen unter Modul und Breakout."""
import sys, itertools
sys.path.insert(0, '.')
import layout_pcb as P, design, libs
from sexp import find, findall

# Sonderfaelle: Koerperausdehnung fuer Footprints ohne Umriss
MANUAL = {'Buzzer_Beeper:Buzzer_12x9.5RM7.6': (-2.4, -5.05, 10.0, 5.05),
          'Button_Switch_THT:SW_Slide_SPDT_Straight_CK_OS102011MS2Q': (-3.7, -2.7, 7.7, 2.7)}

def boxes_of(ref):
    fpid = design.COMPONENTS[ref][2]
    node = libs.load_footprint(fpid)
    xs, ys = [], []
    for ln in findall(node, 'fp_line') + findall(node, 'fp_rect'):
        lay = find(ln, 'layer')
        if lay is None or str(lay[1]) != 'F.CrtYd':
            continue
        for k in ('start', 'end'):
            q = find(ln, k)
            if q:
                xs.append(float(q[1])); ys.append(float(q[2]))
    if fpid in MANUAL:
        a, b, c, d = MANUAL[fpid]
        raw = [(a, b, c, d)]
    elif xs:
        raw = [(min(xs), min(ys), max(xs), max(ys))]
    else:
        for pad in findall(node, 'pad'):
            at, sz = find(pad, 'at'), find(pad, 'size')
            px, py = float(at[1]), float(at[2])
            w, h = float(sz[1]) / 2 + 0.3, float(sz[2]) / 2 + 0.3
            xs += [px - w, px + w]; ys += [py - h, py + h]
        raw = [(min(xs), min(ys), max(xs), max(ys))]
    if ref == 'U1':
        # Rumpf und Antennenausbuchtung getrennt. Der Rumpf reicht in x bis
        # zur Aussenkante der verlaengerten Randkontakte (+-10,5 mm), nicht
        # nur bis zum Umriss des unveraenderten Footprints (+-9,75 mm).
        raw = [(-10.5, -6.85, 10.5, 7.15), (-14.25, -18.35, 14.25, -6.85)]
    x, y, rot = P.PLACE[ref]
    out = []
    for a, b, c, d in raw:
        pts = [libs.fp_transform(u, v, x, y, rot) for u in (a, c) for v in (b, d)]
        out.append((min(p[0] for p in pts), min(p[1] for p in pts),
                    max(p[0] for p in pts), max(p[1] for p in pts)))
    return out


def abstand(A, C):
    """Abstand zweier Rechtecke; negativ, wenn sie sich ueberlappen."""
    dx = max(C[0] - A[2], A[0] - C[2])
    dy = max(C[1] - A[3], A[1] - C[3])
    if dx >= 0 and dy >= 0:
        return (dx * dx + dy * dy) ** 0.5
    return max(dx, dy)


B = {r: boxes_of(r) for r in P.PLACE}
fehler = 0

# --- 1. Abstand zwischen den Bauteilen: Platz fuer die Loetspitze ---
eng = []
for a, b in itertools.combinations(sorted(B), 2):
    g = min(abstand(A, C) for A in B[a] for C in B[b])
    if g < P.LOETABSTAND:
        eng.append((round(g, 2), a, b))
eng.sort()
print('Umrissabstand unter %.1f mm: %d' % (P.LOETABSTAND, len(eng)))
for g, a, b in eng:
    print('    %-5s %-5s %6.2f mm' % (a, b, g))
fehler += len(eng)

# --- 2. Randabstand ---
edge = sorted({r for r, bs in B.items() for x1, y1, x2, y2 in bs
               if r != 'U1' and (x1 < P.RANDABSTAND or y1 < P.RANDABSTAND
                                 or x2 > P.W - P.RANDABSTAND or y2 > P.H - P.RANDABSTAND)})
print('zu dicht am Rand (< %.1f mm):' % P.RANDABSTAND, edge or 'keine')
fehler += len(edge)

# --- 3. Antennensperrflaeche ---
kx1, ky1, kx2, ky2, _ = P.KEEPOUTS[0]
ink = sorted({r for r, bs in B.items() for x1, y1, x2, y2 in bs
              if r != 'U1' and x1 < kx2 and kx1 < x2 and y1 < ky2 and ky1 < y2})
print('in der Antennensperrflaeche:', ink or 'keine')
fehler += len(ink)

# --- 4. bauteilfreie Flaechen (Projektplan 4.5.2) ---
for x1, y1, x2, y2, name in P.BAUTEILFREI:
    drin = sorted({r for r, bs in B.items() for a, b, c, d in bs
                   if r not in ('U1', 'J1') and a < x2 and x1 < c and b < y2 and y1 < d})
    print('in "%s":' % name, drin or 'keine')
    fehler += len(drin)

# --- 5. Kupferflaechen: jede muss ein Pad ihres Netzes enthalten ---
# Sonst fuellt KiCad sie und wirft sie gleich wieder als nicht angebundene
# Insel weg - die Waermeableitung waere still verschwunden.
PADNET = {(r, p): n for n, l in design.NETS.items() for r, p in l}
for x1, y1, x2, y2, netz in P.NETZONES:
    treffer = []
    for ref, (x, y, rot) in P.PLACE.items():
        node = libs.load_footprint(design.COMPONENTS[ref][2])
        for pad in findall(node, 'pad'):
            num = str(pad[1])
            if PADNET.get((ref, num)) != netz:
                continue
            at, sz = find(pad, 'at'), find(pad, 'size')
            cx, cy = libs.fp_transform(float(at[1]), float(at[2]), x, y, rot)
            w, h = float(sz[1]) / 2, float(sz[2]) / 2
            if cx + w > x1 and cx - w < x2 and cy + h > y1 and cy - h < y2:
                treffer.append('%s.%s' % (ref, num))
    flaeche = (x2 - x1) * (y2 - y1)
    print('Kupferflaeche %s: %.0f mm2, angebunden ueber %s'
          % (netz, flaeche, ', '.join(treffer) if treffer else 'NICHTS'))
    if not treffer:
        fehler += 1

# --- 6. Flaechennutzung ---
flaeche = sum((c - a) * (d - b) for r in B for a, b, c, d in B[r])
print('Platine %.0f x %.0f = %.0f mm2, Umrisse %.0f mm2, Fuellgrad %.0f %%'
      % (P.W, P.H, P.W * P.H, flaeche, 100 * flaeche / (P.W * P.H)))

if fehler:
    print('Platzierung: %d Beanstandungen' % fehler)
    sys.exit(1)
print('Platzierung in Ordnung.')
