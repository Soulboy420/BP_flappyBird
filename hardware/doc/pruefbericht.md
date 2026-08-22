# Prüfbericht zum Entwurf

Zweiter Durchgang über Schaltplan und Layout, nach der ersten Fassung.
Geprüft wurde gegen die Datenblätter von ESP32-C3-WROOM-02, MCP73831,
AP2112K-3.3 und USBLC6-2SC6 sowie gegen den Projektplan.

## 1. Elektrisch geprüft und in Ordnung

| Prüfpunkt | Ergebnis |
|---|---|
| Pinbelegung aller vier Halbleiter gegen Datenblatt | stimmt |
| Kanalpaarung des ESD-Arrays (Pins 1/6 und 3/4) | stimmt, D+ und D− werden nicht vertauscht |
| USB D−/D+ an IO18/IO19, keine Serienwiderstände | richtig für den ESP32-C3 |
| Polarität beider LEDs, Kathode D3 an VBAT | stimmt |
| Mittelanschluss SW1 (Pin 2) trägt VBAT | stimmt |
| Ladestromwiderstand R1 = 6,8 kΩ → 147 mA | stimmt (1000 V / 6,8 kΩ) |
| Strapping-Pins IO2, IO8, IO9 beim Start hoch | R15, R16, chipinterner Pull-up |
| Aderfolge J3 gegen Projektplan 4.4.1 | stimmt |
| Reset-Zeitkonstante R4 · C10 = 1 ms | stimmt |
| Tasterentladestrom 3,3 V / (100 Ω + 220 Ω) = 10 mA | stimmt |
| Vorwiderstand Lade-LED: (5 V − 2 V) / 1 kΩ = 3 mA in STAT (max. 25 mA) | stimmt |

## 2. Gefunden und geändert

### 2.1 Piezo überschritt den zulässigen GPIO-Strom

Mit dem im Projektplan genannten R13 = 100 Ω zieht der Piezo an jeder Flanke
3,3 V / 100 Ω = **33 mA**. Das ESP32-C3-Datenblatt nennt für einen Anschluss
I_OH = 40 mA und **I_OL = 28 mA** — der Senkstrom wäre überschritten, und zwar
schon bei der stärksten Treiberstufe; voreingestellt sind ohnehin nur 20 mA.

**Geändert auf R13 = 220 Ω** → 15 mA. Die Lautstärke ändert sich praktisch
nicht: der Piezo ist eine Kapazität von etwa 20 nF, die Zeitkonstante steigt
von 2 µs auf 4,4 µs und bleibt gegenüber der Halbperiode von 125 µs bei 4 kHz
bedeutungslos.

### 2.2 Abblockung saß zu weit vom Modul entfernt

In der ersten Fassung lagen C8 (10 µF) und C9 (100 nF) **17 mm** vom
Versorgungspin des Funkmoduls entfernt. Projektplan 5.4 verlangt „unmittelbar
an den Versorgungspins", und die Forderung hat einen messbaren Hintergrund:
NF-06 erlaubt beim Sendevorgang höchstens 100 mV Einbruch. 17 mm Leiterbahn
entsprechen etwa 15 nH — die 100 nF hätte bei den schnellen Flanken kaum noch
gewirkt.

**Umplatziert.** Neue Abstände:

| Kondensator | vorher | jetzt |
|---|---|---|
| C9 (100 nF, HF-Abblockung) | 17,1 mm | **2,8 mm** |
| C8 (10 µF, Stützkondensator) | 14,2 mm | 10,8 mm |
| C11 (Entprellung) | 15,8 mm | 5,8 mm |
| R5…R9 (Serienterminierung) | 8,8…13,8 mm | 4,8…9,8 mm |

C8 darf weiter weg liegen: er stützt den Lastsprung über 10 µs, dafür ist die
Leitungsinduktivität ohne Bedeutung. Die schnelle Arbeit macht C9.

C10 (Reset) liegt mit 14,6 mm am weitesten entfernt. Das ist unkritisch — die
Zeitkonstante beträgt 1 ms, und der 100-nF-Kondensator hält den Knoten
oberhalb weniger Kilohertz ohnehin niederohmig.

### 2.3 Rückseitige Leitungsstücke reduziert

Durch die Umplatzierung sank der Anteil der Leiterbahnen auf der Rückseite von
9,0 % auf **8,1 %** (69 mm von 860 mm, längstes Einzelstück 10,8 mm). Die
Massefläche auf B.Cu bleibt **eine zusammenhängende Fläche von 4904 mm²**.

## 3. Flächennutzung

| | |
|---|---|
| Platine | 90 × 60 mm = 5400 mm² |
| Summe der Bauteilumrisse | 1435 mm² |
| Füllgrad | **27 %** |
| wirklich ungenutzt | etwa 450 mm² (Band x 33…90 mm, y 24…34 mm) |

**Ja, es ginge kleiner** — realistisch etwa 90 × 52 mm oder 84 × 52 mm, also
13 bis 19 % weniger Fläche. Dafür müssten das obere Bauteilband und der
Piezo umgesetzt werden, weil die linke Spalte (USB-Breakout, Piezo, Anzeige,
Tastereingabe) über die volle Höhe belegt ist.

**Empfehlung: so lassen.** Drei Gründe:

1. Der Preis ändert sich nicht. Beide Maße liegen im selben Preisfenster der
   Prototypenfertiger (bis 100 × 100 mm); fünf Platinen kosten so oder so
   etwa 25 €.
2. Der Füllgrad von 27 % ist **gewollt**. Risiko R2 des Projektplans nennt
   Lötfehler bei der Eigenbestückung als hohes Risiko mit hoher Wirkung. Jeder
   Millimeter Abstand zwischen zwei Bauteilen ist ein Millimeter, in dem die
   Lötspitze frei ansetzen kann.
3. Das Gehäuse hat Platz (siehe unten).

Wer trotzdem kompakter will: in `gen/layout_pcb.py` `W`, `H` und die
Bauteilkoordinaten ändern, dann `./erzeugen.sh` laufen lassen. Der
Rasterverdrahter verlegt selbstständig neu, DRC und Netzlistenabgleich
laufen automatisch mit.

## 4. Gehäuse — Abweichung vom Projektplan

Der Projektplan skizziert in 4.4.4 ein Gehäuse von etwa 100 × 65 × 28 mm mit
der „Platine liegend auf vier Abstandsbolzen, **Akku daneben**".

Das geht mit dieser Platine nicht auf: 90 mm Platine plus etwa 35 mm Akku
nebeneinander ergeben 125 mm und sprengen NF-07 (≤ 110 mm).

**Der Plan widerspricht sich hier selbst** — Abschnitt 4.4.3 sagt bereits
„Der Akku wird mit doppelseitigem Klebeband **im Gehäuseboden** fixiert".
Genau so geht die Rechnung auf:

| Ebene | Höhe |
|---|---|
| Akku auf dem Gehäuseboden | 6 mm |
| Luft und Abstandsbolzen | 2 mm |
| Leiterplatte | 1,6 mm |
| höchstes Bauteil (Piezo LS1) | 9,5 mm |
| **Summe** | **19,1 mm** |

Bei 28 mm Außenhöhe und 2,5 mm Wandstärke stehen 23 mm zur Verfügung —
knapp 4 mm bleiben für die Kabelführung. Außenmaß des Gehäuses damit etwa
**98 × 68 × 26 mm**, innerhalb von NF-07 (110 × 70 × 30 mm).

Zu beachten: 68 mm überschreiten die im Plan genannten „ca. 65 mm" um 3 mm.
Wer bei 65 mm bleiben will, muss die Platine auf 90 × 55 mm bringen.

## 5. Was bewusst so bleibt

| Punkt | Begründung |
|---|---|
| Freiraum um U3 nur 2,1 mm statt 3 mm (4.5.3) | begrenzender Nachbar ist ein flaches 0805; die Anschlüsse von U3 zeigen frei nach links und rechts |
| 8,1 % der Leiterbahnen auf der Rückseite | die Mittelanschlüsse der SOT-23-Gehäuse sind zwischen ihren eigenen Nachbarpads eingeklemmt; jedes Stück ist von Massevias flankiert |
| Sperrstrom von D3 im Tiefschlafbudget | wird in M3 gemessen, Ersatztyp ist dokumentiert |
| C8 mit 10,8 mm Abstand | Stützkondensator für 10-µs-Lastsprünge, Induktivität ohne Bedeutung |


---

# Zweiter Durchgang: Prüfung des Werkzeugs

Der erste Durchgang prüfte die Schaltung. Dieser prüft den Code, der sie
erzeugt — jeder Baustein zuerst einzeln, dann alles zusammen. Aufbau und
Umfang stehen in `pruefstand.md`.

## 6. Gefunden und behoben

### 6.1 Die Wegsuche benutzte eine unzulässige Schätzfunktion

Der Verdrahter suchte mit A\* und schätzte die Restkosten über die
Manhattan-Distanz. Weil er aber auch diagonal laufen darf (Kosten 1,414 statt
2,0), **überschätzt** Manhattan die tatsächlichen Restkosten um bis zu 41 %.
Eine überschätzende Schätzfunktion ist unzulässig: A\* liefert dann nicht mehr
garantiert den kürzesten Weg, sondern nur noch irgendeinen.

Ersetzt durch die Oktil-Distanz `max(dx,dy) + 0,414·min(dx,dy)`, die die
tatsächlichen Kosten nie überschätzt.

**Wirkung:** Gesamtlänge der Leiterbahnen 859,9 mm → **843,5 mm**, Zahl der
Segmente 376 → 371, bei gleicher Viazahl.

### 6.2 Die Verdrahtung hing an der Reihenfolge

Mit den nun kürzeren Wegen belegten frühe Netze Platz, den `LED_CHG` gebraucht
hätte — die Verdrahtung schlug fehl. Ein Verdrahter, der Netz für Netz vorgeht
und nichts zurücknimmt, ist immer reihenfolgeabhängig.

**Behoben:** Schlägt ein Netz fehl, wird es in der Reihenfolge vier Plätze nach
vorn geschoben und alles noch einmal verlegt (bis zu zwölf Versuche). Hier
genügt ein Versuch. Der Vorgang ist deterministisch — die Reproduzierbarkeit
ist geprüft (S3-A).

### 6.3 Entartete Leiterbahnstücke

Die Anbindung eines Massepads an das 0,2-mm-Raster erzeugte **drei Segmente der
Länge null** und **sechs schräge Stummel** von höchstens 0,12 mm. Beides ist
elektrisch belanglos, aber Segmente der Länge null sind im Layouteditor lästig
und in manchen Gerber-Betrachtern auffällig.

**Behoben:** Der Versatz wird jetzt in bis zu zwei waagerechte bzw. senkrechte
Stücke zerlegt; deckt sich das Pad schon mit dem Raster, entfällt der Stummel.

### 6.4 Warnungen des Verdrahters blieben folgenlos

Konnte ein Massepad kein Via bekommen, stand eine Warnung auf dem Bildschirm —
das Skript lief aber weiter und `erzeugen.sh` ebenfalls. Aufgefallen wäre das
erst beim DRC, und auch nur, wenn die Massefläche das Pad nicht ohnehin
erreicht hätte.

**Behoben:** Der Verdrahter endet jetzt mit Fehlerstatus, wenn eine Warnung
aufgetreten ist. `erzeugen.sh` bricht dadurch ab.

### 6.5 Ohne den Füllschritt fehlt in den Gerbern die gesamte Massefläche

Der Generator schreibt die Masseflächen nur als Umriss; gefüllt werden sie erst
von KiCad. Wer `mk_pcb.py` einzeln laufen lässt und danach Gerber erzeugt,
bekommt **Kupferlagen ganz ohne Massefläche** — und nichts weist darauf hin.
Nachgemessen: 0 Flächenbereiche statt 17 auf der Oberseite und 1 auf der
Rückseite.

**Behoben:** Der Füllschritt ist in `erzeugen.sh` als eigener, kommentierter
Schritt ausgewiesen, und T8 schlägt fehl, wenn eine Kupferzone ungefüllt ist.

### 6.6 Der Prüfstand hängt jetzt am Erzeugen

`erzeugen.sh` hat einen achten Schritt bekommen: Stufe 1 und 2 des Prüfstands
laufen bei jedem Durchgang mit. Wer die Schaltung ändert, merkt sofort, wenn
etwas nicht mehr zusammenpasst.

## 7. Zur Kenntnis: KiCad schreibt die Platine in seinem eigenen Format zurück

Der Generator erzeugt das KiCad-9-Format (`version 20241229`). Der Füllschritt
lässt KiCad die Datei speichern, und KiCad 10 schreibt sie dabei in seinem
Format zurück (`version 20260206`; die Netztabelle am Dateianfang entfällt,
Pads nennen ihr Netz beim Namen).

Für die Gruppe heißt das: **die Platinendatei im Repository lässt sich nur mit
der KiCad-Fassung öffnen, die den Füllschritt ausgeführt hat** — hier KiCad 10.
Wer mit KiCad 9 arbeitet, lässt `erzeugen.sh` einmal auf seinem Rechner laufen;
dann liegt die Datei im 9er-Format vor. Der Prüfstand kommt mit beiden Formaten
zurecht.

## 8. Ergebnis

| Prüfung | Ergebnis |
|---|---|
| Stufe 1 und 2 | **1664 Einzelprüfungen, 0 Fehler** |
| davon Abstandsprüfung ohne KiCad | 645 Kupferstücke paarweise |
| Reproduzierbarkeit | zweimal erzeugen ergibt **bitgleiche Dateien** |
| Fehlererkennung | **8 von 8** eingebauten Fehlern gefunden |
| ERC des Schaltplans | 0 Verstöße |
| DRC, offene Verbindungen, Abgleich | 0 / 0 / 0 |
