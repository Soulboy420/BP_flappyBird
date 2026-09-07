# Freigabe und gestufte Inbetriebnahme

**Stand 06.09.2026: NO-GO für eine Bestellung als freigegebenes, akkubetriebenes Endgerät.** Die CAD-Prüfungen sind abgeschlossen; die nachstehenden realen Schnittstellen und elektrischen Abnahmen sind offen. R39 bleibt DNP: Laden ist in der ausgelieferten Bestückung deaktiviert. Es wurde weder bestellt noch ein Prototyp gemessen.

## Abgeschlossene digitale Prüfungen

- [x] Originaldateien und absichtliche Löschungen erhalten; neue Daten ausschließlich in `hardware/redesign/`.
- [x] KiCad 10.0.5: finaler ERC ohne Fehler/Warnungen; finaler DRC ohne Fehler/Warnungen, offene Verbindungen oder Schaltplan-Abweichungen.
- [x] Exakter Abgleich: 111 Referenzen, 58 Funktionsnetze; 85 bestückte Teile und 26 DNP-Referenzen einschließlich 16 Testpads und vier Bohrungen. `verification/consistency.json`.
- [x] 301 nummerierte physische Pads mit XML-Netzliste, Entwurfsquelle und BOM verglichen. `output/pinmapping.csv`.
- [x] Symbole, Footprints und Modellpfade lokal auflösbar; kritische Gehäuse-Pinouts anhand der in `quellen.md` genannten Herstellerunterlagen geprüft.
- [x] Antennensperrbereich auf beiden Kupferlagen; native Prüfung auf Kurzschlüsse, Abstände, Kupferinseln, Courtyards, Lötstopp und Bestückungsdruck.
- [x] Masseflächen gefüllt; Gerber und Bohrdaten aus dem geprüften gespeicherten PCB. Export/Dateiintegrität siehe `verification/pruefbericht.md` und `verification/SHA256SUMS`.

## Vor Bestellung am realen Teil bzw. beim Fertiger klären

- [ ] **OLED:** Hersteller/Modell notieren; 3,3-V-Versorgung und Logik prüfen; tatsächliche Pinfolge jeder der acht Adern durchmessen. Platinenfolge J3: **1 GND, 2 3V3, 3 SCK, 4 GND, 5 MOSI, 6 RESET, 7 DC, 8 CS**. Gegensteckeransicht und Kabellänge dokumentieren. Aufgenommenen Start-/Dauerstrom mit der 60-mA-Auslegungsannahme vergleichen.
- [ ] **Akku:** Datenblatt und Pack-Schutzschaltung identifizieren; 1S/4,2 V, erlaubtes oberes Ladeende ≥4,23 V, Ladestrom ≥160 mA, Entladestrom ≥0,8 A und Kapazität ≥500 mAh bestätigen. Tatsächliches J2-Pin1 = Plus mit Multimeter nachweisen. UV/OV/OC/Kurzschluss-Schutz und eigene Temperatur-Ladeabschaltung bestätigen. Unbekannter Pack bleibt abgesteckt.
- [ ] **Temperatur:** Semitec 103AT-2 oder elektrisch qualifiziertes Äquivalent am Pack befestigen. J6.1 NTC/J6.2 GND. BQ-TS allein genügt nicht für garantiertes Laden nur bei 0…45 °C. Ohne unabhängigen Nachweis bleibt R39 unbestückt.
- [ ] **Schalter:** OS102011MS2QN1 oder vorab geprüfte Alternative; 1–2/2–3, nicht kurzschließend, drei Kontakt-/zwei Befestigungsbohrungen, Betätigerhöhe und Ausschnitt prüfen. Wenige-µA-Kontaktstrom ist separat zu erproben.
- [ ] **Taster/Piezo:** Potentialfreien Schließer und getrennte Lampenpins identifizieren. Piezo passiv, isoliert und ≤30 nF als Startannahme; Kapazität, Abmessungen und Einbau prüfen. Kein magnetischer/aktiver Summer ohne Neuauslegung.
- [ ] **Mechanik:** Vier M2-Bohrungen Ø2,2 mm bei (3,3), (87,3), (3,57), (87,57) mm. Schraubköpfe bis 5 mm, Abstandshalter und Werkzeugzugang prüfen. PCB 90×60 mm; ESP-Antenne ragt oberhalb der Kante heraus. Akku/Metall/Display dürfen den Antennenraum nicht füllen. USB-Stecker, PH/XH-Gegenstecker und Kabelbiegeradien prüfen.
- [ ] **Druckmaßstab:** PCB-PDFs sind zur Sichtprüfung 2,5:1 vergrößert. Für eine mechanische Schablone auf **40 %** ausgeben bzw. aus KiCad neu 1:1 plotten, „an Seite anpassen“ ausschalten und die 90-mm-Kante nachmessen.
- [ ] **Fertiger:** Zwei Lagen, 1,6 mm; 35 µm Kupfer je Seite und 1,51-mm-Kern/εr≈4,2 sind Annahmen. Tatsächliche Dicke, Dk, Lötstopp und Kupferfinish bestätigen. USB-Hauptstrecke 1,50/0,25 mm einschließlich Übergängen vom Fertiger auf 90 Ω ±10 % bewerten lassen; bei Änderung neu routen/prüfen/exportieren.
- [ ] **Fertigungstoleranzen:** 0,15-mm-Leiter/Abstand, kleinste Vias 0,50/0,25 mm und nominaler Restring 0,125 mm, 0,30-mm-Kupferkantenabstand, PTH/NPTH und USB-Schlitze bestätigen. Keine Daten stillschweigend auf gröbere Fertigungsregeln skalieren.
- [ ] **Kondensatoren:** TDK-DC-Bias-/Alterungsdaten qualifizieren; ≥10 µF effektiv an LDO IN/OUT, ≥4,7 µF an BQ BAT/OUT, lokales Modulziel ≥10 µF. Toleranz und Temperatur einbeziehen. Keine 0805-Ersatzteile nur nach Nennwert bestellen.
- [ ] **Bestückungsverfahren:** QFN-Exposed-Pad und USB-Buchse mit Schablone/Heißluft oder Reflow beherrschen. Kleine Massevias teilweise nahe/in Pads: Lötzinnabfluss und Exposed-Pad-Lötung beachten; gegebenenfalls Füllen/Tenting mit dem Fertiger abstimmen und anschließend erneut prüfen. Alle DNP-Optionen gegen BOM kontrollieren.

Erst wenn diese Punkte dokumentiert abgeschlossen sind, kann ein eingeschränkt freigegebener Laborprototyp ohne aktive Ladefunktion erwogen werden. Die Bestellfreigabe entsteht nicht automatisch durch einen sauberen DRC.

## Stufen am Prototyp – noch nicht durchgeführt

1. **Unbestromt:** Lötstellen, Orientierung von IC/FET/Diode/LED, Pin1-Markierungen, Exposed Pad und USB-Pins unter Vergrößerung kontrollieren. Widerstände GND↔VBUS/VBAT/VSYS/3V3 plausibilisieren; Kondensator-Aufladeeffekte berücksichtigen. R39/R12/R6/R22/C17/C18 unbestückt lassen.
2. **USB ohne Akku/Module, SW1 OFF:** Strombegrenzte 5-V-Quelle an USB, zunächst 100-mA-Limit. VBUS/VSYS, CE HIGH und 3V3≈0 V messen. Bei Kurzschluss, Instabilität oder Erwärmung sofort abschalten. Ein USB-Stecker mit Labornetzteil ersetzt keine Enumeration.
3. **Regler getrennt:** R14 entfernen, SW1 RUN. 3V3_REG und Ein-/Ausschaltverlauf prüfen; elektronische Last schrittweise bis zum vorgesehenen Strom. Ausgang 3,0…3,6 V einschließlich Spitzen; keine anhaltende Schwingung. Spannung, Lastsprung und Gehäusetemperatur protokollieren.
4. **Modul:** R14 wieder einsetzen oder über geeignetes Messgerät überbrücken. Revision-B-Firmware mit passender GPIO-Tabelle programmieren. Boot/Reset/Download, beide USB-C-Orientierungen und Enumeration prüfen. USB100 vor Freigabe, USB500 erst danach. Ohne Akku keine WLAN-Last vor Enumeration. Suspend/Resume mit GPIO2/Q7 testen.
5. **Akku-Simulation:** Echte Zelle zunächst weiter abgesteckt. Strombegrenzte, zum bidirektionalen Versuch passende Quelle/Simulator verwenden; gewöhnliche Labornetzteile können Ladestrom oft nicht aufnehmen. Korrekte/verpolte Verbindung und Akku-/USB-Reihenfolgen einschließlich SW1 OFF/RUN testen. Negative Spannung an BQ BAT und andere Absolutgrenzen mit Oszilloskop prüfen; nicht aus statischen Multimeterwerten ableiten.
6. **Peripherie einzeln:** OLED mit geprüfter Kabelbelegung anschließen, zunächst 1 MHz SPI. Versorgung, Anlaufstrom, Reset und abgeschaltete Schiene auf Rückspeisung prüfen. Taster entprellen/Wake-up; Piezo mit zunächst 2 kHz anregen und Strom/Lautstärke messen. LEDs prüfen.
7. **Strom und Unterspannung:** Gesamten Akkustrom in J2 und geschalteten Strom über R14 getrennt messen: OFF, Boot, Spiel, OLED aus, Deep Sleep, USB-Suspend, gedrückter Taster. Temperatur und Pack-Schutzverbrauch dokumentieren. ADC bei mindestens zwei Spannungen kalibrieren; 150 ms Einschwingen berücksichtigen. Abschaltpunkt um 3,6 V unter Last anhand 3V3-Minimum und Packdaten festlegen.
8. **Laden nur nach separater Akku-/Temperaturfreigabe:** R39 bestücken, realen geschützten Pack und bestätigten NTC verwenden. Ladestrom 127,5…159,1 mA unter nicht begrenzenden Bedingungen; Spannung ≤4,23 V und innerhalb Zellfreigabe. Ladeende unter Systemlast, Timer, NTC-offen/Kurzschluss und Temperaturabschaltung prüfen. Keine absichtliche Zellüberhitzung zum Prüfen; qualifizierte Simulation/Prüfmittel nutzen.
9. **Wärme/Robustheit:** Bei höchster vorgesehener Umgebung (zunächst 40 °C) und Systemlast mit/ohne Laden Temperaturen und Spannungsfälle messen. Sperrschichtreserve und kein thermisches Regeln im Normalbetrieb nachweisen. USB-Hot-Plug, ESD und Störungen an externen Kabeln mit geeigneter Ausrüstung prüfen. Ein Datenblatt-ESD-Wert ist kein Systemprüfergebnis.

## Freigabeprotokoll

| Feld | Eintrag |
|---|---|
| CAD-Stand | Rev B; Hashes in `verification/SHA256SUMS` |
| Physischer Prüfer / Datum | offen |
| Akkumodell / Datenblatt / zulässiges Ladefenster | offen |
| OLED-Modell / verifizierte Kabelzeichnung | offen |
| Fertiger / bestätigter Stack-up | offen |
| Messprotokoll / Firmware-Version | offen |
| R39-Ladeoption freigegeben? | **Nein** |
| Bestell-/Betriebsfreigabe | **NO-GO** |
