"""Engraved face — the session's strongest MARK (line crosshatch) on its growth SUBJECT
(the profile face). Profile silhouette-contour relief height-field → Lambert tone → woodcut
crosshatch ladder (hatch sets added at new angles as tone darkens) + brow/jaw following
lines. Warm-black ink on cream."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
u, v = xs / W, ys / H


def smooth(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


ky = np.array([0.10, 0.20, 0.30, 0.37, 0.44, 0.50, 0.55, 0.60, 0.66, 0.72, 0.80, 0.90])
kx = np.array([0.52, 0.60, 0.64, 0.635, 0.70, 0.74, 0.66, 0.70, 0.665, 0.70, 0.60, 0.50])
front = np.interp(v[:, 0], ky, kx)[:, None]
vn = np.clip((v[:, 0] - 0.08) / 0.84, 0, 1)
back = (0.34 - 0.13 * np.sin(np.pi * vn) ** 0.8)[:, None]
inside = (u < front) & (u > back) & (v > 0.08) & (v < 0.92)
midx = (front + back) / 2
halfw = np.clip((front - back) / 2, 1e-3, None)
cheek = np.clip(1 - ((u - midx) / halfw) ** 2, 0, 1)
ymid = 0.5
z = 1.7 * np.sqrt(cheek) * np.clip(1 - ((v - ymid) / 0.46) ** 2, 0, 1) ** 0.5


def bump(cx, cy, rx, ry, a):
    return a * np.exp(-(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2))


z = z + bump(0.66, 0.46, 0.05, 0.06, 0.18) + bump(0.60, 0.345, 0.07, 0.03, 0.10) \
    - bump(0.575, 0.375, 0.035, 0.025, 0.16) + bump(0.60, 0.565, 0.05, 0.025, 0.07) \
    + bump(0.58, 0.65, 0.06, 0.05, 0.06)
z = smooth(np.where(inside, np.clip(z, 0, None), 0.0), 3)
gx = np.gradient(z, axis=1) * W * 0.5
gy = np.gradient(z, axis=0) * H * 0.5
ln = np.sqrt(gx * gx + gy * gy + 1)
L = np.array([0.6, -0.5, 0.62]); L /= np.linalg.norm(L)
lam = np.clip((-gx * L[0] - gy * L[1] + L[2]) / ln, 0, 1)
dark = np.where(inside, 1 - (0.16 + 0.86 * lam), 0.08)
dark = np.clip(dark, 0, 1)


def hatch(angle, freq):
    a = np.radians(angle)
    s = (xs * np.cos(a) + ys * np.sin(a)) / freq
    return (np.abs(np.cos(np.pi * s)) > 0.70).astype(float)


ink = np.zeros((H, W))
ink += hatch(32, 7.0) * (dark > 0.16)
ink += hatch(-32, 7.0) * (dark > 0.38)
ink += hatch(85, 7.0) * (dark > 0.60)
ink += hatch(5, 7.0) * (dark > 0.80)
ink = np.clip(ink, 0, 1)
# crisp profile contour
edge = (np.abs(u - front) < 0.004) & (v > 0.085) & (v < 0.915) & (u > back)
edge |= (np.abs(u - back) < 0.004) & (v > 0.085) & (v < 0.915)
ink = np.maximum(ink, edge.astype(float) * inside.astype(float))
ink = np.maximum(ink, edge.astype(float))

paper = np.array([0.96, 0.94, 0.87]); INKC = np.array([0.11, 0.09, 0.10])
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
t = np.random.default_rng(11).random((H // 4, W // 4))
out *= (1 - 0.02 * (np.repeat(np.repeat(t, 4, 0), 4, 1)[:H, :W] - 0.5))[..., None]
write_png("../images/engraved_face.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/engraved_face.png")
