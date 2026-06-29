"""CMYK halftone still-life — four lit spheres of different hues, so ALL four screens
(C/M/Y/K) fire and the offset-print ROSETTE + registration show. Answers halftone.py's
critique (a warm subject only exercised Y+K)."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)

L = np.array([0.45, -0.6, 0.66]); L = L / np.linalg.norm(L)
img_rgb = np.stack([np.full((H, W), 0.95), np.full((H, W), 0.96), np.full((H, W), 0.98)], -1)

# (cx, cy, R, albedo) — hues spanning the wheel so C, M, Y all get exercised
SPHERES = [
    (-0.42, 0.06, 0.40, np.array([0.85, 0.18, 0.20])),  # red  -> M+Y
    (0.10, -0.30, 0.34, np.array([0.95, 0.80, 0.18])),  # yellow -> Y
    (0.40, 0.22, 0.46, np.array([0.16, 0.42, 0.78])),   # blue -> C+M
    (-0.05, 0.42, 0.28, np.array([0.55, 0.20, 0.62])),  # purple -> C+M
]
# painter's order: far (top) to near (bottom)
for cx, cy, R, alb in sorted(SPHERES, key=lambda s: s[1]):
    d2 = (nx - cx) ** 2 + (ny - cy) ** 2
    inside = d2 < R * R
    z = np.sqrt(np.clip(R * R - d2, 0, None))
    nxn, nyn, nzn = (nx - cx) / R, (ny - cy) / R, z / R
    lam = np.clip(nxn * L[0] + nyn * L[1] + nzn * L[2], 0, 1)
    spec = np.clip(nzn, 0, 1) ** 12
    shade = (0.14 + 0.82 * lam)[..., None] * alb[None, None, :] + 0.6 * spec[..., None]
    # contact shadow under each
    sh = np.exp(-(((nx - cx) ** 2) / (R * R * 1.4) + ((ny - cy - R * 0.95) ** 2) / 0.012))
    img_rgb *= (1 - 0.30 * (sh * ~inside)[..., None])
    img_rgb = np.where(inside[..., None], np.clip(shade, 0, 1), img_rgb)

# RGB -> CMYK with UCR
C = 1 - img_rgb[..., 0]; M = 1 - img_rgb[..., 1]; Y = 1 - img_rgb[..., 2]
K = np.minimum.reduce([C, M, Y])
C, M, Y = (np.clip((c - K) / (1 - K + 1e-6), 0, 1) for c in (C, M, Y))
K *= 0.85

CELL = 7.0


def screen(intensity, angle_deg):
    a = np.radians(angle_deg)
    u = (xs * np.cos(a) - ys * np.sin(a)) / CELL
    v = (xs * np.sin(a) + ys * np.cos(a)) / CELL
    spot = (0.5 + 0.5 * np.cos(2 * np.pi * u)) * (0.5 + 0.5 * np.cos(2 * np.pi * v))
    return np.clip((intensity - (1 - spot)) * 6.0 + 0.5, 0, 1)


covs = {"C": screen(C, 15), "M": screen(M, 75), "Y": screen(Y, 0), "K": screen(K, 45)}
INK = {"C": np.array([0.85, 0.10, 0.05]), "M": np.array([0.10, 0.85, 0.20]),
       "Y": np.array([0.05, 0.10, 0.90]), "K": np.array([0.88, 0.88, 0.88])}
out = np.ones((H, W, 3))
tooth = np.random.default_rng(5).random((H // 4, W // 4))
out *= (1 - 0.02 * (np.repeat(np.repeat(tooth, 4, 0), 4, 1)[:H, :W] - 0.5))[..., None]
for key in ("Y", "C", "M", "K"):
    out *= (1 - covs[key][..., None] * INK[key][None, None, :])

write_png("../images/stilllife.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/stilllife.png")
