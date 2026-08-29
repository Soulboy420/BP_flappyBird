# Prüfbericht zum Entwurf

Drei Durchgänge über Schaltplan und Layout. Geprüft wurde gegen die
Datenblätter von ESP32-C3-WROOM-02, MCP73831, AP2112K-3.3 und USBLC6-2SC6
sowie gegen den Projektplan.

| Durchgang | Gegenstand | Ergebnis |
|---|---|---|
| 1 | Schaltung | Abschnitt 1 und 2.1 bis 2.3 |
| 2 | Werkzeug (der Code, der die Schaltung erzeugt) | Abschnitt 6 |
| 3 | **Abgleich Schaltplan ↔ Layout, Fläche, Handbestückbarkeit** | Abschnitt 2.4, 2.5, 3 |

Die Abschnitte 2.1 bis 2.3 halten den Stand des ersten Durchgangs fest; die
dort genannten Abstände sind durch die Umplatzierung in Abschnitt 3 überholt.

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

### 2.4 Layout und Schaltplan waren auseinandergelaufen

Der Schaltplan war nach dem letzten Erzeugungslauf **von Hand in KiCad
nachbearbeitet** worden (Commit „update"): an J1-5 und J1-6 kamen zwei
5,1-kΩ-Widerstände R17 und R18 nach Masse dazu, und die beiden
Nichtanschluss-Markierungen an diesen Stiften verschwanden.

Diese Änderung war **nur im Schaltplan**. Weder `gen/design.py` noch die
Platinendatei kannten sie:

| | Schaltplan | Platine |
|---|---|---|
| Bauteile | 57 | 55 |
| R17, R18 | vorhanden | **fehlen** |
| J1-5, J1-6 | über R17/R18 nach Masse | **unbeschaltet** |

Sonst stimmten beide Dateien überein — 34 Netze, 122 Pinverbindungen, gleiche
Werte, gleiche Footprints. Es war also genau eine Abweichung, und sie war die
entscheidende: **eine Platine nach diesem Layout hätte keine CC-Widerstände
gehabt.**

Das ist kein Schönheitsfehler. An USB-C erkennt eine Quelle einen Verbraucher
ausschließlich daran, dass er CC1 oder CC2 mit 5,1 kΩ nach Masse zieht. Ohne
diese Widerstände schaltet ein C-nach-C-Kabel **kein VBUS** durch; das Gerät
ließe sich nur mit einem alten A-nach-C-Kabel laden.

**Behoben in der Wahrheitsquelle.** R17 und R18 stehen jetzt in
`gen/design.py` mit den Netzen `CC1` und `CC2`, J1-5 und J1-6 sind aus
`NO_CONNECT` heraus. Damit erzeugt `./erzeugen.sh` sie in **beide** Dateien.

**Beim Kauf zu prüfen:** viele USB-C-Breakouts bringen die 5,1 kΩ schon mit.
Sind sie vorhanden, ergeben R17/R18 parallel dazu 2,55 kΩ — ein Wert, der
weder als Rd noch als Ra gilt, und manche Quelle erkennt den Verbraucher dann
gar nicht. In diesem Fall R17 und R18 **weglassen**. Der Siebdruck sagt es
neben dem Steckverbinder: „R17/R18 nur ohne CC am Breakout".

### 2.5 Der eingeklemmte Mittelanschluss war ein Sonderfall zu wenig

Der Verdrahter reserviert für die Mittelanschlüsse der SOT-23-Gehäuse vorab
eine Durchkontaktierung, weil sie zwischen ihren eigenen Nachbarpads nicht
herauskommen. In der Liste standen `D1.2`, `U2.2` und `U3.2` — alle drei
Massepins, die Liste hieß im Code „Massevias".

`D1.5` (VBUS am ESD-Array) ist genauso eingeklemmt, stand aber nicht drin. In
Revision A ging das gut, weil rundherum viel Platz war. Auf der kleineren
Platine schlug die Verdrahtung dadurch fehl: VBUS muss von Pin 5 nach oben,
USB_DM von Pin 6 daneben nach unten — die beiden müssen sich kreuzen, und
ohne reservierten Weg belegte jeweils das zuerst verlegte Netz den einzigen
Ausgang des anderen.

**Behoben.** Die Liste heißt jetzt `VORAB_VIA`, enthält `D1.5` mit und nimmt
den Netznamen aus der Netzliste statt fest „GND" anzunehmen.

## 3. Flächennutzung — Revision B

Der Entwurf lag als 90 × 60 mm mit 27 % Füllgrad vor. Der erste Durchgang
empfahl, ihn so zu lassen; die Begründung war „Füllgrad 27 % ist gewollt,
jeder Millimeter Abstand hilft beim Handlöten".

**Diese Begründung hielt der Nachmessung nicht stand.** Der Platz war nicht
gleichmäßig verteilt, sondern lag als 450 mm² großes leeres Band herum,
während an anderer Stelle Bauteile fast aneinander stießen:

| engstes Paar (Revision A) | Umrissabstand |
|---|---|
| LS1 ↔ R13 | 0,15 mm |
| C9 ↔ R5 | 0,17 mm |
| C9 ↔ U1 | 0,27 mm |
| C8 ↔ R6 | 0,37 mm |

0,15 mm Umrissabstand sind rund 0,65 mm freies Kupfer zwischen zwei Pads.
Eine 1,6-mm-Meißelspitze kommt dort nicht mehr sauber an. Eine Platine, die
zu einem Viertel gefüllt ist und trotzdem solche Stellen hat, ist nicht groß
genug — sie ist ungleichmäßig belegt.

**Neu umplatziert.** Die Forderung „gut von Hand lötbar" steht jetzt als
prüfbare Regel im Layoutmodul und nicht mehr als Absicht im Bericht:

```python
LOETABSTAND = 0.8      # freier Abstand zwischen zwei Bauteilumrissen
RANDABSTAND = 0.5      # freier Abstand zum Platinenrand
```

`gen/chk_place.py` prüft beide bei jedem Durchgang und beendet sich mit
Fehlerstatus, wenn eine Paarung darunter liegt; `erzeugen.sh` bricht dann ab.

| | Revision A | Revision B |
|---|---|---|
| Platinenmaß | 90 × 60 mm = 5400 mm² | **72 × 51 mm = 3672 mm² (−32 %)** |
| Füllgrad | 27 % | 40 % |
| **kleinster Umrissabstand** | **0,15 mm** | **0,82 mm** |
| Leiterbahnlänge | 843 mm | 725 mm |
| Durchkontaktierungen | 113 | 87 |
| längstes Rückseitenstück | 10,8 mm | **5,4 mm** |

Die Platine ist also **ein Drittel kleiner geworden und gleichzeitig
großzügiger gelötet** — der gewonnene Platz kam aus dem leeren Band, nicht
aus den Lötabständen.

### 3.1 Was sich in der Aufteilung geändert hat

| Bereich | vorher | jetzt |
|---|---|---|
| oberer Streifen | USB, Laden, Akku, Schalter über 90 mm verteilt | dasselbe auf 72 mm, Regler U3 mit hinaufgezogen |
| Mitte links | Piezo, Anzeige, Tastereingabe in einer breiten Spalte | zwei enge Spalten links vom Modul, dazwischen eine 2,5 mm breite Gasse für USB D+/D− |
| Mitte rechts | Terminierung und Displaykabel weit auseinander | Spalte A (Abblockung, Reset) direkt am Modul, Spalte B (R5…R9) daneben, J3 am rechten Rand |
| unterer Streifen | ungenutzt | 0-Ω-Trennstelle R3 mit TP3/TP4, Prüfpunkte TP6 und TP12 neben der Antennensperrfläche |

Die funktionskritischen Abstände sind dabei **besser** geworden, nicht
schlechter:

| | Revision A | Revision B | Grenze |
|---|---|---|---|
| C9 (HF-Abblockung) am Modulpin 1 | 2,8 mm | 3,3 mm | ≤ 5 mm |
| C8 (Stützkondensator) am Modulpin 1 | 10,8 mm | **5,0 mm** | ≤ 15 mm |
| R5…R9 (Serienterminierung) am Modulpin | 4,8…9,8 mm | 7,8…9,8 mm | ≤ 10 mm |

### 3.2 Die Kühlfläche des Ladereglers hing an einer Leiterbahn

Beim Umplatzieren fiel auf, dass die VBAT-Kupferfläche (Projektplan 5.2,
≥ 100 mm²) in Revision A **nicht am Gehäuse von U2 lag**, sondern einige
Millimeter daneben und nur über eine 0,5 mm breite Leiterbahn angebunden war.
Thermisch bringt das fast nichts: 10 mm einer 0,5-mm-Bahn in 35 µm Kupfer
haben einen Wärmewiderstand von über 1000 K/W. Die Fläche erfüllte die
Zahlenvorgabe, nicht ihren Zweck.

**Geändert.** Die Fläche (35,5 … 49,0 mm | 7,0 … 16,0 mm, **122 mm²**) liegt
jetzt unmittelbar am VBAT-Pad von U2 und schließt C3, C4 und TP2 mit ein.
Damit gibt es einen flächigen Weg vom Gehäuse ins Kupfer.

Zusätzlich gilt: eine Kupferfläche, die **kein** Pad ihres Netzes enthält,
wird von KiCad gefüllt und anschließend als nicht angebundene Insel wieder
verworfen — die Kühlfläche wäre also stillschweigend verschwunden.
`gen/chk_place.py` prüft deshalb jetzt für jede Fläche in `NETZONES`, dass
mindestens ein Pad des Netzes darin liegt.

## 4. Gehäuse — Abweichung vom Projektplan

Der Projektplan skizziert in 4.4.4 ein Gehäuse von etwa 100 × 65 × 28 mm mit
der „Platine liegend auf vier Abstandsbolzen, **Akku daneben**".

Mit der Platine der Revision A (90 mm) ging das nicht auf: 90 mm plus etwa
35 mm Akku nebeneinander ergeben 125 mm und sprengen NF-07 (≤ 110 mm).
Mit 72 mm wäre es rechnerisch möglich (72 + 35 = 107 mm), aber der Akku läge
dann neben der Antenne — genau dort, wo Projektplan 4.5.7 Freiraum verlangt.
Es bleibt deshalb bei der Anordnung übereinander.

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
knapp 4 mm bleiben für die Kabelführung. Außenmaß des Gehäuses mit der
72 × 51 mm großen Platine damit etwa **80 × 59 × 26 mm**, deutlich innerhalb
von NF-07 (110 × 70 × 30 mm) und auch innerhalb der im Projektplan genannten
„ca. 100 × 65 mm". Die 3 mm Überschreitung aus Revision A sind damit erledigt.

## 5. Was bewusst so bleibt

| Punkt | Begründung |
|---|---|
| 10,5 % der Leiterbahnen auf der Rückseite (vorher 8,1 %) | die Mittelanschlüsse der SOT-23-Gehäuse sind zwischen ihren eigenen Nachbarpads eingeklemmt. Das längste Rückseitenstück ist dafür von 10,8 mm auf **5,4 mm** gesunken, und jedes Stück ist von Massevias flankiert — für den Rückstrom zählt die Länge des einzelnen Schnitts, nicht die Summe |
| Sperrstrom von D3 im Tiefschlafbudget | wird in M3 gemessen, Ersatztyp ist dokumentiert |
| C10 (Reset) mit 9,6 mm Abstand | Zeitkonstante 1 ms, der 100-nF-Kondensator hält den Knoten oberhalb weniger Kilohertz niederohmig |
| Prüfpunkte teils weit vom Messobjekt | TP10 liegt bei TP1 (VBUS), TP11 bei TP5 (Taster), TP12 bei TP3/TP4 (3,3 V) — jeder Messpunkt hat seine Masse in der Nähe, die Durchgangsprüfungen sind gleichstromig und dürfen weiter greifen |


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

Stand nach dem dritten Durchgang (Revision B):

| Prüfung | Ergebnis |
|---|---|
| Prüfstand T1–T3 und T5–T10 | **1612 Einzelprüfungen, 0 Fehler** |
| davon Abstandsprüfung ohne KiCad (T6) | **661 Kupferstücke paarweise, 0 Unterschreitungen** |
| Platzierung (`chk_place.py`) | 0 Beanstandungen |
| Abgleich Schaltplan ↔ Layout, unabhängig nachgerechnet | **0 Abweichungen** |
| Siebdruck auf Pads | keine Stelle |
| Reproduzierbarkeit | zweimal erzeugen ergibt **bitgleiche Dateien** |

### Noch offen — braucht eine KiCad-Installation

Die Umplatzierung entstand auf einem Rechner ohne KiCad. Die folgenden
Prüfungen konnten deshalb **für Revision B nicht laufen** und stehen aus:

| Prüfung | wie nachholen |
|---|---|
| T4 (erzeugte Bibliotheken gegen die unveränderte KiCad-Bibliothek) | `python3 gen/tests.py` |
| T11 (Fertigungsunterlagen) | `./erzeugen.sh` |
| ERC des Schaltplans | `./erzeugen.sh`, Schritt 5 |
| **Füllen der Masseflächen** | `./erzeugen.sh`, Schritt 6 — ohne diesen Schritt enthält die Platinendatei nur die Umrisse der Flächen |
| DRC und Netzlistenabgleich | `./erzeugen.sh`, Schritt 6 |
| Gerber, Bohrdaten, PDFs, Stückliste | `./erzeugen.sh`, Schritt 7 |
| Stufe 3 (Reproduzierbarkeit mit KiCad, Fehlererkennung) | `python3 gen/tests_stufe3.py` |

Ein einziger Lauf von `./erzeugen.sh` erledigt alles bis auf Stufe 3.
Die Dateien in `fertigung/` und `ausgabe/` stammen bis dahin aus Revision A
und dürfen **nicht** zur Bestellung benutzt werden.
