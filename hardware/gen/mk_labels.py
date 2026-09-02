# -*- coding: utf-8 -*-
"""Sucht fuer jede Referenzbezeichnung eine freie Stelle auf dem Bestueckungsdruck."""
import math
import design, libs, layout_pcb as P
from sexp import find, findall

SIZE = 0.8          # Texthoehe in mm
CH = 0.62           # mittlere Zeichenbreite

def pad_boxes():
    out = []
    for ref, (x, y, rot) in P.PLACE.items():
        node = libs.load_footprint(design.COMPONENTS[ref][2])
        for pad in findall(node, 'pad'):
            at, sz = find(pad, 'at'), find(pad, 'size')
            px, py = float(at[1]), float(at[2])
            w, h = float(sz[1]) / 2, float(sz[2]) / 2
            prot = float(at[3]) if len(at) > 3 else 0.0
            if round((prot + rot) % 180) == 90:
                w, h = h, w
            cx, cy = libs.fp_transform(px, py, x, y, rot)
            out.append(((cx - w - 0.15, cy - h - 0.15,
                         cx + w + 0.15, cy + h + 0.15), 'Pad'))
        for tx in findall(node, 'fp_text'):
            lay = find(tx, 'layer')
            if lay is None or str(lay[1]) != 'F.SilkS':
                continue
            a = find(tx, 'at')
            p = libs.fp_transform(float(a[1]), float(a[2]), x, y, rot)
            wtxt = len(str(tx[2])) * CH / 2 + 0.3
            out.append(((p[0] - wtxt, p[1] - 0.7, p[0] + wtxt, p[1] + 0.7), 'Druck'))
        for cc in findall(node, 'fp_circle') + findall(node, 'fp_arc'):
            lay = find(cc, 'layer')
            if lay is None or str(lay[1]) != 'F.SilkS':
                continue
            pts = []
            for k in ('center', 'end', 'start', 'mid'):
                q = find(cc, k)
                if q:
                    pts.append(libs.fp_transform(float(q[1]), float(q[2]), x, y, rot))
            if len(pts) >= 2:
                r = max(((p[0]-pts[0][0])**2 + (p[1]-pts[0][1])**2) ** 0.5 for p in pts[1:])
                out.append(((pts[0][0]-r-0.15, pts[0][1]-r-0.15,
                             pts[0][0]+r+0.15, pts[0][1]+r+0.15), 'Druck'))
        for ln in findall(node, 'fp_line') + findall(node, 'fp_rect'):
            lay = find(ln, 'layer')
            if lay is None or str(lay[1]) != 'F.SilkS':
                continue
            a, b = find(ln, 'start'), find(ln, 'end')
            p1 = libs.fp_transform(float(a[1]), float(a[2]), x, y, rot)
            p2 = libs.fp_transform(float(b[1]), float(b[2]), x, y, rot)
            out.append(((min(p1[0], p2[0]) - 0.15, min(p1[1], p2[1]) - 0.15,
                         max(p1[0], p2[0]) + 0.15, max(p1[1], p2[1]) + 0.15), 'Druck'))
    return out

def text_boxes():
    out = []
    for x, y, txt, size, layer, rot in P.TEXTS:
        if not layer.startswith('F.'):
            continue
        w = len(txt) * size * 0.78 + 0.3
        out.append(((x - 0.3, y - size / 2 - 0.3, x + w, y + size / 2 + 0.3), 'Druck'))
    return out


def track_boxes():
    out = []
    import routes
    for net, layer, w, a, b in routes.TRACKS:
        if layer != 'F.Cu':
            continue
        out.append((min(a[0], b[0]) - w / 2 - 0.1, min(a[1], b[1]) - w / 2 - 0.1,
                    max(a[0], b[0]) + w / 2 + 0.1, max(a[1], b[1]) + w / 2 + 0.1))
    for net, x, y, dia, drill in routes.VIAS:
        out.append((x - dia / 2 - 0.1, y - dia / 2 - 0.1,
                    x + dia / 2 + 0.1, y + dia / 2 + 0.1))
    return out

def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

def main():
    obst = pad_boxes() + text_boxes()
    tr = track_boxes()
    placed = []
    off = {}
    order = sorted(P.PLACE, key=lambda r: (r[0] not in 'UJDS', r))
    for ref in order:
        node = libs.load_footprint(design.COMPONENTS[ref][2])
        x, y, rot = P.PLACE[ref]
        tw, th = len(ref) * CH / 2 + 0.2, SIZE / 2 + 0.2
        best = None
        # Findet sich nichts Freies, ist die Stelle mit den wenigsten
        # Ueberdeckungen immer noch besser als ein blinder Festwert - der
        # legte den Bezeichner sonst auf die Polaritaetsmarkierung.
        notfall = None
        for d in (1.6, 2.0, 2.5, 3.1, 3.8, 4.6, 5.6, 6.8, 8.2):
            for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0),
                           (-0.8, -0.8), (0.8, -0.8), (-0.8, 0.8), (0.8, 0.8)):
                cx, cy = x + dx * d, y + dy * d
                box = (cx - tw, cy - th, cx + tw, cy + th)
                if box[0] < 0.4 or box[1] < 0.4 or box[2] > P.W - 0.4 or box[3] > P.H - 0.4:
                    continue
                kx1, ky1, kx2, ky2, _ = P.KEEPOUTS[0]
                if overlap(box, (kx1, ky1, kx2, ky2)):
                    continue
                pen = sum(1 for o in tr if overlap(box, o))
                auf_pad = sum(1 for o, art in obst
                              if art == 'Pad' and overlap(box, o))
                sonst = (sum(1 for o, art in obst
                             if art != 'Pad' and overlap(box, o))
                         + sum(1 for o in placed if overlap(box, o)))
                if auf_pad or sonst:
                    marke = (auf_pad, sonst, pen)
                    if notfall is None or marke < notfall[0]:
                        notfall = (marke, cx - x, cy - y, box)
                    continue
                if best is None or pen < best[0]:
                    best = (pen, cx - x, cy - y, box)
                if pen == 0:
                    break
            if best and best[0] == 0:
                break
        if best is None:
            if notfall is None:
                off[ref] = (0.0, -2.2)
                continue
            print('  %s beengt: %d Pad-, %d Druckueberdeckung(en) unvermeidbar'
                  % (ref, notfall[0][0], notfall[0][1]))
            best = (notfall[0][2], notfall[1], notfall[2], notfall[3])
        off[ref] = (round(best[1], 2), round(best[2], 2))
        placed.append(best[3])
    with open('labels.py', 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n"""Automatisch erzeugt von mk_labels.py."""\n')
        f.write('LABEL_OFF = %r\n' % (off,))
    print('Referenzpositionen bestimmt:', len(off))

if __name__ == '__main__':
    main()
