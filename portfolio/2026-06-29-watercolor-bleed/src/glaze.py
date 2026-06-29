"""Glaze — wet-on-DRY layering. Hard-edged translucent washes that multiply.

The architectural counter to the organic bleeds: each glaze is a crisp-edged
transparent shape; subtractive multiply means OVERLAPS build up to richer, darker
hue (the core of transparent watercolour layering). Soft granular fills, hard
boundaries, a composed set of overlapping arcs/bands in earth pigments. Geometry
+ transparency, not diffusion.
"""
import numpy as np
from pnglib import write_png

H = W = 1100
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


def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


tooth = 0.5 + 0.5 * vn(W // 3, 9)
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (vn(40, 101) - 0.5)[..., None])

SIENNA = np.array([0.42, 1.0, 2.3]); PAYNES = np.array([1.5, 1.28, 1.0])
SAP = np.array([1.45, 0.65, 1.9]); UMBER = np.array([1.0, 1.7, 2.6])


def glaze_disc(cx, cy, R, load, k, edge=0.004):
    d = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    m = np.clip((R - d) / edge, 0, 1)                    # HARD edge (wet-on-dry)
    dens = load * m * (0.7 + 0.5 * tooth)                # granular flat fill
    img[:] = img * np.exp(-dens[..., None] * k[None, None, :])


def glaze_band(y0, y1, load, k):
    m = np.clip((ny - y0) / 0.004, 0, 1) * np.clip((y1 - ny) / 0.004, 0, 1)
    dens = load * m * (0.7 + 0.5 * tooth)
    img[:] = img * np.exp(-dens[..., None] * k[None, None, :])


# overlapping translucent discs (rule-of-thirds cluster) + two quiet bands
glaze_band(0.30, 0.34, 0.5, SIENNA)
glaze_band(0.66, 0.69, 0.45, PAYNES)
glaze_disc(0.40, 0.45, 0.20, 0.7, SIENNA)
glaze_disc(0.55, 0.50, 0.18, 0.7, PAYNES)
glaze_disc(0.48, 0.60, 0.155, 0.65, SAP)
glaze_disc(0.62, 0.62, 0.10, 0.7, UMBER)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/glaze.png", out)
print("wrote images/glaze.png", out.shape)
