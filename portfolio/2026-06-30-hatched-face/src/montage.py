"""Contact sheet — one head, six hands. Tiles all six treatments in a 3x2 grid
on a paper ground: a composition/series move tying the session together."""
import os
import numpy as np
from pngdecode import read_png
from pnglib import write_png

HERE = os.path.dirname(__file__)
IMG = os.path.join(HERE, "..", "images")
names = ["hatched_face", "sanguine_face", "engraved_face",
         "contour_face", "serene_face", "scratchboard_face"]

def downscale(a, k):
    h, w = a.shape[:2]
    h2, w2 = h // k, w // k
    return a[:h2 * k, :w2 * k].reshape(h2, k, w2, k, 3).mean((1, 3))

K = 4
tiles = [downscale(read_png(os.path.join(IMG, n + ".png")).astype(float), K) for n in names]
th, tw = tiles[0].shape[:2]
gut = 18
paper = np.array([0.90, 0.87, 0.80]) * 255
cols, rows = 3, 2
H = rows * th + (rows + 1) * gut
W = cols * tw + (cols + 1) * gut
canvas = np.ones((H, W, 3)) * paper
for i, t in enumerate(tiles):
    r, c = divmod(i, cols)
    y0 = gut + r * (th + gut); x0 = gut + c * (tw + gut)
    canvas[y0:y0 + th, x0:x0 + tw] = t
write_png(os.path.join(IMG, "contact_sheet.png"), np.clip(canvas, 0, 255).astype(np.uint8))
print("wrote contact_sheet.png  %dx%d" % (W, H))
