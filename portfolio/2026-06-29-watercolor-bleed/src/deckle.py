"""Deckle — a stain with a genuinely TORN, irregular silhouette.

Answers the one critique that recurred all session: blob washes kept coming out
egg-/oval-perfect on the outer edge. Fix = DOMAIN WARP — sample the wet-field's
defining noise at warped coordinates (offset by a second noise field), so the
boundary folds, bays and peninsulas form: a ragged wet-into-wet stain / torn paper
edge, not a circle. Restrained sienna+payne's pour inside, granular, big paper.
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


def value_noise_at(u, v, scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    ui = np.clip((u * (scale - 1)), 0, scale - 1).astype(int)
    vi = np.clip((v * (scale - 1)), 0, scale - 1).astype(int)
    return blur(g[vi, ui], max(1, W // scale // 2))


def fbm_at(u, v, seed, oct=6):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(oct):
        out += amp * value_noise_at(u, v, int(freq), seed + o); tot += amp; amp *= .5; freq *= 2
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)


tooth = 0.5 + 0.5 * value_noise_at(nx, ny, W // 3, 9)
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (fbm_at(nx, ny, 101) - 0.5)[..., None])

# DOMAIN WARP: displace sampling coords by two noise fields -> folded coastline
wx = fbm_at(nx, ny, 211, 5) - 0.5
wy = fbm_at(nx, ny, 233, 5) - 0.5
amp = 0.32
uu, vv = nx + amp * wx, ny + amp * wy

cx, cy = 0.52, 0.5
r0 = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
field = fbm_at(uu, vv, 7, 6) * 0.55 + (0.30 - r0) * 1.7      # warped -> torn edge
wet = smoothstep(0.0, 0.12, field)
wet = np.clip(wet * (0.7 + 0.5 * fbm_at(uu, vv, 41, 5)), 0, 1)

dens = (0.32 * blur(wet, 55) * wet + 0.85 * np.clip(wet - blur(wet, 6), 0, 1))
dens *= (0.6 + 0.8 * fbm_at(uu, vv, 60, 5)) * (0.65 + 0.7 * tooth)
dens = np.clip(dens, 0, None) * 1.05

mix = smoothstep(0.25, 0.75, ny)
SIENNA = np.array([0.42, 1.0, 2.3]); PAYNES = np.array([1.5, 1.28, 1.0])
k = SIENNA[None, None, :] * (1 - mix)[..., None] + PAYNES[None, None, :] * mix[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/deckle.png", out)
print("wrote images/deckle.png", out.shape)
