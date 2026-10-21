"""USB (UVC) camera with locked exposure, gain and white balance, and a read-back of what the camera applied.

One interface for every caller (laptop capture, station, scanner):
    configure(CameraSettings) -> dict of APPLIED settings (read back from the camera); raises CameraSettingsError
                                  when a mandatory setting can't be set or confirmed
    grab() -> frame (H, W, 3) RGB uint8;  close()
Linux: v4l2-ctl sets and reads the controls (names vary by kernel: the old names are tried when the new ones fail)
[R50][R51][R52]. Windows/macOS: OpenCV properties; support depends on backend and camera, so every value is read
back with get() and compared [R47][R48][R53]. The B0433 streams processed MJPEG/YUYV (not raw sensor data); the
camera-response calibration (gamma) is what makes the counts usable [K3].
Note: some Arducam UVC modules apply a new exposure only after a few frames [K6]: `discard` frames are dropped
after every configure and before every grab, and the number is recorded.
"""
from __future__ import annotations

import math
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Callable


@dataclass
class CameraSettings:
    exposure_ms: float
    gain: int = 0
    wb_kelvin: int = 5000


class CameraSettingsError(RuntimeError):
    pass


NEW = {"auto": "auto_exposure", "exposure": "exposure_time_absolute", "awb": "white_balance_automatic"}
OLD = {"auto": "exposure_auto", "exposure": "exposure_absolute", "awb": "white_balance_temperature_auto"}


def v4l2_args(dev: str, s: CameraSettings, new_names: bool = True) -> list[list[str]]:
    """v4l2-ctl calls for manual control. exposure_time_absolute is in 100 us units [R51]."""
    n = NEW if new_names else OLD
    units = max(1, round(s.exposure_ms * 10))
    return [
        ["v4l2-ctl", "-d", dev, "-c", f"{n['auto']}=1"],                   # 1 = manual
        ["v4l2-ctl", "-d", dev, "-c", f"{n['exposure']}={units}"],
        ["v4l2-ctl", "-d", dev, "-c", f"gain={s.gain}"],
        ["v4l2-ctl", "-d", dev, "-c", f"{n['awb']}=0"],
        ["v4l2-ctl", "-d", dev, "-c", f"white_balance_temperature={s.wb_kelvin}"],
    ]


def parse_v4l2_get(text: str) -> dict[str, int]:
    """`v4l2-ctl -C a,b` output ('name: value' per line) -> {name: value}."""
    out = {}
    for line in text.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            try:
                out[k.strip()] = int(v.strip().split()[0])
            except (ValueError, IndexError):
                pass
    return out


def v4l2_configure(dev: str, s: CameraSettings, run: Callable = subprocess.run) -> dict:
    """Set with the new control names, fall back to the old ones, then read back and check.
    run(args, ...) -> object with returncode/stdout (subprocess.run signature; injectable for tests)."""
    names = None
    for new in (True, False):
        res = [run(a, check=False, capture_output=True, text=True) for a in v4l2_args(dev, s, new)]
        if all(r.returncode == 0 for r in res[:3]):                     # manual mode, exposure, gain are mandatory
            names = NEW if new else OLD
            break
    if names is None:
        raise CameraSettingsError(f"{dev}: v4l2-ctl could not set manual exposure/gain (check `v4l2-ctl -d {dev} -l`)")
    q = run(["v4l2-ctl", "-d", dev, "-C", f"{names['auto']},{names['exposure']},gain,white_balance_temperature"],
            check=False, capture_output=True, text=True)
    got = parse_v4l2_get(q.stdout or "") if q.returncode == 0 else {}
    want_units = max(1, round(s.exposure_ms * 10))
    if got.get(names["auto"]) != 1 or got.get(names["exposure"]) != want_units or got.get("gain") != s.gain:
        raise CameraSettingsError(f"{dev}: read-back {got} does not confirm manual exposure {want_units} x 100 us, gain {s.gain}")
    return {"exposure_ms": got[names["exposure"]] / 10.0, "gain": got["gain"], "auto_exposure": "manual",
            "wb_kelvin": got.get("white_balance_temperature"), "method": f"v4l2-ctl ({'new' if names is NEW else 'old'} names)"}


class UvcCamera:  # pragma: no cover - needs hardware
    def __init__(self, index: int = 0, width: int = 3840, height: int = 3032, discard: int = 4):
        import cv2
        self.cv2 = cv2
        backend = {"Windows": cv2.CAP_DSHOW, "Linux": cv2.CAP_V4L2}.get(platform.system(), cv2.CAP_ANY)
        self.cap = cv2.VideoCapture(index, backend)
        if not self.cap.isOpened():
            raise CameraSettingsError(f"camera {index} did not open")
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.size = (int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        if self.size != (width, height):
            raise CameraSettingsError(f"camera {index} gives {self.size[0]} x {self.size[1]}, not {width} x {height}")
        self.index, self.discard = index, discard
        self.applied: dict = {}

    def configure(self, s: CameraSettings) -> dict:
        if platform.system() == "Linux" and shutil.which("v4l2-ctl"):
            applied = v4l2_configure(f"/dev/video{self.index}", s)
        else:
            cv2 = self.cv2
            sets = {cv2.CAP_PROP_AUTO_EXPOSURE: 0.25,                     # DirectShow "manual"
                    cv2.CAP_PROP_EXPOSURE: round(math.log2(s.exposure_ms / 1000.0)),
                    cv2.CAP_PROP_GAIN: s.gain, cv2.CAP_PROP_AUTO_WB: 0, cv2.CAP_PROP_WB_TEMPERATURE: s.wb_kelvin}
            failed = [k for k, v in sets.items() if not self.cap.set(k, v)]
            exp = self.cap.get(cv2.CAP_PROP_EXPOSURE)
            if cv2.CAP_PROP_EXPOSURE in failed or abs(exp - sets[cv2.CAP_PROP_EXPOSURE]) > 0.5:
                raise CameraSettingsError(f"exposure not applied (read back {exp}, wanted {sets[cv2.CAP_PROP_EXPOSURE]})")
            applied = {"exposure_ms": 1000.0 * 2 ** exp, "gain": self.cap.get(cv2.CAP_PROP_GAIN),
                       "wb_kelvin": self.cap.get(cv2.CAP_PROP_WB_TEMPERATURE), "method": "OpenCV get() after set()",
                       "note": "OpenCV exposure is log2 seconds: applied value quantised to a power of 2"}
        for _ in range(self.discard):
            self.cap.read()
        self.applied = {**applied, "width": self.size[0], "height": self.size[1], "discard_frames": self.discard,
                        "device": f"index {self.index}"}
        return dict(self.applied)

    def set(self, s: CameraSettings) -> dict:            # older name
        return self.configure(s)

    def set_exposure_ms(self, ms: float) -> dict:
        return self.configure(CameraSettings(ms))

    def readback(self) -> dict:
        return dict(self.applied)

    def grab(self):
        for _ in range(self.discard):            # flush frames taken with old settings
            self.cap.read()
        ok, frame = self.cap.read()
        if not ok or frame is None:
            raise RuntimeError("camera read failed")
        return self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)

    def bracket(self, exposures_ms: list[float], gain: int = 0, wb: int = 5000):
        frames = []
        for e in exposures_ms:
            self.configure(CameraSettings(e, gain, wb))
            frames.append(self.grab())
        return frames

    def close(self) -> None:
        self.cap.release()
