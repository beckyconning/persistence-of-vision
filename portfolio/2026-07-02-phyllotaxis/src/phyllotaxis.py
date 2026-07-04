"""
Phyllotaxis — the golden-angle spiral a sunflower/pinecone uses to pack seeds. Place point i at
angle i·137.507° (the golden angle, 360°/φ²) and radius c·√i. That single rule fills the disc with
NO gaps and NO preferred direction — the parastichy spirals (the visible arms) emerge for free,
their counts landing on Fibonacci numbers. Nobody places the arms; they are what the golden angle
forces. A parametric point-set — new to the corpus alongside the plate/field work.

Rendered as glowing seeds, hue cycling slowly with radius (a warm core → cool rim), each seed a
soft radial dab so the packing reads as light, not dots.
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 1200
N = 2600                      # seeds
GOLDEN = math.pi * (3.0 - math.sqrt(5.0))   # 137.507° in radians
C = 0.5 * min(W, H) / math.sqrt(N) * 0.92    # scale so the disc fills the frame

img = np.zeros((H, W, 3), np.float64)
yy, xx = np.mgrid[0:H, 0:W]

# warm-core → cool-rim ramp
def ramp(t):  # t in [0,1]
    a = np.array([1.00, 0.82, 0.42])   # gold
    b = np.array([0.90, 0.30, 0.45])   # rose
    c = np.array([0.30, 0.55, 0.95])   # blue
    if t < 0.5:
        u = t / 0.5
        return a + (b - a) * u
    u = (t - 0.5) / 0.5
    return b + (c - b) * u

for i in range(N):
    ang = i * GOLDEN
    rad = C * math.sqrt(i)
    cx = W / 2 + rad * math.cos(ang)
    cy = H / 2 + rad * math.sin(ang)
    t = i / (N - 1)
    col = ramp(t)
    dab = 5.5 + 3.5 * t            # seeds grow slightly outward
    # soft radial dab (local window for speed)
    x0, x1 = max(0, int(cx - 4 * dab)), min(W, int(cx + 4 * dab))
    y0, y1 = max(0, int(cy - 4 * dab)), min(H, int(cy + 4 * dab))
    if x0 >= x1 or y0 >= y1:
        continue
    d2 = (xx[y0:y1, x0:x1] - cx) ** 2 + (yy[y0:y1, x0:x1] - cy) ** 2
    g = np.exp(-d2 / (2 * dab * dab))
    img[y0:y1, x0:x1] += g[..., None] * col

# tone-map (additive glow → [0,1]) on near-black
img = 1.0 - np.exp(-1.6 * img)
np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "phyllotaxis.png"), (img * 255).astype(np.uint8))
k = 3
hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/phyllo_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote phyllotaxis.png ({W}x{H}, {N} seeds, golden angle)")
