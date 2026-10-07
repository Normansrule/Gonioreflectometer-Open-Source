"""Standalone station: buttons + OLED pick and run a job; every image is saved with a manifest.

Runs on a Raspberry Pi Zero 2 W (no laptop) or on the laptop. The laptop later pulls the folders
(`opengonio pull`) and checks them (`opengonio verify`).

    NEXT  choose job (when idle)      START run job      STOP abort
    HOME  home axes                    LIGHT white light on/off
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from .gantry.config import Machine
from .gantry.gantry import Gantry
from .plans import inplane
from .plans.hemisphere import complete


def jobs(cfg: Machine) -> list[tuple[str, Callable[[], list[dict]]]]:
    out = [("Mirror check 30", lambda: inplane.mirror_sweep(30.0, span=3.0, step=0.2)),
           ("Swatch 10deg", lambda: inplane.grid(cfg, 10.0))]
    if "M2" in cfg.active_axes:
        from .plans.hemisphere import isotropic
        out.append(("Isotropic 15deg", lambda: isotropic(cfg, 15.0)))
    if "M1" in cfg.active_axes:
        from .plans.hemisphere import spin
        out.append(("Spin 30", lambda: spin(cfg, 30.0, 15.0)))
    if {"M1", "M2"} <= set(cfg.active_axes):
        from .scan.plan import rings_plan
        out.append(("3D scan", lambda: [sp.pose for sp in rings_plan(cfg)]))
    return out


@dataclass
class Station:
    cfg: Machine
    g: Gantry
    hub: object
    cam: object
    data_dir: Path
    save: Callable[[Path, object], None]
    clock: Callable[[], float] = time.time
    job: int = 0
    running: bool = False
    plan: list[dict] = field(default_factory=list)
    i: int = 0
    run_dir: Path | None = None
    manifest: dict = field(default_factory=dict)
    cal: object = None                    # Calibration: snapshot goes into every manifest
    scan_cam: object = None               # second camera for the 3D scan job (None: same camera)
    warm_until: float = 0.0

    def __post_init__(self):
        self.jobs = jobs(self.cfg)
        self.idle_screen()

    def idle_screen(self, msg: str = "ready") -> None:
        self.hub.show("OpenGonio", f"> {self.jobs[self.job][0]}", msg, "NEXT=job START=go")

    def handle(self, kind: str, value: str) -> None:
        if kind == "POWER" and value == "0":
            self.abort("e-stop: re-home")
            self.g.homed.clear()
            return
        if kind != "BTN":
            return
        if value == "NEXT" and not self.running:
            self.job = (self.job + 1) % len(self.jobs)
            self.idle_screen()
        elif value == "START" and not self.running:
            self.start()
        elif value == "STOP":
            self.g.stop()
            self.abort("stopped")
        elif value == "HOME" and not self.running:
            self.hub.show("OpenGonio", "homing...")
            self.g.home()
            self.idle_screen("homed")
        elif value == "LIGHT":
            self.g.toggle_light("white")

    def start(self) -> None:
        name, make = self.jobs[self.job]
        if not self.g.homed:
            self.g.home()
        self.plan, self.i, self.running = make(), 0, True
        stamp = time.strftime("%Y%m%d-%H%M%S", time.localtime(self.clock()))
        self.run_dir = Path(self.data_dir).expanduser() / f"{stamp}-{name.replace(' ', '_')}"
        self.run_dir.mkdir(parents=True, exist_ok=True)
        self.manifest = new_manifest(self.cfg, name, "white", self.cal, self.cfg.station.get("exposure_ms"), stamp)
        self.g.light("white", True)
        self.warm_until = self.clock() + float(self.cfg.lights.get("white", {}).get("warmup_s", 0.0))
        self.write()

    def tick(self) -> None:
        """One pose per call, so STOP stays responsive."""
        if not self.running:
            return
        left = self.warm_until - self.clock()
        if left > 0:                                    # lamp warm-up: brightness settles first
            self.hub.show("OpenGonio", self.jobs[self.job][0], f"lamp warm-up {left:.0f} s", "STOP=abort")
            return
        if self.manifest["reference"] is None and self.plan:
            self.manifest["reference"] = {"start": self.shoot(self.plan[0], "ref_start.png")}
            return
        if self.i >= len(self.plan):
            if self.plan:
                self.manifest["reference"]["end"] = self.shoot(self.plan[0], "ref_end.png")
            self.g.light("white", False)
            self.running = False
            self.manifest["finished"] = True
            self.write()
            self.idle_screen(f"done {self.i} shots")
            return
        self.manifest["shots"].append({"i": self.i, **self.shoot(self.plan[self.i], f"img_{self.i:04d}.png")})
        self.i += 1
        if self.i % 5 == 0 or self.i == len(self.plan):
            self.write()
        self.hub.show("OpenGonio", self.jobs[self.job][0], f"{self.i}/{len(self.plan)}", "STOP=abort")

    def shoot(self, pose: dict, name: str) -> dict:
        pose = complete(self.cfg, pose)
        self.g.move(pose)
        cam = self.scan_cam if self.scan_cam is not None and self.jobs[self.job][0] == "3D scan" else self.cam
        self.save(self.run_dir / name, cam.grab())
        return {"pose": pose, "file": name, "t": round(self.clock(), 3)}

    def abort(self, why: str) -> None:
        if self.running:
            self.running = False
            self.manifest["aborted"] = why
            self.write()
        self.idle_screen(why)

    def write(self) -> None:
        (self.run_dir / "manifest.json").write_text(json.dumps(self.manifest, indent=1), encoding="utf-8")


SCHEMA = 1        # bump when manifest.json changes shape; old runs keep their number


def new_manifest(cfg: Machine, name: str, light: str | None, cal=None, exposure_ms: float | None = None,
                 stamp: str | None = None) -> dict:
    """manifest.json header: everything needed to re-process a run later without this laptop."""
    return {"schema": SCHEMA, "job": name, "started": stamp or time.strftime("%Y%m%d-%H%M%S"),
            "machine": cfg.name, "installed_phase": cfg.installed_phase, "light": light, "exposure_ms": exposure_ms,
            "units": {"angles": "deg, true (after calibration offsets)", "image": "8-bit counts",
                      "spectral": "AS7341 raw counts"},
            "calibration": cal.snapshot() if cal is not None else None,
            "reference": None, "finished": False, "shots": []}


def run_plan(g: Gantry, cam, plan: list[dict], out_dir: Path, save: Callable[[Path, object], None], name: str,
             spectral: Callable[[], list[int]] | None = None, light: str | None = "white", cal=None,
             reference: bool = True, warmup_s: float | None = None, sleep: Callable[[float], None] = time.sleep,
             exposure_ms: float | None = None, exposures: list[float] | None = None) -> Path:
    """Laptop capture: move through `plan`, one image (and optional spectral reading) per pose.
    Same folder format as the station: img_NNNN.png + manifest.json (+ spectral.csv).
    reference: the first pose is shot again before and after the run (ref_start / ref_end) so
    `verify` can measure lamp drift. light=None keeps the lamp off (dark frames).
    exposures: one exposure (ms) per pose, for the camera-response test (`capture linearity`)."""
    out = Path(out_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    man = new_manifest(g.cfg, name, light, cal, exposure_ms)
    spec_rows = []

    def shoot(pose: dict, f: str, exp: float | None = None) -> dict:
        pose = complete(g.cfg, pose)
        g.move(pose)
        shot = {"pose": pose, "file": None}
        if exp is not None:
            cam.set_exposure_ms(exp)
            shot["exposure_ms"] = exp
        if cam is not None:
            save(out / f, cam.grab())
            shot["file"] = f
        if spectral is not None:
            shot["spectral"] = spectral()
        return shot

    if light:
        g.light(light, True)
        sleep(g.cfg.lights.get(light, {}).get("warmup_s", 0.0) if warmup_s is None else warmup_s)
    try:
        if reference and plan:
            man["reference"] = {"start": shoot(plan[0], "ref_start.png")}
        for i, pose in enumerate(plan):
            shot = {"i": i, **shoot(pose, f"img_{i:04d}.png", exposures[i] if exposures else None)}
            if "spectral" in shot:
                spec_rows.append([i, *[pose.get(k, 0.0) for k in ("M4", "M3", "M2", "M1")], *shot["spectral"]])
            man["shots"].append(shot)
        if reference and plan:
            man["reference"]["end"] = shoot(plan[0], "ref_end.png")
        man["finished"] = True
    finally:
        if light:
            g.light(light, False)
        if exposures and exposure_ms:
            cam.set_exposure_ms(exposure_ms)
        (out / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
        if spec_rows:
            head = "i,M4,M3,M2,M1," + ",".join(SPECTRAL_CHANNELS)
            (out / "spectral.csv").write_text(head + "\n" + "\n".join(",".join(str(x) for x in r) for r in spec_rows) + "\n")
    return out


def run_warmup(g: Gantry, cam, out_dir: Path, minutes: float = 10.0, every_s: float = 10.0, tol_pct: float = 0.5,
               sleep: Callable[[float], None] = time.sleep, light: str = "white") -> dict:
    """Lamp warm-up (M18.2): PTFE or grey card at 45:0, one frame every `every_s` s with the lamp on.
    settle_s = first time after which every frame stays within tol_pct of the last one -> lights.<light>.warmup_s."""
    from .imageio import centre_mean
    out = Path(out_dir).expanduser()
    out.mkdir(parents=True, exist_ok=True)
    g.move({"M4": 45.0, "M3": 0.0})
    g.light(light, True)
    rows = []
    try:
        for k in range(int(minutes * 60 / every_s) + 1):
            if k:
                sleep(every_s)
            rows.append((k * every_s, centre_mean(cam.grab())))
    finally:
        g.light(light, False)
    final = rows[-1][1]
    ok = [abs(v - final) <= tol_pct / 100 * final for _, v in rows]
    k = next(i for i in range(len(ok)) if all(ok[i:]))
    (out / "warmup.csv").write_text("t_s,centre_mean\n" + "".join(f"{t:g},{v:.3f}\n" for t, v in rows), encoding="utf-8")
    return {"settle_s": rows[k][0], "change_pct": round(100 * (final - rows[0][1]) / final, 2), "csv": str(out / "warmup.csv"),
            "set": f"software/config/machine.yaml -> lights.{light}.warmup_s: {max(rows[k][0], every_s):g}"}


SPECTRAL_CHANNELS = ["F1_415", "F2_445", "F3_480", "F4_515", "F5_555", "F6_590", "F7_630", "F8_680", "CLEAR", "NIR"]
