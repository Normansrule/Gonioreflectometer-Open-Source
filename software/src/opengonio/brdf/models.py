"""Analytic BRDF models used for fitting (phase 7+).

Notation follows Hanrahan, CS348b Lecture 10 [R2]:
  f_r(w_i -> w_r) = dL_r / dE_i  [1/sr]
  Lambert:  f_r = rho_d / pi
  Schlick:  F(theta) = F0 + (1 - F0)(1 - cos theta)^5   (F0 = 0.04 for glass n = 1.5)
GGX microfacet specular (Walter et al. 2007 [R6]) with height-correlated Smith G,
the model Unreal and Unity's standard shaders use (roughness alpha = r^2).
Vectors are unit length in the sample frame, normal = +Z.
"""
from __future__ import annotations

import math

import numpy as np


def sph_to_vec(theta_deg: float, phi_deg: float) -> np.ndarray:
    t, p = math.radians(theta_deg), math.radians(phi_deg)
    return np.array([math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t)])


def lambert(rho_d: float) -> float:
    return rho_d / math.pi


def schlick_fresnel(cos_theta: float, f0: float) -> float:
    return f0 + (1.0 - f0) * (1.0 - cos_theta) ** 5


def f0_from_ior(n: float) -> float:
    return ((n - 1.0) / (n + 1.0)) ** 2


def cook_torrance_color(theta_deg: float, r0: float, r90: float, f) -> float:
    """Cook-Torrance colour shift [R2][R8]: R = R(0) + R(pi/2) [F(theta) - F(0)] / [F(pi/2) - F(0)]."""
    f0, f90 = f(0.0), f(90.0)
    return r0 + r90 * (f(theta_deg) - f0) / (f90 - f0)


def mirror_direction(wi: np.ndarray) -> np.ndarray:
    """Law of reflection [R2]: R = 2 (N . I) N - I with I pointing to the light, N = +Z."""
    n = np.array([0.0, 0.0, 1.0])
    return 2.0 * float(wi @ n) * n - wi


def refract_direction(wi: np.ndarray, eta_i: float, eta_t: float) -> np.ndarray | None:
    """Snell's law in vector form [R2]; None on total internal reflection."""
    n = np.array([0.0, 0.0, 1.0])
    mu = eta_i / eta_t
    cos_i = float(wi @ n)
    k = 1.0 - mu * mu * (1.0 - cos_i * cos_i)
    if k < 0.0:
        return None
    return -mu * wi + (mu * cos_i - math.sqrt(k)) * n


def ggx_d(cos_h: float, alpha: float) -> float:
    a2 = alpha * alpha
    d = cos_h * cos_h * (a2 - 1.0) + 1.0
    return a2 / (math.pi * d * d)


def smith_g2(cos_i: float, cos_o: float, alpha: float) -> float:
    """Height-correlated Smith masking-shadowing for GGX."""
    a2 = alpha * alpha
    li = cos_o * math.sqrt(cos_i * cos_i * (1 - a2) + a2)
    lo = cos_i * math.sqrt(cos_o * cos_o * (1 - a2) + a2)
    return 2.0 * cos_i * cos_o / (li + lo)


def ggx_brdf(wi: np.ndarray, wo: np.ndarray, base_color: float, roughness: float, metallic: float = 0.0, f0_dielectric: float = 0.04) -> float:
    """Single-channel metallic-roughness BRDF (diffuse Lambert + GGX specular)."""
    n = np.array([0.0, 0.0, 1.0])
    ci, co = float(wi @ n), float(wo @ n)
    if ci <= 0 or co <= 0:
        return 0.0
    h = wi + wo
    h /= np.linalg.norm(h)
    alpha = max(roughness * roughness, 1e-4)
    f0 = f0_dielectric * (1 - metallic) + base_color * metallic
    f = schlick_fresnel(float(wi @ h), f0)
    spec = ggx_d(float(h @ n), alpha) * smith_g2(ci, co, alpha) * f / (4 * ci * co)
    diffuse = (1 - metallic) * (1 - f) * lambert(base_color)
    return diffuse + spec


def directional_albedo(wi: np.ndarray, brdf, n_theta: int = 64, n_phi: int = 128) -> float:
    """Integral of f_r cos(theta_r) over the hemisphere (must be <= 1 for energy conservation)."""
    total = 0.0
    dt, dp = (math.pi / 2) / n_theta, (2 * math.pi) / n_phi
    for i in range(n_theta):
        t = (i + 0.5) * dt
        for j in range(n_phi):
            p = (j + 0.5) * dp
            wo = np.array([math.sin(t) * math.cos(p), math.sin(t) * math.sin(p), math.cos(t)])
            total += brdf(wi, wo) * math.cos(t) * math.sin(t) * dt * dp
    return total
