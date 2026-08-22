#!/bin/sh
# Erzeugt Schaltplan, Layout und Fertigungsunterlagen neu und prueft sie.
# Einzige Wahrheitsquelle ist gen/design.py (Bauteile und Netzliste).
set -e
KICAD=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli
HIER=$(cd "$(dirname "$0")" && pwd)
cd "$HIER/gen"

echo "== 1/7  Bibliotheken =="
python3 mk_sym.py
python3 mk_fp.py

echo "== 2/7  Schaltplan =="
python3 mk_sch.py

python3 mk_sch.py layout_sch_wired -verdrahtet

echo "== 3/7  Platzierung pruefen =="
python3 chk_place.py

echo "== 4/7  Verdrahten =="
python3 autoroute.py
python3 mk_labels.py
python3 mk_pcb.py

cd "$HIER"
echo "== 5/7  ERC und Netzlistenabgleich =="
$KICAD sch erc --severity-all --exit-code-violations -o ausgabe/erc.rpt flappy-esp32c3.kicad_sch
$KICAD sch export netlist --format kicadsexpr -o ausgabe/netzliste.net flappy-esp32c3.kicad_sch
python3 gen/check_net.py ausgabe/netzliste.net
$KICAD sch erc --severity-all --exit-code-violations -o ausgabe/erc_verdrahtet.rpt flappy-esp32c3-verdrahtet.kicad_sch
$KICAD sch export netlist --format kicadsexpr -o ausgabe/netzliste_verdrahtet.net flappy-esp32c3-verdrahtet.kicad_sch
python3 gen/check_net.py ausgabe/netzliste_verdrahtet.net

echo "== 6/7  DRC, Abgleich Schaltplan/Layout =="
$KICAD pcb drc --severity-error --schematic-parity --refill-zones --save-board \
       --exit-code-violations -o ausgabe/drc.rpt flappy-esp32c3.kicad_pcb

echo "== 7/7  Fertigungsunterlagen =="
mkdir -p fertigung ausgabe
$KICAD pcb export gerbers --layers "F.Cu,B.Cu,F.SilkS,B.SilkS,F.Mask,B.Mask,F.Paste,Edge.Cuts" \
       --subtract-soldermask --use-drill-file-origin -o fertigung flappy-esp32c3.kicad_pcb
$KICAD pcb export drill --format excellon --drill-origin plot --excellon-separate-th \
       --generate-map --map-format gerberx2 -o fertigung/ flappy-esp32c3.kicad_pcb
$KICAD pcb export pos --format csv --units mm --side front --use-drill-file-origin \
       -o fertigung/flappy-esp32c3-bestueckung.csv flappy-esp32c3.kicad_pcb
$KICAD sch export pdf -o ausgabe/schaltplan.pdf flappy-esp32c3.kicad_sch
$KICAD sch export pdf -o ausgabe/schaltplan_verdrahtet.pdf flappy-esp32c3-verdrahtet.kicad_sch
$KICAD pcb export pdf --layers "F.Cu,F.SilkS,Edge.Cuts" --mode-single -o ausgabe/layout_oben.pdf flappy-esp32c3.kicad_pcb
$KICAD pcb export pdf --layers "B.Cu,B.SilkS,Edge.Cuts" --mirror --mode-single -o ausgabe/layout_unten.pdf flappy-esp32c3.kicad_pcb
$KICAD sch export bom --fields "Reference,Value,Footprint,\${QUANTITY},Description" \
       --labels "Referenz,Wert,Footprint,Anzahl,Beschreibung" \
       --group-by "Value,Footprint" --field-delimiter ";" -o ausgabe/stueckliste.csv flappy-esp32c3.kicad_sch
$KICAD pcb render --side top --width 1600 --height 1100 --quality high \
       --background opaque -o ausgabe/3d_oben.png flappy-esp32c3.kicad_pcb

echo
echo "Fertig. Keine ERC-Verstoesse, keine DRC-Fehler, Netzliste stimmt mit gen/design.py ueberein."
