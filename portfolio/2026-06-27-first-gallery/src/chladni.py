#!/usr/bin/env python3
"""A Chladni figure: on a vibrating square plate, sand migrates to the nodal
lines where the standing wave is motionless. We superpose a few plate modes
and draw where the displacement is ~0. numpy + stdlib PNG.

    s(x,y) = sum_k a_k [cos(n_k pi x)cos(m_k pi y) - cos(m_k pi x)cos(n_k pi y)]
"""
import numpy as np
from pnglib import write_png

W = H = 1500
# (n, m, amplitude) modes — the antisymmetric combo gives the classic figures
MODES = [(4, 7, 1.0), (6, 3, 0.6), (9, 8, 0.45)]

lin = np.linspace(0, 1, W)
X, Y = np.meshgrid(lin, np.linspace(0, 1, H))

s = np.zeros((H, W))
for n, m, a in MODES:
    s += a * (np.cos(n * np.pi * X) * np.cos(m * np.pi * Y)
              - np.cos(m * np.pi * X) * np.cos(n * np.pi * Y))
s /= np.abs(s).max()

# sand accumulates where |s| is small: sharp bright nodal lines on deep indigo
line = np.exp(-(s ** 2) / (2 * 0.018 ** 2))
bg = np.array([0.03, 0.04, 0.10])
sand = np.array([0.98, 0.92, 0.78])
# faint tint of the antinodes (where the plate moves most) for depth
tint = np.array([0.10, 0.16, 0.30]) * (np.abs(s)[..., None])
rgb = bg + tint + (sand - bg) * line[..., None]
out = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
write_png("chladni.png", out)
print("wrote chladni.png")
