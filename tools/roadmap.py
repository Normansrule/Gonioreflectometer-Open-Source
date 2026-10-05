#!/usr/bin/env python3
"""Phases from .github/phases.yml.

    python tools/roadmap.py                                  # write phases/*/README.md + README table
    python tools/roadmap.py --github --repo OWNER/NAME [--dry-run]
        one milestone per phase, one checklist issue per step (REST only; safe to re-run).

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


def load() -> list[dict]:
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))["phases"]


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


def ms_title(p: dict) -> str:
    return f"{p['id']} · {p['title']}"


def issue_title(s: dict) -> str:
    return f"[{s['id']}] {s['title']}"


def issue_body(p: dict, s: dict) -> str:
    tasks = "\n".join(f"- [ ] {t}" for t in s["tasks"])
    return f"**Goal:** {p['goal']}\n\n{tasks}\n- [ ] **Done:** {s['done']}\n\n`phases/{p['folder']}/`"


def phase_md(p: dict, cost: float, running: float, refs: list[str]) -> str:
    d = ROOT / "phases" / p["folder"]
    n = int(p["id"][1:])
    out = [f"# {n:02d} · {p['title']}", "", p["goal"], ""]
    if p.get("image"):
        out += [f'<img src="../../docs/assets/{p['image']}.svg" width="100%" alt="{p['title']}">', ""]
    if cost:
        out += [f"${cost:.2f} · total so far ${running:.2f} / $500", ""]
    links = [f"[{name}]({sub}/)" for sub, name in SUBFOLDERS if (d / sub).is_dir()]
    if links:
        out += [" · ".join(links), ""]
    for s in p["steps"]:
        out += [f"## {s['id'][1:]} {s['title']}", ""]
        out += [f"- [ ] {t}" for t in s["tasks"]]
        out += [f"- [ ] **Done:** {s['done']}", ""]
    if p.get("safety"):
        out += [f"> **Safety:** {p['safety']}", ""]
    if refs:
        out += [f"[Sources](../../REFERENCES.md): {' · '.join(refs)}", ""]
    return "\n".join(out)


def table(phases: list[dict], c: dict[str, float]) -> str:
    rows = ["| # | Phase | Goal | Cost |", "|---:|---|---|---:|"]
    for p in phases:
        cost = c.get(p["folder"], 0.0)
        rows.append(f"| {p['id'][1:]} | [{p['title']}](phases/{p['folder']}/) | {p['goal']} | "
                    f"{f'${cost:.0f}' if cost else '—'} |")
    return "\n".join(rows)


def write_docs(phases: list[dict]) -> None:
    c, run, src = costs(), 0.0, sources()
    for p in phases:
        cost = c.get(p["folder"], 0.0)
        run += cost
        d = ROOT / "phases" / p["folder"]
        d.mkdir(parents=True, exist_ok=True)
        (d / "README.md").write_text(phase_md(p, cost, run, sort_ids(src.get(int(p["id"][1:]), set()))), encoding="utf-8")
    text = README.read_text(encoding="utf-8")
    nref = len(re.findall(r"^\|\s*\*\*[A-Z]\d+\*\*", (ROOT / "REFERENCES.md").read_text(encoding="utf-8"), re.M))
    text = re.sub(r"\[References \(\d+\)\]", f"[References ({nref})]", text)
    if "<!-- issues:start -->" in text:
        head, rest = text.split("<!-- issues:start -->", 1)
        tail = rest.split("<!-- issues:end -->", 1)[1]
        lines = []
        for p in phases:
            lines.append(f"- **{ms_title(p)}** — " + " · ".join(f"[{s['id']}] {s['title']}" for s in p["steps"]))
        text = f"{head}<!-- issues:start -->\n{chr(10).join(lines)}\n<!-- issues:end -->{tail}"
    if START in text and END in text:
        head, rest = text.split(START, 1)
        tail = rest.split(END, 1)[1]
        README.write_text(f"{head}{START}\n{table(phases, c)}\n{END}{tail}", encoding="utf-8")
    print(f"wrote {len(phases)} phase READMEs, {sum(len(p['steps']) for p in phases)} steps")


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
    """'P04 · Light arm' -> 'P04'."""
    return title.split(" ", 1)[0]


def issue_key(title: str) -> str:
    """'[P04.1] Build' -> 'P04.1'."""
    return title[1:title.index("]")] if title.startswith("[") and "]" in title else title


def push_github(phases: list[dict], repo: str, dry: bool) -> None:
    """Create or update milestones and issues, matched by ID. Unchanged issues keep their ticks;
    an ID whose title changed gets new title, body, milestone, label and is reopened."""
    base = f"repos/{repo}"
    for p in phases:
        gh(["api", "-X", "POST", f"{base}/labels", "-f", f"name=phase-{p['id'][1:]}", "-f", "color=f0883e"],
           dry, ok_codes=("already_exists", "422"))
    by_key = {ms_key(m["title"]): m for m in json.loads(gh(["api", f"{base}/milestones?state=all&per_page=100"], dry) or "[]")}
    issues = json.loads(gh(["api", "--paginate", f"{base}/issues?state=all&per_page=100"], dry) or "[]")
    issues_by_key = {issue_key(i["title"]): i for i in issues if "pull_request" not in i}
    due = date.today()
    for p in phases:
        due += timedelta(weeks=p.get("weeks", 0))
        fields = ["-f", f"title={ms_title(p)}", "-f", f"description={p['goal']}"]
        if p.get("weeks"):
            fields += ["-f", f"due_on={due.isoformat()}T23:59:59Z"]
        old = by_key.get(p["id"])
        if old is None:
            out = gh(["api", "-X", "POST", f"{base}/milestones", *fields], dry)
            number = json.loads(out)["number"] if out and out.strip().startswith("{") else 0
            print("milestone +", ms_title(p))
        else:
            number = old["number"]
            if old["title"] != ms_title(p) or (old.get("description") or "") != p["goal"]:
                gh(["api", "-X", "PATCH", f"{base}/milestones/{number}", *fields], dry)
                print("milestone ~", ms_title(p))
        for s in p["steps"]:
            title = issue_title(s)
            args = ["-f", f"title={title}", "-f", f"body={issue_body(p, s)}", "-F", f"milestone={number}",
                    "-f", f"labels[]=phase-{p['id'][1:]}"]
            cur = issues_by_key.get(s["id"])
            if cur is None:
                gh(["api", "-X", "POST", f"{base}/issues", *args], dry)
                print("  issue +", title)
            elif cur["title"] != title:
                gh(["api", "-X", "PATCH", f"{base}/issues/{cur['number']}", *args, "-f", "state=open"], dry)
                print("  issue ~", title)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--repo", help="OWNER/NAME")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    phases = load()
    if a.github:
        if not a.repo:
            ap.error("--github needs --repo OWNER/NAME")
        push_github(phases, a.repo, a.dry_run)
    else:
        write_docs(phases)
    return 0


if __name__ == "__main__":
    sys.exit(main())
