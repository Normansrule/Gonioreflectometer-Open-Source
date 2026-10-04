"""Scan-mode pose calibration: measure where the camera really is.

A ChArUco board [S12] fixed on the platter is seen at n kinematic poses q_i. OpenCV solvePnP
[S11] gives the board-to-camera transform A_i. With X = world-to-camera (unknown mounting) and
Y = board-to-platter (unknown placement), the chain is

    A_i = X . B_i . Y,      B_i = platter-to-world from the axes (geometry.object_rotation)

an AX = YB-type problem. We solve X and Y jointly by Gauss-Newton on SE(3) (numeric Jacobian).
X replaces the nominal camera pose in every scan; Y is discarded (board placement).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import yaml


def hat(w: np.ndarray) -> np.ndarray:
    return np.array([[0, -w[2], w[1]], [w[2], 0, -w[0]], [-w[1], w[0], 0]])


def exp_so3(w: np.ndarray) -> np.ndarray:
    th = np.linalg.norm(w)
    if th < 1e-12:
        return np.eye(3) + hat(w)
    k = hat(w / th)
    return np.eye(3) + np.sin(th) * k + (1 - np.cos(th)) * k @ k


def log_so3(R: np.ndarray) -> np.ndarray:
    c = np.clip((np.trace(R) - 1) / 2, -1.0, 1.0)
    th = np.arccos(c)
    if th < 1e-9:
        return np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]]) / 2
    return th / (2 * np.sin(th)) * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])


def T(R: np.ndarray, t: np.ndarray) -> np.ndarray:
    M = np.eye(4)
    M[:3, :3], M[:3, 3] = R, t
    return M


def perturb(M: np.ndarray, d: np.ndarray) -> np.ndarray:
    """Left-multiplied SE(3) update (rotation vector d[:3], translation d[3:])."""
    return T(exp_so3(d[:3]), d[3:]) @ M


@dataclass
class AxYbResult:
    X: np.ndarray
    Y: np.ndarray
    rot_rms_deg: float
    trans_rms_mm: float
    iterations: int


def solve_ax_yb(A: list[np.ndarray], B: list[np.ndarray], X0: np.ndarray, Y0: np.ndarray | None = None,
                iters: int = 50) -> AxYbResult:
    """Minimise sum ||log(A_i^-1 X B_i Y)|| over X, Y (4x4 rigid transforms)."""
    X, Y = X0.copy(), (np.eye(4) if Y0 is None else Y0.copy())

    def resid(X, Y):
        r = []
        for a, b in zip(A, B):
            E = np.linalg.inv(a) @ X @ b @ Y
            r += list(log_so3(E[:3, :3]) * 100.0) + list(E[:3, 3])    # 1 rad ~ 100 mm weighting
        return np.array(r)

    lam, it = 1e-3, 0
    r = resid(X, Y)
    for it in range(1, iters + 1):
        J = np.zeros((len(r), 12))
        eps = 1e-6
        for k in range(12):
            d = np.zeros(12)
            d[k] = eps
            J[:, k] = (resid(perturb(X, d[:6]), perturb(Y, d[6:])) - r) / eps
        H = J.T @ J
        step = -np.linalg.solve(H + lam * np.diag(np.diag(H) + 1e-9), J.T @ r)
        Xn, Yn = perturb(X, step[:6]), perturb(Y, step[6:])
        rn = resid(Xn, Yn)
        if rn @ rn < r @ r:
            X, Y, r, lam = Xn, Yn, rn, lam * 0.3
            if np.linalg.norm(step) < 1e-10:
                break
        else:
            lam *= 10
    rr = r.reshape(-1, 6)
    return AxYbResult(X, Y, float(np.degrees(np.sqrt((rr[:, :3] ** 2).mean()) / 100.0)),
                      float(np.sqrt((rr[:, 3:] ** 2).mean())), it)


@dataclass
class CameraCalibration:
    """Measured scan-mode camera: pose in the world frame + OpenCV intrinsics and distortion."""
    R_wc: np.ndarray
    C: np.ndarray
    fx: float
    fy: float
    cx: float
    cy: float
    width: int
    height: int
    dist: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])   # k1 k2 p1 p2

    def save(self, path: str | Path) -> None:
        d = {"R_wc": self.R_wc.tolist(), "C": self.C.tolist(), "fx": self.fx, "fy": self.fy, "cx": self.cx,
             "cy": self.cy, "width": self.width, "height": self.height, "dist_k1_k2_p1_p2": list(self.dist)}
        Path(path).write_text(yaml.safe_dump(d), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "CameraCalibration":
        d = yaml.safe_load(Path(path).read_text())
        return cls(np.array(d["R_wc"]), np.array(d["C"]), d["fx"], d["fy"], d["cx"], d["cy"],
                   int(d["width"]), int(d["height"]), list(d.get("dist_k1_k2_p1_p2", [0, 0, 0, 0])))

    @classmethod
    def from_X(cls, X: np.ndarray, intr, dist=None) -> "CameraCalibration":
        R = X[:3, :3]
        return cls(R, -R.T @ X[:3, 3], intr.fx, intr.fy, intr.cx, intr.cy, intr.width, intr.height,
                   list(dist or [0, 0, 0, 0]))
