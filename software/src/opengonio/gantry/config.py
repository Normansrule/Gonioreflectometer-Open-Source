"""Load and validate config/machine.yaml (axes are data; phases gate them)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[3] / "config" / "machine.yaml"
MICROSTEPS_PER_REV = 200 * 16


class ConfigError(ValueError):
    pass


@dataclass(frozen=True)
class Axis:
    key: str
    name: str
    fluidnc_axis: str
    phase: int
    min_deg: float
    max_deg: float
    home_deg: float
    gear_ratio: float

    @property
    def steps_per_deg(self) -> float:
        """FluidNC steps_per_mm, used as steps per output degree."""
        return MICROSTEPS_PER_REV * self.gear_ratio / 360.0

    @property
    def resolution_deg(self) -> float:
        return 1.0 / self.steps_per_deg

    def in_range(self, deg: float) -> bool:
        return self.min_deg - 1e-9 <= deg <= self.max_deg + 1e-9


@dataclass(frozen=True)
class Machine:
    name: str
    installed_phase: int
    camera_distance_mm: float
    camera_elevation_deg: float
    light_distance_mm: float
    ring_radius_mm: float
    camera_head_radius_mm: float
    lamp_head_radius_mm: float
    arm_radius_mm: float
    keep_out_mm: float
    min_phase_angle_deg: float
    repeatability_target_deg: float
    axes: dict[str, Axis]
    controller: dict[str, Any] = field(default_factory=dict)
    hub: dict[str, Any] = field(default_factory=dict)
    camera: dict[str, Any] = field(default_factory=dict)
    lights: dict[str, dict] = field(default_factory=dict)
    scan: dict[str, Any] = field(default_factory=dict)
    station: dict[str, Any] = field(default_factory=dict)

    @property
    def active_axes(self) -> dict[str, Axis]:
        order = ["M4", "M3", "M2", "M1"]
        return {k: self.axes[k] for k in order if k in self.axes and self.axes[k].phase <= self.installed_phase}

    @property
    def active_lights(self) -> dict[str, int]:
        return {k: v["output"] for k, v in self.lights.items() if v["phase"] <= self.installed_phase}

    def light_elevation(self, name: str) -> float:
        return float(self.lights.get(name, {}).get("elevation_deg", 0.0))

    def for_scan(self) -> "Machine":
        """Camera slid to the scan position on the outrigger (phase 11)."""
        return replace(self, camera_distance_mm=float(self.scan["camera_distance_mm"]))

    def with_phase(self, phase: int) -> "Machine":
        return replace(self, installed_phase=phase)

    def default_pose(self) -> dict[str, float]:
        """Pose assumed for axes that are not installed yet."""
        return {"M4": 90.0, "M3": 0.0, "M2": 0.0, "M1": 0.0}


def load_config(path: str | Path = DEFAULT_CONFIG) -> Machine:
    raw = yaml.safe_load(Path(path).read_text())
    m = raw["machine"]
    axes = {}
    for k, d in raw["axes"].items():
        a = Axis(k, d["name"], d["fluidnc_axis"].upper(), int(d["phase"]), float(d["min_deg"]),
                 float(d["max_deg"]), float(d["home_deg"]), float(d["gear_ratio"]))
        if a.min_deg >= a.max_deg or not a.in_range(a.home_deg):
            raise ConfigError(f"{k}: bad range or home")
        if a.home_deg not in (a.min_deg, a.max_deg):
            raise ConfigError(f"{k}: home switch must sit at a range end (FluidNC soft limits)")
        axes[k] = a
    letters = [a.fluidnc_axis for a in axes.values()]
    if len(set(letters)) != len(letters):
        raise ConfigError("fluidnc_axis letters must be unique")
    return Machine(
        name=m["name"], installed_phase=int(m["installed_phase"]),
        camera_distance_mm=float(m["camera_distance_mm"]), camera_elevation_deg=float(m["camera_elevation_deg"]),
        light_distance_mm=float(m["light_distance_mm"]), ring_radius_mm=float(m["ring_radius_mm"]),
        camera_head_radius_mm=float(m["camera_head_radius_mm"]), lamp_head_radius_mm=float(m["lamp_head_radius_mm"]),
        arm_radius_mm=float(m["arm_radius_mm"]), keep_out_mm=float(m["keep_out_mm"]),
        min_phase_angle_deg=float(m["min_phase_angle_deg"]), repeatability_target_deg=float(m["repeatability_target_deg"]),
        axes=axes, controller=raw.get("controller", {}), hub=raw.get("hub", {}),
        camera=raw.get("camera", {}), lights=raw.get("lights", {}), scan=raw.get("scan", {}),
        station=raw.get("station", {}),
    )
