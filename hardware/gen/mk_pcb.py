# -*- coding: utf-8 -*-
"""Erzeugt flappy-esp32c3.kicad_pcb aus design.py und layout_pcb.py."""
import os, uuid, copy, math
from sexp import parse, dump, find, findall, Str
import design, libs, layout_pcb as P

PROJECT = 'flappy-esp32c3'
OUT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', PROJECT + '.kicad_pcb'))
BX, BY = P.BX, P.BY

def U(seed):
    return Str(str(uuid.uuid5(uuid.NAMESPACE_URL, 'flappypcb://' + seed)))

def A(x, y):
    return (round(BX + x, 4), round(BY + y, 4))

# Nicht angeschlossene Pins bekommen den Namen, den KiCad in der Netzliste
# vergibt - sonst meldet die Abgleichpruefung eine Abweichung.
UNCONNECTED = {}
for ref, pin in design.NO_CONNECT:
    libid = design.COMPONENTS[ref][0]
    name = dict((p[0], p[1]) for p in libs.symbol_pins(libid))[pin]
    name = name.replace('/', '{slash}') or 'Pad%s' % pin
    UNCONNECTED[(ref, pin)] = 'unconnected-(%s-%s-Pad%s)' % (ref, name, pin)

netnames = ['', *sorted(design.NETS), *sorted(UNCONNECTED.values())]
NETNO = {n: i for i, n in enumerate(netnames)}
PADNET = {}
for net, pins in design.NETS.items():
    for ref, pin in pins:
        PADNET[(ref, pin)] = net
PADNET.update({k: v for k, v in UNCONNECTED.items()})

def netclass(n):
    if n in ('VBUS', 'VBAT', 'VBAT_SW', 'BATT_P', '+3V3', '+3V3_MCU'):
        return 'Leistung'
    return 'USB' if n.startswith('USB_D') else 'Default'

LAYERS = [('0', 'F.Cu', 'signal', None), ('2', 'B.Cu', 'signal', None),
          ('9', 'F.Adhes', 'user', 'F.Adhesive'), ('11', 'B.Adhes', 'user', 'B.Adhesive'),
          ('13', 'F.Paste', 'user', None), ('15', 'B.Paste', 'user', None),
          ('5', 'F.SilkS', 'user', 'F.Silkscreen'), ('7', 'B.SilkS', 'user', 'B.Silkscreen'),
          ('1', 'F.Mask', 'user', None), ('3', 'B.Mask', 'user', None),
          ('17', 'Dwgs.User', 'user', 'User.Drawings'),
          ('19', 'Cmts.User', 'user', 'User.Comments'),
          ('21', 'Eco1.User', 'user', 'User.Eco1'), ('23', 'Eco2.User', 'user', 'User.Eco2'),
          ('25', 'Edge.Cuts', 'user', None), ('27', 'Margin', 'user', None),
          ('31', 'F.CrtYd', 'user', 'F.Courtyard'), ('29', 'B.CrtYd', 'user', 'B.Courtyard'),
          ('35', 'F.Fab', 'user', None), ('33', 'B.Fab', 'user', None)]

layers = ['layers']
for num, name, typ, usr in LAYERS:
    row = [num, Str(name), typ]
    if usr:
        row.append(Str(usr))
    layers.append(row)

pcb = ['kicad_pcb', ['version', '20241229'], ['generator', Str('flappy-gen')],
       ['generator_version', Str('9.0')],
       ['general', ['thickness', '1.6'], ['legacy_teardrops', 'no']],
       ['paper', Str('A4')],
       ['title_block',
        ['title', Str('Flappy Bird auf ESP32-C3 - Hauptbaugruppe')],
        ['date', Str('2026-08-21')], ['rev', Str('A')],
        ['company', Str('HAW Hamburg - Bachelorprojekt Elektrotechnik')],
        ['comment', '1', Str('Zweilagig, 1,6 mm, Bestueckung einseitig oben')]],
       layers,
       ['setup',
        ['pad_to_mask_clearance', '0'],
        ['allow_soldermask_bridges_in_footprints', 'no'],
        ['pcbplotparams',
         ['layerselection', '0x00000000_00000000_55555555_5755f5ff'],
         ['plot_on_all_layers_selection', '0x00000000_00000000_00000000_00000000'],
         ['disableapertmacros', 'no'], ['usegerberextensions', 'no'],
         ['usegerberattributes', 'yes'], ['usegerberadvancedattributes', 'yes'],
         ['creategerberjobfile', 'yes'], ['dashed_line_dash_ratio', '12.000000'],
         ['dashed_line_gap_ratio', '3.000000'], ['svgprecision', '4'],
         ['plotframeref', 'no'], ['mode', '1'], ['useauxorigin', 'no'],
         ['hpglpennumber', '1'], ['hpglpenspeed', '20'], ['hpglpendiameter', '15.000000'],
         ['pdf_front_fp_property_popups', 'yes'], ['pdf_back_fp_property_popups', 'yes'],
         ['pdf_metadata', 'yes'], ['pdf_single_document', 'no'],
         ['dxfpolygonmode', 'yes'], ['dxfimperialunits', 'yes'], ['dxfusepcbnewfont', 'yes'],
         ['psnegative', 'no'], ['psa4output', 'no'],
         ['plot_black_and_white', 'yes'], ['sketchpadsonfab', 'no'],
         ['plotpadnumbers', 'no'], ['hidednponfab', 'no'], ['sketchdnponfab', 'yes'],
         ['crossoutdnponfab', 'yes'], ['subtractmaskfromsilk', 'no'],
         ['outputformat', '1'], ['mirror', 'no'], ['drillshape', '1'],
         ['scaleselection', '1'], ['outputdirectory', Str('fertigung/')]]],
       ['net', '0', Str('')]]
for n in netnames[1:]:
    pcb.append(['net', str(NETNO[n]), Str(n)])

# ------------------------------------------------------------------ Footprints
def place_footprint(ref):
    libid, value, fpid, descr = design.COMPONENTS[ref]
    x, y, rot = P.PLACE[ref]
    node = copy.deepcopy(libs.load_footprint(fpid))
    node[0] = 'footprint'
    node[1] = Str(fpid)
    ax, ay = A(x, y)
    out = ['footprint', Str(fpid), ['layer', Str('F.Cu')], ['uuid', U('fp/' + ref)],
           ['at', str(ax), str(ay)] + ([str(rot)] if rot else [])]
    for key in ('descr', 'tags'):
        k = find(node, key)
        if k is not None:
            out.append(copy.deepcopy(k))
    def prop(name, val, ox, oy, hide, layer='F.SilkS'):
        p = ['property', Str(name), Str(val),
             ['at', str(ox), str(oy), '0'], ['layer', Str(layer)]]
        if hide:
            p.append(['hide', 'yes'])
        p += [['uuid', U('prop/%s/%s' % (ref, name))],
              ['effects', ['font', ['size', '0.8', '0.8'], ['thickness', '0.13']]]]
        return p
    dx, dy = P.LABEL_OFF.get(ref, (0.0, -2.2))
    a = math.radians(-rot)                       # Drehung des Footprints ausgleichen
    ox = round(dx * math.cos(a) + dy * math.sin(a), 3)
    oy = round(-dx * math.sin(a) + dy * math.cos(a), 3)
    out.append(prop('Reference', ref, ox, oy, False))
    out.append(prop('Value', value, 0, 1.4, False, 'F.Fab'))   # Bestueckungsplan 4.5.8
    if find(node, 'property') is None or not any(
            str(p[1]) == 'Description' for p in findall(node, 'property')):
        out.append(prop('Description', descr, 0, 0, True, 'F.Fab'))
    for pr in findall(node, 'property'):
        if str(pr[1]) in ('Reference', 'Value'):
            continue
        q = copy.deepcopy(pr)
        if str(q[1]) == 'Description':
            q[2] = Str(descr)
        at = find(q, 'at')
        at[1], at[2], at[3] = '0', '0', '0'
        u = find(q, 'uuid')
        if u is not None:
            u[1] = U('prop/%s/%s' % (ref, str(q[1])))
        else:
            q.append(['uuid', U('prop/%s/%s' % (ref, str(q[1])))])
        out.append(q)
    for key in ('attr',):
        k = find(node, key)
        if k is not None:
            out.append(copy.deepcopy(k))
    GRAPH = ('fp_line', 'fp_rect', 'fp_poly', 'fp_circle', 'fp_arc',
             'fp_text', 'fp_text_box', 'pad', 'zone')
    n_item = 0
    SKIP = ('descr', 'tags', 'property', 'attr', 'version', 'generator',
            'generator_version', 'layer', 'uuid', 'at', 'tedit', 'model')
    for item in node[2:]:
        if not isinstance(item, list):
            continue
        tag = item[0]
        if tag in SKIP:
            continue
        if tag not in GRAPH:
            out.append(copy.deepcopy(item))
            continue
        it = copy.deepcopy(item)
        if tag == 'pad':
            num = str(it[1])
            net = PADNET.get((ref, num))
            if net:
                it.append(['net', str(NETNO[net]), Str(net)])
                it.append(['pintype', Str('passive')])
        n_item += 1
        u = find(it, 'uuid')
        if u is not None:
            u[1] = U('fpitem/%s/%d' % (ref, n_item))
        else:
            it.append(['uuid', U('fpitem/%s/%d' % (ref, n_item))])
        out.append(it)
    m = find(node, 'model')
    if m is not None:
        out.append(copy.deepcopy(m))
    return out

for ref in sorted(P.PLACE):
    pcb.append(place_footprint(ref))

# ------------------------------------------------------------------ Umriss usw.
def gr(kind, layer, width, pts, uid, fill=None):
    n = [kind]
    if kind == 'gr_line':
        n += [['start', str(pts[0][0]), str(pts[0][1])],
              ['end', str(pts[1][0]), str(pts[1][1])]]
    elif kind == 'gr_rect':
        n += [['start', str(pts[0][0]), str(pts[0][1])],
              ['end', str(pts[1][0]), str(pts[1][1])]]
    elif kind == 'gr_circle':
        n += [['center', str(pts[0][0]), str(pts[0][1])],
              ['end', str(pts[1][0]), str(pts[1][1])]]
    n += [['stroke', ['width', str(width)], ['type', 'solid']]]
    if fill:
        n.append(['fill', fill])
    n += [['layer', Str(layer)], ['uuid', uid]]
    return n

W, H = P.W, P.H
c = [A(0, 0), A(W, 0), A(W, H), A(0, H)]
for i in range(4):
    pcb.append(gr('gr_line', 'Edge.Cuts', 0.1, [c[i], c[(i + 1) % 4]], U('edge/%d' % i)))

for i, (x, y, txt, size, layer, rot) in enumerate(P.TEXTS):
    ax, ay = A(x, y)
    just = ['justify', 'left'] + (['mirror'] if layer.startswith('B.') else [])
    pcb.append(['gr_text', Str(txt), ['at', str(ax), str(ay), str(rot)],
                ['layer', Str(layer)], ['uuid', U('txt/%d' % i)],
                ['effects', ['font', ['size', str(size), str(size)],
                             ['thickness', str(round(size * 0.16, 3))]], just]])

for i, (x1, y1, x2, y2, txt) in enumerate(P.KEEPOUTS):
    a, b = A(x1, y1), A(x2, y2)
    pcb.append(['zone', ['net', '0'], ['net_name', Str('')],
                ['layers', Str('F&B.Cu')], ['uuid', U('keep/%d' % i)],
                ['name', Str(txt)], ['hatch', 'edge', '0.5'],
                ['connect_pads', ['clearance', '0']], ['min_thickness', '0.25'],
                ['filled_areas_thickness', 'no'],
                ['keepout', ['tracks', 'not_allowed'], ['vias', 'not_allowed'],
                 ['pads', 'allowed'], ['copperpour', 'not_allowed'],
                 ['footprints', 'allowed']],
                ['placement', ['enabled', 'no'], ['sheetname', Str('')]],
                ['polygon', ['pts', ['xy', str(a[0]), str(a[1])], ['xy', str(b[0]), str(a[1])],
                             ['xy', str(b[0]), str(b[1])], ['xy', str(a[0]), str(b[1])]]]])

# ------------------------------------------------------------------ Leiterbahnen
for i, (net, layer, width, a, b) in enumerate(P.tracks()):
    pa, pb = A(*a), A(*b)
    pcb.append(['segment', ['start', str(pa[0]), str(pa[1])],
                ['end', str(pb[0]), str(pb[1])], ['width', str(width)],
                ['layer', Str(layer)], ['net', str(NETNO[net])], ['uuid', U('trk/%d' % i)]])

for i, (net, x, y, dia, drill) in enumerate(P.vias()):
    p = A(x, y)
    pcb.append(['via', ['at', str(p[0]), str(p[1])], ['size', str(dia)],
                ['drill', str(drill)], ['layers', Str('F.Cu'), Str('B.Cu')],
                ['net', str(NETNO[net])], ['uuid', U('via/%d' % i)]])

# ------------------------------------------------------------------ Massefluten
def zone(layer, uid, prio, poly, net='GND'):
    pts = ['pts'] + [['xy', str(px), str(py)] for px, py in poly]
    return ['zone', ['net', str(NETNO[net])], ['net_name', Str(net)],
            ['layer', Str(layer)], ['uuid', uid],
            ['name', Str('Masseflaeche ' + layer)], ['hatch', 'edge', '0.5'],
            ['priority', str(prio)],
            ['connect_pads', ['clearance', '0.3']],
            ['min_thickness', '0.25'], ['filled_areas_thickness', 'no'],
            ['fill', 'yes', ['thermal_gap', '0.4'], ['thermal_bridge_width', '0.6'],
             ['smoothing', 'fillet'], ['radius', '0.5'],
             ['island_removal_mode', '0']],
            ['polygon', pts]]

margin = 0.3
poly = [A(margin, margin), A(W - margin, margin), A(W - margin, H - margin), A(margin, H - margin)]
pcb.append(zone('F.Cu', U('zoneF'), 0, poly))
pcb.append(zone('B.Cu', U('zoneB'), 0, poly))
for i, (x1, y1, x2, y2, net) in enumerate(P.NETZONES):
    a, b = A(x1, y1), A(x2, y2)
    pcb.append(zone('F.Cu', U('nzone/%d' % i), 10 + i,
                    [a, (b[0], a[1]), b, (a[0], b[1])], net))

open(OUT, 'w', encoding='utf-8').write(dump(pcb) + '\n')
print('geschrieben:', OUT)
print('Footprints %d  Leiterbahnen %d  Vias %d' % (len(P.PLACE), len(P.tracks()), len(P.vias())))
