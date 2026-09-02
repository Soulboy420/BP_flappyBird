# -*- coding: utf-8 -*-
"""Stufe 3: Gesamtlauf, Reproduzierbarkeit und Fehlererkennung.

  python3 tests_stufe3.py            alles
  python3 tests_stufe3.py wiederhol  nur Reproduzierbarkeit
  python3 tests_stufe3.py mutation   nur Fehlererkennung
"""
import hashlib, os, shutil, subprocess, sys, tempfile

HIER = os.path.dirname(os.path.abspath(__file__))
WURZEL = os.path.abspath(os.path.join(HIER, '..'))
sys.path.insert(0, HIER)
import design
KICAD = design.kicad_cli()

_fehler = []


def pruefe(bed, name, detail=''):
    if not bed:
        _fehler.append(name)
        print('  FEHLER  %s%s' % (name, ('  -> ' + detail) if detail else ''))
    else:
        print('  ok      %s%s' % (name, ('  (' + detail + ')') if detail else ''))
    return bool(bed)


def hash_datei(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()[:16]


def lauf(cmd, cwd=HIER):
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, shell=isinstance(cmd, str))


# ---------------------------------------------------------------- Reproduzierbar
def wiederholbarkeit():
    print('S3-A  Reproduzierbarkeit: zweimal erzeugen ergibt dieselben Dateien')
    dateien = ['flappy-esp32c3.kicad_sch', 'flappy-esp32c3.kicad_pcb']
    schritte = [['python3', 'mk_sym.py'], ['python3', 'mk_fp.py'],
                ['python3', 'mk_sch.py'], ['python3', 'autoroute.py'],
                ['python3', 'mk_labels.py'], ['python3', 'mk_pcb.py']]
    vorher = {}
    for durchgang in (1, 2):
        for s in schritte:
            r = lauf(s)
            if r.returncode:
                pruefe(False, 'Schritt %s laeuft' % ' '.join(s), r.stderr[-300:])
                return
        jetzt = {d: hash_datei(os.path.join(WURZEL, d)) for d in dateien}
        # routes.py und labels.py sind Zwischenergebnisse und muessen auch stabil sein
        jetzt['routes.py'] = hash_datei(os.path.join(HIER, 'routes.py'))
        jetzt['labels.py'] = hash_datei(os.path.join(HIER, 'labels.py'))
        if durchgang == 1:
            vorher = jetzt
        else:
            for d in jetzt:
                pruefe(vorher[d] == jetzt[d], 'gleich nach dem zweiten Lauf: %s' % d,
                       '%s / %s' % (vorher[d], jetzt[d]))


# ---------------------------------------------------------------- Gesamtlauf
def gesamtlauf():
    print('S3-B  Gesamtlauf mit KiCad')
    r = lauf(['./erzeugen.sh'], cwd=WURZEL)
    pruefe(r.returncode == 0, 'erzeugen.sh laeuft ohne Fehler',
           r.stderr[-300:] if r.returncode else '')
    text = r.stdout + r.stderr
    pruefe(text.count('IDENTISCH') == 1, 'Netzliste stimmt mit design.py',
           '%d Treffer' % text.count('IDENTISCH'))
    pruefe('Found 0 unconnected items' in text, 'keine offenen Verbindungen')
    pruefe('Found 0 schematic parity issues' in text, 'Schaltplan und Layout im Einklang')
    pruefe(text.count('Found 0 violations') >= 2, 'ERC und DRC ohne Verstoesse',
           '%d Treffer' % text.count('Found 0 violations'))

    # Fertigungsdaten vorhanden und nicht leer
    for d in ['fertigung/flappy-esp32c3-F_Cu.gtl', 'fertigung/flappy-esp32c3-B_Cu.gbl',
              'fertigung/flappy-esp32c3-Edge_Cuts.gm1', 'fertigung/flappy-esp32c3-PTH.drl',
              'fertigung/flappy-esp32c3-NPTH.drl', 'ausgabe/stueckliste.csv',
              'ausgabe/schaltplan.pdf', 'ausgabe/bestueckungsplan.pdf']:
        p = os.path.join(WURZEL, d)
        pruefe(os.path.exists(p) and os.path.getsize(p) > 200,
               'Fertigungsdatei vorhanden: %s' % os.path.basename(d))


# ---------------------------------------------------------------- Fehlererkennung
# Nach jeder Mutation wird neu erzeugt. Damit koennen die Dateipruefungen
# den Fehler nicht mehr "billig" ueber veraltete Dateien finden - es muessen
# die inhaltlichen Pruefungen anschlagen.
NEUERZEUGEN = [['python3', 'mk_sch.py'], ['python3', 'autoroute.py'],
               ['python3', 'mk_labels.py'], ['python3', 'mk_pcb.py']]

# Der Fuellschritt gehoert dazu: ohne ihn waeren die Masseflaechen leer und
# T8 wuerde bei jeder Mutation anschlagen - dann wuerde der Mutationstest
# alles "erkennen", aber aus dem falschen Grund.
FUELLEN = [KICAD, 'pcb', 'drc', '--refill-zones', '--save-board',
           '-o', '/dev/null', 'flappy-esp32c3.kicad_pcb']


def neu_erzeugen():
    for schritt in NEUERZEUGEN:
        r = lauf(schritt)
        if r.returncode:
            return False
    return lauf(FUELLEN, cwd=WURZEL).returncode == 0

MUTATIONEN = [
    ('Netz falsch verbunden',
     "'BUZZ':      [('U1','17'),('R13','1')],",
     "'BUZZ':      [('U1','17'),('R14','1')],"),
    ('Pin vergessen',
     "'EN':        [('U1','2'),('R4','1'),('C10','1'),('TP6','1')],",
     "'EN':        [('U1','2'),('R4','1'),('C10','1')],"),
    ('Bauteilwert verstellt',
     "'R1': ('Device:R', '6k8',  R0805, 'R_prog -> I_chg = 147 mA'),",
     "'R1': ('Device:R', '2k2',  R0805, 'R_prog -> I_chg = 147 mA'),"),
    ('Piezo-Vorwiderstand zu klein',
     "'R13':('Device:R', '220R', R0805,",
     "'R13':('Device:R', '68R', R0805,"),
    ('Serienterminierung falsch bestueckt',
     "'R7': ('Device:R', '68R',  R0805, 'Serienterminierung RES'),",
     "'R7': ('Device:R', '33R',  R0805, 'Serienterminierung RES'),"),
    ('Pull-up am Strapping-Pin entfernt',
     "'IO2':       [('U1','16'),('R15','2')],",
     "'IO2':       [('U1','16'),('R15','2')],  # unveraendert\n 'X_DUMMY':   [],"),
    ('Serienwiderstand ueberbrueckt',
     "'MOSI':      [('R6','2'),('J3','4')],",
     "'MOSI':      [('R6','2'),('J3','4'),('U1','4')],"),
    ('Dauerstrompfad von 3V3 nach Masse',
     "'BTN_CON':   [('R12','2'),('J4','1')],",
     "'BTN_CON':   [('R12','2'),('J4','1'),('R1','2')],"),
]


def fehlererkennung():
    print('S3-C  Fehlererkennung: eingebaute Fehler muessen auffallen')
    quelle = os.path.join(HIER, 'design.py')
    original = open(quelle, encoding='utf-8').read()
    try:
        for name, alt, neu in MUTATIONEN:
            if alt not in original:
                pruefe(False, 'Mutation anwendbar: %s' % name, 'Textstelle nicht gefunden')
                continue
            open(quelle, 'w', encoding='utf-8').write(original.replace(alt, neu, 1))
            # erst neu erzeugen: der Fehler soll inhaltlich auffallen,
            # nicht nur weil eine Datei veraltet ist
            erzeugt_ok = neu_erzeugen()
            r = lauf(['python3', 'tests.py'])
            entdeckt = (not erzeugt_ok) or r.returncode != 0
            meldung = next((z.strip() for z in r.stdout.splitlines()
                            if 'FEHLER' in z), 'Erzeugung bricht ab' if not erzeugt_ok else '')
            pruefe(entdeckt, 'erkannt: %s' % name,
                   meldung[:110] if entdeckt else 'Pruefstand meldet keinen Fehler')
    finally:
        open(quelle, 'w', encoding='utf-8').write(original)
        neu_erzeugen()
        r = lauf(['python3', 'tests.py'])
        pruefe(r.returncode == 0, 'Ausgangszustand wiederhergestellt',
               '' if r.returncode == 0 else r.stdout[-300:])


if __name__ == '__main__':
    was = sys.argv[1] if len(sys.argv) > 1 else 'alles'
    if was in ('alles', 'wiederhol'):
        wiederholbarkeit()
    if was in ('alles', 'mutation'):
        fehlererkennung()
    if was in ('alles', 'gesamt'):
        gesamtlauf()
    print('\n%s' % ('Alles bestanden.' if not _fehler else
                    '%d Pruefungen fehlgeschlagen.' % len(_fehler)))
    sys.exit(1 if _fehler else 0)
