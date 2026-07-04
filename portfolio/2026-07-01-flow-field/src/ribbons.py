"""
Flow field, take 2 — OPAQUE HARD-EDGE ribbons (the fix my own dead-end NOTES prescribed).

The first attempt drowned in grey: thousands of soft alpha-disc stamps of clashing hues
composited toward the mean. The fix: draw few (~130) LONG streamlines, each as a single
CONSTANT-colour, near-opaque, hard-edged ribbon. OVER-composite so the top ribbon WINS at
every pixel (a woven overlap, never an average) — that is what keeps a cool/dissonant
palette dissonant instead of neutralising it.

Palette stays cold and soured (steel/teal/cyan + acid chartreuse + cold violet), but now a
ribbon is one pure hue end to end. The two off-centre vortices organise the weave; the cold
near-black ground breathes in the gaps (few, thick strokes => low coverage).
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1400, 1000
rng = np.random.default_rng(70107)

GROUND = np.array([0.030, 0.048, 0.078])
PALETTE = np.array([
    [0.18, 0.40, 0.66],    # steel blue
    [0.10, 0.62, 0.62],    # teal
    [0.44, 0.86, 0.90],    # cold cyan
    [0.78, 0.90, 0.30],    # ACID chartreuse
    [0.52, 0.34, 0.74],    # cold violet
])
PAL_W = np.array([0.30, 0.30, 0.20, 0.10, 0.10])

def value_noise(w, h, cells):
    g = rng.random((cells + 2, cells + 2))
    ys = np.linspace(0, cells, h, endpoint=False); xs = np.linspace(0, cells, w, endpoint=False)
    y0 = np.floor(ys).astype(int); x0 = np.floor(xs).astype(int)
    fy = ys - y0; fx = xs - x0
    sy = fy * fy * (3 - 2 * fy); sx = fx * fx * (3 - 2 * fx)
    def gg(iy, ix): return g[np.add.outer(iy, np.zeros(w, int)), np.add.outer(np.zeros(h, int), ix)]
    v00 = gg(y0, x0); v10 = gg(y0 + 1, x0); v01 = gg(y0, x0 + 1); v11 = gg(y0 + 1, x0 + 1)
    top = v00 * (1 - sx) + v01 * sx; bot = v10 * (1 - sx) + v11 * sx
    return top * (1 - sy[:, None]) + bot * sy[:, None]

ang = value_noise(W, H, 3) * 2 * np.pi        # single LOW-freq octave -> long smooth arcs, not scribble
YY, XX = np.mgrid[0:H, 0:W].astype(float)
for (vx, vy, spin) in [(0.28 * W, 0.70 * H, +1.0), (0.76 * W, 0.30 * H, -1.25)]:
    dx = XX - vx; dy = YY - vy; r = np.hypot(dx, dy) + 1e-6
    swirl = np.arctan2(dy, dx) + spin * np.pi / 2
    fall = np.exp(-(r / (0.36 * W)) ** 2)
    ang = ang * (1 - fall) + swirl * fall
FX = np.cos(ang); FY = np.sin(ang)

img = np.tile(GROUND, (H, W, 1)).astype(float)

def disc(radius):
    r = int(np.ceil(radius)); offs = []
    for oy in range(-r, r + 1):
        for ox in range(-r, r + 1):
            if np.hypot(ox, oy) <= radius:            # HARD edge (no soft rim)
                offs.append((oy, ox))
    return offs

def draw_seg(x0, y0, x1, y1, col, offs):
    """Opaque hard round brush swept along a segment (fully overwrites -> top wins)."""
    n = max(1, int(np.hypot(x1 - x0, y1 - y0)))
    for t in np.linspace(0, 1, n):
        cx = int(round(x0 + (x1 - x0) * t)); cy = int(round(y0 + (y1 - y0) * t))
        for oy, ox in offs:
            xx, yy = cx + ox, cy + oy
            if 0 <= xx < W and 0 <= yy < H:
                img[yy, xx] = col

N = 150
STEPS = 300
STEP = 1.5
MAIN = disc(4.5); ACC = disc(3.0)
# draw longest/darkest first, brightest accents last, so accents sit ON TOP (punctuation)
order = []
for _ in range(N):
    ci = rng.choice(len(PALETTE), p=PAL_W)
    order.append(ci)
order.sort()                                           # 0..2 (cold) first, 3..4 (accents) last
for ci in order:
    col = PALETTE[ci]; accent = ci >= 3
    offs = ACC if accent else MAIN
    steps = int(STEPS * (0.5 if accent else 1.0))
    while True:                                        # seed off the centre -> negative space
        px = rng.random() * W; py = rng.random() * H
        d = np.hypot(px - 0.5 * W, py - 0.46 * H) / (0.5 * W)
        if rng.random() < (0.15 + 0.85 * min(d, 1.0)):
            break
    for _ in range(steps):
        ix, iy = int(px), int(py)
        if not (0 <= ix < W and 0 <= iy < H):
            break
        nx = px + FX[iy, ix] * STEP; ny = py + FY[iy, ix] * STEP
        draw_seg(px, py, nx, ny, col, offs)
        px, py = nx, ny

np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "ribbons.png"), (img * 255).astype(np.uint8))
k = 3; hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rib_preview.png", (prev * 255).astype(np.uint8))
print("wrote ribbons.png + preview")
