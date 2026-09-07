# Projektbibliotheken

Symbole und Footprints sind projektlokal über `${KIPRJMOD}` aufgelöst. Ausgangsbasis: mit KiCad 10.0.5 gelieferte offizielle Bibliotheken. Angepasst wurden insbesondere das XC6220-SOT-89-5-Pinout, der dreipolige TPD2E2U06, der einteilige 74LVC125A-Symbolblock sowie der auf tatsächlich bedruckbare Fläche begrenzte ESP-Antennen-Bestückungsdruck.

KiCad-Bibliotheksmaterial: Creative Commons Attribution-ShareAlike 4.0 mit KiCad-Ausnahme für elektronische Entwürfe; individuelle Copyright-Hinweise bleiben in den Modellen erhalten. Quellen und Lizenz: https://gitlab.com/kicad/libraries/kicad-footprints und https://gitlab.com/kicad/libraries/kicad-packages3D/-/blob/master/LICENSE.md . Die Nutzung der Bibliothek erzwingt keine Veröffentlichung des Elektronikprojekts.

Die kopierten Standardmodelle sind lediglich Geometriehilfen. Das installierte KiCad enthielt kein VQFN-16-EP1.6- und kein SOT-89-5-Modell. U2 verwendet deshalb das geometrisch ähnliche WQFN-16-EP1.6-Modell; U3 einen in diesem Projekt erstellten rechteckigen Hüllkörper mit fünf Anschlüssen. Höhe, Anschlussform und Verpackung sind am Herstellerteil zu bestätigen. `custom/SOT-89-5-envelope.step` ist ausdrücklich kein zertifiziertes Hersteller-CAD-Modell. Unbestückte Bauteile sind im STEP-Export ausgeschlossen.
