import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest

from opengantry.brdf.models import directional_albedo, ggx_brdf, schlick_fresnel, sph_to_vec
from opengantry.brdf.models import f0_from_ior, lambert

ROOT = Path(__file__).resolve().parents[2]


def _tool(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    import sys
    sys.modules[name] = mod  # dataclasses look the module up while executing it
    spec.loader.exec_module(mod)
    return mod


def test_schlick_matches_slide_values():
    assert f0_from_ior(1.5) == pytest.approx(0.04)
    assert schlick_fresnel(1.0, 0.04) == pytest.approx(0.04)
    assert schlick_fresnel(0.0, 0.04) == pytest.approx(1.0)


def test_lambert_white_reflects_everything():
    wi = sph_to_vec(30, 0)
    assert directional_albedo(wi, lambda a, b: lambert(1.0)) == pytest.approx(1.0, abs=2e-3)


@pytest.mark.parametrize("rough", [0.2, 0.5, 0.9])
def test_ggx_reciprocity(rough):
    wi, wo = sph_to_vec(25, 10), sph_to_vec(60, 200)
    assert ggx_brdf(wi, wo, 0.5, rough) == pytest.approx(ggx_brdf(wo, wi, 0.5, rough))


@pytest.mark.parametrize("theta", [0, 45, 75])
def test_ggx_energy_conservation(theta):
    wi = sph_to_vec(theta, 0)
    alb = directional_albedo(wi, lambda a, b: ggx_brdf(a, b, 1.0, 0.6, metallic=1.0))
    assert alb <= 1.0 + 1e-3


def test_bom_validates_and_stock_path_fits_hard_cap():
    bc = _tool("bom_check")
    rows = bc.load()
    assert bc.validate(rows) == []
    t = bc.totals(rows)
    assert t["grand"]["stock"] <= bc.HARD_CAP
    for p, cap in bc.PHASE_CAPS.items():
        assert t["phase"][p]["stock"] <= cap + 0.005, p


def test_power_budget_headroom_and_buck_realistic():
    pb = _tool("power_budget")
    import yaml
    cfg = yaml.safe_load((ROOT / "data" / "power_loads.yaml").read_text())
    res = pb.compute(cfg)
    assert pb.headroom(cfg, res) >= 0.25
    assert res["peak"].amps_24v < 5.0
    assert res["idle"].wall_w < 8.0
