#!/usr/bin/env python3
"""Copies of the project in formats other software opens and edits -> exports/ (committed; see exports/README.md).

    python tools/exports.py          documents: paper (Word, Overleaf zip), references (Zotero), BOM (Excel/Sheets), wiki book
    python tools/exports.py --cad    also exports/cad/opengonio_assembly.glb (Blender, Windows 3D Viewer, web) - needs cadquery

Sources stay the truth (paper/*.tex, REFERENCES.md, phases/*/bom.csv, wiki/src); exports are regenerated, never edited.
Needs pandoc; the wiki PDF also needs xelatex. Missing tools skip that file with a note.
SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXP, PAPER, WIKI = ROOT / "exports", ROOT / "paper", ROOT / "wiki"
REPO = "https://github.com/Normansrule/Gonioreflectometer-Open-Source/blob/main"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "cad"))


SOURCES = ["paper", "REFERENCES.md", "phases", "PARTS.md", "wiki/src", "tools",   # generated folders excluded:
           ":!paper/build", ":!paper/generated", ":!paper/figures", ":!paper/references.bib", ":!phases/*/3d", ":!phases/*/README.md"]


def source_epoch() -> int:
    """Time of the last commit that touched a source: stamped into every export, so unchanged sources give
    byte-identical files (no noise in git)."""
    import os
    try:
        out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", *SOURCES], cwd=ROOT, capture_output=True,
                             text=True, check=True).stdout.strip()
        return int(out or os.environ.get("SOURCE_DATE_EPOCH", "0"))
    except (subprocess.CalledProcessError, FileNotFoundError, ValueError):
        return 0


EPOCH = source_epoch()


def have(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def pandoc(*args: str, cwd: Path = ROOT) -> None:
    import os
    env = os.environ | {"SOURCE_DATE_EPOCH": str(EPOCH), "FORCE_SOURCE_DATE": "1"}
    subprocess.run(["pandoc", *args], cwd=cwd, check=True, capture_output=True, text=True, env=env)


# ---------------- paper ----------------
def paper_docx() -> str:
    """Word copy of the manuscript (APA citations resolved; PDF figures swapped for PNG)."""
    out = EXP / "paper" / "opengonio.docx"
    out.parent.mkdir(parents=True, exist_ok=True)
    tex = (PAPER / "opengonio.tex").read_text(encoding="utf-8")
    tex = re.sub(r"\{(axes|architecture)\.pdf\}", r"{\1.png}", tex)
    tex = re.sub(r"\\input\{generated/(design_files|bom)\.tex\}", r"\\input{generated/\1_plain.tex}", tex)
    with tempfile.NamedTemporaryFile("w", suffix=".tex", dir=PAPER, delete=False, encoding="utf-8") as t:
        t.write(tex)
    try:
        pandoc(Path(t.name).name, "-f", "latex", "-s", "-o", str(out), "--citeproc", "--csl=apa.csl",
               "--bibliography=references.bib", "--resource-path=.:figures",
               "-M", "title=" + re.search(r"\\title\{([^}]*)\}", tex).group(1),          # same title as the PDF
               "-M", "author=Aleksander Norman", cwd=PAPER)
        deterministic_zip(out)
    finally:
        Path(t.name).unlink()
    return rel(out)


def overleaf_zip() -> str:
    """Upload to Overleaf: New Project -> Upload Project. Compiler pdfLaTeX; biber runs automatically."""
    out = EXP / "paper" / "opengonio-overleaf.zip"
    out.parent.mkdir(parents=True, exist_ok=True)
    import time
    stamp = time.gmtime(max(EPOCH, 315532800))[:6]                 # zip dates start in 1980
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        files = {f: (PAPER / f).read_bytes() for f in ["opengonio.tex", "references.bib", "README.md", *sorted(
            p.relative_to(PAPER).as_posix() for d in ("generated", "figures") for p in (PAPER / d).glob("*"))]}
        files["latexmkrc"] = b"$pdf_mode = 1;\n$bibtex_use = 2;\n"            # Overleaf: no build/ subfolder
        for f, data in files.items():
            z.writestr(zipfile.ZipInfo(f, stamp), data, zipfile.ZIP_DEFLATED)
    return rel(out)


# ---------------- references ----------------
RIS_TYPE = {"article-journal": "JOUR", "paper-conference": "CPAPER", "book": "BOOK", "chapter": "CHAP",
            "webpage": "ELEC", "report": "RPRT", "thesis": "THES"}


def references() -> list[str]:
    """BibTeX (any tool), CSL-JSON and RIS (Zotero, Mendeley, EndNote)."""
    d = EXP / "references"
    d.mkdir(parents=True, exist_ok=True)
    shutil.copy(PAPER / "references.bib", d / "opengonio.bib")
    pandoc(str(PAPER / "references.bib"), "-f", "biblatex", "-t", "csljson", "-o", str(d / "opengonio.json"))
    items = json.loads((d / "opengonio.json").read_text(encoding="utf-8"))
    L = []
    for it in items:
        L.append(f"TY  - {RIS_TYPE.get(it.get('type', ''), 'GEN')}")
        L.append(f"ID  - {it['id']}")
        for a in it.get("author", []):
            L.append("AU  - " + (f"{a['family']}, {a.get('given', '')}".strip(", ") if "family" in a else a.get("literal", "")))
        L.append(f"TI  - {it.get('title', '')}")
        if it.get("container-title"):
            L.append(f"T2  - {it['container-title']}")
        y = (it.get("issued", {}).get("date-parts") or [[None]])[0][0]
        if y:
            L.append(f"PY  - {y}")
        for k, tag in (("volume", "VL"), ("issue", "IS"), ("publisher", "PB"), ("DOI", "DO"), ("URL", "UR")):
            if it.get(k):
                L.append(f"{tag}  - {it[k]}")
        if it.get("page"):
            sp, _, ep = str(it["page"]).partition("–")
            L += [f"SP  - {sp}"] + ([f"EP  - {ep}"] if ep else [])
        L.append("ER  - ")
        L.append("")
    (d / "opengonio.ris").write_text("\n".join(L), encoding="utf-8")
    return [rel(d / f"opengonio.{x}") for x in ("bib", "json", "ris")]


# ---------------- bill of materials ----------------
def bom() -> list[str]:
    """One workbook (Excel, Google Sheets, LibreOffice): summary with formulas, every part with picture and links."""
    import catalog
    import parts_doc
    from openpyxl import Workbook
    from openpyxl.drawing.image import Image as XLImage
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter

    d = EXP / "bom"
    d.mkdir(parents=True, exist_ok=True)
    titles, al = parts_doc.stage_titles(), catalog.aliases()
    wb = Workbook()
    ws = wb.active
    ws.title = "Parts"
    head = ["Stage", "ID", "Type", "Picture", "Part", "Use", "Must meet", "Qty", "Unit USD", "Total USD", "Supplier",
            "Buy", "STEP", "STL", "Price checked", "Status", "Notes"]
    ws.append(head)
    flat = []
    for bomf in sorted((ROOT / "phases").glob("*/bom.csv")):
        stage = bomf.parent.name
        for r in csv.DictReader(bomf.open(newline="", encoding="utf-8")):
            files, _, _ = catalog.classify(stage, r, al)
            step = files[0] if files else None
            stl = step.with_suffix(".stl") if step and step.with_suffix(".stl").exists() else None
            i = ws.max_row + 1
            ws.append([stage, r["ID"], r["Type"], "", r["Part"], r["Use"], r["Requirement"], float(r["Qty"] or 0),
                       float(r["Unit USD"] or 0), f"=H{i}*I{i}", r["Supplier"], r["Link"] or "",
                       step.name if step else "", stl.name if stl else "", r["Price"], r["Status"], r["Notes"]])
            if r["Link"].startswith("http"):
                ws.cell(i, 12).hyperlink, ws.cell(i, 12).value = r["Link"], "buy"
            for col, f in ((13, step), (14, stl)):
                if f:
                    ws.cell(i, col).hyperlink = f"{REPO}/{rel(f)}?raw=true"
            png = ROOT / "docs" / "assets" / "parts" / f"{step.stem}.png" if step else None
            if png and png.exists():
                img = XLImage(str(png))
                img.width = img.height = 48
                ws.add_image(img, f"D{i}")
                ws.row_dimensions[i].height = 40
            flat.append({k: r[k] for k in r} | {"Stage": stage, "STEP": rel(step) if step else "", "STL": rel(stl) if stl else ""})
    n = ws.max_row
    for c, w in zip(range(1, len(head) + 1), (14, 9, 9, 8, 42, 30, 50, 6, 9, 10, 10, 8, 30, 30, 18, 10, 50)):
        ws.column_dimensions[get_column_letter(c)].width = w
    for c in ws[1]:
        c.font, c.fill = Font(bold=True, color="FFFFFF"), PatternFill("solid", fgColor="1F4E79")
    for row in ws.iter_rows(min_row=2, max_row=n):
        for c in row:
            c.alignment = Alignment(vertical="center", wrap_text=c.column in (5, 6, 7, 17))
        for c in (row[8], row[9]):
            c.number_format = '"$"#,##0.00'
    ws.freeze_panes, ws.auto_filter.ref = "E2", f"A1:{get_column_letter(len(head))}{n}"

    sm = wb.create_sheet("Summary", 0)
    sm.append(["Stage", "Title", "Parts USD", "Optional USD", "Tools USD"])
    stages = sorted({p.parent.name for p in (ROOT / "phases").glob("*/bom.csv")})
    for k, st in enumerate(stages, start=2):
        sm.append([st, titles.get(st, st)] + [f'=SUMIFS(Parts!$J:$J,Parts!$A:$A,$A{k},Parts!$C:$C,"{t}")'
                                               for t in ("Purchase", "Optional", "Tool")])
    t = sm.max_row + 1
    sm.append(["Total", ""] + [f"=SUM({c}2:{c}{t - 1})" for c in "CDE"])
    import bom_check
    sm.append(["Budget cap (parts)", "", bom_check.HARD_CAP])
    sm.append(["Under the cap?", "", f'=IF(C{t}<=C{t + 1},"yes","NO")'])
    for c in sm[1] + sm[t]:
        c.font = Font(bold=True)
    for row in sm.iter_rows(min_row=2, max_row=t + 1, min_col=3, max_col=5):
        for c in row:
            c.number_format = '"$"#,##0.00'
    sm.column_dimensions["A"].width, sm.column_dimensions["B"].width = 18, 34
    for c in "CDE":
        sm.column_dimensions[c].width = 14
    sm.append([])
    sm.append(["Source of truth: phases/*/bom.csv (regenerated by make export). Edit decisions in PARTS.md, not here."])
    import datetime
    wb.properties.created = wb.properties.modified = datetime.datetime.fromtimestamp(EPOCH, datetime.timezone.utc).replace(tzinfo=None)
    wb.save(d / "opengonio-bom.xlsx")
    deterministic_zip(d / "opengonio-bom.xlsx")
    with (d / "opengonio-bom.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["Stage", *[k for k in flat[0] if k not in ("Stage", "STEP", "STL")], "STEP", "STL"])
        w.writeheader()
        w.writerows(flat)
    return [rel(d / "opengonio-bom.xlsx"), rel(d / "opengonio-bom.csv")]


# ---------------- wiki book ----------------
def wiki_book() -> list[str]:
    """All wiki pages in sidebar order as one Word file and one PDF."""
    d = EXP / "wiki"
    d.mkdir(parents=True, exist_ok=True)
    order = re.findall(r"\(([\w-]+)\.md\)", (WIKI / "_Sidebar.md").read_text(encoding="utf-8"))
    parts = []
    for name in dict.fromkeys(order):
        t = (WIKI / f"{name}.md").read_text(encoding="utf-8")
        t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
        t = re.sub(r"```\s*math\n(.*?)\n```", r"$$\n\1\n$$", t, flags=re.S)          # GitHub math blocks -> TeX
        t = re.sub(r"\]\(([\w-]+)\.md(#[^)]*)?\)", lambda m: f"](#{m.group(1).lower()})", t)
        t = re.sub(r"^# (.+)$", lambda m: f"# {m.group(1)} {{#{name.lower()}}}", t, count=1, flags=re.M)
        parts.append(t)
    src = d / "_book.md"
    src.write_text("\n\n\\newpage\n\n".join(parts), encoding="utf-8")
    meta = ["-M", "title=OpenGonio wiki", "-M", "subtitle=Explanations, bibliography (APA 7) and background appendices",
            "--toc", "--toc-depth=1"]
    out = [d / "opengonio-wiki.docx"]
    try:
        pandoc(str(src), "-f", "markdown-raw_html", "-o", str(out[0]), *meta)
        deterministic_zip(out[0])
        if have("xelatex"):
            pdf = d / "opengonio-wiki.pdf"
            old = pdf.read_bytes() if pdf.exists() else b""
            pandoc(str(src), "-f", "markdown-raw_html", "-o", str(pdf), "--pdf-engine=xelatex", *meta,
                   "-V", "mainfont=DejaVu Serif", "-V", "monofont=DejaVu Sans Mono", "-V", "geometry:margin=2cm",
                   "-V", "colorlinks=true", "-V", "fontsize=10pt")
            if old and pdf_norm(old) == pdf_norm(pdf.read_bytes()):
                pdf.write_bytes(old)                         # only dates / ID differ: keep the committed file
            out.append(pdf)
    finally:
        src.unlink()
    return [rel(p) for p in out]


# ---------------- CAD ----------------
def cad() -> list[str]:
    """Whole machine as glTF binary: Blender, Windows 3D Viewer, three.js, online viewers. STEP stays the CAD master."""
    import assembly as A
    d = EXP / "cad"
    d.mkdir(parents=True, exist_ok=True)
    out = d / "opengonio_assembly.glb"
    A.build().export(str(out), exportType="GLTF", tolerance=0.2, angularTolerance=0.3)
    glb_scale(out, 0.001)                                    # model is in mm; glTF means metres (Blender imports 1:1)
    return [rel(out)]


def glb_scale(path: Path, k: float) -> None:
    """Set a uniform scale on every root node of a binary glTF (rewrites the JSON chunk, keeps the binary one)."""
    import struct
    b = path.read_bytes()
    jlen = struct.unpack("<I", b[12:16])[0]
    j = json.loads(b[20:20 + jlen])
    for i in j["scenes"][j.get("scene", 0)]["nodes"]:
        j["nodes"][i]["scale"] = [k, k, k]
    js = json.dumps(j, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    rest = b[20 + jlen:]
    path.write_bytes(struct.pack("<4sII", b"glTF", 2, 12 + 8 + len(js) + len(rest)) + struct.pack("<I4s", len(js), b"JSON") + js + rest)


def pdf_norm(b: bytes) -> bytes:
    """PDF bytes without the parts that change on every run (dates, trailer ID, xdvipdfmx font-subset tags)."""
    b = re.sub(rb"/(CreationDate|ModDate)\s*\([^)]*\)", b"", b)
    b = re.sub(rb"/ID\s*\[[^\]]*\]", b"", b)
    return re.sub(rb"/[A-Z]{6}\+", b"/", b)


def deterministic_zip(path: Path) -> None:
    """Rewrite an Office file (a zip) with fixed member dates, document dates and order."""
    import time
    stamp = time.gmtime(max(EPOCH, 315532800))[:6]
    iso = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(EPOCH)).encode()
    with zipfile.ZipFile(path) as z:
        items = [(i.filename, z.read(i.filename)) for i in z.infolist()]
    items = [(n, re.sub(rb"(<dcterms:(?:created|modified)[^>]*>)[^<]*", rb"\g<1>" + iso, d) if n == "docProps/core.xml" else d)
             for n, d in items]
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in items:
            z.writestr(zipfile.ZipInfo(name, stamp), data, zipfile.ZIP_DEFLATED)


def rel(p: Path) -> str:
    return p.relative_to(ROOT).as_posix()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cad", action="store_true")
    a = ap.parse_args()
    if not have("pandoc"):
        print("exports: skipped (needs pandoc)")
        return 0
    try:
        import openpyxl  # noqa: F401
        sheets = bom()
    except ImportError:
        sheets = ["(bom skipped: pip install openpyxl, or make setup)"]
    done = [paper_docx(), overleaf_zip(), *references(), *sheets, *wiki_book()] + (cad() if a.cad else [])
    print("exports: " + " · ".join(done))
    return 0


if __name__ == "__main__":
    sys.exit(main())
