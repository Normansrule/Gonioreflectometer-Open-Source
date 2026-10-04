import math

import numpy as np
import pytest

from opengantry.gantry.collision import clearance, path_is_safe, pose_is_safe, segment_distance
from opengantry.gantry.config import ConfigError, load_config
from opengantry.gantry.encoders import AS5600
from opengantry.gantry.gantry import Gantry, GantryError
from opengantry.gantry.kinematics import brdf_coords, camera_arm, is_specular, light_arm
from opengantry.gantry.moonraker import RecordingSink
from opengantry.gantry.power import PowerManager
from opengantry.plans.repeatability import summarize


@pytest.fixture
def cfg():
    return load_config()


# ---- configuration --------------------------------------------------------------
def test_phase_gating_adds_axes_by_config_only(cfg):
    assert list(cfg.active_axes) == ["A1", "A2"]
    assert list(cfg.with_phase(3).active_axes) == ["A1", "A2", "A3"]
    assert list(cfg.with_phase(4).active_axes) == ["A1", "A2", "A3", "A4"]


def test_rotation_distance_is_degrees_per_motor_rev(cfg):
    assert cfg.axes["A1"].rotation_distance == pytest.approx(72.0)   # 5:1
    assert cfg.axes["A4"].rotation_distance == pytest.approx(90.0)   # 4:1


def test_duplicate_encoder_bus_rejected(tmp_path, cfg):
    text = (load_config.__globals__["DEFAULT_CONFIG"]).read_text().replace("bus: 2", "bus: 1")
    p = tmp_path / "m.yaml"
    p.write_text(text)
    with pytest.raises(ConfigError):
        load_config(p)


# ---- kinematics -------------------------------------------------------------------
@pytest.mark.parametrize("theta", [10, 30, 45, 60, 80])
def test_equal_elevations_are_specular_in_plane(theta):
    assert is_specular(theta, theta)
    assert not is_specular(theta, theta + 2)


def test_brdf_coords_in_plane(cfg):
    c = brdf_coords(30, 50)
    assert c.theta_r == pytest.approx(30)
    assert c.theta_i == pytest.approx(50)
    assert c.delta_phi == pytest.approx(180)


def test_turntable_rotates_sample_frame_not_delta_phi():
    a = brdf_coords(40, 40, a3=0, a4=0)
    b = brdf_coords(40, 40, a3=0, a4=37)
    assert a.delta_phi == pytest.approx(b.delta_phi)
    assert (a.phi_i - b.phi_i) % 360 == pytest.approx(37)


def test_heads_sit_on_working_radius(cfg):
    for t in (0, 33, 85):
        assert np.linalg.norm(camera_arm(cfg, t).head) == pytest.approx(cfg.working_radius_mm)
        assert np.linalg.norm(light_arm(cfg, t, 70).head) == pytest.approx(cfg.working_radius_mm)


# ---- collision ----------------------------------------------------------------------
def test_segment_distance_basics():
    o = np.zeros(3)
    assert segment_distance(o, np.array([1, 0, 0.]), np.array([0, 1, 0.]), np.array([1, 1, 0.])) == pytest.approx(1)
    assert segment_distance(o, np.array([2, 0, 0.]), np.array([1, -1, 0.]), np.array([1, 1, 0.])) == pytest.approx(0)


def test_both_arms_overhead_collide(cfg):
    assert not pose_is_safe(cfg, {"A1": 0, "A2": 0})


def test_home_and_typical_poses_are_safe(cfg):
    assert pose_is_safe(cfg, {"A1": 85, "A2": 85})
    assert pose_is_safe(cfg, {"A1": 45, "A2": 45})


def test_minimum_in_plane_separation_exists(cfg):
    # find the smallest symmetric elevation that clears the keep-out
    safe = [t for t in range(0, 86) if pose_is_safe(cfg, {"A1": t, "A2": t})]
    assert safe and 5 <= safe[0] <= 20, safe[:3]


def test_path_check_finds_unsafe_crossing(cfg):
    ok, bad = path_is_safe(cfg, {"A1": 85, "A2": 85}, {"A1": 0, "A2": 85})
    assert ok  # light parked at grazing angle, camera can go overhead
    ok, bad = path_is_safe(cfg, {"A1": 45, "A2": 5}, {"A1": 2, "A2": 5})
    assert not ok and bad is not None


# ---- gantry G-code ------------------------------------------------------------------
def test_home_then_coordinated_move(cfg):
    sink = RecordingSink()
    g = Gantry(cfg, sink)
    g.home()
    assert "STOP_ON_ENDSTOP=1" in sink.scripts[0] and "a1_camera_el" in sink.scripts[0]
    g.move({"A1": 45, "A2": 25})
    last = sink.scripts[-1].splitlines()
    assert last[0].endswith("SYNC=0") and not last[1].endswith("SYNC=0")
    # speeds scaled so both finish together: 40 deg vs 60 deg at 20 deg/s -> 3 s
    speeds = [float(l.split("SPEED=")[1].split()[0]) for l in last]
    assert speeds[0] == pytest.approx(40 / 3, rel=1e-3) and speeds[1] == pytest.approx(20)


def test_move_rejections(cfg):
    g = Gantry(cfg, RecordingSink())
    with pytest.raises(GantryError, match="not homed"):
        g.move({"A1": 45})
    g.home()
    with pytest.raises(GantryError, match="outside"):
        g.move({"A1": 95})
    with pytest.raises(GantryError, match="not installed"):
        g.move({"A3": 10})
    g.move({"A1": 10, "A2": 30})
    with pytest.raises(GantryError, match="keep-out"):
        g.move({"A2": 2})


def test_power_manager_refuses_wake_on_estop(cfg):
    pins = {17: False, 27: True}
    pm = PowerManager(cfg, RecordingSink(), lambda p: pins[p])
    assert pm.status().estop_active
    with pytest.raises(RuntimeError, match="E-stop"):
        pm.wake()
    pins[17] = True
    pm.sleep(); pm.wake()
    assert pm.sink.scripts == ["OG_SLEEP", "OG_WAKE"]


# ---- encoders -------------------------------------------------------------------------
class FakeBus:
    def __init__(self, raw, status=0x20):
        self.raw, self.st = raw, status

    def read_byte_data(self, addr, reg):
        return self.st

    def read_i2c_block_data(self, addr, reg, n):
        return [(self.raw >> 8) & 0x0F, self.raw & 0xFF]


def test_as5600_angle_and_wrap():
    assert AS5600(FakeBus(1024)).angle(4) == pytest.approx(90.0)
    assert AS5600(FakeBus(4095)).angle(4) == pytest.approx(-360 / 4096, abs=1e-6)
    assert AS5600(FakeBus(1024), offset_deg=45).angle(4) == pytest.approx(45.0)
    assert AS5600(FakeBus(0, status=0x10)).status().ok is False


def test_repeatability_summary():
    s = summarize([45.00, 45.05, 44.97, 45.02], 0.1)
    assert s["pass"] and s["max_dev_deg"] < 0.06
    assert not summarize([45.0, 45.3], 0.1)["pass"]
