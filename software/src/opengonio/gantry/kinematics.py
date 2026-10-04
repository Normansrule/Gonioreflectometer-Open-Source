"""Forward kinematics for the fixed-camera layout of [R1].

World: origin = zero point, +Z up, camera fixed in direction c (on +X, elevation e).
Light:  l = Rz(M4) x  (horizontal, M4 = angle from camera to light about +Z).
Sample: R = Rz(M3) Ry(-M2) Rx(M1)  - extrinsic x-y-z Tait-Bryan rotations as in [R1];
        sample local frame: normal = local x, tangents u = local y, v = local z.
BRDF angles (theta from the normal, phi in the tangent plane) follow [R2].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .config import Machine


def _c(d: float) -> float:
    return math.cos(math.radians(d))


def _s(d: float) -> float:
    return math.sin(math.radians(d))


def rot_x(d: float) -> np.ndarray:
    return np.array([[1, 0, 0], [0, _c(d), -_s(d)], [0, _s(d), _c(d)]])


def rot_y(d: float) -> np.ndarray:
    return np.array([[_c(d), 0, _s(d)], [0, 1, 0], [-_s(d), 0, _c(d)]])


def rot_z(d: float) -> np.ndarray:
    return np.array([[_c(d), -_s(d), 0], [_s(d), _c(d), 0], [0, 0, 1]])


def camera_dir(elev_deg: float = 0.0) -> np.ndarray:
    return np.array([_c(elev_deg), 0.0, _s(elev_deg)])


def light_dir(m4: float) -> np.ndarray:
    return rot_z(m4) @ np.array([1.0, 0.0, 0.0])


def sample_rotation(m3: float = 0.0, m2: float = 0.0, m1: float = 0.0) -> np.ndarray:
    return rot_z(m3) @ rot_y(-m2) @ rot_x(m1)


def sample_normal(m3: float = 0.0, m2: float = 0.0, m1: float = 0.0) -> np.ndarray:
    return sample_rotation(m3, m2, m1)[:, 0]


@dataclass(frozen=True)
class BrdfCoords:
    theta_i: float
    phi_i: float
    theta_r: float
    phi_r: float

    @property
    def delta_phi(self) -> float:
        return abs((self.phi_r - self.phi_i + 180.0) % 360.0 - 180.0)

    @property
    def measurable(self) -> bool:
        """Both light and camera in front of the sample."""
        return self.theta_i < 90.0 and self.theta_r < 90.0


def to_sample(w: np.ndarray, R: np.ndarray) -> tuple[float, float]:
    loc = R.T @ (w / np.linalg.norm(w))
    z, x, y = loc[0], loc[1], loc[2]          # normal is local x
    theta = math.degrees(math.acos(max(-1.0, min(1.0, float(z)))))
    phi = math.degrees(math.atan2(float(y), float(x)))
    return theta, phi


def brdf_coords(cfg: Machine, pose: dict[str, float]) -> BrdfCoords:
    p = {**cfg.default_pose(), **pose}
    R = sample_rotation(p["M3"], p["M2"], p["M1"])
    ti, pi = to_sample(light_dir(p["M4"]), R)
    tr, pr = to_sample(camera_dir(cfg.camera_elevation_deg), R)
    return BrdfCoords(ti, pi, tr, pr)


def specular_m3(m4: float) -> float:
    """In-plane (M2 = 0, camera elevation 0): the sample normal bisects camera and light."""
    return m4 / 2.0 if m4 <= 180 else m4 / 2.0 - 180.0


def per_pixel_directions(cfg: Machine, pose: dict[str, float], uv_mm: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Unit incident and reflected directions for points (u, v) on the sample surface [R1].

    uv_mm: (N, 2) positions in the sample tangent plane. Returns (wi, wr) as (N, 3) world vectors.
    The sample spans a finite area, so directions vary across the image; [R1] computes them per pixel.
    """
    p = {**cfg.default_pose(), **pose}
    R = sample_rotation(p["M3"], p["M2"], p["M1"])
    pts = (R @ np.column_stack([np.zeros(len(uv_mm)), uv_mm[:, 0], uv_mm[:, 1]]).T).T
    cam = cfg.camera_distance_mm * camera_dir(cfg.camera_elevation_deg)
    lamp = cfg.light_distance_mm * light_dir(p["M4"])
    wr = cam - pts
    wi = lamp - pts
    return wi / np.linalg.norm(wi, axis=1, keepdims=True), wr / np.linalg.norm(wr, axis=1, keepdims=True)
