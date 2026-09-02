# Entwurfsentscheidungen und Abweichungen vom Projektplan

Ergänzt Abschnitt 4.3 des Projektplans um das, was beim Schaltplan- und
Layoutentwurf tatsächlich entschieden wurde. Jede Abweichung ist begründet.

## 1. Umgesetzt wie geplant

| Vorgabe | Umsetzung |
|---|---|
| 4.5.1 Modulpads 1 mm nach außen verlängert | eigener Footprint `flappy:ESP32-C3-WROOM-02_HandSolder`: Pads 1,5 → 2,5 mm, Mitte 0,5 mm nach außen. Pad ragt jetzt 1,5 mm statt 0,5 mm über die Modulkante |
| 4.5.2 keine Bauteile unter Funkmodul und USB-Breakout | im Layout gesperrt — dort liegen zusätzlich **auch keine Leiterbahnen** |
| 4.5.4 alle SMD auf einer Seite | 100 % der Bauteile auf der Oberseite; Rückseite trägt Massefläche und Beschriftung |
| 4.5.3 Freiraum zum Handlöten | als prüfbare Regel: ≥ 0,8 mm zwischen zwei Bauteilumrissen, ≥ 0,5 mm zum Rand. `gen/chk_place.py` bricht ab, wenn es enger wird. Kleinster Wert im Entwurf: 0,82 mm |
| 4.5.5 Prüfpunkte 1,5 mm | TP1 VBUS, TP2 VBAT, TP3 3V3, TP4 3V3_MCU, TP5 Tasterknoten, TP6 EN, TP7 BOOT, TP10–TP12 Masse (verteilt, für den kurzen Tastkopfanschluss) |
| 4.5.6 0-Ω-Trennstelle | R3 zwischen `+3V3` und `+3V3_MCU`; TP3 und TP4 liegen links und rechts davon, ein Shunt lässt sich direkt einlöten |
| 4.5.7 Antennenfreiraum | Modulkante bündig mit der Platinenunterkante; darüber eine Sperrfläche 28,5 × 6,25 mm ohne Kupfer auf **beiden** Lagen und ohne Bauteile |
| 4.5.8 Bestückungsdruck mit Werten | Referenzen auf dem Siebdruck, Werte auf `F.Fab`; `erzeugen.sh` legt daraus `ausgabe/bestueckungsplan.pdf` an, das beides zeigt |
| 5.2 ≥ 100 mm² Kupfer am Laderegler | eigene VBAT-Fläche, **122 mm²**, unmittelbar am VBAT-Pad von U2, schließt C3, C4 und TP2 ein |
| 5.4 Stützkondensatoren | C6 = 22 µF am Reglerausgang, C8 = 10 µF und C9 = 100 nF unmittelbar am Modulpin 1 |
| 5.5 Entprellung auf der Platine | R10 10 k, C11 100 n, R11 100 Ω, R12 220 Ω — alle nahe am Controller, nicht am Steckverbinder |
| 5.7 Serienterminierung | R5…R9 = 68 Ω, alle innerhalb von 10 mm ab dem Modulpin, vor der Kabelstrecke |

## 2. Bewusste Abweichungen

### 2.1 Display-Chipauswahl liegt auf IO8, nicht auf IO10

Der Projektplan skizziert IO10 als CS. Mit dem Modul in der gewählten Lage liegt
IO10 auf der **linken** Randkontaktreihe, das Display aber rechts — CS hätte um das
Modul herum geführt werden müssen und dabei die USB-Leitungen gekreuzt. IO8 liegt
auf der richtigen Seite und ist über R16 = 10 kΩ beim Start sicher hoch, was für
einen Strapping-Pin ohnehin nötig ist und für ein CS-Signal genau richtig ist.
IO10 bleibt am Randkontakt frei abgreifbar.

### 2.2 IO10, RXD und TXD bleiben unbeschaltet

Ursprünglich waren UART-Prüfpunkte vorgesehen. Der ESP32-C3 liefert Konsole **und**
JTAG über die USB-Serial-JTAG-Einheit; separate UART-Pads wären totes Kupfer und
hätten den ohnehin engen Kanal zwischen Modul und Display weiter belegt.

### 2.3 Piezo-Vorwiderstand 220 Ω statt 100 Ω

Der Projektplan nennt 100 Ω. Damit zieht der Piezo an jeder Flanke 33 mA; das
ESP32-C3-Datenblatt lässt aber nur **28 mA Senkstrom** je Anschluss zu.
220 Ω ergeben 15 mA und liegen damit auch unter der voreingestellten
Treiberstufe von 20 mA. Die Lautstärke ändert sich praktisch nicht — siehe
`pruefbericht.md`, Abschnitt 2.1.

### 2.4 Betriebs-LED wird vom GPIO getrieben

Im Blockschaltbild hängt die grüne LED an 3,3 V. Bei 1 kΩ zieht sie dauerhaft
etwa 1,3 mA — das **Sechsfache** des Tiefschlafziels NF-04 (≤ 200 µA). Sie hängt
deshalb an IO0 und wird von der Firmware abgeschaltet.

### 2.5 Verpolungsschutz als Crowbar statt Serienelement

Ein Serien-P-MOSFET schützt nicht gegen eine **vertauschte zweiadrige** Zelle, weil
mit der Zelle auch die Masse mitwandert. Gewählt: PTC-Rückstellsicherung F1
(500 mA) in Reihe und Schottky D3 (B5819W) als Crowbar. Bei verpolter Zelle leitet
D3 und F1 löst aus.
**Preis:** der Sperrstrom von D3 (typisch wenige µA bei 4,2 V) geht in das
Tiefschlafbudget ein. Er wird in M3 mitgemessen. Falls er dominiert, kann D3 gegen
eine 1N4148W getauscht werden — geringerer Sperrstrom, geringere Stoßstromfestigkeit,
was durch F1 und das Schutz-IC der Zelle abgedeckt ist.

### 2.6 Kurze Stücke auf der Rückseite

Die Rückseite trägt eine durchgehende Massefläche. 10,5 % der Leiterbahnlänge
(76 mm von 725 mm) liegen dennoch dort, weil einzelne Pads sonst nicht
erreichbar sind — vor allem die mittleren Anschlüsse der SOT-23-Gehäuse
(VBUS am ESD-Array, GND an Laderegler und Spannungsregler), die zwischen ihren
eigenen Nachbarpads eingeklemmt sind.

Für den Rückstrompfad zählt nicht die Summe, sondern wie lang die Massefläche
an einer Stelle aufgeschnitten ist. Das **längste Einzelstück ist 5,4 mm**
(Revision A: 10,8 mm).

**Maßnahme:** neben jedem Rückseitenstück sitzt ein Massevia, damit der
Rückstrom einen kurzen Weg findet. Insgesamt 54 Massevias von 87.

### 2.7 CC-Widerstände auf der Platine statt im Breakout

Die Platine bringt R17 und R18 (5,1 kΩ) an J1-5 und J1-6 selbst mit. Ohne
diese Rd-Widerstände liefert eine C-nach-C-Leitung kein VBUS — die Quelle
sieht dann keinen Verbraucher.

**Preis:** trägt das gekaufte Breakout die Widerstände schon, liegen zwei
5,1 kΩ parallel und ergeben 2,55 kΩ. Das ist kein zulässiger Rd-Wert mehr.
Deshalb sind R17/R18 **bedingt zu bestücken** — siehe Abschnitt 3.

Der umgekehrte Weg (sich auf das Breakout verlassen) wurde verworfen: das
Breakout ist ein Zukaufteil ohne verbindliches Datenblatt, die Platine soll
auch mit einem nackten Breakout funktionieren. Zwei 0805-Widerstände, die
im Zweifel unbestückt bleiben, sind das kleinere Risiko.

### 2.8 Freiraum um SOT-23: die 3 mm aus 4.5.3 sind nicht durchgehalten

Abschnitt 4.5.3 fordert 3 mm Freiraum um die SOT-23-Gehäuse. Der Entwurf hält
durchgehend die Hausregel von **0,8 mm Umrissabstand** ein, aber nicht überall
3 mm zum nächsten Bauteil: U2 hat zu C3 1,24 mm, U3 zu C5 1,24 mm,
D1 zu R17 1,75 mm, D3 zu J2 2,20 mm.

Das ist bewusst so. Der Umriss der Handlöt-Footprints liegt bereits 0,25 mm
außerhalb der Pads, und die begrenzenden Nachbarn sind flache 0805-Bauteile
mit 0,5 mm Bauhöhe. Die Anschlüsse der SOT-23 zeigen nach links und rechts
und sind mit einer 1,6-mm-Meißelspitze frei erreichbar. Die 3 mm hätten die
Platine wieder um mehrere Millimeter wachsen lassen, ohne dass die Lötspitze
mehr Platz bekommt, als sie braucht.

Wer mehr Abstand will, ändert `LOETABSTAND` in `gen/layout_pcb.py` und
verschiebt die betroffenen Bauteile; `chk_place.py` sagt dann, wo es klemmt.

## 3. Vor der Bestellung zu prüfen

1. **CC-Widerstände am USB-C-Breakout.** Nachmessen, ob zwischen CC1 bzw. CC2
   und GND schon 5,1 kΩ liegen. **Wenn ja: R17 und R18 nicht bestücken.**
   Zwei parallele 5,1 kΩ ergeben 2,55 kΩ; das liegt zwischen den Bereichen
   für Ra (Kabel) und Rd (Verbraucher), und die Quelle erkennt das Gerät
   möglicherweise gar nicht. Trägt das Breakout keine Widerstände: R17 und
   R18 bestücken, sonst liefert eine C-nach-C-Leitung kein VBUS.
2. **Pinbelegung des USB-C-Breakouts (J1).** Die Platine erwartet von oben nach
   unten **VBUS, GND, D−, D+, CC1, CC2** — so beschriftet auf dem Siebdruck.
   Diese Reihenfolge ist bei den gängigen 16P-Breakouts üblich, aber **nicht
   genormt**. Vor der Bestellung am gekauften Modul nachmessen. Weicht sie ab,
   in `gen/design.py` die Netze `VBUS`, `GND`, `USB_DM_CON`, `USB_DP_CON` auf die
   passenden J1-Pins umhängen und `./erzeugen.sh` neu laufen lassen.
3. **Aderfolge des OLED-Moduls (J3).** Erwartet: 1 GND, 2 VCC, 3 SCLK (D0),
   4 MOSI (D1), 5 RES, 6 DC, 7 CS — die im Projektplan 4.4.1 genannte Reihenfolge.
4. **Gehäuse.** Der Akku gehört auf den Gehäuseboden, die Platine auf vier
   Abstandsbolzen darüber — nicht daneben. Warum, steht in `pruefbericht.md`,
   Abschnitt 4. Empfohlenes Außenmaß mit der 72 × 51 mm großen Platine: etwa 80 × 59 × 26 mm.
5. **Schiebeschalter.** Der Footprint ist CK OS102011MS2Q (Raster 2 mm, zwei
   Befestigungslaschen 1,5 mm). Ein anderer Typ braucht einen anderen Footprint.
6. **Piezo.** Footprint `Buzzer_12x9.5RM7.6`, Anschlussabstand 7,6 mm.
