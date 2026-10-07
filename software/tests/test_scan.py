import math

import numpy as np
import pytest

from opengonio.gantry.collision import min_safe_m4, pose_is_safe
from opengonio.gantry.config import load_config
from opengonio.gantry.kinematics import light_dir
from opengonio.scan import demo
from opengonio.scan.carve import carve, sphere_mask, write_ply
from opengonio.scan.calibrate import CameraCalibration, T, exp_so3, solve_ax_yb
from opengonio.scan.carve import silhouette_from_background
from opengonio.scan.colmap import read_images_txt, sync_image_ids, write_model
from opengonio.scan.geometry import light_position_object, platter_to_world, world_to_camera
from opengonio.scan.photometric import near_light_inputs
from opengonio.scan.geometry import (camera_center_object, camera_elevation_in_object, intrinsics, object_to_camera,
                                     project, quat_to_rotmat, rotmat_to_quat)
from opengonio.scan.photometric import CoplanarLightsError, light_rank, render_lambert, solve
from opengonio.scan.plan import PlanError, check_object, rings_plan


@pytest.fixture
def cfg():
    return load_config().with_phase(10)


def test_plan_has_144_views_and_needs_m1_m2(cfg):
    plan = rings_plan(cfg)
    assert len(plan) == 144 and len({sp.name for sp in plan}) == 144
    assert all(cfg.axes[k].in_range(v) for sp in plan for k, v in sp.pose.items())
    with pytest.raises(PlanError):
        rings_plan(cfg.with_phase(8))


@pytest.mark.parametrize("elev", [20, 35, 50, 65, 80])
def test_camera_elevation_seen_from_object(cfg, elev):
    s = cfg.for_scan()
    m2 = 90 - elev + s.camera_elevation_deg            # the scan camera sits 15 deg up
    for m1 in (-180, -45, 90):
        assert camera_elevation_in_object(s, {"M3": 0, "M2": m2, "M1": m1}) == pytest.approx(elev, abs=1e-9)


def test_poses_are_rigid_and_look_at_object(cfg):
    s = cfg.for_scan()
    K = intrinsics(s, 650)
    for sp in rings_plan(cfg)[::17]:
        R, t = object_to_camera(s, sp.pose)
        assert np.allclose(R @ R.T, np.eye(3)) and np.linalg.det(R) == pytest.approx(1)
        assert np.linalg.norm(camera_center_object(R, t)) == pytest.approx(650)
        uv, z = project(np.zeros((1, 3)), K.K, R, t)          # object centre lands on the image centre
        assert np.allclose(uv[0], [K.cx, K.cy]) and z[0] == pytest.approx(650)


def test_platter_offset_moves_object_centre_to_zero_point(cfg):
    s = cfg.for_scan()
    K = intrinsics(s, 650)
    pose = {"M3": 0, "M2": 50, "M1": 30}
    R, t = object_to_camera(s, pose, platter_offset_mm=40)
    uv, _ = project(np.array([[0, 0, 40.0]]), K.K, R, t)     # 40 mm up the object axis = zero point
    assert np.allclose(uv[0], [K.cx, K.cy], atol=1e-6)


def test_quaternion_round_trip(cfg):
    s = cfg.for_scan()
    for sp in rings_plan(cfg)[::11]:
        R, _ = object_to_camera(s, sp.pose)
        q = rotmat_to_quat(R)
        assert q[0] >= 0 and np.allclose(quat_to_rotmat(q), R, atol=1e-9)


def test_colmap_model_files(tmp_path, cfg):
    s = cfg.for_scan()
    plan = rings_plan(cfg)
    out = write_model(tmp_path / "sparse_known", s, plan, intrinsics(s, 650))
    cams = (out / "cameras.txt").read_text().splitlines()[-1].split()
    assert cams[:2] == ["1", "PINHOLE"] and len(cams) == 8
    imgs = read_images_txt(out / "images.txt")
    assert len(imgs) == 144 and imgs["img_0000.jpg"][0] == 1
    sh = (tmp_path / "run_colmap.sh").read_text()
    for step in ("feature_extractor", "sync-ids", "exhaustive_matcher", "point_triangulator", "image_undistorter",
                 "patch_match_stereo", "stereo_fusion", "poisson_mesher"):
        assert step in sh
    assert "camera_model PINHOLE" in sh and len((tmp_path / "ref_positions.txt").read_text().splitlines()) == 144


def test_object_fit_dof_and_light_arm_clearance(cfg):
    check_object(cfg, 55)
    with pytest.raises(PlanError, match="depth of field"):
        check_object(cfg, 65)
    with pytest.raises(PlanError, match="keep-out"):
        check_object(cfg, 110)


def test_led_mast_keeps_m4_limits_safe(cfg):
    assert min_safe_m4(cfg) < cfg.axes["M4"].min_deg
    assert pose_is_safe(cfg.for_scan(), {"M4": cfg.scan["lamp_m4_deg"]})
    assert light_dir(0, 40)[2] == pytest.approx(math.sin(math.radians(40)))


def test_visual_hull_of_sphere(cfg):
    s = cfg.for_scan()
    K = intrinsics(s, 650).scaled(0.05)
    plan = rings_plan(cfg)[::4]
    views = [object_to_camera(s, sp.pose) for sp in plan]
    masks = [sphere_mask(np.zeros(3), 30.0, K.K, R, t, K.width, K.height) for R, t in views]
    g = carve(masks, views, K.K, half_size_mm=42, n=48)
    r_eq = (3 * g.volume_mm3 / (4 * math.pi)) ** (1 / 3)
    assert 29.0 < r_eq < 33.0          # hull >= object, close for a sphere


def test_photometric_stereo_recovers_normals_and_rejects_coplanar(cfg):
    rng = np.random.default_rng(0)
    n = rng.normal(size=(200, 3)); n[:, 2] = np.abs(n[:, 2]) + 1.0
    n /= np.linalg.norm(n, axis=1, keepdims=True)
    rho = rng.uniform(0.2, 0.8, 200)
    L_ok = np.array([light_dir(a, 40) for a in (0, 70, 140, 210, 280)])
    L_ok[:, 2] = np.abs(L_ok[:, 2])
    res = solve(render_lambert(n, rho, L_ok) * 0.95, L_ok)
    good = res.valid
    assert good.mean() > 0.6
    assert np.allclose(res.normals[good], n[good], atol=1e-6) and np.allclose(res.albedo[good], 0.95 * rho[good])
    L_flat = np.array([light_dir(a, 0) for a in (0, 70, 140, 210)])
    assert light_rank(L_flat) == 2
    with pytest.raises(CoplanarLightsError):
        solve(render_lambert(n, rho, L_flat), L_flat)


def test_demo_runs(tmp_path, cfg):
    r = demo.run(cfg, tmp_path, scale=0.04)
    assert 29 < r["visual_hull_equiv_radius_mm"] < 33.5
    assert r["ps_median_normal_error_deg"] < 0.5
    assert (tmp_path / "visual_hull.ply").read_text().startswith("ply")


def test_ply_writer(tmp_path):
    p = write_ply(tmp_path / "a.ply", np.zeros((2, 3)), np.ones((2, 3)))
    assert "element vertex 2" in p.read_text() and "property float nz" in p.read_text()


def test_plan_respects_camera_elevation(cfg):
    from dataclasses import replace
    c10 = replace(cfg, scan={**cfg.scan, "camera_elevation_deg": 10.0})
    with pytest.raises(PlanError):                       # 0 deg ring would need M2 = 100
        rings_plan(c10, [{"elevation_deg": 0, "count": 8}])
    rings = [{"elevation_deg": e, "count": 8} for e in (10, 30, 50, 70, 90)]
    for sp in rings_plan(c10, rings):
        assert camera_elevation_in_object(c10.for_scan(), sp.pose) == pytest.approx(sp.elevation_deg, abs=1e-9)


def test_pose_calibration_recovers_camera_mount(cfg):
    s = cfg.for_scan()
    R_wc, C = world_to_camera(s)
    X_nom = T(R_wc, -R_wc @ C)
    X_true = T(exp_so3(np.radians([0.8, -0.6, 0.5])), np.array([1.5, -2.0, 3.0])) @ X_nom
    Y_true = T(exp_so3(np.radians([2.0, 1.0, -3.0])), np.array([4.0, -3.0, 1.0]))
    poses = [sp.pose for sp in rings_plan(cfg)[::12]]
    B = [platter_to_world(p) for p in poses]
    A = [X_true @ b @ Y_true for b in B]
    res = solve_ax_yb(A, B, X_nom)
    assert np.allclose(res.X, X_true, atol=1e-6) and np.allclose(res.Y, Y_true, atol=1e-6)
    assert res.rot_rms_deg < 1e-5 and res.trans_rms_mm < 1e-5


def test_calibration_drives_poses_and_opencv_model(tmp_path, cfg):
    s = cfg.for_scan()
    R_wc, C = world_to_camera(s)
    K = intrinsics(s, 650)
    cal = CameraCalibration(R_wc, C + np.array([0.0, 2.0, 0.0]), K.fx, K.fy, K.cx, K.cy, K.width, K.height,
                            [-0.1, 0.02, 0.0, 0.0])
    cal.save(tmp_path / "cal.yaml")
    cal2 = CameraCalibration.load(tmp_path / "cal.yaml")
    pose = {"M3": 0, "M2": 60, "M1": 10}
    R0, t0 = object_to_camera(s, pose)
    R1, t1 = object_to_camera(s, pose, calib=cal2)
    assert np.allclose(R0, R1) and not np.allclose(t0, t1)
    out = write_model(tmp_path / "m" / "sparse_known", s, rings_plan(cfg)[:3], K, calib=cal2)
    assert (out / "cameras.txt").read_text().splitlines()[-1].split()[1] == "OPENCV"


def test_sync_image_ids(tmp_path, cfg):
    import sqlite3
    s = cfg.for_scan()
    out = write_model(tmp_path / "sparse_known", s, rings_plan(cfg)[:3], intrinsics(s, 650))
    db = tmp_path / "database.db"
    con = sqlite3.connect(db)
    con.execute("CREATE TABLE images (image_id INTEGER, name TEXT)")
    con.executemany("INSERT INTO images VALUES (?, ?)", [(7, "img_0000.jpg"), (8, "img_0001.jpg"), (9, "img_0002.jpg")])
    con.commit(); con.close()
    assert sync_image_ids(db, out) == 3
    assert read_images_txt(out / "images.txt")["img_0002.jpg"][0] == 9


def test_near_light_photometric_stereo(cfg):
    rng = np.random.default_rng(1)
    st = {"M3": 0, "M2": 60, "M1": 0}
    lp = np.array([light_position_object(cfg, st, m) for m in cfg.scan["ps_m4_deg"]])
    pts = rng.normal(size=(300, 3)); pts /= np.linalg.norm(pts, axis=1, keepdims=True)
    n = pts.copy(); pts *= 40.0                              # sphere r = 40 mm at the zero point
    d = lp[:, None, :] - pts[None]
    r = np.linalg.norm(d, axis=-1); l = d / r[..., None]
    I = 0.5 * np.clip((l * n[None]).sum(-1), 0, None) * (300.0 / r) ** 2   # point lights, 1/r^2
    Ic, Lp = near_light_inputs(I, pts, lp)
    near = solve(Ic, Lp)
    far = solve(I, l.mean(1))
    ok = near.valid
    assert ok.mean() > 0.3
    assert np.degrees(np.arccos(np.clip((near.normals[ok] * n[ok]).sum(-1), -1, 1))).max() < 1e-3
    err_far = np.degrees(np.arccos(np.clip((far.normals[far.valid] * n[far.valid]).sum(-1), -1, 1)))
    assert np.median(err_far) > 0.5                          # distant-light assumption is visibly biased


def test_background_silhouette_and_carve_clip(cfg):
    bg = np.full((4, 4, 3), 10, np.uint8)
    img = bg.copy(); img[1, 1] = [40, 10, 10]; img[2, 2] = [11, 10, 10]
    m = silhouette_from_background(img, bg)
    assert m[1, 1] and not m[2, 2]
    s = cfg.for_scan()
    K = intrinsics(s, 650).scaled(0.05)
    views = [object_to_camera(s, sp.pose) for sp in rings_plan(cfg)[::6]]
    masks = [sphere_mask(np.zeros(3), 30.0, K.K, R, t, K.width, K.height) for R, t in views]
    g = carve(masks, views, K.K, half_size_mm=42, n=32, clip_below_z=0.0)
    assert g.centers()[:, 2].min() >= 0.0


def test_project_behind_camera_is_nan(cfg):
    s = cfg.for_scan()
    K = intrinsics(s, 650)
    R, t = object_to_camera(s, {"M3": 0, "M2": 90, "M1": 0})
    uv, z = project(np.array([[0.0, 0.0, 0.0], -(R.T @ t) * 2]), K.K, R, t)
    assert not np.isnan(uv[0]).any() and np.isnan(uv[1]).all() and z[1] < 0


def test_scan_camera_sees_over_measuring_camera(cfg):
    from opengonio.scan.geometry import scan_view_clearance_mm
    cl = scan_view_clearance_mm(cfg)
    assert cl["line_of_sight_mm"] > 20 and cl["frame_edge_mm"] > 0          # measuring camera stays out of the picture
    assert cfg.for_scan().camera["index"] != cfg.camera["index"]
    from dataclasses import replace
    low = replace(cfg, scan={**cfg.scan, "camera_elevation_deg": 3.0})
    with pytest.raises(PlanError):
        check_object(low.with_phase(9))
