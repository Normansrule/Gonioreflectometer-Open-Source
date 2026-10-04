"""Forward kinematics: axis angles -> world geometry and BRDF coordinates.

World frame: origin at the measurement center (sample surface), +Z up.
A1 (camera elevation) rotates about the Y axis; the camera lives on the -X side.
A2 (light elevation) rotates about its own horizontal axis through the center;
at A3 = 0 the lamp lives on the +X side. A3 rotates the light tower about Z.
A4 rotates the sample about Z, so BRDF angles are expressed in the sample frame.

BRDF convention (CS348b): theta from the surface normal, phi azimuth in the
tangent plane; omega_i points from the surface toward the light, omega_r toward
the camera.
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .config import MachineConfig


def rot_z(deg: float) -> np.ndarray:
    c, s = math.cos(math.radians(deg)), math.sin(math.radians(deg))
    return np.array([[c, -s, 0.0], [s, c, 0.0], [0.0, 0.0, 1.0]])


def camera_dir(a1: float) -> np.ndarray:
    t = math.radians(a1)
    return np.array([-math.sin(t), 0.0, math.cos(t)])


def light_dir(a2: float, a3: float = 0.0) -> np.ndarray:
    t = math.radians(a2)
    return rot_z(a3) @ np.array([math.sin(t), 0.0, math.cos(t)])


@dataclass(frozen=True)
class ArmGeometry:
    """Polyline of an arm: tower foot -> hub -> elbow -> head (world mm)."""
    foot: np.ndarray
    hub: np.ndarray
    elbow: np.ndarray
    head: np.ndarray

    def segments(self) -> list[tuple[np.ndarray, np.ndarray]]:
        return [(self.foot, self.hub), (self.hub, self.elbow), (self.elbow, self.head)]


def camera_arm(cfg: MachineConfig, a1: float) -> ArmGeometry:
    r = cfg.working_radius_mm
    hub = np.array([0.0, -cfg.camera_tower_offset_mm, 0.0])
    d = camera_dir(a1)
    head = r * d
    return ArmGeometry(hub + np.array([0, 0, -cfg.sample_height_mm]), hub, hub + r * d, head)


def light_arm(cfg: MachineConfig, a2: float, a3: float = 0.0) -> ArmGeometry:
    r = cfg.working_radius_mm
    hub = rot_z(a3) @ np.array([0.0, cfg.light_tower_offset_mm, 0.0])
    d = light_dir(a2, a3)
    head = r * d
    return ArmGeometry(hub + np.array([0, 0, -cfg.sample_height_mm]), hub, hub + r * d, head)


def _angles(v: np.ndarray) -> tuple[float, float]:
    v = v / np.linalg.norm(v)
    theta = math.degrees(math.acos(max(-1.0, min(1.0, float(v[2])))))
    phi = math.degrees(math.atan2(float(v[1]), float(v[0])))
    return theta, phi


@dataclass(frozen=True)
class BrdfCoords:
    theta_i: float
    phi_i: float
    theta_r: float
    phi_r: float

    @property
    def delta_phi(self) -> float:
        """|phi_r - phi_i| folded to [0, 180] - the isotropic coordinate."""
        d = abs((self.phi_r - self.phi_i + 180.0) % 360.0 - 180.0)
        return d


def brdf_coords(a1: float, a2: float, a3: float = 0.0, a4: float = 0.0) -> BrdfCoords:
    """Sample-frame incident/reflected directions for the given axis angles."""
    to_sample = rot_z(-a4)
    ti, pi = _angles(to_sample @ light_dir(a2, a3))
    tr, pr = _angles(to_sample @ camera_dir(a1))
    return BrdfCoords(ti, pi, tr, pr)


def is_specular(a1: float, a2: float, a3: float = 0.0, tol_deg: float = 1e-6) -> bool:
    """True when the camera sits on the mirror direction of the light."""
    wi = light_dir(a2, a3)
    n = np.array([0.0, 0.0, 1.0])
    mirror = 2.0 * float(wi @ n) * n - wi
    wr = camera_dir(a1)
    ang = math.degrees(math.acos(max(-1.0, min(1.0, float(mirror @ wr)))))
    return ang <= tol_deg
