"""AS5600 magnetic encoders, one per axis, each on its own Pi I2C bus.

The AS5600 has a fixed address (0x36), so every encoder gets a separate hardware
bus enabled with a dtoverlay (see docs/03-architecture-interfaces.md).
Datasheet facts used: 12-bit angle in registers 0x0C-0x0D (RAW ANGLE),
STATUS 0x0B with MD (bit 5, magnet detected), ML (bit 4, too weak), MH (bit 3, too strong).
Absolute accuracy is about +/-1 deg INL, so the encoder is a repeatability and
step-loss check; absolute angle comes from the mirror calibration in Phase 2.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Protocol

AS5600_ADDR = 0x36
REG_STATUS = 0x0B
REG_RAW_ANGLE = 0x0C
COUNTS = 4096


class I2CBus(Protocol):
    def read_byte_data(self, addr: int, reg: int) -> int: ...
    def read_i2c_block_data(self, addr: int, reg: int, n: int) -> list[int]: ...


@dataclass(frozen=True)
class MagnetStatus:
    detected: bool
    too_weak: bool
    too_strong: bool

    @property
    def ok(self) -> bool:
        return self.detected and not self.too_weak and not self.too_strong


class AS5600:
    def __init__(self, bus: I2CBus, offset_deg: float = 0.0, sign: int = 1):
        self.bus, self.offset_deg, self.sign = bus, offset_deg, sign

    def status(self) -> MagnetStatus:
        s = self.bus.read_byte_data(AS5600_ADDR, REG_STATUS)
        return MagnetStatus(bool(s & 0x20), bool(s & 0x10), bool(s & 0x08))

    def raw(self) -> int:
        hi, lo = self.bus.read_i2c_block_data(AS5600_ADDR, REG_RAW_ANGLE, 2)
        return ((hi & 0x0F) << 8) | lo

    def angle(self, samples: int = 32) -> float:
        """Circular mean of `samples` readings, mapped through sign and offset, in (-180, 180]."""
        sx = sy = 0.0
        for _ in range(samples):
            a = 2 * math.pi * self.raw() / COUNTS
            sx += math.cos(a)
            sy += math.sin(a)
        deg = math.degrees(math.atan2(sy, sx))
        out = self.sign * deg - self.offset_deg
        return (out + 180.0) % 360.0 - 180.0


def open_bus(bus_number: int) -> I2CBus:  # pragma: no cover - needs a Raspberry Pi
    from smbus2 import SMBus
    return SMBus(bus_number)
