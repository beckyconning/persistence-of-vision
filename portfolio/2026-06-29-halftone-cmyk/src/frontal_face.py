"""Frontal face with a MOOD — the marquee open subject (only profiles/reliefs so far). A
frontal height-field (brow, eye sockets, nose ridge, lips, chin) with slight ASYMMETRY +
a faint downward gaze for feeling, lit from upper-left, rendered in the MEZZOTINT mark
(softest/most atmospheric) emerging from a dark ground."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
u, v = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)
rng = np.random.default_rng(29)


def smooth(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


def g(cx, cy, rx, ry, a):
    return a * np.exp(-(((u - cx) / rx) ** 2 + ((v - cy) / ry) ** 2))


# head mask (slightly egg-shaped, narrower chin)
head = ((u / 0.52) ** 2 + ((v - 0.02) / 0.66) ** 2) < 1
jaw = (v > 0.18) & (np.abs(u) > 0.30 - (v - 0.18) * 0.5)  # taper the jaw
inside = head & ~jaw

z = np.where(inside, 0.6 * np.sqrt(np.clip(1 - (u / 0.52) ** 2 - ((v - 0.02) / 0.66) ** 2, 0, 1)), 0)
# features (asymmetric a touch for life)
z += g(0.0, 0.18, 0.10, 0.16, 0.20)            # nose ridge
z += g(0.0, 0.28, 0.07, 0.05, 0.10)            # nose tip
z -= g(-0.07, 0.30, 0.03, 0.03, 0.06)          # L nostril
z -= g(0.07, 0.30, 0.03, 0.03, 0.06)           # R nostril
z += g(-0.19, -0.05, 0.13, 0.04, 0.10)         # L brow
z += g(0.20, -0.04, 0.13, 0.04, 0.11)          # R brow (slightly raised → mood)
z -= g(-0.19, 0.04, 0.10, 0.05, 0.13)          # L eye socket
z -= g(0.19, 0.05, 0.10, 0.05, 0.13)           # R eye socket
z += g(-0.19, 0.05, 0.045, 0.03, 0.06)         # L eyeball
z += g(0.19, 0.06, 0.045, 0.03, 0.06)          # R eyeball
z += g(0.0, 0.44, 0.13, 0.035, 0.09)           # upper lip
z += g(0.0, 0.50, 0.14, 0.045, 0.11)           # lower lip
z -= g(0.02, 0.47, 0.10, 0.012, 0.05)          # mouth line (faint downturn via +x offset)
z += g(0.0, 0.60, 0.16, 0.07, 0.10)            # chin
z = smooth(np.where(inside, z, 0), 3)

gx = np.gradient(z, axis=1) * W * 0.5
gy = np.gradient(z, axis=0) * H * 0.5
ln = np.sqrt(gx * gx + gy * gy + 1)
L = np.array([-0.5, -0.45, 0.74]); L /= np.linalg.norm(L)
lam = np.clip((-gx * L[0] - gy * L[1] + L[2]) / ln, 0, 1)
tone = np.where(inside, 0.05 + 0.95 * lam ** 1.25, 0.04 + 0.05 * (v + 1))
dark = np.clip(1 - tone, 0, 1)

gr = smooth(rng.random((H, W)), 1)
gr = (gr - gr.min()) / (gr.max() - gr.min())
ink = (gr < dark).astype(float)
paper = np.array([0.95, 0.93, 0.88]); INKC = np.array([0.05, 0.05, 0.07])
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
write_png("../images/frontal_face.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/frontal_face.png")
