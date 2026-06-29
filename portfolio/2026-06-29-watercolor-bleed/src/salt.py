"""Salt bloom — pigment WICKED AWAY, not added.

A distinct watercolour technique: drop salt into a wet wash and each crystal pulls
pigment outward, leaving a pale starburst with a darker collected rim. Modelled by
SUBTRACTING density at scattered salt points (radial falloff) and adding a thin
collection ring just outside each — still fully subtractive light, earth palette,
one brooding payne's-grey + sienna wash so the pale blooms read against the dark.
"""
import numpy as np
from pnglib import write_png

H = W = 1000
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
rng = np.random.default_rng(5)


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


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def fbm(seed, oct=6):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(oct):
        out += amp * value_noise(int(freq), seed + o); tot += amp; amp *= .5; freq *= 2
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)


tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
img = np.ones((H, W, 3)) * np.array([249, 244, 233]) / 255.0
img *= (1.0 - 0.045 * (fbm(101) - 0.5)[..., None])

# one large brooding wash, off-centre, ragged edge
cx, cy = 0.54, 0.46
r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
wet = smoothstep(0.0, 0.18, fbm(3) * 0.5 + (0.40 - r) * 1.6)
wet = np.clip(wet * (0.6 + 0.8 * fbm(31)), 0, 1)
dens = (0.55 * blur(wet, 70) * wet + 1.7 * np.clip(wet - blur(wet, 6), 0, 1))
dens *= (0.6 + 0.8 * fbm(60, 5))                  # uneven wash, granular pooling
dens *= (0.65 + 0.7 * tooth)

# SALT: scatter crystals inside the wash; each wicks pigment away (subtract) with a
# faint darker collection ring just beyond the cleared centre.
salt = np.zeros((H, W)); ring = np.zeros((H, W))
n_salt = 70
for _ in range(n_salt):
    sx, sy = rng.uniform(0.18, 0.9), rng.uniform(0.08, 0.82)
    if wet[int(sy * (H - 1)), int(sx * (W - 1))] < 0.4:
        continue
    rad = rng.uniform(0.012, 0.05)
    d = np.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
    salt += np.exp(-(d / rad) ** 2)               # cleared (pale) core
    ring += np.exp(-((d - rad * 1.6) / (rad * 0.5)) ** 2)  # collected rim
dens = dens * (1.0 - 0.92 * np.clip(salt, 0, 1)) + 0.45 * ring * wet
dens = np.clip(dens, 0, None) * 1.25

PAYNES = np.array([1.55, 1.3, 1.0]); SIENNA = np.array([0.32, 1.0, 2.4])
# bias hue across the wash: sienna on one flank, payne's on the other (wet-on-wet pour)
mix = smoothstep(0.2, 0.8, nx)
k = PAYNES[None, None, :] * mix[..., None] + SIENNA[None, None, :] * (1 - mix)[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/salt.png", out)
print("wrote images/salt.png", out.shape)
