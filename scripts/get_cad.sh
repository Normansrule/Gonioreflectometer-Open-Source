#!/usr/bin/env bash
# Vendor 3D models from the STEP column of phases/*/bom.csv -> phases/NN/3d/vendor/ (git-ignored).
#   bash scripts/get_cad.sh                                        download files, clone GitHub folders
#   bash scripts/get_cad.sh --from /mnt/c/Users/aleks/Downloads    pick up files you saved in a browser
# SPDX-License-Identifier: GPL-3.0-or-later
set -uo pipefail
cd "$(dirname "$0")/.."
FROM=""; [ "${1:-}" = "--from" ] && FROM=${2:?folder}
FROM="$FROM" python3 - <<'PY'
import csv, glob, os, re, shutil, subprocess
src = os.environ.get("FROM", "")
manual = []
for bom in sorted(glob.glob("phases/*/bom.csv")):
    vend = f"phases/{bom.split('/')[1]}/3d/vendor"
    for r in csv.DictReader(open(bom, encoding="utf-8")):
        for url in re.findall(r"https?://[^\s;)]+", r["STEP"]):
            gh = re.match(r"https://github\.com/([^/]+/[^/]+?)(?:/tree/[^/]+/(.+))?/?$", url)
            if gh:                                               # GitHub repo or folder: shallow clone
                out = f"{vend}/{r['ID']}_{gh.group(1).split('/')[1]}"
                if os.path.isdir(out):
                    print("have ", out); continue
                os.makedirs(vend, exist_ok=True)
                cmd = ["git", "clone", "-q", "--depth", "1", f"https://github.com/{gh.group(1)}.git", out]
                if gh.group(2):
                    cmd[3:3] = ["--filter=blob:none", "--sparse"]
                ok = subprocess.call(cmd) == 0 and (not gh.group(2) or subprocess.call(["git", "-C", out, "sparse-checkout", "set", gh.group(2)]) == 0)
                print(("got  " if ok else "FAIL ") + out)
                if not ok: manual.append(f"{r['ID']}  {url}")
                continue
            name = url.rstrip("/").split("/")[-1].split("file=")[-1].split("/")[-1]
            name = re.sub(r"[^\w.-]", "_", name)[:80]
            if not re.search(r"\.(step|stp|zip|pdf)$", name, re.I):
                manual.append(f"{r['ID']}  {url}  (web page: download the model there)"); continue
            out = f"{vend}/{r['ID']}_{name}"
            if os.path.exists(out) and os.path.getsize(out) > 0:
                print("have ", out); continue
            os.makedirs(vend, exist_ok=True)
            if src and os.path.exists(os.path.join(src, name)):
                shutil.copy(os.path.join(src, name), out); print("took ", out); continue
            ok = subprocess.call(["curl", "-fsSL", "-A", "Mozilla/5.0", "-o", out, url], stderr=subprocess.DEVNULL) == 0
            print(("got  " if ok else "FAIL ") + out)
            if not ok:
                if os.path.exists(out): os.remove(out)
                manual.append(f"{r['ID']}  {url}  (save as {name})")
if manual:
    print("\nNeeds your browser. Download, then run:  bash scripts/get_cad.sh --from /mnt/c/Users/$USER/Downloads")
    print("\n".join("  " + m for m in dict.fromkeys(manual)))
PY
