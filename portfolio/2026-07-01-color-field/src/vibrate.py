"""
Equiluminant vibration — colour as pure PERCEPTION.

Two complementary hues (a warm orange-red and a cool cyan-blue) matched to the
SAME luminance are interleaved in wavy bands. Because the boundary has strong HUE
contrast but almost NO luminance contrast, the eye's edge-detectors (which key on
luminance) can't lock it — so the border shimmers / seems to move (equiluminance,
the phenomenon behind chromostereopsis and Op-art colour "buzz"). Measured, not
eyeballed: both colours are forced to luminance ≈ 0.55 via the Rec.709 weights.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1100, 850
yy, xx = np.mgrid[0:H, 0:W].astype(float)
u, v = xx / W, yy / H

R, G, B = 0.2126, 0.7152, 0.0722          # Rec.709 luminance weights
TARGET = 0.55


def at_luma(rgb):
    rgb = np.array(rgb, float)
    L = R * rgb[0] + G * rgb[1] + B * rgb[2]
    return np.clip(rgb * (TARGET / L), 0, 1)


warm = at_luma([0.95, 0.42, 0.30])        # orange-red pushed to L=0.55
cool = at_luma([0.10, 0.62, 0.85])        # cyan-blue pushed to L=0.55
print("luma warm=%.3f cool=%.3f (want %.2f)" %
      (R*warm[0]+G*warm[1]+B*warm[2], R*cool[0]+G*cool[1]+B*cool[2], TARGET))

# interleaved wavy bands: phase field bends the boundaries so it's not a flat grid
phase = (u * 26 + 2.2 * np.sin(v * 3 * np.pi + u * 4) + 1.4 * np.sin(v * 7)) * np.pi
band = np.sin(phase) > 0
img = np.where(band[..., None], warm[None, None, :], cool[None, None, :])

write_png(os.path.join(OUT, "vibrate.png"), (np.clip(img, 0, 1) * 255).astype(np.uint8))
print("wrote vibrate.png")
