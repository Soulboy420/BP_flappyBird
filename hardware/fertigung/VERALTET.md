# Diese Fertigungsunterlagen sind veraltet

Die Dateien in diesem Verzeichnis (Gerber, Bohrdaten, Bestückungsdatei) gehören
zu **Revision A** der Leiterplatte: 90 × 60 mm, ohne die CC-Widerstände
R17/R18 am USB-C-Anschluss.

Der Entwurf in `gen/design.py`, `flappy-esp32c3.kicad_sch` und
`flappy-esp32c3.kicad_pcb` ist inzwischen **Revision B**: 72 × 51 mm, 57 statt
55 Bauteile, andere Platzierung und andere Verdrahtung.

**Nicht bestellen.** Vorher einmal

```bash
cd hardware && ./erzeugen.sh
```

auf einem Rechner mit KiCad 10 laufen lassen. Der Lauf füllt die Masseflächen
(ohne diesen Schritt enthalten die Kupfer-Gerber überhaupt keine Massefläche),
prüft ERC und DRC und schreibt dieses Verzeichnis neu. Danach kann diese Datei
gelöscht werden.
