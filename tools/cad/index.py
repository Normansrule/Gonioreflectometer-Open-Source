#!/usr/bin/env python3
"""Write phases/NN/3d/README.md (printed + bought parts with their 3D files) and point BOM Print rows at the files.
SPDX-License-Identifier: GPL-3.0-or-later
"""
import csv
import io
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REG = dict((m[0], (m[1], m[2], m[3])) for m in re.findall(
    r'"([A-Z]+-\d+[a-z]?)": \("([\w-]+)", "(\w+)", [^,]+(?:\([^)]*\))?, "([^"]+)"\)', (ROOT / "tools/cad/parts.py").read_text()))
PRINT_NOTE = "PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first."


def stage_index(stage: Path) -> str:
    d3 = stage / "3d"
    out = [f"# {stage.name[:2]} · 3D files", ""]
    printed = sorted(d3.glob("*.step")) if d3.is_dir() else []
    if printed:
        out += ["## Print", "", PRINT_NOTE, "", "**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.", "",
                "| ID | Part | Edit (STEP) | Print (STL) |", "|---|---|---|---|"]
        for f in printed:
            pid = f.stem.split("_", 1)[0]
            what = REG.get(pid, ("", "", f.stem))[2]
            out.append(f"| {pid} | {what} | [{f.name}]({f.name}) | [{f.stem}.stl]({f.stem}.stl) |")
        out += ["", "Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).", ""]
    bom = stage / "bom.csv"
    if bom.exists():
        rows = [r for r in csv.DictReader(bom.open(encoding="utf-8")) if r["Type"] in ("Purchase", "Optional")]
        if rows:
            out += ["## Bought parts", "", "`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).", "",
                    "| ID | Part | 3D model |", "|---|---|---|"]
            for r in rows:
                cad = r["STEP"] or "—"
                url = re.search(r"https?://\S+", cad)
                if url:
                    cad = f"[link]({url.group(0).rstrip(').,')})" + (" " + cad.replace(url.group(0), "").strip(" :-") if cad.replace(url.group(0), "").strip(" :-") else "")
                out.append(f"| {r['ID']} | {r['Part']} | {cad} |")
            out.append("")
    out += ["Design notes: [../design.md](../design.md).", ""]
    return "\n".join(out)


def link_bom(stage: Path) -> None:
    bom = stage / "bom.csv"
    if not bom.exists():
        return
    text = bom.read_text(encoding="utf-8")
    rd = csv.DictReader(io.StringIO(text))
    rows, cols = list(rd), rd.fieldnames
    for r in rows:
        if r["Type"] == "Print":
            files = sorted(f"3d/{f.name}" for f in (stage / "3d").glob(f"{r['ID']}*.step"))
            if files:
                r["STEP"] = "; ".join(files)
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=cols, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    bom.write_text(buf.getvalue(), encoding="utf-8")


if __name__ == "__main__":
    n = 0
    for stage in sorted((ROOT / "phases").iterdir()):
        if (stage / "3d").is_dir() or (stage / "bom.csv").exists():
            (stage / "3d").mkdir(exist_ok=True)
            link_bom(stage)
            (stage / "3d" / "README.md").write_text(stage_index(stage), encoding="utf-8")
            n += 1
    print(f"wrote {n} 3d/README.md")
