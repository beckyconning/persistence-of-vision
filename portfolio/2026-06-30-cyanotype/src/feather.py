"""Cyanotype feather — a quill laid on the sensitised paper. Central rachis + fine barbs
fanning to a feather outline (full mid-shaft, tapering at base + tip), with gaps where barbs
separate (the lacy vane). White-on-blue photogram, soft contact halos."""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
block = np.zeros((H, W))


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
    block[:] = np.maximum(block, np.clip((w - d) / 0.002, 0, 1))


# rachis: from lower-right base to upper-left tip, gently curved
T = np.linspace(0, 1, 200)
ax, ay = 0.74, 0.92
tx, ty = 0.40, 0.10
rx = ax + (tx - ax) * T + 0.05 * np.sin(T * np.pi)   # slight curve
ry = ay + (ty - ay) * T
# rachis shaft (tapers toward tip)
for i in range(len(T) - 1):
    stroke(rx[i], ry[i], rx[i + 1], ry[i + 1], 0.006 * (1 - 0.7 * T[i]), 0.006 * (1 - 0.7 * T[i + 1]))
# barbs: feather-outline width vs position (0 at base, max ~0.42, taper to tip)
rng = np.random.default_rng(3)
for i in range(4, len(T) - 4, 2):
    t = T[i]
    vane = 0.30 * np.sin(np.pi * np.clip((t - 0.04) / 0.92, 0, 1)) ** 0.7  # feather contour
    if vane < 0.005:
        continue
    # local rachis direction
    dx, dy = rx[i + 2] - rx[i - 2], ry[i + 2] - ry[i - 2]
    ang = np.arctan2(dy, dx)
    for s in (+1, -1):
        ba = ang + s * (np.pi / 2) - s * 0.55   # barbs swept toward the tip
        bl = vane * rng.uniform(0.9, 1.0)
        ex, ey = rx[i] + np.cos(ba) * bl, ry[i] + np.sin(ba) * bl
        stroke(rx[i], ry[i], ex, ey, 0.0016, 0.0008)

block[:] = blur(block, 1)

def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


expo = np.clip(0.74 + 0.46 * blur(vn(7, 2), 18) + 0.08 * nx, 0, 1)
deep = np.array([0.06, 0.19, 0.38]); light = np.array([0.11, 0.27, 0.46]); pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + light[None, None, :] * (1 - expo)[..., None]
m = np.clip(block, 0, 1)[..., None]
halo = (blur(block, 6) - block).clip(0, 1)[..., None]
img = blue * (1 - m) + pale[None, None, :] * m
img = img * (1 - 0.4 * halo) + blue * (0.4 * halo)
img *= (1 - 0.04 * (vn(W // 3, 9) - 0.5))[..., None]
write_png("../images/feather.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/feather.png")
