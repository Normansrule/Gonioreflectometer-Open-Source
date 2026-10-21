#!/usr/bin/env bash
# BTT SKR Pico V1.0 running grblHAL, over USB-C [C12][R83][R85].
#   bash scripts/controller.sh flash      how to put grblHAL on the board (drag and drop, no tools)
#   bash scripts/controller.sh settings   send firmware/grblhal/settings.txt, then list them back
#   bash scripts/controller.sh pins       print the board's pin / output-port map ($PINS) for machine.yaml lights
#   bash scripts/controller.sh test       motor test (the same steps as stage 02, per machine.yaml)
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT=$PWD
VENV=$ROOT/.venv
[ -d "$VENV" ] || python3 -m venv "$VENV"
. "$VENV/bin/activate"
og() { opengonio "$@"; }

case "${1:-}" in
  flash)
    cat <<'TXT'
1. Build the firmware in the grblHAL Web Builder: https://svn.io-engineering.com:8443/?driver=RP2040
   Board: "BTT SKR Pico 1.0".  Axes: 4 (X Y Z A).  Leave spindle and coolant off if the builder allows it
   (then the fan and heater outputs stay free as M62/M63 ports).  Download the .uf2 file.
2. Motor power OFF (e-stop pressed). Put the jumper cap on the board's BOOT pins, connect USB-C to the laptop,
   press RESET. A drive called RPI-RP2 appears.
3. Copy the .uf2 onto RPI-RP2. The board restarts by itself; the drive disappears.
4. Remove the BOOT jumper, press RESET. Then: bash scripts/controller.sh settings
TXT
    ;;
  settings)
    pip install -q -e "./software[hw]"
    mapfile -t LINES < <(sed -e 's/;.*//' -e 's/[[:space:]]*$//' firmware/grblhal/settings.txt | grep -v '^$')
    og send "${LINES[@]}"     # stops at the first 'error:': read it, fix the line, run again
    og send '$$' ;;
  pins)
    pip install -q -e "./software[hw]"
    og send '$PINS' ;;
  test)                       # any failed step stops the test (set -e): read the message, fix, run again
    pip install -q -e "./software[hw]"
    og send '$I' '?'          # firmware info + status
    og home                   # homing of installed axes (each move below re-homes and checks the end position)
    og move M4=60             # light arm to 60 deg
    if python3 -c "from opengonio.gantry.config import load_config; import sys; sys.exit('M3' not in load_config().active_axes)"; then
      og move M4=90 M3=45     # table, once M3 is installed (installed_phase in machine.yaml)
    else
      echo "M3 not installed (installed_phase in machine.yaml): table move skipped"
    fi
    og status
    og sleep ;;               # motors off ($SLP; leave with a reset)
  *) sed -n 2,6p "$0"; exit 1 ;;
esac
