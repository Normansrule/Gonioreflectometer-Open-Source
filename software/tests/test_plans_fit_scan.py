"""Out-of-plane plans (inverse kinematics), material fit, camera response, scan hull and photometric stereo."""
import json
import math

import numpy as np
import pytest

from opengonio.gantry.config import load_config
from opengonio.gantry.kinematics import brdf_coords
from opengonio.imageio import write_png
from opengonio.plans.hemisphere import anisotropic, complete, isotropic, pose_for_angles, spin


@pytest.fixture
def cfg9():
    return load_config().with_phase(9)


@pytest.mark.parametrize("ti,tr,dp", [(30, 30, 180), (30, 45, 90), (60, 20, 45), (10, 70, 120), (45, 45, 30), (0, 40, 0)])
def test_inverse_kinematics_hits_the_angles(cfg9, ti, tr, dp):
    b = brdf_coords(cfg9, pose_for_angles(cfg9, ti, tr, dp))
    assert abs(b.theta_i - ti) < 0.01 and abs(b.theta_r - tr) < 0.01
    if ti and tr:
        assert abs(b.delta_phi - dp) < 0.01


def test_phi_i_from_spin(cfg9):
    for phi in (0, 45, 90, -120):
        b = brdf_coords(cfg9, pose_for_angles(cfg9, 30, 50, 90, phi_i=phi))
        assert abs((b.phi_i - phi + 180) % 360 - 180) < 0.01


def test_backscatter_is_unreachable(cfg9):
    assert pose_for_angles(cfg9, 45, 45, 0) is None                 # light on the camera axis


def test_plans_respect_the_stage(cfg9):
    six = isotropic(cfg9.with_phase(6), 15)
    assert six and all(set(p) == {"M4", "M3"} for p in six)          # before the tilt: in-plane only
    nine = isotropic(cfg9, 15)
    assert len(nine) > 5 * len(six) and all(set(p) == {"M4", "M3", "M2", "M1"} for p in nine)
    assert all(p["M1"] == 0 for p in nine)
    assert len(anisotropic(cfg9, 30, 60)) > 0 and [p["M1"] for p in spin(cfg9, 30, 45)] == [0, 45, 90, 135, 180]


def test_complete_keeps_tilt_flat(cfg9):
    assert complete(cfg9, {"M4": 60, "M3": 30}) == {"M4": 60.0, "M3": 30.0, "M2": 0.0, "M1": 0.0}


def test_linearity_finds_gamma():
    from opengonio.calibration import linearity
    t = [2, 4, 8, 16, 32, 64, 128]
    c = [4 + 255 * (min(1.0, 3 * x / 255)) ** (1 / 2.2) for x in t]      # last point saturates: ignored
    r = linearity(t, c, 4.0)
    assert abs(r["gamma"] - 2.2) < 0.01 and r["r2"] > 0.999 and r["points_used"] == 6


def test_sim_isotropic_capture_and_fit(tmp_path):
    from opengonio.cli import main
    m9 = tmp_path / "m9.yaml"
    from opengonio.gantry.config import DEFAULT_CONFIG
    m9.write_text(DEFAULT_CONFIG.read_text().replace("installed_phase: 6", "installed_phase: 9"))
    c = ["--config", str(m9), "--cal", str(tmp_path / "c.yaml")]
    sim = c + ["--sim-gamma", "2.2"]
    for plan, mat in (("dark", "ptfe"), ("linearity", "ptfe"), ("white", "ptfe")):
        assert main(sim + ["--sim", mat, "capture", plan, "--out", str(tmp_path / plan)]) == 0
        assert main(c + ["calibrate", plan, str(tmp_path / plan)]) == 0
    assert main(sim + ["--sim", "plastic", "capture", "isotropic", "--step", "15", "--out", str(tmp_path / "iso")]) == 0
    assert main(c + ["curve", str(tmp_path / "iso")]) == 0
    assert main(c + ["fit", str(tmp_path / "iso")]) == 0
    r = json.loads((tmp_path / "iso" / "fit.json").read_text())
    assert abs(r["roughness"] - 0.3) <= 0.03 and abs(r["base_color"] - 0.2) <= 0.03 and r["metallic"] <= 0.1
    assert (tmp_path / "iso" / "curve.svg").read_text().startswith("<svg") and (tmp_path / "iso" / "fit.svg").exists()


def _fake_scan(cfg, folder, n_views=24, radius=20.0, scale=0.04):
    """Synthetic sphere scan: images (white disc on black) + empty backgrounds + scan.json."""
    from opengonio.scan.carve import sphere_mask
    from opengonio.scan.geometry import intrinsics, object_to_camera
    from opengonio.scan.plan import rings_plan
    scfg = cfg.for_scan()
    K = intrinsics(scfg, cfg.scan["camera_distance_mm"]).scaled(scale)
    plan = rings_plan(cfg)[:: max(1, len(rings_plan(cfg)) // n_views)]
    (folder / "images").mkdir(parents=True)
    (folder / "background").mkdir()
    for i, sp in enumerate(plan):
        R, t = object_to_camera(scfg, sp.pose)
        m = sphere_mask(np.zeros(3), radius, K.K, R, t, K.width, K.height)
        write_png(folder / "images" / f"img_{i:04d}.png", m * 200)
        write_png(folder / "background" / f"img_{i:04d}.png", np.zeros_like(m, dtype=np.uint8))
    (folder / "scan.json").write_text(json.dumps({"plan": [sp.pose for sp in plan], "intrinsics": K.__dict__,
                                                  "ps": [], "platter_offset_mm": 0.0, "calibrated": False}))


def test_scan_hull_measures_the_object(tmp_path, cfg9):
    from opengonio.scan.process import hull
    _fake_scan(cfg9, tmp_path)
    r = hull(cfg9, tmp_path, voxel_mm=1.0, downscale=1)
    assert all(abs(s - 40.0) <= 3.0 for s in r["size_mm"]), r            # 40 mm sphere, 1 mm voxels, 24 views
    assert (tmp_path / "hull.ply").exists()


def test_scan_ps_sphere(tmp_path):
    from opengonio.scan.geometry import light_in_object, object_to_camera
    from opengonio.scan.plan import photometric_stations
    from opengonio.scan.process import ps
    cfg = load_config().with_phase(10)
    st = photometric_stations(cfg)[0]
    L = np.array([light_in_object(cfg, st, float(m)) for m in cfg.scan["ps_m4_deg"]])
    R_oc, _ = object_to_camera(cfg.for_scan(), st)
    yy, xx = np.mgrid[-1.2:1.2:96j, -1.2:1.2:96j]
    inside = xx ** 2 + yy ** 2 < 1
    n_cam = np.dstack([xx, yy, -np.sqrt(np.clip(1 - xx ** 2 - yy ** 2, 0, None))])
    n_obj = n_cam @ R_oc                                                   # n_cam = R_oc n_obj
    (tmp_path / "ps").mkdir()
    for k, l in enumerate(L):
        write_png(tmp_path / "ps" / f"st00_l{k}.png", np.where(inside, 0.8 * np.clip(n_obj @ l, 0, None), 0) * 255)
    (tmp_path / "scan.json").write_text(json.dumps({"ps": [{"pose": st, "lights_object_frame": L.tolist()}],
                                                    "platter_offset_mm": 0.0, "calibrated": False}))
    r = ps(cfg, tmp_path, sphere=True)
    assert r["sphere_median_normal_error_deg"] < 3.0 and r["valid_fraction"] > 0.3, r
