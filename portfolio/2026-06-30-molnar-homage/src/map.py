"""
An invented island — cartography, the one major SUBJECT untouched across the
whole portfolio. A value-noise elevation field, quantised into tinted relief bands
(deep sea → shoal → beach → lowland → upland → peak) with thin contour lines at
each band edge — the look of an old hand-tinted topographic map. New subject,
colour, on aged paper.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 1000
rng = np.random.default_rng(33)


def vnoise(freq):
    g = rng.standard_normal((freq + 2, freq + 2))
    yy = np.linspace(0, freq, H)[:, None] * np.ones((1, W))
    xx = np.linspace(0, freq, W)[None, :] * np.ones((H, 1))
    x0, y0 = np.floor(xx).astype(int), np.floor(yy).astype(int)
    fx, fy = xx - x0, yy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - sx) + g[y0, x0 + 1] * sx
    b = g[y0 + 1, x0] * (1 - sx) + g[y0 + 1, x0 + 1] * sx
    return a * (1 - sy) + b * sy


# fractal elevation, pulled into an island by a radial falloff
elev = sum(vnoise(f) * (0.5 ** i) for i, f in enumerate([3, 6, 12, 24]))
elev = (elev - elev.min()) / (elev.max() - elev.min())
yy, xx = np.mgrid[0:H, 0:W]
r = np.hypot(xx - W / 2, yy - H / 2) / (W * 0.52)
elev = np.clip(elev * 1.25 - r ** 1.7 * 0.95, 0, 1)

# elevation bands (sea level at 0.30) → tints
levels = [0.0, 0.16, 0.30, 0.34, 0.50, 0.70, 0.86, 1.01]
tints = [
    (0.20, 0.34, 0.48),   # deep sea
    (0.34, 0.52, 0.60),   # sea
    (0.55, 0.70, 0.72),   # shoal
    (0.86, 0.82, 0.62),   # beach
    (0.74, 0.76, 0.52),   # lowland
    (0.64, 0.66, 0.42),   # upland
    (0.72, 0.64, 0.46),   # highland
]
band = np.zeros((H, W), int)
for i in range(len(levels) - 1):
    band[(elev >= levels[i]) & (elev < levels[i + 1])] = i
rgb = np.zeros((H, W, 3))
for i, c in enumerate(tints):
    rgb[band == i] = c

# contour lines at every band edge (where the band index changes)
edge = np.zeros((H, W), bool)
edge[1:, :] |= band[1:, :] != band[:-1, :]
edge[:, 1:] |= band[:, 1:] != band[:, :-1]
line = np.array([0.22, 0.18, 0.14])
rgb[edge] = rgb[edge] * 0.35 + line * 0.65

# aged-paper vignette + grain
vig = 1 - 0.18 * (r ** 2)
rgb = rgb * vig[..., None] * (1 + 0.02 * vnoise(60)[..., None])
write_png(os.path.join(OUT, "island_map.png"), (np.clip(rgb, 0, 1) * 255).astype(np.uint8))
print("wrote island_map.png  land frac=%.2f" % (elev > 0.30).mean())
