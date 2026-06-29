"""Wash-land — a wet-on-wet watercolour landscape (depiction via the engine's strength).

The botanical taught: this medium does broad WASHES, not fiddly line-work. So:
receding hill bands as soft sienna/payne's washes, each a thresholded-fbm ridge with
a wet (bleeding) lower edge and a granular body; ATMOSPHERIC perspective (far = paler
+ cooler + higher on the sheet), luminous PAPER mist left between bands. High-key,
lots of untouched paper. Subtractive throughout — no glow, no dusk gradient.
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


def value_noise(scale, seed, aniso=1):
    rng = np.random.default_rng(seed)
    g = rng.random((max(2, scale // aniso), scale))
    yi = (ys / H * (g.shape[0] - 1)).astype(int); xi = (xs / W * (g.shape[1] - 1)).astype(int)
    return blur(g[yi, xi], max(1, W // scale // 2))


def ridge(seed, amp, base, rough=4):
    """A 1-D horizon line y(x) in [0,1] image coords, low base = higher on sheet."""
    line = np.zeros(W); a = 1.0; tot = 0.0; f = rough
    for o in range(5):
        r = np.random.default_rng(seed + o).random(int(f))
        xi = (np.arange(W) / W * (len(r) - 1)).astype(int)
        line += a * np.interp(np.arange(W), np.linspace(0, W, len(r)), r)
        tot += a; a *= 0.5; f *= 2
    line /= tot
    return base + amp * (line - 0.5)


tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
img = np.ones((H, W, 3)) * np.array([250, 246, 236]) / 255.0
img *= (1.0 - 0.03 * (value_noise(40, 101) - 0.5)[..., None])

PAYNES = np.array([1.55, 1.3, 1.0]); SIENNA = np.array([0.5, 1.05, 2.3])

# bands from far (high, pale, cool) to near (low, dark, warm). horizon ~0.62
bands = [
    (0.40, 0.030, 0.32, PAYNES, 0.7),   # farthest ridge
    (0.48, 0.040, 0.55, PAYNES * 0.8 + SIENNA * 0.2, 1.0),
    (0.57, 0.055, 0.85, PAYNES * 0.55 + SIENNA * 0.45, 1.6),
    (0.69, 0.075, 1.25, SIENNA * 0.7 + PAYNES * 0.3, 2.2),  # nearest hill (warm, dark)
]
for i, (base, amp, strength, k, dens_lo) in enumerate(bands):
    horizon = ridge(10 + i * 7, amp, base, rough=4 + i)        # per-column ridge height
    hy = np.interp(np.arange(W), np.arange(W), horizon)
    below = ny - hy[None, :]                                    # >0 below the ridge
    mask = np.clip(below / 0.012, 0, 1)                         # crisp ridge top (dry edge)
    # the wash fades downward as pigment settles toward the wet base; granular body
    body = mask * np.exp(-np.clip(below, 0, None) * 2.2) * (0.4 + 0.9 * (0.65 + 0.7 * tooth))
    wetbase = mask * np.clip(below, 0, 0.05) / 0.05 * 0.5       # darker pooled lower edge
    dens = strength * (body * 0.9 + wetbase)
    # mist: thin out where a soft noise says fog hangs (paper shows through)
    mist = blur(value_noise(7, 200 + i), 30)
    dens *= (0.55 + 0.7 * np.clip(mist + (0.3 if i == len(bands) - 1 else 0.0), 0, 1))
    dens = blur(dens, 2)
    img *= np.exp(-np.clip(dens, 0, None)[..., None] * k[None, None, :])

# a faint wash sky: very dilute cool wash up top, bleeding down to the far ridge
sky = np.clip((0.42 - ny) / 0.42, 0, 1) ** 1.4 * (0.25 + 0.3 * blur(value_noise(6, 7), 25))
img *= np.exp(-sky[..., None] * (PAYNES * 0.5)[None, None, :])

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/washland.png", out)
print("wrote images/washland.png", out.shape)
