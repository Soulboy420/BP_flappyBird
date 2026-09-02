# -*- coding: utf-8 -*-
"""Erzeugt lib/flappy.kicad_sym mit den projekteigenen Versorgungssymbolen."""
import os, sys
from sexp import parse, dump, find, findall, Str
import design, libs

src = parse(libs.lies(os.path.join(design.SYMLIB, 'power.kicad_sym'),
                      'Symbolbibliothek power', 'FLAPPY_KICAD_SYMBOLS'))
blocks = {str(s[1]): s for s in findall(src, 'symbol')}
tpl = blocks['+3V3']

def clone(name, descr):
    import copy
    n = copy.deepcopy(tpl)
    n[1] = Str(name)
    for prop in findall(n, 'property'):
        key = str(prop[1])
        if key == 'Value':
            prop[2] = Str(name)
        elif key == 'Description':
            prop[2] = Str(descr)
    for sub in findall(n, 'symbol'):
        sub[1] = Str(sub[1].replace('+3V3', name, 1))
    for pin in findall(find(n, 'symbol') or n, 'pin'):
        pass
    # Pin-Name auf den neuen Netznamen setzen
    def fixpins(node):
        for x in node:
            if isinstance(x, list):
                if x[0] == 'pin':
                    nm = find(x, 'name')
                    if nm: nm[1] = Str(name)
                fixpins(x)
    fixpins(n)
    return n

out = ['kicad_symbol_lib', ['version', '20241209'], ['generator', Str('flappy-gen')],
       ['generator_version', Str('9.0')]]
out.append(clone('VBAT', 'Versorgungssymbol: Akkuspannung (unmittelbar an der Zelle)'))
out.append(clone('VBAT_SW', 'Versorgungssymbol: Akkuspannung hinter dem Ein/Aus-Schalter'))
out.append(clone('+3V3_MCU', 'Versorgungssymbol: 3,3 V hinter der 0-Ohm-Trennstelle (Modulversorgung)'))

p = os.path.join(os.path.dirname(__file__), '..', 'lib', 'flappy.kicad_sym')
open(p, 'w', encoding='utf-8').write(dump(out) + '\n')
print('geschrieben:', p)
