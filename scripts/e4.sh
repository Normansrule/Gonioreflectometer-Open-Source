#!/usr/bin/env bash
# FYSETC E4 (FluidNC) from the terminal [R81][R24][R25].
#   bash scripts/e4.sh flash               firmware + file system (USB)
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
    TAG=$(curl -fsSL https://api.github.com/repos/bdring/FluidNC/releases/latest | python3 -c "import json,sys;print(json.load(sys.stdin)['tag_name'])")
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
  test)
    pip install -q -e "./software[hw]"
    og send '$I' '?'          # firmware info + status
    og home                   # optical homing of installed axes
    og move M4=60             # light arm to 60 deg
    og move M4=90 M3=45 || echo "M3 not installed yet (phase 5)"
    og status
    og sleep ;;               # motors off
  *) sed -n 2,7p "$0"; exit 1 ;;
esac
