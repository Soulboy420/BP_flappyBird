# Offene Annahmen und Bestückungsvarianten

**Aktuelle Bestellfreigabe: NO-GO.** Die digitalen Entwurfsdaten sind prüfbar; reale Module und der Fertiger-Stack-up sind noch nicht bestätigt. Keine unbekannten Kabel probeweise einstecken.

| Gegenstand | Festgelegte Schnittstelle / Annahme | Erforderlicher Nachweis |
|---|---|---|
| OLED | 3,3-V-SPI-Modul, insgesamt höchstens 60 mA als Auslegungsannahme, Logik ohne externe 5-V-Pullups; J3 XH, 8-polig, 2,50 mm. | Genaue Typnummer, Versorgung/Logikpegel, Anlaufstrom, Abmessungen, Steckeransicht und jede Kabelader durchmessen. |
| J3 | Pin 1 GND, 2 OLED_3V3, 3 SCK, 4 GND, 5 MOSI, 6 RESET_N, 7 DC, 8 CS_N. | Pin 1 ist auf der Platine durch das quadratische Pad und im Bestückungsplan bezeichnet. Die Reihenfolge beim Blick auf den Gegenstecker ist gespiegelt! |
| USB | GCT USB4105-GF-A auf der Platine. Das unbekannte Breakout wird nicht verwendet. 5-V-USB, kein PD-Vertrag. | Steckermechanik, Gehäuseausschnitt, Reflow/Handlötzugang und beide Kabelorientierungen. |
| LiPo | Geschützter 1S-Li-Ion/LiPo, 4,2-V-Ladekennlinie, mindestens 500 mAh, mindestens 160 mA zulässiger Ladestrom und 0,8 A Entladestrom. J2 PH 2 mm: 1 positiv, 2 GND. | Pack-Datenblatt, maximale Ladespannung mindestens 4,23 V innerhalb Herstellerfreigabe, UV/OV/OC/Kurzschluss-Schutz und eigene Temperaturabschaltung fürs Laden. Abschaltschwellen und Kabelpolung prüfen. |
| Akkutemperatur | Semitec 103AT-2, 10 kΩ bei 25 °C, am Pack thermisch befestigt, eigener zweipoliger J6: 1 NTC, 2 GND. | Der BQ-TS-Eingang allein garantiert NICHT das übliche Zell-Ladefenster 0…45 °C. Ein entsprechend begrenzender Pack-Schutz ist nötig; alternativ eine gesondert entwickelte und erneut geprüfte Temperaturüberwachung. R39 bis dahin nicht bestücken. |
| Schalter | C&K OS102011MS2QN1, nicht kurzschließender SPDT, Pin 2 gemeinsamer Kontakt, 1 VSYS/RUN, 3 GND/OFF. | Das gekaufte Teil kann anders aussehen oder anders belegt sein. Mechanik und Durchgang in beiden Stellungen messen. Zuverlässigkeit bei wenigen µA Kontaktstrom nachweisen; keine ungeprüfte Substitution. |
| Taster | Potentialfreier Schließer ohne Lampe/Versorgung am Signalkontakt. J4: 1 BUTTON_EXT, 2 GND. | Getrennte Lampenkontakte identifizieren; Kontakt und Kabel durchmessen; Wake-up prüfen. |
| Piezo | Passiver, elektrisch isolierter Zweidraht-Piezo, zunächst ≤30 nF und Startfrequenz ca. 2 kHz. J5: 1 P, 2 N. | Kapazität, Resonanz, Kabel und erreichbaren Schallpegel messen. Kein aktiver oder magnetischer Summer als ungeprüfter Ersatz. |
| Gehäuse | PCB 90 × 60 mm; ESP-Antenne ragt über die obere Kante. Vier 2,2-mm-M2-Bohrungen. | 1:1-Ausdruck, Schraubköpfe/Abstandshalter, Akku, Displayrückseite, USB-Stecker und freier Antennenraum. Keine leitenden Teile oder Akku direkt an/über der Antenne. |
| Fertigung | Zwei Lagen, 1,6 mm, angenommener Aufbau mit 35 µm Kupfer je Seite und 1,51 mm FR4-Kern, εr = 4,2. | Tatsächliche Material-/Dickenangaben und USB-Impedanzprüfung des Fertigers; 0,15-mm-Leiter/Abstand und kleinste 0,50/0,25-mm-Vias bestätigen. |

## Bestückungsoptionen im ausgelieferten Stand

- **R39 = DNP:** Ladefreigabe gesperrt; R10 zieht CE auf VSYS. Erst nach Akku-/Temperaturfreigabe darf R39 als 0 Ω bestückt werden. Der System-Power-Path arbeitet auch bei gesperrtem Laden.
- **R12 = DNP:** 10-kΩ-TS-Ersatz nur für Labortests OHNE Akku. Nicht als dauerhafte Temperatursensor-Überbrückung verwenden.
- **R6 = DNP:** Kein Widerstandspfad vom verpolten Pack zum BAT-Eingang. Akku korrekt anstecken, bevor USB angeschlossen wird. Wenn der Verpolschutz nach Packwechsel bei bereits vorhandenem USB nicht freigibt: USB abziehen und neu verbinden. Diese Reihenfolge ist funktional relevant.
- **R22 = DNP:** EN2 besitzt einen internen Pulldown; der externe 100-kΩ-Pulldown bleibt unbestückt. R38 = 100 kΩ und Q7 bilden die invertierende Ansteuerung. R22 nicht beiläufig nachbestücken.
- **C17/C18 = DNP:** 18-pF-USB-Option ausschließlich nach Messung der Signalform. Der Ausgangsaufbau nutzt diese Kondensatoren nicht.
- **TP1…TP16 und H1…H4:** Physische PCB-Merkmale, keine einzulötenden Komponenten. DNP bedeutet hier nicht, dass die Kupferpads oder Bohrungen fehlen.

Die vorhandene Firmware ist nicht für Revision B freigegeben. Die verbindliche neue GPIO-Tabelle und Start-/Schlafsequenz stehen in `designentscheidungen.md`. Das ursprüngliche Softwareprojekt wurde nicht automatisch umgestellt.
