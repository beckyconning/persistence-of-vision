"""
Truchet tiles — a tiling generator new to the corpus. Fill a grid; in each cell drop one of two
quarter-arc tiles (⌐ or its mirror). Because every arc meets a cell edge at the same two midpoints,
arcs join across edges into long continuous loops — a maze of interlocking rings emerges from a
purely LOCAL random choice per cell. Nobody routes the loops; the edge-matching forces them.

Rendered as glowing arcs on near-black, hue drifting across the grid so the woven loops read as
bands of coloured light. Deterministic (seeded) so the weave is reproducible.
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 1200
CELLS = 16
T = W // CELLS                 # tile size
rng = np.random.default_rng(20260702)
img = np.zeros((H, W, 3), np.float64)
yy, xx = np.mgrid[0:H, 0:W]

LW = T * 0.14                  # arc line half-width
def arc(cx, cy, r, col):
    # soft ring at radius r centred on (cx,cy), clipped to the local tile window
    d = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    g = np.exp(-((d - r) ** 2) / (2 * LW * LW))
    img[:] += g[..., None] * col

for j in range(CELLS):
    for i in range(CELLS):
        x0, y0 = i * T, j * T
        # hue drifts diagonally across the grid
        t = (i + j) / (2 * (CELLS - 1))
        col = np.array([
            0.5 + 0.5 * math.cos(2 * math.pi * (t + 0.00)),
            0.5 + 0.5 * math.cos(2 * math.pi * (t + 0.33)),
            0.5 + 0.5 * math.cos(2 * math.pi * (t + 0.66)),
        ]) * 0.9 + 0.1
        if rng.random() < 0.5:
            # arcs centred on top-left and bottom-right corners
            arc(x0, y0, T / 2, col)
            arc(x0 + T, y0 + T, T / 2, col)
        else:
            # arcs centred on top-right and bottom-left corners
            arc(x0 + T, y0, T / 2, col)
            arc(x0, y0 + T, T / 2, col)

img = 1.0 - np.exp(-1.4 * img)     # additive glow → tone-mapped
np.clip(img, 0, 1, out=img)
# faint cool ground tint instead of pure black
img = img + (1 - img) * 0.0
write_png(os.path.join(OUT, "truchet.png"), (img * 255).astype(np.uint8))
k = 3
hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/truchet_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote truchet.png ({W}x{H}, {CELLS}x{CELLS} tiles)")
