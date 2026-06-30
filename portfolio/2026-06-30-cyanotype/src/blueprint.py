"""Blueprint cyanotype — the OTHER cyanotype tradition: engineering drawings reproduced as
white line-work on Prussian blue. Same medium as the photogram, opposite aesthetic (precise
lines, centerlines, dimensions vs organic silhouette). Subject: two meshing gears on a shaft.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)
ink = np.zeros((H, W))  # 1 = white line


def ring(cx, cy, r, t=0.0035):
    d = np.abs(np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2) - r)
    return (d < t).astype(float)


def disc(cx, cy, r):
    return (np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2) < r).astype(float)


def gear(cx, cy, R, teeth, t=0.004):
    ang = np.arctan2(ny - cy, nx - cx)
    rr = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    # toothed outer edge: radius modulated by a square-ish wave
    tooth = R * (1 + 0.06 * np.sign(np.cos(ang * teeth)))
    out = (np.abs(rr - tooth) < t).astype(float)
    out = np.maximum(out, ring(cx, cy, R * 0.97))            # root circle
    out = np.maximum(out, ring(cx, cy, R * 0.22))            # hub
    out = np.maximum(out, ring(cx, cy, R * 0.10))            # bore
    # keyway (small square notch at the bore)
    key = (np.abs(nx - cx) < R * 0.04) & (np.abs(ny - cy - R * 0.10) < R * 0.05)
    out = np.maximum(out, ((np.abs(np.abs(nx - cx) - R * 0.04) < t) & (np.abs(ny - cy - 0.06 * R) < R * 0.06)).astype(float))
    # bolt circle of lightening holes
    for k in range(6):
        a = k / 6 * 2 * np.pi
        out = np.maximum(out, ring(cx + R * 0.6 * np.cos(a), cy + R * 0.6 * np.sin(a), R * 0.10))
    return out


def centerlines(cx, cy, r):
    """dash-dot center cross"""
    out = np.zeros((H, W))
    seg = (np.sin((nx) * 240) > -0.3)  # crude dash pattern
    out += ((np.abs(ny - cy) < 0.0015) & (np.abs(nx - cx) < r * 1.15) & seg).astype(float)
    seg2 = (np.sin((ny) * 240) > -0.3)
    out += ((np.abs(nx - cx) < 0.0015) & (np.abs(ny - cy) < r * 1.15) & seg2).astype(float)
    return np.clip(out, 0, 1)


ink = np.maximum(ink, gear(-0.34, 0.05, 0.46, 18))
ink = np.maximum(ink, gear(0.42, 0.08, 0.34, 13))
ink = np.maximum(ink, centerlines(-0.34, 0.05, 0.46))
ink = np.maximum(ink, centerlines(0.42, 0.08, 0.34))
# a leader + dimension line across the top
ink = np.maximum(ink, ((np.abs(ny + 0.78) < 0.0015) & (nx > -0.34) & (nx < 0.42)).astype(float))
for xx in (-0.34, 0.42):
    ink = np.maximum(ink, ((np.abs(nx - xx) < 0.0015) & (ny > -0.82) & (ny < -0.74)).astype(float))
# border + title block (corner)
ink = np.maximum(ink, ((np.abs(np.abs(nx) - 0.95) < 0.002) & (np.abs(ny) < 0.95)).astype(float))
ink = np.maximum(ink, ((np.abs(np.abs(ny) - 0.95) < 0.002) & (np.abs(nx) < 0.95)).astype(float))
ink = np.maximum(ink, ((ny > 0.72) & (nx > 0.46) & (np.abs(ny - 0.72) < 0.002) ).astype(float) * (nx < 0.95))
ink = np.maximum(ink, ((nx > 0.46) & (ny > 0.72) & (np.abs(nx - 0.46) < 0.002)).astype(float) * (ny < 0.95))
ink = np.maximum(ink, ((np.abs(ny - 0.835) < 0.0015) & (nx > 0.46) & (nx < 0.95)).astype(float))

# soft blur for the contact-print feel
def blur(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


ink = np.clip(blur(ink, 1) * 1.6, 0, 1)
g = np.random.default_rng(4).random((H // 3, W // 3))
expo = 0.8 + 0.3 * np.repeat(np.repeat(blur(g, 2), 3, 0), 3, 1)[:H, :W]
deep = np.array([0.07, 0.21, 0.40]); pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * np.clip(expo, 0, 1)[..., None]
img = blue * (1 - ink[..., None]) + pale[None, None, :] * ink[..., None]
write_png("../images/blueprint.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/blueprint.png")
