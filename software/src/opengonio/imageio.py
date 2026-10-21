"""Image helpers: 8-bit PNG read/write without OpenCV (PNG spec [H60]), one pixel convention, region means.

Pixel convention (the same whichever reader is installed): every reader returns uint8 grey (H, W) or RGB (H, W, 3),
never BGR. The measured quantity is the SIGNAL PLANE: the equal-weight mean of R, G and B per pixel (grey stays grey).
Region values are means of per-pixel values, so a non-linear camera response is undone per pixel first
(`region_mean(..., linear=cal.linear_array)`), never on an averaged count.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


SATURATED = 254                 # 8-bit counts at or above this are clipped


def signal_plane(a) -> np.ndarray:
    """(H, W) float: grey as is; RGB -> equal-weight mean of the three channels (an alpha channel is ignored)."""
    a = np.asarray(a, dtype=float)
    if a.ndim == 3:
        a = a[:, :, :3].mean(axis=2)
    if a.ndim != 2:
        raise ValueError(f"image must be (H, W) or (H, W, 3), got shape {a.shape}")
    return a


def decoded(img) -> bool:
    """True if `img` is a usable decoded frame: 2-D or 3-D, non-empty, numeric."""
    if img is None:
        return False
    a = np.asarray(img)
    return a.ndim in (2, 3) and a.shape[0] > 0 and a.shape[1] > 0 and a.dtype.kind in "uif"


def centre_box(shape) -> tuple[int, int, int, int]:
    """Middle third (y0, y1, x0, x1): the legacy region, used when no sample geometry is known."""
    h, w = shape[:2]
    return h // 3, 2 * h // 3, w // 3, 2 * w // 3


def region_mean(a, box=None, linear=None, reject_saturated: bool = False, mask=None) -> float | None:
    """Mean of the signal plane over `mask` (bool, image shape) or box (y0, y1, x0, x1; default: middle third).
    linear: per-pixel response correction (counts array -> linear array), applied BEFORE averaging.
    reject_saturated: None if any pixel of the region is clipped (a clipped highlight has no valid mean)."""
    p = signal_plane(a)
    clip = clipped(a)
    if mask is not None:
        m = np.asarray(mask, dtype=bool)
        r, rc = p[m], clip[m]
    else:
        y0, y1, x0, x1 = box or centre_box(p.shape)
        r, rc = p[y0:y1, x0:x1], clip[y0:y1, x0:x1]
    if r.size == 0:
        return None
    if reject_saturated and rc.any():
        return None
    return float((linear(r) if linear else r).mean())


def clipped(a) -> np.ndarray:
    """Pixels where ANY colour channel is at the top of the range (one clipped channel already biases the mean)."""
    x = np.asarray(a)
    if x.ndim == 3:
        x = x[..., :3].max(axis=2)
    if x.dtype == np.uint16:
        return x >= SATURATED * 257
    return x >= SATURATED


def centre_mean(a) -> float:
    """Raw mean counts of the middle third of the signal plane (reporting only; use region_mean for radiometry)."""
    return float(region_mean(a))


def write_png(path: str | Path, img) -> None:
    """Grey (H, W) or RGB (H, W, 3) uint8 array -> PNG."""
    Path(path).write_bytes(encode_png(img))


def encode_png(img) -> bytes:
    """Grey (H, W) or RGB (H, W, 3) uint8 array -> PNG bytes (the control app serves frames from memory)."""
    a = np.clip(np.asarray(img), 0, 255).astype(np.uint8)
    h, w = a.shape[:2]
    ctype = 0 if a.ndim == 2 else 2
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def read_png(path: str | Path):
    """8-bit, non-interlaced PNG (grey, grey+alpha, RGB, RGBA) -> uint8 array; None if unsupported."""
    try:
        return _read_png(Path(path).read_bytes())
    except (struct.error, zlib.error, ValueError, TypeError, IndexError):
        return None                                  # truncated or malformed file: not an image


def _read_png(b: bytes):
    if b[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    i, idat, hdr = 8, b"", None
    while i < len(b):
        n, t = struct.unpack(">I4s", b[i:i + 8])
        d = b[i + 8:i + 8 + n]
        if t == b"IHDR":
            hdr = struct.unpack(">IIBBBBB", d)
        elif t == b"IDAT":
            idat += d
        i += 12 + n
    if hdr is None:
        return None
    w, h, depth, ctype, _, _, interlace = hdr
    ch = {0: 1, 2: 3, 4: 2, 6: 4}.get(ctype)
    if depth != 8 or ch is None or interlace:
        return None
    raw, stride = zlib.decompress(idat), w * ch
    out = np.zeros((h, stride), dtype=np.int32)
    prev = np.zeros(stride, dtype=np.int32)
    for y in range(h):
        f, line = raw[y * (stride + 1)], np.frombuffer(raw, np.uint8, stride, y * (stride + 1) + 1).astype(np.int32)
        if f == 0:
            cur = line
        elif f == 2:
            cur = (line + prev) & 255
        else:                                    # 1 Sub, 3 Average, 4 Paeth depend on the pixel to the left
            cur = np.zeros(stride, dtype=np.int32)
            for x in range(stride):
                a = cur[x - ch] if x >= ch else 0
                c = prev[x - ch] if x >= ch else 0
                if f == 1:
                    p = a
                elif f == 3:
                    p = (a + prev[x]) // 2
                else:
                    pa, pb, pc = abs(prev[x] - c), abs(a - c), abs(a + prev[x] - 2 * c)
                    p = a if pa <= pb and pa <= pc else prev[x] if pb <= pc else c
                cur[x] = (line[x] + p) & 255
        out[y], prev = cur, cur
    a = out.astype(np.uint8).reshape(h, w, ch)
    return a[:, :, 0] if ch == 1 else a[:, :, :3] if ch in (3, 4) else a[:, :, 0]


def default_reader():
    """OpenCV when installed (any format), else the PNG reader above. Both return grey or RGB (never BGR), so the
    signal plane, and every number computed from it, is the same with or without OpenCV."""
    try:
        import cv2
    except ImportError:
        return lambda p: read_png(p) if str(p).lower().endswith(".png") else None

    def read(p):
        a = cv2.imread(str(p), cv2.IMREAD_UNCHANGED)
        if a is None or a.dtype != np.uint8:
            return None if a is None else (a // 256).astype(np.uint8) if a.dtype == np.uint16 else None
        if a.ndim == 3:
            a = cv2.cvtColor(a, cv2.COLOR_BGRA2RGB if a.shape[2] == 4 else cv2.COLOR_BGR2RGB)
        return a
    return read


def save_image(path: str | Path, img) -> bool:
    """Save an RGB/grey frame (the camera convention). OpenCV when installed (any extension; RGB -> BGR for it),
    else PNG. Returns False when the writer reports failure, so callers can treat it as a failed acquisition."""
    a = np.asarray(img)
    try:
        import cv2
    except ImportError:
        if not str(path).lower().endswith(".png"):
            return False
        write_png(path, a)
        return True
    if a.ndim == 3:
        a = cv2.cvtColor(a, cv2.COLOR_RGB2BGR)
    return bool(cv2.imwrite(str(path), a))
