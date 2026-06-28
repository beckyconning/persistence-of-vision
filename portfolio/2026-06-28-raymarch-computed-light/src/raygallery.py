#!/usr/bin/env python3
"""Session-4 capstone — 2x2 contact sheet of the four ray-marcher pieces.
Reuses the hand-rolled filter-0 PNG decoder (image-as-input) to tile the renders."""
import struct, zlib
import numpy as np
from pnglib import write_png

PIECES = ["raymarch_spheres", "raymarch2", "raymarch3", "raymarch4"]
TW, TH, PAD = 540, 418, 22
BG = np.array([18, 18, 24], np.uint8)


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


def fit(img, tw, th):
    h, w = img.shape[:2]
    yi = (np.arange(th) * h // th); xi = (np.arange(tw) * w // tw)
    return img[yi][:, xi]


def main():
    cols, rows = 2, 2
    cv = np.empty((rows*TH + (rows+1)*PAD, cols*TW + (cols+1)*PAD, 3), np.uint8); cv[:] = BG
    for i, name in enumerate(PIECES):
        th = fit(read_png(f"{name}.png"), TW, TH)
        r, c = divmod(i, cols); y = PAD + r*(TH+PAD); x = PAD + c*(TW+PAD)
        cv[y-2:y+TH+2, x-2:x+TW+2] = (70, 64, 78)
        cv[y:y+TH, x:x+TW] = th
    write_png("RAYGALLERY.png", cv)
    print("wrote RAYGALLERY.png")


if __name__ == "__main__":
    main()
