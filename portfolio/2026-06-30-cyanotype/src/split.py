"""Cyanotype — SPLIT-TONED. The classic partial-tone: shadows keep the cold Prussian blue,
but the paper highlights tone WARM (cream/straw) — a true duotone, blue + warm, not one or the
other. Subject: equisetum (horsetail) — vertical jointed stems with whorls of fine branchlets
at each node. Simple, architectural, lets the split-tone do the talking.
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


def stroke(x0, y0, x1, y1, w0, w1, soft=0.003):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    w = w0 + (w1 - w0) * t
    return np.clip((w - d) / soft, 0, 1)


rg = np.random.default_rng(5)
# three horsetail stems, slightly leaning, with nodes + whorls of branchlets
for stem, (bx, lean, h) in enumerate([(0.34, 0.04, 0.92), (0.52, -0.03, 0.98), (0.68, 0.05, 0.86)]):
    top = 0.97 - h
    nseg = 7
    ys_nodes = np.linspace(0.96, top, nseg + 1)
    for k in range(nseg + 1):
        f = k / nseg
        xx = bx + lean * (1 - f)  # lean toward vertical as it rises
        if k < nseg:
            f2 = (k + 1) / nseg
            xx2 = bx + lean * (1 - f2)
            block[:] = np.maximum(block, stroke(xx, ys_nodes[k], xx2, ys_nodes[k + 1],
                                                0.010 * (1 - 0.5 * f), 0.009 * (1 - 0.5 * f)))
        # node sheath: a small dark band ring (let blue through → thinner block)
        node = (np.abs(ny - ys_nodes[k]) < 0.004) & (np.abs(nx - xx) < 0.014 * (1 - 0.5 * f))
        block[node] = np.maximum(block[node], 0.0)  # leave as stem
        # whorl of fine branchlets at this node, swept upward
        if 0 < k < nseg:
            nb = 7
            blen = 0.16 * (1 - 0.6 * f) + 0.02
            for b in range(nb):
                side = -1 if b % 2 == 0 else 1
                spread = (b // 2 + 1) / (nb // 2 + 1)
                ang = -np.pi / 2 + side * (0.35 + 0.55 * spread)
                ex = xx + np.cos(ang) * blen
                ey = ys_nodes[k] + np.sin(ang) * blen
                block[:] = np.maximum(block, stroke(xx, ys_nodes[k], ex, ey, 0.0024, 0.0006, soft=0.0022))

block[:] = blur(block, 1)
block[:] = np.clip(block, 0, 1)

# ---- compose: SPLIT-TONE ----
expo = 0.74 + 0.40 * blur(vnoise(7, 5), 26) + 0.06 * (1 - ny)
expo = np.clip(expo, 0, 1)
# shadow stays Prussian blue; only highlights tone warm
deep = np.array([0.05, 0.19, 0.37])
mid = np.array([0.10, 0.26, 0.45])
blue = deep[None, None, :] * expo[..., None] + mid[None, None, :] * (1 - expo)[..., None]
warm_paper = np.array([0.93, 0.88, 0.72])  # straw/cream highlight (toned)
m = np.clip(block, 0, 1)[..., None]
img = blue * (1 - m) + warm_paper * m
# the split: blend a touch of warm into the brighter blue too (partial tone of the ground)
gbright = (expo[..., None])  # brighter where more exposed... invert: less exposed = lighter blue
warm_tint = np.array([0.06, 0.03, -0.05])
img = img + 0.06 * (1 - expo)[..., None] * warm_tint[None, None, :]
# halo
halo = (blur(block, 7) - block).clip(0, 1)[..., None]
img = img * (1 - 0.5 * halo) + blue * (0.5 * halo)
img *= (1 - 0.04 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/split.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/split.png")
