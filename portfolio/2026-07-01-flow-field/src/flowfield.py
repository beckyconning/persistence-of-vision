"""
Flow field — a NON-GRID generative system, and a deliberately COOL / DISSONANT palette.

Two frontiers at once (per FRONTIERS.md after s16 colour-field):
  1. Non-grid generative: thousands of particles integrate along a smooth angle
     field (value-noise + two off-centre vortex singularities), tracing streamlines.
     No grid of primitives — the composition emerges from advection.
  2. Cool / dissonant colour: every palette in the corpus so far is warm-harmonious
     or neon-glow. This is cold — steel blue, teal, cold cyan — deliberately SOURED
     by an acid chartreuse and a cold violet that refuse to harmonise with the blues.

And it breaks the repo's soft-GLOW crutch: marks are HARD-EDGE. Each step draws a
thin, near-opaque antialiased thread with OVER compositing (not additive glow), so
the image is a dense woven mat of crisp filaments over a cold near-black ground —
value built from overlapping hard threads, not from luminous blur.

Composition is off-centre: the two vortices sit low-left and upper-right, so the
streams sweep on a diagonal with tension in the empty cold corners.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1400, 1000
rng = np.random.default_rng(20260701)

# ---- cool / dissonant palette (linear-ish 0..1) --------------------------------
GROUND = np.array([0.035, 0.055, 0.085])           # cold near-black (blue-black)
PALETTE = np.array([
    [0.16, 0.34, 0.55],    # steel blue
    [0.12, 0.55, 0.56],    # teal
    [0.36, 0.80, 0.84],    # cold cyan
    [0.70, 0.82, 0.28],    # ACID chartreuse  <- the dissonance
    [0.42, 0.30, 0.62],    # cold violet      <- the second sour note
])
# weights: mostly cold blues/teal, chartreuse + violet are rare accents (the clash)
PAL_W = np.array([0.30, 0.30, 0.20, 0.10, 0.10])

# ---- smooth value-noise angle field --------------------------------------------
def value_noise(w, h, cells):
    """Smoothstep-interpolated random lattice -> smooth scalar field in [0,1]."""
    g = rng.random((cells + 2, cells + 2))
    ys = np.linspace(0, cells, h, endpoint=False)
    xs = np.linspace(0, cells, w, endpoint=False)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    fy = ys - y0; fx = xs - x0
    sy = fy * fy * (3 - 2 * fy); sx = fx * fx * (3 - 2 * fx)   # smoothstep
    def gg(iy, ix): return g[np.add.outer(iy, np.zeros(w, int)), np.add.outer(np.zeros(h, int), ix)]
    v00 = gg(y0, x0);      v10 = gg(y0 + 1, x0)
    v01 = gg(y0, x0 + 1);  v11 = gg(y0 + 1, x0 + 1)
    top = v00 * (1 - sx) + v01 * sx
    bot = v10 * (1 - sx) + v11 * sx
    return top * (1 - sy[:, None]) + bot * sy[:, None]

# base angle from two octaves of noise, then add two vortices (cold turbulence)
ang = value_noise(W, H, 6) * 2 * np.pi + value_noise(W, H, 13) * np.pi
YY, XX = np.mgrid[0:H, 0:W].astype(float)
for (vx, vy, spin) in [(0.30 * W, 0.72 * H, +1.0), (0.74 * W, 0.30 * H, -1.3)]:
    dx = XX - vx; dy = YY - vy
    r = np.hypot(dx, dy) + 1e-6
    swirl = np.arctan2(dy, dx) + spin * np.pi / 2
    falloff = np.exp(-(r / (0.34 * W)) ** 2)          # local influence
    ang = ang * (1 - falloff) + swirl * falloff
FX = np.cos(ang); FY = np.sin(ang)

# ---- hard-edge antialiased thread compositing ----------------------------------
img = np.tile(GROUND, (H, W, 1)).astype(float)

# low-frequency "hue region" field: nearby threads share a palette colour, so the
# streams gather into readable RIBBONS of teal / steel / cyan rather than pixel noise.
HUE = value_noise(W, H, 4)

# precompute round-brush disc offsets (crisp-edged, soft 1px rim)
def disc(radius):
    r = int(np.ceil(radius))
    offs = []
    for oy in range(-r, r + 1):
        for ox in range(-r, r + 1):
            d = np.hypot(ox, oy)
            if d <= radius + 0.5:
                offs.append((oy, ox, max(0.0, min(1.0, radius + 0.5 - d))))
    return offs

def stroke(px, py, col, alpha, offs):
    """OVER-composite a thick round brush -> ribbons, not noise. High alpha keeps
    the top ribbon crisp over its neighbours (woven, not averaged to mud)."""
    ix, iy = int(round(px)), int(round(py))
    for oy, ox, edge in offs:
        yy, xx = iy + oy, ix + ox
        if 1 <= xx < W - 1 and 1 <= yy < H - 1:
            a = alpha * edge
            img[yy, xx] = img[yy, xx] * (1 - a) + col * a

def pick_color(px, py):
    h = HUE[min(int(py), H - 1), min(int(px), W - 1)]
    # most of the field is cold blues/teal/cyan; two thin bands are the sour accents
    if h < 0.30:   return PALETTE[0], False          # steel blue
    if h < 0.58:   return PALETTE[1], False           # teal
    if h < 0.80:   return PALETTE[2], False           # cold cyan
    if h < 0.90:   return PALETTE[3], True            # ACID chartreuse (thin band)
    return PALETTE[4], True                            # cold violet (thin band)

# SHORT + BOLD: ribbons cover ~20% of canvas so 80% of the cold ground breathes;
# high alpha keeps each ribbon a pure hue (top ribbon wins -> woven, never mud).
N_PARTICLES = 230
STEPS = 130
STEP_LEN = 1.45
BRUSH = {False: disc(4.0), True: disc(2.6)}            # accents thinner + brighter
for _ in range(N_PARTICLES):
    while True:                                        # off-centre void -> negative space
        px = rng.random() * W; py = rng.random() * H
        d = np.hypot(px - 0.52 * W, py - 0.46 * H) / (0.5 * W)
        if rng.random() < (0.18 + 0.82 * min(d, 1.0)):
            break
    col, accent = pick_color(px, py)
    steps = int(STEPS * (0.62 if accent else 1.0))
    base_a = 0.9 if accent else 0.82
    offs = BRUSH[accent]
    for s in range(steps):
        ix, iy = int(px), int(py)
        if not (0 <= ix < W and 0 <= iy < H):
            break
        # bold solid body, only the last fifth tapers so the ribbon ends cleanly
        taper = 1.0 if s < steps * 0.8 else 1.0 - (s - steps * 0.8) / (steps * 0.2)
        stroke(px, py, col, base_a * max(taper, 0.0), offs)
        px += FX[iy, ix] * STEP_LEN
        py += FY[iy, ix] * STEP_LEN

np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "flowfield.png"), img)
print("wrote flowfield.png")

# small preview for review (block-mean downsample by 3)
k = 3
hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/ff_preview.png", prev)
print("wrote preview", prev.shape)
