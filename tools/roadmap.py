#!/usr/bin/env python3
"""Stages and milestones from .github/phases.yml.

    python tools/roadmap.py                                  # write phases/*/README.md + README tables
    python tools/roadmap.py --github --repo OWNER/NAME [--dry-run] [--prune]
        one GitHub milestone per milestone, one checklist issue per step (REST only; safe to re-run).
        --prune closes milestones/issues whose ID is no longer in the YAML (never deletes).
    python tools/roadmap.py --progress        closed issues -> .github/progress.json (drives ✓ marks and figures)
    python tools/roadmap.py --close M05.1     close that step's issue, then refresh progress
    (--repo defaults to the `origin` remote)

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
import roadmap_svg  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github" / "phases.yml"
README = ROOT / "README.md"
PROGRESS = ROOT / ".github" / "progress.json"
STEP_SVG = ROOT / "docs" / "assets" / "steps"
START, END = "<!-- phases:start -->", "<!-- phases:end -->"
SUBFOLDERS = [("design.md", "Design"), ("research.md", "Research"), ("bom.csv", "Parts list"), ("3d", "3D files"),
              ("test.csv", "Tests")]


IMAGES = {"00-plan": "architecture", "01-power": "power-flow", "03-frame": "axes", "06-camera-light": "brdf-lobe",
          "11-scan-capture": "scanner"}


def done_steps() -> set[str]:
    """Step IDs whose GitHub issue is closed (from the last --progress run)."""
    if not PROGRESS.exists():
        return set()
    return set(json.loads(PROGRESS.read_text(encoding="utf-8")).get("closed", []))


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
        bom = d / "bom.csv"
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


def meta_line(s: dict) -> str:
    bits = []
    if s.get("time"):
        bits.append(f"**Time** {s['time']}" + (f" (+ {s['wait']})" if s.get("wait") else ""))
    if s.get("needs"):
        bits.append("**Needs** " + " · ".join(s["needs"]))
    return " · ".join(bits)


def step_md(s: dict, h: str = "###") -> list[str]:
    out = [meta_line(s), ""] if meta_line(s) else []
    out += [f"{h} Do", ""] + [f"{i}. {t}" for i, t in enumerate(s["do"], 1)]
    out += ["", f"{h} Verify", ""] + [f"- [ ] {t}" for t in s["verify"]]
    if s.get("fail"):
        out += ["", f"{h} If a check fails", ""] + [f"- {t}" for t in s["fail"]]
    if s.get("record") and s["record"] != "—":
        out += ["", f"{h} Record", "", s["record"]]
    return out


def issue_body(m: dict, s: dict) -> str:
    return "\n".join([f"**{m['id']} · {m['title']}** — {m['goal']}", ""] + step_md(s) +
                      ["", f"Stage checklist: `phases/{m['stage']}/README.md` · when done: `make done id={s['id']}`"])


def stage_md(st: dict, ms: list[dict], cost: float, running: float, opt: float, refs: list[str],
             done: set[str] = frozenset()) -> str:
    d = ROOT / "phases" / st["folder"]
    out = [f"# {st['folder'][:2]} · {st['title']}", "",
           f'<img src="../../docs/assets/steps/{st["folder"][:2]}.svg" width="100%" alt="Steps of stage {st["folder"][:2]}">', ""]
    if st["folder"] in IMAGES:
        out += [f'<img src="../../docs/assets/{IMAGES[st["folder"]]}.svg" width="100%" alt="{st["title"]}">', ""]
    if cost:
        out += [f"${cost:.2f} · total so far ${running:.2f} / ${bom_check.HARD_CAP:.0f}", ""]
    if opt:
        out += [f"Optional kit ${opt:.2f} (not in the ${bom_check.HARD_CAP:.0f} total)", ""]
    links = [f"[{name}]({sub}{'/' if (d / sub).is_dir() else ''})" for sub, name in SUBFOLDERS if (d / sub).exists()]
    if links:
        out += [" · ".join(links), ""]
    for m in ms:
        k = sum(s["id"] in done for s in m["steps"])
        hrs = sum(roadmap_svg.hours(s.get("time")) for s in m["steps"])
        out += [f"## {ms_title(m)}", "", f"{m['goal']} · {k}/{len(m['steps'])} steps done · ~{roadmap_svg.fmt_h(hrs)} hands-on"
                + (f" · ~{m['weeks']} wk" if m.get("weeks") else ""), ""]
        for s in m["steps"]:
            out += [f"### {'✅ ' if s['id'] in done else ''}{s['id']} {s['title']}", ""] + step_md(s, "####") + [""]
    if st.get("safety"):
        out += [f"> **Safety:** {st['safety']}", ""]
    if refs:
        out += [f"[Sources](../../REFERENCES.md): {' · '.join(refs)}", ""]
    return "\n".join(out)


def table(stages: list[dict], ms: list[dict], c: dict[str, float], done: set[str] = frozenset()) -> str:
    rows = ["| # | Stage | Milestones | Hours | Done | Cost |", "|---:|---|---|---:|---:|---:|"]
    for st in stages:
        cost = c.get(st["folder"], 0.0)
        mine = [m for m in ms if m["stage"] == st["folder"]]
        steps = [s for m in mine for s in m["steps"]]
        hrs = sum(roadmap_svg.hours(s.get("time")) for s in steps)
        rows.append(f"| {st['folder'][:2]} | [{st['title']}](phases/{st['folder']}/) | "
                    + ", ".join(f"{m['id']} {m['title']}" for m in mine)
                    + f" | {roadmap_svg.fmt_h(hrs)} | {sum(s['id'] in done for s in steps)}/{len(steps)} | {f'${cost:.0f}' if cost else '—'} |")
    return "\n".join(rows)


def parts_rows(stages: list[dict]) -> str:
    rows = ["| Stage | Printed parts (STL) |", "|---|---|"]
    for st in stages:
        d = ROOT / "phases" / st["folder"] / "3d"
        files = sorted(d.glob("*.stl")) if d.is_dir() else []
        if files:
            items = " · ".join(f"[{f.stem.split('_', 1)[0]}](phases/{st['folder']}/3d/{f.name}) {f.stem.split('_', 1)[1].replace('_', ' ')}"
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
    run, src, done = 0.0, sources(), done_steps()
    nxt = roadmap_svg.next_step(ms, done)
    STEP_SVG.mkdir(parents=True, exist_ok=True)
    (ROOT / "docs" / "assets" / "phases.svg").write_text(roadmap_svg.overview(stages, ms, done), encoding="utf-8")
    plan = {"stages": [{"n": int(st["folder"][:2]), "title": st["title"],
                        "ms": [{"id": m["id"], "title": m["title"],
                                "steps": [{"id": x["id"], "title": x["title"], "time": x.get("time", "")} for x in m["steps"]]}
                               for m in ms if m["stage"] == st["folder"]]} for st in stages],
            "done": sorted(done)}
    (ROOT / "docs" / "plan.js").write_text("// Generated from .github/phases.yml by tools/roadmap.py — do not edit; run `make`.\n"
                                           f"window.PLAN = {json.dumps(plan, ensure_ascii=False)};\n", encoding="utf-8")
    for st in stages:
        v = t.get(st["folder"], {"buy": 0.0, "opt": 0.0})
        run += v["buy"]
        d = ROOT / "phases" / st["folder"]
        d.mkdir(parents=True, exist_ok=True)
        mine = [m for m in ms if m["stage"] == st["folder"]]
        (d / "README.md").write_text(stage_md(st, mine, v["buy"], run, v.get("opt", 0.0) if st["folder"] == "15-standalone" else 0.0,
                                              sort_ids(src.get(int(st["folder"][:2]), set())), done), encoding="utf-8")
        (STEP_SVG / f"{st['folder'][:2]}.svg").write_text(
            roadmap_svg.stage(st, mine, done, nxt[1]["id"] if nxt else None), encoding="utf-8")
    text = README.read_text(encoding="utf-8")
    nref = len(re.findall(r"^\|\s*\*\*[A-Z]\d+\*\*", (ROOT / "REFERENCES.md").read_text(encoding="utf-8"), re.M))
    text = re.sub(r"\[References \(\d+\)\]", f"[References ({nref})]", text)
    issues = "\n".join(["| Milestone | Steps (issues) | Checklist |", "|---|---|---|"] +
                       [f"| {ms_title(m)} | " + " · ".join(f"{'✅ ' if s['id'] in done else ''}{s['id']} {s['title']}"
                                                          + (f" ({s['time']})" if s.get("time") else "") for s in m["steps"]) +
                        f" | [open](phases/{m['stage']}/README.md#{re.sub(r'[^a-z0-9 -]', '', ms_title(m).lower()).replace(' ', '-')}) |" for m in ms])
    text = _replace(text, "<!-- issues:start -->", "<!-- issues:end -->", issues)
    text = _replace(text, START, END, table(stages, ms, {k: v["buy"] for k, v in t.items()}, done))
    nxt_md = (f"**Next step: [{nxt[1]['id']} {nxt[1]['title']}](phases/{nxt[0]['stage']}/README.md#"
              f"{re.sub(r'[^a-z0-9 -]', '', (nxt[1]['id'] + ' ' + nxt[1]['title']).lower()).replace(' ', '-')})**"
              + (f" · {nxt[1]['time']}" if nxt[1].get("time") else "") + f" · {len(done)} of {sum(len(m['steps']) for m in ms)} steps done"
              if nxt else "**All steps done.**")
    text = _replace(text, "<!-- next:start -->", "<!-- next:end -->", nxt_md)
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


def _norm(body: str) -> str:
    return body.replace("- [x]", "- [ ]").replace("- [X]", "- [ ]").replace("\r\n", "\n").strip()


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
            elif _norm(cur.get("body") or "") != _norm(issue_body(m, s)):     # steps changed: new text, ticks reset
                gh(["api", "-X", "PATCH", f"{base}/issues/{cur['number']}", "-f", f"body={issue_body(m, s)}"], dry)
                print("  issue body ~", title)
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


def repo_from_git() -> str:
    url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, text=True, capture_output=True).stdout.strip()
    m = re.search(r"[:/]([^/:]+/[^/]+?)(?:\.git)?$", url)
    if not m:
        raise SystemExit("no `origin` remote: pass --repo OWNER/NAME")
    return m.group(1)


def pull_progress(repo: str) -> set[str]:
    """Closed step issues -> .github/progress.json (closed as 'not planned' does not count)."""
    issues = json.loads(gh(["api", "--paginate", f"repos/{repo}/issues?state=closed&per_page=100"], False) or "[]")
    closed = sorted({issue_key(i["title"]) for i in issues if "pull_request" not in i and i["title"].startswith("[")
                     and i.get("state_reason") != "not_planned"})
    PROGRESS.write_text(json.dumps({"updated": date.today().isoformat(), "closed": closed}, indent=1) + "\n", encoding="utf-8")
    print(f"progress: {len(closed)} steps done -> {PROGRESS.relative_to(ROOT)}")
    return set(closed)


def close_step(repo: str, sid: str) -> None:
    issues = json.loads(gh(["api", "--paginate", f"repos/{repo}/issues?state=open&per_page=100"], False) or "[]")
    cur = next((i for i in issues if issue_key(i["title"]) == sid and "pull_request" not in i), None)
    if cur is None:
        print(f"{sid}: no open issue (already closed, or run `make publish` first)")
    else:
        gh(["api", "-X", "PATCH", f"repos/{repo}/issues/{cur['number']}", "-f", "state=closed", "-f", "state_reason=completed"], False)
        print(f"closed {cur['title']}")
    pull_progress(repo)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--repo", help="OWNER/NAME")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--prune", action="store_true")
    ap.add_argument("--progress", action="store_true", help="closed issues -> .github/progress.json")
    ap.add_argument("--close", metavar="STEP", help="close one step's issue, e.g. M05.1")
    a = ap.parse_args(argv)
    stages, ms = load()
    if a.close:
        if a.close not in {s["id"] for m in ms for s in m["steps"]}:
            ap.error(f"unknown step {a.close}")
        close_step(a.repo or repo_from_git(), a.close)
        write_docs(stages, ms)
    elif a.progress:
        pull_progress(a.repo or repo_from_git())
        write_docs(stages, ms)
    elif a.github:
        push_github(stages, ms, a.repo or repo_from_git(), a.dry_run, a.prune)
    else:
        write_docs(stages, ms)
    return 0


if __name__ == "__main__":
    sys.exit(main())
