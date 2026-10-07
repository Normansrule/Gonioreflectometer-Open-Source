# 07 · 3D files

## Print

PETG, 0.2 mm layers, 4 walls, 25 % gyroid, no supports unless noted. v0 geometry: measure your parts first.

**STEP** imports into Onshape as an editable solid (Insert → Import). **STL** is a mesh for the slicer.

| ID | Part | Edit (STEP) | Print (STL) |
|---|---|---|---|
| CAL-06a | PTFE holder | [CAL-06a_ptfe_holder.step](CAL-06a_ptfe_holder.step) | [CAL-06a_ptfe_holder.stl](CAL-06a_ptfe_holder.stl) |
| CAL-06b | Mirror holder | [CAL-06b_mirror_holder.step](CAL-06b_mirror_holder.step) | [CAL-06b_mirror_holder.stl](CAL-06b_mirror_holder.stl) |
| CAL-06c | Chrome-ball holder | [CAL-06c_ball_holder.step](CAL-06c_ball_holder.step) | [CAL-06c_ball_holder.stl](CAL-06c_ball_holder.stl) |
| ENC-04a | Dowel socket (print 4) | [ENC-04a_dowel_socket.step](ENC-04a_dowel_socket.step) | [ENC-04a_dowel_socket.stl](ENC-04a_dowel_socket.stl) |

Regenerate: `python tools/cad/parts.py` (parameters at the top of the file).

## Bought parts

`bash scripts/get_cad.sh` saves vendor models into `vendor/` (not committed: vendor licences).

| ID | Part | 3D model |
|---|---|---|
| ENC-01 | Blackout fabric 54 in (2 yd) | n/a |
| ENC-02 | Black felt sheet | n/a |
| ENC-03 | Poplar dowel 1/2 in x 36 in | n/a |
| CAL-01 | PTFE sheet 6 x 6 x 0.375 in | n/a |
| CAL-02 | Glass mirror tile ~50 mm | n/a |
| CAL-03 | Chrome steel ball 1 in G25 (2) | 25.4 mm sphere |
| CAL-04 | ChArUco print + picture-frame glass | n/a |
| CAL-05 | Colour target (ColorChecker Mini or similar) | n/a |
| ENC-05 | Flocked light-trap sheet 17.5 x 15 in, self-adhesive | n/a |
| CAL-07 | 18 % grey card + white card set (8 x 10 in) | n/a |

Design notes: [../design.md](../design.md).
