"""Cropped sanguine — the off-centre reframe on the red-chalk version: an
intimate trois-crayons detail, composition move + colour palette together."""
import os
import numpy as np
from pngdecode import read_png
from pnglib import write_png

IMG = os.path.join(os.path.dirname(__file__), "..", "images")
a = read_png(os.path.join(IMG, "sanguine_face.png")).astype(float)
H, W = a.shape[:2]
y0, y1 = int(0.05 * H), int(0.72 * H)
x0, x1 = int(0.22 * W), int(0.78 * W)
win = a[y0:y1, x0:x1]
wh, ww = win.shape[:2]
OW, OH = 760, 920
ys = np.clip((np.arange(OH) * wh / OH).astype(int), 0, wh - 1)
xs = np.clip((np.arange(OW) * ww / OW).astype(int), 0, ww - 1)
out = win[ys][:, xs]
write_png(os.path.join(IMG, "cropped_sanguine.png"), np.clip(out, 0, 255).astype(np.uint8))
print("wrote cropped_sanguine.png  %dx%d" % (OW, OH))
