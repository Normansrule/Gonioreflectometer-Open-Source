#!/usr/bin/env bash
# FYSETC E4 (FluidNC) from the terminal [R81][R24][R25].
#   bash scripts/e4.sh flash               firmware + file system (USB), the FluidNC release pinned in
#                                          firmware/fluidnc/FLUIDNC_VERSION (config.yaml was written for it)
#   bash scripts/e4.sh wifi "SSID" "PASS"  join your WiFi (USB)
#   bash scripts/e4.sh config [HOST]       upload firmware/fluidnc/config.yaml (WiFi; default fluidnc.local)
#   bash scripts/e4.sh test                motor test (USB or WiFi, per machine.yaml)
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
    pip install -q esptool pyserial
    TAG=${FLUIDNC_TAG:-$(tr -d '[:space:]' < firmware/fluidnc/FLUIDNC_VERSION)}   # pinned, never "latest":
    # a new FluidNC major version can rename config keys; to try another release: FLUIDNC_TAG=vX.Y.Z bash scripts/e4.sh flash
    mkdir -p .fluidnc && cd .fluidnc
    curl -fLO "https://github.com/bdring/FluidNC/releases/download/$TAG/fluidnc-$TAG-posix.zip"
    rm -rf "fluidnc-$TAG-posix" && unzip -q "fluidnc-$TAG-posix.zip" -d "fluidnc-$TAG-posix"
    cd "fluidnc-$TAG-posix"; cd "$(dirname "$(find . -name install-wifi.sh | head -1)")"
    echo "FluidNC $TAG. Close the terminal it opens with Ctrl+]"
    bash install-wifi.sh
    bash install-fs.sh ;;
  wifi)
    pip install -q -e "./software[hw]"
    og send "\$Sta/SSID=$2" "\$Sta/Password=$3" '$WiFi/Mode=STA>AP'
    echo "Now press the E4 reset button. Its IP prints on boot; fallback hotspot FluidNC / 12345678 at 192.168.0.1" ;;
  config)
    HOST=${2:-fluidnc.local}
    curl -fF "file=@firmware/fluidnc/config.yaml;filename=/config.yaml" "http://$HOST/files"
    echo; echo "Uploaded. Press the E4 reset button, then: bash scripts/e4.sh test" ;;
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
    og sleep ;;               # motors off
  *) sed -n 2,7p "$0"; exit 1 ;;
esac
