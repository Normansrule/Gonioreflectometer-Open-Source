"""Scanner geometry: object frame, camera intrinsics and extrinsics from the axis angles.

Fixed camera, moving object (turntable-style capture [S9]). The object is held on the M1
platter; its frame O has z_O = platter normal (local x of the sample frame), x_O = local y,
y_O = local z, origin at the platter centre. A riser lowered by delta puts the object centre
at the zero point. Points:  p_w = R (P p_O - delta e_x),  R = Rz(M3) Ry(-M2) Rx(M1)  [R1].
Camera axes follow OpenCV/COLMAP (x right, y down, z forward) [S1][S11].
"""
from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from ..gantry.config import Machine
from ..gantry.kinematics import camera_dir, light_dir, sample_rotation

# p_local = P @ p_O : local x = z_O, local y = x_O, local z = y_O (proper rotation, det +1)
P = np.array([[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
E_X = np.array([1.0, 0.0, 0.0])


@dataclass(frozen=True)
class Intrinsics:
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int

    @property
    def K(self) -> np.ndarray:
        return np.array([[self.fx, 0.0, self.cx], [0.0, self.fy, self.cy], [0.0, 0.0, 1.0]])

    def scaled(self, s: float) -> "Intrinsics":
        return Intrinsics(self.fx * s, self.fy * s, self.cx * s, self.cy * s,
                          int(round(self.width * s)), int(round(self.height * s)))


def intrinsics(cfg: Machine, distance_mm: float | None = None) -> Intrinsics:
    """Nominal pinhole model. f is the image distance p' of the thin lens [R1]; replaced by
    the ChArUco calibration [S12] once measured."""
    c = cfg.camera
    f_mm = float(c["focal_length_mm"])
    d = distance_mm or cfg.camera_distance_mm
    p_img = 1.0 / (1.0 / f_mm - 1.0 / d)           # focused at the zero point
    f_px = p_img / (float(c["pixel_um"]) / 1000.0)
    w, h = int(c["width"]), int(c["height"])
    return Intrinsics(f_px, f_px, w / 2.0, h / 2.0, w, h)


def world_to_camera(cfg: Machine, calib=None) -> tuple[np.ndarray, np.ndarray]:
    """Rotation R_wc (rows = camera x, y, z in world) and camera centre C (world, mm).
    Uses the measured pose (scan/calibrate.py) when given, else the nominal design pose."""
    if calib is not None:
        return np.asarray(calib.R_wc, float), np.asarray(calib.C, float)
    C = cfg.camera_distance_mm * camera_dir(cfg.camera_elevation_deg)
    f = -C / np.linalg.norm(C)
    r = np.cross(f, [0.0, 0.0, 1.0])
    r /= np.linalg.norm(r)
    d = np.cross(f, r)
    return np.vstack([r, d, f]), C


def object_rotation(pose: dict[str, float]) -> np.ndarray:
    """World-from-object rotation (R P)."""
    return sample_rotation(pose.get("M3", 0.0), pose.get("M2", 0.0), pose.get("M1", 0.0)) @ P


def object_to_camera(cfg: Machine, pose: dict[str, float], platter_offset_mm: float = 0.0, calib=None):
    """(R_oc, t_oc) with p_c = R_oc p_O + t_oc  - the COLMAP 'world to camera' pose, world = object.
    platter_offset_mm (delta) = how far the object's support sits below the zero point."""
    R_wc, C = world_to_camera(cfg, calib)
    R = sample_rotation(pose.get("M3", 0.0), pose.get("M2", 0.0), pose.get("M1", 0.0))
    R_oc = R_wc @ R @ P
    t_oc = -R_wc @ (C + platter_offset_mm * (R @ E_X))
    return R_oc, t_oc


def camera_center_object(R_oc: np.ndarray, t_oc: np.ndarray) -> np.ndarray:
    return -R_oc.T @ t_oc


def platter_to_world(pose: dict[str, float], platter_offset_mm: float = 0.0) -> np.ndarray:
    """4x4 B_i: object/platter frame -> world (used by the pose calibration)."""
    R = sample_rotation(pose.get("M3", 0.0), pose.get("M2", 0.0), pose.get("M1", 0.0))
    M = np.eye(4)
    M[:3, :3] = R @ P
    M[:3, 3] = -platter_offset_mm * (R @ E_X)
    return M


def camera_elevation_in_object(cfg: Machine, pose: dict[str, float]) -> float:
    """Elevation of the camera seen from the object (deg above the platter plane)."""
    R_oc, t_oc = object_to_camera(cfg, pose)
    c = camera_center_object(R_oc, t_oc)
    return math.degrees(math.asin(c[2] / np.linalg.norm(c)))


def project(points_o: np.ndarray, K: np.ndarray, R_oc: np.ndarray, t_oc: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Pinhole projection x ~ K (R p + t). Returns (uv (N,2), depth (N,))."""
    pc = points_o @ R_oc.T + t_oc
    z = pc[:, 2]
    uv = np.full((len(z), 2), np.nan)
    front = z > 1e-9
    uv[front] = (pc[front] @ K.T)[:, :2] / z[front, None]
    return uv, z


def light_in_object(cfg: Machine, pose: dict[str, float], m4: float, light: str = "multispectral") -> np.ndarray:
    """Direction to a light (distant-light approximation) in the object frame."""
    lw = light_dir(m4, cfg.light_elevation(light))
    return object_rotation(pose).T @ lw


def light_position_object(cfg: Machine, pose: dict[str, float], m4: float, light: str = "multispectral",
                          platter_offset_mm: float = 0.0) -> np.ndarray:
    """Light position (mm) in the object frame, for near-light photometric stereo [S14]."""
    pw = cfg.light_distance_mm * light_dir(m4, cfg.light_elevation(light))
    B = platter_to_world(pose, platter_offset_mm)
    return B[:3, :3].T @ (pw - B[:3, 3])


def rotmat_to_quat(R: np.ndarray) -> np.ndarray:
    """Hamilton quaternion (w, x, y, z), w >= 0, as COLMAP expects [S1]."""
    m = R
    tr = m[0, 0] + m[1, 1] + m[2, 2]
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = [0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s]
    elif m[0, 0] > m[1, 1] and m[0, 0] > m[2, 2]:
        s = math.sqrt(1.0 + m[0, 0] - m[1, 1] - m[2, 2]) * 2
        q = [(m[2, 1] - m[1, 2]) / s, 0.25 * s, (m[0, 1] + m[1, 0]) / s, (m[0, 2] + m[2, 0]) / s]
    elif m[1, 1] > m[2, 2]:
        s = math.sqrt(1.0 + m[1, 1] - m[0, 0] - m[2, 2]) * 2
        q = [(m[0, 2] - m[2, 0]) / s, (m[0, 1] + m[1, 0]) / s, 0.25 * s, (m[1, 2] + m[2, 1]) / s]
    else:
        s = math.sqrt(1.0 + m[2, 2] - m[0, 0] - m[1, 1]) * 2
        q = [(m[1, 0] - m[0, 1]) / s, (m[0, 2] + m[2, 0]) / s, (m[1, 2] + m[2, 1]) / s, 0.25 * s]
    q = np.array(q)
    q /= np.linalg.norm(q)
    return q if q[0] >= 0 else -q


def quat_to_rotmat(q: np.ndarray) -> np.ndarray:
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
        [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
        [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)],
    ])
