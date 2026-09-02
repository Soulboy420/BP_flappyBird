# -*- coding: utf-8 -*-
"""Zugriff auf die KiCad-Standardbibliotheken (Symbole und Footprints)."""
import os, math
from sexp import parse, find, findall, Str
import design

_symcache = {}

LOCALLIB = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib'))

HINWEIS = ('%s nicht gefunden:\n  %s\n'
           'Die KiCad-Standardbibliothek fehlt oder liegt woanders. KiCad '
           'installieren oder das Verzeichnis in %s setzen (siehe README, '
           'Abschnitt Werkzeug).')


def lies(pfad, was, variable):
    """Liest eine Bibliotheksdatei und erklaert im Fehlerfall, was fehlt."""
    if not os.path.exists(pfad):
        raise FileNotFoundError(HINWEIS % (was, pfad, variable))
    return open(pfad, encoding='utf-8').read()

def load_symlib(lib):
    if lib not in _symcache:
        p = os.path.join(LOCALLIB, lib + '.kicad_sym')
        if not os.path.exists(p):
            p = os.path.join(design.SYMLIB, lib + '.kicad_sym')
        _symcache[lib] = parse(lies(p, 'Symbolbibliothek ' + lib,
                                    'FLAPPY_KICAD_SYMBOLS'))
    return _symcache[lib]


def get_symbol(libid):
    """Liefert (root_block, effective_block) fuer 'Lib:Name'."""
    lib, name = libid.split(':', 1)
    root = load_symlib(lib)
    blocks = {str(s[1]): s for s in findall(root, 'symbol')}
    if name not in blocks:
        raise KeyError('Symbol %s nicht gefunden' % libid)
    blk = blocks[name]
    ext = find(blk, 'extends')
    base = blocks[str(ext[1])] if ext else blk
    return blk, base


def symbol_pins(libid):
    """[(nummer, name, elektr_typ, x, y, winkel, laenge)] in Bibliotheks-Koordinaten."""
    blk, base = get_symbol(libid)
    out = []
    for unit in findall(base, 'symbol'):
        for pin in findall(unit, 'pin'):
            etype = pin[1]
            at = find(pin, 'at')
            ln = find(pin, 'length')
            nm = find(pin, 'name')
            nb = find(pin, 'number')
            out.append((str(nb[1]), str(nm[1]), etype,
                        float(at[1]), float(at[2]), float(at[3]),
                        float(ln[1]) if ln else 2.54))
    return out


def symbol_body(libid):
    """Bounding-Box der Grafik (ohne Pins) in Bibliotheks-Koordinaten."""
    blk, base = get_symbol(libid)
    xs, ys = [], []
    def walk(node):
        nonlocal xs, ys
        for x in node:
            if isinstance(x, list):
                if x[0] in ('rectangle',):
                    for k in ('start', 'end'):
                        p = find(x, k)
                        if p: xs.append(float(p[1])); ys.append(float(p[2]))
                elif x[0] in ('polyline', 'circle', 'arc'):
                    pts = find(x, 'pts')
                    if pts:
                        for xy in findall(pts, 'xy'):
                            xs.append(float(xy[1])); ys.append(float(xy[2]))
                    c = find(x, 'center')
                    if c:
                        r = find(x, 'radius')
                        rr = float(r[1]) if r else 0
                        xs += [float(c[1]) - rr, float(c[1]) + rr]
                        ys += [float(c[2]) - rr, float(c[2]) + rr]
                walk(x)
    walk(base)
    if not xs:
        return (-1.27, -1.27, 1.27, 1.27)
    return (min(xs), min(ys), max(xs), max(ys))


def sym_transform(px, py, x0, y0, rot, mirror=None):
    """Bibliotheks-Pinkoordinate -> Schaltplan-Koordinate."""
    if mirror == 'y':
        px = -px
    elif mirror == 'x':
        py = -py
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    rx = px * c - py * s
    ry = px * s + py * c
    return (round(x0 + rx, 4), round(y0 - ry, 4))


def pin_dir(angle, rot, mirror=None):
    """Richtung, in die der Draht vom Pin wegfuehrt, in Schaltplan-Koordinaten."""
    a = math.radians(angle)
    dx, dy = -math.cos(a), -math.sin(a)      # nach aussen, Bibliotheks-Koordinaten
    if mirror == 'y':
        dx = -dx
    elif mirror == 'x':
        dy = -dy
    b = math.radians(rot)
    c, s = math.cos(b), math.sin(b)
    rx = dx * c - dy * s
    ry = dx * s + dy * c
    return (round(rx, 4), round(-ry, 4))     # Bibliothek Y-hoch -> Blatt Y-runter


_fpcache = {}

def load_footprint(fpid, localdir=None):
    if fpid in _fpcache:
        return _fpcache[fpid]
    lib, name = fpid.split(':', 1)
    p = os.path.join(LOCALLIB, lib + '.pretty', name + '.kicad_mod')
    if not os.path.exists(p):
        p = os.path.join(design.FPLIB, lib + '.pretty', name + '.kicad_mod')
    node = parse(lies(p, 'Footprint ' + fpid, 'FLAPPY_KICAD_FOOTPRINTS'))
    _fpcache[fpid] = node
    return node


def fp_pads(fpid, localdir=None):
    """{padnummer: (x, y)} in Footprint-Koordinaten (erster Treffer je Nummer)."""
    node = load_footprint(fpid, localdir)
    out = {}
    for pad in findall(node, 'pad'):
        num = str(pad[1])
        if num == '':
            continue
        at = find(pad, 'at')
        if num not in out:
            out[num] = (float(at[1]), float(at[2]))
    return out


def fp_transform(px, py, x0, y0, rot):
    """Footprint-Padkoordinate -> Platinen-Koordinate (KiCad-Drehung, Y nach unten)."""
    a = math.radians(rot)
    c, s = math.cos(a), math.sin(a)
    return (round(x0 + px * c + py * s, 4), round(y0 - px * s + py * c, 4))
