"""
Chladni figure — a NEW technique for the corpus: the standing-wave nodal set of a vibrating
square plate. Bow a metal plate at a resonant frequency, scatter sand on it, and the sand
migrates to the NODES — the curves that don't move. Those curves are the zero set of a plate
vibration mode; here the superposition

    s(x,y) = cos(nπx)·cos(mπy) − cos(mπx)·cos(nπy)

whose |s|≈0 locus is the nodal pattern. Nobody draws the curves — they are where the physics
goes quiet. Rendered as luminous "sand" (a soft band around s=0) on a dark plate.

Palette: deep indigo plate → pale warm sand at the nodes, with the sand brightest where the
nodal lines cross (the deepest quiet). Distinct from the corpus's density/particle work: this
is a FIELD ZERO-SET, not an accumulation.
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
N = 1200
# Superpose a few resonant mode-pairs (a real driven plate near resonance excites neighbours),
# weighted so one dominates — richer than a single pair without losing the symmetry.
MODES = [((11, 6), 1.0), ((8, 3), 0.5)]
SIGMA = 0.012   # thin, crisp nodal filigree

xs = np.linspace(0.0, 1.0, N)
X, Y = np.meshgrid(xs, xs)
pi = math.pi
s = np.zeros((N, N))
for (n, m), w in MODES:
    s += w * (
        np.cos(n * pi * X) * np.cos(m * pi * Y)
        - np.cos(m * pi * X) * np.cos(n * pi * Y)
    )
s /= max(abs(s.min()), abs(s.max()))  # normalise to [-1,1]

# sand band: bright where |s| is small (near a node). Gaussian in s so lines are soft-edged.
band = np.exp(-(s * s) / (2 * SIGMA * SIGMA))
band = np.power(band, 0.8)

# indigo plate → warm sand ramp
plate = np.array([0.02, 0.03, 0.05])
sand = np.array([0.80, 0.92, 0.98])   # cool silver sand
glow = np.array([0.20, 0.55, 0.75])   # faint violet halo just off the nodes
b = band[..., None]
img = plate + b * (sand - plate)
img += (np.power(band, 3)[..., None]) * (glow - plate) * 0.4  # halo where lines crowd
# subtle round-plate vignette
r = np.sqrt((X - 0.5) ** 2 + (Y - 0.5) ** 2) / 0.72
img *= np.clip(1.15 - 0.5 * (r ** 3), 0.0, 1.0)[..., None]
np.clip(img, 0, 1, out=img)

write_png(os.path.join(OUT, "chladni_crisp.png"), (img * 255).astype(np.uint8))
k = 3
hh, ww = (N // k) * k, (N // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/chladni_crisp_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote chladni_crisp.png ({N}x{N}, modes={MODES})")
