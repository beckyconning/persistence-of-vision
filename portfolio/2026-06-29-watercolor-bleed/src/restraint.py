"""Restraint — one pale wash, mostly paper. Answering my recurring over-density habit.

Every piece this session drifted dark (green→black, near hills→black). The counter:
a single DILUTE payne's-grey + sienna bloom, low ceiling on density so it stays
luminous, a couple of salt stars, off-centre with a large field of untouched paper.
The picture is in the mid-tones and the breathing white. Less is more.
"""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
rng = np.random.default_rng(4)


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
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (fbm(101) - 0.5)[..., None])

# one wash, set low and to the right-of-third, rising — lots of paper left & top
cx, cy = 0.62, 0.60
r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
wet = smoothstep(0.0, 0.16, fbm(13) * 0.5 + (0.26 - r) * 1.7)
wet = np.clip(wet * (0.55 + 0.85 * fbm(41)), 0, 1)
rim = np.clip(wet - blur(wet, 5), 0, 1)
dens = 0.32 * blur(wet, 55) * wet + 0.9 * rim          # LOW ceilings — stays pale
dens *= (0.6 + 0.7 * fbm(60, 5)) * (0.65 + 0.7 * tooth)

# two salt stars
salt = np.zeros((H, W))
for sx, sy, rad in [(0.60, 0.58, 0.035), (0.68, 0.66, 0.022)]:
    d = np.sqrt((nx - sx) ** 2 + (ny - sy) ** 2)
    salt += np.exp(-(d / rad) ** 2)
dens = dens * (1 - 0.9 * np.clip(salt, 0, 1))
dens = np.clip(dens, 0, None) * 0.85                    # global dilution cap

# pour: payne's at the cool base bleeding to sienna at the warm tip
mix = smoothstep(0.45, 0.78, ny)
PAYNES = np.array([1.45, 1.25, 1.0]); SIENNA = np.array([0.45, 1.0, 2.2])
k = SIENNA[None, None, :] * (1 - mix)[..., None] + PAYNES[None, None, :] * mix[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/restraint.png", out)
print("wrote images/restraint.png", out.shape)
