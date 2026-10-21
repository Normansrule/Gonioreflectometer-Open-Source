#!/usr/bin/env python3
"""Download the open-licence 3D models (Adafruit_CAD_Parts: MIT; KiCad packages3D: CC-BY-SA 4.0 with the design
exception) into cad/open/. They are committed, so you only need this to refresh them.
    python tools/cad/fetch_open.py
SPDX-License-Identifier: GPL-3.0-or-later
"""
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "cad" / "open"
ADA = "https://raw.githubusercontent.com/adafruit/Adafruit_CAD_Parts/main/"
KICAD = "https://raw.githubusercontent.com/KiCad/kicad-packages3D/master/"   # mirror of gitlab.com/kicad/libraries/kicad-packages3D
OPEN = {   # file name in cad/open: (url, part IDs, licence)
    "STA-08_adafruit_592_microusb_cable.step": (ADA + quote("592 microUSB B Connector Cable/592 microUSB B Connector Cable.step"), "STA-08, CTL-04", "MIT (Adafruit)"),
    "SPC-01_adafruit_4698_as7341.step": (ADA + quote("4698 AS7341 Light Color Sensor/4698 AS7341 Light Color Sensor.step"), "SPC-01", "MIT (Adafruit)"),
    "LAR-04_adafruit_1253_gt2_20t_pulley_8mm_bore.step": (ADA + quote("1253 Aluminum Timing Pulley/1253 Aluminum Timing Pulley.step"), "LAR-04, TBL-03, TLT-03 (bore 8 mm: set 5 mm in Onshape)", "MIT (Adafruit)"),
    "CTL-06_kicad_JST_XH_B3B_header.step": (KICAD + "Connector_JST.3dshapes/JST_XH_B3B-XH-A_1x03_P2.50mm_Vertical.step", "CTL-06 (SKR Pico endstop socket)", "CC-BY-SA 4.0 + exception (KiCad)"),
    "CTL-11_kicad_JST_XH_B4B_header.step": (KICAD + "Connector_JST.3dshapes/JST_XH_B4B-XH-A_1x04_P2.50mm_Vertical.step", "CTL-11 (SKR Pico motor socket)", "CC-BY-SA 4.0 + exception (KiCad)"),
    "CTL-11_kicad_JST_PH_B6B_header.step": (KICAD + "Connector_JST.3dshapes/JST_PH_B6B-PH-K_1x06_P2.00mm_Vertical.step", "CTL-11 (motor socket)", "CC-BY-SA 4.0 + exception (KiCad)"),
}

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    bad = 0
    for name, (url, ids, lic) in OPEN.items():
        dst = OUT / name
        ok = subprocess.call(["curl", "-fsSL", "-o", str(dst), url]) == 0
        print(("got  " if ok else "FAIL ") + name)
        bad += not ok
    sys.exit(1 if bad else 0)
