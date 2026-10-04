"""Minimal Moonraker HTTP client (standard library only).

Endpoints used (https://moonraker.readthedocs.io/en/latest/external_api/printer/):
  POST /printer/gcode/script   {"script": "..."}  - returns after the G-code completes
  POST /printer/emergency_stop
  GET  /printer/objects/query?<objects>
  GET  /printer/info
"""
from __future__ import annotations

import json
import urllib.parse
import urllib.request
from typing import Any, Protocol


class GcodeSink(Protocol):
    def gcode(self, script: str) -> Any: ...
    def emergency_stop(self) -> Any: ...


class MoonrakerError(RuntimeError):
    pass


class Moonraker:
    def __init__(self, url: str = "http://localhost:7125", timeout_s: float = 120.0):
        self.url = url.rstrip("/")
        self.timeout_s = timeout_s

    def _request(self, method: str, path: str, body: dict | None = None) -> Any:
        data = json.dumps(body).encode() if body is not None else None
        req = urllib.request.Request(self.url + path, data=data, method=method,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                payload = json.loads(resp.read().decode() or "{}")
        except urllib.error.HTTPError as exc:  # Klipper errors arrive as HTTP 400
            raise MoonrakerError(exc.read().decode(errors="replace")) from exc
        return payload.get("result", payload)

    def gcode(self, script: str) -> Any:
        return self._request("POST", "/printer/gcode/script", {"script": script})

    def emergency_stop(self) -> Any:
        return self._request("POST", "/printer/emergency_stop")

    def info(self) -> Any:
        return self._request("GET", "/printer/info")

    def query(self, *objects: str) -> Any:
        q = "&".join(urllib.parse.quote(o) for o in objects)
        return self._request("GET", f"/printer/objects/query?{q}")


class RecordingSink:
    """Test double / dry-run sink that records every script."""

    def __init__(self) -> None:
        self.scripts: list[str] = []
        self.stopped = False

    def gcode(self, script: str) -> None:
        self.scripts.append(script)

    def emergency_stop(self) -> None:
        self.stopped = True
