"""Risograph duotone — two fluoro spot inks (pink + teal) screened separately and
deliberately MIS-REGISTERED (each screen offset a few px), so the overlap glows a third
colour and the edges fringe — the beloved riso print error, a distinct sub-aesthetic of the
halftone axis. Subject: bold overlapping forms (riso loves flat graphic shapes)."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)

# Two tonal "plates" (each drives one ink). Bold lit forms.
L = np.array([0.5, -0.55, 0.67]); L /= np.linalg.norm(L)


def lit_disc(cx, cy, R):
    d2 = (nx - cx) ** 2 + (ny - cy) ** 2
    z = np.sqrt(np.clip(R * R - d2, 0, None))
    nn = np.stack([(nx - cx) / R, (ny - cy) / R, z / R], -1)
    lam = np.clip(nn @ L, 0, 1)
    return np.where(d2 < R * R, 0.25 + 0.8 * lam, 0.0)


# plate A (pink): two discs; plate B (teal): two discs offset -> overlaps glow
plateA = np.maximum(lit_disc(-0.28, -0.10, 0.46), lit_disc(0.30, 0.34, 0.30))
plateB = np.maximum(lit_disc(0.22, -0.22, 0.40), lit_disc(-0.18, 0.36, 0.34))

CELL = 8.0
PINK = np.array([0.96, 0.18, 0.52])   # fluoro pink ink (absorption complement applied below)
TEAL = np.array([0.0, 0.70, 0.66])


def screen(intensity, ang, dx=0.0, dy=0.0):
    a = np.radians(ang)
    u = ((xs + dx) * np.cos(a) - (ys + dy) * np.sin(a)) / CELL
    v = ((xs + dx) * np.sin(a) + (ys + dy) * np.cos(a)) / CELL
    spot = (0.5 + 0.5 * np.cos(2 * np.pi * u)) * (0.5 + 0.5 * np.cos(2 * np.pi * v))
    return np.clip((intensity - (1 - spot)) * 6 + 0.5, 0, 1)


# misregistration: each ink's screen + sample offset by a few px in different directions
covA = screen(plateA, 45, dx=4, dy=-3)
covB = screen(plateB, 18, dx=-4, dy=3)

# composite: spot inks are subtractive on white paper (transmittance = 1 - cov*absorb)
paper = np.ones((H, W, 3))
tooth = np.random.default_rng(7).random((H // 5, W // 5))
paper *= (1 - 0.025 * (np.repeat(np.repeat(tooth, 5, 0), 5, 1)[:H, :W] - 0.5))[..., None]
absorbA = 1 - PINK   # how much each channel the pink ink removes
absorbB = 1 - TEAL
out = paper * (1 - covA[..., None] * absorbA[None, None, :])
out *= (1 - covB[..., None] * absorbB[None, None, :])

write_png("../images/riso.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/riso.png")
