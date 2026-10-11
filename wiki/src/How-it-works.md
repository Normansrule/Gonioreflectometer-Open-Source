# How it works

## What is measured

The BRDF $f_r$ is reflected radiance per unit incident irradiance, for one incoming and one outgoing direction [@G1; @R2]:

```math
f_r(\omega_i\to\omega_r)=\frac{dL_r(\omega_i\to\omega_r)}{dE_i}\;[\mathrm{sr}^{-1}]
```

Isotropic materials need 3 angles; anisotropic ones (brushed metal, satin) need 4 [@G9].

## Geometry

One zero point; every axis turns about it.

| Axis | Moves | Range |
|---|---|---|
| M4 | light arm around the sample | 20–324° |
| M3 | table (sample yaw) | ±180° |
| M2 | sample tilt | ±90° |
| M1 | sample spin | ±180° |

- Measuring camera fixed at 350 mm; light 300 mm from the zero point.
- Light on a horizontal ring: M3 and M2 already turn the sample to every direction an overhead light could reach, so the arm stays low, stiff and out of the light path [@R1].
- In-plane, the mirror peak sits at M3 = M4 / 2.
- Light within 20° of the camera is out of reach: pure back-scatter is not measured.

## One measurement

1. Move to a pose (inverse kinematics from $\theta_i, \theta_r, \Delta\varphi$).
2. Capture at fixed exposure; several exposures for high dynamic range (HDR) [@R5].
3. Subtract dark frame, linearise, divide by the white reference ([Calibration](Calibration.md)).
4. Fit Lambert + GGX microfacet model [@R6; @T11] → game-engine material.

Full equations: [README theory]({{REPO}}/README.md#theory-and-equations).
