# -*- coding: utf-8 -*-
"""Minimaler S-Expression-Parser/-Serialisierer fuer KiCad-Dateien."""

def parse(text):
    """Gibt eine verschachtelte Liste zurueck. Atome bleiben Strings;
    Strings in Anfuehrungszeichen werden als ('str', wert) markiert."""
    i, n = 0, len(text)
    stack, cur = [], None
    while i < n:
        c = text[i]
        if c == '(':
            new = []
            if cur is not None:
                cur.append(new)
                stack.append(cur)
            cur = new
            i += 1
        elif c == ')':
            if stack:
                cur = stack.pop()
            else:
                return cur
            i += 1
        elif c == '"':
            j = i + 1
            buf = []
            while j < n:
                if text[j] == '\\':
                    buf.append(text[j+1]); j += 2; continue
                if text[j] == '"':
                    break
                buf.append(text[j]); j += 1
            cur.append(Str(''.join(buf)))
            i = j + 1
        elif c in ' \t\r\n':
            i += 1
        else:
            j = i
            while j < n and text[j] not in ' \t\r\n()"':
                j += 1
            cur.append(text[i:j])
            i = j
    return cur


class Str(str):
    """Atom, das beim Schreiben in Anfuehrungszeichen gesetzt wird."""
    pass


def esc(s):
    return s.replace('\\', '\\\\').replace('"', '\\"')


def dump(node, indent=0):
    pad = '\t' * indent
    if isinstance(node, Str):
        return '"%s"' % esc(node)
    if isinstance(node, str):
        return node
    if not node:
        return '()'
    head = node[0]
    simple = all(not isinstance(x, list) for x in node)
    if simple:
        return '(' + ' '.join(dump(x) for x in node) + ')'
    out = ['(' + dump(head)]
    for x in node[1:]:
        if isinstance(x, list):
            out.append('\n' + '\t' * (indent + 1) + dump(x, indent + 1))
        else:
            out.append(' ' + dump(x))
    out.append('\n' + pad + ')')
    return ''.join(out)


def find(node, name):
    for x in node:
        if isinstance(x, list) and x and x[0] == name:
            return x
    return None


def findall(node, name):
    return [x for x in node if isinstance(x, list) and x and x[0] == name]
