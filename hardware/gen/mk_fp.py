# -*- coding: utf-8 -*-
"""Erzeugt die projekteigene Footprint-Bibliothek lib/flappy.pretty."""
import os, re, sys
from sexp import parse, dump, find, findall, Str
import design

OUT = os.path.join(os.path.dirname(__file__), '..', 'lib', 'flappy.pretty')
SRC = os.path.join(design.FPLIB, 'RF_Module.pretty', 'ESP32-C3-WROOM-02.kicad_mod')

node = parse(open(SRC, encoding='utf-8').read())
node[1] = Str('ESP32-C3-WROOM-02_HandSolder')

for d in findall(node, 'descr'):
    d[1] = Str('ESP32-C3-WROOM-02, Randkontakt-Pads 1 mm nach aussen verlaengert '
               '(Handbestueckung, Projektplan 4.5.1)')
for d in findall(node, 'tags'):
    d[1] = Str('esp32-c3 wifi ble module handsolder')

# Randkontakte 1..18: Pad von 1,5 mm auf 2,5 mm verlaengern, Aussenkante 1 mm weiter nach aussen.
n = 0
for pad in findall(node, 'pad'):
    num = str(pad[1])
    if not num.isdigit() or not (1 <= int(num) <= 18):
        continue
    at, size = find(pad, 'at'), find(pad, 'size')
    x = float(at[1])
    at[1] = '%.4f' % (x + (-0.5 if x < 0 else 0.5))   # Mittelpunkt 0,5 mm nach aussen
    size[1] = '2.5'                                    # Laenge 1,5 -> 2,5 mm
    n += 1
assert n == 18, n

# Waermevias unter dem Modul von 0,2 mm auf 0,3 mm aufbohren (Fertigungsgrenze)
nv = 0
for pad in findall(node, 'pad'):
    if str(pad[1]) != '19' or pad[2] != 'thru_hole':
        continue
    dr = find(pad, 'drill')
    if dr is not None and float(dr[1]) < 0.3:
        dr[1] = '0.3'
        sz = find(pad, 'size')
        sz[1] = sz[2] = '0.7'
        nv += 1
print('Waermevias aufgebohrt:', nv)

# Silkscreen an der Antennenkante entfernen (liegt auf der Platinenkante)
keep = []
for item in node[2:]:
    if isinstance(item, list) and item[0] == 'fp_line':
        lay = find(item, 'layer')
        st, en = find(item, 'start'), find(item, 'end')
        if lay is not None and str(lay[1]) == 'F.SilkS' and \
           min(float(st[2]), float(en[2])) < -12.9:
            continue
    keep.append(item)
node[2:] = keep

# Silkscreen-Hinweis auf die Antennen-Sperrflaeche ergaenzen
node.append(parse('''(fp_text user "ANT KEEPOUT" (at 0 -15.5 0) (layer "Cmts.User")
 (effects (font (size 1 1) (thickness 0.15))))''' ))

os.makedirs(OUT, exist_ok=True)
open(os.path.join(OUT, 'ESP32-C3-WROOM-02_HandSolder.kicad_mod'), 'w',
     encoding='utf-8').write(dump(node) + '\n')
print('geschrieben:', n, 'Pads verlaengert')

# Kontrolle
import libs
libs._fpcache.clear()
pads = libs.fp_pads('flappy:ESP32-C3-WROOM-02_HandSolder',
                    os.path.join(os.path.dirname(__file__), '..', 'lib'))
print('Pad 1:', pads['1'], ' Pad 18:', pads['18'], ' Pad 9:', pads['9'])
