"""Line engraving / crosshatch — tonal shading by LINES not dots: progressively add hatch
sets at new angles as tone darkens (1 set in light, +perpendicular in mid, +two diagonals in
shadow), the woodcut/banknote mark. Distinct from the dot halftone. Subject: a lit sphere on
a hatched ground, warm-black ink on cream paper."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)

# tonal source: a lit sphere + soft ground
cx, cy, R = -0.12, -0.10, 0.60
d2 = (nx - cx) ** 2 + (ny - cy) ** 2
inside = d2 < R * R
z = np.sqrt(np.clip(R * R - d2, 0, None))
nn = np.stack([(nx - cx) / R, (ny - cy) / R, z / R], -1)
Ldir = np.array([0.5, -0.55, 0.67]); Ldir /= np.linalg.norm(Ldir)
lam = np.clip(nn @ Ldir, 0, 1)
amb = 0.10 + 0.05 * nn[..., 2]
tone = np.where(inside, amb + 0.9 * lam, 0.86 - 0.18 * (ny + 1) / 2)  # darkness: low=dark
dark = 1 - np.clip(tone, 0, 1)  # 0 light .. 1 dark
# contact shadow
dark += 0.5 * np.exp(-(((nx - cx - 0.05) ** 2) / 0.18 + ((ny - cy - 0.62) ** 2) / 0.01)) * (~inside)
dark = np.clip(dark, 0, 1)


def hatch(angle, freq, phase=0.0):
    a = np.radians(angle)
    s = (xs * np.cos(a) + ys * np.sin(a)) / freq + phase
    # thin dark lines: 1 where near a line crest
    return (np.abs(np.cos(np.pi * s)) > 0.72).astype(float)


# threshold ladder: each darker band adds another hatch direction
ink = np.zeros((H, W))
ink += hatch(28, 9.0) * (dark > 0.18)
ink += hatch(-28, 9.0) * (dark > 0.40)
ink += hatch(80, 9.0) * (dark > 0.62)
ink += hatch(0, 9.0) * (dark > 0.80)
# engraving line WEIGHT also tracks tone on the lit side (thicker lines in shadow) via a
# second finer set following the sphere's longitude for form
lon = np.arctan2(nn[..., 0], nn[..., 2])
ink += ((np.abs(np.cos(lon * 9)) > 0.80) & inside & (dark > 0.30)).astype(float)
ink = np.clip(ink, 0, 1)
ink = np.maximum(ink, (np.abs(np.sqrt(d2) - R) < 0.004).astype(float))  # crisp contour line

paper = np.array([0.96, 0.94, 0.88])  # cream
INKC = np.array([0.12, 0.10, 0.10])   # warm near-black
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
# faint paper tooth
t = np.random.default_rng(9).random((H // 4, W // 4))
out *= (1 - 0.02 * (np.repeat(np.repeat(t, 4, 0), 4, 1)[:H, :W] - 0.5))[..., None]
write_png("../images/engraving.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/engraving.png")
