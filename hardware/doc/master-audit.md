# Master-Audit Flappy-C3

**Finale Prüfung vor Fertigungsfreigabe · Effekte 2. Ordnung, Grenzfälle, Fertigungsrisiken**

| | |
|---|---|
| Prüfgegenstand | Gesamtsystem Schaltung + Layout + Bauteile |
| Grundlage | 17 Datenblätter, `.kicad_pcb` (nachgemessen), `design.py` |
| Prüfstand beim Start | **1823 Prüfungen, 1 Fehler** |
| Prüfstand nach Neubau | 1786 Prüfungen, 0 Fehler |
| Datum | 2026-09-03 |

---

## 1 Executive Verdict

### ⛔ NO-GO — Korrekturen zwingend erforderlich

Der Entwurf ist elektrisch und im Layout **deutlich reifer** als beim ersten Bericht.
Die Freigabe scheitert an einem einzigen, aber harten Punkt: **drei von elf
Kondensatoren sind in der spezifizierten Kombination aus dem hinterlegten
Datenblatt in 0805 nicht lieferbar.** Das ist derselbe Defekt wie K-3 im ersten
Bericht — nur auf ein neues Datenblatt verschoben.

**Reifegrad: 7,5 / 10** (vorher 6/10)

| Dimension | Bewertung |
|---|---|
| Layout- und Massedisziplin | 9/10 |
| Werkzeug- und Prüfstandsqualität | 9/10 |
| Schaltungsauslegung | 7/10 |
| Transienten- und ESD-Robustheit | 5/10 |
| Beschaffungsdokumentation | **4/10** ← blockiert |

### Vorbemerkung: drei Abweichungen von der Auftragsbeschreibung

Ich habe den Repository-Stand geprüft statt der Zusammenfassung zu vertrauen.
Drei Punkte stimmten nicht:

1. **C1 ist `4u7 25V X7R`, nicht 10 µF.** Für die LC-Rechnung in Abschnitt 1
   entscheidend — ich rechne mit dem realen Wert.
2. **Der Prüfstand war nicht grün.** Beim Audit-Start: **1 Fehler**
   („alle Kupferzonen sind gefüllt → 0 von 4"). Die Platinendatei hatte **null
   gefüllte Zonen** — keine Massefläche.
3. **Die Fertigungsdaten waren älter als die Quelle.** `.kicad_pcb` und
   `routes.py` um 18:05:03, die Gerber um 18:03:17. Es liefen die
   Python-Generatoren ohne den anschließenden KiCad-Füll- und Exportschritt.

Punkt 2 und 3 sind behoben (`./erzeugen.sh` neu gefahren, 1786 Prüfungen,
0 Fehler). Sie sind aber ein **Freigabe-relevanter Prozessbefund**: der
Prüfstand hatte den Fehler gefunden, er wurde nur nicht gelesen.

---

## 2 Kritische Showstopper (P0)

### P0-1 — Drei Kondensatoren sind aus der hinterlegten Reihe nicht beschaffbar

*Quelle: `C_SMD-0805-MLCC-Kondensatoren_KEMET-X7R.pdf`, Tabelle 1A, Seite 5
(YAGEO/KEMET C1002_X7R, 2026-08-18) — Spalte **C0805C**, visuell ausgewertet*

Die Auswahltabelle listet je Kapazitätswert, in welchen Gehäusen und
Spannungsklassen er existiert. Für 0805 (Spaltengruppe C0805C, Spannungscodes
9=6,3 V · 8=10 V · 4=16 V · 3=25 V · 6=35 V · 5=50 V):

| Position | Spezifikation | Zeile in Tabelle 1A, Spalte C0805C | Urteil |
|---|---|---|---|
| C2,C4,C7,C9,C10,C11 | 100n 50V X7R | `DN DN DN DN DN DN DH` → bis 100 V | ✅ lieferbar |
| C5 | 2u2 16V X7R | `DH DH DH DH¹ DH¹ DH¹` → bis 50 V | ✅ lieferbar |
| C1 | 4u7 25V X7R | `DH DH DH DH` → bis 25 V | ✅ lieferbar |
| **C3** | **10u 25V X7R** | `DH¹ DH¹` → **nur 6,3 V und 10 V** | ❌ **existiert nicht** |
| **C8** | **10u 16V X7R** | `DH¹ DH¹` → **nur 6,3 V und 10 V** | ❌ **existiert nicht** |
| **C6** | **22u 10V X5R** | 22 µF in 0805 **gar nicht gelistet**; X5R ist zudem nicht Gegenstand dieses X7R-Dokuments | ❌ **doppelt ungedeckt** |

**Warum T12 das nicht findet.** Die von mir eingeführte Prüfstufe vergleicht den
*Inhalt der Datei* mit der *Kennung des Bauteils* — sie fängt ein falsch
abgelegtes Datenblatt. Sie prüft nicht, ob die konkrete Kombination aus Wert,
Spannungsklasse, Dielektrikum und Gehäuse in diesem Dokument überhaupt
vorkommt. Genau diese Ebene fehlt noch.

**Konsequenz.** Die Stückliste ist in dieser Form nicht bestellbar. Die Teile
sind zwar am Markt erhältlich (10 µF/16 V X7R 0805 und 22 µF/10 V X5R 0805 sind
gängig; 10 µF/25 V X7R 0805 ist selten, dick und teuer), aber **nicht aus der
Reihe, die als Nachweis hinterlegt ist**. Für eine Abschlussarbeit, die
Datenblattkonformität behauptet, ist das derselbe Bruch wie beim ersten Bericht.

**Abhilfe — zwei saubere Wege:**

- **A (empfohlen):** Werte auf das ändern, was die hinterlegte Reihe führt.
  C3 → `4u7 25V X7R`, C8 → `4u7 16V X7R`, C6 → `4u7 25V X7R` ×2 parallel oder
  Gehäuse auf 1206 wechseln (dort führt die Reihe 10 µF bis 25 V und 22 µF bis
  10 V). **Achtung:** C3 muss nach MCP73831 § 6.1.1.4 ≥ 4,7 µF *wirksam* bei
  4,2 V bleiben — mit 4u7/25V X7R sind das ca. 4,1 µF, also knapp darunter.
  Sauber ist hier **1206**.
- **B:** Die Datenblätter der tatsächlich beschafften Typen ablegen (X5R-Reihe
  für C6, passende X7R-Reihe für C3/C8) und `DATENBLATT` je Position
  differenzieren statt einer Sammelzeile.

**Zusätzlich:** T12 um eine Wertabdeckungsprüfung erweitern, sonst wiederholt
sich der Befund beim nächsten Bauteilwechsel ein drittes Mal.

### P0-2 — Prozess: Fertigungsdaten waren nicht aus dem geprüften Stand erzeugt

Behoben, aber festzuhalten: eine Freigabe darf nur auf einem Stand erfolgen, bei
dem `./erzeugen.sh` **in einem Zug** durchgelaufen ist. Die Python-Generatoren
allein schreiben die Platinendatei **ohne Zonenfüllung** — wer danach nur
exportiert, liefert eine Platine ohne Massefläche.

**Empfehlung:** einen Schutz gegen genau diesen Fehler einbauen — z. B. im
Gerber-Export prüfen, dass `B_Cu.gbl` mindestens ein Flächenobjekt (`G36`)
enthält, und sonst abbrechen.

---

## 3 Praxis- und Zuverlässigkeitsrisiken (P1)

### P1-1 — VBUS-Heißstecken: 7,3…8,6 V am Ladereglereingang

*Szenario: USB-A→C-Kabel. Bei einer echten USB-C-Quelle tritt es **nicht** auf,
weil VBUS erst nach CC-Erkennung mit definierter Rampe zugeschaltet wird.*

```
C1 = 4u7/25V X7R bei 5 V DC-Bias ≈ 4,09 µF, plus C2 100n → C = 4,19 µF

Z0 = sqrt(L/C):     L=1,0 µH → 0,489 Ω    f0 = 77,8 kHz
                    L=1,5 µH → 0,598 Ω    f0 = 63,5 kHz
                    L=2,0 µH → 0,691 Ω    f0 = 55,0 kHz

V_peak = 5,25 V · (1 + exp(-π·ζ/√(1-ζ²))),  ζ = R/(2·Z0)

  L=1,0 µH  R=0,60 Ω   Q=0,81   V_peak = 5,71 V   unkritisch
  L=1,5 µH  R=0,35 Ω   Q=1,71   V_peak = 7,26 V   > MCP73831 V_DD,max = 7,0 V
  L=1,5 µH  R=0,25 Ω   Q=2,39   V_peak = 7,93 V   > 7,0 V
  L=2,0 µH  R=0,20 Ω   Q=3,45   V_peak = 8,57 V   > 7,0 V
```

**Wird das Absolute Maximum verletzt?** Rechnerisch ja — aber **D1 rettet die
Schaltung**: die USBLC6-2 hat zwischen VBUS und GND eine Klemmdiode mit
V_BR ≥ 6,0 V (DS4260, Tabelle 2). Sie leitet, bevor der MCP73831 seine 7,0 V
sieht.

**Der Preis dafür:**

```
Strom in die Klemme bei V_cl ≈ 6,5 V (L=1,5 µH, R=0,35 Ω):
  I ≈ (5,25/0,598) · √(1-0,238²) · 0,75 ≈ 6,4 A

USBLC6-2 charakterisiert: V_CL = 17 V bei I_PP = 5 A (8/20 µs)
→ 6,4 A liegt über dem Kennwert, und ein ESD-Array ist für
  einzelne Ereignisse qualifiziert, nicht für tausende Steckzyklen.
```

**Urteil:** kein Sofortausfall, aber ein **Verschleißmechanismus**. Über die
Produktlebensdauer (z. B. 1000 Steckvorgänge) wird D1 außerhalb seiner
Qualifikation betrieben — und wenn D1 degradiert, fällt der Schutz für den
MCP73831 lautlos weg.

**Abhilfe, nach Aufwand sortiert:**
1. **TVS an J1**: `SMAJ5.0A` (SMA, V_BR 6,4 V min, V_CL 9,2 V bei 43 A) — ein
   Bauteil, löst es vollständig.
2. **Dämpfung statt Klemmung**: 10 µF Tantal oder Alu-Polymer mit 1…2 Ω ESR
   parallel zu C1. Q fällt unter 1, das Überschwingen unter 10 %. Vorsicht:
   USB 2.0 begrenzt die Eingangskapazität auf 10 µF.
3. **Nichts tun und dokumentieren** — vertretbar, wenn ausschließlich mit
   USB-C-Quellen geladen wird. Das ist eine Betriebsbedingung, keine
   Eigenschaft der Baugruppe.

### P1-2 — ESD an J3/J4/J5: die Serienwiderstände schlagen über

Drei ungeschirmte Kabel nach außen, **kein einziges Klemmelement**.

```
IEC 61000-4-2, 8 kV Kontakt, Generator 330 Ω / 150 pF an J4:

  I_anfang = 8000 V / (330 Ω + 220 Ω + 100 Ω) = 12,3 A
  U über R12 (0805) = 12,3 A · 220 Ω = 2708 V

  CRCW0805 Grenzspannung laut Datenblatt:      150 V
  Überschlagsfestigkeit 0805 (~0,6 mm Kriechweg, 1…3 kV/mm):  600…1800 V
  → R12 schlägt über. Die Entladung erreicht C11 und den GPIO.

  Ladungsbilanz: 150 pF · 8 kV = 1,20 µC in C11 = 100 nF
  → ΔU = 12,0 V am Tasterknoten und an IO3
```

R11/R12 sind **keine ESD-Schutzbeschaltung**. Sie begrenzen einen stationären
Fehlerstrom. Was hier tatsächlich schützt, ist **C11 durch Ladungsteilung** —
und das ist ein Nebeneffekt, kein Entwurf.

**J5 (Piezo)** ist paradoxerweise besser dran, weil der Wandler selbst 45 nF hat:

```
Ladungsteilung: 8 kV · 150 pF/(150 pF + 45 nF) = 26,6 V
Strom in IO1 über R13 = 220 Ω: (26,6 − 3,9)/220 = 103 mA

Das Modul-Datenblatt (Tab. 6-1) nennt für I/O-Pins KEINEN Klemmstrom —
nur eine Spannungsgrenze von −0,3 V … VDD+0,3 V. Der Betriebsfall liegt
außerhalb jeder Spezifikation.
```

Dasselbe gilt für den piezoelektrischen Rückschlag bei mechanischem Stoß
(≈ 119 mA bei 30 V Generatorspannung).

**J3 (Display)** führt fünf Leitungen nach außen, jede nur über 68 Ω — dieselbe
Situation, ohne jede Klemmung.

**Abhilfe:**
- J4, J5: je ein **PESD3V3L1BA** (SOD-323) oder **ESD9B3.3ST5G** direkt am
  Steckverbinder.
- J3: ein 4- bis 6-kanaliges TVS-Array mit ≤ 5 pF je Kanal. Kapazitätsbudget
  prüfen: 5 pF zusätzlich heben t_r von 5,7 auf ≈ 6,8 ns — die SSD1306-Grenze
  von 40 ns bleibt mit Faktor 6 unterschritten.
- Die Klemmen gehören **an den Steckverbinder**, nicht in die Leitungsmitte,
  und ihr Massepfad muss ein Via direkt am Pad haben.

### P1-3 — VBAT-Einbruch beim Einschalten (selbstbegrenzend)

```
Wirksame Kapazitäten bei DC-Bias:
  C5 = 1,87 µF   C6 = 9,9 µF   C8 = 7,5 µF   → C_out = 17,6 µF

Hochlauf mit AP2112-Foldback (50 mA bei V_out=0 → 600 mA bei 3,3 V):
  t = C·∫dV/I(V) = 262 µs

VBAT-Einbruch bei 600 mA über Zell-ESR + F1 + SW1:
  R = 0,15 + 0,15 + 0,02 = 0,32 Ω  → 0,19 V  → 3,70 V fällt auf 3,51 V
  R = 0,15 + 0,90 + 0,02 = 1,07 Ω  → 0,64 V  → 3,70 V fällt auf 3,06 V
```

Bei PTC-Höchstwiderstand bricht VBAT auf **3,06 V** ein. Der LDO geht dabei in
Dropout, der Ausgangsstrom sinkt, die Spannung erholt sich — **das System
begrenzt sich selbst**, es gibt keinen Latch-up-Pfad. Der Anstieg bleibt
monoton, weil EN fest an V_IN liegt und der Regler keine Rückwärtsschleife hat.

**Entscheidend:** Der ESP32-C3 sieht davon nichts, weil das EN-Glied ihn
1,39 ms lang im Reset hält — zu diesem Zeitpunkt ist die Schiene längst stabil.

### P1-4 — Schalterprellen: vom EN-Glied korrekt abgefangen

```
Abschalten: der AP2112 entlädt VOUT aktiv über 60 Ω
  τ = 60 Ω · 17,6 µF = 1,06 ms

Prellen mit 1 ms Unterbrechung:
  Schiene fällt auf 3,3 · e^(-1/1,06) = 1,28 V
  EN folgt mit τ = 1 ms und erreicht V_IH = 2,475 V erst
  t = 1 ms · ln((3,3-1,28)/(3,3-2,475)) = 0,90 ms nach Wiederkehr
  → Die Schiene ist dann seit ~0,6 ms wieder auf 3,3 V.
```

**Kein Brownout-Latchup.** Drei Mechanismen greifen ineinander: die aktive
Entladung des LDO erzwingt einen sauberen Kollaps, das ratiometrische EN-Glied
verzögert den Neustart, und der interne Brownout-Detektor des ESP32-C3 fängt
Zwischenzustände ab. **Voraussetzung:** der Brownout-Detektor muss in der
Firmware aktiviert bleiben (ESP-IDF-Voreinstellung).

### P1-5 — 3W-Regel verletzt, Übersprechen trotzdem unkritisch

Vier Parallelläufe unterschreiten die 3W-Regel (Spalt ≥ 0,50 mm bei 0,25 mm
Bahnbreite):

| Netzpaar | Länge | Spalt | Bewertung |
|---|---|---|---|
| MOSI / OLED_RES | 15,4 mm | 0,35 mm | verletzt |
| MOSI / SCLK | 9,0 mm | 0,35 mm | verletzt |
| +3V3_MCU / SCLK | 8,9 mm | 0,42 mm | verletzt (ruhiger Aggressor) |
| +3V3_MCU / OLED_CS_MCU | 7,8 mm | 0,42 mm | verletzt (ruhiger Aggressor) |

```
Zweilagig, h = 1,5 mm, w = 0,25 mm, Mittenabstand d = 0,60 mm
  d/h = 0,40  →  K_NE ≈ 0,25/(1+(d/h)²) = 0,216

Sättigungslänge: L_sat = t_r·v/2 = 5,7 ns · 164 mm/ns / 2 = 467 mm
Unsere Kopplung ist mit 9…15 mm weit davon entfernt:

  MOSI → OLED_RES:  NEXT = 23,4 mV  =  2,8 % der Störreserve (825 mV)
  MOSI → SCLK:      NEXT = 13,7 mV  =  1,7 % der Störreserve
```

**Bemerkenswert:** Der Kopplungsfaktor ist mit 0,216 sehr hoch — das ist der
Preis einer zweilagigen 1,6-mm-Platine, bei der die Bahnen 1,5 mm über der
Masse, aber nur 0,6 mm voneinander entfernt liegen. Gerettet wird es allein
durch die **kurze Kopplungslänge** und die **flachen Flanken der 68-Ω-Reihe**.
Ohne R5…R9 (t_r ≈ 2 ns) wäre das Übersprechen **2,9-fach höher**.

Die Opfer sind zudem statische Signale (RES, CS, DC) — ein Glitch dort ist
folgenlos. Der einzige kritische Pfad, MOSI → SCLK, liegt bei 1,7 %.

**Kein Handlungsbedarf.** Aber die 68-Ω-Widerstände sind damit
**sicherheitsrelevant**, nicht optional: die Firmware darf die Treiberstärke
nicht auf `GPIO_DRIVE_CAP_3` erhöhen.

---

## 4 DFM/DFA & Lötbarkeits-Review

### Bestätigt in Ordnung

| Prüfpunkt | Messwert | Urteil |
|---|---|---|
| Massepads an SMD und Buchsen | GND-Zonen F.Cu und B.Cu: **Wärmefalle** (0,4 mm Spalt, 0,6 mm Stege) | ✅ handlötgerecht |
| Pad-zu-Pad SOT-23-6 (D1) | **0,300 mm** Kupferspalt | ✅ Standard für 0,95 mm Raster |
| Pad-zu-Pad SOT-23-5 (U2/U3) | 0,300 mm | ✅ |
| ESP32-Handlötpads | 18 Pads, je 1 mm nach außen verlängert, Innenkante unverändert | ✅ vorbildlich |
| Leiterbahn zu Platinenrand | kleinster Wert **0,750 mm** | ✅ |
| Siebdruck über Kupfer | KiCad mit `--severity-all`: **0 Verstöße** | ✅ |
| Bohrungen | ≥ 0,3 mm, Restring 0,2 mm | ✅ |

### Befunde

**DFA-1 — U2 Pad 3 ist vollflächig in 177,8 mm² eingebettet**

Das ist die Kehrseite der M-2-Korrektur. Wärmebilanz beim Handlöten:

```
Spreizwiderstand Pad → Fläche (35 µm Cu, Ersatzradius 0,57 mm → 8 mm):
  R_th = ln(8/0,57)/(2π·400·35e-6) = 30,1 K/W

Wärmestrom für 250 °C Padtemperatur bei 25 °C Umgebung:
  vollflächig:      225 K / 30,1 K/W  = 7,5 W
  mit Wärmefalle:   225 K / 42,0 K/W  = 5,4 W   (4 Stege parallel: 11,9 K/W)
  → die Vollanbindung kostet 40 % mehr Wärmestrom
```

**Bewertung:** Mit einer geregelten Lötstation (≥ 60 W, 350…370 °C,
2–3 mm Meißelspitze) gut machbar. Mit einem 25–40-W-Stiftlötkolben und feiner
Konusspitze **nicht** — das Pad kommt nicht auf Temperatur, und es entsteht die
klassische kalte Lötstelle.

Erfreulich: **nur dieses eine Pad** ist betroffen. Die Messung über alle Pads in
der VBAT-Zone ergab U2 Pad 3 als einzigen Treffer — C3, C4, TP2, F1, D3 und SW1
liegen außerhalb.

**Empfehlung:** So lassen (die Wärmeabfuhr ist der Zweck der Zone) und die
Anforderung in die Bestückungsanleitung schreiben. Alternativ ein Kompromiss mit
2 statt 4 Stegen, der etwa die Hälfte des Vorteils behält.

**DFA-2 — Zonenrand 0,30 mm zum Platinenrand**

```
kleinster Abstand gefüllte Kupferzone → Edge.Cuts: 0,300 mm
```

Das ist `margin = 0.3` in `mk_pcb.py`. Für gefräste Außenkanten mit ±0,15…0,2 mm
Fertigungstoleranz ist das knapp — im ungünstigen Fall wird die Massefläche
angefräst. Die meisten Leiterplattenhersteller akzeptieren 0,25 mm, empfehlen
aber 0,4…0,5 mm.

**Empfehlung:** `margin` auf 0,4 mm anheben. Einzeiliger Eingriff, kostet
nichts, entfernt ein Fertigungsrisiko.

**DFA-3 — EPAD des Moduls bleibt bei Handbestückung unlötbar**

Die 13 Wärmevias unter dem Modul (0,7 mm Pad / 0,3 mm Bohrung) sind auf
`"*.Cu" "F.Mask"` definiert — von unten durch Lötstopplack abgedeckt, von oben
vom Modul verdeckt. Espressif erlaubt das ausdrücklich („not a must"), aber der
thermische und HF-Nutzen der Vias wird in diesem Prozess **nicht realisiert**.

**Empfehlung:** B.Mask an diesen 13 Pads öffnen, dann kann von unten
durchgelötet werden — oder die Vias als reine Durchkontaktierungen deklarieren
und den Anspruch fallenlassen.

---

## 5 Stellungnahme zu den offenen M-Befunden

| Befund | Einstufung | Begründung |
|---|---|---|
| **M-6** Laden unter Last | **reales Risiko** | I_TERM = 11 mA gegen ≈ 50 mA Systemlast → Abschaltung wird nie erreicht, Zelle liegt dauerhaft auf 4,20 V Float. Das ist der Hauptalterungsmechanismus einer LiPo-Zelle. |
| **M-4** Ruhestrom | **reales Risiko** | AP2112K allein 55…80 µA = 28…40 % des 200-µA-Ziels. Das Displaymodul hängt ungeschaltet an +3V3. |
| **M-1** PTC im Entladepfad | **reales Risiko, moderat** | 0,31 V Spannungsfall bei 345 mA kosten ca. 30 % nutzbare Kapazität. Kein Ausfall, aber spürbar. |
| **M-10** Piezo-Klemmung | **reales Risiko, billig zu lösen** | 103 mA in einen Pin ohne spezifizierten Klemmstrom (Abschnitt 3, P1-2). Eine BAT54S löst es. |
| **M-8** Kabel-EMV / ESD | **gespalten** | EMV-Teil: 20 dB Reserve gegen EN 55032 Klasse B → unkritisch. ESD-Teil: real (P1-2). |
| **M-5** Schalterbelastung | **akademisch** | Bei 3,7…4,2 V ist unterhalb der Silber-Mindestbogenspannung (~12 V) **kein stehender Lichtbogen möglich**. Einschaltenergie 6,5 µJ, Ausschaltenergie 24 nJ, Tragverlust 2,4 mW. Formal außerhalb des Ratings, physikalisch harmlos. |
| **M-3** Crowbar-Koordination | **akademisch für diesen Aufbau** | Neue Erkenntnis aus dem echten B5819W-Datenblatt: I_FSM = 9 A bei 8,3 ms, R_θJA = 500 K/W — die Diode überlebt den Verpolungsfall **nicht**. Aber: **J2 ist ein JST-PH und mechanisch kodiert.** Verpolung setzt einen falsch konfektionierten Akkupack voraus. Eintrittswahrscheinlichkeit gering, Versagensart (Kurzschluss) schützend. |

### Software-Maßnahmen, die die Hardware entlasten

**M-6 lässt sich vollständig in Firmware entschärfen** — und das ist die
wichtigste Erkenntnis dieses Abschnitts:

Der ESP32-C3 kann über seine **USB-Serial-JTAG-Einheit den Bus-Zustand
erkennen** (Reset/Suspend). Damit weiß die Firmware ohne zusätzliche Hardware,
ob USB angesteckt ist. Reaktion: Display abschalten, WLAN aus, in
Light-Sleep gehen. Die Systemlast fällt unter die 11-mA-Abschaltschwelle, der
Ladevorgang terminiert regulär und die Zelle geht nicht in den Dauerfloat.

Weiter:
- **M-4:** aggressives Deep-Sleep-Management und D4 per PWM dimmen statt
  statisch treiben. Der LDO-Ruhestrom bleibt allerdings hardwareseitig.
- **M-1:** die Sendeleistung begrenzen (`esp_wifi_set_max_tx_power`). 345 mA
  gelten für 802.11b bei 20,5 dBm; bei 14 dBm sinkt der Spitzenstrom deutlich
  und mit ihm der Spannungsfall über der PTC.
- **P1-5:** Treiberstärke der SPI-Pins auf der Voreinstellung lassen.

---

## 6 Die drei wichtigsten Maßnahmen vor dem Bestellen

### 1. Kondensator-Beschaffung in Ordnung bringen *(blockierend)*

C3, C6 und C8 auf Werte ändern, die die hinterlegte Reihe in 0805 führt — oder
auf 1206 wechseln, wo 10 µF/25 V und 22 µF/10 V verfügbar sind. C3 muss dabei
≥ 4,7 µF **wirksam bei 4,2 V** behalten (MCP73831 § 6.1.1.4). Zusätzlich T12 um
eine Wertabdeckungsprüfung erweitern, sonst tritt der Befund ein drittes Mal auf.

### 2. ESD-Klemmen an die drei Kabelabgänge

Je ein TVS an J4 und J5, ein 4–6-kanaliges Array an J3, jeweils unmittelbar am
Steckverbinder mit Massevia im Pad. Rechnerisch schlägt heute R12 bei 8 kV mit
2708 V über; geschützt wird nur zufällig durch C11.

### 3. TVS an VBUS *(oder dokumentierte Betriebsbedingung)*

`SMAJ5.0A` an J1 — oder die schriftliche Festlegung, dass ausschließlich mit
USB-C-Quellen geladen wird. Ohne beides läuft die USBLC6-2 bei jedem
USB-A-Steckvorgang mit ≈ 6,4 A gegen einen 5-A-Kennwert.

**Zwei Einzeiler obendrein:** `margin` in `mk_pcb.py` von 0,3 auf 0,4 mm, und
eine Abbruchbedingung im Gerber-Export, wenn `B_Cu.gbl` keine Fläche enthält.

---

## 7 Prüfgrundlage

Nachgemessen aus `flappy-esp32c3.kicad_pcb` (57 Footprints, 160 Pads,
Zonenfüllung nach KiCad-Lauf), ausgewertet gegen: ESP32-C3-WROOM-02 v1.7 ·
MCP73831/2 DS20001984G · AP2112 DS39724 · USBLC6-2 DS4260 Rev. 6 · SSD1306
Rev. 1.1 · MF-PSMF Rev. P · C&K OS Series · CEP-1114 · B5819W (SOD-123) ·
YAGEO/KEMET C1002_X7R 2026-08-18 · Vishay CRCW e3 · APT2012EC/SGC.

KiCad-DRC mit `--severity-all --schematic-parity`: 12 Verstöße, sämtlich
`lib_footprint_mismatch` — vorbestehend und generatorbedingt, gegen den
Ausgangsstand verifiziert. `isolated_copper` ist von 1 auf 0 gefallen.
