"""
Homage to Bridget Riley — Op-art wave bands (after "Fall" / "Current", 1963-64).

The third piece deliberately breaks the grid-of-line-figures formula the Molnar
and Mohr share: no grid, no discrete figures — instead CONTINUOUS filled bands of
black and white that warp, so the eye reads optical movement/shimmer off a static
image. A different lineage (perceptual Op art, not algorithmic plotter line) and a
different register (filled bands + curvature). The undulation frequency rises down
the field — the "fall" — and a slow horizontal phase warp makes the bands breathe.
Rendered at 3x and box-downscaled so the high-frequency band edges anti-alias
(otherwise they alias into false moire of the wrong kind).
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 3
W, H = 900 * SS, 1100 * SS

yy, xx = np.mgrid[0:H, 0:W].astype(float)
u = xx / W
v = yy / H

# phase field: vertical bands whose frequency GROWS toward the bottom (the fall),
# warped horizontally by a low-frequency sine so the columns bow and shimmer.
freq = 26 + 95 * v ** 2.2                         # bands per width, rising downward
warp = 0.16 * np.sin(2 * np.pi * (v * 1.5)) * np.sin(np.pi * u)   # gentle bow
phase = (u + warp) * freq * np.pi
band = np.sin(phase)

# soft threshold → near-crisp black/white bands with a hair of anti-alias
# (supersampling does the real AA; this keeps edges from being razor-hard)
t = np.clip(band / 0.06, -1, 1)
ink = (1 - t) / 2.0                               # 1=black band, 0=paper

# Riley monochrome: warm-white paper, cool near-black
paper = np.array([0.95, 0.94, 0.91])
inkc = np.array([0.08, 0.08, 0.10])
rgb = paper[None, None, :] * (1 - ink[..., None]) + inkc[None, None, :] * ink[..., None]


def box(a):
    h, w, c = a.shape
    return a.reshape(h // SS, SS, w // SS, SS, c).mean((1, 3))


out = np.clip(box(rgb), 0, 1)
write_png(os.path.join(OUT, "riley_fall.png"), (out * 255).astype(np.uint8))
print("wrote riley_fall.png  %dx%d" % (W // SS, H // SS))
