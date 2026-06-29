"""Estuary — three earth pigments converging in one wet basin.

Piece 3, answering piece 2's critique:
  * density was so high the green read black -> tune deposit + k so each hue SURVIVES.
  * pigments sat adjacent, not overlapping -> ONE connected wet basin that all three
    bleed into, so the SUBTRACTIVE overlaps are the subject: green*sienna = olive,
    +payne's grey = deep umber, the triple core = near-black shadow. Multiplicative
    pigment, not additive — every overlap darkens and shifts hue the way real
    washes do. Keeps piece 2's granulation engine (the win).
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
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)],
                max(1, W // scale // 2))


def fbm(seed, octaves=6):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(octaves):
        out += amp * value_noise(int(freq), seed + o); tot += amp; amp *= 0.5; freq *= 2
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)


# paper
paper_rgb = np.array([249, 244, 233], np.float64)
tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
img = np.ones((H, W, 3)) * paper_rgb / 255.0
img *= (1.0 - 0.045 * (fbm(101) - 0.5)[..., None])

# one connected wet basin, ragged-edged, centred a touch low-left of centre
cx, cy = 0.47, 0.52
r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
wet = smoothstep(0.0, 0.16, fbm(7) * 0.5 + (0.34 - r) * 1.7)
wet = np.clip(wet * (0.6 + 0.8 * fbm(33, 5)), 0, 1)
edge = np.clip(wet - blur(wet, 6), 0, 1)


def deposit(seed, sx, sy):
    rg = np.random.default_rng(seed)
    p = np.zeros((H, W))
    for _ in range(4):
        ox, oy = sx + rg.uniform(-0.05, 0.05), sy + rg.uniform(-0.05, 0.05)
        rad = rg.uniform(0.06, 0.11)
        p += np.exp(-(((nx - ox) ** 2 + (ny - oy) ** 2) / (2 * rad * rad)))
    return p * wet


def bleed(p, seed, iters=24, dens=0.85):
    flow = 0.7 + 0.6 * fbm(seed + 200, 5)
    for _ in range(iters):
        p = wet * blur(p, 4) * flow
        p += 0.06 * edge * blur(p, 8)
    p = blur(p, 2) * (0.65 + 0.7 * tooth)
    return np.clip(p, 0, None) * dens


SAP_GREEN   = np.array([1.45, 0.65, 1.9])
RAW_SIENNA  = np.array([0.32, 1.0, 2.4])
PAYNES_GREY = np.array([1.55, 1.3, 1.0])

# three sources placed to share the basin centre -> heavy overlap
washes = [
    (bleed(deposit(11, 0.36, 0.42), 11, dens=0.8), SAP_GREEN),
    (bleed(deposit(29, 0.58, 0.50), 29, dens=0.8), RAW_SIENNA),
    (bleed(deposit(43, 0.47, 0.64), 43, dens=0.85), PAYNES_GREY),
]
for p, k in washes:
    img *= np.exp(-p[..., None] * k[None, None, :])

# settling shadow where pigment pooled deepest (paper buckle)
heavy = blur(np.clip(sum(p for p, _ in washes) - 0.8, 0, 1), 16)
img *= (1.0 - 0.05 * heavy)[..., None]

out = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/estuary.png", out)
print("wrote images/estuary.png", out.shape)
