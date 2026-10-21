"""High-level control: home, validated coordinated moves, lights, sleep.

All axes are degrees (controller steps_per_mm = steps per degree). A single G1 move
interpolates every axis linearly, so the collision check of the straight joint path
is exactly the path the machine takes. Machine coordinates via G53 [R20].
Angles here are TRUE angles: offsets from calibration.yaml (true = commanded + offset) are removed
only in the G-code words, so plans, manifests and collision checks never see them.

Position trust: after every move the controller's reported machine position is compared with the target
(`position_tol_deg`, default 0.01 deg). A mismatch, an alarm, a reset or a failed command clears `homed`
(position no longer trusted) and raises GantryError, so a run can never record a pose it did not reach.
The controller position is still not proof the motor did not skip steps: repeatability tests and encoders do that.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .collision import path_is_safe, pose_is_safe
from .config import Machine
from .fluidnc import FluidNC, FluidNCError, dialect


# Lights the code refuses to switch on whatever machine.yaml says (an older or edited config can't lift the block).
BLOCKED_LIGHTS = {"multispectral": "LED bank driver circuit not reviewed (audit F09, phases/10-color/design.md)"}


def blocked_output_lines(cfg: Machine) -> set[str]:
    """Raw G-code that would switch a blocked light on (refused by `opengonio send`)."""
    return {f"M62 P{cfg.lights[n]['output']}" for n in BLOCKED_LIGHTS if n in cfg.lights}


def switches_blocked_output(cfg: Machine, line: str) -> bool:
    """True if a raw line turns a blocked output on in any spelling: M62/M64 (synchronised / immediate), with or
    without spaces, leading zeros or decimals in the P word (M62P3, M064 P3, M62 P3.0)."""
    import re
    ports = {int(cfg.lights[n]["output"]) for n in BLOCKED_LIGHTS if n in cfg.lights}
    txt = re.sub(r"\s+", "", line.upper().split(";")[0])
    txt = re.sub(r"\(.*?\)", "", txt)
    for m in re.finditer(r"M0*6([24])(?![0-9])", txt):
        p = re.search(r"P(-?[0-9.]+)", txt[m.end():])
        if p and float(p.group(1)) in ports:
            return True
    return False


class GantryError(RuntimeError):
    pass


@dataclass
class Gantry:
    cfg: Machine
    nc: FluidNC
    position: dict[str, float] = field(default_factory=dict)
    homed: set[str] = field(default_factory=set)
    light_state: dict[str, bool] = field(default_factory=dict)
    offsets: dict[str, float] = field(default_factory=dict)      # calibration.yaml angle_offset_deg
    reported: dict[str, float] = field(default_factory=dict)     # last controller-reported pose (true angles)
    controller_id: str | None = None                              # `$I` answer, recorded in every manifest

    @property
    def axes(self):
        return self.cfg.active_axes

    @property
    def dialect(self) -> dict:
        return dialect(self.cfg)

    def _zero(self, k: str) -> float:
        """Commanded angle at machine position 0: home_deg when the firmware zeroes the axis at its switch (grblHAL)."""
        return self.axes[k].home_deg if self.dialect["origin_at_home"] else 0.0

    @property
    def tol(self) -> float:
        return float(self.cfg.controller.get("position_tol_deg", 0.01))

    def invalidate(self) -> None:
        """Position no longer trusted (alarm, reset, power loss, mismatch): re-home before measuring."""
        self.homed.clear()
        self.reported = {}

    def _send(self, line: str) -> list[str]:
        try:
            return self.nc.command(line)
        except FluidNCError as exc:
            self.invalidate()
            raise GantryError(f"controller refused {line!r}: {exc}; position no longer trusted, re-home") from exc

    def handshake(self) -> str:
        """Identify the controller (firmware build) before any motion; recorded with every run. Refuses a firmware
        that differs from controller.firmware: the coordinate convention (zero at the switch or home_deg) and the
        output ports depend on it, and a mismatch would move to the wrong angles while the end checks still pass."""
        lines = self._send("$I")
        self.controller_id = " | ".join(lines) or "unknown"
        txt = self.controller_id.lower()
        want = str(self.cfg.controller.get("firmware", "grblhal")).lower()
        other = {"grblhal": "fluidnc", "fluidnc": "grblhal"}.get(want)
        if other and other in txt and want not in txt:
            self.invalidate()
            raise GantryError(f"controller reports {other} but machine.yaml controller.firmware is {want}: "
                              f"set controller.firmware: {other} (and its lights output ports) before any move")
        return self.controller_id

    def _send_unlocked(self, line: str) -> list[str]:
        """grblHAL refuses G/M-code in Alarm (error:9): lamp-off and driver re-init must still go through, so clear
        the alarm with $X first. Homing is still required: the software keeps refusing moves until it has homed."""
        if not self.dialect["wake"]:                               # grblHAL
            try:
                if self.nc.status().state == "Alarm":
                    self._send("$X")
            except FluidNCError:
                pass                                               # no status: send anyway, the reply decides
        return self._send(line)

    def _true(self, mpos: dict[str, float]) -> dict[str, float]:
        """Controller machine position (commanded angles) -> true angles of the installed axes."""
        return {k: mpos[a.fluidnc_axis] + self._zero(k) + self.offsets.get(k, 0.0) for k, a in self.axes.items() if a.fluidnc_axis in mpos}

    def _settle(self, expect: dict[str, float]) -> dict[str, float]:
        """Wait for Idle, then require the reported position of every expected axis to match within tol."""
        try:
            st = self.nc.wait_idle()
        except FluidNCError as exc:
            self.invalidate()
            raise GantryError(f"move did not complete: {exc}; position no longer trusted, re-home") from exc
        got = self._true(st.mpos)
        bad = {k: (v, got.get(k)) for k, v in expect.items() if got.get(k) is None or abs(got[k] - v) > self.tol}
        if bad:
            self.invalidate()
            txt = ", ".join(f"{k}: wanted {w:.4f}, controller {g}" for k, (w, g) in bad.items())
            raise GantryError(f"end position mismatch ({txt}); position no longer trusted, re-home")
        self.reported = got
        return got

    def home(self, keys: tuple[str, ...] | None = None) -> None:
        # M4 first: moves the light to its switch beside the camera, then the stage axes.
        for k in [k for k in ("M4", "M3", "M2", "M1") if k in self.axes and (keys is None or k in keys)]:
            a = self.axes[k]
            self.homed.discard(k)
            self._send(f"$H{a.fluidnc_axis}")
            want = a.home_deg + self.offsets.get(k, 0.0)
            self._settle({k: want})
            self.position[k] = want
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

    def move(self, target: dict[str, float], feed: float | None = None) -> dict[str, float]:
        """Validated move; returns the controller-reported true pose (also in `reported`)."""
        end = self.validate(target)
        words = " ".join(f"{self.axes[k].fluidnc_axis}{v - self.offsets.get(k, 0.0) - self._zero(k):.4f}" for k, v in target.items())
        f = feed or self.cfg.controller.get("feed_deg_per_min", 600)
        self._send(f"G53 G1 {words} F{f:.0f}")
        self._send("G4 P0")             # dwell 0: its "ok" comes after the move is executed, so Idle can't be stale
        got = self._settle({k: end[k] for k in target})
        self.position.update({k: end[k] for k in target})
        return got

    def light(self, name: str, on: bool) -> None:
        outs = self.cfg.active_lights
        if name not in outs:
            raise GantryError(f"light '{name}' not installed")
        why = self.cfg.lights.get(name, {}).get("blocked") or BLOCKED_LIGHTS.get(name)
        if on and why:
            raise GantryError(f"light '{name}' is blocked: {why}")
        self._send_unlocked(f"{'M62' if on else 'M63'} P{outs[name]}")
        self.light_state[name] = on

    def all_lights_off(self) -> list[str]:
        """Switch every installed light off, each independently; returns the errors (empty = all off)."""
        errs = []
        for n in self.cfg.active_lights:
            try:
                self.light(n, False)
            except Exception as exc:                         # keep going: the others must still go off
                errs.append(f"{n} off failed: {exc}")
        return errs

    def toggle_light(self, name: str = "white") -> None:
        self.light(name, not self.light_state.get(name, False))

    def sleep(self) -> None:
        errs = self.all_lights_off()
        self.invalidate()               # holding torque gone: re-home before measuring
        self._send(self.dialect["sleep"])            # grblHAL $SLP, FluidNC $MD
        if errs:
            raise GantryError("; ".join(errs))

    def wake(self) -> None:
        if self.dialect["wake"]:
            self._send(self.dialect["wake"])         # FluidNC $ME
        else:
            self.invalidate()                        # grblHAL leaves sleep only through a reset (Alarm: re-home)
            self.nc.reset()

    def reinit_drivers(self) -> None:
        """After motor power returns the TMC2209s are back at defaults: resend config (grblHAL M122 I [R84], FluidNC $MI [R28])."""
        self.invalidate()
        self._send_unlocked(self.dialect["reinit"])

    def stop(self) -> None:
        """Soft stop: hold, then reset (the controller enters Alarm; re-home required)."""
        self.invalidate()
        self.nc.hold()
        self.nc.reset()
