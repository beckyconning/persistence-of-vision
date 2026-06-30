"""
Homage to Vera Molnar — "(Des)Ordres".

A deliberate move OUT of the portrait corner the recent work has lived in
(s2/3/11/13/14 were all faces). New axes: CONCEPT/LINEAGE (a generative piece
honouring a pioneer of generative art — a direct ancestor) and METHOD (rule-based
plotter geometry, not value-blocked tone). Molnar's signature, ~1974: a grid of
nested concentric squares, near-identical at one corner (ORDER) and progressively
perturbed toward the opposite corner (DISORDER) — the rule is legible in the image
(LeWitt-adjacent). Monochrome plotter ink on warm paper; one red cell, as she
sometimes allowed herself.

Tone is NOT painted — the picture is line. Each square edge is stamped onto a 2x
supersampled coverage buffer (point-to-segment distance, bbox-limited) then
box-downscaled for clean anti-aliased pen strokes.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W = H = 1000 * SS
GRID = 11
SQUARES = 6
MARGIN = 0.085 * W
rng = np.random.default_rng(3)

ink = np.zeros((H, W), float)
redb = np.zeros((H, W), float)

ys_full = np.arange(H)
xs_full = np.arange(W)


def stamp_segment(buf, p0, p1, halfw):
    """Add soft coverage for a round-capped segment of half-width `halfw` (px)."""
    x0, y0 = p0
    x1, y1 = p1
    lo_x = int(max(0, np.floor(min(x0, x1) - halfw - 2)))
    hi_x = int(min(W, np.ceil(max(x0, x1) + halfw + 2)))
    lo_y = int(max(0, np.floor(min(y0, y1) - halfw - 2)))
    hi_y = int(min(H, np.ceil(max(y0, y1) + halfw + 2)))
    if hi_x <= lo_x or hi_y <= lo_y:
        return
    yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
    px, py = xx - x0, yy - y0
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else np.clip((px * dx + py * dy) / L2, 0, 1)
    cx, cy = x0 + t * dx, y0 + t * dy
    dist = np.hypot(xx - cx, yy - cy)
    cov = np.clip((halfw - dist) / 1.4 + 0.5, 0, 1)   # soft 1.4px edge
    buf[lo_y:hi_y, lo_x:hi_x] = np.maximum(buf[lo_y:hi_y, lo_x:hi_x], cov)


def square(cx, cy, half, rot, jit):
    """Four corners of a square, each displaced by gaussian jitter `jit` and the
    whole rotated by `rot` radians."""
    base = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]], float) * half
    c, s = np.cos(rot), np.sin(rot)
    R = np.array([[c, -s], [s, c]])
    pts = base @ R.T
    pts = pts + rng.normal(0, jit, pts.shape)
    return [(cx + x, cy + y) for x, y in pts]


cell = (W - 2 * MARGIN) / GRID
# the one red cell (a quiet asymmetry, Molnar-style): off-centre
red_cell = (7, 3)

for gy in range(GRID):
    for gx in range(GRID):
        cx = MARGIN + (gx + 0.5) * cell
        cy = MARGIN + (gy + 0.5) * cell
        # disorder grows toward the bottom-right corner (order at top-left)
        d = ((gx / (GRID - 1)) + (gy / (GRID - 1))) / 2.0
        d = d ** 1.4
        rot_amt = d * 0.55
        jit_amt = d * cell * 0.16
        buf = redb if (gx, gy) == red_cell else ink
        for k in range(SQUARES):
            half = cell * 0.42 * (1 - k / SQUARES)
            if half < 2:
                continue
            rot = rng.normal(0, rot_amt)
            corners = square(cx, cy, half, rot, jit_amt)
            for i in range(4):
                stamp_segment(buf, corners[i], corners[(i + 1) % 4], halfw=1.1 * SS / 2)

# ── downscale (box) + composite paper/ink/red ───────────────────────────────
def box(a):
    h, w = a.shape
    return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))

inkd = box(ink)
redd = box(redb)
paper = np.array([0.94, 0.91, 0.84])
inkc = np.array([0.11, 0.10, 0.13])
redc = np.array([0.74, 0.13, 0.12])
mottle = 1.0 + 0.018 * rng.standard_normal((H // SS, W // SS))[..., None]
rgb = paper[None, None, :] * mottle
rgb = rgb * (1 - inkd[..., None]) + inkc[None, None, :] * inkd[..., None]
rgb = rgb * (1 - redd[..., None]) + redc[None, None, :] * redd[..., None]
rgb = np.clip(rgb, 0, 1)
write_png(os.path.join(OUT, "desordres.png"), (rgb * 255).astype(np.uint8))
print("wrote desordres.png  ink=%.3f red=%.3f" % (inkd.mean(), redd.mean()))
