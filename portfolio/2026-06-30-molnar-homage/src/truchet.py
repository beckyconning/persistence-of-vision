"""
Truchet tiles (Smith arcs) — the quick final piece. Each cell randomly places one
of two quarter-arc pairs; neighbouring arcs connect into long flowing loops and a
maze of curves from nothing but a per-cell coin-flip. A classic generative
tradition not yet touched here; multi-scale (some cells subdivide) for richness.
Two-tone ink + amber on paper.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W = H = 980 * SS
rng = np.random.default_rng(44)
ink = np.zeros((H, W))
colacc = np.zeros((H, W, 3))
inkc = np.array([0.13, 0.12, 0.16]); amber = np.array([0.80, 0.50, 0.18])


def arc(cxp, cyp, rad, a0, a1, halfw, col):
    n = max(8, int(rad * (a1 - a0) / 1.5))
    for a in np.linspace(a0, a1, n):
        x, y = cxp + rad * np.cos(a), cyp + rad * np.sin(a)
        lo_x = int(max(0, x - halfw - 1)); hi_x = int(min(W, x + halfw + 2))
        lo_y = int(max(0, y - halfw - 1)); hi_y = int(min(H, y + halfw + 2))
        if hi_x <= lo_x or hi_y <= lo_y:
            continue
        yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
        cov = np.clip((halfw - np.hypot(xx - x, yy - y)) / 1.4 + 0.5, 0, 1)
        sub = ink[lo_y:hi_y, lo_x:hi_x]; m = cov > sub
        ink[lo_y:hi_y, lo_x:hi_x] = np.maximum(sub, cov)
        cc = colacc[lo_y:hi_y, lo_x:hi_x]; cc[m] = col; colacc[lo_y:hi_y, lo_x:hi_x] = cc


def tile(x0, y0, c, col):
    """Two quarter-arcs; orientation flips the corner pair."""
    h = c / 2.0
    hw = max(1.0, c * 0.07) * SS / 2
    if rng.random() < 0.5:
        arc(x0, y0, h, 0, np.pi / 2, hw, col)               # TL corner
        arc(x0 + c, y0 + c, h, np.pi, 1.5 * np.pi, hw, col)  # BR corner
    else:
        arc(x0 + c, y0, h, np.pi / 2, np.pi, hw, col)        # TR
        arc(x0, y0 + c, h, 1.5 * np.pi, 2 * np.pi, hw, col)  # BL


G = 12
cell = W / G
for gy in range(G):
    for gx in range(G):
        x0, y0 = gx * cell, gy * cell
        col = amber if rng.random() < 0.22 else inkc
        if rng.random() < 0.30:                              # subdivide → multi-scale
            for sy in range(2):
                for sx in range(2):
                    tile(x0 + sx * cell / 2, y0 + sy * cell / 2, cell / 2,
                         amber if rng.random() < 0.22 else inkc)
        else:
            tile(x0, y0, cell, col)


def box(a):
    if a.ndim == 2:
        h, w = a.shape; return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))
    h, w, c = a.shape; return a.reshape(h // SS, SS, w // SS, SS, c).mean((1, 3))


inkd, cold = box(ink), box(colacc)
paper = np.array([0.94, 0.92, 0.86])
mottle = 1.0 + 0.015 * rng.standard_normal((H // SS, W // SS))[..., None]
rgb = paper[None, None, :] * mottle
rgb = rgb * (1 - inkd[..., None]) + cold * inkd[..., None]
write_png(os.path.join(OUT, "truchet.png"), (np.clip(rgb, 0, 1) * 255).astype(np.uint8))
print("wrote truchet.png")
