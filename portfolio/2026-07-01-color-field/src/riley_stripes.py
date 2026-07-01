"""
Hard-edge colour — after Bridget Riley's stripe paintings (her colour period).

The counterpoint to the soft fields in this session, and the answer to the
frontier I just filed: colour interaction with NO glow crutch — flat, hard-edged
vertical bands whose optical vibration comes purely from the SEQUENCE of hues and
the widths. A cool base (teals / blues / violets / greens) with sparse warm accents
(rose, amber) placed by contrast-of-extension so a little warm charges the whole
cool field. Precise rhythm: band widths follow a gently varying cadence, not random.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1100, 850

# a curated cool sequence + a few warm accents (Riley "Cool Edge" register)
COOL = [
    (0.16, 0.34, 0.46), (0.20, 0.48, 0.50), (0.30, 0.55, 0.44),   # deep teal→sea-green
    (0.24, 0.40, 0.60), (0.34, 0.44, 0.66), (0.42, 0.40, 0.62),   # blue→periwinkle→violet
    (0.18, 0.42, 0.52), (0.28, 0.52, 0.56), (0.22, 0.36, 0.58),
]
WARM = [(0.86, 0.44, 0.42), (0.90, 0.66, 0.34), (0.78, 0.34, 0.46)]  # rose / amber / raspberry

rng = np.random.default_rng(11)
# build a band sequence L→R: mostly cool in a rotating order, warm accent ~every 9th
cols, widths = [], []
ci = 0
x = 0
i = 0
base_w = 15
while x < W:
    # gentle width cadence: sinusoidal breathing of band width (Riley's rhythm)
    w = int(base_w * (0.75 + 0.5 * (0.5 + 0.5 * np.sin(i * 0.5))))
    w = max(7, w)
    if i > 0 and i % 9 == 4:                      # sparse warm accent — contrast of extension
        cols.append(WARM[(i // 9) % len(WARM)]); widths.append(max(7, w - 3))
    else:
        cols.append(COOL[ci % len(COOL)]); widths.append(w); ci += 1
    x += widths[-1]; i += 1

img = np.zeros((H, W, 3))
x = 0
for c, w in zip(cols, widths):
    img[:, x:min(W, x + w)] = np.array(c)
    x += w
    if x >= W:
        break

# the tiniest tooth so the flats read as painted, not screen-fill (NOT a glow)
tooth = 1.0 + 0.012 * rng.standard_normal((H, W, 1))
img = np.clip(img * tooth, 0, 1)
write_png(os.path.join(OUT, "riley_stripes.png"), (img * 255).astype(np.uint8))
print("wrote riley_stripes.png  (%d bands)" % len(cols))
