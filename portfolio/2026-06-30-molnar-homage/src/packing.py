"""
Circle packing — the non-grid coda.

The s15 stills leaned on a grid of rotated primitives (the mini-rut). This breaks
it: a largest-empty-circle packing — repeatedly drop a random point, grow a circle
to just touch its nearest neighbour (or the bounds), keep it if big enough. Organic,
space-filling, NO grid; and it keeps the new colour axis (hue mapped to radius:
the big circles read warm/focal — red, orange, olive — floating in a sea of small
cool teal/blue ones), flat fields on paper. Not the s1 density-glow corner
(discrete placement + constraint, not accumulation).
"""
import os
import numpy as np
from pnglib import write_png, ramp

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 1100
rng = np.random.default_rng(8)

MARGIN = 60
RMAX, RMIN = 130.0, 2.2
ATTEMPTS = 26000

cx = np.empty(0); cy = np.empty(0); cr = np.empty(0)
placed = []
for _ in range(ATTEMPTS):
    x = rng.uniform(MARGIN, W - MARGIN); y = rng.uniform(MARGIN, H - MARGIN)
    # max radius = min(distance to bounds, distance to nearest circle edge)
    rb = min(x - MARGIN, W - MARGIN - x, y - MARGIN, H - MARGIN - y)
    if placed:
        d = np.hypot(cx - x, cy - y) - cr
        rb = min(rb, d.min())
    if rb >= RMIN:
        r = min(rb, RMAX)
        placed.append((x, y, r))
        cx = np.append(cx, x); cy = np.append(cy, y); cr = np.append(cr, r)

# ── render: flat-filled circles, hue by radius (big→cool, small→warm) ─────────
paper = np.array([0.93, 0.91, 0.85])
img = np.ones((H, W, 3)) * paper
stops = [(0.80, 0.30, 0.20), (0.85, 0.55, 0.22), (0.55, 0.62, 0.38),
         (0.22, 0.52, 0.55), (0.18, 0.32, 0.46)]   # warm(small) → cool(big)
rmin_p, rmax_p = cr.min(), cr.max()
yy, xx = np.mgrid[0:H, 0:W]
order = np.argsort(-cr)                              # big first, small drawn on top
for idx in order:
    x, y, r = cx[idx], cy[idx], cr[idx]
    t = (r - rmin_p) / (rmax_p - rmin_p + 1e-9)      # 0 small .. 1 big
    col = ramp(np.array(1 - t), stops)               # small→warm end
    lo_y = max(0, int(y - r - 1)); hi_y = min(H, int(y + r + 2))
    lo_x = max(0, int(x - r - 1)); hi_x = min(W, int(x + r + 2))
    sub_y = yy[lo_y:hi_y, lo_x:hi_x]; sub_x = xx[lo_y:hi_y, lo_x:hi_x]
    d = np.hypot(sub_x - x, sub_y - y)
    cov = np.clip(r - d, 0, 1)                        # 1px AA edge
    ring = np.clip(d - (r - 2.2), 0, 1) * np.clip(r - d, 0, 1)  # faint darker rim
    patch = img[lo_y:hi_y, lo_x:hi_x]
    base = col[None, None, :] * (1 - 0.16 * ring[..., None])
    img[lo_y:hi_y, lo_x:hi_x] = patch * (1 - cov[..., None]) + base * cov[..., None]

write_png(os.path.join(OUT, "circle_packing.png"), (np.clip(img, 0, 1) * 255).astype(np.uint8))
print("wrote circle_packing.png  %d circles, r %.1f..%.1f" % (len(placed), rmin_p, rmax_p))
