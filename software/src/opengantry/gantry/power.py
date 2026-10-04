"""Power-module host software: sleep mode, e-stop and 5 V rail status.

Klipper's [idle_timeout] runs OG_SLEEP on its own (firmware/klipper/printer.cfg),
so the machine still sleeps if this process dies. This class adds:
  * an explicit sleep()/wake() for scan scripts,
  * e-stop detection from the 24 V MOTION sense divider (GPIO 17),
  * buck power-good monitoring (GPIO 27, D42V55F5 PG pin, open drain).
GPIO access is injected so the logic is testable off the Pi.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .config import MachineConfig
from .moonraker import GcodeSink

GpioReader = Callable[[int], bool]


def pi_gpio_reader() -> GpioReader:  # pragma: no cover - needs a Raspberry Pi
    """Real reader using gpiozero (Pi 4 and Pi 5)."""
    from gpiozero import DigitalInputDevice

    cache: dict[int, DigitalInputDevice] = {}

    def read(pin: int) -> bool:
        if pin not in cache:
            cache[pin] = DigitalInputDevice(pin, pull_up=None, active_state=True)
        return bool(cache[pin].value)

    return read


@dataclass
class PowerStatus:
    motion_power: bool   # True = 24 V reaches the motion board (e-stop released)
    rail_5v_good: bool

    @property
    def estop_active(self) -> bool:
        return not self.motion_power


class PowerManager:
    def __init__(self, cfg: MachineConfig, sink: GcodeSink, gpio: GpioReader):
        self.cfg, self.sink, self.gpio = cfg, sink, gpio
        self.asleep = False

    def status(self) -> PowerStatus:
        io = self.cfg.host_io
        return PowerStatus(self.gpio(io["estop_sense_gpio"]), self.gpio(io["buck_pg_gpio"]))

    def sleep(self) -> None:
        """Drivers, lights and controller fan off. Pi and Moonraker stay up."""
        self.sink.gcode("OG_SLEEP")
        self.asleep = True

    def wake(self) -> None:
        st = self.status()
        if st.estop_active:
            raise RuntimeError("E-stop is latched: twist to release, then FIRMWARE_RESTART and re-home")
        self.sink.gcode("OG_WAKE")
        self.asleep = False
