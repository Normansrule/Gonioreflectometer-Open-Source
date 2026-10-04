"""Load and validate config/machine.yaml.

Each axis is plain data. A later phase becomes available by raising
``machine.installed_phase`` - nothing in the code has to change.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path(__file__).resolve().parents[3] / "config" / "machine.yaml"


@dataclass(frozen=True)
class EncoderConfig:
    bus: int
    offset_deg: float = 0.0
    sign: int = 1
    on_motor_shaft: bool = False


@dataclass(frozen=True)
class AxisConfig:
    key: str
    name: str
    klipper_stepper: str
    phase: int
    min_deg: float
    max_deg: float
    home_deg: float
    home_direction: int
    speed_deg_s: float
    gear_ratio: float
    encoder: EncoderConfig | None = None

    @property
    def rotation_distance(self) -> float:
        """Klipper rotation_distance so one Klipper unit equals one output degree."""
        return 360.0 / self.gear_ratio

    def in_range(self, deg: float) -> bool:
        return self.min_deg - 1e-9 <= deg <= self.max_deg + 1e-9


@dataclass(frozen=True)
class MachineConfig:
    name: str
    installed_phase: int
    working_radius_mm: float
    center_tolerance_mm: float
    keep_out_mm: float
    sample_height_mm: float
    camera_tower_offset_mm: float
    light_tower_offset_mm: float
    arm_radius_mm: float
    camera_head_radius_mm: float
    lamp_head_radius_mm: float
    repeatability_target_deg: float
    axes: dict[str, AxisConfig]
    moonraker_url: str = "http://localhost:7125"
    moonraker_timeout_s: float = 120.0
    host_io: dict[str, int] = field(default_factory=dict)
    lights: dict[str, dict[str, Any]] = field(default_factory=dict)

    @property
    def active_axes(self) -> dict[str, AxisConfig]:
        """Axes whose phase is installed, in key order (A1, A2, ...)."""
        return {k: a for k, a in sorted(self.axes.items()) if a.phase <= self.installed_phase}

    @property
    def active_lights(self) -> dict[str, str]:
        return {k: v["klipper_pin"] for k, v in self.lights.items() if v["phase"] <= self.installed_phase}

    def with_phase(self, phase: int) -> "MachineConfig":
        from dataclasses import replace
        return replace(self, installed_phase=phase)


class ConfigError(ValueError):
    pass


def _axis(key: str, d: dict) -> AxisConfig:
    enc = d.get("encoder")
    a = AxisConfig(
        key=key,
        name=d["name"],
        klipper_stepper=d["klipper_stepper"],
        phase=int(d["phase"]),
        min_deg=float(d["min_deg"]),
        max_deg=float(d["max_deg"]),
        home_deg=float(d["home_deg"]),
        home_direction=int(d["home_direction"]),
        speed_deg_s=float(d["speed_deg_s"]),
        gear_ratio=float(d["gear_ratio"]),
        encoder=EncoderConfig(**enc) if enc else None,
    )
    if a.min_deg >= a.max_deg:
        raise ConfigError(f"{key}: min_deg must be < max_deg")
    if not a.in_range(a.home_deg):
        raise ConfigError(f"{key}: home_deg {a.home_deg} outside [{a.min_deg}, {a.max_deg}]")
    if a.home_direction not in (-1, 1):
        raise ConfigError(f"{key}: home_direction must be -1 or 1")
    if a.gear_ratio <= 0 or a.speed_deg_s <= 0:
        raise ConfigError(f"{key}: gear_ratio and speed must be positive")
    return a


def load_config(path: str | Path = DEFAULT_CONFIG) -> MachineConfig:
    raw = yaml.safe_load(Path(path).read_text())
    m = raw["machine"]
    axes = {k: _axis(k, v) for k, v in raw["axes"].items()}
    steppers = [a.klipper_stepper for a in axes.values()]
    if len(set(steppers)) != len(steppers):
        raise ConfigError("klipper_stepper names must be unique")
    buses = [a.encoder.bus for a in axes.values() if a.encoder]
    if len(set(buses)) != len(buses):
        raise ConfigError("each AS5600 needs its own I2C bus (fixed address 0x36)")
    mr = raw.get("moonraker", {})
    return MachineConfig(
        name=m["name"],
        installed_phase=int(m["installed_phase"]),
        working_radius_mm=float(m["working_radius_mm"]),
        center_tolerance_mm=float(m["center_tolerance_mm"]),
        keep_out_mm=float(m["keep_out_mm"]),
        sample_height_mm=float(m["sample_height_mm"]),
        camera_tower_offset_mm=float(m["camera_tower_offset_mm"]),
        light_tower_offset_mm=float(m["light_tower_offset_mm"]),
        arm_radius_mm=float(m["arm_radius_mm"]),
        camera_head_radius_mm=float(m["camera_head_radius_mm"]),
        lamp_head_radius_mm=float(m["lamp_head_radius_mm"]),
        repeatability_target_deg=float(m["repeatability_target_deg"]),
        axes=axes,
        moonraker_url=mr.get("url", "http://localhost:7125"),
        moonraker_timeout_s=float(mr.get("timeout_s", 120)),
        host_io=raw.get("host_io", {}),
        lights=raw.get("lights", {}),
    )
