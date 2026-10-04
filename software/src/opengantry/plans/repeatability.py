"""Phase 1 milestone test: home, move away, come back, read the AS5600 - N times.

Pass when the spread of encoder readings at the return pose is within the
repeatability target (0.1 deg) - reported as max |x - mean| and 2-sigma.
"""
from __future__ import annotations

import statistics

from ..gantry.config import MachineConfig
from ..gantry.encoders import AS5600, open_bus
from ..gantry.gantry import Gantry


def summarize(readings: list[float], target_deg: float) -> dict:
    mean = statistics.fmean(readings)
    dev = [r - mean for r in readings]
    two_sigma = 2 * statistics.pstdev(readings) if len(readings) > 1 else 0.0
    worst = max(abs(d) for d in dev)
    return {"n": len(readings), "mean_deg": round(mean, 4), "max_dev_deg": round(worst, 4),
            "two_sigma_deg": round(two_sigma, 4), "target_deg": target_deg,
            "pass": worst <= target_deg}


def run_repeatability(cfg: MachineConfig, g: Gantry, axis: str, cycles: int = 20,
                      test_deg: float = 45.0, away_deg: float = 20.0) -> dict:  # pragma: no cover - hardware
    enc_cfg = cfg.active_axes[axis].encoder
    enc = AS5600(open_bus(enc_cfg.bus), enc_cfg.offset_deg, enc_cfg.sign)
    if not enc.status().ok:
        raise RuntimeError(f"{axis}: AS5600 magnet not detected or out of range")
    g.home()
    readings = []
    for _ in range(cycles):
        g.move({axis: test_deg - away_deg})
        g.move({axis: test_deg})
        readings.append(enc.angle(samples=64))
    return summarize(readings, cfg.repeatability_target_deg)
