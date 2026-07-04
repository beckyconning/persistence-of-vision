"""
Strange attractor — a chaotic dynamical system rendered as a DENSITY FIELD. New technique for the
corpus (not packing, not flow-field streamlines, not hard-edge planes): iterate a Clifford map for
millions of steps, accumulate where the orbit lands into a fine histogram, then log-map that density
to a luminous palette. The filaments emerge from the maths — nobody places them.

  x' = sin(a·y) + c·cos(a·x)
  y' = sin(b·x) + d·cos(b·y)

Palette: a cold-to-hot LUMINANCE ramp on a near-black ground — rarely-visited regions glow faint
indigo, the dense caustic folds burn up through teal/cyan to near-white. Density (not a stroke) IS
the image, so the structure reads as light through a fold rather than drawn lines.
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1400, 1000
N = 4_000_000          # orbit steps (single true orbit)
a, b, c, d = -1.7, 1.8, -1.9, -0.4   # a classic Clifford parameter set (rich folds)

# A recurrence can't be numpy-vectorised (each step needs the prior). math.sin/cos on Python floats
# is the fast path for a scalar loop — ~4M iterations in a few seconds.
sin, cos = math.sin, math.cos
xs = np.empty(N); ys = np.empty(N)
px, py = 0.1, 0.1
for k in range(N):
    nx = sin(a * py) + c * cos(a * px)
    ny = sin(b * px) + d * cos(b * py)
    xs[k] = nx; ys[k] = ny
    px, py = nx, ny

# map orbit coords (~[-2,2]) to pixels
xmin, xmax = xs.min(), xs.max(); ymin, ymax = ys.min(), ys.max()
gx = ((xs - xmin) / (xmax - xmin) * (W - 1)).astype(np.int32)
gy = ((ys - ymin) / (ymax - ymin) * (H - 1)).astype(np.int32)
dens = np.zeros((H, W), np.float64)
np.add.at(dens, (gy, gx), 1.0)

# log-normalise density
d_log = np.log1p(dens)
d_log /= d_log.max()

# luminance ramp: indigo -> teal -> cyan -> white on near-black
stops = np.array([
    [0.02, 0.03, 0.06],   # ground / unvisited
    [0.15, 0.13, 0.38],   # faint indigo
    [0.10, 0.45, 0.55],   # teal
    [0.35, 0.82, 0.85],   # cyan
    [0.95, 0.98, 1.00],   # near-white caustics
])
t = d_log * (len(stops) - 1)
i0 = np.clip(t.astype(int), 0, len(stops) - 2)
f = (t - i0)[..., None]
img = stops[i0] + (stops[i0 + 1] - stops[i0]) * f
img[dens == 0] = stops[0]     # keep unvisited pure ground

np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "clifford.png"), (img * 255).astype(np.uint8))
k = 3; hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/clif_prev.png", (prev * 255).astype(np.uint8))
print(f"wrote clifford.png (orbit {N:,})")
