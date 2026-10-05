import math

import numpy as np
import pytest

from opengonio.gantry.collision import clearance_mm, min_safe_m4, path_is_safe, pose_is_safe, segment_distance
from opengonio.gantry.config import ConfigError, DEFAULT_CONFIG, load_config
from opengonio.gantry.fluidnc import FluidNC, RecordingTransport, parse_status
from opengonio.gantry.gantry import Gantry, GantryError
from opengonio.gantry.hub import FakeHub, parse
from opengonio.gantry.kinematics import brdf_coords, per_pixel_directions, sample_normal, specular_m3
from opengonio.gantry.panel import Panel
from opengonio.plans import inplane
from opengonio.plans.repeatability import reflection_shift_to_deg, summarize


@pytest.fixture
def cfg():
    return load_config()


def gantry(cfg):
    t = RecordingTransport()
    return Gantry(cfg, FluidNC(t, timeout_s=1)), t


# ---- config ----
def test_phase_gating(cfg):
    assert list(cfg.active_axes) == ["M4", "M3"]
    assert list(cfg.with_phase(4).active_axes) == ["M4"]
    assert list(cfg.with_phase(8).active_axes) == ["M4", "M3", "M2"]
    assert list(cfg.with_phase(9).active_axes) == ["M4", "M3", "M2", "M1"]
    assert list(cfg.active_lights) == ["white"]
    assert list(cfg.with_phase(10).active_lights) == ["white", "multispectral"]


def test_resolution_beats_target(cfg):
    for a in cfg.axes.values():
        assert a.resolution_deg < cfg.repeatability_target_deg / 3


def test_home_must_be_range_end(tmp_path):
    txt = DEFAULT_CONFIG.read_text().replace("home_deg: 20.0", "home_deg: 90.0")
    p = tmp_path / "m.yaml"; p.write_text(txt)
    with pytest.raises(ConfigError):
        load_config(p)


# ---- kinematics ----
@pytest.mark.parametrize("ti,tr", [(10, 10), (30, 50), (45, 20), (70, 70)])
def test_inplane_pose_gives_requested_angles(cfg, ti, tr):
    b = brdf_coords(cfg, inplane.pose_for(ti, tr))
    assert b.theta_i == pytest.approx(ti, abs=1e-9)
    assert b.theta_r == pytest.approx(tr, abs=1e-9)
    assert b.delta_phi == pytest.approx(180, abs=1e-6) and b.measurable


@pytest.mark.parametrize("m4", [30, 90, 150, 300])
def test_specular_condition(cfg, m4):
    b = brdf_coords(cfg, {"M4": m4, "M3": specular_m3(m4)})
    assert b.theta_i == pytest.approx(b.theta_r, abs=1e-9)


def test_tilt_moves_normal_up_and_spin_keeps_normal(cfg):
    assert sample_normal(0, 30, 0)[2] == pytest.approx(math.sin(math.radians(30)))
    assert np.allclose(sample_normal(20, 10, 0), sample_normal(20, 10, 77))
    a = brdf_coords(cfg.with_phase(9), {"M4": 60, "M3": 30, "M2": 10, "M1": 0})
    b = brdf_coords(cfg.with_phase(9), {"M4": 60, "M3": 30, "M2": 10, "M1": 25})
    assert a.theta_i == pytest.approx(b.theta_i) and a.delta_phi == pytest.approx(b.delta_phi)
    assert (a.phi_i - b.phi_i) % 360 == pytest.approx(25)


def test_back_of_sample_not_measurable(cfg):
    assert not brdf_coords(cfg, {"M4": 200, "M3": 0}).measurable


def test_per_pixel_directions_center_matches_nominal(cfg):
    pose = {"M4": 60, "M3": 30}
    wi, wr = per_pixel_directions(cfg, pose, np.array([[0.0, 0.0], [20.0, 0.0]]))
    assert wi[0] @ wi[0] == pytest.approx(1)
    b = brdf_coords(cfg, pose)
    n = sample_normal(30)
    assert math.degrees(math.acos(wr[0] @ n)) == pytest.approx(b.theta_r, abs=1e-6)
    assert not np.allclose(wr[0], wr[1])          # directions vary across the swatch


# ---- collision ----
def test_segment_distance():
    o = np.zeros(3)
    assert segment_distance(o, np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([1, 1, 0.])) == pytest.approx(1)


def test_light_cannot_reach_camera(cfg):
    lim = min_safe_m4(cfg)
    assert 5 < lim < cfg.axes["M4"].home_deg
    assert not pose_is_safe(cfg, {"M4": lim - 2})
    assert pose_is_safe(cfg, {"M4": 90}) and clearance_mm(cfg, 180) > 200


def test_path_through_camera_rejected(cfg):
    assert path_is_safe(cfg, {"M4": 30}, {"M4": 330})[0]       # goes round the back
    assert not path_is_safe(cfg, {"M4": 30}, {"M4": 5})[0]


# ---- FluidNC + gantry ----
def test_parse_status():
    s = parse_status("<Idle|MPos:20.000,-180.000,0.000,0.000|FS:0,0|Pn:X>")
    assert s.state == "Idle" and s.mpos["X"] == 20 and s.mpos["Y"] == -180 and s.pins == "X"


def test_home_move_light_gcode(cfg):
    g, t = gantry(cfg)
    g.home()
    assert t.lines[:2] == ["$HX", "$HY"]
    assert t.lines[2].startswith("G53 G1 X180.0000")
    g.move(inplane.pose_for(30, 30))
    assert t.lines[-1].startswith("G53 G1") and "X60.0000" in t.lines[-1] and "Y30.0000" in t.lines[-1]
    g.light("white", True); g.light("white", False)
    assert t.lines[-2:] == ["M62 P0", "M63 P0"]


def test_move_rejections(cfg):
    g, _ = gantry(cfg)
    with pytest.raises(GantryError, match="not homed"):
        g.move({"M3": 10})
    g.home()
    with pytest.raises(GantryError, match="outside"):
        g.move({"M4": 10})
    with pytest.raises(GantryError, match="not installed"):
        g.move({"M2": 5})
    with pytest.raises(GantryError, match="not installed"):
        g.light("multispectral", True)


def test_sleep_and_stop_clear_homing(cfg):
    g, t = gantry(cfg)
    g.home(); g.sleep()
    assert "$MD" in t.lines and not g.homed
    g.home(); g.stop()
    assert "'!'" in t.lines and "'\\x18'" in t.lines and not g.homed


# ---- hub + panel ----
def test_hub_parse():
    assert parse("BTN HOME").value == "HOME"
    assert parse("BTN FOO") is None and parse("garbage") is None
    assert parse("POWER 0").kind == "POWER"


def test_panel_buttons(cfg):
    g, t = gantry(cfg)
    p = Panel(g, inplane.grid(cfg, 40))
    hub = FakeHub(["BTN HOME", "BTN LIGHT", "BTN NEXT", "POWER 0"])
    while (ev := hub.poll()):
        p.handle(ev.kind, ev.value)
    assert "$HX" in t.lines and "M62 P0" in t.lines and p.index == 1 and not g.homed
    p.handle("POWER", "1")
    assert t.lines[-1] == "$MI"
    hub.band(3); hub.band(None)
    assert hub.sent == ["BAND 3", "BAND OFF"]


def test_start_runs_one_pose_per_tick_and_stop_interrupts(cfg):
    g, t = gantry(cfg)
    g.home()
    p = Panel(g, inplane.grid(cfg, 30))
    p.handle("BTN", "START")
    p.tick(); p.tick()
    assert p.index == 2 and p.running
    p.handle("BTN", "STOP")
    p.tick()
    assert p.index == 2 and not p.running


# ---- plans ----
def test_inplane_grid_is_safe_and_serpentine(cfg):
    poses = inplane.grid(cfg, 10)
    assert poses and all(pose_is_safe(cfg, p) for p in poses)
    assert all(cfg.axes["M4"].in_range(p["M4"]) for p in poses)


def test_mirror_sweep_crosses_specular():
    s = inplane.mirror_sweep(30, span=1, step=0.5)
    assert any(abs(p["M3"] - 30) < 1e-9 for p in s) and all(p["M4"] == 60 for p in s)


def test_repeatability_math():
    assert summarize([45.0, 45.04, 44.98], 0.1)["pass"]
    d = reflection_shift_to_deg(8, 1.55, 16, 650, 300)
    assert 0.05 < d < 0.2          # ~8 px per 0.1 deg: the camera can see the target precision


# ---- standalone station + verify ----
def _station(tmp_path, cfg):
    import json as _json
    from opengonio.gantry.fluidnc import FluidNC, RecordingTransport
    from opengonio.gantry.gantry import Gantry
    from opengonio.gantry.hub import FakeHub
    from opengonio.station import Station

    class Cam:
        def grab(self):
            return b"img"
    saved = []
    g = Gantry(cfg, FluidNC(RecordingTransport()))
    hub = FakeHub()
    st = Station(cfg, g, hub, Cam(), tmp_path, save=lambda p, img: (p.write_bytes(img), saved.append(p)), clock=lambda: 0.0)
    return st, hub, saved, _json


def test_station_runs_job_without_laptop(tmp_path, cfg):
    st, hub, saved, json = _station(tmp_path, cfg)
    assert hub.sent[-1].startswith("SHOW OpenGonio|> Mirror")
    st.handle("BTN", "START")
    for _ in range(100):
        st.tick()
    m = json.loads((st.run_dir / "manifest.json").read_text())
    assert m["finished"] and len(m["shots"]) == len(saved) == len(st.plan) > 10
    assert "done" in hub.sent[-1]


def test_station_stop_and_next(tmp_path, cfg):
    st, hub, saved, json = _station(tmp_path, cfg)
    st.handle("BTN", "NEXT")
    assert "Swatch" in hub.sent[-1]
    st.handle("BTN", "START"); st.tick(); st.tick()
    st.handle("BTN", "STOP")
    m = json.loads((st.run_dir / "manifest.json").read_text())
    assert not st.running and m["aborted"] == "stopped" and not m["finished"]


def test_verify_pass_and_fail(tmp_path, cfg):
    import numpy as np
    from opengonio.verify import verify
    st, hub, saved, json = _station(tmp_path, cfg)
    st.handle("BTN", "START")
    for _ in range(100):
        st.tick()
    peak = min(st.plan, key=lambda p: abs(p["M3"] - p["M4"] / 2))
    img = lambda p: np.full((30, 30), 200.0 if json.loads((st.run_dir / "manifest.json").read_text())["shots"][int(p.stem[4:])]["pose"] == peak else 50.0)
    rep = verify(st.run_dir, cfg, read_image=img)
    assert rep["result"] == "PASS" and abs(rep["mirror_peak_error_deg"]) < 0.2
    saved[0].unlink()
    assert verify(st.run_dir, cfg, read_image=img)["result"] == "FAIL"
