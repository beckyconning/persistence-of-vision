"""Off-centre crop — kill the centred-oval-on-empty-ground habit. Reframe the
engraving (image-as-input) into a tight portrait that bleeds past the frame:
the eyes on the upper third, the head running out of the top and sides."""
import os
import numpy as np
from pngdecode import read_png
from pnglib import write_png

IMG = os.path.join(os.path.dirname(__file__), "..", "images")
a = read_png(os.path.join(IMG, "engraved_face.png")).astype(float)
H, W = a.shape[:2]
# window: inside the face, off-centre (face is ~centre); take a tall crop biased
# left & up so the lit cheek dominates and the crown/right edge run off-frame.
y0, y1 = int(0.06 * H), int(0.74 * H)
x0, x1 = int(0.20 * W), int(0.74 * W)
win = a[y0:y1, x0:x1]
wh, ww = win.shape[:2]
# nearest-neighbour upscale to a 3:4 portrait
OW, OH = 720, 960
ys = np.clip((np.arange(OH) * wh / OH).astype(int), 0, wh - 1)
xs = np.clip((np.arange(OW) * ww / OW).astype(int), 0, ww - 1)
out = win[ys][:, xs]
write_png(os.path.join(IMG, "cropped_face.png"), np.clip(out, 0, 255).astype(np.uint8))
print("wrote cropped_face.png  %dx%d" % (OW, OH))
