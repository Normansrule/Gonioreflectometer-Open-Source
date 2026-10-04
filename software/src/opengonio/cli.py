"""opengonio command line.

    opengonio check-pose M4=40 M3=20         offline: BRDF angles + collision check
    opengonio plan inplane --step 10         offline: list Phase 1 poses
    opengonio --dry-run move M4=60 M3=30     print the G-code instead of sending it
    opengonio home | move ... | light on|off | sleep | wake | status
    opengonio panel                          run the button panel (Pico hub) loop
"""
from __future__ import annotations

import argparse
import json
import sys

from .gantry.collision import clearance_mm, min_safe_m4, pose_is_safe
from .gantry.config import load_config
from .gantry.fluidnc import FluidNC, RecordingTransport
from .gantry.gantry import Gantry
from .gantry.kinematics import brdf_coords
from .plans import inplane


def _pose(items: list[str]) -> dict[str, float]:
    return {k.upper(): float(v) for k, v in (i.split("=") for i in items)}


def _transport(cfg, dry: bool):
    if dry:
        return RecordingTransport()
    c = cfg.controller
    if c.get("transport", "serial") == "tcp":
        from .gantry.fluidnc import TcpTransport
        return TcpTransport(c.get("host", "fluidnc.local"), int(c.get("tcp_port", 23)))
    from .gantry.fluidnc import SerialTransport
    return SerialTransport(c.get("port", "auto"), int(c.get("baud", 115200)))


def _scan_offline(cfg, a) -> int:
    from .scan import demo
    from .scan.colmap import write_model
    from .scan.geometry import intrinsics
    from .scan.plan import check_object, rings_plan
    cfg4 = cfg.with_phase(max(cfg.installed_phase, 4))
    if a.action == "plan":
        check_object(cfg4)
        plan = rings_plan(cfg4)
        print(json.dumps({"views": len(plan), "rings": cfg4.scan["rings"],
                          "first": plan[0].pose, "last": plan[-1].pose}, indent=2))
    elif a.action == "sync-ids":
        from .scan.colmap import sync_image_ids
        print(f"updated {sync_image_ids(a.db, a.model)} image IDs")
    elif a.action == "export-colmap":
        plan = rings_plan(cfg4)
        K = intrinsics(cfg4.for_scan(), cfg4.scan["camera_distance_mm"])
        calib = None
        if cfg4.scan.get("calibration"):
            from .scan.calibrate import CameraCalibration
            calib = CameraCalibration.load(cfg4.scan["calibration"])
        out = write_model(f"{a.out}/sparse_known", cfg4.for_scan(), plan, K,
                          float(cfg4.scan["platter_offset_mm"]), calib)
        print(f"wrote {out} ({len(plan)} images) and {a.out}/run_colmap.sh")
    elif a.action == "demo":
        print(json.dumps(demo.run(cfg4, a.out), indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="opengonio")
    ap.add_argument("--config")
    ap.add_argument("--dry-run", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)
    cp = sub.add_parser("check-pose"); cp.add_argument("pose", nargs="+")
    pl = sub.add_parser("plan"); pl.add_argument("kind", choices=["inplane", "mirror"])
    pl.add_argument("--step", type=float, default=10.0); pl.add_argument("--theta", type=float, default=30.0)
    sub.add_parser("home"); sub.add_parser("status"); sub.add_parser("sleep"); sub.add_parser("wake")
    mv = sub.add_parser("move"); mv.add_argument("pose", nargs="+")
    li = sub.add_parser("light"); li.add_argument("state", choices=["on", "off"]); li.add_argument("--name", default="white")
    sub.add_parser("panel")
    sc = sub.add_parser("scan", help="Phase 6 photo scanner")
    sc.add_argument("action", choices=["plan", "export-colmap", "demo", "run", "calibrate", "sync-ids"])
    sc.add_argument("--db", default="database.db")
    sc.add_argument("--model", default="sparse_known")
    sc.add_argument("--background", action="store_true", help="capture the empty-platter pass")
    sc.add_argument("--out", default="scan_out")
    sc.add_argument("--exposure-ms", type=float, default=20.0)
    a = ap.parse_args(argv)
    cfg = load_config(a.config) if a.config else load_config()

    if a.cmd == "check-pose":
        pose = {**cfg.default_pose(), **_pose(a.pose)}
        b = brdf_coords(cfg, pose)
        print(json.dumps({"pose": pose, "theta_i": round(b.theta_i, 3), "theta_r": round(b.theta_r, 3),
                          "delta_phi": round(b.delta_phi, 3), "measurable": b.measurable,
                          "clearance_mm": round(clearance_mm(cfg, pose["M4"]), 1),
                          "min_safe_M4": min_safe_m4(cfg), "safe": pose_is_safe(cfg, pose)}, indent=2))
        return 0 if pose_is_safe(cfg, pose) else 2
    if a.cmd == "plan":
        poses = inplane.grid(cfg, a.step) if a.kind == "inplane" else inplane.mirror_sweep(a.theta)
        print(json.dumps(poses))
        return 0

    if a.cmd == "scan" and a.action not in ("run", "calibrate"):
        return _scan_offline(cfg, a)

    t = _transport(cfg, a.dry_run)
    g = Gantry(cfg, FluidNC(t))
    if a.dry_run:                      # pretend everything is homed at its home position
        g.position = {k: ax.home_deg for k, ax in cfg.active_axes.items()}
        g.homed = set(cfg.active_axes)
    if a.cmd == "home":
        g.home()
    elif a.cmd == "move":
        if not a.dry_run:
            g.home()                   # positions are not persisted between CLI calls
        g.move(_pose(a.pose))
    elif a.cmd == "light":
        g.light(a.name, a.state == "on")
    elif a.cmd == "sleep":
        g.sleep()
    elif a.cmd == "wake":
        g.wake()
    elif a.cmd == "status":
        print(g.nc.status())
    elif a.cmd == "panel":  # pragma: no cover - hardware loop
        from .gantry.hub import Hub
        from .gantry.panel import Panel
        hub = Hub(cfg.hub.get("port", "auto"), int(cfg.hub.get("baud", 115200)))
        panel = Panel(g, inplane.grid(cfg, 10.0))
        print("panel ready: HOME START STOP LIGHT NEXT (PAUSE is on the E4)")
        hub.send("POWER?")
        while True:
            ev = hub.poll()
            if ev:
                panel.handle(ev.kind, ev.value)
                print(panel.log[-1] if panel.log else ev)
            panel.tick()
    elif a.cmd == "scan":  # pragma: no cover - hardware
        from .camera.uvc import UvcCamera
        from .gantry.hub import Hub
        from .scan.run import run_scan
        c = cfg.camera
        g.home()
        if a.action == "calibrate":
            from .scan.run import calibrate_scan
            calibrate_scan(cfg, g, UvcCamera(int(c["index"]), int(c["width"]), int(c["height"])),
                           f"{a.out}/scan_calibration.yaml")
            return 0
        run_scan(cfg, g, UvcCamera(int(c["index"]), int(c["width"]), int(c["height"])),
                 Hub(cfg.hub.get("port", "auto")), a.out, a.exposure_ms, background=a.background)
    if isinstance(t, RecordingTransport):
        print("\n".join(t.lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
