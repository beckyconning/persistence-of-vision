"""Pop-art benday dots (Lichtenstein scale) — coarse dots + flat spot colour + a bold black
key line. Distinct SCALE/aesthetic from the fine CMYK rosette: posterized tone, big dots,
limited palette. Subject: a bold rising sun over a band — graphic, printy, optimistic."""
import numpy as np
from pnglib import write_png

H = W = 1100
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - H / 2) / (H / 2)
CELL = 22.0  # COARSE benday cell


def dots(intensity, ang=15.0):
    a = np.radians(ang)
    u = (xs * np.cos(a) - ys * np.sin(a)) / CELL
    v = (xs * np.sin(a) + ys * np.cos(a)) / CELL
    spot = (0.5 + 0.5 * np.cos(2 * np.pi * u)) * (0.5 + 0.5 * np.cos(2 * np.pi * v))
    return np.clip((intensity - (1 - spot)) * 8 + 0.5, 0, 1)


# sky: graded benday red dots, denser toward the top corners (posterized to 3 levels)
sky = np.clip(0.25 + 0.55 * (ny + 0.2) + 0.2 * np.abs(nx), 0, 1)
sky = np.round(sky * 3) / 3
# sun: solid disc, off-centre (rule of thirds)
sun = (nx + 0.32) ** 2 + (ny + 0.18) ** 2 < 0.30 ** 2
# rays: alternating wedges behind the sun
ang = np.arctan2(ny + 0.18, nx + 0.32)
rays = ((np.floor(ang / (np.pi / 9)) % 2) == 0) & (~sun)

paper = np.ones((H, W, 3))
RED = np.array([0.93, 0.26, 0.21]); YELL = np.array([0.99, 0.80, 0.12]); BLUE = np.array([0.18, 0.35, 0.70])
out = paper.copy()
# benday red sky dots
out *= (1 - dots(sky, 15)[..., None] * (1 - RED)[None, None, :])
# faint blue ray benday over sky (subtle), only in ray wedges
out *= (1 - (dots(0.45 * rays, 75))[..., None] * (1 - BLUE)[None, None, :])
# solid yellow sun
out = np.where(sun[..., None], YELL[None, None, :], out)
# bold black key line around the sun (annulus)
r = np.sqrt((nx + 0.32) ** 2 + (ny + 0.18) ** 2)
ring = (np.abs(r - 0.30) < 0.012)
out = np.where(ring[..., None], 0.08, out)

write_png("../images/benday.png", np.clip(out * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/benday.png")
