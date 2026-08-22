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
$KICAD pcb drc --severity-error --schematic-parity --refill-zones --save-board \
       --exit-code-violations -o ausgabe/drc.rpt flappy-esp32c3.kicad_pcb

echo "== 7/8  Fertigungsunterlagen =="
mkdir -p fertigung ausgabe
$KICAD pcb export gerbers --layers "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Paste,Edge.Cuts" \
       --subtract-soldermask --use-drill-file-origin -o fertigung flappy-esp32c3.kicad_pcb
$KICAD pcb export drill --format excellon --drill-origin plot --excellon-separate-th \
       --generate-map --map-format gerberx2 -o fertigung/ flappy-esp32c3.kicad_pcb
$KICAD pcb export pos --format csv --units mm --side front --use-drill-file-origin \
       -o fertigung/flappy-esp32c3-bestueckung.csv flappy-esp32c3.kicad_pcb
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
