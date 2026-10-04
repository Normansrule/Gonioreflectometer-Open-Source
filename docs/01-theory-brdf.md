# BRDF theory, mapped onto this machine

Background follows Pat Hanrahan's CS348b Lecture 10, *Reflection Models I: Ideal Materials*
(Stanford, Spring 2016) — the slide deck that also pictures the Stanford four-degree-of-freedom gantry.

## What the machine measures

The **Bidirectional Reflectance Distribution Function (BRDF)** is the ratio of reflected radiance
leaving toward the camera to the irradiance arriving from the light, per steradian:

f_r(ω_i → ω_r) = dL_r(ω_r) / dE_i(ω_i)   [1/sr]

Integrating it against incoming light gives the **reflection equation**,
L_r(ω_r) = ∫ f_r(ω_i → ω_r) L_i(ω_i) cos θ_i dω_i — which is exactly what a game engine evaluates
per pixel. Our job is to sample f_r at enough (ω_i, ω_r) pairs to fit a model the engine understands.

| BRDF quantity | Machine | Phase |
|---|---|---|
| θ_r (view elevation) | A1 | 1 |
| θ_i (light elevation) | A2 | 1 |
| φ_r − φ_i (relative azimuth) | A3 (180° at A3 = 0) | 3 |
| absolute φ (anisotropy) | A4 rotates the sample frame | 4 |

`opengantry.gantry.kinematics.brdf_coords(A1, A2, A3, A4)` converts axis angles into these
coordinates.

## Properties we use as built-in tests

1. **Linearity** — total reflection is a sum of lobes (diffuse + specular), which is why a
   diffuse + GGX model works and why we can subtract dark frames.
2. **Reciprocity**, f_r(ω_r → ω_i) = f_r(ω_i → ω_r). Swapping A1 and A2 must give the same
   calibrated value. This is a free check of the radiometric calibration: a mismatch means the light
   falloff or camera response is wrong, not the material.
3. **Isotropy**: for most materials f_r depends only on θ_i, θ_r and |φ_r − φ_i|. Phases 1–3 assume
   this; Phase 4 (turntable) measures the materials that break it (brushed metal, fabric, hair).
4. **Energy conservation**: the reflected fraction ∫ f_r cos θ_r dω_r ≤ 1. Fitted parameters that
   violate it are rejected (`opengantry.brdf.models.directional_albedo`).

## Ideal cases we use for calibration

- **Ideal mirror** — reflects only where θ_r = θ_i and φ_r = φ_i ± π. The first-surface mirror in the
  calibration kit therefore produces a single peak at **A1 = A2**; where the peak really occurs tells
  us each arm's angular offset. This is the Phase 1 milestone test.
- **Ideal diffuse (Lambert)** — f_r = ρ_d / π, the same in every direction; radiance follows the cosine
  law. The PTFE block is our near-Lambertian white reference for converting pixel values into BRDF
  units (Phase 2). Real diffusers fail at grazing angles, so we only trust PTFE below about 60°.
- **Fresnel** — reflection rises toward grazing. Schlick's approximation
  F(θ) = F0 + (1 − F0)(1 − cos θ)^5 with F0 = 0.04 for a dielectric of index 1.5 is what the GGX fit
  uses for plastics and paints; metals have F0 around 0.8–0.95 and coloured F0.

## Consequences for the hardware

- A **small light source** approximates a single ω_i: the 4.5 mm COB at 300 mm subtends about 0.9°.
- The light must be **stable and not PWM-dimmed** (PWM beats against the rolling shutter), hence
  constant-current drive with plain on/off switching.
- **RAW, linear capture** with fixed exposure and HDR bracketing is needed because specular peaks
  can be 1000× brighter than the diffuse floor.
- The 30 mm keep-out means near-retroreflection (light and camera almost coincident) cannot be
  measured; the collision model tells the scan planner which poses to skip.
