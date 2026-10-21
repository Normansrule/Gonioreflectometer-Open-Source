"""tools/cad/poses.py (no cadquery): the interference checker moves parts with the same conventions as the software
kinematics, and never reports a failed Boolean as clear (audit F22, F23)."""
import math

import numpy as np
import pytest

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "cad"))
import poses as P  # noqa: E402

from opengonio.gantry.kinematics import light_dir, sample_normal, sample_rotation


def test_classify_never_hides_a_failed_boolean():
    assert P.classify(0.0) == P.CLEAR and P.classify(0.5) == P.CLEAR
    assert P.classify(5.0) == P.INTERSECTION
    assert P.classify(None, RuntimeError("BRep failure")) == P.COMPUTATION_ERROR
    assert P.classify(-1.0, None) == P.COMPUTATION_ERROR                  # the old code's sentinel was dropped as clear
    assert P.classify(float("nan")) == P.COMPUTATION_ERROR


@pytest.mark.parametrize("m3,m2,m1", [(0, 0, 0), (30, 0, 0), (0, -90, 0), (0, 45, 0), (45, -30, 60), (-120, 70, -150)])
def test_stage_parts_follow_kinematics(m3, m2, m1):
    pose = {"M3": m3, "M2": m2, "M1": m1}
    zero = np.array([0.0, 0.0, P.ZERO_Z])
    # sample normal: +z in the shown pose (face up)
    tip = np.array(P.apply(zero + [0, 0, 10.0], "spin", pose)) - np.array(P.apply(zero, "spin", pose))
    assert np.allclose(tip / 10.0, sample_normal(m3, m2, m1), atol=1e-9)
    # a point on the face rotates with the full sample rotation
    R_shown = sample_rotation(0.0, 90.0, 0.0)
    q = np.array([3.0, -7.0, 0.0])
    want = sample_rotation(m3, m2, m1) @ R_shown.T @ q
    got = np.array(P.apply(zero + q, "spin", pose)) - zero
    assert np.allclose(got, want, atol=1e-9)


def test_tilt_convention_single_source():
    assert P.tilt_angle(90) == 0 and P.tilt_angle(0) == 90 and P.tilt_angle(-90) == 180
    # M2 = 0: the sample faces the camera (+x), as in the kinematics; the pre-audit sweep turned it to -x
    tip = P.apply([0, 0, P.ZERO_Z + 1], "tilt", {"M2": 0.0})
    assert np.allclose(tip, [1, 0, P.ZERO_Z], atol=1e-9)


def test_arm_follows_light_direction():
    for m4 in (20.0, 90.0, 200.0, 324.0):
        lamp = P.apply([0.0, 300.0, 150.0], "arm", {"M4": m4})            # lamp at +y in the shown pose (M4 = 90)
        assert np.allclose(np.array(lamp[:2]) / 300.0, light_dir(m4)[:2], atol=1e-9)


def test_groups_move_with_the_right_axes():
    assert P.moves_with("M1") == {"spin"}
    assert P.moves_with("M2") == {"spin", "tilt"}
    assert P.moves_with("M3") == {"spin", "tilt", "table"}
    assert P.moves_with("M4") == {"arm"}
    assert P.rotations("fixed", {"M4": 30, "M3": 40, "M2": 0, "M1": 10}) == []


def test_sweeps_cover_configured_travel_and_mixed_poses():
    rg = {"M4": (20.0, 324.0), "M3": (-180.0, 180.0), "M2": (-90.0, 90.0), "M1": (-180.0, 180.0)}
    sw = P.axis_sweeps(rg, 30.0)
    for k, (lo, hi) in rg.items():
        vals = [p[k] for p in sw[k]]
        assert vals[0] == lo and vals[-1] == hi and max(np.diff(vals)) <= 30.0 + 1e-9
    mixed = P.mixed_poses(rg, 4)
    assert len(mixed) == 4 ** 4 and any(p["M2"] == -90 and p["M4"] == 20 for p in mixed)
    assert math.isclose(min(p["M1"] for p in mixed), -180.0)
