"""
Hidden in chrominance — an image that exists ONLY in colour.

A target of concentric rings is drawn in two complementary hues forced to the SAME
luminance (Rec.709). LEFT panel: the colour image — the rings read plainly. RIGHT
panel: the exact luminance of the same pixels (grayscale) — the rings VANISH into a
flat field, because there is no luminance difference to see. Proof, in one plate,
that colour alone can carry a whole image (and that our form-vision is luminance-
driven). The session's thesis — colour as the subject — pushed to its literal edge.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
S = 760
R, G, B = 0.2126, 0.7152, 0.0722
T = 0.55


def at_luma(rgb):
    rgb = np.array(rgb, float)
    L = R * rgb[0] + G * rgb[1] + B * rgb[2]
    return np.clip(rgb * (T / L), 0, 1)


hueA = at_luma([0.90, 0.35, 0.45])       # warm rose  @ L=0.55
hueB = at_luma([0.20, 0.62, 0.55])       # cool teal  @ L=0.55

yy, xx = np.mgrid[0:S, 0:S].astype(float)
r = np.hypot(xx - S / 2, yy - S / 2)
rings = (np.sin(r / 26.0) > 0)           # concentric target
colour = np.where(rings[..., None], hueA[None, None, :], hueB[None, None, :])

# right panel = the true luminance of those very pixels (rings gone)
luma = (R * colour[..., 0] + G * colour[..., 1] + B * colour[..., 2])
gray = np.repeat(luma[..., None], 3, axis=2)

gap = 24
plate = np.ones((S, S * 2 + gap, 3)) * 0.5
plate[:, :S] = colour
plate[:, S + gap:] = gray
write_png(os.path.join(OUT, "hidden.png"), (np.clip(plate, 0, 1) * 255).astype(np.uint8))
print("wrote hidden.png  luma spread across image = %.4f (≈0 ⇒ rings invisible in gray)"
      % (luma.max() - luma.min()))
