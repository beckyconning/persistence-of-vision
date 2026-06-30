"""Charcoal drapery study — hanging cloth folds. Same TONAL charcoal medium as the portrait,
different subject: the classic atelier fold study. Folds are a height field of stacked vertical
ridges (varying phase/width, sagging under gravity); a raking side light gives deep core shadows
in the valleys and bright crests; smudged blends + a few crisp accent darks in the deepest folds;
eraser highlights on the lit ridge tops. Showcases charcoal's full black-to-paper tonal range.
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


# ---- height field of cloth: sum of vertical folds with varying centre/width, gathered at top ----
rg = np.random.default_rng(4)
# folds gather toward a pin at the top-centre and spread/sag downward
gather = 0.5 + (nx - 0.5) * (0.35 + 0.65 * ny)          # x fans out lower down
sag = 1.0 - 0.18 * np.sin(ny * np.pi)                    # cloth bellies in the middle
z = np.zeros((H, W))
centres = np.linspace(0.10, 0.90, 11)
for i, c in enumerate(centres):
    w = 0.026 + 0.014 * rg.random()                      # narrower → crisper folds
    phase = c + 0.03 * np.sin(ny * 6 + i)                # fold wanders as it falls
    ridge = np.exp(-((gather - phase) / w) ** 2)
    z = z + ridge * (0.6 + 0.5 * rg.random()) * sag
# a couple of cross sub-folds (diagonal tension wrinkles)
for k in range(3):
    cy = 0.3 + 0.25 * k
    z = z + 0.25 * np.exp(-((ny - cy - 0.04 * np.sin(nx * 8)) / 0.03) ** 2) * (0.5 + 0.5 * np.sin(nx * 20))
z = blur(z, 2)

# ---- shade with a raking light from the left ----
gy, gx = np.gradient(z)
SC = 135.0
lx, ly, lz = -gx * SC, -gy * SC, np.ones_like(z)
ln = np.sqrt(lx * lx + ly * ly + lz * lz) + 1e-9
lx, ly, lz = lx / ln, ly / ln, lz / ln
L = np.array([-0.72, -0.2, 0.5]); L = L / np.linalg.norm(L)   # low raking key from upper-left
lam = np.clip(lx * L[0] + ly * L[1] + lz * L[2], 0, 1)
val = 0.10 + 0.90 * lam ** 1.1
# deepen the valleys (low z) → core fold shadows
val = val * (0.45 + 0.55 * np.clip(z / (z.max() + 1e-9), 0, 1) ** 0.5)
# smudge
val = blur(val, 1)
# crisp accent darks in the deepest valleys (where z is lowest between folds)
valley = np.clip(1 - z / (0.5 * z.max() + 1e-9), 0, 1)
val = val - 0.18 * valley * (valley > 0.6)
# eraser highlights on the brightest crests
hi = np.clip((val - 0.78) / 0.22, 0, 1)
val = val + 0.10 * hi
val = np.clip(val, 0, 1)

# ---- palette ----
paper = np.array([0.82, 0.79, 0.73])
charc = np.array([0.09, 0.09, 0.11])
img = charc[None, None, :] + (paper - charc)[None, None, :] * val[..., None]
img = img * (1 - 0.05 * (vnoise(W // 2, 11) - 0.5))[..., None]      # paper tooth
vig = 1 - 0.22 * ((nx - 0.5) ** 2 + (ny - 0.5) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/drapery.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/drapery.png")
