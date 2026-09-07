# Prüfung des Ausgangsentwurfs

Stand: 5. September 2026. Maßgeblich sind die vorhandenen KiCad-Dateien unter `hardware/`, nicht die älteren Exportdateien. Dieser Bericht bewertet den ursprünglichen Entwurf; Referenzbezeichner in diesem Bericht beziehen sich auf diesen Ausgangsstand. Revision B verwendet eine neue Nummerierung.

## Unveränderter Ausgangsstand

Der anfängliche Git-Status ist unter `verification/initial-git-status.txt` gesichert. Die absichtlich entfernten Dateien wurden nicht wiederhergestellt. Historische Informationen wurden nur lesend verwendet. Der ursprüngliche Schaltplan, das PCB und Projekt wurden nicht überschrieben. Es wurde nichts bestellt, committed oder gepusht.

Die neu ausgeführten Originalprüfungen liegen unter `verification/old-current-erc.rpt`, `old-current-drc.rpt` und `old-current.net`. KiCad 10.0.5 meldet beim Original 0 ERC-Fehler und 18 Warnungen; beim PCB 89 DRC-Warnungen und 0 offene Verbindungen. Die DRC-Warnungen verteilen sich auf 65 isolierte Kupferbereiche, 11 Bibliotheksabweichungen, 9 Siebdruck/Kupfer-Konflikte, 3 Siebdrucküberschneidungen und 1 Bibliotheksproblem. Der fehlende lokale Bibliotheksbestand erklärt einen Teil der Meldungen; er wurde bewusst nicht aus Git restauriert.

## Befunde und Folgen

| Priorität | Befund im Original | Technische Folge | Umsetzung in Revision B |
|---|---|---|---|
| Kritisch | MCP73831-BAT versorgt gleichzeitig Akku und laufendes System. | Der Regler sieht den Summenstrom; eine Last über der Abschaltschwelle verhindert oder verfälscht den Ladeabschluss. | BQ24074 mit getrenntem OUT-Systempfad und BAT-Ladestrommessung. |
| Kritisch | USB-C-Breakout und dessen Rd-Bestückung unbekannt. | Keine belegbare Type-C-Senkenfunktion; doppelte Rd ergeben falsche CC-Pegel. | Definierter GCT USB4105 direkt auf dem PCB, genau ein 5,1-kΩ-Widerstand je CC. |
| Kritisch | Reale Akku- und Displaykabelbelegung unbestätigt. | Verpolung oder 5-V-Einspeisung kann Bauteile beschädigen. Ein Steckerserienname legt die Kabelpolung nicht fest. | Pinfolgen festgelegt; reale Kabel bleiben Bestellungssperren. Laden standardmäßig deaktiviert. |
| Hoch | VBUS-Messung mit 100 kΩ / 100 kΩ an GPIO20. | Bei 4,75 V nur 2,375 V; das liegt unter 0,75 × 3,3 V = 2,475 V. Bei ausgeschaltetem LDO kann der Teiler den GPIO speisen. | Kein VBUS-Teiler an einem ESP-GPIO. PGOOD ist als Open-Drain-Messpunkt zugänglich; USB-Anwesenheit über die USB-Funktion. |
| Hoch | Permanenter Akku-ADC-Teiler bei ausgeschalteter 3V3-Versorgung. | Dauerverbrauch und Strom über die GPIO-Schutzstruktur. | High-Side-Schalter im Messzweig; aus, wenn 3V3 aus ist. |
| Hoch | OLED bleibt mit Spannung versorgt. | Der unbekannte Modulregler und Controller dominieren möglicherweise den Schlafstrom. | TPS22919 schaltet die OLED-Schiene; Nexperia-Puffer trennt die vier SPI-Signale bei ausgeschalteter Schiene. |
| Hoch | CS direkt am Strapping-Pin GPIO8 und externen Modul. | Externe Pull-Widerstände beeinflussen den Startmodus. | GPIO8 steuert nur ein MOSFET-Gate; physisches CS ist invertiert und an OLED_3V3 hochgezogen. |
| Hoch | Große MLCC ohne eindeutige Herstellerteilenummer und belegte DC-Bias-Kurve. C3: 10 µF/25 V X7R, C6: 22 µF/10 V X5R, C8: 10 µF/16 V X7R, jeweils 0805. | Nennkapazität beweist weder wirksame Kapazität noch Beschaffbarkeit dieses konkreten Dielektrikums/Gehäuses. | Konkrete 1206-Teilenummer, parallelisierte Stützung, quantitative Mindestkapazitäten als Abnahmekriterien. |
| Hoch | PTC und Schottky-Crowbar ohne gemeinsame Zeit-/Energieauslegung. | Eine PTC begrenzt langsam und kann einen Diodenfehler nicht zwangsläufig beherrschen. | Serien-Schmelzsicherungen; aktive Batterie-Verpolerkennung; VBUS-TVS und spannungsfester Ladeeingang. Keine Behauptung einer universellen Crowbar-Koordination. |
| Hoch | Keine unabhängig belegte Akku-Temperaturüberwachung bzw. Schutzplatine. | Ein Lader ersetzt keinen Zellschutz. | TS-Eingang, Timer und externer NTC; R39 bleibt DNP, bis zusätzlich der reale Akku einschließlich Temperaturabschaltung qualifiziert ist. |
| Mittel | AP2112K-Ruhestrom wurde für einen sehr kleinen System-Schlafstrom nicht vollständig berücksichtigt. | Bereits der LDO benötigt typisch 55 µA, maximal 80 µA unter den Datenblattbedingungen. | XC6220B mit typ. 8 µA im Sparmodus; vollständiges Budget mit Leckströmen und offenen Pack-Anteilen. |
| Mittel | ESD und Piezo-Schutz teilweise railbezogen; unbestätigter Piezo. | Ein Diodenarray beweist weder systemweiten ESD-Schutz noch Eignung eines beliebigen Summers. | Separate Kabel-ESD-Arrays, MOSFET-Treiber, Strombegrenzung, Freilaufdiode; nur isolierter passiver Piezo. |
| Mittel | Exporte und Stückliste widersprechen dem aktuellen Design. | Falsche Teilebestellung oder falsches Displaykabel möglich. | Alle Lieferdaten aus dem abschließend geprüften Rev-B-Stand neu exportiert; Prüfsummenliste. |

Die aktuelle Originalnetzliste hat den achtpoligen J3. Die ältere Stückliste enthält noch sieben Kontakte und lässt C12, D5 sowie R19 bis R23 aus. Solche Altdateien sind keine Fertigungsgrundlage. Dass der Original-DRC keine Luftlinien meldet, entkräftet die elektrischen Befunde nicht.

## Unabhängige Grenzen der Prüfung

Es wurden keine realen Bauteile, kein Prototyp und keine fertige Platine gemessen. Temperatur, Transienten, tatsächlicher Schlafstrom, Schallpegel, HF-Abstrahlung und USB-Signalqualität sind deshalb nicht als bestanden gekennzeichnet. Die neue Fertigungsfreigabe richtet sich ausschließlich nach `freigabe-checkliste.md`.
