"""Dry-brush — the opposite mark. Pigment catches only the paper-tooth peaks.

A scumble: a near-dry brush dragged over textured paper deposits only on the raised
tooth, leaving the valleys white — broken, scratchy, granular strokes. Density =
stroke * (tooth above a threshold), per stroke, a few directional drags crossing the
sheet. Still subtractive earth pigment, lots of paper. Ends the session on a mark
that is all texture and no bleed — the counter to every wet wash before it.
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


# fine tooth (high-freq) — the grain the dry brush rides
tooth = vn(W // 2, 9) * 0.6 + vn(W // 6, 12) * 0.4
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (vn(40, 101) - 0.5)[..., None])

SIENNA = np.array([0.42, 1.0, 2.3]); PAYNES = np.array([1.5, 1.28, 1.0]); UMBER = np.array([1.0, 1.7, 2.6])


def stroke(x0, y0, x1, y1, width, load, k, seed):
    """A dry drag from (x0,y0)->(x1,y1): broad soft band × tooth-peaks × fading load."""
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)     # param along stroke
    px, py = x0 + t * dx, y0 + t * dy
    dist = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    band = np.exp(-(dist / width) ** 2) * (t > 0) * (t < 1)
    fade = (1 - t) ** 0.7 * (0.7 + 0.6 * vn(80, seed))            # brush runs out of paint
    catch = np.clip((tooth - 0.5) / 0.32, 0, 1)                  # only tooth peaks take pigment
    dens = load * band * fade * catch
    img[:] = img * np.exp(-np.clip(dens, 0, None)[..., None] * k[None, None, :])


# a small set of crossing drags, off-centre, rising — gesture, not fill
stroke(0.18, 0.74, 0.74, 0.40, 0.055, 2.4, PAYNES, 1)
stroke(0.24, 0.80, 0.80, 0.50, 0.045, 2.0, SIENNA, 2)
stroke(0.30, 0.66, 0.66, 0.30, 0.035, 2.2, UMBER, 3)
stroke(0.20, 0.62, 0.58, 0.46, 0.030, 1.8, PAYNES, 4)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/drybrush.png", out)
print("wrote images/drybrush.png", out.shape)
