"""Small image helpers with no OpenCV: 8-bit PNG read/write (PNG spec [H60]) and the centre-region mean.

OpenCV is still used for the camera; this keeps `verify`, `curve`, `calibrate` and the simulator dependency-free.
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

import numpy as np


def centre_mean(a) -> float:
    """Mean of the middle third of the image (the sample), all channels."""
    a = np.asarray(a, dtype=float)
    h, w = a.shape[:2]
    return float(a[h // 3: 2 * h // 3, w // 3: 2 * w // 3].mean())


def write_png(path: str | Path, img) -> None:
    """Grey (H, W) or RGB (H, W, 3) uint8 array -> PNG."""
    a = np.clip(np.asarray(img), 0, 255).astype(np.uint8)
    h, w = a.shape[:2]
    ctype = 0 if a.ndim == 2 else 2
    raw = b"".join(b"\x00" + a[y].tobytes() for y in range(h))

    def chunk(t: bytes, d: bytes) -> bytes:
        return struct.pack(">I", len(d)) + t + d + struct.pack(">I", zlib.crc32(t + d) & 0xFFFFFFFF)
    Path(path).write_bytes(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, ctype, 0, 0, 0))
                          + chunk(b"IDAT", zlib.compress(raw, 6)) + chunk(b"IEND", b""))


def read_png(path: str | Path):
    """8-bit, non-interlaced PNG (grey, grey+alpha, RGB, RGBA) -> uint8 array; None if unsupported."""
    b = Path(path).read_bytes()
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
    """OpenCV when installed (any format), else the PNG reader above."""
    try:
        import cv2
        return lambda p: cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
    except ImportError:
        return lambda p: read_png(p) if str(p).lower().endswith(".png") else None
