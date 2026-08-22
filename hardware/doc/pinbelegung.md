# Pinbelegung ESP32-C3-WROOM-02-N4

Verbindlich für die Firmware (AP-B, AP-C). Modulpinnummern nach Espressif-Datenblatt
ESP32-C3-WROOM-02, Abschnitt „Pin Definitions".

| Modulpin | GPIO | Netz | Funktion | Bemerkung |
|---|---|---|---|---|
| 1 | – | `+3V3_MCU` | Versorgung | hinter der 0-Ω-Trennstelle R3 (Strommessung M3) |
| 2 | – | `EN` | Reset | R4 10 kΩ nach 3V3, C10 100 nF nach GND, Prüfpunkt TP6 |
| 3 | IO4 | `SCLK_MCU` | SPI-Takt zum Display | über R5 = 68 Ω auf J3-3 |
| 4 | IO5 | `MOSI_MCU` | SPI-Daten zum Display | über R6 = 68 Ω auf J3-4 |
| 5 | IO6 | `OLED_RES_MCU` | Display-Reset | über R7 = 68 Ω auf J3-5 |
| 6 | IO7 | `OLED_DC_MCU` | Display Daten/Befehl | über R8 = 68 Ω auf J3-6 |
| 7 | IO8 | `OLED_CS_MCU` | Display-Chipauswahl | über R9 = 68 Ω auf J3-7; **Strapping-Pin**, R16 = 10 kΩ hält ihn beim Start hoch |
| 8 | IO9 | `BOOT` | Downloadmodus | nur Prüfpunkt TP7; beim Reset nach GND ziehen erzwingt den Bootlader |
| 9 | – | `GND` | Masse | |
| 10 | IO10 | – | frei | nicht angeschlossen, am Modulrandkontakt abgreifbar |
| 11 | IO20 | – | frei (U0RXD) | Konsole läuft über USB-Serial-JTAG |
| 12 | IO21 | – | frei (U0TXD) | dito |
| 13 | IO18 | `USB_DM` | USB D− | über D1 (USBLC6-2SC6) auf J1-3 |
| 14 | IO19 | `USB_DP` | USB D+ | über D1 auf J1-4 |
| 15 | IO3 | `BTN` | Taster | RTC-fähig → weckt aus dem Tiefschlaf (F-13); Pull-up R10, C11, R11, R12 |
| 16 | IO2 | – | **Strapping-Pin** | R15 = 10 kΩ nach 3V3, sonst unbenutzt |
| 17 | IO1 | `BUZZ` | Piezo über LEDC | R13 = 100 Ω in Reihe zu LS1 |
| 18 | IO0 | `LED_G` | Betriebsanzeige | R14 = 1 kΩ, D4 grün; **muss im Tiefschlaf auf 0 gesetzt werden** |
| 19 | – | `GND` | Wärmepad | im Footprint mit 12 Vias zur Massefläche |

## Auswirkungen auf die Firmware

* **SPI:** SCLK/MOSI/CS liegen nicht auf den IO-MUX-Pins des FSPI. ESP-IDF schaltet
  automatisch auf die GPIO-Matrix um; bis etwa 40 MHz ist das unkritisch, die
  geplanten 8 MHz erst recht (Projektplan 5.6).
* **Tiefschlaf (NF-04, ≤ 200 µA):** vor dem Schlafen muss die Firmware
  1. dem SSD1306 `0xAE` (Display aus) senden — sonst zieht das Modul weiter ~11 mA,
  2. IO0 auf 0 setzen (Betriebs-LED aus, sonst 1,3 mA),
  3. die SPI-Pins definiert halten, damit der SSD1306-Eingang nicht floatet.
* **Aufwecken:** nur IO0…IO5 sind RTC-fähig. Der Taster liegt deshalb auf IO3.
* **Treiberstärke:** `gpio_set_drive_capability()` auf die kleinste ausreichende
  Stufe setzen (Projektplan 4.2 und 5.7).
* **Bootverhalten:** IO2 und IO8 werden von R15/R16 hochgehalten, IO9 hat den
  chipinternen Pull-up. Für den Downloadmodus TP7 beim Reset auf einen der
  Massepunkte legen.
