"""Scan plans: rings of views on the object's view sphere.

Camera elevation seen from the object = 90 - M2 (platter normal up at M2 = 90). Each ring
spins M1 through 360 deg; rings alternate direction so M1 never unwinds a full turn.
Default rings give 144 views, the image count the original brief targeted.
"""
from __future__ import annotations

from dataclasses import dataclass

from ..gantry.config import Machine


@dataclass(frozen=True)
class ScanPose:
    index: int
    ring: int
    elevation_deg: float
    pose: dict[str, float]

    @property
    def name(self) -> str:
        return f"img_{self.index:04d}.jpg"


class PlanError(ValueError):
    pass


def check_object(cfg: Machine, radius_mm: float | None = None) -> None:
    """Object must clear the light arm (keep-out) and fit the scan field of view."""
    r = float(radius_mm if radius_mm is not None else cfg.scan["object_max_radius_mm"])
    reach = cfg.ring_radius_mm - cfg.arm_radius_mm - cfg.keep_out_mm
    if r > reach:
        raise PlanError(f"object radius {r} mm > {reach} mm: would enter the light-arm keep-out")
    from .geometry import intrinsics
    k = intrinsics(cfg.for_scan(), cfg.scan["camera_distance_mm"])
    half_h_mm = (k.height / 2) / k.fy * cfg.scan["camera_distance_mm"]
    if r > 0.95 * half_h_mm:
        raise PlanError(f"object radius {r} mm does not fit the {2 * half_h_mm:.0f} mm tall field of view")
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[4] / "tools"))
    try:
        import optics
        dof = optics.scan_dof_mm(float(cfg.camera["focal_length_mm"]), float(cfg.scan["camera_distance_mm"]),
                                 float(cfg.scan["aperture_f"]), float(cfg.camera["pixel_um"]))
        if 2 * r > dof:
            raise PlanError(f"object depth {2 * r:.0f} mm exceeds the {dof:.0f} mm depth of field")
    except ImportError:                       # installed package without the repo tools
        pass


def rings_plan(cfg: Machine, rings: list[dict] | None = None, lamp_m4: float | None = None) -> list[ScanPose]:
    if cfg.installed_phase < 4:
        raise PlanError("scanning needs M2 (Phase 3) and M1 (Phase 4)")
    rings = rings or cfg.scan["rings"]
    m4 = float(lamp_m4 if lamp_m4 is not None else cfg.scan["lamp_m4_deg"])
    a2, a1 = cfg.axes["M2"], cfg.axes["M1"]
    out, idx = [], 0
    for ri, ring in enumerate(rings):
        e = float(ring["elevation_deg"])
        m2 = 90.0 - e + cfg.camera_elevation_deg      # view elevation = 90 - |M2 - camera elevation|
        if not a2.in_range(m2):
            raise PlanError(f"elevation {e} needs M2 = {m2}, outside the tilt range")
        n = int(ring["count"])
        step = 360.0 / n
        m1s = [a1.min_deg + k * step for k in range(n)]
        if ri % 2:
            m1s.reverse()
        for m1 in m1s:
            out.append(ScanPose(idx, ri, e, {"M4": m4, "M3": 0.0, "M2": m2, "M1": round(m1, 4)}))
            idx += 1
    return out


def photometric_stations(cfg: Machine, every_deg: float = 60.0, elevation_deg: float = 30.0) -> list[dict[str, float]]:
    """Object poses where the LED bank sweeps for photometric stereo (object held still)."""
    m2 = 90.0 - elevation_deg + cfg.camera_elevation_deg
    a1 = cfg.axes["M1"]
    n = int(round(360.0 / every_deg))
    return [{"M3": 0.0, "M2": m2, "M1": a1.min_deg + k * every_deg} for k in range(n)]
