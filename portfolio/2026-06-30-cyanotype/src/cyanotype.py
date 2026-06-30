"""Cyanotype photogram — Anna-Atkins-style botanical sun-print. New axis: physical-media
PHOTOGRAM (not pigment, not screened ink). UV light turns the sensitised paper deep Prussian
blue; a specimen laid on top BLOCKS the light → pale silhouette, with soft halos where thin
parts let light leak through. Palette is cyan-blue + paper-white (no glow-on-black).

Subject: a fern frond + a couple of grasses/leaves, arranged as a contact print.
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


# specimen mask accumulator: 1 = fully blocked light (white), 0 = full exposure (blue)
block = np.zeros((H, W))


def stroke(x0, y0, x1, y1, w0, w1):
    """A tapered stem/blade from (x0,y0)->(x1,y1), width w0->w1 (normalised)."""
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    w = w0 + (w1 - w0) * t
    return np.clip((w - d) / 0.004, 0, 1) * ((t > 0) & (t < 1))


def pinna(cx, cy, ang, length, width):
    """A leaflet: tapered pointed blade at angle, with a few lobes."""
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    taper = np.clip(1 - (u / length) ** 2, 0, 1)
    lobes = 0.82 + 0.18 * np.cos(u / length * np.pi * 9)  # serrated edge
    edge = width * np.sqrt(taper) * lobes
    return np.clip((edge - np.abs(v)) / 0.003, 0, 1) * ((u > 0) & (u < length))


def fern(cx, cy, ang, scale, seed=0):
    rg = np.random.default_rng(seed)
    # rachis (main stem), gently curved
    tips = np.linspace(0, 1, 60)
    bx = cx + np.cos(ang) * scale * tips - np.sin(ang) * 0.06 * scale * np.sin(tips * 2.2)
    by = cy + np.sin(ang) * scale * tips + np.cos(ang) * 0.06 * scale * np.sin(tips * 2.2)
    for i in range(len(tips) - 1):
        block[:] = np.maximum(block, stroke(bx[i], by[i], bx[i + 1], by[i + 1], 0.006, 0.0015))
    # paired pinnae, shrinking toward the tip — thin + swept forward so blue shows between
    for t in np.linspace(0.04, 0.97, 30):
        i = int(t * (len(tips) - 1))
        plen = scale * 0.20 * (1 - t) ** 0.9 + 0.008
        pw = plen * 0.14  # THIN leaflet (was 0.32 → solid wedge)
        droop = 0.95  # sweep leaflets strongly toward the tip (lacy frond, not a triangle)
        for s in (+1, -1):
            pa = ang + s * (np.pi / 2 - droop)
            block[:] = np.maximum(block, pinna(bx[i], by[i], pa, plen, pw))


def grass(cx, cy, ang, length, seed):
    rg = np.random.default_rng(seed)
    a = ang + rg.uniform(-0.05, 0.05)
    x1 = cx + np.cos(a) * length + 0.02 * np.sin(np.linspace(0, 3, 1))[0]
    y1 = cy + np.sin(a) * length
    block[:] = np.maximum(block, stroke(cx, cy, x1, y1, 0.004, 0.0006))
    # a seed head
    block[:] = np.maximum(block, pinna(x1, y1, a, length * 0.18, length * 0.04))


fern(0.30, 0.86, -np.radians(74), 0.92, seed=1)
fern(0.62, 0.90, -np.radians(82), 0.78, seed=2)
for k in range(5):
    grass(0.50 + 0.06 * k, 0.92, -np.radians(88 - k * 3), 0.5 + 0.05 * k, seed=10 + k)
block[:] = blur(block, 2)  # soft contact edges

# ---- compose: Prussian-blue exposure + pale specimen ----
expo = 0.75 + 0.45 * blur(vnoise(7, 5), 20) + 0.10 * (1 - ny)  # uneven sun exposure
expo = np.clip(expo, 0, 1)
deep = np.array([0.06, 0.20, 0.38])   # Prussian blue (exposed)
pale = np.array([0.86, 0.92, 0.96])   # paper highlight (blocked)
blue = deep[None, None, :] * expo[..., None] + np.array([0.10, 0.26, 0.45])[None, None, :] * (1 - expo)[..., None]
m = np.clip(block, 0, 1)[..., None]
# specimen pale, but thin parts let some blue leak (halo) → multiply pale toward blue at edges
halo = (blur(block, 8) - block).clip(0, 1)[..., None]
img = blue * (1 - m) + pale * m
img = img * (1 - 0.5 * halo) + blue * (0.5 * halo)  # blue halo under translucent edges
# paper grain
img *= (1 - 0.04 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/cyanotype.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/cyanotype.png")
