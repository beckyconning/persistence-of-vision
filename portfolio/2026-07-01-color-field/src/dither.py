"""
Bayer-dithered colour gradient — a new technique to close the session.

A smooth diagonal gradient between two session hues, rendered with ZERO blending:
every pixel is one of the two flat colours, chosen by thresholding the gradient
against a tiled 8×8 Bayer matrix (ordered dithering). The eye fuses the stipple
into a gradient — tone from arrangement, not mixing (the print/pixel lineage), now
in colour. Distinct from every soft/flat piece here: the transition IS the texture.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1100, 760

# 8×8 Bayer threshold matrix (recursive construction), normalised to (0,1)
def bayer(n):
    if n == 1:
        return np.array([[0.0]])
    b = bayer(n // 2)
    return np.block([[4 * b, 4 * b + 2], [4 * b + 3, 4 * b + 1]]) / (n * n)

B = bayer(8)
yy, xx = np.mgrid[0:H, 0:W]
thresh = B[yy % 8, xx % 8]                       # tiled dither thresholds

# gradient value 0→1 on a diagonal, with a gentle wave so bands aren't straight
u, v = xx / W, yy / H
g = np.clip(u + 0.10 * np.sin(v * 5 * np.pi), 0, 1)   # L→R sweep, gentle wave

hotA = np.array([0.93, 0.30, 0.42])              # raspberry
coolB = np.array([0.18, 0.52, 0.66])             # ocean blue
pick = (g > thresh)[..., None]                   # ordered-dither decision
img = np.where(pick, hotA[None, None, :], coolB[None, None, :])

write_png(os.path.join(OUT, "dither.png"), (np.clip(img, 0, 1) * 255).astype(np.uint8))
print("wrote dither.png")
