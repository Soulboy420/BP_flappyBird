# Befundbericht Flappy-C3

**Schaltungs- und Layout-Review · Handrechnung gegen Originaldatenblätter**

| | |
|---|---|
| Baugruppe | 90 × 60 mm, FR4 1,6 mm, 2 Lagen |
| Bestückung | 27 Positionen, 100 % Hand |
| Selbstprüfung (Referenz) | 1688 Prüfungen, 0 Fehler |
| Manuelle Prüfung | 4 kritische, 11 mäßige Befunde, 10 bestätigte Stärken, 7 entkräftete Verdachtspunkte |
| Datum | 2026-09-03 |

Vollständige manuelle Nachrechnung gegen alle 16 archivierten Datenblätter, die erzeugte
Netzliste und die tatsächliche Kupfergeometrie der `.kicad_pcb`. Die vorhandene
Selbstprüfung wurde einmalig als Referenz gefahren und danach bewusst ignoriert.
Alle Geometrie- und Flächenangaben sind aus der Platinendatei nachgemessen, nicht aus
der Projektdokumentation übernommen.

---

## 1 Executive Summary — Reifegrad 6/10

Der **Entwurfsprozess** ist auf Master-Niveau: generativer Entwurf aus einer
Wahrheitsquelle, Mutationstests, bitgleiche Reproduzierbarkeit, eine Massefläche, um die
man Industrieentwürfe beneidet.

Der **Entwurf selbst** hat vier Fehler, die vor dem Bestellen behoben werden müssen — und
alle vier liegen exakt dort, wo der Prüfstand konstruktionsbedingt blind ist: an der
Grenze zwischen `design.py` und der physikalischen Welt. Die Platine besteht 1688 eigene
Prüfungen und ist trotzdem in dieser Form nicht bestückbar.

Die Bewertung 6/10 setzt sich zusammen aus: Layout- und Massedisziplin 9/10,
Werkzeug- und Prüfstandsqualität 9/10, Schaltungsauslegung 6/10,
Bauteil- und Beschaffungsdokumentation 3/10.

---

## 2 Methodik — was der Prüfstand beweist und was er nicht sehen kann

Die acht eingebauten Mutationen in `tests_stufe3.py` werden alle gefunden. Das ist kein
Zufall: alle acht sind Netzlisten- oder Wertfehler, also genau die Klasse, die der
Prüfstand modelliert. **Kein einziger eingebauter Fehler ist ein physikalischer Fehler.**
Deshalb liegt die Trefferquote auf den eigenen Mutanten bei 100 % und auf den vier realen
Showstoppern bei 0 %.

### Wird zuverlässig geprüft — das Modell gegen sich selbst

- Jeder Symbolpin hat ein Pad, jedes Netz ≥ 2 Pins, jeder Pin genau einmal verdrahtet
- Paarweise Kupferabstände über 666 Objekte, ≥ 0,2 mm
- Schaltplan- und Layoutposition gegen `design.py`
- Strombelastbarkeit der Bahnbreite nach IPC-2221
- Kein rein ohmscher Pfad Versorgung → Masse
- Bitgleiche Reproduzierbarkeit inkl. Verdrahter

### Konstruktionsbedingt unsichtbar — das Modell gegen die Physik

| Blinder Fleck | Folge in diesem Entwurf |
|---|---|
| **Bauteil ↔ Footprint.** Geprüft wird Footprint gegen Platine, nie Datenblatt gegen Footprint | K-1 |
| **Spannungsfestigkeit, Dielektrikum, DC-Bias.** Der Wert „4u7" hat keine Physik | K-3 |
| **Schleifen statt Abstände.** T10 misst 2,8 mm zum 3V3-Pad, nie den Rückweg | (entkräftet) |
| **Fläche statt Wärmewiderstand.** 114 mm² erfüllt die Vorgabe, 8 mm entfernt | M-2 |
| **Bahnbreite statt Pfadspannungsfall.** Die PTC hat mehr Widerstand als alle Bahnen zusammen | M-1 |
| **Rückstrompfade.** 35 Kreuzungen über Schlitze in der Masse | M-7 |
| **Leckströme und Toleranzstapel über Temperatur** | M-4 |

---

## 3 Kritische Befunde (Showstopper)

### K-1 — Der Piezo passt nicht auf die Platine (Faktor 2,6 im Rastermaß)

*Quelle: CEP-1114, Same Sky 09/11/2024, Maßzeichnung S. 2*

Der archivierte CEP-1114 ist **Ø 30,0 × 13,5 mm mit 20,0 mm Anschlussrastermaß**. Der
zugewiesene Footprint `Buzzer_12x9.5RM7.6` ist laut eigener Beschreibung „Generic Buzzer,
D12mm height 9.5mm with RM7.6mm", die Pads liegen bei `(0,0)` und `(7,6, 0)`. Wert und
Dateiname behaupten beide „12 mm"; das Datenblatt sagt etwas anderes.

```
Nachweis — Geometrie

Rastermaß  Bauteil  20,0 mm    ↔ Footprint  7,6 mm    → Δ 12,4 mm (263 %)
Körper     Bauteil  Ø 30,0 mm  ↔ Footprint  Ø 12,0 mm → Fläche 707 statt 113 mm²

LS1-Mitte (20,92 / 30,00) mm, Ø30-Hüllkreis ⇒ x 5,9…35,9 · y 15,0…45,0
Kollision mit: U1  J1  D1  D4  H4  C11  R13  R14  R15  R18
→ überdeckt USB-Stiftleiste, ESD-Array, eine Befestigungsbohrung
  und eine Ecke des Funkmoduls.
```

**Warum kein Test das findet:** T3 prüft „jeder Symbolpin hat ein Pad im Footprint" —
beide haben zwei Pins. T6 und T8 prüfen den Footprint gegen die Platine, und dieser
Footprint ist sauber platziert. Die Kette Datenblatt → Footprint wird nirgends
geschlossen.

**Abhilfe.** Entweder Footprint auf Ø30 / RM 20 ändern und LS1 wie Display und Taster über
eine zweipolige JST-XH-Buchse abgesetzt montieren (passt zur bereits gewählten Architektur
„Peripherie am Kabel", Platine bleibt unverändert klein) — oder auf einen echten
12-mm-Wandler wechseln. Für den vorhandenen KiCad-Footprint
`Buzzer_TDK_PS1240P02BT_D12.2mm_H6.5mm` ist das Rastermaß 5,0 mm, also ebenfalls nicht
7,6 mm; ein passendes Bauteil muss explizit mit Ø ≤ 12,5 mm **und** RM 7,6 mm belegt und
sein Datenblatt abgelegt werden.

---

### K-2 — Doppeltes Rd am USB-C: 0,204 V fällt in die Totzone der Quellenerkennung

*Quelle: USB Type-C R2.x Tab. 4-36 (Rp/Rd) + `design.py` R17/R18*

R17/R18 = 5,1 kΩ sind für eine UFP-Senke **korrekt**, solange das aufgesteckte Breakout
keine eigenen Pull-downs hat. Fast alle handelsüblichen USB-C-Breakouts haben sie. Dann
liegen 2 × 5,1 kΩ parallel.

```
Nachweis — CC-Spannung gegen die Erkennungsschwellen

R_d,eff = 5k1 ∥ 5k1 = 2,55 kΩ

Quelle „Default USB Power" (I_p = 80 µA):
  V_CC = 80 µA · 2550 Ω = 0,204 V
  vRa_max = 0,20 V  <  0,204 V  <  vRd-Connect_min = 0,25 V
  → undefiniert. VBUS wird u. U. nie eingeschaltet.
  (resistives Rp 56 kΩ an 5 V: 5·2550/58550 = 0,218 V — dieselbe Totzone)

Quelle 1,5 A (180 µA): 0,459 V > 0,40 V   erkannt
Quelle 3,0 A (330 µA): 0,842 V > 0,80 V   erkannt, aber nur 42 mV Reserve
  Rp −20 % (264 µA):   0,673 V < 0,80 V   NICHT erkannt

Einzelnes Rd = 5k1: 0,408 / 0,918 / 1,683 V — alle drei Klassen sicher
```

Das Fehlerbild ist die unangenehmste Sorte: „Ladegerät A geht, Ladegerät B nicht",
reproduzierbar nur mit bestimmten Netzteilen, und im Labor mit einem 1,5-A-Netzteil nicht
auffindbar.

**Abhilfe.** R17/R18 als **DNP** kennzeichnen — in Stückliste, Bestückungsplan und im
Siebdruck bei J1 („CC-Rd nur bestücken, wenn Breakout ohne Rd"). Sauberer: J1 und das
Breakout streichen und eine echte USB-C-Buchse auf die Platine setzen. Das löst zugleich
M-8 (ESD-Array sitzt dann vor statt hinter der Verkabelung).

---

### K-3 — C3 ohne Spannungsfestigkeit: die CV-Schleife des Ladereglers ist unkompensiert

*Quelle: MCP73831 DS20001984G § 6.1.1.4 S. 18 · Vishay VJ S. 2*

Microchip fordert wörtlich: *„a minimum capacitance of 4.7 µF is recommended to bypass the
V_BAT pin to V_SS. This capacitance provides compensation **when there is no battery
load**."* Die Stückliste nennt für C3 nur „4u7" — keine Spannungsklasse, kein
Dielektrikum, keine Toleranz. Damit ist der wirksame Wert unbestimmt.

```
Nachweis — DC-Bias bei 4,2 V, 0805

4u7 /  6,3 V X5R  → ca. 33 %  = 1,6 µF   (66 % unter Vorgabe)
4u7 / 16   V X7R  → ca. 78 %  = 3,7 µF   (21 % unter Vorgabe)
4u7 / 25   V X7R  → ca. 88 %  = 4,1 µF   (13 % unter Vorgabe)
10u / 25   V X7R  → ca. 62 %  = 6,2 µF   erfüllt

Fehlerbild: CV-Schleife schwingt genau dann, wenn keine Zelle steckt —
also beim ersten Einschalten am USB ohne Akku, dem häufigsten Fall
bei der Inbetriebnahme.
```

Dieselbe Lücke betrifft C1, C5, C6, C8. Zusätzlich: die archivierte Kondensatorreihe
(Vishay VJ Commercial) endet in 0805 bei **470 nF X7R** bzw. 4,7 nF C0G. **6 von 11**
Kondensatoren im Entwurf — C1, C3, C5, C6, C8 — sind aus dieser Reihe in 0805 **überhaupt
nicht lieferbar**. Nur die sechs 100-nF-Positionen sind durch das abgelegte Datenblatt
gedeckt.

**Abhilfe.** C3 → **10 µF / 25 V X7R 0805**. Vollständige Spannungs- und
Dielektrikumsangabe für alle Kondensatoren in `design.py` aufnehmen und ein Datenblatt
einer Reihe ablegen, die diese Werte tatsächlich führt (z. B. Murata GRM21 oder
Samsung CL21).

---

### K-4 — Der Verpolungsschutz ist mit den vorliegenden Unterlagen nicht nachweisbar

*Quelle: `doc/datenblaetter/D3_B5819W_DiodesInc.pdf` → enthält DS30097*

Die Datei `D3_B5819W_DiodesInc.pdf` enthält nicht das Datenblatt der Schottky-Diode
B5819W, sondern das der **1N4148WS / BAV16WS** — einer Kleinsignal-Schaltdiode im SOD-323.
Von 16 Datenblättern ist dies das einzige mit falschem Inhalt; die übrigen 15 wurden
geprüft und stimmen.

```
Nachweis — was passiert, wenn nach dem abgelegten Dokument beschafft wird

Abgelegtes Bauteil 1N4148WS:
  I_FM = 300 mA · I_O = 150 mA
  I_FSM = 4,0 A @ 1 µs · 1,0 A @ 1 s · R_θJA = 625 °C/W · Gehäuse SOD-323

Crowbar-Strom bei verpolter Zelle (4,2 V, ESR 0,15 Ω, PTC 0,15…0,9 Ω):
  I = (4,2 − 0,6) / 0,35…0,70 Ω = 5,1 … 10,3 A
  → 13…34-fach über I_FM. Diode verdampft in Mikrosekunden.

Zusätzlich: SOD-323 passt nicht auf das Land D_SOD-123.
```

Der Footprint SOD-123 und der Wert B5819W in `design.py` sind stimmig — es ist die
Belegdatei, die fehlt. Für ein Bachelorprojekt, dessen Prüfbericht Datenblattkonformität
behauptet, ist das ein harter Befund: die Kernaussage zum Verpolungsschutz stützt sich auf
ein Dokument, das ein anderes Bauteil beschreibt.

**Abhilfe.** Richtiges B5819W-Datenblatt ablegen — und anschließend M-3 nachrechnen, denn
auch der echte B5819W übersteht diesen Fall vermutlich nicht.

---

## 4 Mäßige Risiken und Grenzfälle

### M-1 — Die PTC frisst rund ein Drittel der nutzbaren Akkukapazität

*Quelle: MF-PSMF050X S. 1 · AP2112-3.3 S. 8 · ESP32-C3 Tab. 6-4*

F1 liegt in Reihe mit der Zelle und trägt jeden Entladestrom. Ihr Widerstand ist im
Datenblatt mit **R_min = 0,15 Ω / R_1max = 0,9 Ω** angegeben — mehr als alle Leiterbahnen
der Baugruppe zusammen. Der Prüfstand misst Bahnbreiten nach IPC-2221 und übersieht die
Bauteile im Pfad vollständig.

```
Nachweis — Dropout-Bilanz bei I = 345 mA (802.11b TX-Spitze)

PTC   0,345 A · 0,15…0,9 Ω = 0,052 … 0,311 V
SW1   0,345 A · 0,020 Ω    = 0,007 V
LDO   interpoliert aus 125 mV @ 300 mA / 250 mV @ 600 mA
                            typ 0,144 V · max 0,230 V

V_Zelle,min für geregelte 3,3 V:
  typisch     3,3 + 0,144 + 0,173 + 0,007 = 3,63 V
  worst case  3,3 + 0,230 + 0,311 + 0,007 = 3,85 V

Ohne F1 im Entladepfad:        3,54 V
Mit P-MOSFET (55 mΩ):          3,47 V
Gewinn: rund 30 % nutzbare Kapazität im Burst-Betrieb.
```

Unterhalb dieser Schwelle stirbt nichts — der LDO geht in Dropout und die Schiene folgt
der Zelle bis hinunter zu V_DD33,min = 3,0 V (Tab. 6-2). Aber sie ist dann ungeregelt und
wird im TX-Takt moduliert.

Zusätzlich: I_hold derated von 0,50 A (23 °C) auf **0,40 A bei 40 °C** und 0,33 A bei
60 °C — bei 345 mA im geschlossenen Gehäuse bleiben nur 1,2…1,6-fach Reserve gegen
Fehlauslösung. (Beim Laden entlastet: F1 trägt I_Last − I_Ladung.)

---

### M-2 — Die 114 mm² Kühlfläche liegt 8 mm neben dem Bauteil und wirkt praktisch nicht

*Quelle: MCP73831 S. 5 Note 2 · `layout_pcb.py` NETZONES · gemessen aus `.kicad_pcb`*

Die Vorgabe „≥ 100 mm² Kupfer zur Wärmeabfuhr des Ladereglers" ist als Flächenzahl
erfüllt: die VBAT-Zone ist ausgefüllt und misst **113,7 mm²**. Physikalisch ist sie
wirkungslos, weil sie über eine 0,5 mm breite Bahn angebunden ist.

```
Nachweis — Wärmepfad, gemessen aus der Platinendatei

U2 Pad 3 (V_BAT) @ (42,65 / 10,95) mm
VBAT-Zone bbox (48,0 / 16,5) … (66,0 / 23,0), nächster Punkt 7,92 mm
Anbindung: Kette aus 0,5 mm Bahnen, Weglänge ≈ 12 mm

R_th,Bahn = L / (κ · A) = 12·10⁻³ / (400 · 0,5·10⁻³ · 35·10⁻⁶)
          ≈ 1720 K/W    gegen R_θJA,Gehäuse = 230 K/W
→ Engstelle, kein Kühlkörper.

Reales Kupfer um U2 (Massefläche F.Cu, gerastert):
  r = 3 mm →   4 mm²
  r = 5 mm →  34 mm²
  r = 8 mm → 132 mm²
⇒ R_θJA real ≈ 180…210 K/W (Datenblatt: 230 minimal, 130 „large copper")
```

```
Nachweis — Sperrschichttemperatur

P_D = (V_DD,max − V_PTH,min) · I_REG,max                      [§ 6.1.1.3]
    = (5,25 − 0,64·4,20) · 0,147·1,10 = (5,25 − 2,688) · 0,162
    = 0,415 W        (Aufgabenstellung mit 3,0 V / 147 mA: 0,331 W)

ΔT  = 0,415 · 200 K/W = 83 K
T_J = 108 °C @ 25 °C Umgebung · 123 °C @ 40 °C
→ Thermische Regelung (Fig. 4-2) greift, Ladestrom wird gedrosselt.

Mit Zone direkt am Pad: ΔT ≈ 54 K → 79 / 94 °C
```

Kein Schaden — der MCP73831 regelt bei ~120 °C herunter und schaltet bei 150 °C ab. Die
Folge ist eine gedrosselte, verlängerte Ladung.

**Abhilfe kostenlos:** die VBAT-Zone (gleiches Netz!) direkt um Pad 3 legen und 4–6
Wärmevias innerhalb von 2 mm zur unteren Massefläche setzen.

---

### M-3 — Crowbar und PTC sind thermisch nicht koordiniert; die Klemmung verletzt Abs.-Max.

*Quelle: MCP73831 Abs. Max. · AP2112 Abs. Max. · MF-PSMF050X S. 3*

Die Polung von D3 ist **richtig**: KiCad `D_Schottky` Pin 1 = K, Pin 2 = A; Kathode an
VBAT, Anode an GND. Bei verpolter Zelle wird die Diode leitend. Zwei Probleme bleiben.

```
Nachweis — Zeitkonstanten-Fehlanpassung

I_Crowbar ≈ 5,1 … 10,3 A (siehe K-4)
P_D3 = 5,1 A · 0,6 V ≈ 3,1 W
PTC: „max. time to trip 0,1 s bei 8,0 A" → t ≈ 60…150 ms
SOD-123 Z_θJA(100 ms) ≈ 60…90 K/W
  ΔT ≈ 3,1 W · 75 K/W ≈ 230 K → T_J ≈ 255 °C ≫ 150 °C

Die Diode (τ_th ≈ 10…50 ms) heizt schneller als die PTC (τ_th ≈ 0,1…1 s)
auslöst. D3 ist ein Einwegbauteil — was für einen Crowbar akzeptabel ist
(Kurzschluss ist das gewünschte Versagen), aber dokumentiert werden muss.
```

```
Nachweis — Restspannung gegen Absolute Maximum Ratings

V_F(B5819W) bei 5 A ≈ 0,65…0,75 V ⇒ VBAT klemmt auf ≈ −0,7 V
MCP73831: „All Inputs and Outputs w.r.t. V_SS … −0,3 V"  → verletzt
AP2112 V_IN über SW1 ebenfalls auf −0,7 V → Substratdiode leitet

Ein Schottky-Crowbar kann diese Grenze prinzipiell nicht einhalten.
```

**Abhilfe (löst zugleich M-1 und die Hälfte von M-4).** D3 und die Rolle von F1 im
Entladepfad durch einen **P-Kanal-MOSFET als ideale Diode** ersetzen, z. B. `DMG2301L`
(SOT-23, −20 V, −2,3 A, R_DS(on) ≈ 55 mΩ bei V_GS = −2,5 V): echtes Sperren statt Klemmen,
19 mV statt 311 mV Spannungsfall bei 345 mA, Leckstrom im nA-Bereich statt zweistelliger µA.

---

### M-4 — Tiefschlaf: 80 µA nachweisbar, zwei Posten unbestimmt

*Quelle: AP2112 S. 8 · ESP32-C3 Tab. 6-6 · MCP73831 S. 4 · Ziel ≤ 200 µA*

| Beitrag | Typ | Max | Quelle |
|---|---:|---:|---|
| ESP32-C3 Deep-Sleep (RTC-Timer + RTC-Speicher) | 5 µA | n. s. | Tab. 6-6 |
| **AP2112K-3.3 Ruhestrom I_Q** | 55 µA | 80 µA | DC-Kennwerte |
| AP2112K EN, interner 3-MΩ-Pull-down an 3,7 V | 1,2 µA | 1,2 µA | R_PD |
| MCP73831 I_DISCHARGE, V_DD < V_STOP | 0,15 µA | 2 µA | S. 4 |
| MLCC-Isolationswiderstand, 9 Positionen | < 1 µA | ~2 µA | 1000 Ω·F |
| **D3 Sperrstrom bei 4,2 V** | *unbekannt* | *unbekannt* | Datenblatt fehlt (K-4) |
| **SSD1306-Modul, dauerhaft an +3V3** | *unbekannt* | *unbekannt* | kein Lastschalter |
| **Summe der belegbaren Posten** | **61 µA** | **85 µA** | — |

```
Nachweis — warum D3 der kritische Posten ist

Schottky-Sperrstrom verdoppelt sich je ~10 K.
Angenommen 15 µA @ 25 °C ⇒ bei 60 °C: 15 · 2^3,5 ≈ 170 µA
⇒ ein einzelnes Bauteil kann das gesamte 200-µA-Budget aufzehren.

P-MOSFET-Variante (M-3): I_DSS < 1 µA über den ganzen Bereich.
```

**Zwei konkrete Hebel.**

1. LDO tauschen: der AP2112K ist mit 55…80 µA allein für **28…40 %** des Budgets
   verantwortlich. Ein RT9080-33GJ5 (600 mA, I_Q ≈ 20 µA, Dropout 200 mV @ 600 mA) nutzt
   dieselbe SOT-23-5-Standardbelegung IN/GND/EN/NC/OUT — vor der Bestellung gegen das
   Datenblatt gegenprüfen.
2. +3V3 zum Display über einen P-FET-Lastschalter aus einem freien GPIO schaltbar machen;
   IO10 ist unbeschaltet.

---

### M-5 — SW1: formal 3,5-fach überlastet, physikalisch weitgehend entschärft

*Quelle: C&K OS Series S. I-37 · ESP32-C3 Tab. 6-2*

```
Nachweis — Tragstrom
R_Kontakt ≤ 20 mΩ (Datenblatt, Materials/Specifications)
P = I²R = 0,345² · 0,020 = 2,4 mW → thermisch belanglos

Nachweis — Einschalten (Kapazitätsstoß)
Der LDO begrenzt seinen Ausgang selbst (Foldback 50 mA bei V_OUT = 0).
Über den Kontakt fließt nur die Ladung von C5:
  E = ½·C·V² = ½ · 0,85 µF · 3,9² = 6,5 µJ
→ drei Größenordnungen unter der Verschweißenergie.

Nachweis — Ausschalten (Lichtbogen)
E_Bogen = ½·L·I² ≈ ½ · 400 nH · 0,345² = 24 nJ
Mindestbogenspannung Silber ≈ 12 V, Betriebsspannung 3,7…4,2 V
→ ein stehender Lichtbogen ist bei dieser Spannung physikalisch nicht möglich.
Die Angabe „0,1 A @ 12 VDC" ist genau durch dieses Bogenkriterium gesetzt.
```

Bleibt: die Nennwerte werden überschritten, der Hersteller steht dafür nicht ein, und die
10 000 Zyklen Lebensdauer gelten für Nennlast. Espressif fordert außerdem in Tab. 6-2
ausdrücklich eine Quelle mit **I_VDD ≥ 0,5 A** — ein 0,1-A-Kontakt im Versorgungspfad ist
für eine Abschlussarbeit nur mit dieser Rechnung verteidigbar.

**Eleganteste Abhilfe, null Zusatzbauteile:** SW1 nicht mehr die Leistung schalten lassen,
sondern den **EN-Pin des LDO**. Der Kontakt trägt dann nur noch den
3-MΩ-Pull-down-Strom, das Rating wird um Größenordnungen unterschritten, und der
Ruhestrom steigt um höchstens I_STD = 1,0 µA (max).

---

### M-6 — Laden unter Last terminiert nie

*Quelle: MCP73831 § 4.7 · Siebdruck y = 30,5 mm*

Der Entwurf erkennt das Problem und bedruckt die Platine mit *„Laden nur im
ausgeschalteten Zustand (kein Lastpfad)"*. Das ist ehrliche Ingenieurspraxis. Es bleibt
eine prozedurale Maßnahme gegen eine elektrische Eigenschaft.

```
Nachweis

Abschaltkriterium: I_TERM = 7,5 % · I_REG = 11 mA
Systemlast im Spielbetrieb ≈ 50 mA > 11 mA
⇒ Abschaltbedingung wird nie erreicht

Folgen: STAT-LED bleibt dauerhaft an · Zelle liegt unbegrenzt auf 4,20 V
Float (Kalenderalterung ~2× je 0,1 V über 4,0 V).
Bei 345 mA Last > 147 mA Ladestrom entlädt sich die Zelle, während
„geladen" angezeigt wird.

Ein Sicherheitstimer existiert im MCP73831/2 nicht.
```

Zwei Randbefunde zur Zelle: es gibt **keine Tiefentladeschutzschwelle** — im Tiefschlaf
ist die Last so klein, dass der LDO nie in Dropout geht und die Zelle bis unter 3,0 V
entleert wird — und **keine Akkuspannungsmessung**. IO2 ist ADC1_CH2, trägt nur den
Strapping-Pull-up und wäre über einen Teiler frei für eine Ladestandsanzeige. Ob die
eingesetzte 500-mAh-Zelle eine integrierte Schutzelektronik hat, sagt die Stückliste
nicht — für eine Li-Polymer-Baugruppe ist das die wichtigste fehlende Angabe.

---

### M-7 — 35 Rückstrompfad-Unterbrechungen, davon 24 unter schnellen Signalen

*Quelle: gemessen aus `.kicad_pcb`*

Die untere Lage ist zu 91 % durchgehende Masse — sehr gut. Die 27 Signalsegmente, die
trotzdem dort liegen, schneiden aber Schlitze hinein, und jede darüber laufende Bahn auf
F.Cu zwingt ihren Rückstrom zu einem Umweg.

```
Nachweis — der dominierende Schlitz

+3V3_MCU auf B.Cu:
  (58,80 / 52,80) → (58,80 / 42,00) = 10,80 mm
  (58,80 / 44,60) → (68,20 / 44,60) =  9,40 mm
Aussparung inkl. 0,3 mm Freistellung: 1,1 mm × ≈ 20 mm

Darüber kreuzen: SCLK (2×) · MOSI_MCU · OLED_CS · OLED_CS_MCU
  OLED_DC_MCU · OLED_RES · USB_DM · USB_DP · BUZZ
Zweiter Schlitz (EN, 7,2 mm) kreuzt weitere fünf SPI-Leitungen.

L_Umweg ≈ 0,2·ℓ·[ln(2ℓ/(w+h)) − 0,75]
        ≈ 0,2·10·[ln(20/2,6) − 0,75] ≈ 2,6 nH

Gemeinsame Rückimpedanz ⇒ Übersprechen:
  dI/dt = 32 mA / 5,7 ns = 5,6·10⁶ A/s
  U = 2,6 nH · 5,6·10⁶ = 15 mV je Aggressor, 4 gleichzeitig ≈ 58 mV
  gegen Störabstand V_IL = 0,825 V → 7 % — tolerabel
  ohne R5…R9 wären es ≈ 170 mV.
```

Funktional unkritisch bei diesen Flanken, aber vermeidbare Entwurfsschuld.

**Nebenbefund:** USB_DM wechselt für 2,00 mm auf B.Cu und hat zwei Vias, USB_DP keines —
die beiden Hälften des Paares sind asymmetrisch, und USB_DP kreuzt den Schlitz von
USB_DM. Bei 12 Mbit/s Full-Speed ohne Folgen, aber es ist die Art Asymmetrie, die man in
einem Review anspricht.

**Abhilfe:** +3V3_MCU auf F.Cu verlegen und B.Cu als reine Masse halten.

---

### M-8 — Eine Masseleitung für fünf Signale; ESD-Array hinter der Verkabelung

*Quelle: USBLC6-2 DS4260 S. 2 · IEC 61000-4-2*

```
Nachweis — Schleifenfläche und Abstrahlung

J3: 1 GND · 2 VCC · 3 SCLK · 4 MOSI · 5 RES · 6 DC · 7 CS
CS (Pin 7) ist 6 · 2,5 mm = 15 mm vom einzigen Rückleiter entfernt.
Bei 20 cm Kabellänge: A = 200 · 15 = 3000 mm² = 30 cm²

E ≈ 1,32 · f² · A · I / r   [µV/m @ 3 m]
bei 50 MHz, I ≈ 1 mA: 1,32 · 2500 · 30 · 0,001 / 3 = 33 µV/m ≈ 30 dBµV/m
EN 55032 Klasse B @ 3 m ≈ 50 dBµV/m → 20 dB Reserve

Zum Vergleich: Umwegschleife eines Layout-Schlitzes ≈ 0,3 cm²
→ das Kabel strahlt rund 40 dB stärker als jede Platinenstelle.
```

```
Nachweis — Wirksamkeit des ESD-Arrays

D1 sitzt auf der Platine, die USB-C-Buchse auf dem Breakout dahinter.
Verbindung: ~5…10 cm ungeschirmter Draht ≈ 50…100 nH
IEC 61000-4-2, 8 kV Kontakt: di/dt ≈ 30 A/ns
U = L · di/dt = 75 nH · 3·10¹⁰ A/s ≈ 2250 V
→ die Entladung liegt auf der Verkabelung an, BEVOR D1 klemmen kann.

Zusatz: D1 Pad 2 (GND) → nächstes Massevia 1,65 mm
≈ 2 nH ⇒ 60 V Masseversatz beim Schlag. Via direkt ans Pad setzen.
```

**Abhilfe.** J3 auf 8 oder 9 Pole erweitern und eine zweite Masse neben SCLK legen
(halbiert die Schleifenfläche und liefert einen Rückleiter für die schnellste Leitung).
USB-C-Buchse auf die Platine holen, dann sitzt D1 an der richtigen Stelle. J4 und J3
zusätzlich mit einem TVS bestücken — R11/R12 sind reine Strombegrenzung; ein CRCW0805 hat
nur **150 V** Grenzspannung und überschlägt bei einem 8-kV-Ereignis.

---

### M-9 — Die Betriebs-LED liefert 0,34 mcd

*Quelle: APT2012SGC S. 1/2 · APT2012EC S. 1/2*

Beide LEDs sind elektrisch und thermisch unbedenklich, aber optisch weit
unterdimensioniert. Die APT2012SGC ist eine **GaP**-Grüne — die schwächste verfügbare
Grüntechnologie mit 5 mcd Minimum bei 20 mA.

```
Nachweis

D4 grün (IO0 → R14 1 kΩ → LED → GND), V_F ≈ 1,95 V bei kleinem Strom
  I   = (3,3 − 0,035 − 1,95) / 1000 = 1,32 mA
  I_v ≈ 5 mcd · 1,32/20 = 0,33 mcd (min-Bin), typ. 0,79 mcd

D2 rot (VBUS → R2 1 kΩ → LED → STAT), V_OL = 0,4 V typ / 1 V max
  I   = (5,0 − 1,8 − 0,4) / 1000 = 2,8 mA (worst case 2,2 mA)
  I_v ≈ 8 mcd · 2,8/20 = 1,1 mcd
  I_SINK,max = 25 mA → Reserve reichlich

Sperrspannung geprüft: V_R,max = 5 V für beide LEDs.
MCP73831 Tri-State treibt STAT bei „complete" auf V_DD−0,4 V ≈ 4,6 V,
Anode liegt dann stromlos auf 5,0 V ⇒ 0,4 V in Durchlassrichtung,
keine Sperrbelastung.
Bei MCP73832 (Open-Drain) floatet STAT ⇒ ebenfalls unkritisch.
Die Abschaltung funktioniert also für BEIDE Varianten.
```

**Abhilfe.** R2 → 560 Ω (≈ 4,9 mA) und R14 → 330 Ω (≈ 4,1 mA), oder D4 gegen eine
InGaN-Grüne tauschen. Bei 4,1 mA Dauerbetrieb kostet D4 rechnerisch
500 mAh / 4,3 mA ≈ 116 h reine LED-Laufzeit — vertretbar, und da D4 GPIO-gesteuert ist,
kann die Firmware sie per PWM dimmen.

---

### M-10 — Der Piezo braucht eine Klemmung; die Kapazität ist 4-mal größer als angenommen

*Quelle: CEP-1114 S. 1 · ESP32-C3 Tab. 6-1/6-3*

Zuerst die Richtigstellung einer Zahl aus der Aufgabenstellung: **die 28 mA sind kein
Absolute Maximum Rating.** Tab. 6-1 des Modul-Datenblatts enthält nur V_DD33 und T_STORE.
Die 28 mA sind der *typische* Senkstrom bei V_OL = 0,495 V und PAD_DRIVER = 3 — eine
Treiberkennlinie, keine Grenze. Die tatsächliche Grenze ist eine **Spannungsgrenze**:
−0,3 V … V_DD + 0,3 V.

```
Nachweis — Ansteuerung

C_Piezo = 31,5 / 45 / 58,5 nF (min/typ/max, Datenblatt S. 1)
I_Spitze = 3,3 V / 220 Ω = 15,0 mA → 54 % von I_OL · unkritisch
τ = 220 Ω · 45 nF = 9,9 µs → t_r = 2,2τ = 21,8 µs
bei 2 kHz (Nennfrequenz): 8,7 % der Halbperiode  ok
obere Nutzgrenze ≈ 8…10 kHz
P(R13) = 2·f·½CV² = 0,98 mW ≪ 125 mW  ok

Schalldruck: 93 dB gilt bei 10 V_pp. Hier 3,3 V_pp:
  93 + 20·log(3,3/10) ≈ 83 dB @ 10 cm — laut genug.
```

```
Nachweis — piezoelektrischer Rückschlag

Erschütterung erzeugt Ladung auf 45 nF. Bei 20 V Generatorspannung:
  I_Klemm = (20 − 3,9) / 220 Ω = 73 mA in die interne ESD-Diode
  Dauer ≈ τ = 10 µs, Ladung ≈ 720 nC
Das Modul-Datenblatt gibt KEINEN Klemmstrom an —
der Betriebsfall liegt außerhalb jeder Spezifikation.

R13 vergrößern hilft nicht: 1 kΩ ⇒ τ = 45 µs ⇒ 40 % der Halbperiode
bei 2 kHz — der Ton bricht ein.
```

**Abhilfe.** Eine `BAT54S` (Doppel-Schottky, SOT-23) von BUZZ_P nach GND und nach
+3V3_MCU. Ein Bauteil, ~2 pF, klemmt beidseitig auf V_DD + 0,3 V.

**Kostenlose Verbesserung obendrein:** den Piezo mit einem zweiten GPIO gegenphasig
treiben (IO10 ist frei) — 6,6 V_pp statt 3,3 V_pp, also **+6 dB**, für einen zusätzlichen
220-Ω-Widerstand.

---

### M-11 — Stückliste nicht bestellbar; „0 DRC-Verstöße" ist ein gefiltertes Ergebnis

*Quelle: `ausgabe/stueckliste.csv` · `flappy-esp32c3.kicad_pro`*

Keine einzige Position trägt eine Herstellerbestellnummer. Bei Kondensatoren fehlen
Spannungsfestigkeit und Dielektrikum (K-3), bei Widerständen die Toleranz, bei den LEDs,
der PTC und dem Schalter jede Typbezeichnung. `MCP73831-2-OT` ist unvollständig — der
Optionscode legt Vorkonditionierung und Abschaltschwelle fest (z. B. `MCP73831T-2ACI/OT`)
und geht direkt in die P_D-Rechnung aus M-2 ein.

```
Nachweis — DRC-Konfiguration

drc.rpt: „Report includes: Errors" — Warnungen nicht enthalten
7 Regeln auf ignore, 22 Regeln auf warning, darunter:
  isolated_copper · copper_sliver · silk_over_copper · track_dangling

Tatsächlich vorhanden, aber nicht berichtet:
  • 1 verwaiste Kupferinsel, 5,5 mm² bei (7,0…10,4 / 53,8…56,2) mm
    auf Netz GND, ohne Pad oder Via — Ursache: island_removal_mode 0
  • 6 Courtyard-Überlappungen (C9, C11, R4, R5, R7, R9 gegen U1)

min_clearance: 0.0 · min_connection: 0.0
→ kein absoluter Fertigungsboden, nur die Netzklasse (0,2 mm) greift.
```

Beides ist harmlos in der Wirkung — die Insel ist mit 3,4 × 2,4 mm viel zu klein, um bei
2,4 GHz zu resonieren, und die Courtyard-Überlappungen entstehen nur, weil der eigene
Modul-Footprint seine Antennensperrfläche in den Courtyard zeichnet. Aber die Aussage
„0 DRC-Verstöße" trägt in dieser Form nicht.

---

## 5 Bestätigte Stärken

Jeder Punkt wurde nachgemessen, nicht übernommen. Mehrere davon sind besser, als die
Projektdokumentation selbst behauptet.

**S-1 Antennensperrfläche kompromisslos umgesetzt.**
Punkt-in-Polygon-Test über ein 0,5 × 0,25 mm Raster: **0 von 1265** Punkten innerhalb der
Sperrfläche tragen Kupfer — auf beiden Lagen, einschließlich beider Masseflächen und der
VBAT-Zone. Der Modulkörper endet bei y = 60,00 mm exakt bündig mit dem Platinenrand, es
liegt kein FR4 unter der Antenne. Sperrfläche 28,5 × 6,25 mm gegen gefordert 5,1 mm.

**S-2 Zweilagige Masse auf Vierlagen-Niveau.**
Die untere Lage ist **eine einzige zusammenhängende** gefüllte Fläche mit 4894 mm² = 91 %
der Platinenfläche und 120 Ankerpunkten. Nur 77 mm Signal liegen unten gegen 782 mm oben —
ein Verhältnis von 1:10. 84 Massenähvias. Das ist die Entwurfsentscheidung, die den
restlichen SI-Befunden ihre Schärfe nimmt.

**S-3 Strapping korrekt — und robuster als angenommen.**
Tab. 4-1 zeigt GPIO2 und GPIO8 als **floating ohne interne Pull-ups**; die externen 10 kΩ
sind also zwingend, und Espressif empfiehlt den Pull-up an GPIO2 wörtlich „due to
glitches". Entscheidend für die Display-Frage: Tab. 4-3 gibt für SPI-Boot
**GPIO8 = „Any value"** an. Eine Belastung von IO8 durch das Display verhindert also
**nicht** den Normalstart — sie verhindert nur den **Download-Modus** (dort ist
GPIO8 = 1 gefordert). Das Fehlerbild wäre „lässt sich nicht flashen", nicht „bootet
nicht". R16 hält IO8/CS zudem auch bei gezogenem Displaykabel auf High.

**S-4 Reset-RC: 28-fache Reserve gegen die Spezifikation.**
Espressif *empfiehlt* in der Peripherieschaltung 10 kΩ + 1 µF, spezifiziert aber in
Tab. 4-6 hart **t_STBL ≥ 50 µs**. Gerechnet: t = τ·ln(4) = 10 kΩ · 100 nF · 1,386 =
**1,39 ms**. Auch bei linear ansteigender Versorgung (ratiometrischer Fall) ergibt
0,25x ≥ 1−e^(−x) ⇒ x ≈ 3,92τ ≈ 3,9 ms. Die Abweichung von der Empfehlung ist damit
belegbar unkritisch, und t_H ≥ 3 ms für die Strapping-Pins ist durch R15/R16 ohnehin
erfüllt.

**S-5 R5…R9 = 68 Ω sind richtig — aus dem anderen Grund.**
Die Leitung ist **elektrisch kurz**: t_Flug(20 cm Flachband) ≈ 1,1 ns gegen t_r ≈ 5,7 ns.
Impedanzanpassung ist damit gar nicht der wirksame Mechanismus. Der reale Nutzen ist
Flankenbegrenzung: f_knee sinkt von 250 MHz auf 88 MHz, das Übersprechen über die
gemeinsame Rückimpedanz von 170 mV auf 58 mV. Die Summe R_drv + 68 Ω ≈ 103 Ω trifft Z_0
des Kabels zusätzlich gut.

**S-6 10 MHz SPI halten mit Reserve.**
SSD1306 Tab. 13-4: t_cycle,min = 100 ns, t_DSW = 15 ns, t_R/F,max = 40 ns. Bei 25 pF
Kabel- und Eingangslast und R_ges = 103 Ω ergibt sich t_r = 2,2·R·C = 5,7 ns — 7-fache
Reserve gegen die Flankengrenze, Setup-Reserve 35 ns. Der Betrieb genau am Katalogmaximum
ist hier ausnahmsweise vertretbar; bei Kabeln über 30 cm auf 4…8 MHz zurückgehen.

**S-7 USBLC6 durchgehend richtig verdrahtet.**
Pins 1/6 sind intern I/O1, Pins 3/4 sind I/O2 — im SOT-23-6 liegen sie einander direkt
gegenüber. D− läuft über 1 → 6, D+ über 3 → 4: geradlinig durch das Gehäuse, GND und VBUS
mittig. Genau die vorgesehene Durchgangstopologie. C_I/O = 3,5 pF max, I_RM = 150 nA max.
Laufzeitversatz D+/D− = 33 ps ≪ 100 ps (USB-Grenzwert).

**S-8 Handlöt-Footprint mit echter Sorgfalt.**
Die 18 Randpads sind auf 2,5 mm verlängert — exakt 1 mm nach außen, Innenkante unverändert
bei 9,25 mm. Der EPAD ist als 13 Durchkontaktierungen (0,7 mm Pad / 0,3 mm Bohrung) auf
allen Kupferlagen ausgeführt, wie in Espressif Fig. 11-1 gezeigt. Dass er bei
Handbestückung unlötbar bleibt, ist unschädlich: das Datenblatt sagt ausdrücklich
„not a must".

**S-9 Steckerbelegung von J3 durchdacht.**
Reihenfolge GND · VCC · SCLK · MOSI · RES · DC · CS. Die beiden ruhigen Leiter liegen
damit unmittelbar neben dem schnellsten Signal, und VCC wirkt über C6/C7 und die
Modulabblockung als AC-Rückleiter für SCLK. Bei nur einer echten Masseleitung ist das die
bestmögliche Anordnung.

**S-10 Ladeauslegung und Betriebs-LED.**
I_chg = 1000/6,8k = 147 mA = **0,29 C**, mit ±10 % IC-Toleranz 132…162 mA — konservativ
gegen die 1-C-Empfehlung, gut für die Zellalterung. Und die Betriebs-LED hängt an IO0
statt fest an der Schiene: sie ist per Firmware abschaltbar und belastet den Tiefschlaf
nicht. Kleine Entscheidung, oft falsch gemacht.

---

## 6 Geprüft und entkräftet

Sieben Verdachtspunkte aus der Aufgabenstellung, die sich nach Nachrechnung als
unbegründet erwiesen haben. Sie gehören ins Protokoll, weil ihre Abwesenheit selbst ein
Ergebnis ist.

| Verdacht | Nachrechnung | Ergebnis |
|---|---|---|
| C6 = 22 µF überkompensiert den LDO / ESR zu niedrig | AP2112: „Stable with 1.0 µF Flexible Cap: Ceramic, Tantalum and Aluminum Electrolytic" — keine Obergrenze, keine ESR-Bedingung. 22 µF/6,3 V bei 3,3 V ≈ 8,8 µF wirksam. | unbegründet |
| Foldback-Strombegrenzung verhindert den Anlauf | Datenblatt S. 11 nennt den Fall explizit: „a current load … *before* the part is enabled". Hier ist EN fest an V_IN, der LDO wird zeitgleich mit V_IN freigegeben. Fall tritt nicht ein. | unbegründet |
| C10 = 100 nF zu klein für den Reset | 1,39 ms gegen t_STBL,min = 50 µs (siehe S-4). | unbegründet |
| Lade-LED schaltet bei MCP73832 nicht ab | Bei Tri-State treibt STAT auf V_DD−0,4 V (0,4 V Restspannung über der LED), bei Open-Drain floatet der Pin. Beide Varianten dunkel, keine Sperrbelastung gegen V_R,max = 5 V. | unbegründet |
| SW1-Kontakt durch Einschaltstromstoß gefährdet | 6,5 µJ Ladeenergie (C5), 24 nJ Bogenenergie, und bei 3,9 V ist unterhalb der Silber-Mindestbogenspannung von ~12 V kein stehender Bogen möglich. | unbegründet |
| D3 falsch gepolt (Kathode/Anode vertauscht) | KiCad `D_Schottky`: Pin 1 = K, Pin 2 = A. Netzliste legt Pin 1 auf VBAT, Pin 2 auf GND ⇒ im Normalbetrieb gesperrt, bei Verpolung leitend. Crowbar korrekt. Dieselbe Konvention macht D2 und D4 ebenfalls richtig herum. | korrekt |
| C8/C9 zu weit vom Modul entfernt | Schleifeninduktivität ≈ 4,0 nH ⇒ ΔU = L·dI/dt = 4,0 nH · 3·10⁷ A/s = **120 mV**; Schiene fällt auf 3,18 V gegen V_DD33,min = 3,0 V. C9 hat sein Massevia in 0,26 mm Abstand, der EPAD ist mit 13 Durchkontaktierungen angebunden, und das Modul bringt eigene Abblockung mit. C8 bei 10,75 mm ist als Bulk-Kondensator distanzunkritisch. | ausreichend |

---

## 7 Konkrete Optimierungsvorschläge

### 7.1 Bauteiltausch

| Pos. | Bisher | Vorschlag | Wirkung | Löst |
|---|---|---|---|---|
| D3 + F1 | B5819W + PTC im Entladepfad | **DMG2301L** P-Kanal-MOSFET als ideale Diode (SOT-23, −20 V, −2,3 A, 55 mΩ) | Echtes Sperren statt Klemmen auf −0,7 V · 19 mV statt 311 mV Spannungsfall · Leckstrom nA statt zweistellig µA | M-1 M-3 M-4 |
| LS1 | Footprint Ø12/RM 7,6 | Footprint auf **Ø30 / RM 20** ändern, Wandler über 2-pol. JST-XH absetzen | Baugruppe wird überhaupt erst bestückbar; Platine bleibt unverändert | **K-1** |
| R17 R18 | 5k1 bestückt | **DNP** + Siebdruckhinweis an J1, oder USB-C-Buchse auf die Platine | Beseitigt die CC-Totzone bei Default-USB-Quellen | **K-2** |
| C3 | 4u7 (ohne Angabe) | **10 µF / 25 V X7R 0805** | 6,2 µF wirksam bei 4,2 V ⇒ CV-Schleife auch ohne Akku kompensiert | **K-3** |
| C6 | 22u (nur 6,3 V X5R lieferbar) | **10 µF / 16 V X7R 0805** | Gleiche wirksame Kapazität bei doppelter Spannungsreserve und kleinerer Temperaturdrift | K-3 |
| C5 · C8 | 1u · 10u | **2,2 µF / 16 V X7R** · **10 µF / 16 V X7R** | Derateter Wert bleibt über der Herstellervorgabe | K-3 |
| U3 | AP2112K-3.3 (I_Q 55…80 µA) | **RT9080-33GJ5** (600 mA, I_Q ≈ 20 µA) — SOT-23-5 Standardbelegung, vor Bestellung prüfen | −35…60 µA Tiefschlaf, 50 mV weniger Dropout | M-4 |
| LS1-Pfad | R13 220 Ω, einseitig | **BAT54S** nach GND/+3V3_MCU · zweiter Treiber-GPIO (IO10) + 220 Ω | Klemmung des piezoelektrischen Rückschlags · +6 dB Schalldruck | M-10 |
| D4 · R14 · R2 | GaP-Grün, 1 kΩ · 1 kΩ | InGaN-Grün oder R14 = 330 Ω · R2 = 560 Ω | 0,33 → ~1,5 mcd bzw. 1,1 → ~2 mcd | M-9 |
| J3 · J4 | nur R-Begrenzung | TVS (z. B. **PESD3V3L1BA**) an beiden Kabelabgängen | CRCW0805 hält nur 150 V; ESD-Pfad hat bisher keine Klemmung | M-8 |

### 7.2 Schaltung und Layout — ohne zusätzliche Bauteile

| Maßnahme | Begründung | Löst |
|---|---|---|
| **SW1 schaltet EN statt Leistung.** Kontakt vom VBAT-Pfad an den EN-Pin des LDO legen, VBAT fest auf V_IN, Pull-down nach GND. | Kontaktstrom sinkt von 345 mA auf < 2 µA — das 0,1-A-Rating wird um Größenordnungen unterschritten. Ruhestrom steigt um höchstens I_STD = 1,0 µA. | M-5 |
| **VBAT-Kühlzone direkt um U2 Pad 3 ziehen** (gleiches Netz) und 4–6 Wärmevias innerhalb 2 mm setzen. | R_th der Anbindung fällt von ≈ 1720 K/W auf nahe null; T_J sinkt von 123 °C auf ≈ 94 °C bei 40 °C Umgebung. | M-2 |
| **OLED_CS von IO8 auf IO10 verlegen.** IO10 ist unbeschaltet, R16 bleibt als reiner Strapping-Pull-up ohne externe Last. | Der Download-Modus wird unabhängig davon, was am Displaykabel hängt. Beseitigt die einzige verbleibende Strapping-Abhängigkeit. | S-3 |
| **+3V3_MCU von B.Cu nach F.Cu verlegen.** | Entfernt den 1,1 × 20 mm Schlitz, über den neun schnelle Leitungen laufen. Danach bleibt B.Cu reine Masse. | M-7 |
| **J3 auf 8 oder 9 Pole erweitern**, zweite Masse neben SCLK. | Halbiert die Schleifenfläche des Kabels von 30 cm² — die mit Abstand größte Störquelle der Baugruppe. | M-8 |
| **Massevia unmittelbar an D1 Pad 2** (heute 1,65 mm). | ≈ 2 nH ⇒ 60 V Masseversatz bei 8 kV Kontaktentladung. Das Via gehört ins Pad. | M-8 |
| **USB-C-Buchse auf die Platine, J1 und Breakout streichen.** | Löst K-2 strukturell, bringt D1 vor die Verkabelung statt dahinter und entfernt eine ungeschirmte Strecke aus dem USB-Pfad. | K-2 M-8 |
| **Akkuspannungsteiler auf IO2** (ADC1_CH2, trägt bisher nur den Strapping-Pull-up). | Ermöglicht Ladestandsanzeige und Tiefentladeabschaltung in Firmware — beides fehlt heute vollständig. | M-6 |
| **`island_removal_mode` auf 1** und DRC-Report auf „Errors + Warnings" umstellen. | Entfernt die verwaiste Kupferinsel und macht die Aussage „0 DRC-Verstöße" belastbar. | M-11 |
| **Prüfstand um eine Datenblatt-Ebene erweitern:** je Bauteil Rastermaß, Gehäusemaß, Spannungsfestigkeit und Nennstrom in `design.py` hinterlegen und gegen den Footprint bzw. den Betriebsfall prüfen. | Genau die vier Showstopper dieses Berichts wären damit automatisch gefallen. Eine Mutation der Art „Bauteilmaß passt nicht zum Footprint" gehört in `tests_stufe3.py`. | **K-1 K-3 K-4** |

---

## 8 Prüfgrundlage

Geprüft gegen: ESP32-C3-WROOM-02 v1.7 · MCP73831/2 DS20001984G · AP2112 DS39724 Rev. 2-2 ·
USBLC6-2 DS4260 Rev. 6 · SSD1306 Rev. 1.1 · MF-PSMF Series Rev. P · C&K OS Series
11 Nov 20 · CEP-1114 09/11/2024 · APT2012EC V.13A · APT2012SGC V.18B · Vishay VJ
Commercial 08-May-2026 · Vishay CRCW e3 — sowie `gen/design.py`,
`flappy-esp32c3.kicad_pcb` (57 Footprints, 160 Pads, 387 Segmente, 119 Vias, 5 Zonen),
`ausgabe/stueckliste.csv` und `flappy-esp32c3.kicad_pro`.

Alle Geometrie- und Flächenangaben wurden aus der Platinendatei nachgemessen, nicht aus
der Projektdokumentation übernommen. Ein Datenblatt — `D3_B5819W_DiodesInc.pdf` —
beschreibt ein anderes Bauteil; die zugehörigen Aussagen sind entsprechend gekennzeichnet.

---

## 9 Bearbeitungsstand

Nachtrag zum Bericht. Alles Folgende ist im Repository umgesetzt, aus
`gen/design.py` neu erzeugt und mit `./erzeugen.sh` verifiziert
(ERC, DRC, Schaltplan/Layout-Abgleich, **1786 Prüfungen, 0 Fehler, 0 offene Belege**).

| Befund | Stand | Umsetzung |
|---|---|---|
| **K-1** | behoben | `LS1` entfällt als Platinenbauteil; der CEP-1114 sitzt wie Display und Taster am Kabel an der neuen Buchse **J5** (JST-XH 2-polig). Der handgesetzte Körpermaß-Eintrag in `chk_place.py`, der die Ursache war, ist gelöscht. |
| **K-2** | behoben | `R17/R18` ab Werk **DNP** (`design.DNP`), im Schaltplan als `(dnp yes)`, im Layout als Footprint-Attribut, in der Stückliste als „NICHT BESTÜCKEN", zusätzlich Siebdruckhinweis an J1. |
| **K-3** | behoben | Alle Kondensatoren tragen Spannungsklasse und Dielektrikum. C3 → 10 µF/25 V X7R, C5 → 2,2 µF/16 V X7R, C6 → 22 µF/10 V X5R, C8 → 10 µF/16 V X7R. T3 fordert die Angabe jetzt, T9j prüft ≥ 2 × Betriebsspannung. KEMET X7R 0805 Datenblatt hinterlegt. |
| **K-4** | **vollständig behoben** | Das echte Datenblatt der Schottky-Diode B5819W (SOD-123) wurde beschafft und in `hardware/doc/datenblaetter/D3_B5819W_SOD-123.pdf` abgelegt. KEMET X7R (0805 bis 22 µF) und Vishay CRCW0805 (1 %) sind ebenfalls erfasst. Prüfstufe **T12** verifiziert alle 16 Belege vollautomatisch mit **0 offenen Belegen**. |
| **M-2** | behoben | Kühlfläche zweiteilig, der schmale Teil überdeckt U2 Pad 3 und ist **vollflächig** angebunden (keine Wärmefalle). 113,7 mm² in 7,92 mm Entfernung → **177,8 mm², davon ein Stück direkt am Pad**. Zusätzlich 4 Wärmevias, nächste Massevias jetzt 1,65 / 2,14 / 2,60 mm statt 1,65 / 4,41 mm. |
| **M-7** | verbessert | Router auf `VIA_COST = 60`, `BACK_COST = 40` getrimmt (Messreihe über 18 Kombinationen, siehe Kommentar in `autoroute.py`). Signalkupfer auf der Masselage **77,0 → 58,3 mm**, davon schnelle Netze **41,1 → 25,8 mm**. Kreuzungen unverändert 35/24. |
| **M-9** | behoben | R2 1 k → **560 R** (2,8 → 5,4 mA), R14 1 k → **330 R** (1,3 → 3,9 mA). |
| **M-11** | teilweise | Die verwaiste Kupferinsel ist mit der neuen Verdrahtung verschwunden (`isolated_copper` 1 → 0). U2 trägt die vollständige Bestellbezeichnung `MCP73831T-2ACI/OT`. |

### Verworfener Ansatz

Der naheliegende M-7-Eingriff — `+3V3_MCU` hart auf die Vorderseite zwingen —
wurde gemessen und **verworfen**: das Netz verschwand zwar von der Masselage,
verdrängte dort aber SCLK und OLED_RES mit je 17 mm. Die Güte
(`L(B.Cu) + 2·L(B.Cu, schnell) + 3·Kreuzungen(schnell)`) verschlechterte sich von
241 auf 356. Ein Versorgungsnetz auf der Masselage ist harmloser als ein
schnelles Signal. Der wirksame Hebel war stattdessen `BACK_COST`, der lange
Ausflüge auf die Rückseite bestraft, bei gleichzeitig **billigerem** Via — also
„hinüber, einmal kreuzen, sofort zurück".

### Nicht angefasst

M-1 (PTC im Entladepfad), M-3 (Crowbar-Koordination), M-4 (Ruhestrom),
M-5 (Schalterrating), M-6 (Laden unter Last), M-8 (Kabelschleife, ESD),
M-10 (Piezo-Klemmung). Diese Befunde erfordern Bauteiländerungen mit neuen
Datenblättern (P-MOSFET, LDO-Tausch, TVS, BAT54S) und waren nicht Teil des
Auftrags. Die Empfehlungen aus Abschnitt 7 bleiben gültig.
