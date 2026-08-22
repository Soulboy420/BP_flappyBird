# -*- coding: utf-8 -*-
"""Prueft Ueberlappungen der Umrisse, Randabstand und die Antennensperrflaeche."""
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
    if ref == 'U1':      # Rumpf und Antennenausbuchtung getrennt betrachten
        raw = [(-9.75, -6.85, 9.75, 7.15), (-14.25, -18.35, 14.25, -6.85)]
    x, y, rot = P.PLACE[ref]
    out = []
    for a, b, c, d in raw:
        pts = [libs.fp_transform(u, v, x, y, rot) for u in (a, c) for v in (b, d)]
        out.append((min(p[0] for p in pts), min(p[1] for p in pts),
                    max(p[0] for p in pts), max(p[1] for p in pts)))
    return out

B = {r: boxes_of(r) for r in P.PLACE}
bad = []
for a, b in itertools.combinations(sorted(B), 2):
    for A in B[a]:
        for C in B[b]:
            if A[0] < C[2] and C[0] < A[2] and A[1] < C[3] and C[1] < A[3]:
                bad.append((a, b, round(min(A[2], C[2]) - max(A[0], C[0]), 2),
                            round(min(A[3], C[3]) - max(A[1], C[1]), 2)))
print('Umriss-Ueberlappungen:', len(bad))
for t in bad:
    print('   ', t)
edge = [r for r, bs in B.items() for x1, y1, x2, y2 in bs
        if r != 'U1' and (x1 < 0.3 or y1 < 0.3 or x2 > P.W - 0.3 or y2 > P.H - 0.3)]
print('zu dicht am Rand:', sorted(set(edge)))
kx1, ky1, kx2, ky2, _ = P.KEEPOUTS[0]
ink = [r for r, bs in B.items() for x1, y1, x2, y2 in bs
       if r != 'U1' and x1 < kx2 and kx1 < x2 and y1 < ky2 and ky1 < y2]
print('in der Antennensperrflaeche:', sorted(set(ink)))
