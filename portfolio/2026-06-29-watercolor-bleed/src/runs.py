"""Runs — pigment running DOWN a tilted wet sheet (gravity). Fixes the too-round edge.

New sub-technique: anisotropic downward advection — each step the pigment is pushed
down (roll + vertical-biased blur) within the wet paper, modulated by vertical streak
noise so it breaks into distinct RUNS with a ragged, dripping lower edge (the deckle
/ irregular silhouette the round blooms lacked). A cool payne's curtain over a warm
sienna ground at the base where the runs pool. High negative space up top.
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


def blur(a, rx, ry=None):
    ry = rx if ry is None else ry
    for _ in range(3):
        a = _box1d(a, ry, 0); a = _box1d(a, rx, 1)
    return a


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def fbm(seed, oct=6):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(oct):
        out += amp * value_noise(int(freq), seed + o); tot += amp; amp *= .5; freq *= 2
    return out / tot


tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
img = np.ones((H, W, 3)) * np.array([250, 246, 237]) / 255.0
img *= (1.0 - 0.03 * (fbm(101) - 0.5)[..., None])

# wet sheet: a broad band across the upper-middle, wet all the way down (so runs travel)
top = 0.22 + 0.04 * np.interp(np.arange(W), np.linspace(0, W, 24), np.random.default_rng(2).random(24))
wet = np.clip((ny - top[None, :]) / 0.02, 0, 1)              # wet below an irregular top line
wet *= np.clip((0.95 - ny) / 0.3, 0, 1)                      # dries toward the bottom margin
wet = np.clip(wet * (0.7 + 0.6 * fbm(31)), 0, 1)

# vertical streak field — where runs prefer to travel
streak = 0.35 + 0.9 * blur(value_noise(60, 77), 1, 14)      # tall thin features

# seed: a heavy charged band near the top of the wet sheet
seed = np.exp(-((ny - (top + 0.04)[None, :]) / 0.045) ** 2) * (0.9 + 0.7 * fbm(50))
# per-column drip REACH/decay: streaky columns run far, others barely move.
decay = 0.955 + 0.043 * streak / (streak.max() + 1e-9)      # per-pixel ~[0.955,0.998]
# max-drip: pigment falls and decays; can't collapse (it's a running maximum)
p = seed.copy()
for _ in range(220):
    p = np.maximum(p, np.roll(p, 1, axis=0) * decay)        # extend downward
p = p * wet                                                 # only on the wet sheet
p = blur(p, 1, 2)                                           # soften the runs a touch
p += 0.06 * np.clip(wet - blur(wet, 4), 0, 1) * blur(p, 3)  # edge cling at the sheet rim
p = np.clip(p, 0, None) * (0.6 + 0.7 * tooth) * 1.3

# colour: sienna where it pooled low/heavy, payne's in the thinner upper curtain
heavy = blur(p, 6)
mix = np.clip(ny * 0.6 + 0.4 * (1 - heavy / (heavy.max() + 1e-6)), 0, 1)
PAYNES = np.array([1.5, 1.28, 1.0]); SIENNA = np.array([0.45, 1.0, 2.3])
k = PAYNES[None, None, :] * mix[..., None] + SIENNA[None, None, :] * (1 - mix)[..., None]
img *= np.exp(-p[..., None] * k)

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/runs.png", out)
print("wrote images/runs.png", out.shape)
