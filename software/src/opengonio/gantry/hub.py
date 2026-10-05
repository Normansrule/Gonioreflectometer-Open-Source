"""Client for the Pico panel + sensor hub (firmware/pico-hub/main.py).

Lines from the hub:  "BTN <HOME|START|STOP|LIGHT|NEXT>", "POWER <0|1>", "ENC a b c d", "PONG ...", "ERR ..."
Lines to the hub:    "BAND <0-7>", "BAND OFF", "ENC?", "POWER?", "PING", "SHOW a|b|c" (OLED)
Port: USB (laptop) or the Pi UART /dev/serial0 (standalone station).
"""
from __future__ import annotations

from dataclasses import dataclass, field

BUTTONS = ("HOME", "START", "STOP", "LIGHT", "NEXT")


@dataclass
class HubEvent:
    kind: str           # BTN | POWER | ENC | PONG
    value: str


def parse(line: str) -> HubEvent | None:
    parts = line.strip().split(maxsplit=1)
    if not parts or parts[0] not in ("BTN", "POWER", "ENC", "PONG"):
        return None
    ev = HubEvent(parts[0], parts[1] if len(parts) > 1 else "")
    if ev.kind == "BTN" and ev.value not in BUTTONS:
        return None
    return ev


class Hub:  # pragma: no cover - needs hardware
    def __init__(self, port: str = "auto", baud: int = 115200):
        import serial
        from serial.tools import list_ports
        if port == "auto":
            picos = [p.device for p in list_ports.comports() if p.vid == 0x2E8A]   # Raspberry Pi USB VID
            if not picos:
                raise RuntimeError("Pico hub not found; set hub.port in machine.yaml")
            port = picos[0]
        self.s = serial.Serial(port, baud, timeout=0.1)

    def send(self, line: str) -> None:
        self.s.write((line + "\n").encode())

    def poll(self) -> HubEvent | None:
        return parse(self.s.readline().decode(errors="replace"))

    def band(self, n: int | None) -> None:
        self.send("BAND OFF" if n is None else f"BAND {int(n)}")

    def show(self, *lines: str) -> None:
        self.send("SHOW " + "|".join(str(x).replace("|", "/") for x in lines))


@dataclass
class FakeHub:
    """Test double."""
    queue: list[str] = field(default_factory=list)
    sent: list[str] = field(default_factory=list)

    def send(self, line: str) -> None:
        self.sent.append(line)

    def poll(self) -> HubEvent | None:
        return parse(self.queue.pop(0)) if self.queue else None

    def band(self, n: int | None) -> None:
        self.send("BAND OFF" if n is None else f"BAND {int(n)}")

    def show(self, *lines: str) -> None:
        self.send("SHOW " + "|".join(str(x).replace("|", "/") for x in lines))
