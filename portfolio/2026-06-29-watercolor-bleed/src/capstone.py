"""Capstone — the picture, not a study. Composing the session's best techniques.

Restraint (high-key, low density, breathing paper) + ONE elegant wet-on-wet pour
(sienna shoulder bleeding to payne's-grey) + three deliberately placed cauliflower
blooms on a rule-of-thirds diagonal + a single salt star for a point of light. The
aim is composition and quiet, not a demo grid.
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

# main pour: an organic wash filling the upper-right two-thirds, soft ragged edge
cx, cy = 0.60, 0.42
r0 = np.sqrt(((nx - cx) * 1.15) ** 2 + ((ny - cy) * 0.9) ** 2)
wet = smoothstep(0.0, 0.2, fbm(13) * 0.5 + (0.34 - r0) * 1.6)
wet = np.clip(wet * (0.6 + 0.8 * fbm(41)), 0, 1)
dens = (0.30 * blur(wet, 60) * wet + 0.7 * np.clip(wet - blur(wet, 6), 0, 1))
dens *= (0.6 + 0.8 * fbm(60, 5))

# three blooms on a rising diagonal (rule-of-thirds nodes), one big two small
for bx, by, R, seed in [(0.40, 0.62, 0.10, 71), (0.58, 0.45, 0.135, 83), (0.70, 0.30, 0.07, 97)]:
    dx, dy = nx - bx, ny - by
    rr = np.sqrt(dx * dx + dy * dy); ang = np.arctan2(dy, dx)
    rg = np.random.default_rng(seed)
    jit = 1.0 + 0.15 * sum((0.6 ** k) * np.sin((k + 3) * ang + rg.uniform(0, 6.28)) for k in range(5))
    Rj = R * jit
    core = smoothstep(Rj, Rj * 0.5, rr)
    ring = np.exp(-((rr - Rj) / (R * 0.11)) ** 2)
    dens = dens * (1 - 0.8 * core) + 1.15 * ring * wet

# a single salt star — the point of light, upper-right third
ds = np.sqrt((nx - 0.72) ** 2 + (ny - 0.34) ** 2)
dens *= (1 - 0.9 * np.exp(-(ds / 0.03) ** 2))
dens = np.clip(dens, 0, None) * (0.65 + 0.7 * tooth) * 0.95

mix = smoothstep(0.2, 0.72, ny)                       # sienna shoulder -> payne's base
SIENNA = np.array([0.42, 1.0, 2.3]); PAYNES = np.array([1.5, 1.28, 1.0])
k = SIENNA[None, None, :] * (1 - mix)[..., None] + PAYNES[None, None, :] * mix[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/capstone.png", out)
print("wrote images/capstone.png", out.shape)
