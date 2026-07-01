"""
Fauve landscape — colour AS representation, in a deliberately dissonant palette.

The last frontier this session opens: a recognisable scene built from FLAT colour
shapes alone — no line, no value modelling — with NON-naturalistic, slightly
clashing hues (Derain/Matisse: a green-gold sky, magenta and vermilion hills, a
violet river, a hot orange sun). The subject reads purely from shape + colour
adjacency; the clash is the point (every prior colour piece stayed harmonious).
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1100, 820
yy, xx = np.mgrid[0:H, 0:W].astype(float)
u, v = xx / W, yy / H
img = np.zeros((H, W, 3))


def fill(mask, color):
    global img
    img = np.where(mask[..., None], np.array(color), img)


# sky — a green-gold band over a turquoise band (non-naturalistic)
fill(v < 1.0, (0.86, 0.82, 0.30))            # green-gold upper sky
fill(v < 0.28, (0.30, 0.72, 0.68))           # turquoise high sky

# sun — hot orange disc, placed off-centre (rule of thirds)
sun = np.hypot((xx - 0.72 * W) / 1.0, (yy - 0.22 * H)) < 78
fill(sun, (0.96, 0.45, 0.10))

# hills — overlapping bands with sine crests, back→front, clashing hues
def hill(base, amp, freq, phase, color):
    crest = base + amp * np.sin(u * freq * 2 * np.pi + phase)
    fill(v > crest, color)

hill(0.42, 0.05, 1.3, 0.0, (0.82, 0.24, 0.52))   # magenta far hill
hill(0.55, 0.06, 0.9, 1.4, (0.40, 0.16, 0.52))   # violet mid hill
hill(0.66, 0.05, 1.7, 3.0, (0.90, 0.30, 0.16))   # vermilion near hill

# river cutting through the foreground — a violet-blue diagonal ribbon
river_c = 0.30 + 0.22 * v + 0.05 * np.sin(v * 8)
river = (np.abs(u - river_c) < (0.06 + 0.10 * v)) & (v > 0.6)
fill(river, (0.28, 0.30, 0.66))

# foreground meadow — acid lime
fill(v > 0.86, (0.55, 0.72, 0.18))

# a single tree (flat): violet trunk + a vermilion-dotted teal canopy
trunk = (np.abs(xx - 0.22 * W) < 10) & (yy > 0.60 * H) & (yy < 0.80 * H)
fill(trunk, (0.35, 0.18, 0.30))
canopy = np.hypot((xx - 0.22 * W), (yy - 0.56 * H)) < 62
fill(canopy, (0.16, 0.52, 0.42))                 # teal canopy (clashes the lime)

img = np.clip(img, 0, 1)
write_png(os.path.join(OUT, "fauve.png"), (img * 255).astype(np.uint8))
print("wrote fauve.png")
