"""Amber. The dusk street on a one-colour phosphor terminal: no colour per cell at all, only which of the
16 quadrant glyphs is lit. Tone comes from Floyd-Steinberg error diffusion run on the quadrant grid, so
the dithering IS the glyph choice. 80 columns, P3 amber, with a faint bloom on the lit quadrants."""
import sys, numpy as np
from PIL import Image, ImageFilter
sys.path.insert(0, "src")
from street import scene

GLYPH = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"
img = scene(0.35)                                       # early evening
lum = img @ np.array([0.30, 0.55, 0.15], np.float32)
lum = np.clip((lum - 0.04) / 0.62, 0, 1) ** 0.85        # stretch into the phosphor's range
COLS = 80
Hq = int(round(lum.shape[0] / lum.shape[1] * COLS / 2)) * 2       # quadrants are 2 source px tall: rows = H/W * 2*COLS / 2, even
q = np.asarray(Image.fromarray((lum * 255).astype(np.uint8)).resize((COLS * 2, Hq), Image.LANCZOS), np.float32) / 255
q = q[:Hq // 2 * 2]
h, w = q.shape
on = np.zeros_like(q, bool)
err = q.copy()
for y in range(h):                                       # serpentine Floyd-Steinberg
    xs = range(w) if y % 2 == 0 else range(w - 1, -1, -1)
    d = 1 if y % 2 == 0 else -1
    for x in xs:
        v = err[y, x]; lit = v >= 0.5; on[y, x] = lit; e = v - (1.0 if lit else 0.0)
        if 0 <= x + d < w: err[y, x + d] += e * 7 / 16
        if y + 1 < h:
            if 0 <= x - d < w: err[y + 1, x - d] += e * 3 / 16
            err[y + 1, x] += e * 5 / 16
            if 0 <= x + d < w: err[y + 1, x + d] += e * 1 / 16
rows = h // 2
lines = []
for r in range(rows):
    s = []
    for c in range(COLS):
        b = on[2 * r, 2 * c] * 1 + on[2 * r, 2 * c + 1] * 2 + on[2 * r + 1, 2 * c] * 4 + on[2 * r + 1, 2 * c + 1] * 8
        s.append(GLYPH[b])
    lines.append("".join(s))
with open("amber-80x%d.ans" % rows, "w", encoding="utf-8") as f:
    f.write("\n".join("\x1b[38;2;255;176;0m\x1b[48;2;18;8;0m" + l + "\x1b[0m" for l in lines) + "\n")
CW, CH = 10, 20
px = np.zeros((rows * CH, COLS * CW), np.float32)
for y in range(h):
    for x in range(w):
        if on[y, x]: px[y * CH // 2:(y + 1) * CH // 2, x * CW // 2:(x + 1) * CW // 2] = 1
glow = np.asarray(Image.fromarray((px * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(3)), np.float32) / 255
amber = np.array([255, 176, 0], np.float32); ground = np.array([18, 8, 0], np.float32)
out = ground + (amber - ground) * np.clip(px * 0.92 + glow * 0.35, 0, 1)[..., None]
scan = (np.arange(out.shape[0]) % 4 == 3)[:, None, None]                     # faint scanlines
out = np.where(scan, out * 0.82, out)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save("amber.png")
print(COLS, "x", rows, "lit quadrants", int(on.sum()), "of", on.size)
