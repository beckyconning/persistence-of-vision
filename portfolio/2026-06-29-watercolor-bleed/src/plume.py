"""Plume — ink dropped into water. Strong domain warp + directional pull = tendrils.

Pushes deckle's edge fix to its conclusion: big warp amplitude and an upward
directional bias turn the round stain into a tendrilled PLUME with thin reaching
fingers and a torn silhouette — ink blooming in water. Payne's-grey core warming to
sienna at the dispersing tips, granular, rising off-centre into open paper.
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


def vn(u, v, scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    ui = np.clip(u * (scale - 1), 0, scale - 1).astype(int); vi = np.clip(v * (scale - 1), 0, scale - 1).astype(int)
    return blur(g[vi, ui], max(1, W // scale // 2))


def fbm(u, v, seed, oct=6):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(oct):
        out += amp * vn(u, v, int(freq), seed + o); tot += amp; amp *= .5; freq *= 2
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)


tooth = 0.5 + 0.5 * vn(nx, ny, W // 3, 9)
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (fbm(nx, ny, 101) - 0.5)[..., None])

# strong warp + vertical stretch (tendrils reach upward)
wx = fbm(nx, ny, 211, 6) - 0.5
wy = fbm(nx, ny, 233, 6) - 0.5
uu, vv = nx + 0.6 * wx, ny + 0.6 * wy

cx, cy = 0.46, 0.6
r = np.sqrt(((nx - cx) * 1.3) ** 2 + ((ny - cy) * 0.7) ** 2)  # vertically stretched
field = fbm(uu, vv, 7, 6) * 0.62 + (0.26 - r) * 1.7
wet = smoothstep(-0.04, 0.10, field)                          # lower thresh -> thin fingers
wet = np.clip(wet * (0.6 + 0.6 * fbm(uu, vv, 41, 5)), 0, 1)

dens = (0.40 * blur(wet, 45) * wet + 0.8 * np.clip(wet - blur(wet, 5), 0, 1))
dens *= (0.55 + 0.85 * fbm(uu, vv, 60, 5)) * (0.65 + 0.7 * tooth)
dens = np.clip(dens, 0, None) * 1.15

# core (dense) = cool payne's; dispersing tips (thin) = warm sienna
thin = 1 - smoothstep(0.15, 0.8, blur(dens, 8) / (dens.max() + 1e-9))
PAYNES = np.array([1.5, 1.28, 1.0]); SIENNA = np.array([0.42, 1.0, 2.3])
k = PAYNES[None, None, :] * (1 - thin)[..., None] + SIENNA[None, None, :] * thin[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/plume.png", out)
print("wrote images/plume.png", out.shape)
