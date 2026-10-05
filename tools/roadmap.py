#!/usr/bin/env python3
"""Stages and milestones from .github/phases.yml.

    python tools/roadmap.py                                  # write phases/*/README.md + README tables
    python tools/roadmap.py --github --repo OWNER/NAME [--dry-run] [--prune]
        one GitHub milestone per milestone, one checklist issue per step (REST only; safe to re-run).
        --prune closes milestones/issues whose ID is no longer in the YAML (never deletes).

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bom_check  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github" / "phases.yml"
README = ROOT / "README.md"
START, END = "<!-- phases:start -->", "<!-- phases:end -->"
SUBFOLDERS = [("research", "Research"), ("design", "Design"), ("3d", "3D files"), ("bom", "Bill of materials"),
              ("test", "Tests")]


IMAGES = {"00-plan": "architecture", "01-power": "power-flow", "03-frame": "axes", "06-camera-light": "brdf-lobe",
          "11-scan-capture": "scanner"}


def load() -> tuple[list[dict], list[dict]]:
    y = yaml.safe_load(SOURCE.read_text(encoding="utf-8"))
    return y["stages"], y["milestones"]


def costs() -> dict[str, float]:
    return {p: v["buy"] for p, v in bom_check.totals(bom_check.load()).items()}


ORDER = "RSGTVNHPCKLMFE"


def sources() -> dict[int, set[str]]:
    """Phase number -> reference IDs: rows tagged '(phase NN)', BOM Refs, and [ID] cites in the phase folder."""
    out: dict[int, set[str]] = {}
    for line in (ROOT / "REFERENCES.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"\|\s*\*\*([A-Z]\d+)\*\*.*\(phases? ([\d, ]+)\) \|\s*$", line)
        if m:
            for n in re.findall(r"\d+", m.group(2)):
                out.setdefault(int(n), set()).add(m.group(1))
    known = set(re.findall(r"^\|\s*\*\*([A-Z]\d+)\*\*", (ROOT / "REFERENCES.md").read_text(encoding="utf-8"), re.M))
    for d in (ROOT / "phases").iterdir():
        if not d.is_dir():
            continue
        ids = out.setdefault(int(d.name[:2]), set())
        for f in d.rglob("*.md"):
            if f.name != "README.md":
                ids.update(i for i in re.findall(r"\[([A-Z]\d{1,3})\]", f.read_text(encoding="utf-8")) if i in known)
        bom = d / "bom" / "bom.csv"
        if bom.exists():
            for r in csv.DictReader(bom.open(encoding="utf-8")):
                ids.update(i.strip() for i in r["Refs"].split(",") if i.strip() in known)
    return out


def sort_ids(ids: set[str]) -> list[str]:
    return sorted(ids, key=lambda i: (ORDER.index(i[0]) if i[0] in ORDER else 99, int(i[1:])))


def ms_title(m: dict) -> str:
    return f"{m['id']} · {m['title']}"


def issue_title(s: dict) -> str:
    return f"[{s['id']}] {s['title']}"


def issue_body(m: dict, s: dict) -> str:
    tasks = "\n".join(f"- [ ] {t}" for t in s["tasks"])
    return f"**Goal:** {m['goal']}\n\n{tasks}\n- [ ] **Done:** {s['done']}\n\n`phases/{m['stage']}/`"


def stage_md(st: dict, ms: list[dict], cost: float, running: float, opt: float, refs: list[str]) -> str:
    d = ROOT / "phases" / st["folder"]
    out = [f"# {st['folder'][:2]} · {st['title']}", ""]
    if st["folder"] in IMAGES:
        out += [f'<img src="../../docs/assets/{IMAGES[st["folder"]]}.svg" width="100%" alt="{st["title"]}">', ""]
    if cost:
        out += [f"${cost:.2f} · total so far ${running:.2f} / $500", ""]
    if opt:
        out += [f"Optional kit ${opt:.2f} (not in the $500 total)", ""]
    links = [f"[{name}]({sub}/)" for sub, name in SUBFOLDERS if (d / sub).is_dir()]
    if links:
        out += [" · ".join(links), ""]
    for m in ms:
        out += [f"## {ms_title(m)}", "", f"{m['goal']}" + (f" · ~{m['weeks']} wk" if m.get("weeks") else ""), ""]
        for s in m["steps"]:
            out += [f"**{s['id']} {s['title']}**", ""]
            out += [f"- [ ] {t}" for t in s["tasks"]]
            out += [f"- [ ] **Done:** {s['done']}", ""]
    if st.get("safety"):
        out += [f"> **Safety:** {st['safety']}", ""]
    if refs:
        out += [f"[Sources](../../REFERENCES.md): {' · '.join(refs)}", ""]
    return "\n".join(out)


def table(stages: list[dict], ms: list[dict], c: dict[str, float]) -> str:
    rows = ["| # | Stage | Milestones | Cost |", "|---:|---|---|---:|"]
    for st in stages:
        cost = c.get(st["folder"], 0.0)
        mine = [m for m in ms if m["stage"] == st["folder"]]
        rows.append(f"| {st['folder'][:2]} | [{st['title']}](phases/{st['folder']}/) | "
                    + ", ".join(f"{m['id']} {m['title']}" for m in mine) + f" | {f'${cost:.0f}' if cost else '—'} |")
    return "\n".join(rows)


def parts_rows(stages: list[dict]) -> str:
    rows = ["| Stage | Printed parts (STL) |", "|---|---|"]
    for st in stages:
        d = ROOT / "phases" / st["folder"] / "3d" / "print"
        files = sorted(d.glob("*.stl")) if d.is_dir() else []
        if files:
            items = " · ".join(f"[{f.stem.split('_', 1)[0]}](phases/{st['folder']}/3d/print/{f.name}) {f.stem.split('_', 1)[1].replace('_', ' ')}"
                              for f in files)
            rows.append(f"| [{st['folder'][:2]} {st['title']}](phases/{st['folder']}/3d/) | {items} |")
    return "\n".join(rows)


def ref_bullets() -> str:
    """Every row of REFERENCES.md as a bullet, under its section heading."""
    out = []
    for line in (ROOT / "REFERENCES.md").read_text(encoding="utf-8").splitlines():
        h = re.match(r"^(##+) (.+)$", line)
        if h and not line.startswith("# "):
            out += ["", f"{'###' if len(h.group(1)) == 2 else '####'} {h.group(2)}", ""]
            continue
        m = re.match(r"^\|\s*\*\*([A-Z]\d+)\*\*\s*\|(.*)\|(.*)\|\s*$", line)
        if m:
            out.append(f"- **{m.group(1)}** {m.group(2).strip()} — *{m.group(3).strip()}*")
    return "\n".join(out).strip("\n")


def _replace(text: str, start: str, end: str, body: str) -> str:
    if start not in text or end not in text:
        return text
    head, rest = text.split(start, 1)
    return f"{head}{start}\n{body}\n{end}{rest.split(end, 1)[1]}"


def write_docs(stages: list[dict], ms: list[dict]) -> None:
    t = bom_check.totals(bom_check.load())
    run, src = 0.0, sources()
    for st in stages:
        v = t.get(st["folder"], {"buy": 0.0, "opt": 0.0})
        run += v["buy"]
        d = ROOT / "phases" / st["folder"]
        d.mkdir(parents=True, exist_ok=True)
        mine = [m for m in ms if m["stage"] == st["folder"]]
        (d / "README.md").write_text(stage_md(st, mine, v["buy"], run, v.get("opt", 0.0) if st["folder"] == "15-standalone" else 0.0,
                                              sort_ids(src.get(int(st["folder"][:2]), set()))), encoding="utf-8")
    text = README.read_text(encoding="utf-8")
    nref = len(re.findall(r"^\|\s*\*\*[A-Z]\d+\*\*", (ROOT / "REFERENCES.md").read_text(encoding="utf-8"), re.M))
    text = re.sub(r"\[References \(\d+\)\]", f"[References ({nref})]", text)
    issues = "\n".join(f"- **{ms_title(m)}** — " + " · ".join(f"[{s['id']}] {s['title']}" for s in m["steps"]) for m in ms)
    text = _replace(text, "<!-- issues:start -->", "<!-- issues:end -->", issues)
    text = _replace(text, START, END, table(stages, ms, {k: v["buy"] for k, v in t.items()}))
    text = _replace(text, "<!-- parts:start -->", "<!-- parts:end -->", parts_rows(stages))
    text = _replace(text, "<!-- refs:start -->", "<!-- refs:end -->", ref_bullets())
    text = re.sub(r"^\d+ sources, grouped by ID prefix", f"{nref} sources, grouped by ID prefix", text, flags=re.M)
    README.write_text(text, encoding="utf-8")
    print(f"wrote {len(stages)} stage READMEs, {len(ms)} milestones, {sum(len(m['steps']) for m in ms)} issues")


def gh(args: list[str], dry: bool, ok_codes: tuple[str, ...] = ()) -> str:
    """Run `gh` (REST only, so it also works where GraphQL is blocked)."""
    if dry:
        print("DRY: gh", " ".join(a if len(a) < 60 else a[:57] + "..." for a in args[:8]))
        return "[]"
    res = subprocess.run(["gh", *args], text=True, capture_output=True)
    if res.returncode != 0:
        if any(c in (res.stdout + res.stderr) for c in ok_codes):
            return ""
        raise RuntimeError(f"gh {' '.join(args[:3])} failed: {res.stderr.strip() or res.stdout.strip()}")
    return res.stdout


def ms_key(title: str) -> str:
    """'M04 · Order power parts' -> 'M04'."""
    return title.split(" ", 1)[0]


def issue_key(title: str) -> str:
    """'[M04.1] Order' -> 'M04.1'."""
    return title[1:title.index("]")] if title.startswith("[") and "]" in title else title


def push_github(stages: list[dict], ms: list[dict], repo: str, dry: bool, prune: bool = False) -> None:
    """Create or update milestones and issues, matched by ID. Unchanged issues keep their ticks;
    an ID whose title changed gets new title, body, milestone, label and is reopened."""
    base = f"repos/{repo}"
    for st in stages:
        gh(["api", "-X", "POST", f"{base}/labels", "-f", f"name=stage-{st['folder'][:2]}", "-f", "color=f0883e"],
           dry, ok_codes=("already_exists", "422"))
    gh_ms = json.loads(gh(["api", f"{base}/milestones?state=all&per_page=100"], dry) or "[]")
    by_key = {ms_key(m["title"]): m for m in gh_ms}
    issues = json.loads(gh(["api", "--paginate", f"{base}/issues?state=all&per_page=100"], dry) or "[]")
    issues_by_key = {issue_key(i["title"]): i for i in issues if "pull_request" not in i}
    due = date.today()
    for m in ms:
        due += timedelta(weeks=m.get("weeks", 0))
        fields = ["-f", f"title={ms_title(m)}", "-f", f"description={m['goal']}"]
        if m.get("weeks"):
            fields += ["-f", f"due_on={due.isoformat()}T23:59:59Z"]
        old = by_key.get(m["id"])
        if old is None:
            out = gh(["api", "-X", "POST", f"{base}/milestones", *fields], dry)
            number = json.loads(out)["number"] if out and out.strip().startswith("{") else 0
            print("milestone +", ms_title(m))
        else:
            number = old["number"]
            if old["title"] != ms_title(m) or (old.get("description") or "") != m["goal"] or old["state"] != "open":
                gh(["api", "-X", "PATCH", f"{base}/milestones/{number}", *fields, "-f", "state=open"], dry)
                print("milestone ~", ms_title(m))
        for s in m["steps"]:
            title = issue_title(s)
            args = ["-f", f"title={title}", "-f", f"body={issue_body(m, s)}", "-F", f"milestone={number}",
                    "-f", f"labels[]=stage-{m['stage'][:2]}"]
            cur = issues_by_key.get(s["id"])
            if cur is None:
                gh(["api", "-X", "POST", f"{base}/issues", *args], dry)
                print("  issue +", title)
            elif cur["title"] != title:
                gh(["api", "-X", "PATCH", f"{base}/issues/{cur['number']}", *args, "-f", "state=open"], dry)
                print("  issue ~", title)
    if prune:
        keep_ms = {m["id"] for m in ms}
        keep_is = {s["id"] for m in ms for s in m["steps"]}
        for k, old in by_key.items():
            if k not in keep_ms and old["state"] == "open":
                gh(["api", "-X", "PATCH", f"{base}/milestones/{old['number']}", "-f", "state=closed"], dry)
                print("milestone closed (no longer planned):", old["title"])
        for k, cur in issues_by_key.items():
            if k not in keep_is and cur["state"] == "open" and cur["title"].startswith("["):
                gh(["api", "-X", "PATCH", f"{base}/issues/{cur['number']}", "-f", "state=closed",
                    "-f", "state_reason=not_planned"], dry)
                print("  issue closed (no longer planned):", cur["title"])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--repo", help="OWNER/NAME")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true")
    a = ap.parse_args(argv)
    stages, ms = load()
    if a.github:
        if not a.repo:
            ap.error("--github needs --repo OWNER/NAME")
        push_github(stages, ms, a.repo, a.dry_run, a.prune)
    else:
        write_docs(stages, ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
