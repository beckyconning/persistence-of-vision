"""Confluence — two earth pigments bleeding into each other, wet-on-wet.

Piece 2, answering piece 1's self-critique:
  * Edges were inflated/balloon-like -> drive the wet front with a THRESHOLDED fbm,
    so the boundary is naturally ragged and FINGERED (dendritic bleed), and feather
    it with a multiplicative fine-noise front. No angular-harmonic blobs.
  * Back-runs were a repeated stamped 3-lobe motif -> interior variation now comes
    from diffusion + noise pools, never a reused shape.
  * Subject is the MIXING SEAM: a sap-green field and a raw-sienna field share a
    damp zone and bleed together; where they overlap the subtractive washes
    multiply into a deep umber. Lots of dry paper around them (negative space).
"""
import numpy as np
from pnglib import write_png

H = W = 1000
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis)
    cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - r, 0, n)
    hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64)
    shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    yi = (ys / H * (scale - 1)).astype(int)
    xi = (xs / W * (scale - 1)).astype(int)
    return blur(g[yi, xi], max(1, W // scale // 2))


def fbm(seed, octaves=6, lac=2.0, gain=0.5):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(octaves):
        out += amp * value_noise(int(freq), seed + o)
        tot += amp; amp *= gain; freq *= lac
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1)
    return t * t * (3 - 2 * t)


# ---- paper ----
paper_rgb = np.array([249, 244, 233], np.float64)
tooth = 0.5 + 0.5 * value_noise(W // 3, 9)            # granulation tooth
fibre = fbm(101, 6)
img = np.ones((H, W, 3)) * paper_rgb / 255.0
img *= (1.0 - 0.045 * (fibre - 0.5)[..., None])

# ---- a damp region (where both pigments can travel), ragged-edged ----
# radial falloff biased to a centre, modulated by fbm => fingered coastline
cx, cy = 0.46, 0.5
r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
field = fbm(7, 6) * 0.55 + (0.42 - r) * 1.6           # high in centre, noisy edge
wet = smoothstep(0.0, 0.18, field)                    # ragged wet island
front = 0.6 + 0.8 * fbm(33, 5)                          # feathered bleed front
wet = np.clip(wet * front, 0, 1)


def deposit(seed, bias_x):
    """A pigment source pooled toward one side of the wet field (bias_x in [0,1])."""
    rg = np.random.default_rng(seed)
    p = np.zeros((H, W))
    for _ in range(5):
        sx = bias_x + rg.uniform(-0.10, 0.10)
        sy = 0.5 + rg.uniform(-0.18, 0.18)
        rad = rg.uniform(0.05, 0.12)
        p += np.exp(-(((nx - sx) ** 2 + (ny - sy) ** 2) / (2 * rad * rad)))
    return p * wet


def bleed(p, iters=26):
    """Diffuse pigment, confined to the wet field, accumulating at the drying edge."""
    edge = np.clip(wet - blur(wet, 6), 0, 1)           # the wet boundary ring
    flow = 0.7 + 0.6 * fbm(seed=int(p.sum()) % 9999 + 1, octaves=5)  # uneven channels
    for _ in range(iters):
        p = wet * blur(p, 4) * flow + (1 - 0.0) * 0     # spread only into wet, in channels
        p += 0.06 * edge * blur(p, 8)                   # pigment migrates to the edge
    p = blur(p, 2)
    p *= (0.65 + 0.7 * tooth)                            # granulation
    return np.clip(p, 0, None)


SAP_GREEN  = np.array([1.5, 0.7, 1.95])
RAW_SIENNA = np.array([0.35, 1.05, 2.45])

pg = bleed(deposit(11, 0.33)) * 1.5
ps = bleed(deposit(29, 0.62)) * 1.5

for p, k in ((pg, SAP_GREEN), (ps, RAW_SIENNA)):
    img *= np.exp(-p[..., None] * k[None, None, :])

# a faint settling shadow under the heaviest pigment (paper buckling cue)
heavy = blur(np.clip(pg + ps - 0.6, 0, 1), 14)
img *= (1.0 - 0.05 * heavy)[..., None]

out = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/confluence.png", out)
print("wrote images/confluence.png", out.shape)
