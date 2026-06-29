"""Botanical — a watercolour sprig. The new medium pulled toward DEPICTION.

Leaves are oriented bleed-washes (rotated elongated wet masks) with a SUBTRACTED
central vein + side veins (the paper shows through where the brush left it), pooled
darker at the leaf edge and tip. A thin ink stem ties them into a sprig. Off-centre,
rising from the lower-left into open paper. Subtractive pigment throughout.
"""
import numpy as np
from pnglib import write_png

H = W = 1000
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


tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
img = np.ones((H, W, 3)) * np.array([249, 244, 233]) / 255.0
img *= (1.0 - 0.045 * (fbm(101) - 0.5)[..., None])

SAP = np.array([1.5, 0.62, 1.95]); OLIVE = np.array([1.15, 0.85, 2.3]); SIENNA = np.array([0.4, 1.05, 2.4])


def leaf(cx, cy, ang, length, width, k, seed, curl=0.0):
    ca, sa = np.cos(-ang), np.sin(-ang)
    u = (nx - cx) * ca - (ny - cy) * sa
    v = (nx - cx) * sa + (ny - cy) * ca
    v = v - curl * (u ** 2) / max(length, 1e-3)          # gentle curve to the blade
    # pointed-ellipse leaf: width tapers to the tip
    taper = np.clip(1 - (u / length) ** 2, 0, 1)
    blade = np.exp(-(v / (width * (0.25 + 0.75 * np.sqrt(taper + 1e-6)))) ** 2) * (np.abs(u) < length)
    blade *= taper ** 0.6
    wet = np.clip(blade * (0.8 + 0.3 * fbm(seed, 4)), 0, 1)
    interior = blur(wet, 16) * wet
    rim = np.clip(wet - blur(wet, 5), 0, 1)               # darker edge/tip pooling
    dens = 0.5 * interior + 1.5 * rim
    # veins: pale (paper shows) — a midrib + a few angled laterals
    midrib = np.exp(-(v / (width * 0.10)) ** 2) * (np.abs(u) < length * 0.96)
    lat = np.zeros((H, W))
    for s in np.linspace(-length * 0.7, length * 0.7, 7):
        lv = v - 0.45 * (u - s)                            # diagonal lateral vein
        lat += np.exp(-(lv / (width * 0.07)) ** 2) * (np.abs(u - s) < length * 0.28)
    veins = np.clip(midrib + 0.6 * lat, 0, 1) * (blade > 0.05)
    dens = dens * (1 - 0.8 * veins)
    dens *= (0.65 + 0.7 * tooth)
    return np.clip(dens, 0, None)


# a sprig rising from lower-left, leaves alternating, into open upper-right paper
leaves = [
    leaf(0.30, 0.74, 2.55, 0.20, 0.075, SAP,    11, curl=0.15),
    leaf(0.40, 0.60, 2.05, 0.235, 0.085, SAP,    23, curl=-0.18),
    leaf(0.34, 0.52, 2.75, 0.165, 0.06, OLIVE,  31, curl=0.2),
    leaf(0.49, 0.46, 1.7, 0.255, 0.09, SAP,    43, curl=0.12),
    leaf(0.45, 0.36, 2.25, 0.15, 0.055, OLIVE,  57, curl=-0.15),
    leaf(0.57, 0.33, 1.5, 0.175, 0.065, SIENNA, 69, curl=0.18),
]
for d, (_, _, _, _, _, k, *_), in zip(leaves, [
    (0.30, 0.74, 2.55, 0.20, 0.075, SAP), (0.40, 0.60, 2.05, 0.235, 0.085, SAP),
    (0.34, 0.52, 2.75, 0.165, 0.06, OLIVE), (0.49, 0.46, 1.7, 0.255, 0.09, SAP),
    (0.45, 0.36, 2.25, 0.15, 0.055, OLIVE), (0.57, 0.33, 1.5, 0.175, 0.065, SIENNA)]):
    img *= np.exp(-d[..., None] * k[None, None, :])

# thin ink stem: a curved dark line from base up through the leaf joins
t = np.linspace(0, 1, 400)
stx = 0.30 + 0.27 * t + 0.04 * np.sin(t * 3)
sty = 0.80 - 0.50 * t
stem = np.zeros((H, W))
for px, py in zip(stx, sty):
    stem += np.exp(-(((nx - px) ** 2 + (ny - py) ** 2) / (2 * 0.006 ** 2)))
stem = np.clip(stem, 0, 1) * (0.7 + 0.6 * tooth)
img *= np.exp(-stem[..., None] * np.array([1.4, 1.5, 1.7])[None, None, :])

out = np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/botanical.png", out)
print("wrote images/botanical.png", out.shape)
