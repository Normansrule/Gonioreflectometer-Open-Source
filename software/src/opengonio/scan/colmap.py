"""Write a COLMAP text model with the known poses (pose priors) [S1][S2].

cameras.txt : CAMERA_ID MODEL WIDTH HEIGHT PARAMS[]   (PINHOLE: fx fy cx cy)
images.txt  : IMAGE_ID QW QX QY QZ TX TY TZ CAMERA_ID NAME, then an empty POINTS2D line
points3D.txt: empty
Then (COLMAP FAQ, "known camera poses" [S2]): feature_extractor -> exhaustive_matcher ->
point_triangulator -> image_undistorter -> patch_match_stereo -> stereo_fusion.
Image IDs must match the IDs COLMAP assigns in database.db: run feature_extractor on the
images folder first and keep the default sorted order (img_0000.jpg, img_0001.jpg, ...).
Units: millimetres (metric scale comes from the kinematics).
"""
from __future__ import annotations

from pathlib import Path

from ..gantry.config import Machine
from .geometry import Intrinsics, object_to_camera, rotmat_to_quat
from .plan import ScanPose

def commands(model: str, params: str) -> str:
    """COLMAP command sequence for known poses [S2]. patch_match_stereo needs an NVIDIA (CUDA) GPU;
    without one, use Meshroom [S10] / OpenMVS [S17] on the same images, or the visual hull."""
    return f"""# run inside the scan folder (images/ + sparse_known/ written by opengonio)
rm -f database.db
colmap feature_extractor --database_path database.db --image_path images \\
  --ImageReader.single_camera 1 --ImageReader.camera_model {model} --ImageReader.camera_params "{params}"
opengonio scan sync-ids --db database.db --model sparse_known   # image IDs must match the database [S2]
colmap exhaustive_matcher --database_path database.db
mkdir -p sparse dense
colmap point_triangulator --database_path database.db --image_path images --input_path sparse_known --output_path sparse
# optional: refine poses, then pin metric scale back to the kinematic camera centres
# colmap bundle_adjuster --input_path sparse --output_path sparse
# colmap model_aligner --input_path sparse --output_path sparse --ref_images_path ref_positions.txt --ref_is_gps 0 --alignment_max_error 1
colmap image_undistorter --image_path images --input_path sparse --output_path dense
colmap patch_match_stereo --workspace_path dense
colmap stereo_fusion --workspace_path dense --output_path dense/fused.ply
colmap poisson_mesher --input_path dense/fused.ply --output_path dense/meshed-poisson.ply
"""


def write_model(out_dir: str | Path, cfg: Machine, plan: list[ScanPose], K: Intrinsics,
                platter_offset_mm: float = 0.0, calib=None) -> Path:
    """Write cameras.txt / images.txt / points3D.txt, ref_positions.txt and run_colmap.sh.
    With a calibration (scan/calibrate.py) the measured camera pose and OPENCV distortion are used."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    if calib is not None:
        k1, k2, p1, p2 = calib.dist
        model = "OPENCV"
        vals = [calib.fx, calib.fy, calib.cx, calib.cy, k1, k2, p1, p2]
        w, h = calib.width, calib.height
    else:
        model = "PINHOLE"
        vals = [K.fx, K.fy, K.cx, K.cy]
        w, h = K.width, K.height
    params = ",".join(f"{v:.6f}" for v in vals)
    (out / "cameras.txt").write_text(
        "# Camera list with one line of data per camera:\n"
        "#   CAMERA_ID, MODEL, WIDTH, HEIGHT, PARAMS[]\n"
        f"1 {model} {w} {h} {' '.join(f'{v:.6f}' for v in vals)}\n", encoding="utf-8")
    lines = ["# Image list with two lines of data per image:",
             "#   IMAGE_ID, QW, QX, QY, QZ, TX, TY, TZ, CAMERA_ID, NAME",
             "#   POINTS2D[] as (X, Y, POINT3D_ID)"]
    refs = []
    for sp in sorted(plan, key=lambda s: s.name):
        R, t = object_to_camera(cfg, sp.pose, platter_offset_mm, calib)
        q = rotmat_to_quat(R)
        lines.append(f"{sp.index + 1} {q[0]:.10f} {q[1]:.10f} {q[2]:.10f} {q[3]:.10f} "
                     f"{t[0]:.6f} {t[1]:.6f} {t[2]:.6f} 1 {sp.name}")
        lines.append("")
        c = -R.T @ t
        refs.append(f"{sp.name} {c[0]:.6f} {c[1]:.6f} {c[2]:.6f}")
    (out / "images.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (out / "points3D.txt").write_text("# empty: triangulated by point_triangulator\n", encoding="utf-8")
    (out.parent / "ref_positions.txt").write_text("\n".join(refs) + "\n", encoding="utf-8")
    (out.parent / "run_colmap.sh").write_text("#!/usr/bin/env bash\nset -e\n" + commands(model, params), encoding="utf-8")
    return out


def sync_image_ids(db_path: str | Path, model_dir: str | Path) -> int:
    """Rewrite images.txt IDs to the IDs COLMAP stored in database.db (matched by file name)."""
    import sqlite3
    con = sqlite3.connect(str(db_path))
    ids = dict((name, iid) for iid, name in con.execute("SELECT image_id, name FROM images"))
    con.close()
    p = Path(model_dir) / "images.txt"
    out, n = [], 0
    for line in p.read_text().splitlines():
        f = line.split()
        if line.startswith("#") or len(f) < 10:
            out.append(line)
            continue
        if f[9] not in ids:
            raise KeyError(f"{f[9]} is not in {db_path}")
        f[0] = str(ids[f[9]])
        out.append(" ".join(f))
        n += 1
    p.write_text("\n".join(out) + "\n", encoding="utf-8")
    return n


def read_images_txt(path: str | Path) -> dict[str, tuple]:
    """Parse images.txt back (used by tests and by the SVBRDF stage)."""
    out = {}
    lines = [l for l in Path(path).read_text().splitlines() if not l.startswith("#")]
    for i in range(0, len(lines), 2):
        if not lines[i].strip():
            continue
        f = lines[i].split()
        out[f[9]] = (int(f[0]), [float(x) for x in f[1:5]], [float(x) for x in f[5:8]])
    return out
