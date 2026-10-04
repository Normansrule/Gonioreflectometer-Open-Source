"""High-level control: home, validated coordinated moves, lights, sleep.

All axes are degrees (FluidNC steps_per_mm = steps per degree). A single G1 move
interpolates every axis linearly, so the collision check of the straight joint path
is exactly the path the machine takes. Machine coordinates via G53 [R20].
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .collision import path_is_safe, pose_is_safe
from .config import Machine
from .fluidnc import FluidNC


class GantryError(RuntimeError):
    pass


@dataclass
class Gantry:
    cfg: Machine
    nc: FluidNC
    position: dict[str, float] = field(default_factory=dict)
    homed: set[str] = field(default_factory=set)
    light_state: dict[str, bool] = field(default_factory=dict)

    @property
    def axes(self):
        return self.cfg.active_axes

    def home(self, keys: tuple[str, ...] | None = None) -> None:
        # M4 first: moves the light to its switch beside the camera, then the stage axes.
        for k in [k for k in ("M4", "M3", "M2", "M1") if k in self.axes and (keys is None or k in keys)]:
            a = self.axes[k]
            self.nc.command(f"$H{a.fluidnc_axis}")
            self.position[k] = a.home_deg
            self.homed.add(k)
        if "M4" in self.homed:          # park the light behind the sample after homing
            self.move({"M4": 180.0})

    def validate(self, target: dict[str, float]) -> dict[str, float]:
        extra = set(target) - set(self.axes)
        if extra:
            raise GantryError(f"axes not installed in phase {self.cfg.installed_phase}: {sorted(extra)}")
        for k, v in target.items():
            if k not in self.homed:
                raise GantryError(f"{k} is not homed")
            if not self.axes[k].in_range(v):
                a = self.axes[k]
                raise GantryError(f"{k}={v} outside [{a.min_deg}, {a.max_deg}]")
        end = {**self.position, **target}
        if not pose_is_safe(self.cfg, end):
            raise GantryError(f"pose violates the {self.cfg.keep_out_mm} mm keep-out: {end}")
        ok, bad = path_is_safe(self.cfg, self.position, end)
        if not ok:
            raise GantryError(f"path crosses the keep-out near M4={bad:.1f}")
        return end

    def move(self, target: dict[str, float], feed: float | None = None) -> None:
        end = self.validate(target)
        words = " ".join(f"{self.axes[k].fluidnc_axis}{v:.4f}" for k, v in target.items())
        f = feed or self.cfg.controller.get("feed_deg_per_min", 600)
        self.nc.command(f"G53 G1 {words} F{f:.0f}")
        self.nc.wait_idle()
        self.position.update({k: end[k] for k in target})

    def light(self, name: str, on: bool) -> None:
        outs = self.cfg.active_lights
        if name not in outs:
            raise GantryError(f"light '{name}' not installed")
        self.nc.command(f"{'M62' if on else 'M63'} P{outs[name]}")
        self.light_state[name] = on

    def toggle_light(self, name: str = "white") -> None:
        self.light(name, not self.light_state.get(name, False))

    def sleep(self) -> None:
        for n in self.cfg.active_lights:
            self.light(n, False)
        self.nc.command("$MD")
        self.homed.clear()              # holding torque gone: re-home before measuring

    def wake(self) -> None:
        self.nc.command("$ME")

    def reinit_drivers(self) -> None:
        """After motor power returns the TMC2209s are back at defaults: resend config ($MI [R28])."""
        self.nc.command("$MI")
        self.homed.clear()

    def stop(self) -> None:
        """Soft stop: hold, then reset (FluidNC enters Alarm; re-home required)."""
        self.nc.hold()
        self.nc.reset()
        self.homed.clear()
