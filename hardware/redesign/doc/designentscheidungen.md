# Revision B: Auslegung und technische Entscheidungen

Stand 2026-09-06. Dieses Dokument beschreibt den tatsächlich gezeichneten Entwurf. Herstellerquellen mit Revision und Fundstelle stehen in `quellen.md`; die Pin-/Netz-Zuordnung ist zusätzlich maschinenlesbar in `output/pinmapping.csv` dokumentiert. Messwerte eines Prototyps liegen noch nicht vor.

## Versorgung und Laden

J1 → F1 → VBUS → BQ24074 IN. D1 liegt hinter F1 nach GND. Der BQ speist VSYS separat von seinem BAT-Ladeanschluss; VSYS versorgt den LDO und die Ladeanzeige. J2 → F2 → Q1 → VBAT ist der bidirektionale Akkupfad. Systemlast fließt damit nicht durch die Ladeabschlussmessung. SW1 schaltet nur den LDO-Enable-Eingang: Laden kann nach gesonderter Freigabe auch bei ausgeschaltetem Gerät stattfinden.

Der MCP73831 wurde durch BQ24074RGTR ersetzt, um Power-Path, Eingangsbegrenzung, Sicherheits-Timer und TS-Überwachung zusammenzuführen. Das 3 × 3 mm große VQFN mit Exposed Pad erfordert lokale Reflow-/Heißluftbestückung und Kontrolle der Lötung. Dies ist eine bewusste Ausnahme vom Lötkolben-Aufbau. Die große Zahl zusätzlicher Teile entsteht hauptsächlich durch Schutz, abschaltbare Peripherie, Messzugänge und konkret ausgelegte Stützkondensatoren.

**Default: kein Laden.** R10 = 100 kΩ zieht CE auf VSYS. R39 = DNP; erst dessen freigegebene 0-Ω-Bestückung aktiviert den Lader. R10 ist kein Freigabe-Jumper. Der CE-Eingang erreicht bei vorhandenem USB selbst mit 10 µA angenommenem Eingangsstrom mindestens etwa 3,3 V und liegt damit über VIH = 1,4 V. Ein offener NTC-Anschluss verhindert beim BQ24074 zusätzlich das Laden.

### Strom, Spannung und Timer

- R7 = 6,19 kΩ ±1 %: ICHG = KISET/R. Typisch 890/6190 = **143,8 mA**; mit KISET = 797…975 und Widerstandstoleranz **127,5…159,1 mA**. Für einen 500-mAh-Pack maximal etwa 0,32 C. Die Freigabe muss dessen Datenblatt dennoch ausdrücklich erlauben.
- BAT-Regelspannung **4,16…4,23 V**. Der Zelltyp muss diese obere Grenze erlauben. Kein LiFePO4 und kein 4,35-V-Pack.
- ITERM bleibt ausdrücklich NC: BQ-Standardabschaltung, typisch 10 % des programmierten Ladestroms im 500-mA-Modus; USB100 verwendet eine andere interne Abschaltschwelle. Nicht aus der Schaltung allein auf einen exakten gemessenen Abschlussstrom schließen.
- R8 = 3,24 kΩ setzt die Reserve-Stromprogrammierung. Normalbetrieb verwendet die USB100/500-Modi. Firmware darf den Zustand EN2=1/EN1=0 nicht unbeabsichtigt als Dauerzustand wählen.
- R9 = 46,4 kΩ ±1 %: Timer typisch 48 × 46,4 × 10 = 22 272 s = **6,19 h**. Mit 36…60 s/kΩ und R-Toleranz etwa **4,59…7,81 h**. Strom-/Temperaturregelung beeinflusst den realen Ablauf; der Timer ist keine Kapazitätsmessung.
- Einschaltzustand EN1=0, EN2=0: USB100, garantiert höchstens 100 mA. Nach USB-Enumeration darf EN1=1 gewählt werden: höchstens 500 mA. Ein USB-C-Stecker allein erlaubt keine beliebig hohe Stromaufnahme.
- Bei laufendem Gerät und 500-mA-Eingangslimit reduziert der Power-Path zuerst den Ladestrom und nutzt bei Bedarf den Akku zur Unterstützung. Ohne Akku müssen Start und Firmware bis zur Enumeration innerhalb des USB100-Budgets bleiben; WLAN darf vorher nicht anlaufen.

### Akku-Temperatur: bewusst offen gehaltene Freigabe

Der Semitec 103AT-2 hat 10 kΩ ±1 %, B25/85 = 3435 K ±1 %. Mit dem 100-Ω-Serienwiderstand R11 und den BQ-Grenzen VHOT=270…330 mV, VCOLD=2,0…2,2 V, ITS=72…78 µA ergeben sich NTC-Widerstände von ungefähr 3,36…4,48 kΩ am heißen und 25,54…30,46 kΩ am kalten Abschaltpunkt. Eine einfache Beta-Näherung ergibt ungefähr **47…56 °C** bzw. **−1,3…+2,6 °C**, noch ohne NTC-Toleranz, Kennlinienabweichung und thermische Verzögerung.

Das genügt **nicht** als garantierte 0…45-°C-Ladebegrenzung. TS dient hier als zusätzliche Pack-/Kabelfehlerüberwachung. R39 darf nur freigegeben werden, wenn ein eigenständig temperaturgeschützter Pack diese Lücke schließt, oder wenn eine gesondert entwickelte Temperaturüberwachung erneut geprüft wurde. Der 10-kΩ-DNP-Widerstand R12 darf diese Anforderung nicht verdecken.

### Verpolung, Sicherung, Stromtragfähigkeit

Q1 DMP2035U-7 und Q2 BSS84-7-F folgen dem Erkennungsprinzip aus ADI AN-171, Abbildung 7. Q1: Source an VBAT, Drain an PACK_FUSED, Gate BAT_GATE. Q2 erkennt eine negative Packspannung und hebt das Q1-Gate zur Source an. R5 zieht das Gate im Normalfall nach GND. Die Bodydiode von Q1 lässt einen korrekt angeschlossenen Akku zunächst zur Systemseite anlaufen.

**R6 bleibt DNP:** Ein bestückter 1-MΩ-Referenzpfad würde bei verpoltem Pack einen kleinen Gleichstrom in VBAT erlauben, dessen negative Spannung am BQ nicht ausreichend begrenzt ist. Deshalb ist als Betriebsregel Akku-vor-USB festgelegt. Ein Packwechsel bei laufendem Ladeeingang kann den Schutz in einem sperrenden Zustand halten; USB aus-/einstecken. Schalttransienten und die Einsteckreihenfolgen müssen mit einer strombegrenzten Akku-Simulation gemessen werden. Das ist kein Nachweis beliebiger Hot-Swap-Festigkeit.

F1/F2 sind **Littelfuse 0466001.NRHF, 1206, 1 A**. Nenn-Kaltwiderstand 75 mΩ; typisch 37,5 mV bei 0,5 A. 200 % Nennstrom werden spätestens nach 5 s, 300 % spätestens nach 0,2 s unter den Datenblattbedingungen unterbrochen. Eine Sicherung ersetzt keinen schnellen Pack-Kurzschlussschutz. Kontinuierlich maximal 0,5 A als Geräte-Auslegungsgrenze; Temperatur-Derating des Fertigteils berücksichtigen.

Q1 hat maximal 45 mΩ bei VGS = −2,5 V (25 °C), somit 22,5 mV und 11,3 mW bei 0,5 A. Im Fehlerfall sind etwa 8,46 V zwischen positiv gespeister Systemseite und negativem Akku möglich: unter 20 V VDS von Q1 und 50 V von Q2. Die Gates liegen innerhalb ±10 V bzw. ±20 V, soweit die dokumentierten Anschlusszustände eingehalten werden. Temperaturabhängiger RDS(on), Pack-Leitungen und Schutzplatine kommen hinzu.

## Regler, Kondensatoren und Wärme

U3 **XC6220B331PR-G**: 3,3 V, SOT-89-5, bis 1 A, interne Entladung beim Abschalten. Das PR-Pinout unterscheidet sich ausdrücklich vom SOT-25-Typ: **1 CE, 2 GND/Tab, 3 NC, 4 VIN, 5 VOUT**. Genau dieses Pinout ist im lokalen Symbol umgesetzt. SW1 legt CE fest auf VSYS oder GND, R13 = 1 MΩ verhindert Schweben beim Umschalten. CE verträgt die maximal 4,5 V an VSYS. Die Regler-Eingangsbetriebsgrenze beträgt 6 V, absolut 6,5 V.

Die Ausgangsgenauigkeit beträgt im schnellen Modus ±1 %, im Sparmodus ±2 %: im letzteren Fall 3,234…3,366 V vor weiteren dynamischen Effekten. Der ESP32 benötigt 3,0…3,6 V. Die Referenz-Stabilitätsbeschaltung des LDO verwendet 10 µF an Ein- und Ausgang. C7 wurde so orientiert, dass sein Versorgungspad unmittelbar neben dem Regler-Eingang liegt; C9 sitzt am Ausgang. R14 = 0 Ω trennt für Messungen die gesamte geschaltete 3V3-Last ab.

### Wirksame Kapazität

C3…C11 verwenden konkret **TDK C3216X5R1C226M160AB**, 22 µF, 16 V, X5R, ±20 %, 1206. C3/C4 stützen BAT, C5/C6 VSYS am Lader, C7/C8 den LDO-Eingang, C9/C10 den LDO-Ausgang; C11 stützt das Modul lokal. Die offiziellen Produktdaten führen die Teilenummer als Production. Sie ist kein ungeprüfter Platzhalter für beliebige 22-µF-Kondensatoren.

Für jedes 44-µF-Paar gilt als Berechnungsgerüst:

`Ceff = 44 µF × 0,80 × 0,85 × k(DC-Bias, Alterung, Messbedingung)`.

Bei k = 0,50 bleiben 14,96 µF. Damit sind ≥10 µF am LDO erreichbar, **sofern k tatsächlich mindestens 0,50 beträgt**. Die rechnerische Grenzbedingung für 10 µF liegt bei k ≥0,335. Das Charakterisierungsblatt ist eine typische Kurve und kein garantierter Serien-Minimalwert. Eine exakt abgelesene Retention wird hier nicht als gemessen ausgegeben. Vor Freigabe: Kurve mit dem Hersteller/Fertiger bestätigen und effektive Kapazität bei 4,5 V bzw. 3,3 V samt Temperatur-/Alterungsreserve qualifizieren. BAT und OUT müssen mindestens 4,7 µF wirksam behalten; Modul lokal mindestens 10 µF als Entwurfsziel.

100 nF: TDK C2012X7R1H104K085AA, 50 V, X7R. 1 µF: TDK C2012X7R1E105K125AB, 25 V, X7R. Die nicht bestückten USB-Kondensatoren sind KEMET C0805C180J5GACTU, 18 pF/50 V/C0G. Kein Ersatz allein nach Nennkapazität.

### Verlustleistung und Unterspannung

Beispiel BQ: VIN=5,25 V, VBAT=3,0 V, ICHG=0,159 A und ISYS=0,30 A ergeben grob `(5,25−3,0)×0,159 + (5,25−4,4)×0,30 = 0,613 W`, ohne kleine Zusatzverluste. 44,5 K/W aus der Datenblatt-Testplatine entsprächen etwa 27 K Erwärmung; **dieser Wärmewiderstand ist nicht für das eigene Zweilagenlayout garantiert**. Das Exposed Pad ist mit einer thermischen Durchkontaktierung und einer zusätzlichen Massebrücke an die Rückseite angeschlossen. Wärmebild/Temperaturmessung im Gehäuse ist erforderlich.

Beim LDO ergibt VSYS=4,5 V und IOUT=0,5 A ungefähr 0,60 W. Die im Datenblatt für SOT-89-5 angegebenen 1,3 W gelten nur unter dessen definierten Leiterplattenbedingungen und bei 25 °C. Die gefüllten Masseflächen und der Tab dienen der Wärmeabfuhr. Abnahme: dauernd unter 100 °C berechnete/gemessene Sperrschichttemperatur bei der vorgesehenen Umgebung; keine thermische Regelung im Normalbetrieb. Die 1-A-Nennangabe ist keine Freigabe für 1 A Dauerlast im geschlossenen Gerät.

Ein LDO kann bei leerem Akku keine 3,3 V hochsetzen. Sicherung, Q1, BQ-Batteriepfad, Leiterbahnen und Dropout reduzieren die Spannung. Firmware soll bei etwa **3,6 V unter definierter Last** warnen/abschalten; dieser Startwert ist am Pack unter den höchsten Lastimpulsen zu kalibrieren. Der Pack-UV-Schutz bleibt die unabhängige letzte Abschaltung. Kein Anspruch auf vollständige Nutzung der nominellen Akkukapazität.

## GPIOs, Start und USB

| GPIO | Modul-Pad | Rev-B-Funktion | Start-/Schlafanforderung |
|---|---:|---|---|
| 0 | 18 | BAT_ADC | ADC1, kalibrieren; Eingang nicht als Ausgang konfigurieren. |
| 1 | 17 | BUZZ_GATE | LOW, bevor PWM gestartet wird; LOW im Schlaf. |
| 2 | 16 | SUSPEND_N | 10-kΩ-Pullup; HIGH hält BQ EN2 über Q7 LOW. Strap wird nicht von einem externen Kabel belastet. |
| 3 | 15 | BUTTON | RTC-fähiger Wake-up-Eingang, aktiv LOW. |
| 4 | 3 | SCK_M | Über U5 und 220 Ω zum OLED. |
| 5 | 4 | MOSI_M | Über U5 und 220 Ω zum OLED. |
| 6 | 5 | RES_M | Über U5 und 220 Ω zum OLED-Reset. |
| 7 | 6 | DC_M | Über U5 und 220 Ω zum OLED-DC. |
| 8 | 7 | CS_INVERT | 10-kΩ-Pullup. HIGH bedeutet physisches CS LOW; in der Firmware invertieren. |
| 9 | 8 | BOOT_N | 10-kΩ-Pullup; TP8 nach GND und Reset für Download. |
| 10 | 10 | OLED_EN | 100-kΩ-Pulldown; LOW = OLED und U5 aus. |
| 18 / 19 | 13 / 14 | USB D− / D+ | Native USB-Serial-JTAG-Funktion erhalten. |
| 20 | 11 | USB_500 / EN1 | Pulldown; HIGH erst nach erlaubter USB-Enumeration. |
| 21 | 12 | LED_N | Aktive LOW-LED. ROM-UART-Startausgaben dürfen höchstens die LED blinken lassen. |

GPIO21 ist ausdrücklich kein Ladecontroller-Eingang: ROM-Ausgaben hätten EN2 sonst beim Start umgeschaltet. Q7 und R38 invertieren stattdessen GPIO2. R38=100 kΩ liefert bei 3,234 V noch 18,3 µA bis zur EN2-VIH-Schwelle von 1,4 V und übertrifft damit den Datenblatt-Eingangsstrom von 10 µA. R22 bleibt unbestückt. EN2 LOW, wenn 3V3 aus ist, wird durch den internen Pulldown hergestellt.

USB-Suspend: zuerst GPIO20 HIGH, dann GPIO2 LOW → EN1=EN2=HIGH. Resume: zuerst GPIO2 HIGH, danach den ausgehandelten EN1-Zustand setzen. Sleep mit aktivem USB ist gesondert zu behandeln; GPIO-Zustände halten und Host-Suspend beachten. Keine UART-Ausgaben auf GPIO20 umkonfigurieren. Die Hardware allein beweist keine USB-Stromkonformität der vorhandenen Software.

EN/Reset: R16=10 kΩ, C13=1 µF, nominell 10 ms. Sauberen Anstieg und Brownout-Reset unter Last messen. Straps GPIO2/8/9 sind lokal definiert. U1 enthält Quarz und Flash; diese werden nicht extern nachgebildet.

## USB-C, Überspannung und Layout

J1 verwendet die eindeutig dokumentierte GCT-Belegung einschließlich der doppelten USB2-Pins. A6/B6 sind D+, A7/B7 D−; beide Steckerorientierungen sind elektrisch verbunden. SBU bleibt NC. Schirm und GND sind niederimpedant an die PCB-Masse angeschlossen. CC1 und CC2 besitzen je 5,1 kΩ ±1 % nach GND. D3 schützt beide CC-Leitungen. Es gibt keinen USB-PD-Controller und keine Anforderung einer Spannung über 5 V.

D1 SMBJ6.0A schützt gegen begrenzte VBUS-Transienten. Die spezifizierte 10/1000-µs-Klemmspannung von 10,3 V bei Nennimpulsstrom liegt unter der absoluten 28-V-IN-Grenze des BQ24074. Der BQ sperrt bei anhaltender Überspannung um 10,5 V. TVS-Pulsleistung, Wiederholrate, Sicherung und Quellstrom sind trotzdem gemeinsam zu prüfen. Die TVS darf nicht als unbegrenzt belastbarer Schutz vor einem dauerhaft falschen Netzteil verstanden werden. Die Versorgungskondensatoren direkt an VBUS sind 25 bzw. 50 V spezifiziert.

D2 TPD2E2U06DCKR sitzt bei den USB-Pins. Wichtig: SC70-3 hat **1 IO1, 2 IO2, 3 GND** und keinen Versorgungspin. Die geringe Kapazität ist für USB geeignet. R3/R4 =22 Ω liegen modulnah; C17/C18 bleiben DNP. Schutzbauteil-IEC-Werte sind kein ESD-Prüfzeugnis für das gesamte Gerät.

Das PCB besitzt 90 × 60 mm Außenmaß, zwei Kupferlagen und einen als Annahme dokumentierten 1,6-mm-Aufbau. Die Antennen-Sperrzone ist in der Modulbibliothek auf **F.Cu und B.Cu** wirksam; die Antenne ragt über die obere Kante. Das übrige Layout nutzt beidseitige gefüllte GND-Flächen und zusätzliche Massevias. Jede verbleibende Insel wird vom abschließenden KiCad-DRC als reale Verbindung geprüft, nicht nur optisch vermutet.

Der breite Hauptabschnitt des USB-Paars hat **1,50 mm Leiterbreite und 0,25 mm Abstand**, mit durchgehender Rückseitenreferenz darunter. Bei h=1,51 mm, εr=4,2 und t=35 µm ergibt eine einfache Microstrip-Näherung eine differentielle Impedanz in der Größenordnung **86…90 Ω**. Das ist eine Vorabschätzung, kein Feldlöser-Nachweis. An Widerständen, Schutzbauteil und Steckerkreuzung existieren schmale Übergänge und ein kurzer Lagenwechsel für die duplizierten D+-Kontakte. Die gesamte Strecke ist deshalb nicht pauschal als kontrollierte 90-Ω-Leitung freigegeben. Fertiger-Aufbau, Rückstrompfad, Engstellen und USB-FS-Signalform müssen vor Bestellung/Abnahme geprüft werden; bei geändertem Aufbau Breite/Abstand anpassen und alle Enddaten neu erzeugen.

Normale Leiterbahnen: überwiegend 0,20…0,30 mm; feine Pin-Ausleitungen 0,15 mm. Grundregeln: 0,15 mm Kupferabstand, 0,30 mm Kupfer zur Kante, kleinste durchgehende Vias 0,50/0,25 mm. Der ringförmige Restring dieser kleinsten Vias beträgt nominal 0,125 mm und muss beim Fertiger bestätigt werden. Es handelt sich nicht um Laser-Microvias. Belastbare Strompfade werden zusätzlich unter Last auf Spannungsfall und Temperatur geprüft.

### Rechnerische Prüfung der Leiterbahnen

Der aus dem End-PCB ausgelesene VBAT-Leiterzug enthält insgesamt 54,97 mm mit 0,15 mm Breite. Selbst wenn konservativ die gesamte verzweigte Länge in Serie angenommen wird, ergibt sich bei 35 µm Kupfer und ρ=0,0175 Ω·mm²/m etwa 0,183 Ω: höchstens rund 92 mV und 46 mW bei 0,5 A, vor Temperaturzuschlag. Die reale Hauptstromstrecke ist kürzer; Rückleiter, Vias, Sicherung und BQ-Schalter kommen hinzu. Dieser Spannungsabfall ist beim Unterspannungs-Abschaltpunkt zu berücksichtigen.

Als grobe thermische Vorprüfung nach der in [TI SNVA766, April 2017, S.16, Gl.3](https://www.ti.com.cn/cn/lit/pdf/snva766) wiedergegebenen IPC-2221-Näherung gilt für Außenlagen `I = 0,048 × ΔT^0,44 × A^0,725`, mit A in mil². 0,15×0,035 mm ergeben 8,138 mil² und bei 0,5 A etwa 6,5 K rechnerische Eigenerwärmung; bei 0,25 mm etwa 2,8 K. Dies ist keine thermische Simulation des Gehäuses und kein Kurzschlussnachweis. Kupfer-Enddicke, Ätztoleranzen und Via-Metallisierung muss der Fertiger bestätigen. Die Geräte-Dauerlast bleibt auf 0,5 A begrenzt; 1 A Sicherungsnennstrom ist keine 1-A-Betriebsfreigabe.

## OLED, Taster und Piezo

TPS22919 schaltet OLED_3V3 und U5 gemeinsam; R29=100 Ω verbindet QOD zur Ausgangsschiene. R27 zieht CS nur auf diese geschaltete Schiene. U5 ist **Nexperia 74LVC125AD,118**, SO14/SOIC-14, mit explizit spezifiziertem IOFF für VCC=0. Kein beliebiger 74HC125 und kein ungeprüfter anderer 74LVC125A-Hersteller als Ersatz. U5-Pinout: OE 1/4/10/13 an GND; A 2/5/9/12 vom ESP; Y 3/6/8/11 zu den vier Serienwiderständen; 7 GND, 14 OLED_3V3. C19=100 nF stützt U5.

R23…R26=220 Ω begrenzen bei einem Kurzschluss ungefähr auf 15,5 mA je Leitung und zusammen unter 100 mA Gehäusestrom. Bei angenommener Kabel-/Eingangskapazität von 100 pF ist RC≈22 ns. Mit zunächst 1 MHz SPI beginnen; schnellere Übertragung erst nach Messung am realen Kabel. GND auf J3.1 und J3.4 führt den Rückstrom.

Einschalten: sichere GPIO-Pegel setzen, OLED_EN HIGH, Versorgung einschwingen lassen, physisches CS zunächst HIGH setzen (GPIO8 LOW), Display-Reset ausführen, danach SPI. Schlaf: Übertragung beenden, vier Buffer-Eingänge LOW, GPIO8 HIGH, OLED_EN LOW; notwendige Hold-Zustände setzen. Der Puffer schützt auch vor direkten GPIO-Pegeln während des ROM-Starts bei ausgeschalteter OLED-Schiene. Leckströme bleiben endlich und werden im Budget berücksichtigt.

Taster: R33=100 kΩ Pullup, R34=1 kΩ am Kabelpfad, C15=100 nF. Nominelle Entprellzeit etwa 10 ms; der gedrückte Taster benötigt etwa 33 µA. D7 liegt am externen Signal. Entprellung und Wake-up ergänzend in Software prüfen.

Piezo: Q6 **DMN2056U-7**, bei 2,5 V spezifizierter Logic-Level-MOSFET. Der ESP liefert nur Gate-Ladung. R35=100 kΩ hält das Gate LOW; R36=100 Ω begrenzt den Strom, R37=1 kΩ entlädt den Piezo nach Abschalten. Statischer Strom bei eingeschaltetem Q6 ungefähr 3,3/1100 =3 mA; ein Kurzschluss des P-Knotens nach GND erzeugt bis etwa 34 mA. R36 dissipiert dann etwa 0,114 W bei 3,366 V und −1 % Toleranz, knapp unter 0,125 W bei den vorgesehenen Umgebungstemperaturen. D12 BAV19W klemmt negative Differenzspannung, D8 beide Kabeladern gegen GND. Die erreichbare Lautstärke ist ohne Piezo-Modell nicht berechenbar; kein Schallpegel wird behauptet.

Lade-LED D10: aus VSYS über 3,3 kΩ, typisch unter 1 mA beim Laden. Lauf-LED D11: 3,3 kΩ, GPIO21 aktiv LOW, im Schlaf HIGH. LED-Vorwärtsspannung und Sichtbarkeit bei kleinem Strom sind am Aufbau zu prüfen.

## ADC und Ruhestrombudget

Q4/Q5 schalten den High-Side-Messzweig zusammen mit 3V3. R31=1 MΩ, R32=330 kΩ: nominal 0,24812 × VBAT, bei 4,23 V und ±1 % Widerständen maximal **1,0655 V**. C16=100 nF; Thevenin-Widerstand etwa 248 kΩ, Zeitkonstante 24,8 ms. Nach Einschalten mindestens etwa 150 ms warten. Eine ADC-Dämpfung wählen, deren kalibrierter Bereich 1,066 V sicher umfasst, etwa 2,5 dB oder 6 dB; ADC1-Kalibrierung und Messfehler bei hohem Quellwiderstand verifizieren. Zwei-Punkt-Messung mit Multimeter; keine lineare Prozentanzeige allein aus Akkuspannung.

Budget für Akku-only, OLED aus, kein gedrückter Taster, LEDs aus, GPIO20 LOW und GPIO2 HIGH:

| Anteil | Ansatz bei 25 °C | Grenze / Einschränkung |
|---|---:|---|
| ESP32-Modul Deep Sleep | 5 µA typisch | Kein garantierter Gesamt-Maximalwert für die vorhandene Firmware. |
| BQ BAT-Ruhestrom | 4,3 µA typisch | Bis 6,5 µA unter den angegebenen Bedingungen; externe Logikeingangsströme separat berücksichtigen. |
| XC6220 Sparmodus | 8 µA typisch | 18 µA bei Datenblatt-Testbedingungen; High-Speed-Modus typ. 50 µA. |
| ADC-Teiler + Q4-Gatepfad | ca. 7,4 µA bei 4,2 V | Widerstands- und Leckstromtoleranzen. |
| Q7/R38 | ca. 33 µA | Bewusster Preis der strap-sicheren Ladecontroller-Ansteuerung. |
| RUN_EN/R13 | ca. 4,2 µA | Dazu CE-Eingangsleckstrom. |
| TPS22919 aus | 0,002 µA typisch | Bis 0,8 µA über den spezifizierten Temperaturbereich. |
| U5 bei abgeschalteter Schiene | ca. 0,1 µA je aktiv getriebenem Eingang typisch | IOFF bis 10 µA je Pin bis 85 °C. Vier GPIO-Eingänge können im konservativen Budget bis 40 µA beitragen. |
| MLCC-Leckströme | Nicht als Null angenommen | 22-µF-Typ: ≥4 MΩ; mehrere parallel geschaltete Kondensatoren zusammen im µA-Bereich. |
| FETs, ESD, LED-Status, Verschmutzung | Zusätzliche Reserve | Temperatur und reale Fertigung beeinflussen Leckströme. |
| Akku-Schutzplatine / Selbstentladung | Unbekannt | Muss aus dem realen Pack-Datenblatt bzw. Messung kommen. |

Die sichtbaren typischen Grundanteile ergeben rund **62 µA plus Leck-/Pack-Anteile**. Ein Ziel um 100 µA ist damit plausibel, aber **nicht garantiert**. Aus den Einzel-Maximalwerten lässt sich kein belastbarer Gesamtwert unter 100 µA beweisen. Mit aktivem USB-Suspend bzw. gedrücktem Taster steigt das Budget. Ein Vollsystem-Messwert ist zwingend.

OFF über SW1 trennt nicht den Akku galvanisch. BQ, LDO-Standby, CE-Pullup-Eingangspfad, BAT/SYS-Kondensatoren und der Pack-Schutz bleiben relevant. Weder „0 µA“ noch „5 µA Gesamtverbrauch“ sind zulässige Angaben. Für Lagerung Akku abstecken; Entnahme nur mit geprüftem Steckverbinder und ausgeschaltetem USB.

## Messzugang und Prüfgrenzen

TP1 VBUS; TP2 VBAT; TP3 VSYS; TP4 3V3_REG; TP5 3V3; TP6 GND; TP7 RESET_N; TP8 BOOT_N; TP9 BAT_ADC; TP10 USB_GOOD_N; TP11 CHG_DISABLE; TP12 NTC; TP13/14 GND; TP15 BUTTON; TP16 ISET. TP10 ist Open Drain und braucht für eine Messung einen externen Pullup, vorzugsweise 100 kΩ an 3V3. Niemals einen 5-V-Logikanalysator-Pullup an einen ESP-Pin anlegen.

R14 herausnehmen und ein geeignetes Strommessgerät zwischen dessen Pads setzen, um den geschalteten Systemstrom zu messen. Der Gesamt-Akkustrom einschließlich Lader/Pack muss zusätzlich in der J2-Zuleitung gemessen werden. DNP-Testpads sind blanke Pads und keine Keystone-Steckteile.

ERC, DRC und Netzlistenvergleich prüfen CAD-Konsistenz. Sie ersetzen keine Zellfreigabe, thermische Messung, Impedanzprüfung, EMV-/ESD-Prüfung oder Firmware-Abnahme. Alle ausstehenden Prüfungen sind in der Checkliste bewusst unmarkiert.
