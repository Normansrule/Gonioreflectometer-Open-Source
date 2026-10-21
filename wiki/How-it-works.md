<!-- generated from wiki/src/How-it-works.md by tools/refs_bib.py - edit the source -->

# How it works

## What is measured

The BRDF $f_r$ is reflected radiance per unit incident irradiance, for one incoming and one outgoing direction (Hanrahan, 2016; Nicodemus et al., 1977):

``` math
f_r(\omega_i\to\omega_r)=\frac{dL_r(\omega_i\to\omega_r)}{dE_i}\;[\mathrm{sr}^{-1}]
```

Isotropic materials need 3 angles; anisotropic ones (brushed metal, satin) need 4 (Ward, 1992).

## Geometry

One zero point; every axis turns about it.

| Axis | Moves                       | Range   |
|------|-----------------------------|---------|
| M4   | light arm around the sample | 20–324° |
| M3   | table (sample yaw)          | ±180°   |
| M2   | sample tilt                 | ±90°    |
| M1   | sample spin                 | ±180°   |

- Measuring camera fixed at 350 mm; light 300 mm from the zero point.
- Light on a horizontal ring: M3 and M2 already turn the sample to every direction an overhead light could reach, so the arm stays low, stiff and out of the light path (Ansari-Asl et al., 2024).
- In-plane, the mirror peak sits at M3 = M4 / 2.
- Light within 20° of the camera is out of reach: pure back-scatter is not measured.

## One measurement

1.  Move to a pose (inverse kinematics from $\theta_i, \theta_r, \Delta\varphi$).
2.  Capture at fixed exposure; several exposures for high dynamic range (HDR) (Debevec & Malik, 1997).
3.  Subtract dark frame, linearise, divide by the white reference ([Calibration](Calibration.md)).
4.  Fit Lambert + GGX microfacet model (Trowbridge & Reitz, 1975; Walter et al., 2007) → game-engine material.

Full equations: [Theory](Theory.md).

## References

Ansari-Asl, M., Barbieri, M., Obein, G., & Hardeberg, J. Y. (2024). Optical and electromechanical design and implementation of an advanced multispectral device to capture material appearance. *Journal of Imaging*, *10*(3), 55. <https://doi.org/10.3390/jimaging10030055>

Debevec, P., & Malik, J. (1997). Recovering high dynamic range radiance maps from photographs. *Proc. SIGGRAPH ’97*. <https://pauldebevec.com/Research/HDR/debevec-siggraph97.pdf>

Hanrahan, P. (2016). *Reflection models I: Ideal materials*.

Nicodemus, F. E., Richmond, J. C., Hsia, J. J., Ginsberg, I. W., & Limperis, T. (1977). Geometrical considerations and nomenclature for reflectance. *NBS Monograph*, *160*. <https://doi.org/10.6028/NBS.MONO.160>

Trowbridge, T. S., & Reitz, K. P. (1975). Average irregularity representation of a rough surface for ray reflection. *Journal of the Optical Society of America*, *65*(5), 531–536. <https://doi.org/10.1364/JOSA.65.000531>

Walter, B., Marschner, S., Li, H., & Torrance, K. (2007). Microfacet models for refraction through rough surfaces. *Eurographics Symposium on Rendering*.

Ward, G. J. (1992). Measuring and modeling anisotropic reflection. *ACM SIGGRAPH Computer Graphics*, *26*(2), 265–272. <https://doi.org/10.1145/142920.134078>
