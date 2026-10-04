"""High-level gantry control on top of Klipper manual_steppers.

One Klipper unit = one output degree (rotation_distance = 360 / gear_ratio), so
every command here is in degrees. Coordinated moves scale each axis speed so all
axes finish together; the straight joint-space path is collision-checked first.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .collision import path_is_safe, pose_is_safe
from .config import MachineConfig
from .moonraker import GcodeSink

# Homing order keeps the arms apart: elevations go to their grazing ends first.
HOME_ORDER = ("A1", "A2", "A3", "A4")


class GantryError(RuntimeError):
    pass


@dataclass
class Gantry:
    cfg: MachineConfig
    sink: GcodeSink
    position: dict[str, float] = field(default_factory=dict)
    homed: set[str] = field(default_factory=set)

    @property
    def axes(self):
        return self.cfg.active_axes

    def _stepper(self, key: str) -> str:
        return self.axes[key].klipper_stepper

    # ---- homing ---------------------------------------------------------------
    def home(self, keys: tuple[str, ...] | None = None) -> None:
        order = [k for k in HOME_ORDER if k in self.axes and (keys is None or k in keys)]
        for k in order:
            a = self.axes[k]
            st = a.klipper_stepper
            span = (a.max_deg - a.min_deg) + 10.0
            # Treat the current spot as the far end so the search move can cover the full range.
            start = a.home_deg - a.home_direction * span
            self.sink.gcode(
                f"MANUAL_STEPPER STEPPER={st} ENABLE=1\n"
                f"MANUAL_STEPPER STEPPER={st} SET_POSITION={start:.4f}\n"
                f"MANUAL_STEPPER STEPPER={st} MOVE={a.home_deg:.4f} SPEED={min(5.0, a.speed_deg_s):.3f} STOP_ON_ENDSTOP=1\n"
                f"MANUAL_STEPPER STEPPER={st} SET_POSITION={a.home_deg:.4f}"
            )
            self.position[k] = a.home_deg
            self.homed.add(k)

    # ---- motion ---------------------------------------------------------------
    def validate(self, target: dict[str, float]) -> dict[str, float]:
        unknown = set(target) - set(self.axes)
        if unknown:
            raise GantryError(f"axes not installed in phase {self.cfg.installed_phase}: {sorted(unknown)}")
        for k, v in target.items():
            if k not in self.homed:
                raise GantryError(f"{k} is not homed")
            if not self.axes[k].in_range(v):
                a = self.axes[k]
                raise GantryError(f"{k}={v} outside [{a.min_deg}, {a.max_deg}]")
        end = {**self.position, **target}
        if not pose_is_safe(self.cfg, end):
            raise GantryError(f"target pose violates the {self.cfg.keep_out_mm} mm keep-out: {end}")
        ok, bad = path_is_safe(self.cfg, self.position, end)
        if not ok:
            raise GantryError(f"path crosses the keep-out near {bad}")
        return end

    def move(self, target: dict[str, float], speed_scale: float = 1.0) -> None:
        end = self.validate(target)
        deltas = {k: abs(end[k] - self.position[k]) for k in target if abs(end[k] - self.position[k]) > 1e-9}
        if not deltas:
            return
        # Time for the slowest axis, then every axis is slowed to match it.
        t = max(d / (self.axes[k].speed_deg_s * speed_scale) for k, d in deltas.items())
        keys = list(deltas)
        lines = []
        for i, k in enumerate(keys):
            speed = max(deltas[k] / t, 0.01)
            sync = "" if i == len(keys) - 1 else " SYNC=0"
            lines.append(f"MANUAL_STEPPER STEPPER={self._stepper(k)} MOVE={end[k]:.4f} SPEED={speed:.4f}{sync}")
        self.sink.gcode("\n".join(lines))
        self.position.update({k: end[k] for k in keys})

    def light(self, name: str, on: bool) -> None:
        pins = self.cfg.active_lights
        if name not in pins:
            raise GantryError(f"light '{name}' not installed")
        self.sink.gcode(f"SET_PIN PIN={pins[name]} VALUE={1 if on else 0}")

    def disable(self) -> None:
        """Drivers off. Position is no longer trusted until re-homed or encoder-verified."""
        self.sink.gcode("M84")
        self.homed.clear()

    def estop(self) -> None:
        self.sink.emergency_stop()
        self.homed.clear()
