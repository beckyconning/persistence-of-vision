"""Cyanotype album plate — Atkins composed her specimens across an album page. A botanical
study: a fern frond, grass sprigs, and a leafy stem arranged on one Prussian-blue plate."""
import numpy as np
from pnglib import write_png

H = W = 1300
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
block = np.zeros((H, W))
rng = np.random.default_rng(21)


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
    block[:] = np.maximum(block, np.clip(((w0 + (w1 - w0) * t) - d) / 0.0022, 0, 1))


def pinna(cx, cy, ang, length, width):
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    taper = np.clip(1 - (u / length) ** 2, 0, 1)
    edge = width * np.sqrt(taper) * (0.85 + 0.15 * np.cos(u / length * np.pi * 7))
    block[:] = np.maximum(block, np.clip((edge - np.abs(v)) / 0.0028, 0, 1) * ((u > 0) & (u < length)))


def fern(cx, cy, ang, scale, seed=0):
    tips = np.linspace(0, 1, 50)
    bx = cx + np.cos(ang) * scale * tips - np.sin(ang) * 0.05 * scale * np.sin(tips * 2)
    by = cy + np.sin(ang) * scale * tips + np.cos(ang) * 0.05 * scale * np.sin(tips * 2)
    for i in range(len(tips) - 1):
        stroke(bx[i], by[i], bx[i + 1], by[i + 1], 0.005, 0.0012)
    for t in np.linspace(0.05, 0.96, 24):
        i = int(t * (len(tips) - 1)); plen = scale * 0.19 * (1 - t) ** 0.9 + 0.006
        for s in (+1, -1):
            pinna(bx[i], by[i], ang + s * (np.pi / 2 - 0.95), plen, plen * 0.14)


def grass(cx, cy, ang, length, seed):
    a = ang + rng.uniform(-0.05, 0.05)
    x1, y1 = cx + np.cos(a) * length, cy + np.sin(a) * length
    stroke(cx, cy, x1, y1, 0.0035, 0.0006)
    pinna(x1, y1, a, length * 0.16, length * 0.035)


def sprig(cx, cy, ang, length):
    tips = np.linspace(0, 1, 30)
    bx = cx + np.cos(ang) * length * tips
    by = cy + np.sin(ang) * length * tips
    for i in range(len(tips) - 1):
        stroke(bx[i], by[i], bx[i + 1], by[i + 1], 0.004, 0.0015)
    for j, t in enumerate(np.linspace(0.12, 0.93, 8)):
        i = int(t * (len(tips) - 1)); side = 1 if j % 2 == 0 else -1
        ll = length * 0.22 * (1 - 0.4 * t)
        pinna(bx[i], by[i], ang + side * 1.05, ll, ll * 0.28)  # slim ovate leaf, alternating


fern(0.22, 0.90, -np.radians(78), 0.80, seed=1)
for k in range(6):
    grass(0.50 + 0.02 * k, 0.93, -np.radians(86 - k * 4), 0.42 + 0.05 * k, seed=k)
sprig(0.80, 0.90, -np.radians(80), 0.62)
# faint hand-label baseline (a thin underline like Atkins' captions)
stroke(0.12, 0.965, 0.45, 0.965, 0.0009, 0.0009)

block[:] = blur(block, 2)

def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


expo = np.clip(0.72 + 0.5 * blur(vn(6, 4), 20) + 0.07 * (1 - ny), 0, 1)
deep = np.array([0.06, 0.20, 0.39]); light = np.array([0.11, 0.27, 0.46]); pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + light[None, None, :] * (1 - expo)[..., None]
m = np.clip(block, 0, 1)[..., None]
halo = (blur(block, 6) - block).clip(0, 1)[..., None]
img = blue * (1 - m) + pale[None, None, :] * m
img = img * (1 - 0.4 * halo) + blue * (0.4 * halo)
img *= (1 - 0.04 * (vn(W // 3, 9) - 0.5))[..., None]
write_png("../images/plate.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/plate.png")
