# 12 · Research

## 3D scan methods

Turntable reconstruction [S9].

### Methods

| Method | Uses | Gives | Code |
|---|---|---|---|
| Visual hull [S5][S6][V41] | silhouettes + known poses | fast preview, no concavities | `scan/carve.py` |
| Photogrammetry, known poses (COLMAP) [S1][S2][S3][V37] | 144 photos + poses | full mesh in mm | `scan/colmap.py` |
| Photometric stereo [S4][V25] | still object, 6 LED-bank positions | fine surface detail | `scan/photometric.py` |

Meshing: screened Poisson [V45][V46], marching cubes [V43]. Alternatives: Meshroom [S10], OpenMVS [S17], RealityScan [S18].

### Equations

**Object pose** (object frame O: z = platter normal; riser offset δ) [R1]:

$$p_w = R\,(P\,p_O - \delta\,\hat e_x),\qquad R = R_z(M_3)R_y(-M_2)R_x(M_1)$$

**Camera pose in the object frame** (COLMAP world-to-camera [S1]):

$$R_{oc} = R_{wc}\,R\,P,\qquad t_{oc} = -R_{wc}\,(C + \delta\,R\hat e_x)$$

**View elevation** seen from the object: $\epsilon = 90^\circ - M_2 + e_{cam}$.

**Camera calibration** [V10][V11][V15] ($A_i$ board pose from solvePnP [S11], $B_i$ platter pose from the axes):

$$A_i = X\,B_i\,Y \;\Rightarrow\; \min_{X,Y}\sum_i \big\lVert \log\!\left(A_i^{-1} X B_i Y\right)\big\rVert^2$$

$X$ = real camera pose, $Y$ = board placement.

**Pinhole projection** [S11]:

$$\lambda\begin{bmatrix}u\\v\\1\end{bmatrix} = K\,(R_{oc}\,p_O + t_{oc}),\qquad K=\begin{bmatrix}f_x&0&c_x\\0&f_y&c_y\\0&0&1\end{bmatrix},\quad f_x=\frac{p'}{\text{pixel pitch}}$$

**Visual hull** [S5]:

$$V = \bigcap_j \{\,p : \pi_j(p) \in S_j\,\}$$

**Photometric stereo** [S4] (Lambertian [R2]), $k \ge 3$ non-coplanar lights [S8]:

$$I_j = \rho\,\max(0,\ \hat n\cdot\hat l_j)\;\Rightarrow\; I = L\,g,\quad g = L^{+} I,\quad \rho = \lVert g\rVert,\quad \hat n = g/\rho$$

Horizontal lamp only → rank$(L)=2$; the 40° LED mast fixes it: $\hat l = R_z(M_4)(\cos 40^\circ, 0, \sin 40^\circ)^\top$.

**Near-light photometric stereo** [S14][V29][V30]:

$$\hat l_j(X) = \frac{S_j - X}{\lVert S_j - X\rVert},\qquad I_j' = I_j\,\frac{\lVert S_j - X\rVert^2}{r_0^2}$$

**Pose accuracy:** $\Delta p \approx r\,\Delta\theta = 55\,\text{mm}\times 0.1^\circ \approx 0.1$ mm (after camera calibration).
