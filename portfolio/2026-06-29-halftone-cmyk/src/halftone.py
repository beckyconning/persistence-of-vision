"""CMYK halftone print — a lit form separated into C/M/Y/K dot-screens at the classic
rosette angles (C 15deg, M 75deg, Y 0deg, K 45deg), composited subtractively on white.

New axis from session 10 (watercolour washes): same physical-media family, opposite MARK —
hard periodic DOTS, channel registration, the offset-print rosette. Subject: a lit sphere
(Lambert + rim + ambient) so the tonal range exercises dot growth from highlight to shadow.
Subtractive ink (white paper × per-channel transmittance) keeps it honest to print.
"""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)  # [-1,1]

# ---- tonal source: a lit sphere, off-centre, on a soft vertical gradient ----
cx, cy, R = -0.18, -0.12, 0.62
d2 = (nx - cx) ** 2 + (ny - cy) ** 2
inside = d2 < R * R
z = np.sqrt(np.clip(R * R - d2, 0, None))
# surface normal
nxn, nyn, nzn = (nx - cx) / R, (ny - cy) / R, z / R
L = np.array([0.5, -0.6, 0.62]); L = L / np.linalg.norm(L)
lam = np.clip(nxn * L[0] + nyn * L[1] + nzn * L[2], 0, 1)
spec = np.clip(nzn, 0, 1) ** 8  # crude rim/highlight
shade = 0.12 + 0.8 * lam + 0.5 * spec
bg = 0.93 - 0.20 * ((ny + 1) / 2)  # soft gradient backdrop

# build an RGB image: warm sphere on cool-paper backdrop
img_rgb = np.empty((H, W, 3))
sphere_col = np.stack([0.95 * shade, 0.62 * shade, 0.30 * shade], -1)  # warm ochre sphere
bg_col = np.stack([bg * 0.96, bg * 0.97, bg * 1.0], -1)                # faint cool paper
img_rgb[:] = np.where(inside[..., None], np.clip(sphere_col, 0, 1), bg_col)
# soft contact shadow
sh = np.exp(-(((nx - cx - 0.10) ** 2) / 0.20 + ((ny - cy - 0.55) ** 2) / 0.03))
img_rgb *= (1 - 0.35 * sh)[..., None]

# ---- RGB -> CMYK ----
C = 1 - img_rgb[..., 0]
M = 1 - img_rgb[..., 1]
Y = 1 - img_rgb[..., 2]
K = np.minimum.reduce([C, M, Y])
# undercolour removal: pull common grey into K, lighten CMY
C, M, Y = (np.clip((c - K) / (1 - K + 1e-6), 0, 1) for c in (C, M, Y))
K = K * 0.9

CELL = 7.0  # screen frequency (px per dot cell)


def screen(intensity, angle_deg):
    """Rotated dot screen: ink where intensity exceeds the spot function. Dot grows with
    intensity. Returns coverage in [0,1] (1 = full ink)."""
    a = np.radians(angle_deg)
    u = (xs * np.cos(a) - ys * np.sin(a)) / CELL
    v = (xs * np.sin(a) + ys * np.cos(a)) / CELL
    # spot function: a smooth 2-D cosine dot, value in [0,1]; threshold by intensity so the
    # inked dot radius tracks ink amount (classic amplitude-modulated halftone).
    spot = (0.5 + 0.5 * np.cos(2 * np.pi * u)) * (0.5 + 0.5 * np.cos(2 * np.pi * v))
    # antialiased coverage near the dot edge
    return np.clip((intensity - (1 - spot)) * 6.0 + 0.5, 0, 1)


covC = screen(C, 15)
covM = screen(M, 75)
covY = screen(Y, 0)
covK = screen(K, 45)

# ---- composite subtractively on white paper ----
paper = np.ones((H, W, 3))
# faint paper tooth
tooth = np.random.default_rng(3).random((H // 4, W // 4))
tooth = np.repeat(np.repeat(tooth, 4, 0), 4, 1)[:H, :W]
paper *= (1 - 0.02 * (tooth - 0.5))[..., None]
# ink absorptions (per-channel subtractive); each dot multiplies the paper
INK = {
    "C": np.array([0.85, 0.10, 0.05]),  # cyan absorbs red
    "M": np.array([0.10, 0.85, 0.20]),  # magenta absorbs green
    "Y": np.array([0.05, 0.10, 0.90]),  # yellow absorbs blue
    "K": np.array([0.88, 0.88, 0.88]),  # black absorbs all
}
out = paper.copy()
for cov, key in ((covY, "Y"), (covC, "C"), (covM, "M"), (covK, "K")):
    out *= (1 - cov[..., None] * INK[key][None, None, :])

png = np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/halftone.png", png)
print("wrote images/halftone.png", png.shape)
