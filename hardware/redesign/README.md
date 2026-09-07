# Flappy Bird – Elektronik Revision B

Eigenständiger KiCad-10-Entwurf für das HAW-Bachelorprojekt. Der ursprüngliche Entwurf unter `hardware/` und absichtliche Benutzerlöschungen wurden nicht überschrieben. Es wurde nichts bestellt, committed oder gepusht.

**Status: NO-GO für eine Bestellfreigabe als fertiges Akkugerät.** Die digitalen Prüfungen bestehen; OLED-/Akku-Schnittstellen, Temperaturfreigabe, Gehäuse und Fertigeraufbau sind noch offen. R39 ist DNP und sperrt das Laden in der Standardbestückung. Die vollständigen Freigabebedingungen stehen in [doc/freigabe-checkliste.md](doc/freigabe-checkliste.md).

## Projekt öffnen

`flappy-esp32c3-revb.kicad_pro` mit KiCad 10.0.5 oder neuer öffnen. Hauptschaltplan und sechs hierarchische Funktionsblätter liegen daneben. Symbole, Footprints und 3D-Modelle sind unter `lib/` lokal eingebunden. Maßgeblich sind die gespeicherten nativen CAD-Dateien, nicht ein Generatorlauf. Das bestehende Firmwareprojekt wurde nicht auf die neue Pinbelegung umgestellt.

Das Layout ist 90×60 mm, zweilagig und 1,6 mm dick. Die ESP-Antenne ragt über die Oberkante. Überwiegend 0805/1206 und THT, mit begründeter lokaler Reflow-Ausnahme für den BQ24074 und anspruchsvoller USB-Buchsenbestückung.

## Inhalt

| Datei/Ordner | Zweck |
|---|---|
| `doc/audit.md` | Nachvollziehbare Fehler und Widersprüche im Ausgangsentwurf |
| `doc/designentscheidungen.md` | Tatsächliche Schaltung, Berechnungen, GPIOs, Betriebssequenzen, Ruhestrom und Grenzen |
| `doc/quellen.md` | Originaldatenblätter, Revisionen und Symbol-/Footprint-Pinprüfung |
| `doc/offene-annahmen.md` | Unbekannte reale Teile und DNP-Varianten |
| `doc/freigabe-checkliste.md` | Messungen vor Bestellung und gestufte Inbetriebnahme |
| `output/schaltplan.pdf` | Aktueller siebenseitiger Schaltplan, A3 |
| `output/pcb-oberseite.pdf`, `pcb-unterseite.pdf` | Kupfer/Bestückungsdruck, Unterseite gespiegelt, Maßstab 2,5:1 |
| `output/bestueckungsplan.pdf` | Kontrastreicher Plan mit Padnummern und DNP-Kreuzen, 2,5:1 |
| `output/stueckliste.csv` | Vollständige BOM mit Hersteller/MPN/Gehäuse/DNP |
| `output/pinmapping.csv` | Jede tatsächliche Pad-Netz-Zuordnung |
| `output/bestueckungspositionen.csv` | 85 zu bestückende Teile, Millimeter; DNP ausgeschlossen |
| `output/fertigung/` | Gerber X2, getrennte PTH-/NPTH-Bohrdaten und Bohrübersichten; noch keine Bestellfreigabe |
| `output/platine-3d.png`, `platine.step` | Ansicht und CAD-Geometrie zur Prüfung; U2/U3 haben vereinfachte Modelle |
| `verification/final-erc.*`, `final-drc.*` | Echte KiCad-Endberichte |
| `verification/consistency.json`, `pruefbericht.md` | Unabhängiger Datenabgleich und Prüfgrenzen |
| `verification/SHA256SUMS` | Dateihashes des Abgabestands |

## Ergebnis der digitalen Prüfung

KiCad 10.0.5: **ERC 0 Fehler/0 Warnungen; DRC 0 Fehler/0 Warnungen, 0 offene Verbindungen, 0 Schaltplan-Abweichungen**. Keine individuellen DRC-Ausnahmen. Abgleich aller 111 Referenzen und 58 Funktionsnetze bestanden; 85 bestückt, 26 DNP (darunter physische Testpads/Bohrungen). Detaillierte aktivierte bzw. standardmäßig nicht ausgeführte Prüfarten sind im Prüfbericht offengelegt.

## Weiterbearbeitung

Die Routingskripte unter `tools/` dokumentieren die Entwicklung und sind **keine idempotente Ein-Kommando-Neuerzeugung des fertigen Boards**. `build.py --update-board` setzt u.a. Bibliotheken und Beschriftungspositionen zurück. Nicht auf dem geprüften Endstand ausführen. Direkte KiCad-Bearbeitung ist der bevorzugte Weg; danach native ERC/DRC mit Neufüllung, XML-Netzexport, `verify_consistency.py` und sämtliche Ausgaben/Hashes neu erzeugen. `export_release.py` erzeugt nur die Abgabedateien aus bereits geprüften CAD-Dateien und prüft, dass der PCB-Inhalt beim Export unverändert bleibt. Die Skripte enthalten die hier verwendeten lokalen KiCad-Pfade und müssen auf einem anderen Rechner angepasst werden.

Die Schaltplanblätter verwenden globale Netzlabels und sind nach Funktionen gegliedert. Gleichnamige Labels sind elektrisch verbunden. Eine drahtlose Darstellung im Plan bedeutet keine fehlende Leiterbahn; die tatsächlichen Verbindungen stehen in der nativen Netzliste und wurden gegen das PCB geprüft.
