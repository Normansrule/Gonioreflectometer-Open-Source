"""USB (UVC) camera with locked exposure, gain and white balance.

Linux: v4l2-ctl sets controls (names vary by kernel: check `v4l2-ctl -l`) [R50][R51][R52].
Windows/macOS: OpenCV properties; behaviour differs by backend and camera [R47][R48][R53].
Note: some Arducam UVC modules apply a new exposure only after a few frames [K6].
"""
from __future__ import annotations

import platform
import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class CameraSettings:
    exposure_ms: float
    gain: int = 0
    wb_kelvin: int = 5000


def v4l2_args(dev: str, s: CameraSettings, new_names: bool = True) -> list[list[str]]:
    """v4l2-ctl calls for manual control. exposure_time_absolute is in 100 us units [R51]."""
    auto, expo = ("auto_exposure", "exposure_time_absolute") if new_names else ("exposure_auto", "exposure_absolute")
    units = max(1, round(s.exposure_ms * 10))
    return [
        ["v4l2-ctl", "-d", dev, "-c", f"{auto}=1"],                   # 1 = manual
        ["v4l2-ctl", "-d", dev, "-c", f"{expo}={units}"],
        ["v4l2-ctl", "-d", dev, "-c", f"gain={s.gain}"],
        ["v4l2-ctl", "-d", dev, "-c", "white_balance_automatic=0"],
        ["v4l2-ctl", "-d", dev, "-c", f"white_balance_temperature={s.wb_kelvin}"],
    ]


class UvcCamera:  # pragma: no cover - needs hardware
    def __init__(self, index: int = 0, width: int = 3840, height: int = 3032, discard: int = 4):
        import cv2
        self.cv2 = cv2
        backend = {"Windows": cv2.CAP_DSHOW, "Linux": cv2.CAP_V4L2}.get(platform.system(), cv2.CAP_ANY)
        self.cap = cv2.VideoCapture(index, backend)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.index, self.discard = index, discard

    def set(self, s: CameraSettings) -> None:
        if platform.system() == "Linux" and shutil.which("v4l2-ctl"):
            for args in v4l2_args(f"/dev/video{self.index}", s):
                subprocess.run(args, check=False, capture_output=True)
        else:
            cv2 = self.cv2
            self.cap.set(cv2.CAP_PROP_AUTO_EXPOSURE, 0.25)      # DirectShow "manual"; unconfirmed per camera
            import math
            self.cap.set(cv2.CAP_PROP_EXPOSURE, round(math.log2(s.exposure_ms / 1000.0)))
            self.cap.set(cv2.CAP_PROP_GAIN, s.gain)
            self.cap.set(cv2.CAP_PROP_AUTO_WB, 0)
            self.cap.set(cv2.CAP_PROP_WB_TEMPERATURE, s.wb_kelvin)

    def set_exposure_ms(self, ms: float) -> None:
        self.set(CameraSettings(ms))

    def grab(self):
        for _ in range(self.discard):            # flush frames taken with old settings
            self.cap.read()
        ok, frame = self.cap.read()
        if not ok:
            raise RuntimeError("camera read failed")
        return frame

    def bracket(self, exposures_ms: list[float], gain: int = 0, wb: int = 5000):
        frames = []
        for e in exposures_ms:
            self.set(CameraSettings(e, gain, wb))
            frames.append(self.grab())
        return frames
