# Prüfstand

`hardware/gen/tests.py` und `tests_stufe3.py` prüfen den Entwurf in drei Stufen.
Stufe 1 und 2 laufen als letzter Schritt von `erzeugen.sh` automatisch mit.

```bash
cd hardware && ./erzeugen.sh          # erzeugt alles und prüft (Stufe 1+2)
python3 gen/tests.py                  # nur prüfen, etwa 2 Sekunden
python3 gen/tests_stufe3.py           # Reproduzierbarkeit + Fehlererkennung, etwa 10 min
```

## Stufe 1 — Grundbausteine einzeln

| | Prüfung |
|---|---|
| **T1** | S-Expression: `parse`/`dump` sind für echte KiCad-Dateien verlustfrei; Sonderzeichen überleben die Anführungszeichen |
| **T2** | Koordinatentransformationen gegen von Hand gerechnete Werte, für alle vier Drehungen und beide Spiegelungen; Stichprobe von 200 zufälligen Punktepaaren auf Abstandstreue |
| **T3** | Entwurfsdaten: jedes Symbol und jeder Footprint ladbar, **jeder Symbolpin hat ein Pad im Footprint**, jeder Pin genau einmal verdrahtet oder als offen markiert, kein Netz mit nur einem Pin, alle Bauteilwerte lesbar |
| **T4** | Erzeugte Bibliotheken: Versorgungssymbole haben genau einen Pin mit dem richtigen Netznamen; der Handlöt-Footprint hat 18 um genau 1 mm nach außen verlängerte Pads, die Innenkante bleibt unverändert, die Wärmevias sind auf 0,3 mm aufgebohrt |
| **T5** | Verdrahter: findet einen Weg um ein Hindernis, meldet einen unmöglichen Weg, wechselt bei Bedarf die Lage und setzt an jedem Lagenwechsel eine Durchkontaktierung; alle erzeugten Segmente sind waagerecht, senkrecht oder 45 Grad, keines hat die Länge null, alle liegen auf der Platine |
| **T6** | **Abstandsprüfung ohne KiCad**: alle 645 Kupferstücke (Bahnen, Vias, Pads) paarweise gegeneinander, mindestens 0,2 mm zwischen verschiedenen Netzen |

## Stufe 2 — Erzeugnisse einzeln

| | Prüfung |
|---|---|
| **T7** | Schaltplan: jedes Bauteil genau einmal, Wert und Footprint stimmen mit `design.py`, Position stimmt mit dem Layoutmodul, **jeder Pin ist nachweislich angebunden** (Draht, Bezeichner, Versorgungssymbol oder Nichtanschluss an genau seiner Koordinate), kein Draht der Länge null, alle Drahtenden im 1,27-mm-Raster, Verknüpfungspunkt an jeder T-Stelle, keine zwei verschiedenen Versorgungssymbole aufeinander |
| **T8** | Platine: jedes Bauteil an der geplanten Stelle und Drehung, **jedes Pad trägt das richtige Netz**, nur Kupferlagen benutzt, kleinste Bahn ≥ 0,2 mm, kleinste Bohrung ≥ 0,3 mm, Umriss geschlossen, **alle Kupferzonen gefüllt**, kein Kupfer in der Antennensperrfläche |
| **T9** | Schaltungstopologie: **kein rein ohmscher Pfad von einer Versorgung nach Masse** (das wäre ein Dauerstrom und würde NF-04 sprengen), `+3V3` und `+3V3_MCU` hängen ausschließlich über R3 zusammen, jedes Displaysignal führt über genau einen 68-Ω-Widerstand zwischen Modul und Steckverbinder, Strapping-Pins haben ihren Pull-up, die Sicherung sitzt direkt an der Akkubuchse; Ladestrom, LED-Ströme, Piezostrom gegen das ESP32-C3-Datenblatt, Entprell- und Reset-Zeitkonstante |
| **T10** | Funktionskritische Abstände auf der Platine (Abblockung, Serienterminierung) und Strombelastbarkeit nach IPC-2221 |
| **T12** | **Datenblattbelege**: jeder Beleg wird geoeffnet und sein Inhalt gegen die Kennung des Bauteils geprueft; jedes bestueckte Bauteil braucht einen Beleg oder einen begruendeten Eintrag in `BELEG_FEHLT`. Diese Stufe schliesst Befund K-4 — ein falsch abgelegtes PDF kann nicht mehr unbemerkt als Nachweis durchgehen. Ohne `pdfplumber` wird nur die Existenz geprueft. |
| **T11** | Fertigungsunterlagen: Bohrungszahl in der Excellon-Datei gegen die Platine, Umrissmaß im Gerber, **Masseflächen in den Kupfer-Gerbern vorhanden**, Stückliste enthält genau die bestückten Bauteile |

## Stufe 3 — Verhalten des Werkzeugs

| | Prüfung |
|---|---|
| **S3-A** | **Reproduzierbarkeit**: zweimal erzeugen ergibt bitgleiche Dateien, auch für den Verdrahter |
| **S3-B** | Gesamtlauf mit KiCad: ERC, DRC, Abgleich Schaltplan/Layout, Fertigungsdaten vorhanden und nicht leer |
| **S3-C** | **Fehlererkennung**: acht absichtlich eingebaute Fehler werden in `design.py` eingesetzt, alles neu erzeugt, und der Prüfstand muss sie finden |

Die eingebauten Fehler und wie sie auffallen:

| eingebauter Fehler | wird gefunden von |
|---|---|
| Netz auf das falsche Bauteil gelegt | „kein Pin in zwei Netzen" |
| Pin aus einem Netz vergessen | „jeder Pin ist versorgt" |
| R1 auf 2,2 kΩ verstellt | Ladestrom läge bei 455 mA statt 147 mA |
| Piezowiderstand auf 68 Ω verkleinert | 48,5 mA überschreiten I_OL = 28 mA |
| ein Serienwiderstand auf 33 Ω | „alle fünf mit 68 Ohm" |
| Pull-up am Strapping-Pin entfernt | „kein Netz mit nur einem Pin" |
| Serienwiderstand überbrückt | „kein Pin in zwei Netzen" |
| Dauerstrompfad von 3,3 V nach Masse eingebaut | „kein Pin in zwei Netzen" |
| Kondensatorwert ohne Spannungsklasse | T3 „Kondensatorwert mit Spannung und Dielektrikum“ |
| Spannungsklasse unter 2 x Betriebsspannung | T9j „Spannungsklasse >= 2 x Betriebsspannung“ |
| Datenblatt eines fremden Bauteils abgelegt | T12 „Beleg passt zum Bauteil“ |

Die drei letzten Zeilen sind aus dem Befundbericht nachgeruestet. Sie decken die
Klasse ab, die der Pruefstand bis dahin konstruktionsbedingt nicht sehen konnte:
Fehler, die nicht in der Netzliste oder der Geometrie stehen, sondern in der
Bauteilwirklichkeit — Bauteilmass, Spannungsfestigkeit, Beleglage.

Die letzten drei der urspruenglichen Mutationen zeigen, dass die inhaltlichen Prüfungen greifen und nicht nur
veraltete Dateien auffallen: nach jeder Mutation wird erst neu erzeugt.

**Achtung:** `tests_stufe3.py mutation` verändert `design.py` vorübergehend.
Währenddessen darf `tests.py` nicht parallel laufen.
