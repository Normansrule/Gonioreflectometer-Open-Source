# 3D photo scanner (Phase 6)

<img src="assets/scanner.svg" width="100%" alt="Fixed camera, object spinning and tilting, view sphere filling with 144 views">

The same machine scans objects up to ~110 mm. Camera fixed; the object turns on M1 and tilts on M2, so every pose is known from the axes — a turntable scanner with calibrated poses [S9]. Note: [R1] measures flat samples only; this phase goes beyond it.

## Modes

| | BRDF mode (Phases 1–5) | Scan mode (Phase 6) |
|---|---|---|
| Camera position | 350 mm, f/8 | 650 mm, f/8 (printed stop on the outrigger) |
| Field / pixel footprint | 124 × 98 mm · 0.032 mm | 236 × 186 mm · 0.061 mm (resolution ~0.25 mm) |
| Depth of field | ~23 mm (blur ≤ 2 px) | ~117 mm (blur = diffraction) |
| Object | flat swatch on the 60 mm riser | object on a lower riser, centre at the zero point |
| Camera pose | nominal | measured by `opengonio scan calibrate` (ChArUco + joint pose fit) |

## Three ways to get shape

| Method | Uses | Gives | Code |
|---|---|---|---|
| Visual hull (silhouette carving) [S5][S6] | silhouettes on the black backdrop + known poses | fast watertight preview, convex parts | `scan/carve.py` |
| Photogrammetry with pose priors (COLMAP) [S1][S2][S3] | 144 textured views + known poses | dense mesh incl. concavities, metric (mm) | `scan/colmap.py` |
| Photometric stereo [S4] | object still, LED bank at 6 positions on the 40° mast | per-pixel normals + albedo (fine detail) | `scan/photometric.py` |

Alternatives for the dense step: Meshroom [S10], OpenMVS [S17], RealityScan [S18]. Outputs open in Blender (PLY / OBJ / glTF) [S16].

## Equations

**Object pose** (object frame O: z = platter normal; riser offset δ) [R1]:

$$p_w = R\,(P\,p_O - \delta\,\hat e_x),\qquad R = R_z(M_3)R_y(-M_2)R_x(M_1)$$

**Camera pose in the object frame** (what COLMAP stores as world-to-camera [S1]):

$$R_{oc} = R_{wc}\,R\,P,\qquad t_{oc} = -R_{wc}\,(C + \delta\,R\hat e_x)$$

**View elevation** seen from the object: $\epsilon = 90^\circ - M_2 + e_{cam}$.

**Pose calibration** (board pose $A_i$ from solvePnP [S11], platter pose $B_i$ from the axes):

$$A_i = X\,B_i\,Y \;\Rightarrow\; \min_{X,Y}\sum_i \big\lVert \log\!\left(A_i^{-1} X B_i Y\right)\big\rVert^2$$

$X$ = measured world-to-camera pose (replaces the nominal one), $Y$ = board placement on the platter.

**Pinhole projection** [S11]:

$$\lambda\begin{bmatrix}u\\v\\1\end{bmatrix} = K\,(R_{oc}\,p_O + t_{oc}),\qquad K=\begin{bmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{bmatrix},\quad f_x=\frac{p'}{\text{pixel pitch}}$$

**Visual hull** [S5] — a point survives if it is inside every silhouette $S_j$:

$$V = \bigcap_j \{\,p : \pi_j(p) \in S_j\,\}$$

**Photometric stereo** [S4] (Lambertian [R2]), $k \ge 3$ non-coplanar lights [S8]:

$$I_j = \rho\,\max(0,\ \hat n\cdot\hat l_j)\;\Rightarrow\; I = L\,g,\quad g = L^{+} I,\quad \rho = \lVert g\rVert,\quad \hat n = g/\rho$$

The white lamp only moves in the horizontal plane (rank$(L)=2$), so photometric stereo uses the LED bank on the 40° mast: $\hat l = R_z(M_4)\,(\cos 40^\circ, 0, \sin 40^\circ)^\top$.

**Near-light photometric stereo** [S14] — per-pixel light vector and $1/r^2$ falloff from the hull or mesh point $X$:

$$\hat l_j(X) = \frac{S_j - X}{\lVert S_j - X\rVert},\qquad I_j' = I_j\,\frac{\lVert S_j - X\rVert^2}{r_0^2}$$

**Pose accuracy** from axis repeatability $\Delta\theta$ at object radius $r$: $\Delta p \approx r\,\Delta\theta = 55\,\text{mm}\times 0.1^\circ \approx 0.10$ mm, after the camera pose is calibrated.

## Run it

```bash
opengonio scan plan                       # 144 views, rings at 0/20/40/60/80°
opengonio scan demo --out demo            # offline: synthetic sphere → hull PLY + photometric-stereo check
opengonio scan export-colmap --out s1     # COLMAP model with known poses + run_colmap.sh
opengonio scan calibrate --out cal        # on the machine: measured camera pose + distortion
opengonio scan run --background --out myscan   # empty platter (silhouettes)
opengonio scan run --out myscan           # object (START button works too)
cd myscan && bash run_colmap.sh           # dense mesh: dense/meshed-poisson.ply (CUDA GPU needed)
```

Milestone checklist: [ROADMAP.md → M6](../ROADMAP.md). Hardware: [`hardware/scan-kit`](../hardware/scan-kit/README.md).
