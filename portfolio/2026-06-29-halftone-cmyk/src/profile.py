"""Halftone profile portrait — the untouched 'face with expression' axis (FRONTIERS #1)
rendered in the new CMYK-halftone medium. A side-profile is defined by its silhouette
CONTOUR (forehead, brow, nose, lips, chin); the face is a relief height-field bulging from
that silhouette, Lambert-shaded, then screened into warm-ink + black dots (duotone-ish CMYK).
"""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
u, v = xs / W, ys / H  # [0,1], u=x, v=y(down)


def smooth(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)
    return a


# ---- profile silhouette: face-right edge x = f(y), as a sequence of (y, x) knots ----
# y from top(0) to bottom(1); x is the front edge (face looks right, +x = front).
knots_y = np.array([0.10, 0.20, 0.30, 0.37, 0.44, 0.50, 0.55, 0.60, 0.66, 0.72, 0.80, 0.90])
knots_x = np.array([0.52, 0.60, 0.64, 0.635, 0.70, 0.74, 0.66, 0.70, 0.665, 0.70, 0.60, 0.50])
#                  crown  brow  brow  eye   nose  nose  lip   lip   chin  jaw   neck
front = np.interp(v[:, 0], knots_y, knots_x)  # per-row front edge
front2d = front[:, None]
# rounded back of the head (occiput bulges out at mid-head, tapers at crown + neck)
vn = np.clip((v[:, 0] - 0.08) / 0.84, 0, 1)
back_edge = 0.34 - 0.13 * np.sin(np.pi * vn) ** 0.8
back2d = back_edge[:, None]
inside = (u < front2d) & (u > back2d) & (v > 0.08) & (v < 0.92)

# relief height: rounded cheek (max mid-face), tapering to silhouette edges
midx = (front2d + back2d) / 2
halfw = np.clip((front2d - back2d) / 2, 1e-3, None)
cheek = np.clip(1 - ((u - midx) / halfw) ** 2, 0, 1)
ymid = (0.08 + 0.92) / 2
zface = 1.7 * np.sqrt(cheek) * np.clip(1 - ((v - ymid) / 0.46) ** 2, 0, 1) ** 0.5
# feature modulation: brow ridge, nose bulge, lips, eye-socket dimple (height bumps/dents)
def bump(cx, cy, rx, ry, amp):
    return amp * np.exp(-(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2))
zface += bump(0.66, 0.46, 0.05, 0.06, 0.18)   # nose
zface += bump(0.60, 0.345, 0.07, 0.03, 0.10)  # brow ridge
zface -= bump(0.575, 0.375, 0.035, 0.025, 0.16)  # eye socket (dent)
zface += bump(0.60, 0.565, 0.05, 0.025, 0.07)  # lips
zface += bump(0.58, 0.65, 0.06, 0.05, 0.06)    # chin
z = np.where(inside, np.clip(zface, 0, None), 0.0)
z = smooth(z, 3)

# ---- shade from height-field normal ----
gx = np.gradient(z, axis=1) * W * 0.5
gy = np.gradient(z, axis=0) * H * 0.5
nzz = np.ones_like(z)
ln = np.sqrt(gx * gx + gy * gy + 1)
L = np.array([0.55, -0.5, 0.67]); L /= np.linalg.norm(L)
lam = np.clip((-gx * L[0] + -gy * L[1] + nzz * L[2]) / ln, 0, 1)
skin = np.where(inside, 0.18 + 0.85 * lam, 0.97)  # tone; bg near-white
# warm skin RGB
img = np.stack([skin * 0.98, skin * 0.80, skin * 0.66], -1)
img = np.where(inside[..., None], img, np.array([0.96, 0.96, 0.97]))

# ---- CMYK halftone (warm duotone: heavy M/Y + K) ----
C = 1 - img[..., 0]; M = 1 - img[..., 1]; Y = 1 - img[..., 2]
K = np.minimum.reduce([C, M, Y])
C, M, Y = (np.clip((c - K) / (1 - K + 1e-6), 0, 1) for c in (C, M, Y))
K *= 0.8
CELL = 6.5


def screen(intensity, ang):
    a = np.radians(ang)
    uu = (xs * np.cos(a) - ys * np.sin(a)) / CELL
    vv = (xs * np.sin(a) + ys * np.cos(a)) / CELL
    spot = (0.5 + 0.5 * np.cos(2 * np.pi * uu)) * (0.5 + 0.5 * np.cos(2 * np.pi * vv))
    return np.clip((intensity - (1 - spot)) * 6 + 0.5, 0, 1)


covs = {"C": screen(C, 15), "M": screen(M, 75), "Y": screen(Y, 0), "K": screen(K, 45)}
INK = {"C": np.array([0.8, 0.1, 0.05]), "M": np.array([0.1, 0.82, 0.2]),
       "Y": np.array([0.05, 0.1, 0.88]), "K": np.array([0.85, 0.85, 0.85])}
out = np.ones((H, W, 3))
for key in ("Y", "M", "C", "K"):
    out *= (1 - covs[key][..., None] * INK[key][None, None, :])
write_png("../images/profile.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/profile.png")
