# Flappy Bird auf ESP32-C3 — Bachelorprojekt HAW Hamburg

Hardware zum Projekt „Flappy Bird auf eigener ESP32-Baugruppe": zweilagige
Leiterplatte 72 × 51 mm, unbestückt zu beziehen und von Hand zu bestücken,
Display und Taster über JST-XH-Steckverbinder abgesetzt.

> **Vor der Bestellung:** Im Repository liegen nur die Quellen, keine
> Fertigungsunterlagen. Einmal `cd hardware && ./erzeugen.sh` auf einem
> Rechner mit KiCad 10 laufen lassen — das legt `ausgabe/` und `fertigung/`
> an und prüft dabei ERC, DRC und den Netzlistenabgleich mit.

## Alles erzeugen und prüfen

```bash
cd hardware && ./erzeugen.sh
```

Acht Schritte: Bibliotheken, Schaltplan, Platzierungsprüfung, Verdrahtung,
ERC und Netzlistenabgleich, Masseflächen füllen und DRC, Fertigungsunterlagen,
Prüfstand.

| Prüfung | Ergebnis |
|---|---|
| Prüfstand T1–T3, T5–T10, T12 (1618 Einzelprüfungen) | **0 Fehler** |
| Abstandsprüfung ohne KiCad (T6, 659 Kupferstücke paarweise) | **0 Unterschreitungen** |
| Durchgang ohne KiCad (T12, alle 36 Netze) | **0 offene Verbindungen** |
| Platzierung: Lötabstand, Rand, Sperrflächen, Kupferflächen | **0 Beanstandungen** |
| Abgleich Schaltplan ↔ Layout (unabhängig nachgerechnet) | **0 Abweichungen** |
| Reproduzierbarkeit | zweimal erzeugen ergibt bitgleiche Dateien |
| ERC, DRC, Gerber (T4, T11) | **noch offen** — braucht KiCad, siehe Kasten oben |

## Verzeichnisse

Im Repository liegen nur Quellen — alles Erzeugte entsteht aus ihnen neu.

```
hardware/
  flappy-esp32c3.kicad_pro / .kicad_sch / .kicad_pcb   Projektdateien
  erzeugen.sh                     erzeugt und prüft alles neu
  gen/                            Quellen des Entwurfs
  gen/tests.py, tests_stufe3.py   Prüfstand
  lib/                            projekteigene Symbole und Footprints
  fp-lib-table, sym-lib-table     damit KiCad lib/ findet
  doc/pruefbericht.md             Entwurfsprüfung: Befunde, Fläche, Gehäuse
  doc/pruefstand.md               was der Prüfstand prüft
  doc/pinbelegung.md              GPIO-Belegung, verbindlich für die Firmware
  doc/entscheidungen.md           Entwurfsentscheidungen und Abweichungen
  doc/inbetriebnahme.md           gestuftes Protokoll nach Projektplan 4.5
```

`./erzeugen.sh` legt zusätzlich an — beides bleibt bewusst außerhalb der
Versionsverwaltung, damit nie eine veraltete Fassung zur Bestellung geht:

```
  ausgabe/     Schaltplan-PDF, Layout-PDFs, Bestückungsplan, Stückliste,
               3D-Bild, ERC- und DRC-Bericht, exportierte Netzliste
  fertigung/   Gerber, Bohrdaten, Bestückungsdatei
```

## Kennzahlen

| | Revision A | Revision B |
|---|---|---|
| Platine | 90 × 60 mm (5400 mm²) | **72 × 51 mm (3672 mm², −32 %)** |
| Bauteile | 55 | 57 (43 bestückt, 10 Prüfpunkte, 4 Bohrungen M2) |
| Leiterbahnen | 371 Segmente, 843 mm | 413 Segmente, 723 mm |
| davon auf der Rückseite | 8,4 %, längstes Stück 10,8 mm | 10,5 %, längstes Stück **5,4 mm** |
| Durchkontaktierungen | 113 (82 Masse) | 86 (54 Masse) |
| kleinster Umrissabstand zwischen zwei Bauteilen | 0,15 mm | **0,82 mm** |
| kleinste Bahn / kleinster Abstand / kleinste Bohrung | 0,25 / 0,20 / 0,30 mm | unverändert |
| Kühlfläche am Laderegler | 114 mm², über eine Bahn angebunden | **122 mm², direkt am VBAT-Pad von U2** |

Zwei Lagen, 1,6 mm, Bestückung einseitig oben.

## Wie der Entwurf entsteht

Schaltplan und Layout sind **erzeugt**, nicht von Hand gezeichnet. Einzige
Wahrheitsquelle ist `gen/design.py` mit Bauteilen und Netzliste. Wer eine
Schaltungsänderung braucht, ändert diese Datei und lässt `./erzeugen.sh`
laufen — Schaltplan, Layout, Prüfungen und Fertigungsdaten entstehen neu.

Wer lieber in KiCad weiterzeichnet, kann das jederzeit tun; dann sollte
`erzeugen.sh` nicht mehr aufgerufen werden, sonst werden die Handänderungen
überschrieben.

## Handbestückung

Die Platine wird mit einer kleinen Lötstation von Hand bestückt. Dafür gilt
im Layout eine feste Regel, die `gen/chk_place.py` bei jedem Durchgang prüft:

* **mindestens 0,8 mm freier Abstand zwischen zwei Bauteilumrissen**
  (`LOETABSTAND` in `gen/layout_pcb.py`). Der Umriss der Handlöt-Footprints
  liegt schon 0,25 mm außerhalb der Pads — es bleiben also rund 1,3 mm
  freies Kupfer zwischen zwei benachbarten Pads, genug für eine
  1,6-mm-Meißelspitze.
* **mindestens 0,5 mm zum Platinenrand** (`RANDABSTAND`).
* alle SMD-Bauteile auf der Oberseite, alle im Handlöt-Footprint (0805
  statt 0603, verlängerte Pads am Funkmodul).

Schlägt eine dieser Regeln an, bricht `erzeugen.sh` ab.

## Vor der Bestellung

Vier Punkte am **gekauften** Bauteil nachmessen, siehe
`hardware/doc/entscheidungen.md` Abschnitt 3:

1. Pinbelegung des USB-C-Breakouts (erwartet VBUS, GND, D−, D+, CC1, CC2)
2. **Ob das Breakout schon 5,1-kΩ-Widerstände an CC1/CC2 trägt** — wenn ja,
   R17 und R18 **nicht** bestücken
3. Aderfolge des OLED-Moduls
4. Bauform des Schiebeschalters

## Werkzeug

KiCad 10 und Python 3 mit NumPy (für den Verdrahter). Der Generator schreibt
das KiCad-9-Format; der Füllschritt lässt KiCad die Platine in seinem eigenen
Format zurückschreiben. Wer KiCad 9 benutzt, lässt `erzeugen.sh` einmal auf
seinem Rechner laufen.

`erzeugen.sh` und `gen/design.py` suchen KiCad selbst — erst in den unten
genannten Umgebungsvariablen, dann im `PATH` bzw. in KiCads eigenen
`KICAD*_SYMBOL_DIR`/`KICAD*_FOOTPRINT_DIR`, dann an den üblichen
Installationsorten von macOS, Linux und Windows. Nur wenn das fehlschlägt,
muss von Hand nachgeholfen werden:

| Variable | wofür |
|---|---|
| `FLAPPY_KICAD_CLI` | Pfad zum Programm `kicad-cli` |
| `FLAPPY_KICAD_SYMBOLS` | Verzeichnis mit den `*.kicad_sym` der Standardbibliothek |
| `FLAPPY_KICAD_FOOTPRINTS` | Verzeichnis mit den `*.pretty` der Standardbibliothek |

Findet `erzeugen.sh` kein `kicad-cli`, bricht es gleich am Anfang mit einer
Meldung ab, statt eine halb erzeugte Platine zu hinterlassen.
