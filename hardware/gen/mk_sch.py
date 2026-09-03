# -*- coding: utf-8 -*-
"""Erzeugt flappy-esp32c3.kicad_sch aus design.py und layout_sch.py."""
import os, sys, uuid, copy, math
from sexp import parse, dump, find, findall, Str
import design, libs
import importlib, sys

LAYOUT = sys.argv[1] if len(sys.argv) > 1 else 'layout_sch'
SUFFIX = sys.argv[2] if len(sys.argv) > 2 else ''
L = importlib.import_module(LAYOUT)

PROJECT = 'flappy-esp32c3'
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..',
                                  PROJECT + SUFFIX + '.kicad_sch'))

def U(seed):
    return Str(str(uuid.uuid5(uuid.NAMESPACE_URL, 'flappy://' + seed)))

ROOT_UUID = U('sheet/root' + SUFFIX)

POWERSYM = {'GND': 'power:GND', 'VBUS': 'power:VBUS', '+3V3': 'power:+3V3',
            'VBAT': 'flappy:VBAT', 'VBAT_SW': 'flappy:VBAT_SW',
            '+3V3_MCU': 'flappy:+3V3_MCU'}
DIRVEC = {'up': (0, -1), 'down': (0, 1), 'left': (-1, 0), 'right': (1, 0)}
# Symbolgrafik zeigt in Richtung X  ->  noetige Drehung
ROT_SUPPLY = {'up': 0, 'left': 90, 'down': 180, 'right': 270}
ROT_GND    = {'down': 0, 'right': 90, 'up': 180, 'left': 270}

def rot_for(net, direction):
    return (ROT_GND if net == 'GND' else ROT_SUPPLY)[direction]

def dirname_of(vec):
    for k, v in DIRVEC.items():
        if abs(v[0] - vec[0]) < 1e-6 and abs(v[1] - vec[1]) < 1e-6:
            return k
    raise ValueError('schraege Pinrichtung: %r' % (vec,))

# ---------------------------------------------------------------- Pinpositionen
PINPOS, PINDIR = {}, {}
for ref, (x, y, rot, mir) in L.PLACE.items():
    libid = design.COMPONENTS[ref][0]
    if libid.startswith('Mechanical'):
        continue
    for num, name, etype, px, py, pang, plen in libs.symbol_pins(libid):
        PINPOS[(ref, num)] = libs.sym_transform(px, py, x, y, rot, mir)
        PINDIR[(ref, num)] = libs.pin_dir(pang, rot, mir)

def pt(item):
    return PINPOS[item] if isinstance(item, tuple) and isinstance(item[0], str) else tuple(item)

# ---------------------------------------------------------------- Drahtsegmente
segments = []
for path in L.WIRES:
    pts = [pt(i) for i in path]
    for a, b in zip(pts, pts[1:]):
        dx, dy = round(b[0] - a[0], 4), round(b[1] - a[1], 4)
        if dx == 0 and dy == 0:
            continue
        assert dx == 0 or dy == 0 or abs(abs(dx) - abs(dy)) < 1e-6, \
            'Segment weder waagerecht, senkrecht noch 45 Grad: %r -> %r' % (a, b)
        segments.append((a, b))

# ---------------------------------------------------------------- Verknuepfungen
def on_segment(p, a, b):
    if p == a or p == b:
        return False
    cross = (b[0]-a[0])*(p[1]-a[1]) - (b[1]-a[1])*(p[0]-a[0])
    if abs(cross) > 1e-6:
        return False
    dot = (p[0]-a[0])*(b[0]-a[0]) + (p[1]-a[1])*(b[1]-a[1])
    return 0 < dot < (b[0]-a[0])**2 + (b[1]-a[1])**2

# Segmente auftrennen: KiCad verbindet nur an Drahtenden, nicht mitten im Draht.
changed = True
while changed:
    changed = False
    pts_all = set(PINPOS.values())
    for a, b in segments:
        pts_all.add(a); pts_all.add(b)
    for i, (a, b) in enumerate(segments):
        for p in pts_all:
            if on_segment(p, a, b):
                segments[i:i+1] = [(a, p), (p, b)]
                changed = True
                break
        if changed:
            break

endpoints = {}
for a, b in segments:
    for p in (a, b):
        endpoints[p] = endpoints.get(p, 0) + 1

pin_at = {}
for k, v in PINPOS.items():
    pin_at.setdefault(v, []).append(k)

junctions = set()
for p, cnt in endpoints.items():
    n = cnt + len(pin_at.get(p, []))
    if n >= 3:
        junctions.add(p)

# ---------------------------------------------------------------- Versorgungssymbole
wired_pins = set()
for path in L.WIRES:
    for i in path:
        if isinstance(i, tuple) and isinstance(i[0], str):
            wired_pins.add(i)

power_syms = []          # (net, x, y, rot)
for net, pins in design.NETS.items():
    if net not in POWERSYM:
        continue
    for ref, pin in pins:
        if (ref, pin) in wired_pins:
            continue
        p = PINPOS[(ref, pin)]
        power_syms.append((net, p[0], p[1], rot_for(net, dirname_of(PINDIR[(ref, pin)]))))
for net, x, y, d in L.EXTRA_POWER:
    power_syms.append((net, x, y, rot_for(net, d)))

# ---------------------------------------------------------------- Bibliotheksblock
def flatten(libid):
    """Abgeleitete Symbole (extends) zu eigenstaendigen Symbolen aufloesen."""
    blk, base = libs.get_symbol(libid)
    name = libid.split(':', 1)[1]
    node = copy.deepcopy(blk)
    node[1] = Str(libid)
    ext = find(node, 'extends')
    src, srcname = (base, str(base[1])) if ext else (node, str(blk[1]))
    if ext:
        node.remove(ext)
        have = {x[0] for x in node if isinstance(x, list)}
        inherit = ['pin_names', 'pin_numbers', 'power', 'exclude_from_sim',
                   'in_bom', 'on_board', 'in_pos_files',
                   'duplicate_pin_numbers_are_jumpers']
        pos = 2
        for key in inherit:
            src_attr = find(src, key)
            if src_attr is not None and key not in have:
                node.insert(pos, copy.deepcopy(src_attr))
                pos += 1
        units = [copy.deepcopy(u) for u in findall(src, 'symbol')]
        node.extend(units)
    else:
        units = findall(node, 'symbol')
    for u in units:
        un = str(u[1])
        assert un.startswith(srcname), (un, srcname)
        u[1] = Str(name + un[len(srcname):])
    return node


used_libids = sorted({design.COMPONENTS[r][0] for r in L.PLACE}
                     | set(POWERSYM.values()) | {'power:PWR_FLAG'})
lib_symbols = ['lib_symbols'] + [flatten(l) for l in used_libids]

# ---------------------------------------------------------------- Datei aufbauen
sch = ['kicad_sch', ['version', '20250114'], ['generator', Str('flappy-gen')],
       ['generator_version', Str('9.0')], ['uuid', ROOT_UUID],
       ['paper', Str(getattr(L, 'PAPER', 'A3'))]]
sch.append(['title_block',
            ['title', Str('Flappy Bird auf ESP32-C3 - Hauptbaugruppe')],
            ['date', Str('2026-08-21')], ['rev', Str('A')],
            ['company', Str('HAW Hamburg - Bachelorprojekt Elektrotechnik')],
            ['comment', '1', Str('Zweilagige Leiterplatte, unbestueckt bezogen, in Eigenleistung bestueckt')],
            ['comment', '2', Str('Display und Taster ueber JST-XH-Steckverbinder abgesetzt')],
            ['comment', '3', Str('Erzeugt aus gen/design.py - Aenderungen dort vornehmen')]])
sch.append(lib_symbols)

EFF = lambda *j: ['effects', ['font', ['size', '1.27', '1.27']]] + ([['justify'] + list(j)] if j else [])

for i, (x1, y1, x2, y2, title) in enumerate(L.FRAMES):
    if not title:
        continue
    sch.append(['rectangle', ['start', str(x1), str(y1)], ['end', str(x2), str(y2)],
                ['stroke', ['width', '0.2'], ['type', 'dash']],
                ['fill', ['type', 'none']], ['uuid', U('frame/%d' % i)]])
    sch.append(['text', Str(title), ['exclude_from_sim', 'no'],
                ['at', str(x1 + 2.54), str(y1 - 1.27), '0'],
                ['effects', ['font', ['size', '2', '2'], ['bold', 'yes']], ['justify', 'left']],
                ['uuid', U('frametxt/%d' % i)]])

for i, (txt, x, y, sz) in enumerate(L.NOTES):
    sch.append(['text', Str(txt), ['exclude_from_sim', 'no'], ['at', str(x), str(y), '0'],
                ['effects', ['font', ['size', str(sz), str(sz)]], ['justify', 'left']],
                ['uuid', U('note/%d' % i)]])

for i, (a, b) in enumerate(segments):
    sch.append(['wire', ['pts', ['xy', str(a[0]), str(a[1])], ['xy', str(b[0]), str(b[1])]],
                ['stroke', ['width', '0'], ['type', 'default']], ['uuid', U('wire/%d' % i)]])

for i, p in enumerate(sorted(junctions)):
    sch.append(['junction', ['at', str(p[0]), str(p[1])], ['diameter', '0'],
                ['color', '0', '0', '0', '0'], ['uuid', U('junc/%d' % i)]])

for i, (ref, pin) in enumerate(design.NO_CONNECT):
    p = PINPOS[(ref, pin)]
    sch.append(['no_connect', ['at', str(p[0]), str(p[1])], ['uuid', U('nc/%d' % i)]])

for i, (net, x, y, rot, shape) in enumerate(L.LABELS):
    sch.append(['global_label', Str(net), ['shape', shape],
                ['at', str(x), str(y), str(rot)], ['fields_autoplaced', 'yes'],
                EFF('left') if rot == 0 else EFF('right'),
                ['uuid', U('glbl/%d' % i)],
                ['property', Str('Intersheetrefs'), Str('${INTERSHEET_REFS}'),
                 ['at', str(x), str(y), '0'],
                 ['effects', ['font', ['size', '1.27', '1.27']], ['hide', 'yes']]]])

for i, (ref, pin, length, net) in enumerate(L.STUB_LABELS):
    p, d = PINPOS[(ref, pin)], PINDIR[(ref, pin)]
    q = (round(p[0] + d[0] * length, 4), round(p[1] + d[1] * length, 4))
    sch.append(['wire', ['pts', ['xy', str(p[0]), str(p[1])], ['xy', str(q[0]), str(q[1])]],
                ['stroke', ['width', '0'], ['type', 'default']], ['uuid', U('stub/%d' % i)]])
    rot = 180 if d[0] < 0 else 0
    sch.append(['global_label', Str(net), ['shape', 'input'],
                ['at', str(q[0]), str(q[1]), str(rot)], ['fields_autoplaced', 'yes'],
                EFF('right') if rot == 180 else EFF('left'),
                ['uuid', U('stublbl/%d' % i)],
                ['property', Str('Intersheetrefs'), Str('${INTERSHEET_REFS}'),
                 ['at', str(q[0]), str(q[1]), '0'],
                 ['effects', ['font', ['size', '1.27', '1.27']], ['hide', 'yes']]]])

FIELD_OFF = getattr(L, 'FIELD_OFF', {})


def field_places(ref, rot):
    """Ablage von Referenz und Wert: bei waagerechten Bauteilen ueber und unter
    dem Koerper, bei senkrechten rechts daneben."""
    if ref in FIELD_OFF:
        return FIELD_OFF[ref]
    if rot in (90, 270):
        return (0.0, -2.54), (0.0, 2.54)
    return (2.54, -1.905), (2.54, 0.635)


def sym_instance(libid, ref, value, footprint, descr, x, y, rot, mirror,
                 uid, in_bom='yes', on_board='yes', show_fields=True):
    n = ['symbol', ['lib_id', Str(libid)], ['at', str(x), str(y), str(rot)]]
    if mirror:
        n.append(['mirror', mirror])
    n += [['unit', '1'], ['exclude_from_sim', 'no'], ['in_bom', in_bom],
          ['on_board', on_board],
          ['dnp', 'yes' if ref in design.DNP else 'no'],
          ['fields_autoplaced', 'yes'],
          ['uuid', uid]]
    hide = ['effects', ['font', ['size', '1.27', '1.27']], ['hide', 'yes']]
    vis = ['effects', ['font', ['size', '1.27', '1.27']], ['justify', 'left']]
    (rdx, rdy), (vdx, vdy) = field_places(ref, rot)
    fang = {0: '0', 90: '270', 180: '0', 270: '90'}[int(rot) % 360]  # Feldtext waagerecht
    n.append(['property', Str('Reference'), Str(ref),
              ['at', str(round(x + rdx, 3)), str(round(y + rdy, 3)), fang],
              vis if show_fields else hide])
    vshow = show_fields and ref not in getattr(L, 'HIDE_VALUE', set())
    n.append(['property', Str('Value'), Str(value),
              ['at', str(round(x + vdx, 3)), str(round(y + vdy, 3)), fang],
              vis if vshow else hide])
    n.append(['property', Str('Footprint'), Str(footprint), ['at', str(x), str(y), '0'], hide])
    n.append(['property', Str('Datasheet'), Str('~'), ['at', str(x), str(y), '0'], hide])
    n.append(['property', Str('Description'), Str(descr), ['at', str(x), str(y), '0'], hide])
    for num, *_ in libs.symbol_pins(libid):
        n.append(['pin', Str(num), ['uuid', U('pin/%s/%s' % (ref, num))]])
    n.append(['instances', ['project', Str(PROJECT),
                            ['path', Str('/' + str(ROOT_UUID)),
                             ['reference', Str(ref)], ['unit', '1']]]])
    return n

# ---- Netznamen: Netze ohne Bezeichner bekommen einen lokalen Bezeichner ----
labeled = {n for n, *_ in L.LABELS} | {n for *_, n in L.STUB_LABELS} | set(POWERSYM)
LBL_PIN = {
    'USB_DM_CON': ('J1', '3'), 'USB_DP_CON': ('J1', '4'),
    'USB_CC1': ('J1', '5'), 'USB_CC2': ('J1', '6'),
    'PROG': ('R1', '1'), 'CHG_A': ('D2', '2'), 'LED_CHG': ('D2', '1'),
    'BATT_P': ('J2', '1'), 'EN': ('C10', '1'), 'BOOT': ('TP7', '1'),
    'IO2': ('R15', '2'), 'BTN_SW': ('R12', '1'), 'BTN_CON': ('J4', '1'),
    'BUZZ_P': ('J5', '1'), 'LED_G_A': ('D4', '2'),
    'SCLK': ('J3', '3'), 'MOSI': ('J3', '4'), 'OLED_RES': ('J3', '5'),
    'OLED_DC': ('J3', '6'), 'OLED_CS': ('J3', '7'),
}
LBL_AT = getattr(L, 'LBL_AT', {})
auto = set() if getattr(L, 'NO_AUTO_LABELS', False) else set(design.NETS) - labeled
for k, (net) in enumerate(sorted(auto)):
    if net in LBL_AT:
        px, py, rot = LBL_AT[net]
        p = (px, py)
    else:
        ref, pin = LBL_PIN[net]
        p, d = PINPOS[(ref, pin)], PINDIR[(ref, pin)]
        sx = L.PLACE[ref][0]
        rot = 0 if (d[0] > 0 or (d[0] == 0 and p[0] >= sx)) else 180
    sch.append(['global_label', Str(net), ['shape', 'passive'],
                ['at', str(p[0]), str(p[1]), str(rot)],
                ['fields_autoplaced', 'yes'],
                EFF('right') if rot == 180 else EFF('left'),
                ['uuid', U('lbl/%d' % k)],
                ['property', Str('Intersheetrefs'), Str('${INTERSHEET_REFS}'),
                 ['at', str(p[0]), str(p[1]), '0'],
                 ['effects', ['font', ['size', '1.27', '1.27']], ['hide', 'yes']]]])

NO_BOM = tuple(r for r in design.COMPONENTS if r.startswith(('TP', 'H')))

for ref in sorted(L.PLACE):
    libid, value, fp, descr = design.COMPONENTS[ref]
    x, y, rot, mir = L.PLACE[ref]
    sch.append(sym_instance(libid, ref, value, fp, descr, x, y, rot, mir,
                            U('sym/' + ref),
                            in_bom='no' if ref in NO_BOM else 'yes'))

pwr_n = 0
for net, x, y, rot in power_syms:
    pwr_n += 1
    sch.append(sym_instance(POWERSYM[net], '#PWR%02d' % pwr_n, net, '', '',
                            x, y, rot, None, U('pwr/%d' % pwr_n),
                            in_bom='no', on_board='no', show_fields=False))
for i, (x, y, d) in enumerate(L.PWR_FLAGS):
    pwr_n += 1
    sch.append(sym_instance('power:PWR_FLAG', '#FLG%02d' % (i + 1), 'PWR_FLAG', '', '',
                            x, y, ROT_SUPPLY[d], None, U('flg/%d' % i),
                            in_bom='no', on_board='no', show_fields=False))

sch.append(['sheet_instances', ['path', Str('/'), ['page', Str('1')]]])
open(OUT, 'w', encoding='utf-8').write(dump(sch) + '\n')
print('geschrieben:', OUT)
print('Segmente %d  Verknuepfungen %d  Versorgungssymbole %d' %
      (len(segments), len(junctions), len(power_syms)))
