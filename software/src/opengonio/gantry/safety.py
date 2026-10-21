"""One place for what a power or STOP event means, used by the panel, the station and laptop runs.

POWER 0 (motion power cut: e-stop, over-travel switch, adapter unplugged)
    -> position no longer trusted (re-home), any running job stops, light state unknown.
POWER 1 (motion power back)
    -> drivers re-initialised (grblHAL M122 I / FluidNC $MI: the TMC2209s restarted at defaults), still unhomed: nothing moves until HOME.
Nothing resumes by itself after either event.
"""
from __future__ import annotations

from .gantry import Gantry


def on_power(g: Gantry, value: str) -> str:
    """Apply a POWER event to the gantry; returns a one-line message for the log / OLED."""
    if value == "0":
        g.invalidate()
        errs = g.all_lights_off()          # the controller may still be reachable (motor power only): lamp off anyway
        if errs:
            g.light_state.clear()          # state unknown: the next LIGHT press must not assume "off"
            return "e-stop: motion power off; job stopped; LAMP STATE UNKNOWN; press HOME when power is back"
        return "e-stop: motion power off; job stopped; lamp off; press HOME when power is back"
    try:
        g.reinit_drivers()
        return "motion power back: drivers re-initialised; press HOME"
    except Exception as exc:                 # controller link may still be reconnecting
        g.invalidate()
        return f"motion power back; driver re-init failed ({exc}); reconnect, then HOME"
