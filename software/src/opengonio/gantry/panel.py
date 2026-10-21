"""Physical buttons -> machine actions (runs on the laptop).

HOME  -> home all installed axes        START -> run the loaded plan (one pose per tick)
STOP  -> stop the plan + soft stop       LIGHT -> toggle the white light
NEXT  -> one plan pose                   POWER 0 -> mark unhomed; POWER 1 -> re-init drivers (M122 I / $MI)
PAUSE -> stop the plan after the pose in progress (START carries on from the next pose). It is a hub button: for an
         immediate stop use the e-stop.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .gantry import Gantry
from .safety import on_power


@dataclass
class Panel:
    g: Gantry
    plan: list[dict[str, float]] = field(default_factory=list)
    index: int = 0
    running: bool = False
    log: list[str] = field(default_factory=list)

    def handle(self, kind: str, value: str) -> None:
        if kind == "POWER":
            self.running = False
            self.log.append(on_power(self.g, value))
            return
        if kind != "BTN":
            return
        self.log.append(value)
        if value == "HOME":
            self.g.home()
        elif value == "LIGHT":
            if self.running:                      # a measurement owns the lamp: no toggling mid-plan
                self.log.append("LIGHT ignored while a plan is running")
            else:
                self.g.toggle_light("white")
        elif value == "STOP":
            self.running = False
            errs = self.g.all_lights_off()
            self.g.stop()
            if errs:
                self.log.append("lamp may still be on: " + "; ".join(errs))
        elif value == "START":
            self.running = True
        elif value == "PAUSE":
            self.running = False                  # lamp and position kept: START resumes at self.index
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
