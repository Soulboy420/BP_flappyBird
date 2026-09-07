# Prüfbericht des Abgabestands

KiCad **10.0.5**, Prüfung am **06.09.2026**. Projekt `flappy-esp32c3-revb`. Die Dateien `final-erc.json/.rpt` und `final-drc.json/.rpt` sind echte KiCad-Ausgaben. Dateihashes stehen in `SHA256SUMS`; Ausgabeinhalte und Koordinaten wurden zusätzlich mit den beiden lesenden Prüfscripten abgeglichen. Es liegen keine Prototyp-Messwerte vor.

## Ergebnisse

| Prüfung | Tatsächliches Ergebnis |
|---|---|
| ERC, alle eingestellten Fehler/Warnungen/Ausnahmen | 0 Meldungen auf sieben Schaltplanblättern |
| DRC mit `--all-track-errors --schematic-parity --refill-zones --save-board` | 0 Regelverletzungen, 0 offene Verbindungen, 0 Schaltplan-Abweichungen |
| Zweiter nativer DRC-Textbericht auf unverändertem Endstand | Ebenfalls 0/0/0 |
| Individuelle DRC-Ausnahmen | Keine; `drc_exclusions` leer |
| Referenzen / Werte / MPN / Hersteller / Gehäuse / Footprints / DNP | Schaltplan-XML, PCB, BOM und explizite Entwurfsdaten stimmen überein |
| Bauteile | 111 Referenzen; 85 bestückt, 26 DNP einschließlich PCB-Testpads/Bohrungen |
| Netze | 58 funktionale Netze; native XML zusätzlich fünf ausdrücklich unverbundene NC-Netze |
| Physische Pad-Zuordnung | 301 nummerierte Pads geprüft, einschließlich gleicher Nummern auf Mehrfachpads |
| Projektabhängigkeiten | Hierarchische Blätter, Symbole, Footprints und 91 Modellreferenzen lokal auflösbar |
| Kupferflächen | 53 gefüllte F.Cu-Polygone, 2 B.Cu-Polygone; elektrisch über Pads/Vias verbunden, keine DRC-Kupferinseln |
| Kupfer-Gerber | Entsprechend 53/2 G36/G37-Flächenregionen. Größte Region ca.2066,43 mm² oben, 4964,43 mm² unten; GND-Netzattribute vorhanden |
| Positionen | Alle 85 bestückten Referenzen mit PCB-X/Y, Rotation und Seite abgeglichen, DNP ausgeschlossen |
| Bohrungen | 403 metallisierte einschließlich vier USB-Schlitzen, 6 NPTH; mit den gespeicherten Pads/Vias abgeglichen |
| Exportintegrität | PCB-Hash vor/nach PDF-/Gerber-/Bohr-/Positionsexport identisch, siehe `artifact-check.json` |
| Sichtprüfung | Sieben Schaltplanseiten, PCB-Ober-/Unterseite, Bestückungsplan und 3D-Darstellung gerendert und kontrolliert; doppelte Fab-Referenztexte entfernt, Bestückungsplan schwarzweiß |
| 3D-Export | Native STEP-Ausgabe erfolgreich, DNP-Modelle ausgeschlossen; U3 im STEP enthalten. U2/U3 sind vereinfachte Geometriehilfen |
| Benutzeränderungen | Liste der bereits geänderten/gelöschten versionierten Dateien unverändert; Original-CAD nicht bearbeitet |

## Regelprofil und Reichweite

Aktiv sind unter anderem Kurzschlüsse, Abstände, Löcher, Restring, Leiterbreite, Kupferkante, Lötstoppüberdeckung, Courtyard-Kollisionen, Antennen-Regelbereiche, thermische Anschlüsse, Kupferinseln, offene Verbindungen, Bibliotheksvergleich und Schaltplan-Parität. Es wurden keine einzelnen Fehler als Ausnahme markiert.

Konkrete Untergrenzen: Leiter/Abstand 0,15 mm; Kupferkante 0,30 mm; Bohrung-zu-Kupfer 0,15 mm; Loch-zu-Loch 0,25 mm; Via-Durchmesser 0,50 mm, Bohrung 0,25 mm, DRC-Restringminimum 0,10 mm (kleinste tatsächlich verwendete Kombination nominal 0,125 mm); Schrift 0,80 mm, Strich 0,08 mm. Das Profil verlangt keinen zusätzlichen positiven Bestückungsdruckabstand über Überlappungsfreiheit hinaus (`min_silk_clearance=0`); Textpositionen wurden zusätzlich mit Abstand zu Masken und Körpern gesetzt und visuell geprüft. Eine Fertigerzusage zu Mindestschrift und Lötstoppstegen wird dadurch nicht ersetzt.

Folgende im JSON/RPT ausdrücklich ausgewiesenen Prüfarten sind in diesem Profil nicht ausgeführt:

| Nicht ausgeführte Prüfung | Einordnung / Ersatznachweis |
|---|---|
| ERC: einzelnes globales Label | Kein allgemeiner elektrischer Fehler; vollständige Pad-Netz-Liste und expliziter Netzabgleich liegen vor. |
| ERC: Vierfachknoten | Darstellungsregel; die Schaltplanblätter verwenden kurze Label-Anschlüsse. Keine Vierfachknoten als verdeckte Verbindungsannahme. |
| ERC: SPICE-Modell | Es wurde keine SPICE-Simulation behauptet; diese Dateien sind ein Fertigungs-CAD-Projekt. |
| ERC/DRC: Footprint-Namensfilter | Lokale `RevB:`-Kopien und individuell umgepinntes Regler-Symbol; tatsächliche Padnummern, MPN-Gehäuse und lokale Bibliotheksdateien wurden direkt geprüft. Ein Namensfilter wäre kein Pin-Nachweis. |
| DRC: fehlender Courtyard | Nicht global erzwungen. Vorhandene Courtyards/Kollisionen werden geprüft; PCB-Testpads und Bohrungen sind keine einzulötenden Bauteile. Gehäuse/Kabel bleiben physische Freigabepunkte. |
| DRC: Leiterende exakt auf Via-Mitte | Geometrische Stilprüfung; tatsächliche elektrische Verbindung, Kupferabstand und Durchmesser werden geprüft. |
| DRC: Tuning-Profil-Geometrie | Keine KiCad-Tuning-Profile verwendet; USB-Impedanz ist deshalb auch nicht als automatisch geprüft ausgewiesen. |
| DRC: Footprint-Typ gegen Pad-Typ | Die USB-Buchse kombiniert SMD-Signale und THT-Schirm. Tatsächliche Pads, Bohrdaten und 85 Bestückungspositionen wurden direkt abgeglichen. |

Die unabhängigen Scripte `tools/verify_consistency.py` und `tools/verify_exports.py` prüfen konkrete Datenkorrespondenz und Exportinhalte. Sie ersetzen weder die nativen ERC/DRC-Werkzeuge noch die Herstellerprüfung. Unter `development/` liegen ausdrücklich ungültige Zwischenstände als Entwicklungsnachweis. `old-current-*` betreffen den Ausgangsentwurf und sind keine Endberichte für Revision B.

## Ausgaben und Koordinaten

Schaltplan-PDF: sieben A3-Seiten. Drei PCB-PDFs: jeweils eine A4-Querformatseite, 2,5:1. Unterseiten-PDF gespiegelt; Gerber unverändert in Fertigungskoordinaten. Für 1:1-Papierkontrolle die PCB-PDF auf 40 % ausgeben und nachmessen.

Gerber: neun X2-Lagen plus Gerberjob; leere B.Paste ist bei ausschließlich oberseitiger Bestückung richtig. F.Paste zeigt auch DNP-Optionen; bei einer Schablone deren Öffnungen gemäß BOM sperren. Excellon PTH/NPTH getrennt, metrisch, USB-Schlitze enthalten. Positionsdatei in mm, Ursprung absolut nach KiCad: X nach rechts, Y nach oben; damit negative Y-Werte für die auf dem Board nach unten laufende KiCad-Achse. Rotationskonvention mit dem Bestücker prüfen.

Der Gerberjob meldet eine 90,05×60,05-mm-Begrenzungsbox wegen der 0,05-mm-Edge.Cuts-Strichbreite; die mechanische Mittellinienkontur ist 90×60 mm. Der eingetragene Stack-up ist eine ausdrücklich vorläufige Entwurfsannahme. Ihn ungeprüft beim Fertiger zu übernehmen würde keine Impedanzfreigabe herstellen.

Alle relevanten Dateien können über `SHA256SUMS` auf Unverändertheit geprüft werden. Der Hashbestand enthält native CAD-/Bibliotheksdaten, Dokumentation, Endberichte und Ausgaben. Er nimmt sich selbst und flüchtige Arbeits-/Cachedateien aus.

## Nicht nachgewiesen / Freigabe

**NO-GO für die Bestellung eines freigegebenen Akkugeräts.** Nicht nachgewiesen sind reale OLED-Kabelbelegung und Einschaltlast, Packpolung/-schutz/-temperaturfenster, Schalter-Zuverlässigkeit bei Kleinstrom, Piezo-Lautstärke, Gehäusepassung, garantierte wirksame MLCC-Kapazität, tatsächliche USB-Impedanz, Firmware-Konformität, Lastsprünge, Ruhestrom, Unterspannungsabschaltung, Verpol-Hot-Swap, Wärme sowie System-ESD/EMV. Die Schaltung ist mit R39 DNP standardmäßig gegen unbeabsichtigtes Laden gesperrt. Die einzeln abzuarbeitenden Messungen stehen in `doc/freigabe-checkliste.md`.

Es fand keine Bestellaktion, kein Commit und kein Push statt. Eine während der Arbeit auftauchende unversionierte KiCad-Projektsperrdatei am alten Projekt wurde nicht entfernt oder als Entwurfsänderung behandelt.
