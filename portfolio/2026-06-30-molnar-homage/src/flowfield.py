"""
Flow field — as discrete pen strokes, NOT the s1 density-glow corner.

The one classic generative system this body of work hadn't revisited since the
first gallery — but done in the new idiom: short tapered INK strokes seeded across
the page, each advected a few steps along a smooth value-noise vector field, drawn
as plotter lines on paper (no additive accumulation, no glow-on-black). Hue runs
with stroke direction over a restrained three-colour set — closing the session's
colour thread.
"""
import os
import numpy as np
from pnglib import write_png, ramp

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W, H = 950 * SS, 950 * SS
rng = np.random.default_rng(21)

ink = np.zeros((H, W))
colacc = np.zeros((H, W, 3))


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


field = vnoise(7) * np.pi * 2.0      # smooth angle field
stops = [(0.20, 0.30, 0.46), (0.32, 0.52, 0.40), (0.82, 0.52, 0.22)]  # blue→green→amber


def stamp(x0, y0, x1, y1, halfw, col):
    lo_x = int(max(0, min(x0, x1) - halfw - 2)); hi_x = int(min(W, max(x0, x1) + halfw + 2))
    lo_y = int(max(0, min(y0, y1) - halfw - 2)); hi_y = int(min(H, max(y0, y1) + halfw + 2))
    if hi_x <= lo_x or hi_y <= lo_y:
        return
    yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    dist = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    cov = np.clip((halfw - dist) / 1.4 + 0.5, 0, 1)
    sub = ink[lo_y:hi_y, lo_x:hi_x]
    m = cov > sub
    ink[lo_y:hi_y, lo_x:hi_x] = np.maximum(sub, cov)
    cc = colacc[lo_y:hi_y, lo_x:hi_x]; cc[m] = col; colacc[lo_y:hi_y, lo_x:hi_x] = cc


def angle_at(x, y):
    ix = min(W - 1, max(0, int(x))); iy = min(H - 1, max(0, int(y)))
    return field[iy, ix]


N = 1700
STEPS = 14
hstep = 5.0 * SS
for _ in range(N):
    x = rng.uniform(0, W); y = rng.uniform(0, H)
    a0 = angle_at(x, y)
    col = ramp(np.array((np.cos(a0) + 1) / 2), stops)     # hue by direction
    for k in range(STEPS):
        a = angle_at(x, y)
        nx, ny = x + hstep * np.cos(a), y + hstep * np.sin(a)
        hw = (1.7 * (1 - k / STEPS) + 0.5) * SS / 2        # taper along the stroke
        stamp(x, y, nx, ny, hw, col)
        x, y = nx, ny
        if not (0 <= x < W and 0 <= y < H):
            break


def box(a):
    if a.ndim == 2:
        h, w = a.shape; return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))
    h, w, c = a.shape; return a.reshape(h // SS, SS, w // SS, SS, c).mean((1, 3))


inkd, cold = box(ink), box(colacc)
paper = np.array([0.94, 0.92, 0.86])
mottle = 1.0 + 0.014 * rng.standard_normal((H // SS, W // SS))[..., None]
rgb = paper[None, None, :] * mottle
rgb = rgb * (1 - inkd[..., None]) + cold * inkd[..., None]
write_png(os.path.join(OUT, "flowfield_strokes.png"), (np.clip(rgb, 0, 1) * 255).astype(np.uint8))
print("wrote flowfield_strokes.png  %d strokes" % N)
