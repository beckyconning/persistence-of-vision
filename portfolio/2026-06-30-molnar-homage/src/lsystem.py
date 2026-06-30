"""
L-system plant — the closing piece: a formal-grammar method (string rewriting →
turtle graphics) not yet used in this body of work. Organic and recursive, the
counterpoint to the session's rigid grids. Axiom + production rules iterated to a
depth, then interpreted as turtle moves; branch width tapers and hue runs
trunk-brown → leaf-green with depth (keeping the new colour axis). Lines via the
vectorised stamp engine; a touch of per-turn angle jitter so it reads grown, not
printed.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W, H = 900 * SS, 1100 * SS
rng = np.random.default_rng(12)

# rules (a classic bushy plant)
AXIOM = "X"
RULES = {"X": "F+[[X]-X]-F[-FX]+X", "F": "FF"}
DEPTH = 6
ANGLE = np.radians(24)
STEP = 7.0 * SS

s = AXIOM
for _ in range(DEPTH):
    s = "".join(RULES.get(c, c) for c in s)

trunk = np.array([0.32, 0.22, 0.13])
leaf = np.array([0.30, 0.52, 0.22])
ink = np.zeros((H, W))
colacc = np.zeros((H, W, 3))


def stamp(x0, y0, x1, y1, halfw, col, depth_frac):
    lo_x = int(max(0, np.floor(min(x0, x1) - halfw - 2))); hi_x = int(min(W, np.ceil(max(x0, x1) + halfw + 2)))
    lo_y = int(max(0, np.floor(min(y0, y1) - halfw - 2))); hi_y = int(min(H, np.ceil(max(y0, y1) + halfw + 2)))
    if hi_x <= lo_x or hi_y <= lo_y:
        return
    yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    dist = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    cov = np.clip((halfw - dist) / 1.4 + 0.5, 0, 1)
    sub = ink[lo_y:hi_y, lo_x:hi_x]
    newmask = cov > sub
    ink[lo_y:hi_y, lo_x:hi_x] = np.maximum(sub, cov)
    cc = colacc[lo_y:hi_y, lo_x:hi_x]
    cc[newmask] = col
    colacc[lo_y:hi_y, lo_x:hi_x] = cc


# turtle
x, y = W * 0.5, H - 40 * SS
ang = -np.pi / 2          # pointing up
stack = []
depth = 0
maxdepth = 1
# precompute max nesting for width/colour scaling
d = 0
for c in s:
    if c == "[":
        d += 1; maxdepth = max(maxdepth, d)
    elif c == "]":
        d -= 1
for c in s:
    if c == "F":
        a = ang + rng.normal(0, 0.04)
        nx, ny = x + STEP * np.cos(a), y + STEP * np.sin(a)
        f = depth / maxdepth
        col = trunk * (1 - f) + leaf * f
        hw = (3.2 * (1 - f) + 0.7) * SS / 2
        stamp(x, y, nx, ny, hw, col, f)
        x, y, ang = nx, ny, a
    elif c == "+":
        ang += ANGLE + rng.normal(0, 0.05)
    elif c == "-":
        ang -= ANGLE + rng.normal(0, 0.05)
    elif c == "[":
        stack.append((x, y, ang, depth)); depth += 1
    elif c == "]":
        x, y, ang, depth = stack.pop()


def box(a):
    if a.ndim == 2:
        h, w = a.shape; return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))
    h, w, c = a.shape; return a.reshape(h // SS, SS, w // SS, SS, c).mean((1, 3))


inkd = box(ink); cold = box(colacc)
paper = np.array([0.94, 0.92, 0.86])
mottle = 1.0 + 0.015 * rng.standard_normal((H // SS, W // SS))[..., None]
rgb = paper[None, None, :] * mottle
rgb = rgb * (1 - inkd[..., None]) + cold * inkd[..., None]
write_png(os.path.join(OUT, "lsystem_plant.png"), (np.clip(rgb, 0, 1) * 255).astype(np.uint8))
print("wrote lsystem_plant.png  string len=%d maxdepth=%d" % (len(s), maxdepth))
