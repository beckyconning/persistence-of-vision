#!/usr/bin/env python3
"""Session-2 capstone contact sheet — tiles the rendered pieces (all filter-0
PNGs from pnglib) into one overview. Reuses the filter-0 decoder."""
import struct, zlib
import numpy as np
from pnglib import write_png

PIECES = ["landscape", "frame_dusk", "stilllife", "figure2", "martin", "type_grow"]
T, PAD = 440, 26
COLS, ROWS = 3, 2
BG = np.array([238, 230, 213], np.uint8)   # warm paper


def read_png(path):
    d = open(path, "rb").read(); pos, w, h, idat = 8, 0, 0, b""
    while pos < len(d):
        ln = struct.unpack(">I", d[pos:pos+4])[0]; tag = d[pos+4:pos+8]; ch = d[pos+8:pos+8+ln]
        if tag == b"IHDR": w, h = struct.unpack(">II", ch[:8])
        elif tag == b"IDAT": idat += ch
        elif tag == b"IEND": break
        pos += 12 + ln
    a = np.frombuffer(zlib.decompress(idat), np.uint8).reshape(h, w*3+1)
    return a[:, 1:].reshape(h, w, 3)


def fit(img, t):
    h, w = img.shape[:2]
    s = min(h, w); y0 = (h-s)//2; x0 = (w-s)//2          # centre-crop to square
    sq = img[y0:y0+s, x0:x0+s]
    yi = (np.arange(t) * s // t); xi = (np.arange(t) * s // t)
    return sq[yi][:, xi]


def main():
    cv = np.empty((ROWS*T + (ROWS+1)*PAD, COLS*T + (COLS+1)*PAD, 3), np.uint8); cv[:] = BG
    for i, name in enumerate(PIECES):
        th = fit(read_png(f"{name}.png"), T)
        r, c = divmod(i, COLS); y = PAD + r*(T+PAD); x = PAD + c*(T+PAD)
        cv[y-2:y+T+2, x-2:x+T+2] = (120, 108, 90)
        cv[y:y+T, x:x+T] = th
    write_png("GALLERY.png", cv)
    print("wrote GALLERY.png")


if __name__ == "__main__":
    main()
