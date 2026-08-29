# Inbetriebnahmeprotokoll

Nach Projektplan 4.5. Für **jede** gebaute Baugruppe einzeln ausfüllen und ablegen.

Baugruppe Nr.: ______   Datum: ______   Bearbeiter: ______

## Lötreihenfolge

Flach vor hoch, klein vor groß:

1. U1 noch **nicht** bestücken.
2. SOT-23: U2 (MCP73831), U3 (AP2112K-3.3), D1 (USBLC6-2SC6), D3 (B5819W, SOD-123)
3. Passive 0805: R1…R18, F1, C1…C11
   **R17 und R18 (5,1 kΩ, CC1/CC2) nur bestücken, wenn das USB-C-Breakout
   selbst keine CC-Widerstände trägt** — nachmessen, siehe
   `entscheidungen.md` Abschnitt 3. Der Siebdruck erinnert daran.
4. LEDs D2 (rot, zu U2) und D4 (grün, links unten) — Polarität beachten
5. **U1** (ESP32-C3-WROOM-02): die Pads ragen 1,5 mm über die Modulkante,
   von außen anlöten, Modul nicht mit der Spitze berühren
6. J1 (USB-C-Breakout) flach auf die sechs Lötaugen
7. Durchsteckbauteile: J2, J3, J4, SW1, LS1

## Gestufte Inbetriebnahme

| Stufe | Vorgehen | Erwartung | gemessen | i.O. |
|---|---|---|---|---|
| 0 | Sichtprüfung unter der Lupe; Durchgangsprüfung TP3–TP12 (3V3–GND) und TP2–TP10 (VBAT–GND) | hochohmig, kein Kurzschluss | | ☐ |
| 0b | Widerstand CC1 bzw. CC2 gegen GND messen (an J1-5/J1-6) | 5,1 kΩ ± 5 %. 2,55 kΩ heißt: das Breakout hat eigene Widerstände, R17/R18 wieder auslöten | | ☐ |
| 1 | U1 noch nicht bestückt. Labornetzteil 5 V, Strombegrenzung 100 mA an TP1 (VBUS) und TP10 (GND) | TP3 = 3,30 V ± 3 %, Aufnahme < 1 mA, grüne LED **aus** (sie hängt am GPIO) | | ☐ |
| 2 | Akku an J2 (Pluspol am Pad mit dem „+" im Siebdruck), Strommessgerät in Reihe, USB anstecken, SW1 auf **Aus** | Ladestrom 147 mA ± 10 %, rote LED D2 leuchtet | | ☐ |
| 3 | U1 bestücken, Strombegrenzung 300 mA, SW1 auf **Ein** | 20…30 mA, kein Bauteil wird warm | | ☐ |
| 4 | USB an den Rechner | Gerät meldet sich als serielle Schnittstelle (USB-Serial-JTAG) | | ☐ |
| 5 | Blinkprogramm auf IO0 flashen | grüne LED D4 blinkt | | ☐ |
| 6a | Display über den 7-poligen Kabelsatz an J3 | Testbild erscheint | | ☐ |
| 6b | Taster über den 2-poligen Kabelsatz an J4 | Pegel an TP5 wechselt beim Drücken | | ☐ |
| 6c | Piezo LS1 | Ton beim Testprogramm hörbar | | ☐ |

## Wenn Stufe 1 fehlschlägt

* TP3 = 0 V → U3 falsch herum, SW1 in Stellung Aus oder Kurzschluss nach GND.
  Widerstand TP3–TP12 messen; unter 10 Ω deutet auf einen Lötzinnschluss an C6/C7.
* TP3 = VBUS → U3 nicht angelötet (Durchgang von TP2 nach TP3).
* Stromaufnahme > 5 mA ohne U1 → Zinnbrücke an einem SOT-23 suchen.

## Wenn Stufe 4 fehlschlägt

* Kein serielles Gerät → EN prüfen: TP6 muss nach dem Einschalten auf 3,3 V liegen.
  Liegt EN auf 0 V, ist R4 nicht angelötet oder C10 hat einen Schluss.
* Gerät meldet sich, lässt sich aber nicht flashen → TP7 (BOOT) beim Reset
  (TP6 kurz auf Masse) auf einen Massepunkt legen, das erzwingt den Bootlader.
* Nichts geht → Pinbelegung von J1 gegen das gekaufte Breakout prüfen
  (siehe `entscheidungen.md`, Abschnitt 3.1). D+ und D− vertauscht ist der
  häufigste Fehler.

## Zugehörige Messungen (Projektplan 6)

| Nr. | Messung | Messpunkte auf dieser Platine |
|---|---|---|
| M1 | Prellverhalten des Tasters | TP5 (Tasterknoten) gegen TP11 (liegt daneben) |
| M2 | Bildzeit | freier GPIO IO10 am Modulrandkontakt |
| M3 | Stromaufnahme der Modulversorgung | R3 auslöten, Shunt zwischen TP3 und TP4 |
| M4 | Lade- und Entladekurve | TP2 (VBAT) gegen TP10 |
| M5 | Jitter des Physiktakts | IO10 am Modulrandkontakt |
| M7 | Einbruch der 3,3-V-Schiene | TP4 gegen TP12 (liegt daneben), wechselspannungsgekoppelt |
| M8 | Signalintegrität am Displaykabel | am Displayende messen; R5…R9 sind einzeln gegen 0/33/68/100 Ω tauschbar |
