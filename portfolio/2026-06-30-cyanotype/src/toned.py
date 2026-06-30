"""Cyanotype — TONED (the second-hue frontier). A finished cyanotype dipped in tannin (tea,
coffee, oak gall) bleaches the Prussian blue and re-deposits a warm brown/violet: the deep
exposed ground goes aubergine-to-sepia, the paper highlights warm to cream. So the palette is
a SPLIT-TONE (warm shadow + warm paper) instead of the cold blue/white. Subject: a single
arching botanical sprig with paired leaves + buds — a herbarium specimen.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
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


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


block = np.zeros((H, W))
nx2, ny2 = nx, ny


def stroke(x0, y0, x1, y1, w0, w1, soft=0.0035):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    w = w0 + (w1 - w0) * t
    return np.clip((w - d) / soft, 0, 1)


def leaf(cx, cy, ang, length, width):
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    s = np.clip(u / length, 0, 1)
    # lance-shaped: widest ~1/3 up, tapering to a point — *1.35 not *2.0 (was too round)
    halfw = width * np.sqrt(np.clip(s * (1.0 - s), 0, 1)) * 1.35 * (1.0 - 0.35 * s)
    inside = (u > 0) & (u < length)
    body = np.clip((halfw - np.abs(v)) / 0.0025, 0, 1) * inside
    block[:] = np.maximum(block, body)
    # a thin midrib gap (vein lets a sliver of ground through) — only where leaf is wide enough
    rib = (np.abs(v) < 0.0011) & inside & (s > 0.12) & (s < 0.92) & (halfw > 0.004)
    block[rib] *= 0.5


def bud(cx, cy, r):
    d = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    block[:] = np.maximum(block, np.clip((r - d) / 0.0035, 0, 1))


# arching main stem (a gentle S), bottom-left to upper-right
ts = np.linspace(0, 1, 80)
sx = 0.18 + 0.64 * ts
sy = 0.84 - 0.55 * ts - 0.10 * np.sin(ts * np.pi)
for i in range(len(ts) - 1):
    block[:] = np.maximum(block, stroke(sx[i], sy[i], sx[i + 1], sy[i + 1], 0.0045, 0.0018))

# paired leaves along the stem, alternating, shrinking toward the tip
rg = np.random.default_rng(3)
for t in np.linspace(0.10, 0.86, 6):
    i = int(t * (len(ts) - 1))
    # local stem direction
    j = min(i + 1, len(ts) - 1)
    ang = np.arctan2(sy[j] - sy[i], sx[j] - sx[i])
    llen = 0.20 * (1 - 0.5 * t) + 0.03
    lw = llen * 0.24
    for sgn in (+1, -1):
        la = ang + sgn * np.radians(48) + rg.uniform(-0.04, 0.04)
        leaf(sx[i], sy[i], la, llen, lw)

# a few buds near the tip
tipx, tipy = sx[-1], sy[-1]
for k, off in enumerate([(0.0, 0.0), (-0.03, -0.02), (0.025, -0.03), (0.0, -0.05)]):
    bud(tipx + off[0], tipy + off[1], 0.016 - 0.002 * k)

block[:] = blur(block, 2)
block[:] = np.clip(block, 0, 1)

# ---- compose: TONED split-tone ----
expo = 0.74 + 0.40 * blur(vnoise(7, 5), 26) + 0.10 * (1 - ny) + 0.04 * (nx - 0.5)
expo = np.clip(expo, 0, 1)
# toned shadow: not Prussian blue but a warm aubergine/sepia. two ground tones for unevenness.
ground_lo = np.array([0.16, 0.10, 0.13])   # deep aubergine-brown (heavily exposed)
ground_hi = np.array([0.34, 0.22, 0.18])   # warmer umber (less exposed)
ground = ground_lo[None, None, :] * expo[..., None] + ground_hi[None, None, :] * (1 - expo)[..., None]
paper = np.array([0.92, 0.86, 0.74])       # warm cream highlight (toned, not cold white)
m = block[..., None]
img = ground * (1 - m) + paper * m
# tannin mottling: warm blotches drifting across the paper (uneven toning bath)
tan = blur(vnoise(9, 21), 30)
warm = np.array([0.10, 0.04, -0.04])  # push toward brown
img = img + 0.10 * (tan - 0.5)[..., None] * warm[None, None, :]
# leak halo at thin leaf edges → warm ground bleeds under
halo = (blur(block, 8) - block).clip(0, 1)[..., None]
img = img * (1 - 0.5 * halo) + ground * (0.5 * halo)
# paper grain
img *= (1 - 0.045 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/toned.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/toned.png")
