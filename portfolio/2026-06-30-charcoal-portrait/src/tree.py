"""Charcoal — a lone tree in mist. Session variety: an atmospheric landscape (vs faces/objects).
Recursive tapered branches drawn as dark charcoal strokes against a graded misty ground; far
twigs FADE into the fog (atmospheric perspective) so the tree dissolves upward — the smudgy,
breathing quality charcoal does best. Warm toned paper, soft ground shadow, vignette.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H

ink = np.zeros((H, W))   # darkness accumulator (charcoal laid down)
rng = np.random.default_rng(7)


def stroke(x0, y0, x1, y1, w0, w1):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    w = w0 + (w1 - w0) * t
    return np.clip((w - d) / 0.0025, 0, 1)


def branch(x, y, ang, length, width, depth):
    if depth <= 0 or length < 0.012:
        return
    x2 = x + np.cos(ang) * length
    y2 = y + np.sin(ang) * length
    # higher (smaller y) + thinner branches fade — atmospheric perspective into mist
    fade = np.clip(0.35 + 0.65 * (y2), 0, 1)
    global ink
    ink = np.maximum(ink, stroke(x, y, x2, y2, width, width * 0.62) * (0.55 + 0.45 * fade))
    n = 2 if depth > 2 else 2
    for _ in range(n):
        da = rng.uniform(0.30, 0.62) * (1 if rng.random() > 0.5 else -1)
        ls = rng.uniform(0.62, 0.82)
        branch(x2, y2, ang + da + rng.uniform(-0.06, 0.06), length * ls, width * 0.66, depth - 1)
    # occasional straight-ish continuation
    if rng.random() > 0.4:
        branch(x2, y2, ang + rng.uniform(-0.18, 0.18), length * 0.8, width * 0.7, depth - 1)


# trunk base lower-centre, growing up (negative y)
branch(0.46, 0.92, -np.radians(90), 0.20, 0.013, 8)

# soften (charcoal) + a little broken-stroke texture
def blurr(a, r):
    def b1(a, r, ax):
        n = a.shape[ax]; cs = np.cumsum(a, axis=ax)
        cs = np.concatenate([np.zeros_like(np.take(cs, [0], ax)), cs], axis=ax)
        lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
        cnt = (hi - lo).astype(float); sh = [1, 1]; sh[ax] = n
        return (np.take(cs, hi, ax) - np.take(cs, lo, ax)) / cnt.reshape(sh)
    for _ in range(2):
        a = b1(a, r, 0); a = b1(a, r, 1)
    return a

ink = blurr(ink, 1)
ink = np.clip(ink, 0, 1)

# ---- misty background: light at top (fog), warm ground lower; soft horizon band ----
sky = 0.86 - 0.10 * (0.5 - np.abs(ny - 0.35))       # luminous upper mist
ground = 0.74 - 0.10 * (ny - 0.78)
base = np.where(ny < 0.80, sky, ground)
base = blurr(base, 8)
# faint ground shadow pooled under the tree
gshadow = np.clip(1 - (((nx - 0.46) / 0.13) ** 2 + ((ny - 0.93) / 0.02) ** 2), 0, 1)
base = base * (1 - 0.25 * blurr(gshadow, 4))

# ---- compose: charcoal ink over misty paper ----
paper = np.array([0.84, 0.81, 0.74])
charc = np.array([0.10, 0.10, 0.13])
val = base * (1 - ink) + 0.12 * ink
val = np.clip(val, 0, 1)
img = charc[None, None, :] + (paper - charc)[None, None, :] * val[..., None]
# paper tooth + faint drifting mist (low-freq noise lightening upper area)
g = rng.random((8, 8)); mist = blurr(g[(ys / H * 7).astype(int), (xs / W * 7).astype(int)], 60)
img = img + (0.05 * (mist - 0.5) * np.clip(1 - ny, 0, 1))[..., None]
vig = 1 - 0.18 * ((nx - 0.46) ** 2 + (ny - 0.5) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/tree.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/tree.png")
