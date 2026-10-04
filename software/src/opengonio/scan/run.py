"""Run a scan on the machine: photogrammetry rings + photometric-stereo stations.

Output folder:
  images/img_0000.jpg ...       photogrammetry frames (white lamp, cross-polarized)
  ps/st00_l0.png ...            photometric-stereo frames (LED bank band, object still)
  sparse_known/                 COLMAP model with the known poses (colmap.py)
  run_colmap.sh                 COLMAP commands [S2]
  scan.json                     poses, lights, camera settings (reproducibility)
"""
from __future__ import annotations

import json
from pathlib import Path

from ..gantry.config import Machine
from ..gantry.gantry import Gantry
from .colmap import write_model
from .geometry import intrinsics, light_in_object, light_position_object
from .plan import check_object, photometric_stations, rings_plan


def calibrate_scan(cfg: Machine, g: Gantry, cam, out_path: str | Path, squares=(7, 5), square_mm: float = 10.0,
                   marker_mm: float = 7.0, every: int = 12) -> Path:  # pragma: no cover - needs hardware
    """Scan-mode pose calibration (acceptance test S2): ChArUco board on the platter, ~12 poses.

    1. Intrinsics + distortion from all views (OpenCV ChArUco calibration [S12]).
    2. Board pose per view by solvePnP [S11] -> A_i; kinematic platter pose -> B_i.
    3. Solve A_i = X B_i Y (calibrate.solve_ax_yb); save X as the measured camera pose.
    """
    import cv2
    import numpy as np

    from .calibrate import CameraCalibration, T, solve_ax_yb
    from .geometry import platter_to_world, world_to_camera

    d = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    board = cv2.aruco.CharucoBoard(squares, square_mm, marker_mm, d)
    det = cv2.aruco.CharucoDetector(board)
    poses = [sp.pose for sp in rings_plan(cfg)[::every]]
    obj_pts, img_pts, kept, size = [], [], [], None
    for p in poses:
        g.move(p)
        img = cam.grab()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        size = gray.shape[::-1]
        corners, ids, _, _ = det.detectBoard(gray)
        if ids is None or len(ids) < 6:
            continue
        o, i = board.matchImagePoints(corners, ids)
        obj_pts.append(o); img_pts.append(i); kept.append(p)
    rms, K, dist, rvecs, tvecs = cv2.calibrateCamera(obj_pts, img_pts, size, None, None)
    A = [T(cv2.Rodrigues(r)[0], t.ravel()) for r, t in zip(rvecs, tvecs)]
    B = [platter_to_world(p, float(cfg.scan["platter_offset_mm"])) for p in kept]
    R_wc, C = world_to_camera(cfg.for_scan())
    res = solve_ax_yb(A, B, T(R_wc, -R_wc @ C))
    from .geometry import Intrinsics
    intr = Intrinsics(K[0, 0], K[1, 1], K[0, 2], K[1, 2], size[0], size[1])
    cal = CameraCalibration.from_X(res.X, intr, dist.ravel()[:4].tolist())
    cal.save(out_path)
    print(f"reprojection RMS {rms:.3f} px; pose fit {res.rot_rms_deg:.3f} deg / {res.trans_rms_mm:.3f} mm "
          f"over {len(kept)} views -> {out_path}")
    return Path(out_path)


def run_scan(cfg: Machine, g: Gantry, cam, hub, out_dir: str | Path, exposure_ms: float,
             ps: bool = True, background: bool = False) -> Path:  # pragma: no cover - needs hardware
    """background=True: same poses with the empty platter -> background/ (for silhouettes)."""
    import cv2

    scfg = cfg.for_scan()
    check_object(cfg)
    out = Path(out_dir)
    folder = "background" if background else "images"
    (out / folder).mkdir(parents=True, exist_ok=True)
    plan = rings_plan(cfg)
    calib = None
    if cfg.scan.get("calibration"):
        from .calibrate import CameraCalibration
        calib = CameraCalibration.load(cfg.scan["calibration"])
    g.light("white", True)
    cam.set_exposure(exposure_ms) if hasattr(cam, "set_exposure") else None
    for sp in plan:
        g.move(sp.pose)
        cv2.imwrite(str(out / folder / sp.name), cam.grab())
    g.light("white", False)
    if background:
        return out
    K = intrinsics(scfg, cfg.scan["camera_distance_mm"])
    write_model(out / "sparse_known", scfg, plan, K, float(cfg.scan["platter_offset_mm"]), calib)
    meta = {"plan": [sp.pose for sp in plan], "intrinsics": K.__dict__, "ps": [],
            "platter_offset_mm": float(cfg.scan["platter_offset_mm"]), "calibrated": calib is not None}
    if ps:
        (out / "ps").mkdir(exist_ok=True)
        g.light("multispectral", True)
        for si, st in enumerate(photometric_stations(cfg)):
            g.move(st)
            lights = []
            for li, m4 in enumerate(cfg.scan["ps_m4_deg"]):
                g.move({"M4": float(m4)})
                hub.band(int(cfg.scan["ps_band"]))
                cv2.imwrite(str(out / "ps" / f"st{si:02d}_l{li}.png"), cam.grab())
                hub.band(None)
                lights.append(light_in_object(cfg, st, float(m4)).tolist())
            meta["ps"].append({"pose": st, "lights_object_frame": lights,
                               "light_positions_object_mm": [light_position_object(cfg, st, float(m4)).tolist()
                                                              for m4 in cfg.scan["ps_m4_deg"]]})
        g.light("multispectral", False)
    (out / "scan.json").write_text(json.dumps(meta, indent=1), encoding="utf-8")
    return out
