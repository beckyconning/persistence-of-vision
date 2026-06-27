#!/usr/bin/env python3
"""Voronoi 'stained glass': each pixel takes the colour of its nearest seed.
Cells darken toward their edges (distance to the *second*-nearest seed) for a
leaded-glass depth, and the seams between cells are drawn as dark cames.
numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W = H = 1400
NSITES = 150
RNG = np.random.default_rng(20260627)

# jewel-tone palette; each cell picks one
JEWELS = np.array([
    [0.78, 0.16, 0.28], [0.92, 0.45, 0.16], [0.96, 0.78, 0.25],
    [0.20, 0.55, 0.40], [0.13, 0.40, 0.55], [0.25, 0.30, 0.62],
    [0.55, 0.20, 0.50], [0.30, 0.62, 0.66], [0.85, 0.55, 0.55],
])

sx = RNG.uniform(0, W, NSITES)
sy = RNG.uniform(0, H, NSITES)
site_col = JEWELS[RNG.integers(0, len(JEWELS), NSITES)]

Y, X = np.mgrid[0:H, 0:W]
best = np.full((H, W), np.inf)      # nearest distance^2
second = np.full((H, W), np.inf)    # second-nearest distance^2
idx = np.zeros((H, W), np.intp)
for i in range(NSITES):
    d = (X - sx[i]) ** 2 + (Y - sy[i]) ** 2
    closer = d < best
    second = np.where(closer, best, np.minimum(second, d))
    idx = np.where(closer, i, idx)
    best = np.where(closer, d, best)

rgb = site_col[idx]
# depth: bright in cell interior, darker near the boundary to the next cell
edge = np.sqrt(second) - np.sqrt(best)        # 0 at the seam, large in interior
shade = np.clip(edge / 26.0, 0, 1)
shade = 0.35 + 0.65 * np.power(shade, 0.6)
rgb = rgb * shade[..., None]
# dark cames right on the seams
came = (edge < 1.4)
rgb[came] = [0.05, 0.04, 0.07]

out = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
write_png("voronoi.png", out)
print("wrote voronoi.png")
