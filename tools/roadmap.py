#!/usr/bin/env python3
"""Roadmap tooling from .github/milestones.yml (single source of truth).

    python tools/roadmap.py --write-md                 # regenerate ROADMAP.md
    python tools/roadmap.py --github [--repo OWNER/NAME] [--dry-run]
        create labels, milestones and one checklist issue per roadmap item with the GitHub CLI.
        Safe to re-run: milestones/issues are matched by ID (M6, M6.3); renamed ones are updated, unchanged ones untouched.

SPDX-License-Identifier: GPL-3.0-or-later
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import date, timedelta
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github" / "milestones.yml"
ROADMAP = ROOT / "ROADMAP.md"

LABEL_COLOURS = {
    "planning": "c5def5", "design": "bfdadc", "hardware": "fbca04", "firmware": "0e8a16",
    "software": "1d76db", "power": "b60205", "milestone-test": "5319e7", "release": "000000",
    "stretch": "d4c5f9", "validation": "006b75", "calibration": "f9d0c4",
}


def load() -> list[dict]:
    return yaml.safe_load(SOURCE.read_text())["milestones"]


def issue_title(item: dict) -> str:
    return f"[{item['id']}] {item['title']}"


def issue_body(ms: dict, item: dict) -> str:
    tasks = "\n".join(f"- [ ] {t}" for t in item["tasks"])
    return (
        f"**Milestone goal:** {ms['goal']}\n\n"
        f"### Tasks\n{tasks}\n\n"
        f"### Acceptance\n- [ ] {item['acceptance']}\n\n"
        f"_Generated from `.github/milestones.yml` — edit the checklist here as you work; "
        f"close the issue when the acceptance box is ticked._"
    )


def write_md(milestones: list[dict]) -> str:
    out = [
        "# Roadmap",
        "",
        "Goal-oriented milestones. Each item is a GitHub issue with a checklist; each phase is a GitHub",
        "milestone whose progress bar fills as issues close. Generated from `.github/milestones.yml` by",
        "`python tools/roadmap.py --write-md` — edit the YAML, not this file.",
        "",
        "| Milestone | Goal | Cap | Items |",
        "|---|---|---:|---:|",
    ]
    for ms in milestones:
        cap = f"${ms['cap_usd']}" if "cap_usd" in ms else "—"
        out.append(f"| {ms['title']} | {ms['goal']} | {cap} | {len(ms['issues'])} |")
    for ms in milestones:
        out += ["", f"## {ms['title']}", "", f"**Goal:** {ms['goal']}", ""]
        for it in ms["issues"]:
            out += [f"### {it['id']} — {it['title']}", ""]
            out += [f"- [ ] {t}" for t in it["tasks"]]
            out += [f"- [ ] **Acceptance:** {it['acceptance']}", ""]
    return "\n".join(out) + "\n"


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
    """'M6 - Phase 6: ...' -> 'M6' (milestones are matched by ID so renames update in place)."""
    return title.split(" ", 1)[0]


def issue_key(title: str) -> str:
    """'[M6.3] Scan planner' -> 'M6.3'."""
    return title[1:title.index("]")] if title.startswith("[") and "]" in title else title


def push_github(milestones: list[dict], repo: str, dry: bool) -> None:
    """Create or update labels, milestones and checklist issues (GitHub REST only).

    Matching is by ID (M6, M6.3). Unchanged issues are left alone so ticked boxes survive;
    an issue whose title changed in the YAML gets its title, body, milestone and labels replaced.
    """
    base = f"repos/{repo}"
    labels = sorted({l for ms in milestones for it in ms["issues"] for l in it.get("labels", [])})
    for l in labels:
        gh(["api", "-X", "POST", f"{base}/labels", "-f", f"name={l}", "-f", f"color={LABEL_COLOURS.get(l, 'ededed')}"],
           dry, ok_codes=("already_exists", "422"))
    ms_list = json.loads(gh(["api", f"{base}/milestones?state=all&per_page=100"], dry) or "[]")
    by_key = {ms_key(m["title"]): m for m in ms_list}
    issues = json.loads(gh(["api", "--paginate", f"{base}/issues?state=all&per_page=100"], dry) or "[]")
    issues_by_key = {issue_key(i["title"]): i for i in issues if "pull_request" not in i}
    due = date.today()
    for ms in milestones:
        due += timedelta(weeks=ms.get("due_weeks", 0))
        fields = ["-f", f"title={ms['title']}", "-f", f"description={ms['goal']}"]
        if ms.get("due_weeks"):
            fields += ["-f", f"due_on={due.isoformat()}T23:59:59Z"]
        old = by_key.get(ms["id"])
        if old is None:
            out = gh(["api", "-X", "POST", f"{base}/milestones", *fields], dry)
            number = json.loads(out)["number"] if out and out.strip().startswith("{") else 0
            print("milestone +", ms["title"])
        else:
            number = old["number"]
            if old["title"] != ms["title"] or (old.get("description") or "") != ms["goal"]:
                gh(["api", "-X", "PATCH", f"{base}/milestones/{number}", *fields], dry)
                print("milestone ~", ms["title"])
        for it in ms["issues"]:
            title = issue_title(it)
            body_args = ["-f", f"title={title}", "-f", f"body={issue_body(ms, it)}", "-F", f"milestone={number}"]
            for l in it.get("labels", []):
                body_args += ["-f", f"labels[]={l}"]
            cur = issues_by_key.get(it["id"])
            if cur is None:
                gh(["api", "-X", "POST", f"{base}/issues", *body_args], dry)
                print("  issue +", title)
            elif cur["title"] != title:             # repurposed ID: new content, reopen
                gh(["api", "-X", "PATCH", f"{base}/issues/{cur['number']}", *body_args, "-f", "state=open"], dry)
                print("  issue ~", title)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-md", action="store_true")
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--repo", help="OWNER/NAME (required with --github)")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ms = load()
    if a.write_md:
        ROADMAP.write_text(write_md(ms), encoding="utf-8")
        print(f"wrote {ROADMAP.name}: {len(ms)} milestones, {sum(len(m['issues']) for m in ms)} issues")
    if a.github:
        if not a.repo:
            ap.error("--github needs --repo OWNER/NAME")
        push_github(ms, a.repo, a.dry_run)
    if not (a.write_md or a.github):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
