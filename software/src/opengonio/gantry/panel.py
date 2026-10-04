"""Physical buttons -> machine actions (runs on the laptop).

HOME  -> home all installed axes        START -> run the loaded plan (one pose per tick)
STOP  -> stop the plan + soft stop       LIGHT -> toggle the white light
NEXT  -> one plan pose                   POWER 0 -> mark unhomed; POWER 1 -> re-init drivers ($MI)
PAUSE is wired to the E4 feed-hold pin, so it works without the laptop.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .gantry import Gantry


@dataclass
class Panel:
    g: Gantry
    plan: list[dict[str, float]] = field(default_factory=list)
    index: int = 0
    running: bool = False
    log: list[str] = field(default_factory=list)

    def handle(self, kind: str, value: str) -> None:
        if kind == "POWER":
            if value == "0":
                self.running = False
                self.g.homed.clear()
                self.log.append("e-stop: motion power off, re-home needed")
            else:
                try:
                    self.g.reinit_drivers()
                    self.log.append("motion power back: drivers re-initialised, press HOME")
                except Exception as exc:          # controller link may still be reconnecting
                    self.g.homed.clear()
                    self.log.append(f"motion power back; re-init failed ({exc}); reconnect, then HOME")
            return
        if kind != "BTN":
            return
        self.log.append(value)
        if value == "HOME":
            self.g.home()
        elif value == "LIGHT":
            self.g.toggle_light("white")
        elif value == "STOP":
            self.running = False
            self.g.stop()
        elif value == "START":
            self.running = True
        elif value == "NEXT":
            self.next_pose()

    def tick(self) -> None:
        """Call between hub polls: advances one pose while running, so STOP stays responsive."""
        if self.running:
            self.next_pose()

    def next_pose(self) -> None:
        if self.index >= len(self.plan):
            self.running = False
            self.log.append("plan finished")
            return
        self.g.move(self.plan[self.index])
        self.index += 1
