# -*- coding: utf-8 -*-
"""Vergleicht die von KiCad exportierte Netzliste mit design.NETS."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sexp import parse, find, findall
import design

def kicad_nets(path):
    n = parse(open(path, encoding='utf-8').read())
    out = {}
    for net in findall(find(n, 'nets'), 'net'):
        nodes = frozenset((str(find(nd, 'ref')[1]), str(find(nd, 'pin')[1]))
                          for nd in findall(net, 'node'))
        out[str(find(net, 'name')[1])] = nodes
    return out

def expected():
    out = {}
    for name, pins in design.NETS.items():
        out[name] = frozenset(pins)
    return out

got, exp = kicad_nets(sys.argv[1]), expected()
got = {k: v for k, v in got.items() if not k.startswith('unconnected-')}
ok = True
for name, pins in sorted(exp.items()):
    hit = [k for k, v in got.items() if v == pins]
    if not hit:
        ok = False
        near = max(got.items(), key=lambda kv: len(kv[1] & pins))
        print('ABWEICHUNG  %-14s' % name)
        print('   erwartet :', sorted(pins))
        print('   naechstes: %s %s' % (near[0], sorted(near[1])))
    elif hit[0] != name and not hit[0].startswith('Net-'):
        print('HINWEIS  %s heisst in KiCad %s' % (name, hit[0]))
extra = [k for k, v in got.items() if v not in set(exp.values())]
if extra:
    ok = False
    print('ZUSAETZLICHE NETZE:', extra)
print('Netze erwartet %d / exportiert %d  ->  %s'
      % (len(exp), len(got), 'IDENTISCH' if ok else 'FEHLER'))
sys.exit(0 if ok else 1)
