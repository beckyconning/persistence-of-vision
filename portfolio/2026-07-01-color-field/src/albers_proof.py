"""
Albers, rigorously — "one colour looks like two", with the PROOF bar.

The canonical Interaction-of-Color demonstration done as a measured plate (not a
nested-square homage): a single physical swatch colour M sits on two grounds
engineered to push it in opposite directions (simultaneous contrast → M drifts
toward each ground's complement). To PROVE the two M patches are identical, a thin
bar of the SAME M spans the seam between the grounds — the eye sees it is one
continuous colour, yet the two framed patches still refuse to match.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1100, 720
img = np.zeros((H, W, 3))

M = np.array([0.62, 0.55, 0.32])          # the one middle colour (muted olive-gold)
A = np.array([0.16, 0.30, 0.42])          # cool teal ground (left)  → M reads warm/light
B = np.array([0.80, 0.52, 0.24])          # warm ochre ground (right) → M reads cool/dark

img[:, :W // 2] = A
img[:, W // 2:] = B

# two framed patches of the identical M, one centred on each ground
def patch(cx, cy, w, h, col):
    img[cy - h // 2:cy + h // 2, cx - w // 2:cx + w // 2] = col

patch(W // 4,     H // 2, 210, 300, M)
patch(3 * W // 4, H // 2, 210, 300, M)

# the PROOF bar: a thin continuous strip of the SAME M spanning both grounds
img[H // 2 - 16:H // 2 + 16, W // 4:3 * W // 4] = M

write_png(os.path.join(OUT, "albers_proof.png"), (np.clip(img, 0, 1) * 255).astype(np.uint8))
print("wrote albers_proof.png  (both patches + bar are the identical colour M)")
