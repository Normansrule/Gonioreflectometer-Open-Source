"""Command line: `opengantry status|home|move|sleep|wake|check-pose|repeatability`.

Examples (on the Pi, Klipper + Moonraker running):
    opengantry home
    opengantry move A1=45 A2=45          # specular geometry in Phase 1
    opengantry check-pose A1=10 A2=10    # offline collision check, no hardware
    opengantry repeatability --axis A1 --cycles 20
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .gantry.collision import clearance
from .gantry.config import load_config
from .gantry.gantry import Gantry
from .gantry.moonraker import Moonraker, RecordingSink


STATE_FILE = Path.home() / ".opengantry_state.json"


def _load_state(g: Gantry, path: Path | None) -> None:
    """Positions persist between CLI calls; anything that disables drivers clears them."""
    if path and path.exists():
        d = json.loads(path.read_text())
        g.position.update(d.get("position", {}))
        g.homed.update(k for k in d.get("homed", []) if k in g.axes)


def _save_state(g: Gantry, path: Path | None) -> None:
    if path:
        path.write_text(json.dumps({"position": g.position, "homed": sorted(g.homed)}))


def _pose(items: list[str]) -> dict[str, float]:
    out = {}
    for it in items:
        k, v = it.split("=")
        out[k.upper()] = float(v)
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opengantry")
    ap.add_argument("--config", default=None)
    ap.add_argument("--dry-run", action="store_true", help="print G-code instead of sending it")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    sub.add_parser("home")
    mv = sub.add_parser("move"); mv.add_argument("pose", nargs="+")
    cp = sub.add_parser("check-pose"); cp.add_argument("pose", nargs="+")
    sub.add_parser("sleep"); sub.add_parser("wake")
    rp = sub.add_parser("repeatability")
    rp.add_argument("--axis", required=True); rp.add_argument("--cycles", type=int, default=20)
    args = ap.parse_args(argv)

    cfg = load_config(args.config) if args.config else load_config()
    if args.cmd == "check-pose":
        pose = {**{k: a.home_deg for k, a in cfg.active_axes.items()}, **_pose(args.pose)}
        c = clearance(cfg, pose)
        print(json.dumps({"pose": pose, "gap_mm": round(c.gap_mm, 1), "closest": c.between,
                          "safe": c.ok(cfg.keep_out_mm)}, indent=2))
        return 0 if c.ok(cfg.keep_out_mm) else 2

    sink = RecordingSink() if args.dry_run else Moonraker(cfg.moonraker_url, cfg.moonraker_timeout_s)
    g = Gantry(cfg, sink)
    state = STATE_FILE if not args.dry_run else None
    _load_state(g, state)
    if args.cmd == "status":
        print(json.dumps(sink.info() if isinstance(sink, Moonraker) else {"dry_run": True}, indent=2))
    elif args.cmd == "home":
        g.home()
    elif args.cmd == "move":
        if args.dry_run and not g.homed:
            g.home()
        g.move(_pose(args.pose))
    elif args.cmd == "sleep":
        sink.gcode("OG_SLEEP")
        g.homed.clear()          # drivers off: position must be re-established
    elif args.cmd == "wake":
        sink.gcode("OG_WAKE")
    elif args.cmd == "repeatability":
        from .plans.repeatability import run_repeatability  # needs encoders on the Pi
        print(json.dumps(run_repeatability(cfg, g, args.axis.upper(), args.cycles), indent=2))
    _save_state(g, state)
    if isinstance(sink, RecordingSink):
        print("\n".join(sink.scripts))
    return 0


if __name__ == "__main__":
    sys.exit(main())
