"""
Cold Dissonance — HARD-EDGE geometric composition in a deliberately COOL / DISSONANT palette.

Two frontiers the corpus keeps dodging (per FRONTIERS after s16): every palette so far is
warm-harmonious or neon-GLOW, and the successful colour work (albers_proof) was a measured
demonstration plate, not a COMPOSITION. This is the opposite of glow — flat, crisp-edged planes
(Kelly / Herrera / Lohse concrete-art vocabulary), hand-placed for asymmetric balance, no blending
anywhere. The palette is cold (steel / teal / indigo / cold violet) and SOURED by one acid
chartreuse — the sour note is small and off-centre so it reads as tension, not decoration.

It also carries the Albers idea forward compositionally: the same cold grey rectangle appears
against indigo (reads light/warm) and against chartreuse (reads dark/dead) — simultaneous contrast
put to WORK inside a picture rather than proved in a lab plate.

Hand-built (explicit placement, not a generative fill); portrait format to break the landscape habit.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 1000, 1400
img = np.zeros((H, W, 3))

GROUND   = np.array([0.87, 0.90, 0.91])   # icy pale grey-cyan
STEEL    = np.array([0.19, 0.33, 0.52])
TEAL     = np.array([0.09, 0.47, 0.49])
INDIGO   = np.array([0.11, 0.13, 0.27])
VIOLET   = np.array([0.35, 0.27, 0.52])
CHART    = np.array([0.74, 0.82, 0.22])   # the dissonant sour note
COLDGREY = np.array([0.55, 0.60, 0.62])   # the "same grey" for simultaneous contrast

img[:] = GROUND

def rect(x0, y0, x1, y1, col):
    img[y0:y1, x0:x1] = col

def quad(pts, col):
    """Fill a convex quad given 4 (x,y) points — hard edge via half-plane test."""
    pts = np.array(pts, float)
    ys, xs = np.mgrid[0:H, 0:W]
    inside = np.ones((H, W), bool)
    for i in range(4):
        x0, y0 = pts[i]; x1, y1 = pts[(i + 1) % 4]
        # left side of directed edge (CCW winding)
        cross = (x1 - x0) * (ys - y0) - (y1 - y0) * (xs - x0)
        inside &= cross >= 0
    img[inside] = col

# --- asymmetric hard-edge composition (rule-of-thirds, weight low-left / focal upper-right) ---
# tall steel plane anchoring the left third
rect(0, 0, 360, H, STEEL)
# a broad indigo band across the lower third (horizon-like weight, but flat)
rect(0, 980, W, 1220, INDIGO)
# teal block interlocking over the steel/indigo seam, off-centre
rect(230, 760, 640, 1080, TEAL)
# cold violet upright to the right, tension against teal (cool-vs-cool dissonance)
rect(700, 300, 900, 900, VIOLET)
# a slim diagonal chartreuse sliver — the sour focal note, upper-right third, small
quad([(760, 120), (900, 150), (620, 780), (560, 760)], CHART)
# simultaneous-contrast pair: identical COLDGREY squares, one on indigo, one on chartreuse-adjacent
rect(140, 1040, 300, 1180, COLDGREY)     # sits on INDIGO -> reads light/luminous
rect(470, 470, 630, 630, COLDGREY)       # sits near CHART/ground -> reads dark/leaden
# a small indigo square top-left for asymmetric counterweight
rect(120, 150, 250, 290, INDIGO)

np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "cold.png"), (img * 255).astype(np.uint8))  # uint8, not float!
print("wrote cold.png")
