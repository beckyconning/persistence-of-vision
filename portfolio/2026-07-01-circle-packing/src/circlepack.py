"""
Circle packing — a NON-GRID generative technique the corpus hasn't touched, and a deliberate
WARM / harmonious palette as a counterpoint to the same day's cold-dissonance + cold flow-field.

Greedy largest-first packing: for each radius (large -> small), throw darts; keep a circle only if
it clears every placed circle (and the frame) by a small gap. The result is an organic, gap-filling
mosaic — dense small circles crowd the interstices between the big ones. Circles are drawn as filled
ANTI-ALIASED discs (crisp edge, 1px feather), coloured from a warm jewel palette weighted so the
ground reads deep and the highlights (gold/cream) are rare — a considered warm scheme, not neon glow.

Off-centre weighting: a soft radial bias makes the big circles cluster low-right, so the packing has
a focal mass and the upper-left breathes. Uses the pnglib uint8 contract correctly from the start.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1400, 1000
rng = np.random.default_rng(31415)

GROUND = np.array([0.06, 0.09, 0.12])            # deep slate ground
# warm jewel palette (deep -> bright); weighted so brights are rare accents
PALETTE = np.array([
    [0.72, 0.28, 0.20],   # rust / terracotta
    [0.85, 0.45, 0.22],   # burnt orange
    [0.90, 0.62, 0.28],   # amber
    [0.93, 0.80, 0.52],   # pale gold
    [0.55, 0.20, 0.28],   # oxblood
    [0.30, 0.42, 0.45],   # muted teal (the single cool note, for tension)
])
PAL_W = np.array([0.26, 0.24, 0.18, 0.10, 0.14, 0.08])

img = np.tile(GROUND, (H, W, 1)).astype(float)

# --- packing ---
circles = []   # (cx, cy, r)
GAP = 2.0
def fits(cx, cy, r):
    if cx - r < 2 or cy - r < 2 or cx + r > W - 2 or cy + r > H - 2:
        return False
    for (ox, oy, orr) in circles:
        if (cx - ox) ** 2 + (cy - oy) ** 2 < (r + orr + GAP) ** 2:
            return False
    return True

# radii from big to small; more dart-throws as they shrink (fill interstices)
radii = np.concatenate([
    np.full(60, 95.0) * rng.uniform(0.6, 1.0, 60),
    np.full(220, 46.0) * rng.uniform(0.5, 1.0, 220),
    np.full(900, 20.0) * rng.uniform(0.5, 1.0, 900),
    np.full(4000, 8.0) * rng.uniform(0.5, 1.0, 4000),
])
for r in radii:
    for _try in range(24):
        # off-centre bias: pull samples toward low-right focal mass
        cx = np.clip(rng.normal(0.62 * W, 0.30 * W), r, W - r)
        cy = np.clip(rng.normal(0.60 * H, 0.30 * H), r, H - r)
        if fits(cx, cy, r):
            circles.append((cx, cy, r))
            break

# --- draw filled AA discs (colour by size: big=deep, small=bright accents skew) ---
YY, XX = np.mgrid[0:H, 0:W]
rmax = max(c[2] for c in circles)
for (cx, cy, r) in circles:
    # smaller circles lean toward the brighter/among-accent palette entries
    small = 1.0 - min(r / rmax, 1.0)
    w = PAL_W * (1.0 + small * np.array([0, 0.3, 0.8, 1.6, 0, 0.4]))
    w = w / w.sum()
    col = PALETTE[rng.choice(len(PALETTE), p=w)]
    x0, x1 = int(cx - r - 2), int(cx + r + 2)
    y0, y1 = int(cy - r - 2), int(cy + r + 2)
    sub = (XX[y0:y1, x0:x1] - cx) ** 2 + (YY[y0:y1, x0:x1] - cy) ** 2
    d = np.sqrt(sub)
    a = np.clip(r - d + 0.5, 0.0, 1.0)[..., None]     # 1px AA feather at the rim
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - a) + col * a

np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "circlepack.png"), (img * 255).astype(np.uint8))
print(f"wrote circlepack.png ({len(circles)} circles)")
