#!/usr/bin/env python3
"""Capstone: tile the whole session's gallery into one contact sheet.
Includes a minimal PNG *decoder* — valid because every image here was written
by pnglib with filter-0 (None) scanlines, so un-filtering is just dropping the
leading byte of each row. numpy + stdlib.

Run from a directory holding the rendered <name>.png files (e.g. ../images,
or render them here first). Writes GALLERY.png.
"""
import struct, zlib
import numpy as np
from pnglib import write_png

IMG_DIR = "."    # directory containing the rendered piece PNGs
PIECES = ["dejong_hi", "julia", "newton", "mandelbrot",
          "flowfield", "domainwarp", "harmonograph", "lorenz",
          "phyllotaxis", "reaction", "chladni", "voronoi"]
T = 380          # thumbnail edge
PAD = 22
COLS, ROWS = 4, 3
BG = np.array([14, 13, 22], np.uint8)


def read_png(path):
    """Decode an 8-bit RGB, filter-0 PNG into (H,W,3) uint8."""
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos = 8; w = h = 0; idat = b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]
        tag = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", chunk[:8])
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    stride = w * 3 + 1
    arr = np.frombuffer(raw, np.uint8).reshape(h, stride)
    assert (arr[:, 0] == 0).all(), "expected filter-0 scanlines"
    return arr[:, 1:].reshape(h, w, 3)


def resize_nn(img, t):
    h, w = img.shape[:2]
    yi = (np.arange(t) * h // t)
    xi = (np.arange(t) * w // t)
    return img[yi][:, xi]


def main():
    canvas = np.empty((ROWS * T + (ROWS + 1) * PAD,
                       COLS * T + (COLS + 1) * PAD, 3), np.uint8)
    canvas[:] = BG
    for i, name in enumerate(PIECES):
        thumb = resize_nn(read_png(f"{IMG_DIR}/{name}.png"), T)
        r, c = divmod(i, COLS)
        y = PAD + r * (T + PAD)
        x = PAD + c * (T + PAD)
        # thin border
        canvas[y - 2:y + T + 2, x - 2:x + T + 2] = (60, 58, 80)
        canvas[y:y + T, x:x + T] = thumb
        print(f"  placed {name}")
    write_png("GALLERY.png", canvas)
    print(f"wrote GALLERY.png ({canvas.shape[1]}x{canvas.shape[0]})")


if __name__ == "__main__":
    main()
