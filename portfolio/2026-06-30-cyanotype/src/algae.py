"""Cyanotype algae — Anna Atkins' iconic subject ('Photographs of British Algae', 1843).
Wispy recursive branching seaweed: a holdfast at the base splitting into ever-finer curved
filaments. Organic, flowing — unlike the fern's regular pinnae. White silhouette on blue."""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
block = np.zeros((H, W))
rng = np.random.default_rng(7)


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
    w = w0 + (w1 - w0) * t
    block[:] = np.maximum(block, np.clip((w - d) / 0.0025, 0, 1))


def branch(x, y, ang, length, width, depth):
    if depth == 0 or length < 0.01:
        return
    # draw this segment as a gentle arc (several sub-steps that curve)
    steps = 8
    curve = rng.uniform(-0.9, 0.9)
    px, py, pa = x, y, ang
    for i in range(steps):
        pa += curve / steps
        nx2 = px + np.cos(pa) * length / steps
        ny2 = py + np.sin(pa) * length / steps
        stroke(px, py, nx2, ny2, width * (1 - i / steps / 1.5), width * (1 - (i + 1) / steps / 1.5))
        px, py = nx2, ny2
    # children: 2-3 finer branches fanning from the tip
    n = rng.integers(2, 4)
    for _ in range(n):
        da = rng.uniform(-0.7, 0.7)
        branch(px, py, pa + da, length * rng.uniform(0.6, 0.82), width * 0.62, depth - 1)


# a few fronds rising from a holdfast cluster near the bottom
base_y = 0.93
for k in range(3):
    bx = 0.40 + 0.10 * k + rng.uniform(-0.02, 0.02)
    branch(bx, base_y, -np.pi / 2 + rng.uniform(-0.25, 0.25), rng.uniform(0.20, 0.26),
           0.010, 6)
# a holdfast (rooty base)
for _ in range(10):
    a = rng.uniform(np.pi * 0.6, np.pi * 1.4)
    stroke(0.50, base_y, 0.50 + np.cos(a) * 0.05, base_y - np.sin(a) * 0.05 + 0.03, 0.004, 0.001)

block[:] = blur(block, 2)

# cyanotype compose
def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


expo = np.clip(0.72 + 0.5 * blur(vn(6, 5), 18) + 0.10 * (1 - ny), 0, 1)
deep = np.array([0.06, 0.20, 0.39]); light = np.array([0.11, 0.27, 0.46]); pale = np.array([0.87, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + light[None, None, :] * (1 - expo)[..., None]
m = np.clip(block, 0, 1)[..., None]
halo = (blur(block, 7) - block).clip(0, 1)[..., None]
img = blue * (1 - m) + pale[None, None, :] * m
img = img * (1 - 0.45 * halo) + blue * (0.45 * halo)
img *= (1 - 0.04 * (vn(W // 3, 9) - 0.5))[..., None]
write_png("../images/algae.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/algae.png")
