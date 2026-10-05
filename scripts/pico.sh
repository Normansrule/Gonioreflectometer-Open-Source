#!/usr/bin/env bash
# Pico button hub [R42]. First: hold BOOTSEL, plug in, drop the MicroPython .uf2
# (https://micropython.org/download/RPI_PICO/) onto the RPI-RP2 drive. Then:
#   bash scripts/pico.sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q mpremote pyserial
mpremote mip install ssd1306 || echo "no OLED driver (display optional)"
mpremote cp firmware/pico-hub/main.py :main.py
mpremote reset
sleep 2
python3 - <<'PY'
import glob, serial, time
port = (glob.glob("/dev/ttyACM*") + glob.glob("/dev/cu.usbmodem*"))[0]
with serial.Serial(port, 115200, timeout=1) as s:
    s.write(b"PING\n"); time.sleep(0.3); print(port, s.read(200).decode(errors="ignore").strip() or "no reply")
PY
echo "Press a button: run  opengonio panel"
