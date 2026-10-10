#!/usr/bin/env python3
"""Starter geometry for every printed part (CadQuery). Writes STEP (edit in Onshape) + STL (slice) into phases/NN/3d/.

    pip install cadquery          # once
    python tools/cad/parts.py     # all parts;  --only CAL-06a  for one

These are v0 starting points: dimensions come from the docs and datasheets, not from your measured parts.
Measure, edit the PARAMETERS below (or import the STEP into Onshape), print one, check, then commit.
SPDX-License-Identifier: CERN-OHL-S-2.0
"""
from __future__ import annotations

import argparse
import math
import sys
from pathlib import Path

import cadquery as cq

sys.path.insert(0, str(Path(__file__).resolve().parent))
import stepio  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]

# ---------------- PARAMETERS (mm) ----------------
CLEAR = 0.2                       # print clearance; set from the tolerance coupon (M03)
M3_TAP = 2.7                      # M3 screw self-taps into ABS (no heat-set inserts, no soldering iron); set from the coupon (M03)
WOOD = 4.6                        # #8 wood screw clearance [F8]; 6 mm flanges so a 16 mm screw stays inside 12 mm plywood
M2_5, M3, M4, M5, M8 = 2.9, 3.4, 4.5, 5.5, 8.5
OG40 = 40.0                       # interface: 4 x M4 on a 40 mm square + 6.2 mm locator
BEARING_608 = (22.0 + CLEAR, 7.0)  # OD, width
NEMA17_HOLES, NEMA17_BOSS = 31.0, 22.5
GT2_PITCH = 2.0


def og40_holes(wp: cq.Workplane) -> cq.Workplane:
    h = OG40 / 2
    return wp.pushPoints([(h, h), (-h, h), (h, -h), (-h, -h)]).hole(M4).faces(">Z").workplane().hole(6.2)


# ---------------- 00 plan ----------------
def tolerance_coupon():
    """M3 self-tap holes 2.5-2.9 and 608 pockets 22.0-22.4: pick what fits, set CLEAR / M3_TAP."""
    p = cq.Workplane("XY").box(100, 60, 8, centered=(False, False, False))
    for i, d in enumerate((2.5, 2.6, 2.7, 2.8, 2.9)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(8).translate((12 + 19 * i, 10, 0)))
        p = p.cut(cq.Workplane("XY").box(1, 2 + i, 1, centered=(True, False, False)).translate((12 + 19 * i, 15, 7)))
    for i, d in enumerate((22.0, 22.2, 22.4)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(7.1).translate((18 + 32 * i, 40, 0.9)))
    return p


# ---------------- 01 power ----------------
BOX_H = 60.0                      # e-stop needs 48.7 mm behind the lid (IDEC YW, screw terminals + cover) + 6 mm wire bend


def power_box():
    L, W, H, t = 120.0, 80.0, BOX_H, 2.4                       # 6 perimeters of 0.4 mm: stiff enough in ABS
    b = cq.Workplane("XY").box(L, W, H, centered=(True, True, False)).faces(">Z").shell(-t)
    for sx in (-1, 1):
        for sy in (-1, 1):
            post = cq.Workplane("XY").circle(4.5).extrude(H - 3).translate((sx * (L / 2 - t - 4), sy * (W / 2 - t - 4), 0))
            post = post.cut(cq.Workplane("XY").circle(M3_TAP / 2).extrude(10).translate((sx * (L / 2 - t - 4), sy * (W / 2 - t - 4), H - 11)))
            b = b.union(post)
    def side(w, h, y, z):                                                                               # +X wall
        return cq.Workplane("YZ").rect(w, h).extrude(20).translate((L / 2 - 10, y, z))
    b = b.cut(side(11.5, 20, -22, H - 10 + 0.01))                                                       # DC jack adapter [P45]: slot from the top, lid holds it
    b = b.cut(cq.Workplane("XY").circle(5.75).extrude(20).rotate((0, 0, 0), (0, 1, 0), 90).translate((L / 2 - 10, -22, H - 20)))
    b = b.cut(cq.Workplane("YZ").rect(14, 8).extrude(20).translate((-L / 2 - 10, -18, 15)))             # 24 V out pair (-X)
    b = b.cut(cq.Workplane("YZ").rect(10, 6).extrude(20).translate((-L / 2 - 10, 10, 15)))              # J3 over-travel loop
    for k in range(6):                                                                                   # vents (-Y)
        b = b.cut(cq.Workplane("XZ").rect(3, 20).extrude(-20).translate((-30 + 12 * k, -W / 2 + 10, 28)))
    h = OG40 / 2
    for x, y in ((h, h), (-h, h), (h, -h), (-h, -h)):                                                   # 6 mm bosses: a 16 mm wood screw
        b = b.union(cq.Workplane("XY").circle(5).extrude(6).translate((x, y, 0)))                       # stays inside 12 mm plywood [F8]
        b = b.cut(cq.Workplane("XY").circle(M4 / 2).extrude(6).translate((x, y, 0)))
    return b


def power_lid():
    L, W, t = 120.0, 80.0, 3.2
    lid = cq.Workplane("XY").box(L, W, t, centered=(True, True, False))
    lid = lid.faces(">Z").workplane().hole(22.3)                                                          # e-stop [P16]
    pts = [(sx * (L / 2 - t - 4), sy * (W / 2 - t - 4)) for sx in (-1, 1) for sy in (-1, 1)]
    return lid.faces(">Z").workplane().pushPoints(pts).cboreHole(M3, 6, 1.8)


# ---------------- 02 controller ----------------
def button_panel():
    """Two 1x4 membrane keypads [C9] in 0.6 mm locating recesses (adhesive back) + tail slots + OLED window."""
    p = cq.Workplane("XY").box(160, 60, 3, centered=(True, True, False))
    for x in (-38, 38):
        p = p.cut(cq.Workplane("XY").rect(70 + CLEAR, 20 + CLEAR).extrude(0.6).translate((x - 8, -10, 2.4)))
        p = p.cut(cq.Workplane("XY").rect(12, 2.5).extrude(3).translate((x - 8, -21.5, 0)))             # tail through
    p = p.cut(cq.Workplane("XY").rect(26, 15).extrude(3).translate((55, 12, 0)))                       # OLED [H52]
    p = p.faces(">Z").workplane().pushPoints([(75, -25), (-75, -25), (75, 25), (-75, 25)]).hole(M3)
    return p


PICO_PEG = 8.0                    # tray floor 3 + 5 mm under the Pico's component side (USB, BOOTSEL, debug header)


def controller_tray():
    """Base for E4 + Pico. E4 holes from FYSETC "E4 V1.0B.step" [C1]: 4 x 3.2 mm on 83.6 x 60.6 mm."""
    t = cq.Workplane("XY").box(200, 130, 3, centered=(True, True, False))
    e4 = [(-50 + x, y) for x in (-41.8, 41.8) for y in (-30.3, 30.3)]                                  # measured from the vendor STEP
    pico = [(52 + x, -42 + y) for x in (-23.5, 23.5) for y in (-5.7, 5.7)]                            # 47 x 11.4 [C6]
    t = t.cut(cq.Workplane("XY").rect(82.5 + CLEAR, 55 + CLEAR).extrude(1).translate((52, 20, 2.01)))   # breadboard [P46] locator
    t = t.cut(cq.Workplane("XY").rect(70, 46).extrude(3).translate((-50, 0, 0)))                         # window under the E4 (air, less ABS)
    for x, y in e4:
        t = t.union(cq.Workplane("XY").circle(3.5).extrude(9).translate((x, y, 0)))
        t = t.cut(cq.Workplane("XY").circle(M3_TAP / 2).extrude(9).translate((x, y, 3)))
    for x, y in pico:                                  # push-fit pegs through the Pico's 2.1 mm holes; Pico H mounts components
        t = t.union(cq.Workplane("XY").circle(2.5).extrude(PICO_PEG).translate((x, y, 0)))       # down, header pins UP, so the
        t = t.union(cq.Workplane("XY").circle(0.95).extrude(2.5).translate((x, y, PICO_PEG)))     # jumpers plug in from above
    for x, y in ((92, 57), (-92, 57), (92, -57), (-92, -57)):                                       # corner bosses, 6 mm: 16 mm wood screws
        t = t.union(cq.Workplane("XY").circle(5).extrude(6).translate((x, y, 0)))                      # stay inside 12 mm plywood [F8]
        t = t.cut(cq.Workplane("XY").circle(WOOD / 2).extrude(6).translate((x, y, 0)))
    return t


# ---------------- 03 frame ----------------
def og40_adapter():
    """6 mm plate: 4 edge holes take #8 wood screws into the plywood [F8] (no tee nuts, no drilling);
    the OG-40 square (M4 = #8 clearance) carries the part on top."""
    p = cq.Workplane("XY").box(56, 56, 6, centered=(True, True, False))
    p = og40_holes(p.faces(">Z").workplane())
    return p.faces(">Z").workplane().pushPoints([(24, 0), (-24, 0), (0, 24), (0, -24)]).cskHole(WOOD, 9, 90)


def foot():
    """Corner foot: two #8 wood screws up into the plywood (6 mm under the heads). Flat, no levelling bolts:
    the optics are referenced to the board, not to gravity."""
    f = cq.Workplane("XY").box(50, 50, 12, centered=(True, True, False)).edges("|Z").fillet(6)
    f = f.cut(cq.Workplane("XY").rect(36, 36).extrude(8))                                          # hollow from below: 7 mm
    for x, y in ((-12, 12), (12, -12)):                                                            # walls, 4 mm top
        f = f.union(cq.Workplane("XY").circle(7).extrude(12).translate((x, y, 0)))                  # screw bosses
        f = f.cut(cq.Workplane("XY").circle(WOOD / 2).extrude(12).translate((x, y, 0)))
        f = f.cut(cq.Workplane("XY").circle(4.5).extrude(6).translate((x, y, 0)))                    # head pocket, 6 mm left above
    return f


def extrusion_saddle():
    """Holds the 2020 outrigger on the board: 4 #8 wood screws down, 2 M5 x 10 sideways into T-nuts in the side slots."""
    s = cq.Workplane("XY").box(45, 40, 6, centered=(True, True, False))
    s = s.faces(">Z").workplane().pushPoints([(sx * 16, sy * 13) for sx in (-1, 1) for sy in (-1, 1)]).cskHole(WOOD, 9, 90)
    for sy in (-1, 1):
        s = s.union(cq.Workplane("XY").box(20, 5, 16, centered=(True, True, False)).translate((0, sy * (10.2 + CLEAR / 2 + 2.5), 6)))
        s = s.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(30, both=True).translate((0, 0, 16)))
    return s


def post_socket():
    """Stands the 500 mm scan-camera post upright on the outrigger (x = 674.4): straddles its top 14 mm (M5 x 10
    sideways into a side-slot T-nut) and holds the post in a socket (M5 x 10 into the post)."""
    s = cq.Workplane("XY").box(40, 32, 20, centered=(True, True, False))
    s = s.cut(cq.Workplane("XY").rect(40, 20.4).extrude(14))                                      # straddles the outrigger
    s = s.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(20, both=True).translate((0, 0, 4)))      # into a side T-nut
    sock = cq.Workplane("XY").box(30, 30, 30, centered=(True, True, False)).translate((0, 0, 20))
    sock = sock.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(26).translate((0, 0, 24)))
    return s.union(sock).cut(cq.Workplane("YZ").circle(M5 / 2).extrude(40).translate((-20, 0, 38)))


OUTRIGGER_X = (215.0, 715.0)      # 500 mm 2020 along +x, in the two saddles (x = 237, 282)


def camera_pillar():
    """Measuring-camera pillar (x = 391.8): straddles the outrigger like the post socket and rises as a printed 20 x 20
    column to z 196, so nothing stands in the scan camera's line of sight (a 500 mm post here would cut through the
    middle of its picture; its sight lines pass x = 392 above z 236). The camera plate's clamp slides down the column;
    its M5 x 10 self-taps into the 4.2 mm pilot at the camera axis (z = 150); the optional spectral tube (SPC-03a)
    clamps above it (pilot at z 181). Print standing up, brim on."""
    base_z = 12.0                                                    # straddle bottom (outrigger 6..26 above the board)
    s = cq.Workplane("XY").box(40, 32, 20, centered=(True, True, False))
    s = s.cut(cq.Workplane("XY").rect(40, 20.4).extrude(14))                                      # straddles the outrigger
    s = s.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(20, both=True).translate((0, 0, 4)))      # into a side T-nut
    top = 196.0 - base_z
    col = cq.Workplane("XY").box(20, 20, top - 20, centered=(True, True, False)).translate((0, 0, 20))
    col = col.union(cq.Workplane("XY").box(30, 30, 10, centered=(True, True, False)).translate((0, 0, 20)))   # foot fillet
    col = col.faces(">Z").edges().chamfer(1.5)
    for z in (150.0, 181.0):                                         # camera axis, spectral tube clamp
        col = col.cut(cq.Workplane("XZ").circle(4.2 / 2).extrude(20, both=True).translate((0, 0, z - base_z)))
    return s.union(col)


def end_foot():
    """Holds the far end of the outrigger level with the saddles: 30 mm = feet (12) + plywood (12) + saddle floor (6)."""
    f = cq.Workplane("XY").box(40, 40, 30, centered=(True, True, False))
    f = f.union(cq.Workplane("XY").box(20, 32, 12, centered=(True, True, False)).translate((0, 0, 30)))
    f = f.cut(cq.Workplane("XY").rect(20, 20.4).extrude(12).translate((0, 0, 30)))
    return f.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(20, both=True).translate((0, 0, 36)))


def washers():
    """8 x 4 mm washers for the lazy-Susan wood screws: the steel plate is thin, so a 16 mm screw would poke through
    12 mm plywood without them (2 mm plate + 4 mm washer = 6 mm, like every printed flange)."""
    w = cq.Workplane("XY")
    for i in range(8):
        w = w.union(cq.Workplane("XY").circle(6).circle(WOOD / 2).extrude(4).translate((16 * (i % 4), 16 * (i // 4), 0)))
    return w


def protractor_segment():
    """80 deg scale segment for the ring (print 4: 20-100, 100-180, 180-260, 260-340 deg; the gap around 0 deg is the
    M4 motor and the arm's keep-out). Ticks every 5 deg, long ticks every 10 deg."""
    r0, r1, span, th = 160.0, 175.0, 80, 2.0
    seg = cq.Workplane("XY").circle(r1).circle(r0).extrude(th)
    wedge = cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.radians(span)), 300 * math.sin(math.radians(span)))]).close().extrude(3)
    seg = seg.intersect(wedge)
    for a in range(0, span + 1, 5):
        ln = 9 if a % 10 == 0 else 5
        tick = cq.Workplane("XY").rect(ln, 0.8).extrude(1).translate((r1 - ln / 2, 0, th - 0.8)).rotate((0, 0, 0), (0, 0, 1), a)
        seg = seg.cut(tick)
    return seg


# ---------------- 04 light arm ----------------
RIM_TEETH = 480                               # 24:1 with a 20T pinion meshing the rim belt; set gear_ratio from the real rim
RIM_R = RIM_TEETH * GT2_PITCH / (2 * math.pi)


GT2_BACK = 0.38                               # GT2 belt back -> pitch line (1.38 thick - 0.75 tooth - 0.254 PLD)
RIM_SEAT_R = RIM_R - GT2_BACK                 # belt back glued here (teeth out): its pitch line lands on RIM_R
RIM_BODY_R = RIM_R - 2.5                      # the pinion's 16 mm flanges reach r = RIM_R - 1.6 at the mesh
RIM_H, BAND_Z = 9.0, (1.5, 7.5)               # 6 mm belt band; belt edges line up with the band edges


def rim_segment(inner: float = 22.0):
    """1/8 of the belt rim. The GT2 belt is CA-glued teeth-out on a 6 mm band whose edges match the belt's; no lips,
    so the 20T pinion's flanges pass above and below the band (lips would collide with them). Print 7 (+ the arm
    segment LAR-08c). Two radial M4 slots: bolt (M4 x 16 + nut) through whichever top-plate hole falls under a slot;
    CA-glue the rest; the belt ties the ring together."""
    seg = cq.Workplane("XY").circle(RIM_BODY_R).circle(RIM_R - inner).extrude(RIM_H)
    seg = seg.union(cq.Workplane("XY").circle(RIM_SEAT_R).circle(RIM_BODY_R - 1).extrude(BAND_Z[1] - BAND_Z[0]).translate((0, 0, BAND_Z[0])))
    wedge = cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.radians(45)), 300 * math.sin(math.radians(45)))]).close().extrude(10)
    seg = seg.intersect(wedge)
    for a in (11.25, 33.75):                                                          # radial slots, r = RIM_R-20 .. RIM_R-6
        sl = cq.Workplane("XY").slot2D(14 + M4, M4, 0).extrude(RIM_H).translate((RIM_R - 13, 0, 0))
        seg = seg.cut(sl.rotate((0, 0, 0), (0, 0, 1), a))
    return seg


RING_MOTOR_R = RIM_R + 20 * GT2_PITCH / (2 * math.pi)   # pitch circles touch: 20T pinion on the rim belt's pitch line


def ring_motor_mount():
    """M4 drive at angle 0 (+X). The base screws to the plywood OUTSIDE the lazy Susan (r > 156) through slots that
    stay reachable from above; the 56 mm motor plate cantilevers inward at z 25 above the rim, narrow enough that the
    arm segment clears it at the travel ends (lamp 20 / 324 deg = upright 35 / 339 deg). Motor stands on the plate, shaft down; its 20T pulley meshes
    with the teeth-out rim belt at band height. Radial slots set the mesh. Local x = radius - RING_MOTOR_R."""
    pz, WB, WP = 25.0, 96.0, 56.0
    x0 = 156.0 - RING_MOTOR_R                                   # base starts outside the lazy Susan
    x1 = 211.0 - RING_MOTOR_R                                   # ...and stops before saddle 1 (x = 214.5)
    base = cq.Workplane("XY").box(x1 - x0, WB, 6, centered=(False, True, False)).translate((x0, 0, 0))
    for y in (-38, 38):                                         # outside the plate: a screwdriver reaches them
        base = base.cut(cq.Workplane("XY").slot2D(x1 - x0 - 14, WOOD, 0).extrude(6).translate(((x0 + x1) / 2, y, 0)))
    walls = cq.Workplane("XY").box(6, WP, pz - 6, centered=(False, True, False)).translate((x1 - 6, 0, 6))
    for s in (-1, 1):
        walls = walls.union(cq.Workplane("XY").box(x1 - x0, 6, pz - 6, centered=(False, False, False)).translate((x0, s * WP / 2 - (6 if s > 0 else 0), 6)))
    plate = cq.Workplane("XY").box(x1 + 26, WP, 5, centered=(False, True, False)).translate((-26, 0, pz))
    plate = plate.cut(cq.Workplane("XY").slot2D(NEMA17_BOSS + 8, NEMA17_BOSS, 0).extrude(5).translate((0, 0, pz)))
    for x in (-1, 1):
        for y in (-1, 1):
            plate = plate.cut(cq.Workplane("XY").slot2D(3.4 + 8, 3.4, 0).extrude(5).translate((x * NEMA17_HOLES / 2, y * NEMA17_HOLES / 2, pz)))
    return base.union(walls).union(plate)


ARM_R = RIM_R - 16.0                          # light-arm upright centre radius (on the rim, inside the belt band)
UPRIGHT_OFFSET = 36.0                         # upright stands this far BESIDE the lamp's beam line, not on it: a 20 mm
                                              # upright on the beam line would shade the sample (beam bundle +-21 mm there)
UPRIGHT_LEAD = math.degrees(math.asin(UPRIGHT_OFFSET / ARM_R))     # upright azimuth - lamp azimuth, 15.3 deg
LAMP_ARM_X = -UPRIGHT_OFFSET + 22.0           # horizontal arm, measured from the beam line (cross-clamp pitch 22 mm)


def arm_segment():
    """Arm segment: one rim segment (same belt band and slots, wider inward) carrying the 2020 upright socket at its
    middle (22.5 deg), so the arm needs no plate holes of its own and cannot collide with the rim. The socket is
    turned by -UPRIGHT_LEAD so the cross clamp and the horizontal arm run parallel to the beam line (the upright
    stands 36 mm beside it). Turn the rim so one slot lands on a top-plate hole: M4 x 16 + nut there, CA-glue the
    whole underside."""
    seg = rim_segment(inner=31.0)
    sock = cq.Workplane("XY").box(30, 30, 30, centered=(True, True, False)).translate((0, 0, RIM_H))
    sock = sock.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(26).translate((0, 0, RIM_H + 4)))
    sock = sock.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(40).translate((0, 20, RIM_H + 18)))      # M5 x 10 into a T-nut
    sock = sock.rotate((0, 0, 0), (0, 0, 1), -UPRIGHT_LEAD).translate((ARM_R, 0, 0))
    return seg.union(sock.rotate((0, 0, 0), (0, 0, 1), 22.5))


def cross_clamp():
    """Joins the light-arm upright and the horizontal arm side by side (channels 22 mm apart, not crossing), so the
    500 mm upright runs straight through: slide the clamp to lamp height on an uncut upright. M5 x 10 into a T-nut in each."""
    c = cq.Workplane("XY").box(54, 32, 32, centered=(True, True, False))
    c = c.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(32).translate((-11, 0, 0)))               # upright, through (along z)
    c = c.cut(cq.Workplane("XZ").rect(20.4, 20.4).extrude(20, both=True).translate((11, 0, 16)))     # arm, through (along y)
    c = c.cut(cq.Workplane("YZ").circle(M5 / 2).extrude(10).translate((-27, 0, 16)))               # into the upright, from -x
    return c.cut(cq.Workplane("XY").circle(M5 / 2).extrude(6).translate((11, 0, 26)))              # into the arm, from above


# ---------------- 05/08/09 axes: bolts as axles (no shafts to cut, no flats to file) ----------------
# Table: an M8 x 70 bolt turns in two 608s; head, inner races, spacers, the 100T pulley and the hub are clamped by
# one M8 nut in the hub's hex trap, so the stack turns as one. Tilt: two M8 x 35 stub bolts, nuts trapped in the
# cradle. Spin: direct drive, the platter clamps the pancake motor's D-shaft.
M8_NUT = 13.0 + 0.3                                       # across flats + clearance (hex trap)
STACK = {"head": 5.5, "bearing": 7.0, "pulley": 9.4, "shim_head": 2.0, "shim": 1.0}
MOTOR_BODY = 48.0                                         # 17HS19-2004S1 [P40]


def gt2_pulley(teeth: int, bore: float = 8.0 + CLEAR):
    """Printed GT2 pulley (simplified round-tooth profile), hubless: clamped on the tilt stub bolt. 100T = tilt (5:1)."""
    pd = teeth * GT2_PITCH / math.pi
    od = pd - 0.508
    body = cq.Workplane("XY").circle(od / 2).extrude(7)
    body = body.cut(cq.Workplane("XY").polarArray(od / 2 + 0.15, 0, 360, teeth).circle(0.6).extrude(7))
    fl = cq.Workplane("XY").circle(od / 2 + 2).extrude(1.2)
    p = fl.union(body.translate((0, 0, 1.2))).union(fl.translate((0, 0, 8.2)))
    return p.cut(cq.Workplane("XY").circle(bore / 2).extrude(10))


def home_flag():
    """1.5 mm blade for the TCST2103 3.1 mm slot, with a tab: two M3 x 8 self-tap into the moving part. Print 3."""
    tab = cq.Workplane("XY").box(16, 10, 4, centered=(True, True, False))
    tab = tab.faces(">Z").workplane().pushPoints([(-4.5, 0), (4.5, 0)]).hole(M3)
    blade = cq.Workplane("XY").box(1.5, 24, 10, centered=(True, False, False)).translate((0, 5, 0))
    return tab.union(blade)


# Table: FIXED axle. An M8 x 75 bolt stands in the post, its head locked in a hex pocket. The rotating drum (100T teeth
# + hub) carries two 608s on their OUTER races; the inner races sit on the bolt, clamped by a 1 mm shim on the post top,
# a 6 mm spacer and the top nut (13 mm spanner, the bolt can't turn). Like a skateboard wheel: nothing to cut or file.
# Heights in mm above the plywood. The motor stands shaft-up inside the lazy Susan opening (ID ~160 mm); its 20T teeth
# (z ~54-61) set the drum's tooth band.
TABLE_Z = {"floor": 1.0}
TABLE_Z["head_top"] = TABLE_Z["floor"] + STACK["head"]                  # bolt head 1.0 .. 6.5, hex-locked
TABLE_Z["drum"] = MOTOR_BODY + 5.5                                      # drum bottom 53.5 (0.5 above the motor bracket); teeth 54.7 .. 61.7
TABLE_Z["post_top"] = TABLE_Z["drum"] - STACK["shim"]                   # 51.8: the shim carries the lower inner race
TABLE_Z["b1"] = TABLE_Z["drum"]                                         # lower 608 52.8 .. 59.8 (in the drum)
TABLE_Z["b2"] = TABLE_Z["b1"] + STACK["bearing"] + 6.0                  # upper 608 65.8 .. 72.8
TABLE_Z["nut"] = TABLE_Z["b2"] + STACK["bearing"]                       # M8 nut 72.8 .. 79.3 (bolt end 81.5)
TABLE_Z["hub_top"] = TABLE_Z["nut"] + 7.2                               # drum top 80.0: yoke base sits here
TABLE_BELT_C = 49.4                                                      # 232 mm GT2 loop, 20T-100T centre distance


def spacers():
    """All printed spacers (r 6: inner races only). Table: 1 mm shim (post top) + 6 mm spacer.
    Tilt: 2 x 6.8 (arm -> cradle), 2 x 1 mm (pulley / head side), 1 x 9.4 (the side without a pulley)."""
    hs = [STACK["shim"], 6.0, 6.8, 6.8, 1.0, 1.0, STACK["pulley"]]
    s = cq.Workplane("XY")
    for i, h in enumerate(hs):
        s = s.union(cq.Workplane("XY").circle(6).circle(4.2 + CLEAR / 2).extrude(h).translate((16 * (i % 4), 16 * (i // 4), 0)))
    return s


def table_post():
    """Fixed post at (0, 0): round flange (4 #8 wood screws), tube up to z 51.8, hex pocket that locks the M8 x 75
    bolt head (insert the bolt from below before screwing the post down)."""
    post = cq.Workplane("XY").circle(27).extrude(6)                    # r 27: clears the table motor (r > 28.4)
    post = post.faces(">Z").workplane().polarArray(22.2, 45, 360, 4).cskHole(WOOD, 8.6, 90)
    post = post.union(cq.Workplane("XY").circle(14).extrude(TABLE_Z["post_top"]))
    post = post.cut(cq.Workplane("XY").polygon(6, M8_NUT / math.cos(math.radians(30))).extrude(TABLE_Z["head_top"]))   # open below
    return post.cut(cq.Workplane("XY").circle(M8 / 2).extrude(TABLE_Z["post_top"]))


def table_drum():
    """The turning table: 100T GT2 teeth at the bottom, two 608 outer-race seats, nut recess at the top (open:
    tighten with a 13 mm spanner before the yoke goes on), OG-40 top (M4 x 16 self-tap) for the yoke, 2 flag holes."""
    pd = 100 * GT2_PITCH / math.pi
    od = pd - 0.508
    z0 = TABLE_Z["drum"]
    teeth = cq.Workplane("XY").circle(od / 2).extrude(7)
    teeth = teeth.cut(cq.Workplane("XY").polarArray(od / 2 + 0.15, 0, 360, 100).circle(0.6).extrude(7))
    fl = cq.Workplane("XY").circle(od / 2 + 2).extrude(1.2)
    d = fl.union(teeth.translate((0, 0, 1.2))).union(fl.translate((0, 0, 8.2)))
    d = d.union(cq.Workplane("XY").circle(34).extrude(TABLE_Z["hub_top"] - z0 - 9.4).translate((0, 0, 9.4)))
    h = TABLE_Z["hub_top"] - z0
    for zz in (TABLE_Z["b1"], TABLE_Z["b2"]):
        d = d.cut(cq.Workplane("XY").circle(BEARING_608[0] / 2).extrude(STACK["bearing"]).translate((0, 0, zz - z0)))
    d = d.cut(cq.Workplane("XY").circle(7.0).extrude(h))                                    # inner races / spacer clear
    d = d.cut(cq.Workplane("XY").circle(10).extrude(h - (TABLE_Z["nut"] - z0)).translate((0, 0, TABLE_Z["nut"] - z0)))   # nut + spanner
    d = d.faces(">Z").workplane().rect(OG40, OG40, forConstruction=True).vertices().hole(3.5, 12)   # M4 x 16 self-tap from the yoke
    return d.cut(cq.Workplane("XY").pushPoints([(30, -4.5), (30, 4.5)]).circle(M3_TAP / 2).extrude(8).translate((0, 0, h - 8)))


def table_motor_bracket():
    """Holds the table motor shaft-up on the plywood inside the lazy Susan opening (motor centre 49.4 mm from the
    axis for a 232 mm belt): two side rails with radial slots (#8 wood screws: slide to tension the belt), a top
    plate that screws to the motor face (4 x M3 x 8)."""
    gap = 42.6
    rails = cq.Workplane("XY")
    for s in (-1, 1):
        r = cq.Workplane("XY").box(46, 8, MOTOR_BODY, centered=(True, False, False)).translate((0, s * gap / 2 - (8 if s < 0 else 0), 0))
        foot = cq.Workplane("XY").box(36, 10, 6, centered=(True, False, False)).translate((0, s * (gap / 2 + 8) - (10 if s < 0 else 0), 0))
        foot = foot.cut(cq.Workplane("XY").slot2D(24, WOOD, 0).extrude(6).translate((0, s * (gap / 2 + 13), 0)))   # stays inside r 80
        rails = rails.union(r).union(foot)
    top = cq.Workplane("XY").box(46, gap + 16, 5, centered=(True, True, False)).translate((0, 0, MOTOR_BODY))
    top = top.cut(cq.Workplane("XY").circle(NEMA17_BOSS / 2 + 0.3).extrude(5).translate((0, 0, MOTOR_BODY)))
    top = top.cut(cq.Workplane("XY").rect(NEMA17_HOLES, NEMA17_HOLES, forConstruction=True).vertices().circle(M3 / 2).extrude(5).translate((0, 0, MOTOR_BODY)))
    return rails.union(top)


YOKE_INNER = 116.0
YOKE_BASE = 6.0
YOKE_SEAT = 150.0 - TABLE_Z["hub_top"]                                  # tilt axis through the zero point
TILT_BELT_C = 75.6                                                       # 280 mm GT2 loop, 20T-100T
YOKE_TOP = YOKE_SEAT + TILT_BELT_C + 21 + 8                              # the tilt motor sits above the axis, inside the yoke


def tilt_yoke():
    """U yoke on the table hub (OG-40). 608 seats (outer face of each arm) put the tilt axis through the zero point.
    The tilt motor hangs on the inner face of the +X arm, above the axis, shaft out through the arm (slots = belt
    tension); its pulley drives the 100T on the stub axle outside the arm. Everything stays within r 70 of the table axis."""
    base = cq.Workplane("XY").box(YOKE_INNER + 24, 34, YOKE_BASE, centered=(True, True, False))
    base = og40_holes(base.faces(">Z").workplane())
    base = base.cut(cq.Workplane("XY").circle(5).extrude(YOKE_BASE))                     # bolt end of the table axle
    for s in (-1, 1):
        x0 = s * (YOKE_INNER / 2 + 6)
        arm = cq.Workplane("XY").box(12, 34, YOKE_TOP, centered=(True, True, False)).translate((x0, 0, 0))
        seat_x = s * (YOKE_INNER / 2 + 12) - (7.2 if s > 0 else 0)
        arm = arm.cut(cq.Workplane("YZ").circle(BEARING_608[0] / 2).extrude(7.2).translate((seat_x, 0, YOKE_SEAT)))
        arm = arm.cut(cq.Workplane("YZ").circle(6.5).extrude(14).translate((x0 - 7, 0, YOKE_SEAT)))
        if s > 0:
            mz = YOKE_SEAT + TILT_BELT_C
            arm = arm.cut(cq.Workplane("YZ").slot2D(NEMA17_BOSS + 8, NEMA17_BOSS, 90).extrude(14).translate((x0 - 7, 0, mz)))
            for dy in (-1, 1):
                for dz in (-1, 1):
                    arm = arm.cut(cq.Workplane("YZ").slot2D(3.4 + 8, 3.4, 90).extrude(14).translate((x0 - 7, dy * NEMA17_HOLES / 2, mz + dz * NEMA17_HOLES / 2)))
        base = base.union(arm)
    return base


SPIN = {"platter": 8.0, "hub": 10.0, "motor_face": -24.0, "motor_body": 21.5}   # 17HS08-1004S pancake, 20 mm shaft


def tilt_cradle():
    """Turns about the tilt axis (local z = 0 = sample face = zero point). End blocks trap the M8 nuts of the two
    M8 x 35 stub axles; the floor holds the pancake spin motor face-up (4 x M3 x 8). Printed upside down."""
    w = YOKE_INNER - 4
    depth = 34.0
    zb = SPIN["motor_face"]
    floor = cq.Workplane("XY").box(w, depth, 5, centered=(True, True, False)).translate((0, 0, zb))
    floor = floor.cut(cq.Workplane("XY").circle(NEMA17_BOSS / 2 + 0.3).extrude(5).translate((0, 0, zb)))
    floor = floor.cut(cq.Workplane("XY").rect(NEMA17_HOLES, NEMA17_HOLES, forConstruction=True).vertices().circle(M3 / 2).extrude(5).translate((0, 0, zb)))
    c = floor
    for s in (-1, 1):
        x0 = s * (w / 2 - 6)
        blk = cq.Workplane("XY").box(12, depth, 10 - zb, centered=(True, True, False)).translate((x0, 0, zb))
        blk = blk.cut(cq.Workplane("YZ").circle(M8 / 2).extrude(12).translate((x0 - 6, 0, 0)))
        inner = x0 - s * 6                                                         # nut trapped flush with the inner face
        blk = blk.cut(cq.Workplane("YZ").polygon(6, M8_NUT / math.cos(math.radians(30))).extrude(6.6).translate((inner if s > 0 else inner - 6.6, 0, 0)))
        c = c.union(blk)
    return c.translate((0, 0, -zb))


def spin_platter():
    """Sample face (top = tilt axis = zero point), r 42 between the cradle end blocks. Hub clamps the pancake motor's
    5 mm D-shaft: M3 grub into a captive nut on the flat. M3 holes for risers (stage 11); flag holes on the rim.
    Printed upside down (top face on the bed)."""
    p = cq.Workplane("XY").circle(42).extrude(SPIN["platter"])
    p = p.union(cq.Workplane("XY").circle(8).extrude(SPIN["hub"]).translate((0, 0, -SPIN["hub"])))
    p = p.cut(cq.Workplane("XY").circle(2.6 + CLEAR / 2).extrude(SPIN["hub"] + SPIN["platter"] - 4).translate((0, 0, -SPIN["hub"])))
    g = cq.Workplane("YZ").circle(1.6).extrude(10).translate((0, 0, -SPIN["hub"] / 2))
    g = g.union(cq.Workplane("XY").box(2.7, 5.9, 7).translate((4.8, 0, -SPIN["hub"] / 2 - 2.5)))        # nut slot from below
    p = p.cut(g)
    p = p.faces(">Z").workplane().polarArray(15, 45, 360, 4).hole(M3, 5)          # risers (stage 11)
    return p.cut(cq.Workplane("XY").pushPoints([(36, -4.5), (36, 4.5)]).circle(M3_TAP / 2).extrude(5))


# ---------------- 06 camera + light ----------------
def aperture_stop():
    """f/8 for f = 16 mm: 2.0 mm hole. Disc sits in front of the M12 lens; adjust OD to your holder."""
    return cq.Workplane("XY").circle(7).circle(1.0).extrude(1.2)


CAM_PLATE, CAM_STANDOFF, CAM_BOARD, CAM_HOLDER, CAM_LENS_OUT = 4.0, 6.0, 1.6, 11.0, 7.0
CAM_LENS_Z = CAM_PLATE + CAM_STANDOFF + CAM_BOARD + CAM_HOLDER + CAM_LENS_OUT   # plate back -> lens front, 29.6
CAM_CLAMP = 24.4                                                                   # 2020 channel centre 12.2 behind the plate
CAM_POST_OFFSET = CAM_CLAMP / 2 + CAM_LENS_Z                                       # post centre -> lens front, 41.8
CAM_POST_X = 350.0 + CAM_POST_OFFSET                                               # measuring post: lens front at 350


def _camera_face():
    """Plate + 4 standoffs (6 mm: room for the board's back parts and a side-entry USB-C plug). Camera looks along +z."""
    p = cq.Workplane("XY").box(50, 50, CAM_PLATE, centered=(True, True, False))
    pts = [(sx * 17, sy * 17) for sx in (-1, 1) for sy in (-1, 1)]                                   # 34 mm square [K3]
    for x, y in pts:
        p = p.union(cq.Workplane("XY").circle(3).extrude(CAM_STANDOFF).translate((x, y, CAM_PLATE)))
    p = p.cut(cq.Workplane("XY").pushPoints(pts).circle(1.1).extrude(CAM_PLATE + CAM_STANDOFF))       # M2.5 x 8 self-tap [CAM-07]
    return p.cut(cq.Workplane("XY").circle(17 / 2).extrude(CAM_PLATE))                                # cable / back-part relief


def _post_clamp(tilt: float = 0.0, off: float = CAM_CLAMP / 2):
    """Clamp block behind the plate for a vertical 2020 post, channel centre `off` mm behind the plate back.
    tilt > 0: the camera looks `tilt` deg down while the channel stays vertical (block rotated about the plate's
    x axis, then trimmed at the plate back)."""
    blk = cq.Workplane("XY").box(30, 40, off + 12.2 + 20, centered=(True, True, False)).translate((0, 0, -off - 12.2))
    ch = cq.Workplane("XZ").rect(20.4, 20.4).extrude(40, both=True).translate((0, 0, -off))
    m5 = cq.Workplane("YZ").circle(M5 / 2).extrude(30, both=True).translate((0, 0, -off))
    rot = lambda w: w.rotate((0, 0, 0), (1, 0, 0), -tilt)
    blk = rot(blk).intersect(cq.Workplane("XY").box(30, 80, 80, centered=(True, True, False)).translate((0, 0, -80)))
    return blk.cut(rot(ch)).cut(rot(m5))


def camera_plate():
    """Arducam B0433 38 x 38 mm board on 4 x M2.5 x 8 self-tap into 6 mm standoffs. Clamp block behind grips a vertical
    2020 post (M5 x 10 into a T-nut): the camera looks along +z, the post centre is CAM_POST_OFFSET = 41.8 mm behind
    the lens front (measuring post at x = 391.8 for a 350 mm working distance)."""
    return _camera_face().union(_post_clamp())


HS_H, PAD_T, COB_H = 11.0, 0.25, 1.4          # LSR-03 heatsink, LSR-04 3M 8810 tape, LSR-01 Citizen CLU7A3 [L22]
HOLDER_D, HOLDER_H, PRELOAD = 35.0, 3.6, 0.3  # LSR-06 TE Z35 2213678-5 [L23]; the stack stands 0.3 mm proud so the cap clamps it
LAMP_POCKET = HS_H + HOLDER_H - PRELOAD       # lamp back face -> pocket front wall (the holder face bears on it)
LAMP_COB_Z = HS_H - PRELOAD + PAD_T + COB_H   # lamp back face -> COB emitter: 300 mm from the zero point
LAMP_EXIT_Z = 74.0                            # lamp back face -> exit aperture


def lamp_tube():
    """Lamp: rear square pocket for the 40 x 40 heatsink, a round seat in front of it that centres the TE Z35 COB holder [L23],
    a 50 mm tube with a 10 mm exit aperture and a 1 mm polarizer slot, and a 2020 clamp on top (M5 into a T-nut),
    offset sideways by LAMP_ARM_X (the arm runs 14 mm beside the beam line) so the beam axis passes through the zero point.
    The cap (LSR-05b) presses heatsink + holder forward with 4 x M3 x 8 self-tap: the heatsink stops 0.5 mm short of the
    seat's ledge, so all the clamp force goes through the holder onto the COB. A groove in the -y wall takes the two leads."""
    S = 48.0
    body = cq.Workplane("XY").box(S, S, 22, centered=(True, True, False))
    body = body.cut(cq.Workplane("XY").rect(40.6, 40.6).extrude(HS_H - PRELOAD + 0.5))      # heatsink pocket
    body = body.cut(cq.Workplane("XY").circle(HOLDER_D / 2 + 0.2).extrude(LAMP_POCKET))     # holder seat (centres the COB)
    body = body.cut(cq.Workplane("XY").rect(6, 5.8).extrude(LAMP_POCKET).translate((0, -19.9, 0)))   # lead groove to the cap slot
    body = body.cut(cq.Workplane("XY").circle(12).extrude(22))                              # light through
    body = body.faces("<Z").workplane().pushPoints([(sx * 22, sy * 22) for sx in (-1, 1) for sy in (-1, 1)]).hole(M3_TAP, 10)
    tube = cq.Workplane("XY").circle(16).circle(13).extrude(50).translate((0, 0, 22))
    tube = tube.union(cq.Workplane("XY").circle(16).circle(5).extrude(2).translate((0, 0, 72)))
    tube = tube.cut(cq.Workplane("XY").box(40, 34, 1.2, centered=(False, True, False)).translate((-5, 0, 64)))
    clamp = cq.Workplane("XY").box(30, 24, 22, centered=(True, False, False)).translate((LAMP_ARM_X, S / 2, 0))
    clamp = clamp.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(22).translate((LAMP_ARM_X, S / 2 + 12, 0)))
    clamp = clamp.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(-30).translate((LAMP_ARM_X, S / 2 + 10, 11)))
    return body.union(tube).union(clamp)


def lamp_cap():
    """Back cap: 4 x M3 x 8 into the lamp body; slot over the body's lead groove; vents."""
    c = cq.Workplane("XY").box(48, 48, 3, centered=(True, True, False))
    c = c.faces(">Z").workplane().pushPoints([(sx * 22, sy * 22) for sx in (-1, 1) for sy in (-1, 1)]).hole(M3)
    c = c.cut(cq.Workplane("XY").rect(8, 2.8).extrude(3).translate((0, -21.5, 0)))
    for k in range(4):
        c = c.cut(cq.Workplane("XY").rect(24, 2.5).extrude(3).translate((0, -6 + 5 * k, 0)))
    return c


# ---------------- 07 calibrate ----------------
PTFE_SQ, PTFE_STACK = 50.0 + 1.0, 3 * 3.0       # 50 mm squares knife-cut from a 100 x 100 x 3 mm sheet (CAL-01), 3 stacked


def ptfe_holder():
    """White tile: 3 x 3 mm PTFE squares (9 mm: opaque like a 3/8 in plate), top face flush with the rim.
    Corner reliefs take knife-cut corners; finger notch to lift the stack out."""
    h = cq.Workplane("XY").box(60, 60, 2.4 + PTFE_STACK, centered=(True, True, False))
    h = h.cut(cq.Workplane("XY").rect(PTFE_SQ, PTFE_SQ).extrude(PTFE_STACK).translate((0, 0, 2.4)))
    for sx in (-1, 1):
        for sy in (-1, 1):
            h = h.cut(cq.Workplane("XY").circle(1.5).extrude(PTFE_STACK).translate((sx * PTFE_SQ / 2, sy * PTFE_SQ / 2, 2.4)))
    return h.cut(cq.Workplane("XY").circle(8).extrude(PTFE_STACK).translate((0, 28.5, 2.4)))       # finger notch


def mirror_holder():
    h = cq.Workplane("XY").box(60, 60, 8, centered=(True, True, False))
    return h.cut(cq.Workplane("XY").rect(50.5, 50.5).extrude(5).translate((0, 0, 3)))


def ball_holder():
    """Two 1 in chrome balls 40 mm apart on conical seats [E6]."""
    b = cq.Workplane("XY").box(66, 28, 14, centered=(True, True, False))
    for x in (-20, 20):                                       # 90 deg cone, 22 mm at the top: the ball sits on a ring
        b = b.cut(cq.Workplane("XY").add(cq.Solid.makeCone(2.0, 11.0, 9.0, cq.Vector(x, 0, 5))))   # 2 mm below the top
    return b


def dowel_socket():
    s = cq.Workplane("XY").circle(10).extrude(40).union(cq.Workplane("XY").box(50, 24, 5, centered=(True, True, False)))   # 3.5 mm wall
    s = s.cut(cq.Workplane("XY").circle(6.45).extrude(36).translate((0, 0, 5)))                    # 1/2 in dowel [E3]
    return s.faces("<Z").workplane().pushPoints([(-19, 0), (19, 0)]).hole(M4)


# ---------------- 10 colour ----------------
def led_ring():
    """8 star LEDs on r = 24 mm; mounts at the top of the 40 deg mast."""
    r = cq.Workplane("XY").circle(40).circle(10).extrude(4)
    r = r.faces(">Z").workplane().polarArray(24, 0, 360, 8).hole(M3)
    return r.union(cq.Workplane("XY").box(16, 60, 4, centered=(True, False, False)).translate((0, -95, 0)))


def led_mast():
    """Bolts to the light arm; tilts the LED ring 40 deg up so photometric-stereo lights are non-coplanar."""
    plate = cq.Workplane("XY").box(30, 30, 5, centered=(True, True, False)).faces(">Z").workplane().rect(20, 20, forConstruction=True).vertices().hole(M5)
    arm = cq.Workplane("XY").box(16, 6, 160, centered=(True, True, False)).rotate((0, 0, 0), (1, 0, 0), -50).translate((0, 0, 5))
    return plate.union(arm)


def spectral_tube():
    """AS7341 breakout (25.4 x 17.8 mm, check holes) behind a 40 mm tube with a 3 mm aperture: ~4 deg field,
    ~25 mm spot at 350 mm. Clamps to the camera pillar (FRM-09h) above the camera plate (M5 into its z 181 pilot)."""
    base = cq.Workplane("XY").box(30, 24, 3, centered=(True, True, False))
    base = base.faces(">Z").workplane().pushPoints([(-10.15, 0), (10.15, 0)]).hole(M2_5)
    tube = cq.Workplane("XZ").circle(7).circle(5).extrude(-40).translate((0, 12, 10))
    cap = cq.Workplane("XZ").circle(7).circle(1.5).extrude(-1.5).translate((0, 52, 10))
    wall = cq.Workplane("XY").box(30, 3, 20, centered=(True, False, False)).translate((0, 9, 0))
    wall = wall.cut(cq.Workplane("XZ").circle(5).extrude(-5).translate((0, 8, 10)))
    clamp = cq.Workplane("XY").box(30, 26, 22, centered=(True, False, False)).translate((0, -38, 0))
    clamp = clamp.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(22).translate((0, -25, 0)))
    clamp = clamp.cut(cq.Workplane("XZ").circle(M5 / 2).extrude(-40).translate((0, -45, 11)))
    return base.union(tube).union(cap).union(wall).union(clamp.translate((0, -0.0, 0)))


# ---------------- 11 scan ----------------
def riser(h: float):
    """Hollow riser: 3 mm tube, 6 mm top, 4 screw bosses (less ABS, same stiffness where it matters)."""
    r = cq.Workplane("XY").circle(25).extrude(h)
    if h > 10:
        r = r.cut(cq.Workplane("XY").circle(22).extrude(h - 6))
        r = r.union(cq.Workplane("XY").polarArray(15, 45, 360, 4).circle(5).extrude(h - 6))
    r = r.cut(cq.Workplane("XY").circle(20).extrude(2).translate((0, 0, h - 2)))                   # object nest
    return r.faces("<Z").workplane().polarArray(15, 45, 360, 4).cboreHole(M3, 6, max(h - 6, 1))


SCAN_TILT = 15.0                  # scan camera looks 15 deg down (machine.yaml scan.camera_elevation_deg)


SCAN_CLAMP_OFF = 18.0             # the tilted plate's lower edge swings 6.5 mm back: post 18 mm behind the plate centre


def _scan_post():
    """Scan camera: lens front 650 mm from the zero point, looking SCAN_TILT down; the clamp channel is vertical and
    SCAN_CLAMP_OFF behind the plate-back centre, horizontally. Returns (post x, lens-front z)."""
    e = math.radians(SCAN_TILT)
    lx, lz = 650 * math.cos(e), 150 + 650 * math.sin(e)
    back_x = lx + CAM_LENS_Z * math.cos(e)                 # plate back centre, CAM_LENS_Z behind the lens front
    return back_x + SCAN_CLAMP_OFF, lz


SCAN_POST_X, SCAN_LENS_Z = _scan_post()
END_FOOT_X = round(SCAN_POST_X - 20 - 20 - 6)       # just inside the scan post socket (the post overhangs it by ~45 mm)


def scan_camera_plate():
    """Second camera plate: the plate looks 15 deg down while its clamp stays vertical on the scan post (replaces the
    old wedge; same M2.5 x 8 screws, 6 mm standoffs). Lens front 650 mm from the zero point, centre 168 mm above it."""
    return _camera_face().union(_post_clamp(SCAN_TILT, SCAN_CLAMP_OFF))


# ---------------- 15 standalone ----------------
def pi_mount():
    """Pi Zero 2 W, 58 x 23 mm hole pattern [H51]: push-fit pegs through its 2.75 mm holes (no screws)."""
    p = cq.Workplane("XY").box(75, 40, 3, centered=(True, True, False))
    for x in (-29, 29):
        for y in (-11.5, 11.5):
            p = p.union(cq.Workplane("XY").circle(3).extrude(8).translate((x, y, 0)))
            p = p.union(cq.Workplane("XY").circle(1.25).extrude(2.6).translate((x, y, 8)))
    return p


# ---------------- registry ----------------
PARTS = {   # id: (stage folder, file stem, function, what)
    "PLAN-01": ("00-plan", "tolerance_coupon", tolerance_coupon, "Fit test: M3 self-tap holes + 608 pockets"),
    "PWR-18a": ("01-power", "power_box", power_box, "Power box"),
    "PWR-18b": ("01-power", "power_lid", power_lid, "Power box lid (e-stop)"),
    "CTL-10a": ("02-controller", "button_panel", button_panel, "Keypad panel + OLED window"),
    "CTL-10b": ("02-controller", "controller_tray", controller_tray, "Controller tray (E4 + Pico + breadboard)"),
    "FRM-09a": ("03-frame", "og40_adapter", og40_adapter, "OG-40 adapter plate"),
    "FRM-09b": ("03-frame", "foot", foot, "Corner foot, screws on (print 4)"),
    "FRM-09c": ("03-frame", "protractor_segment", protractor_segment, "Ring scale, 80 deg (print 4: 20-340 deg)"),
    "FRM-09d": ("03-frame", "extrusion_saddle", extrusion_saddle, "2020 saddle, screws on (print 2)"),
    "FRM-09e": ("03-frame", "post_socket", post_socket, "Scan-post socket on the outrigger"),
    "FRM-09h": ("03-frame", "camera_pillar", camera_pillar, "Measuring-camera pillar on the outrigger"),
    "FRM-09f": ("03-frame", "end_foot", end_foot, "Outrigger end foot"),
    "FRM-09g": ("03-frame", "washers", washers, "4 mm screw washers for the lazy Susan (8)"),
    "LAR-08a": ("04-light-arm", "rim_segment", rim_segment, "Belt rim segment (print 7)"),
    "LAR-08b": ("04-light-arm", "ring_motor_mount", ring_motor_mount, "M4 motor mount at 0 deg, pinion meshes the rim"),
    "LAR-08c": ("04-light-arm", "arm_segment", arm_segment, "Arm segment: rim segment + 2020 upright socket"),
    "LAR-08e": ("04-light-arm", "cross_clamp", cross_clamp, "2020 cross clamp: upright to horizontal arm"),
    "TBL-07a": ("05-table", "table_drum", table_drum, "Table drum: 100T teeth, 608 seats, OG-40 top"),
    "TBL-07b": ("05-table", "home_flag", home_flag, "Home flag (print 3: table, tilt, spin)"),
    "TBL-07c": ("05-table", "table_motor_bracket", table_motor_bracket, "Table motor bracket (shaft up, slotted)"),
    "TBL-07d": ("05-table", "table_post", table_post, "Table post: fixed M8 x 75 axle (hex-locked head)"),
    "TBL-07f": ("05-table", "spacers", spacers, "Spacers + shims, table and tilt (one print)"),
    "CAM-03a": ("06-camera-light", "aperture_stop_f8", aperture_stop, "f/8 aperture stop"),
    "CAM-03b": ("06-camera-light", "camera_plate", camera_plate, "Camera plate + post clamp"),
    "LSR-05a": ("06-camera-light", "lamp_tube", lamp_tube, "Lamp body + tube, 2020 clamp, polarizer slot"),
    "LSR-05b": ("06-camera-light", "lamp_cap", lamp_cap, "Lamp back cap"),
    "CAL-06a": ("07-calibrate", "ptfe_holder", ptfe_holder, "PTFE holder"),
    "CAL-06b": ("07-calibrate", "mirror_holder", mirror_holder, "Mirror holder"),
    "CAL-06c": ("07-calibrate", "ball_holder", ball_holder, "Chrome-ball holder"),
    "ENC-04a": ("07-calibrate", "dowel_socket", dowel_socket, "Dowel socket (print 4)"),
    "TLT-07a": ("08-tilt", "tilt_yoke", tilt_yoke, "Tilt yoke: 608 seats, motor slots above the axis"),
    "TLT-07b": ("08-tilt", "pulley_100T", lambda: gt2_pulley(100), "GT2 100T pulley (5:1) on the stub axle"),
    "TLT-07c": ("08-tilt", "tilt_cradle", tilt_cradle, "Tilt cradle: stub-axle nut traps, spin motor floor"),
    "SPN-07a": ("09-spin", "spin_platter", spin_platter, "Spin platter: clamps the motor D-shaft (direct drive)"),
    "MSK-06a": ("10-color", "led_ring", led_ring, "LED ring (8 bands)"),
    "MSK-06b": ("10-color", "led_mast", led_mast, "40 deg LED mast"),
    "SPC-03a": ("10-color", "spectral_tube", spectral_tube, "Spectral sensor tube + post clamp"),
    "SCN-03a": ("11-scan-capture", "riser_20", lambda: riser(20), "Riser 20 mm"),
    "SCN-03b": ("11-scan-capture", "riser_40", lambda: riser(40), "Riser 40 mm"),
    "SCN-03c": ("11-scan-capture", "riser_60", lambda: riser(60), "Riser 60 mm"),
    "SCN-03d": ("11-scan-capture", "scan_camera_plate_15", scan_camera_plate, "Scan camera plate, looks 15 deg down"),
    "STA-07a": ("15-standalone", "pi_zero_mount", pi_mount, "Pi Zero 2 W mount"),
}


def build(only: str | None = None) -> list[Path]:
    out = []
    for pid, (stage, stem, fn, _) in PARTS.items():
        if only and pid != only:
            continue
        d = ROOT / "phases" / stage / "3d"
        d.mkdir(parents=True, exist_ok=True)
        shape = fn()
        for ext in ("step", "stl"):
            path = d / f"{pid}_{stem}.{ext}"
            if ext == "stl":
                cq.exporters.export(shape, str(path), tolerance=0.05, angularTolerance=0.2)
            else:
                cq.exporters.export(shape, str(path))
                stepio.stabilise(path)
            out.append(path)
        bb = shape.val().BoundingBox()
        print(f"{pid:8} {stage:16} {stem:22} {bb.xlen:6.1f} x {bb.ylen:6.1f} x {bb.zlen:5.1f} mm")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--only")
    a = ap.parse_args()
    build(a.only)
    sys.exit(0)
