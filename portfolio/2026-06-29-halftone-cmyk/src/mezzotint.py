"""Mezzotint / stipple — tone from RANDOM dot density, not a regular screen. The rocker
roughens the plate; ink sits in pits → darks are dense random grain, lights are burnished
smooth. Softer, velvety reproduction mark (vs the crisp halftone rosette). Subject: a lit
sphere fading into a dark ground — mezzotint's signature deep blacks + glowing highlight."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)
rng = np.random.default_rng(13)

cx, cy, R = 0.10, 0.04, 0.58
d2 = (nx - cx) ** 2 + (ny - cy) ** 2
inside = d2 < R * R
z = np.sqrt(np.clip(R * R - d2, 0, None))
nn = np.stack([(nx - cx) / R, (ny - cy) / R, z / R], -1)
L = np.array([-0.45, -0.5, 0.74]); L /= np.linalg.norm(L)
lam = np.clip(nn @ L, 0, 1)
spec = np.clip(nn[..., 2], 0, 1) ** 20
tone = np.where(inside, 0.05 + 0.9 * lam ** 1.3 + 0.5 * spec, 0.10 + 0.10 * (ny + 1))
tone = np.clip(tone, 0, 1)  # 1 = light, 0 = dark
dark = 1 - tone

# rocker grain: clustered random field (blur white noise a touch → mezzotint tooth)
g = rng.random((H, W))
k = np.ones(3) / 3
g = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, g)
g = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, g)
g = (g - g.min()) / (g.max() - g.min())
# ink where the grain pit is "deeper" than the local lightness → denser ink in darks
ink = (g < dark).astype(float)

paper = np.array([0.95, 0.93, 0.88]); INKC = np.array([0.06, 0.05, 0.07])
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
write_png("../images/mezzotint.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/mezzotint.png")
