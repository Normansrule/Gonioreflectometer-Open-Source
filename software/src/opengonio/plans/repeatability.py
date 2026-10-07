"""Repeatability: return to a pose N times and measure the scatter.

Measured with the fixed camera, as the deviation study in Fig. 12 of [R1]:
  M3: pose of a ChArUco board on the stage (OpenCV solvePnP) -> yaw angle
  M4: position of the lamp's reflection in the mirror on the stage (pixels -> degrees)
This module holds the statistics; capture helpers live in opengonio.camera.
"""
from __future__ import annotations

import math
import statistics


def summarize(readings_deg: list[float], target_deg: float) -> dict:
    mean = statistics.fmean(readings_deg)
    worst = max(abs(r - mean) for r in readings_deg)
    sd = statistics.pstdev(readings_deg) if len(readings_deg) > 1 else 0.0
    return {"n": len(readings_deg), "mean_deg": round(mean, 4), "max_dev_deg": round(worst, 4),
            "two_sigma_deg": round(2 * sd, 4), "target_deg": target_deg, "pass": worst <= target_deg}


def reflection_shift_to_deg(shift_px: float, pixel_um: float, focal_mm: float,
                            path_mm: float, light_distance_mm: float) -> float:
    """Light-angle change from the shift of the lamp's reflection in a fixed mirror.

    Rotating the light by d about the zero point moves its mirror image sideways by
    light_distance * d. The camera sees that virtual source path_mm away (camera-mirror +
    mirror-lamp) with magnification f / path_mm.
    """
    lateral_mm = (shift_px * pixel_um / 1000.0) * path_mm / focal_mm
    return math.degrees(lateral_mm / light_distance_mm)


def laser_angle_deg(spot_shift_mm: float, wall_distance_mm: float) -> float:
    """Laser on the base, mirror on the moving part, spot on a wall: the reflected beam turns 2x the mirror."""
    return math.degrees(math.atan2(spot_shift_mm, wall_distance_mm)) / 2.0


def laser_limit_mm(target_deg: float, wall_distance_mm: float) -> float:
    """Largest allowed spot shift on the wall for a given repeatability target."""
    return math.tan(math.radians(2 * target_deg)) * wall_distance_mm
