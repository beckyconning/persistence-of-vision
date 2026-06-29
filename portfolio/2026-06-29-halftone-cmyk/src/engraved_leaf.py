"""Engraved botanical — varying the SUBJECT off the lit sphere (self-critique note). A leaf:
blade + midrib + lateral veins, with the crosshatch engraving mark giving tone/curl. Veins
are paper-reserve (un-inked) lines; the blade darkens toward the shaded curl."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)
# rotate frame so the leaf lies on a diagonal
th = np.radians(-32)
u = nx * np.cos(th) - ny * np.sin(th)
v = nx * np.sin(th) + ny * np.cos(th)

# leaf blade: pointed ellipse along u, width tapering at both ends
L0, halfw = 0.82, 0.30
taper = np.clip(1 - (u / L0) ** 2, 0, 1)
width = halfw * np.sqrt(taper) * (0.6 + 0.4 * np.clip(1 - u / L0, 0, 1))  # fuller at base
blade = (np.abs(v) < width) & (np.abs(u) < L0)
# gentle curl shading: one half-blade lit, other shaded; tip curls (darker)
curl = np.clip(0.5 + 0.9 * (v / (width + 1e-3)) + 0.4 * (u / L0), -1, 2)
dark = np.where(blade, np.clip(0.30 + 0.45 * np.clip(curl, 0, 1) + 0.25 * np.clip(u / L0, 0, 1), 0, 1), 0.07)
dark = np.where(blade, dark, dark)


def hatch(angle, freq):
    a = np.radians(angle)
    s = (xs * np.cos(a) + ys * np.sin(a)) / freq
    return (np.abs(np.cos(np.pi * s)) > 0.72).astype(float)


ink = np.zeros((H, W))
ink += hatch(58, 7.0) * (dark > 0.20)
ink += hatch(-58, 7.0) * (dark > 0.45)
ink += hatch(0, 7.0) * (dark > 0.68)
ink = np.clip(ink, 0, 1) * blade
# midrib (reserve line) + lateral veins branching from it
midrib = np.abs(v) < 0.012
veins = np.zeros((H, W), bool)
for s in np.linspace(-0.7, 0.7, 11):
    lv = v - 0.55 * np.sign(s if s != 0 else 1) * (u - s)  # angled lateral
    veins |= (np.abs(lv) < 0.010) & (np.abs(u - s) < 0.30) & blade
reserve = (midrib & blade) | veins
ink = ink * (~reserve)
# crisp leaf outline + a stem
edge = blade & ~((np.abs(v) < width - 0.006) & (np.abs(u) < L0 - 0.006))
stem = (np.abs(v) < 0.012) & (u < -L0 + 0.02) & (u > -L0 - 0.34)
ink = np.maximum(ink, (edge | stem).astype(float))

paper = np.array([0.96, 0.94, 0.87]); INKC = np.array([0.10, 0.12, 0.09])  # warm green-black
out = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
t = np.random.default_rng(23).random((H // 4, W // 4))
out *= (1 - 0.02 * (np.repeat(np.repeat(t, 4, 0), 4, 1)[:H, :W] - 0.5))[..., None]
write_png("../images/engraved_leaf.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/engraved_leaf.png")
