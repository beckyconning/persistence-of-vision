# the-agreement: a daylight halftone diptych from real escape counts.
# Left: the blank deep1e100 view both renderers agreed on (every pixel n = 42245).
# Right: the same depth after the fix, 362 distinct counts, as halftone dots ranked by count.
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
W, H = 192, 108
S = 2                                   # supersample
PAPER = (242, 237, 227)
INK = (38, 36, 34)
VERMILION = (196, 66, 42)
CW, CH = 2400 * S, 1500 * S

def load(name):
    raw = np.fromfile(D + name, dtype=np.uint8).reshape(H * W, 8)
    n = raw[:, 0:4].copy().view(np.uint32).reshape(H, W).astype(np.float64)
    frac = raw[:, 4:8].copy().view(np.float32).reshape(H, W).astype(np.float64)
    return n + frac, n.astype(np.uint32)

old_v, old_n = load('old.bin')
new_v, new_n = load('new.bin')

img = Image.new('RGB', (CW, CH), PAPER)
dr = ImageDraw.Draw(img)
mono = lambda px: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', px * S)
serif = lambda px: ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', px * S)

def halftone(x0, y0, cell, darkness):
    """darkness in [0,1] per data cell -> ink dot whose area is proportional to darkness."""
    for j in range(H):
        for i in range(W):
            d = darkness[j, i]
            if d <= 0.01:
                continue
            r = 0.5 * cell * np.sqrt(d) * 1.05
            cx = x0 + (i + 0.5) * cell
            cy = y0 + (j + 0.5) * cell
            dr.ellipse([cx - r, cy - r, cx + r, cy + r], fill=INK)

cell = 5.0 * S
pw, ph = W * cell, H * cell

# Left panel: the agreement. One value everywhere -> one uniform tone (mid grey, as the value sits mid-range).
lx, ly = 150 * S, 330 * S
uniform = np.full((H, W), 0.42)
halftone(lx, ly, cell, uniform)

# Right panel: the second question. Rank-order the counts so the ink follows the data's own ordering.
rx, ry = lx + pw + 150 * S, 500 * S
flat = new_v.ravel()
ranks = flat.argsort().argsort().reshape(H, W) / (flat.size - 1)
darkness = 1.0 - ranks                  # slowest escapes (nearest the set) print lightest: paper shows the filaments
halftone(rx, ry, cell, darkness ** 1.6)

# Registration rule that ties the two plates: the parity result both carried.
rule_y = ry + ph + 80 * S
dr.line([lx, rule_y, rx + pw, rule_y], fill=INK, width=2 * S)
dr.line([lx, rule_y - 14 * S, lx, rule_y + 14 * S], fill=INK, width=2 * S)
dr.line([rx + pw, rule_y - 14 * S, rx + pw, rule_y + 14 * S], fill=INK, width=2 * S)

def text(x, y, s, font, fill=INK, anchor='la'):
    dr.text((x, y), s, font=font, fill=fill, anchor=anchor)

text(lx, ly - 70 * S, 'what both renderers agreed on', serif(34))
text(lx, ly + ph + 18 * S, 'deep1e100 · every pixel n = 42245 · 20736 of 20736', mono(20))
text(lx, rule_y + 26 * S, 'gpu vs cpu   status 1.0000   n-exact 1.0000   PASS', mono(22))
text(rx, ry - 70 * S, 'the second question: how many different?', serif(34))
text(rx, ry + ph + 18 * S, 'M(23,2) · 362 distinct counts · 10528 to 11098', mono(20))
# the answer to the first plate's question, in the one accent colour
text(lx + pw, ly + ph + 60 * S, '1', serif(150), fill=VERMILION, anchor='ra')
text(rx + pw, ry - 250 * S, '362', serif(150), fill=INK, anchor='ra')
text(150 * S, CH - 110 * S, 'the agreement  ·  Mandeldive build, 2026-09-13  ·  agreement between two renderers is not evidence of an image', mono(20))

img = img.resize((CW // S, CH // S), Image.LANCZOS)
img.save(D + 'the-agreement.png')
print('saved')
