#!/usr/bin/env python3
"""Roadmap tooling from .github/milestones.yml (single source of truth).

    python tools/roadmap.py --write-md                 # regenerate ROADMAP.md
    python tools/roadmap.py --github [--repo OWNER/NAME] [--dry-run]
        create labels, milestones and one checklist issue per roadmap item with the GitHub CLI.
        Safe to re-run: existing milestones/issues (matched by title) are skipped.

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


def gh(args: list[str], dry: bool, capture: bool = True) -> str:
    if dry:
        print("DRY:", " ".join(args[:6]), "...")
        return "[]"
    res = subprocess.run(["gh", *args], check=True, text=True, capture_output=capture)
    return res.stdout


def push_github(milestones: list[dict], repo: str | None, dry: bool) -> None:
    r = ["--repo", repo] if repo else []
    repo_path = repo or json.loads(gh(["repo", "view", "--json", "nameWithOwner"], dry) or "{}").get("nameWithOwner", "OWNER/REPO")
    labels = sorted({l for ms in milestones for it in ms["issues"] for l in it.get("labels", [])})
    for l in labels:
        colour = LABEL_COLOURS.get(l, "ededed")
        gh(["label", "create", l, "--color", colour, "--force", *r], dry)
    existing_ms = {m["title"]: m["number"] for m in json.loads(gh(["api", f"repos/{repo_path}/milestones?state=all&per_page=100"], dry) or "[]")}
    existing_issues = {i["title"] for i in json.loads(gh(["issue", "list", "--state", "all", "--limit", "500", "--json", "title", *r], dry) or "[]")}
    start = date.today()
    for ms in milestones:
        if ms["title"] not in existing_ms:
            fields = ["-f", f"title={ms['title']}", "-f", f"description={ms['goal']}"]
            if ms.get("due_weeks"):
                start += timedelta(weeks=ms["due_weeks"])
                fields += ["-f", f"due_on={start.isoformat()}T23:59:59Z"]
            gh(["api", f"repos/{repo_path}/milestones", "-X", "POST", *fields], dry)
            print("milestone:", ms["title"])
        for it in ms["issues"]:
            title = issue_title(it)
            if title in existing_issues:
                continue
            args = ["issue", "create", "--title", title, "--body", issue_body(ms, it), "--milestone", ms["title"], *r]
            for l in it.get("labels", []):
                args += ["--label", l]
            gh(args, dry)
            print("  issue:", title)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-md", action="store_true")
    ap.add_argument("--github", action="store_true")
    ap.add_argument("--repo")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    ms = load()
    if a.write_md:
        ROADMAP.write_text(write_md(ms), encoding="utf-8")
        print(f"wrote {ROADMAP.name}: {len(ms)} milestones, {sum(len(m['issues']) for m in ms)} issues")
    if a.github:
        push_github(ms, a.repo, a.dry_run)
    if not (a.write_md or a.github):
        ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
