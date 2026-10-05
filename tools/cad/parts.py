#!/usr/bin/env python3
"""Starter geometry for every printed part (CadQuery). Writes STEP + STL into phases/NN/3d/print/.

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

ROOT = Path(__file__).resolve().parents[2]

# ---------------- PARAMETERS (mm) ----------------
CLEAR = 0.2                       # print clearance; set from the tolerance coupon (M03)
INSERT = 4.0                      # M3 heat-set insert hole [F6]
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
    """Insert holes 3.8-4.2 and 608 pockets 22.0-22.4: pick what fits, set CLEAR / INSERT."""
    p = cq.Workplane("XY").box(100, 60, 8, centered=(False, False, False))
    for i, d in enumerate((3.8, 3.9, 4.0, 4.1, 4.2)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(8).translate((12 + 19 * i, 10, 0)))
        p = p.cut(cq.Workplane("XY").box(1, 2 + i, 1, centered=(True, False, False)).translate((12 + 19 * i, 15, 7)))
    for i, d in enumerate((22.0, 22.2, 22.4)):
        p = p.cut(cq.Workplane("XY").circle(d / 2).extrude(7.1).translate((18 + 32 * i, 40, 0.9)))
    return p


# ---------------- 01 power ----------------
def power_box():
    L, W, H, t = 120.0, 80.0, 50.0, 3.2
    b = cq.Workplane("XY").box(L, W, H, centered=(True, True, False)).faces(">Z").shell(-t)
    for sx in (-1, 1):
        for sy in (-1, 1):
            post = cq.Workplane("XY").circle(4.5).extrude(H - 3).translate((sx * (L / 2 - t - 4), sy * (W / 2 - t - 4), 0))
            post = post.cut(cq.Workplane("XY").circle(INSERT / 2).extrude(8).translate((sx * (L / 2 - t - 4), sy * (W / 2 - t - 4), H - 11)))
            b = b.union(post)
    def side(w, h, y, z):                                                                               # +X wall
        return cq.Workplane("YZ").rect(w, h).extrude(20).translate((L / 2 - 10, y, z))
    b = b.cut(cq.Workplane("YZ").circle(4.05).extrude(20).translate((L / 2 - 10, -22, 25)))           # DC jack [P4]
    b = b.cut(side(12.9, 19.2, 0, 25))                                                                   # rocker [P13]
    b = b.cut(cq.Workplane("YZ").rect(12, 6.5).extrude(20).translate((-L / 2 - 10, -18, 15)))           # XT30 out (-X)
    b = b.cut(cq.Workplane("YZ").rect(10, 6).extrude(20).translate((-L / 2 - 10, 2, 15)))               # J3
    b = b.cut(cq.Workplane("YZ").rect(10, 6).extrude(20).translate((-L / 2 - 10, 18, 15)))              # J4
    for k in range(6):                                                                                   # vents (-Y)
        b = b.cut(cq.Workplane("XZ").rect(3, 20).extrude(-20).translate((-30 + 12 * k, -W / 2 + 10, 28)))
    h = OG40 / 2
    for x, y in ((h, h), (-h, h), (h, -h), (-h, -h)):
        b = b.cut(cq.Workplane("XY").circle(M4 / 2).extrude(t).translate((x, y, 0)))
    return b


def power_lid():
    L, W, t = 120.0, 80.0, 3.2
    lid = cq.Workplane("XY").box(L, W, t, centered=(True, True, False))
    lid = lid.faces(">Z").workplane().hole(22.3)                                                          # e-stop [P16]
    pts = [(sx * (L / 2 - t - 4), sy * (W / 2 - t - 4)) for sx in (-1, 1) for sy in (-1, 1)]
    return lid.faces(">Z").workplane().pushPoints(pts).cboreHole(M3, 6, 1.8)


# ---------------- 02 controller ----------------
def button_panel():
    """6 x 12 mm buttons + OLED window; fits the front of the controller case."""
    p = cq.Workplane("XY").box(160, 60, 3, centered=(True, True, False))
    p = p.faces(">Z").workplane().pushPoints([(-65 + 20 * i, -10) for i in range(6)]).hole(12.2)
    p = p.cut(cq.Workplane("XY").rect(26, 15).extrude(3).translate((55, 12, 0)))                       # OLED [H52]
    p = p.faces(">Z").workplane().pushPoints([(75, -25), (-75, -25), (75, 25), (-75, 25)]).hole(M3)
    return p


def controller_tray():
    """Base for E4 + Pico. E4 hole positions: verify on the FYSETC drawing [C1] before printing."""
    t = cq.Workplane("XY").box(170, 110, 3, centered=(True, True, False))
    e4 = [(-35 + x, y) for x in (-41, 41) for y in (-29.5, 29.5)]                                      # ~90 x 67 board, 4 mm inset
    pico = [(55 + x, y) for x in (-23.5, 23.5) for y in (-5.7, 5.7)]                                  # 47 x 11.4 [C6]
    for x, y in e4:
        t = t.union(cq.Workplane("XY").circle(3.5).extrude(9).translate((x, y, 0)))
        t = t.cut(cq.Workplane("XY").circle(INSERT / 2).extrude(9).translate((x, y, 3)))
    for x, y in pico:
        t = t.union(cq.Workplane("XY").circle(2.5).extrude(7).translate((x, y, 0)))
        t = t.cut(cq.Workplane("XY").circle(1.0).extrude(7).translate((x, y, 3)))
    h = OG40 / 2
    for x, y in ((h, h), (-h, h), (h, -h), (-h, -h)):
        t = t.cut(cq.Workplane("XY").circle(M4 / 2).extrude(3).translate((x, y - 30, 0)))
    return t


# ---------------- 03 frame ----------------
def og40_adapter():
    p = cq.Workplane("XY").box(56, 56, 6, centered=(True, True, False))
    p = og40_holes(p.faces(">Z").workplane())
    return p


def foot():
    """Cup for an M8 x 40 bolt head (13 mm hex) under each corner tee nut."""
    f = cq.Workplane("XY").circle(16).extrude(12)
    f = f.cut(cq.Workplane("XY").polygon(6, 13 / math.cos(math.radians(30)) + CLEAR).extrude(6).translate((0, 0, 6)))
    return f.cut(cq.Workplane("XY").circle(M8 / 2).extrude(12))


def protractor_segment():
    """90 deg scale segment for the ring (print 4); ticks every 5 deg, long ticks every 15 deg."""
    r0, r1 = 160.0, 175.0
    seg = cq.Workplane("XY").circle(r1).circle(r0).extrude(2.5)
    seg = seg.intersect(cq.Workplane("XY").polyline([(0, 0), (200, 0), (200, 200), (0, 200)]).close().extrude(3))
    for a in range(0, 91, 5):
        ln = 9 if a % 15 == 0 else 5
        tick = cq.Workplane("XY").rect(ln, 0.8).extrude(1).translate((r1 - ln / 2, 0, 1.6)).rotate((0, 0, 0), (0, 0, 1), a)
        seg = seg.cut(tick)
    return seg


# ---------------- 04 light arm ----------------
RIM_TEETH = 480                               # 24:1 with a 20T pulley; set gear_ratio from the real rim
RIM_R = RIM_TEETH * GT2_PITCH / (2 * math.pi)


def rim_segment():
    """1/8 of the belt rim: belt glued teeth-out in the groove. Print 8."""
    seg = cq.Workplane("XY").circle(RIM_R + 1.0).circle(RIM_R - 10).extrude(9)
    seg = seg.cut(cq.Workplane("XY").circle(RIM_R + 2).circle(RIM_R - 0.75).extrude(6.6).translate((0, 0, 1.2)))
    wedge = cq.Workplane("XY").polyline([(0, 0), (300, 0), (300 * math.cos(math.radians(45)), 300 * math.sin(math.radians(45)))]).close().extrude(10)
    seg = seg.intersect(wedge)
    for a in (11.25, 33.75):
        x, y = (RIM_R - 5) * math.cos(math.radians(a)), (RIM_R - 5) * math.sin(math.radians(a))
        seg = seg.cut(cq.Workplane("XY").circle(2.1).extrude(9).translate((x, y, 0)))        # wood screws
    return seg


def nema17_mount():
    """Slotted plate (belt tension) + OG-40 base."""
    m = cq.Workplane("XY").box(56, 56, 5, centered=(True, True, False))
    m = m.cut(cq.Workplane("XY").slot2D(NEMA17_BOSS + 6, NEMA17_BOSS, 0).extrude(5))
    for x in (-1, 1):
        for y in (-1, 1):
            m = m.cut(cq.Workplane("XY").slot2D(3.4 + 6, 3.4, 0).extrude(5).translate((x * NEMA17_HOLES / 2, y * NEMA17_HOLES / 2, 0)))
    wall = cq.Workplane("XY").box(56, 5, 50, centered=(True, False, False)).translate((0, 28, 0))
    return m.union(wall)


def arm_bracket():
    """Bolts to the lazy-Susan top plate; holds the 2020 light-arm upright."""
    b = cq.Workplane("XY").box(60, 40, 6, centered=(True, True, False))
    b = b.faces(">Z").workplane().pushPoints([(-22, -12), (22, -12), (-22, 12), (22, 12)]).hole(M4)
    sock = cq.Workplane("XY").box(30, 30, 30, centered=(True, True, False)).translate((0, 0, 6))
    sock = sock.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(26).translate((0, 0, 10)))
    sock = sock.cut(cq.Workplane("YZ").circle(M5 / 2).extrude(40).translate((-20, 0, 24)))
    return b.union(sock)


# ---------------- 05/08/09 axes ----------------
def gt2_pulley(teeth: int, bore: float = 8.0 + CLEAR):
    """Printed GT2 pulley (simplified round-tooth profile). 100T = M3 table/M2 tilt (5:1), 80T = M1 spin (4:1)."""
    pd = teeth * GT2_PITCH / math.pi
    od = pd - 0.508
    body = cq.Workplane("XY").circle(od / 2).extrude(7)
    body = body.cut(cq.Workplane("XY").polarArray(od / 2 + 0.15, 0, 360, teeth).circle(0.6).extrude(7))
    fl = cq.Workplane("XY").circle(od / 2 + 2).extrude(1.2)
    p = fl.union(body.translate((0, 0, 1.2))).union(fl.translate((0, 0, 8.2)))
    hub = cq.Workplane("XY").circle(9).extrude(8).translate((0, 0, 9.4))
    p = p.union(hub).cut(cq.Workplane("XY").circle(bore / 2).extrude(30))
    p = p.cut(cq.Workplane("YZ").circle(1.6).extrude(20).translate((0, 0, 13.4)))      # M3 grub (tap or insert)
    return p


def home_flag():
    """Clamps on an 8 mm shaft; 1.5 mm blade passes through the TCST2103 5.8 mm slot."""
    r = cq.Workplane("XY").circle(8).circle(4.1).extrude(8)
    blade = cq.Workplane("XY").box(26, 1.5, 8, centered=(False, True, False)).translate((6, 0, 0))
    r = r.union(blade)
    return r.cut(cq.Workplane("XZ").circle(1.6).extrude(-20).translate((0, 0, 4)))


def tilt_yoke():
    """U yoke on the table flange; two 608 seats put the tilt axis 70 mm above the base, through the zero point."""
    inner = 116.0
    base = cq.Workplane("XY").box(inner + 24, 34, 8, centered=(True, True, False))
    base = og40_holes(base.faces(">Z").workplane())
    for s in (-1, 1):
        arm = cq.Workplane("XY").box(12, 34, 78, centered=(True, True, False)).translate((s * (inner / 2 + 6), 0, 0))
        arm = arm.cut(cq.Workplane("YZ").circle(BEARING_608[0] / 2).extrude(7.2).translate((s * inner / 2 + (0 if s > 0 else -7.2), 0, 70)))
        arm = arm.cut(cq.Workplane("YZ").circle(5).extrude(14).translate((s * inner / 2 - 1 if s > 0 else -inner / 2 - 13, 0, 70)))
        base = base.union(arm)
    return base


def spin_platter():
    p = cq.Workplane("XY").circle(50).extrude(5)
    p = p.union(cq.Workplane("XY").circle(11).extrude(14).translate((0, 0, -9)))
    p = p.cut(cq.Workplane("XY").circle(4.1).extrude(30).translate((0, 0, -10)))
    p = p.faces(">Z").workplane().polarArray(15, 45, 360, 4).hole(M3)            # risers (stage 11)
    return p


# ---------------- 06 camera + light ----------------
def aperture_stop():
    """f/8 for f = 16 mm: 2.0 mm hole. Disc sits in front of the M12 lens; adjust OD to your holder."""
    return cq.Workplane("XY").circle(7).circle(1.0).extrude(1.2)


def camera_plate():
    """Arducam B0433 38 x 38 mm board, 34 mm hole square [K3]; clamps to the 2020 camera post."""
    p = cq.Workplane("XY").box(50, 50, 4, centered=(True, True, False))
    p = p.faces(">Z").workplane().rect(34, 34, forConstruction=True).vertices().hole(M2_5)
    p = p.faces(">Z").workplane().hole(17)
    clamp = cq.Workplane("XY").box(30, 24, 22, centered=(True, False, False)).translate((0, -25 - 24, 0))
    clamp = clamp.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(22).translate((0, -25 - 12, 0)))
    return p.union(clamp).cut(cq.Workplane("XZ").circle(M5 / 2).extrude(-30).translate((0, -60, 11)))


def lamp_tube():
    """Collimation tube for the 40 mm COB heatsink, 10 mm exit aperture, 1 mm polarizer slot."""
    t = cq.Workplane("XY").circle(23).circle(20.5).extrude(60)
    t = t.union(cq.Workplane("XY").circle(23).circle(5).extrude(2).translate((0, 0, 60)))
    return t.cut(cq.Workplane("XY").box(50, 46, 1.2, centered=(False, True, False)).translate((-5, 0, 54)))


# ---------------- 07 calibrate ----------------
def ptfe_holder():
    h = cq.Workplane("XY").box(70, 70, 12, centered=(True, True, False))
    h = h.cut(cq.Workplane("XY").rect(50.5, 50.5).extrude(9.6).translate((0, 0, 2.4)))           # 3/8 in PTFE [E4]
    return h.cut(cq.Workplane("XY").circle(8).extrude(12).translate((0, 33, 2.4)))                # finger notch


def mirror_holder():
    h = cq.Workplane("XY").box(70, 70, 8, centered=(True, True, False))
    return h.cut(cq.Workplane("XY").rect(50.5, 50.5).extrude(5).translate((0, 0, 3)))


def ball_holder():
    """Two 1 in chrome balls 40 mm apart on conical seats [E6]."""
    b = cq.Workplane("XY").box(80, 34, 14, centered=(True, True, False))
    for x in (-20, 20):
        b = b.cut(cq.Workplane("XY").sphere(12.7).translate((x, 0, 14 + 12.7 - 4.5)))
    return b


def dowel_socket():
    s = cq.Workplane("XY").circle(14).extrude(40).union(cq.Workplane("XY").box(50, 28, 5, centered=(True, True, False)))
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


# ---------------- 11 scan ----------------
def riser(h: float):
    r = cq.Workplane("XY").circle(25).extrude(h)
    r = r.cut(cq.Workplane("XY").circle(20).extrude(2).translate((0, 0, h - 2)))                   # object nest
    return r.faces("<Z").workplane().polarArray(15, 45, 360, 4).cboreHole(M3, 6, max(h - 6, 1))


def camera_stop():
    c = cq.Workplane("XY").box(30, 34, 28, centered=(True, True, False))
    c = c.cut(cq.Workplane("XY").rect(20.4, 20.4).extrude(28).translate((0, 0, 0)))
    return c.cut(cq.Workplane("YZ").circle(M5 / 2).extrude(40).translate((-20, 0, 14)))


# ---------------- 15 standalone ----------------
def pi_mount():
    """Pi Zero 2 W, 58 x 23 mm hole pattern, M2.5 [H51]."""
    p = cq.Workplane("XY").box(75, 40, 3, centered=(True, True, False))
    for x in (-29, 29):
        for y in (-11.5, 11.5):
            p = p.union(cq.Workplane("XY").circle(3).extrude(8).translate((x, y, 0)))
            p = p.cut(cq.Workplane("XY").circle(1.25).extrude(8).translate((x, y, 3)))
    return p


# ---------------- registry ----------------
PARTS = {   # id: (stage folder, file stem, function, what)
    "PLAN-01": ("00-plan", "tolerance_coupon", tolerance_coupon, "Fit test: insert holes + 608 pockets"),
    "PWR-18a": ("01-power", "power_box", power_box, "Power box"),
    "PWR-18b": ("01-power", "power_lid", power_lid, "Power box lid (e-stop)"),
    "CTL-10a": ("02-controller", "button_panel", button_panel, "Button panel + OLED window"),
    "CTL-10b": ("02-controller", "controller_tray", controller_tray, "Controller tray (E4 + Pico)"),
    "FRM-09a": ("03-frame", "og40_adapter", og40_adapter, "OG-40 adapter plate"),
    "FRM-09b": ("03-frame", "foot", foot, "Foot cup (print 4)"),
    "FRM-09c": ("03-frame", "protractor_segment", protractor_segment, "Ring scale, 90 deg (print 4)"),
    "LAR-08a": ("04-light-arm", "rim_segment", rim_segment, "Belt rim segment (print 8)"),
    "LAR-08b": ("04-light-arm", "nema17_mount", nema17_mount, "Motor mount, slotted"),
    "LAR-08c": ("04-light-arm", "arm_bracket", arm_bracket, "Light-arm bracket"),
    "TBL-07a": ("05-table", "pulley_100T", lambda: gt2_pulley(100), "GT2 100T pulley (5:1)"),
    "TBL-07b": ("05-table", "home_flag", home_flag, "Home flag"),
    "TBL-07c": ("05-table", "nema17_mount", nema17_mount, "Motor mount"),
    "CAM-03a": ("06-camera-light", "aperture_stop_f8", aperture_stop, "f/8 aperture stop"),
    "CAM-03b": ("06-camera-light", "camera_plate", camera_plate, "Camera plate + post clamp"),
    "LSR-05a": ("06-camera-light", "lamp_tube", lamp_tube, "Lamp tube, aperture, polarizer slot"),
    "CAL-06a": ("07-calibrate", "ptfe_holder", ptfe_holder, "PTFE holder"),
    "CAL-06b": ("07-calibrate", "mirror_holder", mirror_holder, "Mirror holder"),
    "CAL-06c": ("07-calibrate", "ball_holder", ball_holder, "Chrome-ball holder"),
    "ENC-04a": ("07-calibrate", "dowel_socket", dowel_socket, "Dowel socket (print 4)"),
    "TLT-07a": ("08-tilt", "tilt_yoke", tilt_yoke, "Tilt yoke"),
    "TLT-07b": ("08-tilt", "pulley_100T", lambda: gt2_pulley(100), "GT2 100T pulley (5:1)"),
    "SPN-07a": ("09-spin", "spin_platter", spin_platter, "Spin platter"),
    "SPN-07b": ("09-spin", "pulley_80T", lambda: gt2_pulley(80), "GT2 80T pulley (4:1)"),
    "MSK-06a": ("10-color", "led_ring", led_ring, "LED ring (8 bands)"),
    "MSK-06b": ("10-color", "led_mast", led_mast, "40 deg LED mast"),
    "SCN-03a": ("11-scan-capture", "riser_20", lambda: riser(20), "Riser 20 mm"),
    "SCN-03b": ("11-scan-capture", "riser_40", lambda: riser(40), "Riser 40 mm"),
    "SCN-03c": ("11-scan-capture", "riser_60", lambda: riser(60), "Riser 60 mm"),
    "SCN-03d": ("11-scan-capture", "camera_stop_650", camera_stop, "650 mm camera stop"),
    "STA-07a": ("15-standalone", "pi_zero_mount", pi_mount, "Pi Zero 2 W mount"),
}


def build(only: str | None = None) -> list[Path]:
    out = []
    for pid, (stage, stem, fn, _) in PARTS.items():
        if only and pid != only:
            continue
        d = ROOT / "phases" / stage / "3d" / "print"
        d.mkdir(parents=True, exist_ok=True)
        shape = fn()
        for ext in ("step", "stl"):
            path = d / f"{pid}_{stem}.{ext}"
            cq.exporters.export(shape, str(path), tolerance=0.05, angularTolerance=0.2) if ext == "stl" else cq.exporters.export(shape, str(path))
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
