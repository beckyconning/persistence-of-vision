"""Mezzotint profile — the soft random-dot mark on the face subject (vs the engraved LINE
face). Velvety stipple: smooth-burnished lit planes, dense grain in shadow + ground. A
portrait that emerges from the dark the way a mezzotint plate is worked from black to light."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
u, v = xs / W, ys / H
rng = np.random.default_rng(17)


def smooth(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


ky = np.array([0.10, 0.20, 0.30, 0.37, 0.44, 0.50, 0.55, 0.60, 0.66, 0.72, 0.80, 0.90])
kx = np.array([0.50, 0.58, 0.62, 0.615, 0.685, 0.725, 0.645, 0.685, 0.65, 0.685, 0.585, 0.485])
front = np.interp(v[:, 0], ky, kx)[:, None]
vn = np.clip((v[:, 0] - 0.08) / 0.84, 0, 1)
back = (0.32 - 0.13 * np.sin(np.pi * vn) ** 0.8)[:, None]
inside = (u < front) & (u > back) & (v > 0.08) & (v < 0.92)
midx = (front + back) / 2
halfw = np.clip((front - back) / 2, 1e-3, None)
cheek = np.clip(1 - ((u - midx) / halfw) ** 2, 0, 1)
z = 1.7 * np.sqrt(cheek) * np.clip(1 - ((v - 0.5) / 0.46) ** 2, 0, 1) ** 0.5


def bump(cx, cy, rx, ry, a):
    return a * np.exp(-(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2))


z = z + bump(0.65, 0.46, 0.05, 0.06, 0.18) + bump(0.59, 0.345, 0.07, 0.03, 0.10) \
    - bump(0.565, 0.375, 0.035, 0.025, 0.16) + bump(0.59, 0.565, 0.05, 0.025, 0.07) \
    + bump(0.57, 0.65, 0.06, 0.05, 0.06)
z = smooth(np.where(inside, np.clip(z, 0, None), 0.0), 3)
gx = np.gradient(z, axis=1) * W * 0.5
gy = np.gradient(z, axis=0) * H * 0.5
ln = np.sqrt(gx * gx + gy * gy + 1)
L = np.array([0.62, -0.5, 0.6]); L /= np.linalg.norm(L)
lam = np.clip((-gx * L[0] - gy * L[1] + L[2]) / ln, 0, 1)
tone = np.where(inside, 0.06 + 0.92 * lam ** 1.2, 0.05 + 0.06 * (v))  # dark ground
dark = np.clip(1 - tone, 0, 1)

g = rng.random((H, W))
g = smooth(g, 1)
g = (g - g.min()) / (g.max() - g.min())
ink = (g < dark).astype(float)

paper = np.array([0.95, 0.93, 0.88]); INKC = np.array([0.05, 0.05, 0.07])
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
write_png("../images/mezzotint_face.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/mezzotint_face.png")
