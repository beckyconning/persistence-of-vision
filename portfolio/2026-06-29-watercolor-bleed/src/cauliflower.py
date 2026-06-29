"""Cauliflower — backruns / blooms. Water dropped into a drying wash.

The most iconic watercolour 'accident': a drop of water hits a damp wash and pushes
pigment OUTWARD into a hard, jagged, feathered ring (the 'cauliflower' / backrun),
leaving a pale cleared centre. Modelled as: cleared core (subtract) + a SHARP ring
whose radius is angularly jittered (the feathered, dendritic blossom edge), several
blooms of different sizes overlapping in one sienna+payne's wash. Granular, on paper.
"""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
rng = np.random.default_rng(6)


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
img *= (1.0 - 0.04 * (fbm(101) - 0.5)[..., None])

# a soft mid-tone wash to bloom INTO, off-centre, ragged
cx, cy = 0.5, 0.47
r0 = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
wet = smoothstep(0.0, 0.18, fbm(13) * 0.5 + (0.36 - r0) * 1.6)
wet = np.clip(wet * (0.6 + 0.8 * fbm(41)), 0, 1)
dens = (0.5 * blur(wet, 50) * wet + 0.5 * np.clip(wet - blur(wet, 6), 0, 1)) * (0.6 + 0.8 * fbm(60, 5))

# blooms: cleared centre + a sharp, angularly-jittered feathered ring
for _ in range(8):
    bx, by = rng.uniform(0.28, 0.72), rng.uniform(0.22, 0.66)
    if wet[int(by * (H - 1)), int(bx * (W - 1))] < 0.45:
        continue
    R = rng.uniform(0.04, 0.115)
    dx, dy = nx - bx, ny - by
    rr = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    rg = np.random.default_rng(int(rng.integers(1e6)))
    # jagged ring radius: sum of angular harmonics → the feathered blossom outline
    jit = 1.0 + 0.16 * sum((0.6 ** k) * np.sin((k + 3) * ang + rg.uniform(0, 6.28)) for k in range(5))
    Rj = R * jit
    core = smoothstep(Rj, Rj * 0.5, rr)                 # pale cleared interior
    ring = np.exp(-((rr - Rj) / (R * 0.10)) ** 2)       # hard pigment rim
    dens = dens * (1 - 0.85 * core) + 1.3 * ring * wet

dens = np.clip(dens, 0, None) * (0.65 + 0.7 * tooth) * 1.15

mix = smoothstep(0.25, 0.75, ny)
PAYNES = np.array([1.5, 1.28, 1.0]); SIENNA = np.array([0.42, 1.0, 2.35])
k = SIENNA[None, None, :] * (1 - mix)[..., None] + PAYNES[None, None, :] * mix[..., None]
img *= np.exp(-dens[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/cauliflower.png", out)
print("wrote images/cauliflower.png", out.shape)
