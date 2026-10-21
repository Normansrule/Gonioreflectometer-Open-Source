"""Which pixels are valid sample signal at a given pose: the sample, inside the lamp's fully lit spot, facing the camera.

Every pixel's ray from the camera is intersected with the sample plane (thin-lens camera focused at the zero point,
field from camera.focal_length_mm / pixel_um / width / height). A pixel counts when the hit point lies
  - on the sample (|u|, |v| <= sample.size_mm / 2 x sample.roi_fraction), and
  - inside the lamp's umbra (distance to the beam axis <= lights.<light>.umbra_radius_mm x sample.lit_fraction).
A pose is usable when the valid area is at least sample.min_area_mm2. The spread of viewing and incidence directions
over the valid pixels is reported: that is the angular acceptance of the measurement (not the motor step).
The sample is assumed centred on the zero point (checked in M17.4); the umbra radius is the nominal value from the
lamp geometry until measured.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .gantry.config import Machine
from .gantry.kinematics import camera_dir, light_dir, sample_rotation

DEFAULTS = {"size_mm": 50.0, "roi_fraction": 0.8, "lit_fraction": 0.9, "min_area_mm2": 25.0}


@dataclass
class Roi:
    mask: np.ndarray            # bool, image shape (H, W)
    valid: bool
    reason: str
    area_mm2: float
    view_spread_deg: float      # full angle between extreme viewing directions over the mask
    incidence_spread_deg: float

    def summary(self) -> dict:
        return {"valid": self.valid, "reason": self.reason, "area_mm2": round(self.area_mm2, 1), "pixels": int(self.mask.sum()),
                "view_spread_deg": round(self.view_spread_deg, 2), "incidence_spread_deg": round(self.incidence_spread_deg, 2)}


def field_mm(cfg: Machine) -> tuple[float, float]:
    """Object-side field of view (width, height) in mm at the measuring distance."""
    c = cfg.camera
    f = float(c.get("focal_length_mm", 16.0))
    m = f / (cfg.camera_distance_mm - f)
    px = float(c.get("pixel_um", 1.55)) / 1000.0
    return float(c.get("width", 3840)) * px / m, float(c.get("height", 3032)) * px / m


def _basis(cfg: Machine):
    c = camera_dir(cfg.camera_elevation_deg)
    z = -c
    x = np.cross(z, [0.0, 0.0, 1.0])
    x /= np.linalg.norm(x)
    y = np.cross(z, x)
    return cfg.camera_distance_mm * c, x, y, z


def sample_roi(cfg: Machine, pose: dict[str, float], shape, light: str = "white", max_grid: int = 256) -> Roi:
    h, w = int(shape[0]), int(shape[1])
    s = {**DEFAULTS, **(getattr(cfg, "sample", None) or {})}
    p = {**cfg.default_pose(), **pose}
    R = sample_rotation(p["M3"], p["M2"], p["M1"])
    n, tu, tv = R[:, 0], R[:, 1], R[:, 2]
    C, xc, yc, zc = _basis(cfg)
    fw, fh = field_mm(cfg)
    step = max(1, int(math.ceil(max(h, w) / max_grid)))                  # coarse grid, then expanded to full size
    rows = np.arange(0, h, step) + step / 2
    cols = np.arange(0, w, step) + step / 2
    u = (cols - w / 2) * fw / w
    v = (rows - h / 2) * fh / h
    U, V = np.meshgrid(u, v)
    d = cfg.camera_distance_mm
    dirs = zc[None, None, :] + (U[..., None] / d) * xc + (V[..., None] / d) * yc
    dn = dirs @ n
    with np.errstate(divide="ignore", invalid="ignore"):
        t = -(C @ n) / dn
    pts = C + t[..., None] * dirs
    facing = (dn < 0) & (t > 0)
    half = 0.5 * float(s["size_mm"]) * float(s["roi_fraction"])
    on_sample = facing & (np.abs(pts @ tu) <= half) & (np.abs(pts @ tv) <= half)
    lcfg = cfg.lights.get(light, {})
    l = light_dir(p["M4"], cfg.light_elevation(light))
    along = pts @ l
    perp = np.linalg.norm(pts - along[..., None] * l, axis=-1)
    r_lit = float(lcfg.get("umbra_radius_mm", 1e9)) * float(s["lit_fraction"])
    lit = (perp <= r_lit) if float(l @ n) > 0 else np.zeros_like(perp, dtype=bool)   # lamp must face the sample
    coarse = on_sample & lit
    mask = np.repeat(np.repeat(coarse, step, axis=0), step, axis=1)[:h, :w]
    area = float(coarse.sum()) * (step * fw / w) * (step * fh / h)
    view_spread = inc_spread = 0.0
    if coarse.any():
        q = pts[coarse]
        vd = C - q
        vd /= np.linalg.norm(vd, axis=1, keepdims=True)
        L = cfg.light_distance_mm * l
        ld = L - q
        ld /= np.linalg.norm(ld, axis=1, keepdims=True)
        view_spread = _spread(vd)
        inc_spread = _spread(ld)
    cos_r, cos_i = float(-zc @ n), float(l @ n)
    if cos_r <= 0.0:
        reason = "sample faces away from the camera"
    elif cos_i <= 0.0:
        reason = "lamp behind the sample"
    elif area < float(s["min_area_mm2"]):
        reason = f"only {area:.1f} mm2 of lit sample in view (< {s['min_area_mm2']} mm2)"
    else:
        reason = ""
    return Roi(mask, reason == "", reason, area, view_spread, inc_spread)


def _spread(d: np.ndarray) -> float:
    """Full angle of the cone of unit vectors d (largest angle from the mean direction, doubled)."""
    m = d.mean(axis=0)
    m /= np.linalg.norm(m)
    return 2.0 * math.degrees(math.acos(float(np.clip((d @ m).min(), -1.0, 1.0))))
