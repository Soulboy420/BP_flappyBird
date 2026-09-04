# -*- coding: utf-8 -*-
"""Verdrahtet alle Netze mit dem Rasterverdrahter und schreibt routes.py."""
import math, sys
import numpy as np
import design, libs, layout_pcb as P
from router import Router, GRID
from sexp import find, findall

W, H = P.W, P.H
WARNUNGEN = []
# Rasterweite 0,2 mm -> Sicherheitszuschlag, damit die Rundung den
# geforderten Mindestabstand nicht unterschreitet
GRIDPAD = 0.06
CLEAR = {'Leistung': 0.2 + GRIDPAD, 'USB': 0.2 + GRIDPAD, 'Default': 0.2 + GRIDPAD}
WIDTH = {'Leistung': 0.6, 'USB': 0.3, 'Default': 0.25}
# VBUS muss zwischen den Pads des ESD-Arrays hindurch -> schmaler
#
# Lagenwechsel bepreisen (Befund M-7): Auf der Rueckseite liegt die
# durchgehende Massefläche. Jedes Signalstueck dort schneidet einen Schlitz
# hinein, und jede Bahn auf F.Cu, die darueber laeuft, muss ihren Rueckstrom um
# den Schlitz herumfuehren - gemeinsame Rueckimpedanz und damit Uebersprechen.
#
# VIA_COST ist ein einmaliger Aufschlag pro Lagenwechsel, BACK_COST ein
# Faktor je Rasterschritt auf B.Cu. Entscheidend ist BACK_COST: er macht lange
# Ausfluege auf die Rueckseite teuer, waehrend ein billiges Via das kurze
# "rueber, einmal kreuzen, sofort zurueck" erlaubt. Genau das ist gewuenscht.
#
# Messreihe ueber 18 Kombinationen, bewertet mit
#     Guete = L(B.Cu) + 2*L(B.Cu, schnelle Netze) + 3*Kreuzungen(schnell)
#   via=220 back=8   (alt)  83,9 mm | 37 Kreuzungen (25 schnell) | 241,0
#   via=2000 back=8         184,9 mm | 41 Kreuzungen (24 schnell) | 483,1
#   via=220 back=25          67,6 mm | 36 Kreuzungen (24 schnell) | 210,8
#   via=60  back=40  (neu)   60,8 mm | 36 Kreuzungen (23 schnell) | 191,8  <-
#
# Verworfen: +3V3_MCU hart auf F.Cu zu zwingen. Das Netz verschwand zwar von
# der Rueckseite, verdraengte dort aber SCLK und OLED_RES (je 17 mm auf B.Cu) -
# die Guete verschlechterte sich von 241 auf 356. Ein Versorgungsnetz auf der
# Masselage ist harmloser als ein schnelles Signal.
VIA_COST = 60.0
BACK_COST = 40.0

WIDTH_NET = {'VBUS': 0.4, 'VBAT': 0.5, '+3V3': 0.5, '+3V3_MCU': 0.5}

def cls(net):
    if net in ('VBUS', 'VBAT', 'BATT_P', '+3V3', '+3V3_MCU'):
        return 'Leistung'
    return 'USB' if net.startswith('USB_D') else 'Default'

PADNET = {(r, p): n for n, l in design.NETS.items() for r, p in l}

def pad_table():
    out = []
    for ref, (x, y, rot) in P.PLACE.items():
        fpid = design.COMPONENTS[ref][2]
        node = libs.load_footprint(fpid)
        for pad in findall(node, 'pad'):
            num = str(pad[1])
            typ = pad[2]
            at, sz = find(pad, 'at'), find(pad, 'size')
            px, py = float(at[1]), float(at[2])
            w, h = float(sz[1]) / 2, float(sz[2]) / 2
            prot = float(at[3]) if len(at) > 3 else 0.0
            if round((prot + rot) % 180) == 90:
                w, h = h, w
            cx, cy = libs.fp_transform(px, py, x, y, rot)
            layers = (0,) if typ == 'smd' else (0, 1)
            out.append((ref, num, PADNET.get((ref, num)), cx, cy, w, h, layers, typ))
    return out

PADS = pad_table()


def neuer_router():
    """Baut das Hindernisraster neu auf - fuer jeden Verlegeversuch frisch."""
    R = Router(W, H)
    for x1, y1, x2, y2, _ in P.KEEPOUTS:
        R.block_rect(None, x1 - 0.3, y1 - 0.3, x2 + 0.3, y2 + 0.3)
    R.block_rect(0, 33.2, 39.0, 48.8, H)      # keine Leiterbahnen unter dem Funkmodul
    R.block_rect(0,  0.6,  1.4, 12.6, 22.6)   # keine Leiterbahnen unter dem USB-Breakout
    for ref in ('H1', 'H2', 'H3', 'H4'):
        x, y, _ = P.PLACE[ref]
        R.block_circle(None, x, y, 1.1 + 0.35)
    for ref, num, net, cx, cy, w, h, layers, typ in PADS:
        if net is None:                       # z. B. Befestigungslaschen des Schalters
            m = 0.25 + 0.3
            R.block_rect(None if len(layers) == 2 else 0,
                         cx - w - m, cy - h - m, cx + w + m, cy + h + m)
            if typ != 'smd':
                R.block_circle(None, cx, cy, max(w, h) + m)
        else:
            R.add_pad(net, layers, cx, cy, w, h)
    return R


def pad_stummel(pad, ziel, breite=0.4):
    """Anbindung vom Padmittelpunkt an den ersten Rasterpunkt.

    Der Padmittelpunkt liegt selten genau auf dem 0,2-mm-Raster. Damit keine
    schraegen oder entarteten Segmente entstehen, wird der Versatz in bis zu
    zwei waagerechte bzw. senkrechte Stuecke zerlegt.
    """
    ax, ay = pad
    bx, by = ziel
    if abs(ax - bx) < 1e-9 and abs(ay - by) < 1e-9:
        return []                                   # Pad liegt schon im Raster
    if abs(ax - bx) < 1e-9 or abs(ay - by) < 1e-9 or \
       abs(abs(ax - bx) - abs(ay - by)) < 1e-9:
        return [((ax, ay), (bx, by))]               # schon H, V oder 45 Grad
    return [((ax, ay), (bx, ay)), ((bx, ay), (bx, by))]


ORDER = ['VBAT', 'BATT_P', 'VBUS', 'USB_DP', 'USB_DM', 'USB_DP_CON', 'USB_DM_CON',
         'USB_CC1', 'USB_CC2',
         '+3V3',
         'SCLK_MCU', 'MOSI_MCU', 'OLED_RES_MCU', 'OLED_DC_MCU', 'OLED_CS_MCU',
         'SCLK', 'MOSI', 'OLED_RES', 'OLED_DC', 'OLED_CS',
         'EN', 'BOOT', 'IO2', 'BTN', 'BTN_SW', 'BTN_CON',
         'BUZZ', 'BUZZ_P', 'LED_G', 'LED_G_A',
         'PROG', 'CHG_A', 'LED_CHG', '+3V3_MCU',
         'LDO_EN', 'VBAT_SENSE', 'VBUS_SENSE']
assert set(ORDER) == set(design.NETS) - {'GND'}, set(design.NETS) - set(ORDER) - {'GND'}

def verlege(reihenfolge):
    """Verlegt alle Netze in der angegebenen Reihenfolge.

    Gibt (Bahnen, Vias, Bericht) zurueck oder wirft router.KeinWeg. Der
    Verdrahter arbeitet Netz fuer Netz; wer zuerst kommt, bekommt den kuerzeren
    Weg. Schlaegt ein Netz fehl, ruft der Aufrufer erneut mit geaenderter
    Reihenfolge auf (siehe unten).
    """
    R = neuer_router()
    bahnen, durchkontaktierungen, bericht = [], [], []

    # Massevias der eingeklemmten Mittelpins zuerst reservieren (SOT-23, ESD-Array)
    for ref, pin in (('D1', '2'), ('U2', '2'), ('U3', '2')):
        cx, cy = [(a, b) for r, n, _, a, b, w, h, L, t in PADS if (r, n) == (ref, pin)][0]
        r = R.route_to_via('GND', (cx, cy), 0.2, 0.2, maxlen=10.0)
        if r is None:
            WARNUNGEN.append('kein Massevia (Vorabreservierung) fuer %s %s' % (ref, pin))
            bericht.append('  WARNUNG: ' + WARNUNGEN[-1])
            continue
        segs, v = r
        for a, b in pad_stummel((cx, cy), segs[0][0]):
            bahnen.append(('GND', 'F.Cu', 0.4, a, b))
            R.add_track('GND', 0, a, b, 0.4)
        for a, b, L in segs:
            bahnen.append(('GND', 'F.Cu', 0.4, a, b))
            R.add_track('GND', 0, a, b, 0.4)
        durchkontaktierungen.append(('GND', v[0], v[1], 0.8, 0.4))
        R.add_via('GND', v[0], v[1], 0.8)
        bericht.append('%-14s Massevia vorab bei %r' % (ref + '.' + pin, v))

    for net in reihenfolge:
        pts = [(cx, cy, L) for ref, num, n, cx, cy, w, h, L, t in PADS if n == net]
        c = cls(net)
        wdt = WIDTH_NET.get(net, WIDTH[c])
        hw = wdt / 2
        segs, vs = R.route(net, pts, hw, CLEAR[c],
                           via_cost=VIA_COST, back_cost=BACK_COST)
        for a, b, L in segs:
            bahnen.append((net, 'F.Cu' if L == 0 else 'B.Cu', wdt, a, b))
            R.add_track(net, L, a, b, wdt)
        for vx, vy in vs:
            durchkontaktierungen.append((net, vx, vy, 0.8, 0.4))
            R.add_via(net, vx, vy, 0.8)
        bericht.append('%-14s %2d Segmente, %d Vias' % (net, len(segs), len(vs)))
    return R, bahnen, durchkontaktierungen, bericht


import router as _router

reihenfolge = list(ORDER)
for versuch in range(1, 13):
    try:
        R, tracks, vias, bericht = verlege(reihenfolge)
        break
    except _router.KeinWeg as e:
        # Das gescheiterte Netz nach vorn holen und noch einmal versuchen.
        if e.netz not in reihenfolge or reihenfolge.index(e.netz) == 0:
            raise
        i = reihenfolge.index(e.netz)
        reihenfolge.insert(max(0, i - 4), reihenfolge.pop(i))
        print('  Versuch %d: %s war nicht verlegbar, wird frueher verlegt'
              % (versuch, e.netz))
else:
    raise SystemExit('Verdrahtung nach 12 Versuchen nicht moeglich')

if reihenfolge != ORDER:
    print('  Reihenfolge angepasst nach %d Versuch(en)' % versuch)
print('\n'.join(bericht))

obs, own = R._obstacles('GND', 0.4, 0.25)

HOLES = []
for ref, num, net, cx, cy, w, h, layers, typ in PADS:
    if typ != 'smd':
        HOLES.append((cx, cy, max(w, h)))
for ref in ('H1', 'H2', 'H3', 'H4'):
    x, y, _ = P.PLACE[ref]
    HOLES.append((x, y, 1.1))

def hole_ok(x, y, drill=0.4):
    for hx, hy, hr in HOLES:
        if ((x - hx) ** 2 + (y - hy) ** 2) ** 0.5 < drill / 2 + hr + 0.3:
            return False
    return True

def _line_free(x1, y1, x2, y2, hw):
    """True, wenn die Strecke ueberall genug Abstand zu fremdem Kupfer hat."""
    n = max(2, int(math.hypot(x2 - x1, y2 - y1) / 0.15))
    for k in range(n + 1):
        t = k / n
        px, py = x1 + (x2 - x1) * t, y1 + (y2 - y1) * t
        i1, j1 = R._idx(px - hw, py - hw)
        i2, j2 = R._idx(px + hw, py + hw)
        if obs[0][max(0, i1):i2 + 1, max(0, j1):j2 + 1].any():
            return False
    return True


def free_via(x, y, r=0.65, stub=True):
    """Sucht ringweise nach einer freien Stelle fuer ein Massevia."""
    i0, j0 = R._idx(x, y)
    for rad in range(4, 34):
        for di in range(-rad, rad + 1):
            for dj in (-rad, rad):
                for a, b in ((i0 + di, j0 + dj), (i0 + dj, j0 + di)):
                    if not (0 <= a < R.nx and 0 <= b < R.ny):
                        continue
                    px, py = R._pos(a, b)
                    ok = True
                    for L in (0, 1):
                        i1, j1 = R._idx(px - r, py - r)
                        i2, j2 = R._idx(px + r, py + r)
                        if obs[L][max(0, i1):i2 + 1, max(0, j1):j2 + 1].any():
                            ok = False
                            break
                    if ok and (not stub or _line_free(x, y, px, py, 0.45)):
                        return px, py
    return None


ngnd = 0
DONE = {('D1', '2'), ('U2', '2'), ('U3', '2'), ('U1', '19')}
for ref, num, net, cx, cy, w, h, layers, typ in PADS:
    if net != 'GND' or typ != 'smd' or (ref, num) in DONE:
        continue   # Waermepad hat eigene Vias im Footprint
    r = R.route_to_via('GND', (cx, cy), 0.2, 0.2)
    if r is None:
        WARNUNGEN.append('kein Massevia fuer %s %s' % (ref, num))
        print('  WARNUNG:', WARNUNGEN[-1])
        continue
    segs, v = r
    if not hole_ok(*v):
        WARNUNGEN.append('Bohrungsabstand zu klein bei %s %s' % (ref, num))
        print('  WARNUNG:', WARNUNGEN[-1])
        continue
    HOLES.append((v[0], v[1], 0.4))
    for a, b, L in segs:
        tracks.append(('GND', 'F.Cu', 0.4, a, b))
        R.add_track('GND', 0, a, b, 0.4)
    for a, b in pad_stummel((cx, cy), segs[0][0]):
        tracks.append(('GND', 'F.Cu', 0.4, a, b))
        R.add_track('GND', 0, a, b, 0.4)
    vias.append(('GND', v[0], v[1], 0.8, 0.4))
    R.add_via('GND', v[0], v[1], 0.8)
    ngnd += 1
print('Massevias an SMD-Pads:', ngnd)

obs, own = R._obstacles('GND', 0.4, 0.25)
# Ruecklaufpfad: neben jedem B.Cu-Stueck ein Massevia setzen (Abschnitt 5.7)
flank = 0
for net, layer, wdt, a, b in [t for t in tracks if t[1] == 'B.Cu']:
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy) or 1.0
    px, py = -dy / n, dx / n                      # Normale
    for sgn in (1, -1):
        for d in (1.1, 1.5, 2.0, 2.6):
            vx, vy = round(mx + px * d * sgn, 2), round(my + py * d * sgn, 2)
            if not (1.2 < vx < W - 1.2 and 1.2 < vy < H - 1.2):
                continue
            kx1, ky1, kx2, ky2, _ = P.KEEPOUTS[0]
            if kx1 - 1 < vx < kx2 + 1 and ky1 - 1 < vy < ky2 + 1:
                continue
            if R._clash_via('GND', vx, vy) or not hole_ok(vx, vy):
                continue
            vias.append(('GND', vx, vy, 0.8, 0.4))
            R.add_via('GND', vx, vy, 0.8)
            HOLES.append((vx, vy, 0.4))
            flank += 1
            break
print('Vias entlang der B.Cu-Stuecke:', flank)

obs, own = R._obstacles('GND', 0.4, 0.25)
stitch = 0
for gx in np.arange(5.0, W - 4.0, 8.0):
    for gy in np.arange(5.0, H - 4.0, 8.0):
        v = free_via(float(gx), float(gy), 0.7, stub=False)
        if v and abs(v[0] - gx) < 2.5 and abs(v[1] - gy) < 2.5 and hole_ok(*v):
            HOLES.append((v[0], v[1], 0.4))
            vias.append(('GND', v[0], v[1], 0.8, 0.4))
            R.add_via('GND', v[0], v[1], 0.8)
            obs, own = R._obstacles('GND', 0.4, 0.25)
            stitch += 1
print('Naehvias:', stitch)

# Waermevias am Laderegler (Befund M-2): binden die Massefluer auf F.Cu rund um
# U2 Pad 2 an die durchgehende Flaeche auf B.Cu an. Sie tragen keinen Strom,
# sondern spreizen die Verlustleistung von 0,415 W auf beide Lagen.
therm = 0
for tx, ty in getattr(P, 'THERMOVIAS', []):
    best = None
    for rad in range(1, 13):                       # 0,2 mm Raster, bis 2,4 mm
        i0, j0 = R._idx(tx, ty)
        for di in range(-rad, rad + 1):
            for dj in (-rad, rad):
                for a, b in ((i0 + di, j0 + dj), (i0 + dj, j0 + di)):
                    if not (0 <= a < R.nx and 0 <= b < R.ny):
                        continue
                    vx, vy = R._pos(a, b)
                    if R._clash_via('GND', vx, vy) or not hole_ok(vx, vy):
                        continue
                    d = math.hypot(vx - tx, vy - ty)
                    if best is None or d < best[0]:
                        best = (d, vx, vy)
        if best:
            break
    if best is None:
        print('  WARNUNG: kein Platz fuer Waermevia bei %.1f/%.1f' % (tx, ty))
        continue
    d, vx, vy = best
    vias.append(('GND', vx, vy, 0.8, 0.4))
    R.add_via('GND', vx, vy, 0.8)
    HOLES.append((vx, vy, 0.4))
    therm += 1
print('Waermevias am Laderegler:', therm)

with open('routes.py', 'w') as f:
    f.write('# -*- coding: utf-8 -*-\n')
    f.write('"""Automatisch erzeugt von autoroute.py - nicht von Hand aendern."""\n')
    f.write('TRACKS = %r\n' % (tracks,))
    f.write('VIAS = %r\n' % (vias,))
print('routes.py: %d Leiterbahnen, %d Vias' % (len(tracks), len(vias)))

if WARNUNGEN:
    # Eine nicht angebundene Masseflaeche wuerde spaeter zwar auch das DRC
    # finden, aber hier ist die Ursache noch sichtbar.
    print('\nVerdrahtung unvollstaendig:')
    for w in WARNUNGEN:
        print('  -', w)
    sys.exit(1)
