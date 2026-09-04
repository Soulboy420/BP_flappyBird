#!/bin/sh
# Erzeugt Schaltplan, Layout und Fertigungsunterlagen neu und prueft sie.
# Einzige Wahrheitsquelle ist gen/design.py (Bauteile und Netzliste).
set -e
KICAD=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
HIER=$(cd "$(dirname "$0")" && pwd)
cd "$HIER/gen"

echo "== 1/8  Bibliotheken =="
python3 mk_sym.py
python3 mk_fp.py

echo "== 2/8  Schaltplan =="
python3 mk_sch.py

echo "== 3/8  Platzierung pruefen =="
python3 chk_place.py

echo "== 4/8  Verdrahten =="
python3 autoroute.py
python3 mk_labels.py
python3 mk_pcb.py

cd "$HIER"
echo "== 5/8  ERC und Netzlistenabgleich =="
$KICAD sch erc --severity-all --exit-code-violations -o ausgabe/erc.rpt flappy-esp32c3.kicad_sch
$KICAD sch export netlist --format kicadsexpr -o ausgabe/netzliste.net flappy-esp32c3.kicad_sch
python3 gen/check_net.py ausgabe/netzliste.net

echo "== 6/8  Masseflaechen fuellen, DRC, Abgleich Schaltplan/Layout =="
# --refill-zones --save-board ist zwingend: ohne den Fuellschritt enthaelt die
# Platinendatei keine Masseflaeche, und die Gerber waeren ohne sie.
# KiCad schreibt die Datei dabei in seinem eigenen Format zurueck.
# Befund M-11: --severity-error unterdrueckte Warnungen wie isolated_copper.
# Der Bericht enthaelt sie jetzt; Abbruch weiterhin nur bei echten Fehlern.
$KICAD pcb drc --severity-all --schematic-parity --refill-zones --save-board \
       -o ausgabe/drc.rpt flappy-esp32c3.kicad_pcb
grep -q "Found 0 DRC violations" ausgabe/drc.rpt || \
  echo "  Hinweis: ausgabe/drc.rpt enthaelt Warnungen - bitte durchsehen."
$KICAD pcb drc --severity-error --schematic-parity \
       --exit-code-violations -o /dev/null flappy-esp32c3.kicad_pcb

echo "== 7/8  Fertigungsunterlagen =="
mkdir -p fertigung ausgabe
$KICAD pcb export gerbers --layers "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Paste,Edge.Cuts" \
       --subtract-soldermask --use-drill-file-origin -o fertigung flappy-esp32c3.kicad_pcb
$KICAD pcb export drill --format excellon --drill-origin plot --excellon-separate-th \
       --generate-map --map-format gerberx2 -o fertigung/ flappy-esp32c3.kicad_pcb
$KICAD pcb export pos --format csv --units mm --side front --use-drill-file-origin \
       -o fertigung/flappy-esp32c3-bestueckung.csv flappy-esp32c3.kicad_pcb
# Befund M-11: Wer die Generatoren ohne den Fuellschritt laufen laesst, liefert
# Gerber ohne Massefläche. Ein Flaechenobjekt (G36) muss vorhanden sein.
for datei in fertigung/flappy-esp32c3-F_Cu.gtl fertigung/flappy-esp32c3-B_Cu.gbl; do
  grep -q 'G36\*' "$datei" || {
    echo "FEHLER: $datei enthaelt keine Kupferflaeche - Fuellschritt fehlt."; exit 1; }
done
$KICAD sch export pdf -o ausgabe/schaltplan.pdf flappy-esp32c3.kicad_sch
$KICAD pcb export pdf --layers "F.Cu,F.SilkS,Edge.Cuts" --mode-single -o ausgabe/layout_oben.pdf flappy-esp32c3.kicad_pcb
$KICAD pcb export pdf --layers "B.Cu,B.SilkS,Edge.Cuts" --mirror --mode-single -o ausgabe/layout_unten.pdf flappy-esp32c3.kicad_pcb
$KICAD sch export bom --fields "Reference,Value,Footprint,\${QUANTITY},Description" \
       --labels "Referenz,Wert,Footprint,Anzahl,Beschreibung" \
       --group-by "Value,Footprint" --field-delimiter ";" -o ausgabe/stueckliste.csv flappy-esp32c3.kicad_sch
$KICAD pcb render --side top --width 1600 --height 1100 --quality high \
       --background opaque -o ausgabe/3d_oben.png flappy-esp32c3.kicad_pcb

echo "== 8/8  Pruefstand =="
python3 gen/tests.py

echo
echo "Fertig. ERC, DRC, Abgleich und Pruefstand ohne Beanstandung."
