"""
Chladni mode atlas — the capstone. A 4×4 grid sweeping the (n,m) mode-pair space, each panel the
nodal set of one resonance of the square plate. Reading left→right, top→bottom the modes climb, so
the plate goes from a few broad quiet curves to a dense lattice — the whole family of a vibrating
plate in one frame. Same zero-set render as chladni.py; only (n,m) varies per cell.
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
P = 300            # per-panel resolution
G = 6              # gutter
SIGMA = 0.016
pi = math.pi
xs = np.linspace(0.0, 1.0, P)
X, Y = np.meshgrid(xs, xs)
r = np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2) / 0.72
vign = np.clip(1.12 - 0.5 * (r ** 3), 0.0, 1.0)[..., None]

plate = np.array([0.02, 0.03, 0.06])
sand = np.array([0.85, 0.93, 0.99])
glow = np.array([0.22, 0.55, 0.78])

# 16 mode-pairs, climbing in complexity
PAIRS = [
    (2, 1), (3, 1), (3, 2), (4, 1),
    (4, 3), (5, 2), (5, 3), (6, 1),
    (6, 4), (7, 3), (7, 5), (8, 3),
    (8, 6), (9, 5), (10, 4), (11, 7),
]

def panel(n, m):
    s = (np.cos(n * pi * X) * np.cos(m * pi * Y)
         - np.cos(m * pi * X) * np.cos(n * pi * Y))
    s /= max(abs(s.min()), abs(s.max()))
    band = np.power(np.exp(-(s * s) / (2 * SIGMA * SIGMA)), 0.8)
    b = band[..., None]
    img = plate + b * (sand - plate)
    img += (np.power(band, 3)[..., None]) * (glow - plate) * 0.4
    return np.clip(img * vign, 0, 1)

ground = np.array([0.015, 0.02, 0.03])
canvas = np.ones((4 * P + 5 * G, 4 * P + 5 * G, 3)) * ground
for i, (n, m) in enumerate(PAIRS):
    rr, cc = divmod(i, 4)
    y0, x0 = G + rr * (P + G), G + cc * (P + G)
    canvas[y0:y0 + P, x0:x0 + P] = panel(n, m)

write_png(os.path.join(OUT, "chladni_grid.png"), (canvas * 255).astype(np.uint8))
k = 4
hh, ww = (canvas.shape[0] // k) * k, (canvas.shape[1] // k) * k
prev = canvas[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/chladni_grid_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote chladni_grid.png ({canvas.shape[1]}x{canvas.shape[0]}, 16 modes)")
