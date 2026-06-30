"""Cyanotype star chart — a 'blueprint of the sky'. White stars (sized by magnitude),
constellation lines, a faint RA/Dec grid + ecliptic, a soft Milky-Way band — on Prussian
blue. Bridges the photogram + blueprint traditions: an antique celestial atlas as cyanotype."""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
rng = np.random.default_rng(13)
cx, cy, R = 0.5, 0.5, 0.46


def blur(a, r):
    k = np.ones(2 * r + 1) / (2 * r + 1)
    a = np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 1, a)
    return np.apply_along_axis(lambda m: np.convolve(m, k, "same"), 0, a)


light = np.zeros((H, W))  # white-ink accumulator
rr = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
indisc = rr < R

# faint grid: concentric dec circles + radial RA lines (thin)
ang = np.arctan2(ny - cy, nx - cx)
for ri in np.linspace(0.12, R, 4):
    light = np.maximum(light, 0.18 * (np.abs(rr - ri) < 0.0015) * indisc)
for k in range(12):
    a = k / 12 * 2 * np.pi
    light = np.maximum(light, 0.18 * (np.abs(((ang - a + np.pi) % (2 * np.pi)) - np.pi) < 0.004) * (rr < R))
# chart border (double circle)
light = np.maximum(light, (np.abs(rr - R) < 0.003).astype(float))
light = np.maximum(light, (np.abs(rr - R * 1.03) < 0.0015).astype(float))
# ecliptic (a tilted great-circle arc → an offset circle band)
light = np.maximum(light, 0.3 * (np.abs(np.sqrt((nx - cx) ** 2 + ((ny - cy) / 0.55) ** 2) - 0.42) < 0.002) * indisc)

# Milky Way: faint diagonal band of dense tiny stars + soft glow
band = np.exp(-(((nx - cx) * 0.7 + (ny - cy) * 0.7) / 0.10) ** 2) * indisc
light = np.maximum(light, 0.10 * blur(band, 6))

# stars: positions inside the disc, magnitude → size
def star(px, py, mag):
    s = 0.0016 + 0.006 * (1 - mag)   # brighter (low mag) → bigger
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    core = np.clip((s - d) / 0.0015, 0, 1)
    glint = 0.0
    if mag < 0.35:  # bright stars get a 4-point glint
        gl = 0.02 * (1 - mag)
        glint = np.clip((0.0009 - np.abs(nx - px)) / 0.0009, 0, 1) * (np.abs(ny - py) < gl)
        glint = np.maximum(glint, np.clip((0.0009 - np.abs(ny - py)) / 0.0009, 0, 1) * (np.abs(nx - px) < gl))
    return np.maximum(core, 0.9 * glint)


# field stars
n_field = 260
pts = []
for _ in range(n_field):
    a = rng.uniform(0, 2 * np.pi); rad = R * np.sqrt(rng.uniform(0, 1))
    px, py = cx + np.cos(a) * rad, cy + np.sin(a) * rad
    mag = rng.uniform(0.2, 1.0) ** 1.5  # mostly faint
    if abs((px - cx) * 0.7 + (py - cy) * 0.7) < 0.12:
        mag *= 0.7  # denser/brighter near the milky-way band
    light = np.maximum(light, star(px, py, mag))
    pts.append((px, py, mag))

# a constellation: pick 7 bright-ish stars, connect into a figure (a 'plough'-like asterism)
bright = sorted(pts, key=lambda p: p[2])[:40]
con = [bright[i] for i in (2, 5, 9, 14, 20, 27, 33)]
def line(x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0; L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    d = np.sqrt((nx - (x0 + t * dx)) ** 2 + (ny - (y0 + t * dy)) ** 2)
    return 0.4 * np.clip((0.0012 - d) / 0.0012, 0, 1) * ((t > 0) & (t < 1))
for i in range(len(con) - 1):
    light = np.maximum(light, line(con[i][0], con[i][1], con[i + 1][0], con[i + 1][1]))

light = np.clip(blur(light, 1) * 1.3, 0, 1)

def vn(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


expo = np.clip(0.72 + 0.48 * blur(vn(6, 4), 18), 0, 1)
deep = np.array([0.05, 0.17, 0.36]); lite = np.array([0.10, 0.25, 0.45]); pale = np.array([0.90, 0.94, 0.98])
blue = deep[None, None, :] * expo[..., None] + lite[None, None, :] * (1 - expo)[..., None]
# outside the chart disc → lighter paper margin
paper_margin = np.array([0.80, 0.86, 0.92])
base = np.where(indisc[..., None], blue, blue * 0.7 + paper_margin[None, None, :] * 0.3)
m = light[..., None]
img = base * (1 - m) + pale[None, None, :] * m
img *= (1 - 0.04 * (vn(W // 3, 9) - 0.5))[..., None]
write_png("../images/starchart.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/starchart.png")
