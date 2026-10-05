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


def jobs(cfg: Machine) -> list[tuple[str, Callable[[], list[dict]]]]:
    out = [("Mirror check 30", lambda: inplane.mirror_sweep(30.0, span=3.0, step=0.2)),
           ("Swatch 10deg", lambda: inplane.grid(cfg, 10.0))]
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
        self.manifest = {"job": name, "started": stamp, "machine": self.cfg.name,
                         "installed_phase": self.cfg.installed_phase, "finished": False, "shots": []}
        self.g.light("white", True)
        self.write()

    def tick(self) -> None:
        """One pose per call, so STOP stays responsive."""
        if not self.running:
            return
        if self.i >= len(self.plan):
            self.g.light("white", False)
            self.running = False
            self.manifest["finished"] = True
            self.write()
            self.idle_screen(f"done {self.i} shots")
            return
        pose = self.plan[self.i]
        self.g.move(pose)
        name = f"img_{self.i:04d}.png"
        self.save(self.run_dir / name, self.cam.grab())
        self.manifest["shots"].append({"i": self.i, "pose": pose, "file": name, "t": round(self.clock(), 3)})
        self.i += 1
        if self.i % 5 == 0 or self.i == len(self.plan):
            self.write()
        self.hub.show("OpenGonio", self.jobs[self.job][0], f"{self.i}/{len(self.plan)}", "STOP=abort")

    def abort(self, why: str) -> None:
        if self.running:
            self.running = False
            self.manifest["aborted"] = why
            self.write()
        self.idle_screen(why)

    def write(self) -> None:
        (self.run_dir / "manifest.json").write_text(json.dumps(self.manifest, indent=1), encoding="utf-8")
