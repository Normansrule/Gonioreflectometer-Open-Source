"""FluidNC client over USB serial, Bluetooth serial (COM / rfcomm port) or WiFi telnet.

Protocol (FluidNC docs [R20]-[R30]):
  line commands answer "ok" or "error:N";  realtime: "?" status, "!" hold, "~" resume, 0x18 reset
  status: <Idle|MPos:x,y,z,a|FS:0,0|Pn:XY>   (values in axis order, unlabelled)
  $H home all, $HX one axis;  $MD / $ME motors disable / enable;  M62/M63 P<n> user outputs
"""
from __future__ import annotations

import re
import socket
import time
from dataclasses import dataclass, field
from typing import Protocol

AXIS_ORDER = "XYZABC"
STATUS_RE = re.compile(r"<([A-Za-z]+)(?::\d+)?\|MPos:([-\d.,]+)(?:\|.*?Pn:([A-Z]*))?")


class Transport(Protocol):
    def write(self, data: bytes) -> None: ...
    def readline(self, timeout: float) -> str: ...
    def close(self) -> None: ...


class SerialTransport:  # pragma: no cover - needs hardware
    """USB serial (CH340 on the E4) or a paired Bluetooth SPP port [R44][R45][R46]."""

    def __init__(self, port: str = "auto", baud: int = 115200):
        import serial
        from serial.tools import list_ports
        if port == "auto":
            ch340 = [p.device for p in list_ports.comports() if p.vid == 0x1A86]
            if not ch340:
                raise RuntimeError("no CH340 port found; set controller.port in machine.yaml")
            port = ch340[0]
        self.s = serial.Serial(port, baud, timeout=0.1)
        time.sleep(2.0)                      # ESP32 resets when the port opens
        self.s.reset_input_buffer()

    def write(self, data: bytes) -> None:
        self.s.write(data)

    def readline(self, timeout: float) -> str:
        self.s.timeout = timeout
        return self.s.readline().decode(errors="replace").strip()

    def close(self) -> None:
        self.s.close()


class TcpTransport:  # pragma: no cover - needs hardware
    """WiFi: FluidNC telnet server on port 23 [R24]."""

    def __init__(self, host: str = "fluidnc.local", port: int = 23):
        self.sock = socket.create_connection((host, port), timeout=5)
        self.buf = b""

    def write(self, data: bytes) -> None:
        self.sock.sendall(data)

    def readline(self, timeout: float) -> str:
        self.sock.settimeout(timeout)
        while b"\n" not in self.buf:
            try:
                chunk = self.sock.recv(1024)
            except socket.timeout:
                return ""
            if not chunk:
                return ""
            self.buf += chunk
        line, self.buf = self.buf.split(b"\n", 1)
        return line.decode(errors="replace").strip()

    def close(self) -> None:
        self.sock.close()


class FluidNCError(RuntimeError):
    pass


@dataclass
class Status:
    state: str
    mpos: dict[str, float]
    pins: str = ""


def parse_status(line: str) -> Status | None:
    m = STATUS_RE.search(line)
    if not m:
        return None
    vals = [float(v) for v in m.group(2).split(",")]
    return Status(m.group(1), dict(zip(AXIS_ORDER, vals)), m.group(3) or "")


class FluidNC:
    def __init__(self, transport: Transport, timeout_s: float = 120.0):
        self.t, self.timeout_s = transport, timeout_s

    def command(self, line: str) -> list[str]:
        """Send one line, return any text before 'ok'. Raises on 'error:'/'ALARM:'."""
        self.t.write((line.strip() + "\n").encode())
        out, deadline = [], time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            resp = self.t.readline(0.5)
            if not resp:
                continue
            if resp == "ok":
                return out
            if resp.startswith(("error", "ALARM")):
                raise FluidNCError(f"{line!r} -> {resp}")
            out.append(resp)
        raise FluidNCError(f"timeout waiting for ok after {line!r}")

    def realtime(self, ch: bytes) -> None:
        self.t.write(ch)

    def status(self) -> Status:
        self.realtime(b"?")
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            s = parse_status(self.t.readline(0.3))
            if s:
                return s
        raise FluidNCError("no status report")

    def wait_idle(self, poll_s: float = 0.1) -> Status:
        deadline = time.monotonic() + self.timeout_s
        while time.monotonic() < deadline:
            s = self.status()
            if s.state == "Idle":
                return s
            if s.state in ("Alarm", "Door"):
                raise FluidNCError(f"controller in {s.state}")
            if s.state == "Hold":               # PAUSE button: wait as long as it takes
                deadline = time.monotonic() + self.timeout_s
            time.sleep(poll_s)
        raise FluidNCError("timeout waiting for Idle")

    # convenience ------------------------------------------------------------
    def hold(self) -> None:
        self.realtime(b"!")

    def resume(self) -> None:
        self.realtime(b"~")

    def reset(self) -> None:
        self.realtime(b"\x18")


@dataclass
class RecordingTransport:
    """Offline stand-in: answers 'ok' and records every line (dry runs, tests)."""
    lines: list[str] = field(default_factory=list)
    pending: list[str] = field(default_factory=list)
    mpos: dict[str, float] = field(default_factory=lambda: dict.fromkeys(AXIS_ORDER[:4], 0.0))

    def write(self, data: bytes) -> None:
        txt = data.decode()
        if txt == "?":
            vals = ",".join(f"{self.mpos[a]:.3f}" for a in AXIS_ORDER[:4])
            self.pending.append(f"<Idle|MPos:{vals}|FS:0,0>")
            return
        if len(txt) == 1:                 # other realtime bytes
            self.lines.append(repr(txt))
            return
        self.lines.append(txt.strip())
        self.pending.append("ok")

    def readline(self, timeout: float) -> str:
        return self.pending.pop(0) if self.pending else ""

    def close(self) -> None:
        pass
