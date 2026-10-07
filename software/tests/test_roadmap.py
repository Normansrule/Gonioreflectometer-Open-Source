"""Milestone file quality and the generated checklists / figures."""
import re

import roadmap
import roadmap_svg


def test_every_step_is_complete():
    stages, ms = roadmap.load()
    for m in ms:
        for s in m["steps"]:
            assert s.get("time") and re.fullmatch(r"\d+(\.\d+)? (min|h)", s["time"]), s["id"]
            assert s["do"] and s["verify"] and s.get("record"), s["id"]
            assert not any("TODO" in x for x in s["do"] + s["verify"]), s["id"]


def test_hours_and_next_step():
    assert roadmap_svg.hours("45 min") == 0.75 and roadmap_svg.hours("1.5 h") == 1.5 and roadmap_svg.hours(None) == 0
    _, ms = roadmap.load()
    m, s = roadmap_svg.next_step(ms, {"M01.1", "M01.2"})
    assert s["id"] == "M01.3"


def test_done_marks_in_checklist_and_figures():
    stages, ms = roadmap.load()
    mine = [m for m in ms if m["stage"] == "00-plan"]
    md = roadmap.stage_md(stages[0], mine, 0, 0, 0, [], done={"M01.1"})
    assert "### ✅ M01.1" in md and "1/4 steps done" in md and "#### If a check fails" in md and "**Time**" in md
    svg = roadmap_svg.stage(stages[0], mine, {"M01.1"}, "M01.2")
    assert "M01.1  ✓" in svg and "← next" in svg
    over = roadmap_svg.overview(stages, ms, {"M01.1"})
    assert "NEXT STEP" in over and "M01.2" in over


def test_issue_body_has_everything():
    _, ms = roadmap.load()
    m = ms[4]
    body = roadmap.issue_body(m, m["steps"][0])
    for part in ("### Do", "### Verify", "- [ ]", "make done id="):
        assert part in body
