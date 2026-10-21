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
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)             # camera frames are RGB (camera/uvc.py)
        size = gray.shape[::-1]
        corners, ids, _, _ = det.detectBoard(gray)
        if ids is None or len(ids) < 6:
            continue
        o, i = board.matchImagePoints(corners, ids)
        obj_pts.append(o); img_pts.append(i); kept.append(p)
    if len(kept) < 6:
        raise ValueError(f"only {len(kept)} usable board views (need >= 6): check lighting and board placement")
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


def scan_meta(cfg: Machine, plan, background: bool = False, camera: dict | None = None, run_id: str | None = None,
              image_ext: str = ".jpg", calib_file: str | None = None) -> dict:
    """scan.json, the one dataset description `scan hull` / `scan ps` read, written by both `scan run` (laptop) and the
    station's 3D scan job. Intrinsics come from the measured calibration when there is one (copied into the run)."""
    from . import calibrate as _c
    scfg = cfg.for_scan()
    poses = [sp.pose if hasattr(sp, "pose") else sp for sp in plan]
    calib = _c.CameraCalibration.load(calib_file) if calib_file else None
    K = calib.intrinsics if calib is not None else intrinsics(scfg, cfg.scan["camera_distance_mm"])
    return {"schema": 2, "run_id": run_id, "plan": poses, "image_ext": image_ext, "intrinsics": K.__dict__,
            "intrinsics_source": "measured (scan_calibration.yaml in this folder)" if calib else "nominal (thin lens)",
            "distortion": list(calib.dist) if calib is not None else None,
            "calibration_file": Path(calib_file).name if calib_file else None, "calibrated": calib is not None,
            "ps": [], "background": background, "camera": camera,
            "platter_offset_mm": float(cfg.scan["platter_offset_mm"])}


def run_scan(cfg: Machine, g: Gantry, cam, hub, out_dir: str | Path, exposure_ms: float,
             ps: bool = True, background: bool = False, overwrite: bool = False) -> Path:  # pragma: no cover - needs hardware
    """background=True: same poses with the empty platter -> background/ (for silhouettes) in an existing scan folder.
    Exposure is configured and read back (it must apply); every frame save is checked; lights go off on any error."""
    import shutil

    from ..camera.uvc import CameraSettings
    from ..imageio import save_image
    from ..runrecord import AcquisitionError, make_run_dir, new_run_id, record_file, write_json_atomic

    check_object(cfg)
    out = Path(out_dir) if background else make_run_dir(out_dir, overwrite)
    if background and not (out / "scan.json").exists():
        raise AcquisitionError(f"{out}: run the object pass (`scan run`) before the background pass")
    folder = "background" if background else "images"
    (out / folder).mkdir(parents=True, exist_ok=True)
    plan = rings_plan(cfg)
    calib_file = None
    if cfg.scan.get("calibration"):
        calib_file = str(out / "scan_calibration.yaml")
        if not background:
            shutil.copyfile(cfg.scan["calibration"], calib_file)       # the run keeps its own copy
    applied = cam.configure(CameraSettings(exposure_ms))
    meta = json.loads((out / "scan.json").read_text()) if background else \
        scan_meta(cfg, plan, camera=applied, run_id=new_run_id(), calib_file=calib_file)
    files, errors = [], []
    try:
        g.light("white", True)
        for sp in plan:
            g.move(sp.pose)
            name = f"{folder}/{sp.name}"
            if not save_image(out / name, cam.grab()):
                raise AcquisitionError(f"saving {name} failed")
            files.append(record_file(out, name))
        off = g.all_lights_off()
        if off:                                   # a lamp still on would light the photometric frames
            raise AcquisitionError("white lamp did not switch off: " + "; ".join(off))
        if background:
            meta["background"] = True
        elif ps:
            (out / "ps").mkdir(exist_ok=True)
            g.light("multispectral", True)
            for si, st in enumerate(photometric_stations(cfg)):
                g.move(st)
                lights = []
                for li, m4 in enumerate(cfg.scan["ps_m4_deg"]):
                    g.move({"M4": float(m4)})
                    hub.band(int(cfg.scan["ps_band"]))
                    name = f"ps/st{si:02d}_l{li}.png"
                    ok = save_image(out / name, cam.grab())
                    hub.band(None)
                    if not ok:
                        raise AcquisitionError(f"saving {name} failed")
                    files.append(record_file(out, name))
                    lights.append(light_in_object(cfg, st, float(m4)).tolist())
                meta["ps"].append({"pose": st, "lights_object_frame": lights,
                                   "light_positions_object_mm": [light_position_object(cfg, st, float(m4)).tolist()
                                                                  for m4 in cfg.scan["ps_m4_deg"]]})
        meta["status"] = "finished"
    except BaseException as exc:
        from ..gantry.hub import SafetyInterrupt
        meta["status"] = "aborted" if isinstance(exc, (KeyboardInterrupt, SafetyInterrupt)) else "error"
        errors.append(f"{type(exc).__name__}: {exc}")
        raise
    finally:
        cleanup = g.all_lights_off()
        try:
            hub.band(None)
        except Exception as exc:
            cleanup.append(f"band off failed: {exc}")
        meta.setdefault("files", []).extend(files)
        meta["errors"], meta["cleanup_errors"] = meta.get("errors", []) + errors, cleanup
        write_json_atomic(out / "scan.json", meta)
    if not background:
        from .calibrate import CameraCalibration
        calib = CameraCalibration.load(calib_file) if calib_file else None
        K = calib.intrinsics if calib is not None else intrinsics(cfg.for_scan(), cfg.scan["camera_distance_mm"])
        write_model(out / "sparse_known", cfg.for_scan(), plan, K, float(cfg.scan["platter_offset_mm"]), calib)
    return out
