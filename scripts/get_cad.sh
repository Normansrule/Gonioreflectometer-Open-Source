#!/usr/bin/env bash
# Download vendor 3D models linked in phases/*/bom/bom.csv (STEP column) into phases/NN/3d/vendor/ (git-ignored).
#   bash scripts/get_cad.sh
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
cd "$(dirname "$0")/.."
python3 - <<'PY'
import csv, glob, os, re, subprocess
manual = []
for bom in sorted(glob.glob("phases/*/bom/bom.csv")):
    stage = bom.split("/")[1]
    vend = f"phases/{stage}/3d/vendor"
    for r in csv.DictReader(open(bom, encoding="utf-8")):
        for url in re.findall(r"https?://[^\s;)]+", r["STEP"]):
            name = re.sub(r"[^\w.-]", "_", url.rstrip("/").split("/")[-1].split("file=")[-1].split("/")[-1])[:80]
            if not re.search(r"\.(step|stp|zip|pdf)$", name, re.I):
                manual.append(f"{r['ID']}  {url}"); continue
            os.makedirs(vend, exist_ok=True)
            out = f"{vend}/{r['ID']}_{name}"
            if os.path.exists(out) and os.path.getsize(out) > 0:
                print("have ", out); continue
            ok = subprocess.call(["curl", "-fsSL", "-A", "Mozilla/5.0", "-o", out, url]) == 0
            print(("got  " if ok else "FAIL ") + out)
            if not ok:
                manual.append(f"{r['ID']}  {url}")
                if os.path.exists(out): os.remove(out)
if manual:
    print("\nOpen in a browser (vendor pages need a click or login); save into that stage's 3d/vendor/:")
    print("\n".join("  " + m for m in manual))
PY
