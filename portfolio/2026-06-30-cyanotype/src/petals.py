"""Cyanotype — tone from TRANSLUCENCY ALONE (the frontier the dragonfly opened). No opaque
blocks: every element is a thin pressed petal that passes most light. Where petals OVERLAP,
two membranes stack → more light blocked → paler. So the image is built from depth, not edges:
a scatter of translucent leaves/petals whose crossings glow whiter, like pressed flowers laid
in layers on the sensitised paper. Beer–Lambert-ish: transmission multiplies per layer.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis); cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


# OPTICAL DEPTH accumulator: each translucent petal ADDS a little depth (more depth = more
# blocked light = whiter). Overlaps sum → crossings are the brightest.
depth = np.zeros((H, W))
veins = np.zeros((H, W))   # faint darker midrib per petal (toward blue)
rg = np.random.default_rng(7)


def petal(cx, cy, ang, length, width, dens):
    """A thin leaf membrane: each one contributes `dens` optical depth inside its area, with a
    soft feathered edge so layering reads as gradient, not hard cards."""
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    s = np.clip(u / length, 0, 1)
    halfw = width * np.sqrt(np.clip(s * (1.05 - s), 0, 1)) * 2.0  # leaf/ovate profile
    inside = (u > 0) & (u < length)
    # soft membrane: 1 at center spine, feathering to 0 at the edge (translucent rim)
    body = np.clip(1 - (np.abs(v) / (halfw + 1e-6)) ** 1.6, 0, 1) * inside
    depth[:] += dens * body
    # midrib: a faint blue hairline ALONG THIS PETAL ONLY — gate by its own body so it never
    # rides across other petals or empty paper (the overshoot bug). Fade out near the soft tip.
    rib = np.clip((0.0015 - np.abs(v)) / 0.0011, 0, 1) * inside * (s < 0.92) * (body > 0.35)
    veins[:] = np.maximum(veins, rib)


# A loose bouquet: several rosettes of petals + scattered single leaves, overlapping.
def rosette(cx, cy, n, length, width, dens, phase=0.0):
    for k in range(n):
        a = phase + k / n * 2 * np.pi + rg.uniform(-0.06, 0.06)
        petal(cx, cy, a, length * rg.uniform(0.85, 1.1), width * rg.uniform(0.85, 1.12), dens)


rosette(0.40, 0.44, 7, 0.30, 0.060, 0.55, phase=0.2)
rosette(0.62, 0.58, 6, 0.26, 0.055, 0.55, phase=0.9)
rosette(0.52, 0.30, 5, 0.20, 0.048, 0.50, phase=0.4)
# scattered drifting single leaves to break the symmetry and create stray overlaps
for _ in range(14):
    cx, cy = rg.uniform(0.12, 0.88), rg.uniform(0.12, 0.88)
    petal(cx, cy, rg.uniform(0, 2 * np.pi), rg.uniform(0.12, 0.24), rg.uniform(0.03, 0.05), 0.5)

depth[:] = blur(depth, 2)  # soft contact
# transmission: each unit of depth blocks light multiplicatively (Beer–Lambert)
# block fraction in [0,1): more layers → closer to 1 (white). Single petal ~0.42, double ~0.66.
block = 1 - np.exp(-0.9 * depth)

# ---- compose ----
expo = 0.74 + 0.40 * blur(vnoise(7, 5), 26) + 0.08 * (1 - ny)
expo = np.clip(expo, 0, 1)
deep = np.array([0.05, 0.19, 0.37])
pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + np.array([0.10, 0.26, 0.45])[None, None, :] * (1 - expo)[..., None]

m = block[..., None]
img = blue * (1 - m) + pale * m
# (midribs removed — on faint single-layer petals they stranded as scratchy blue lines;
# the translucency-stack glow is the subject, veins fought it. veins[] left computed, unused.)
# the characteristic leak-halo at the very faintest petal rims
halo = (blur(block, 7) - block).clip(0, 1)[..., None]
img = img * (1 - 0.35 * halo) + blue * (0.35 * halo)
img *= (1 - 0.04 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/petals.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/petals.png")
