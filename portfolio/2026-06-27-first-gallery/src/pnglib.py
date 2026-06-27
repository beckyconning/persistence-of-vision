"""Tiny stdlib PNG writer (RGB, 8-bit). Shared across the drawing sketches."""
import struct, zlib
import numpy as np


def write_png(path, rgb):
    """rgb: (H, W, 3) uint8 array."""
    h, w = rgb.shape[:2]

    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))

    filtered = np.hstack([np.zeros((h, 1), np.uint8),
                          rgb.reshape(h, w * 3)]).tobytes()
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(filtered, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


def ramp(t, stops):
    """t: float array in [0,1]; stops: list of (r,g,b) in [0,1]. -> (...,3)."""
    stops = np.asarray(stops, float)
    seg = np.clip(t, 0, 1) * (len(stops) - 1)
    i = np.clip(seg.astype(np.intp), 0, len(stops) - 2)
    f = (seg - i)[..., None]
    return stops[i] + (stops[i + 1] - stops[i]) * f
