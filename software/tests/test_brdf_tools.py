import math

import numpy as np
import pytest
import yaml

import bom_check
import optics
import power_budget
from opengonio.brdf.models import (cook_torrance_color, directional_albedo, f0_from_ior, ggx_brdf, lambert,
                                   mirror_direction, refract_direction, schlick_fresnel, sph_to_vec)


def test_schlick_slide_values():
    assert f0_from_ior(1.5) == pytest.approx(0.04)
    assert schlick_fresnel(1.0, 0.04) == pytest.approx(0.04) and schlick_fresnel(0.0, 0.04) == pytest.approx(1.0)


def test_law_of_reflection():
    wi = sph_to_vec(35, 20)
    r = mirror_direction(wi)
    assert math.degrees(math.acos(r[2])) == pytest.approx(35)
    assert math.degrees(math.atan2(r[1], r[0])) % 360 == pytest.approx((20 + 180) % 360)


def test_snell_and_total_internal_reflection():
    wi = sph_to_vec(30, 0)
    t = refract_direction(wi, 1.0, 1.5)
    assert math.sin(math.radians(30)) == pytest.approx(1.5 * math.sqrt(t[0] ** 2 + t[1] ** 2))
    assert refract_direction(sph_to_vec(60, 0), 1.5, 1.0) is None


def test_cook_torrance_endpoints():
    f = lambda th: schlick_fresnel(math.cos(math.radians(th)), 0.04)
    assert cook_torrance_color(0, 0.5, 0.5, f) == pytest.approx(0.5)
    assert cook_torrance_color(90, 0.5, 0.5, f) == pytest.approx(1.0)


def test_lambert_white_albedo_is_one():
    assert directional_albedo(sph_to_vec(30, 0), lambda a, b: lambert(1.0)) == pytest.approx(1.0, abs=2e-3)


@pytest.mark.parametrize("r", [0.2, 0.6])
def test_ggx_reciprocity_and_energy(r):
    wi, wo = sph_to_vec(25, 10), sph_to_vec(60, 200)
    assert ggx_brdf(wi, wo, 0.5, r) == pytest.approx(ggx_brdf(wo, wi, 0.5, r))
    assert directional_albedo(sph_to_vec(45, 0), lambda a, b: ggx_brdf(a, b, 1.0, r, metallic=1.0)) <= 1.001


def test_bom_valid_and_under_hard_cap():
    rows = bom_check.load()
    assert bom_check.validate(rows) == []
    t = bom_check.totals(rows)
    assert t["grand"]["buy_all"] <= bom_check.HARD_CAP
    assert sum(bom_check.PROPOSED_CAPS.values()) <= bom_check.HARD_CAP


def test_power_headroom():
    cfg = yaml.safe_load((power_budget.INPUT).read_text())
    assert power_budget.headroom(cfg, power_budget.compute(cfg)) >= 0.25


def test_optics_basics():
    m = optics.magnification(16, 350)
    assert m == pytest.approx(16 / 334, rel=1e-6)
    assert optics.airy_um(8) == pytest.approx(2.44 * 0.55 * 8)
    assert optics.dof_mm(16, 350, 8) > optics.dof_mm(16, 350, 2)
