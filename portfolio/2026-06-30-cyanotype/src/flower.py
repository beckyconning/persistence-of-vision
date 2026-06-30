"""Cyanotype bloom — a radial specimen (vs the linear fern/feather/algae). A composite flower:
petals radiating from a disc centre, a stem, two leaves. White-on-blue photogram."""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
block = np.zeros((H, W))
rng = np.random.default_rng(11)


def blur(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


def stroke(x0, y0, x1, y1, w0, w1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    block[:] = np.maximum(block, np.clip(((w0 + (w1 - w0) * t) - d) / 0.0025, 0, 1))


def petal(cx, cy, ang, length, width):
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    # teardrop: widest at ~60% out, pointed tip, narrow base
    prof = np.clip(np.sin(np.pi * np.clip(u / length, 0, 1)) ** 0.7, 0, 1)
    edge = width * prof
    block[:] = np.maximum(block, np.clip((edge - np.abs(v)) / 0.003, 0, 1) * ((u > 0) & (u < length)))


def leaf(cx, cy, ang, length, width):
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    taper = np.clip(1 - (2 * u / length - 1) ** 2, 0, 1)
    block[:] = np.maximum(block, np.clip((width * np.sqrt(taper) - np.abs(v)) / 0.003, 0, 1) * ((u > 0) & (u < length)))


cx, cy = 0.5, 0.42
# stem
stroke(cx, cy, cx + 0.02, 0.95, 0.006, 0.004)
leaf(cx + 0.012, 0.70, np.radians(-25), 0.20, 0.05)
leaf(cx + 0.016, 0.80, np.radians(205), 0.18, 0.045)
# two rings of petals (back ring offset for fullness)
for ring_i, (n, plen, pw, off) in enumerate([(13, 0.27, 0.05, 0.0), (13, 0.23, 0.045, np.pi / 13)]):
    for k in range(n):
        a = k / n * 2 * np.pi + off + rng.uniform(-0.03, 0.03)
        petal(cx, cy, a, plen * rng.uniform(0.94, 1.0), pw)
# centre disc (stippled)
d = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
block[:] = np.maximum(block, (d < 0.06).astype(float) * 0.5)  # faint disc
sp = rng.random((H, W))
block[:] = np.maximum(block, ((d < 0.055) & (sp < 0.5)).astype(float))  # stipple florets

block[:] = blur(block, 2)

def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


expo = np.clip(0.73 + 0.48 * blur(vn(6, 4), 18) + 0.08 * (1 - nx), 0, 1)
deep = np.array([0.06, 0.20, 0.39]); light = np.array([0.11, 0.27, 0.46]); pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + light[None, None, :] * (1 - expo)[..., None]
m = np.clip(block, 0, 1)[..., None]
halo = (blur(block, 6) - block).clip(0, 1)[..., None]
img = blue * (1 - m) + pale[None, None, :] * m
img = img * (1 - 0.4 * halo) + blue * (0.4 * halo)
img *= (1 - 0.04 * (vn(W // 3, 9) - 0.5))[..., None]
write_png("../images/flower.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/flower.png")
