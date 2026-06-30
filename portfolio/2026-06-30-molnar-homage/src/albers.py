"""
Homage to Josef Albers — "Homage to the Square" / "Interaction of Color".

The colour piece — finally breaking the paper-ink-plus-one-red palette the recent
sessions leaned on. Albers' format: nested flat squares sitting LOW in the frame
(equal side margins, ~3x more space above than below), chosen so adjacent hues
interact. A diptych: the INNERMOST square is the identical colour in both panels,
but reads warmer/cooler depending on its surround — the book's whole thesis in one
image. New axis: a real colour system (no tone, no line — just flat fields).
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
S = 760                       # panel size
GAP = 60
W = S * 2 + GAP * 3
H = S + GAP * 2
U = S / 8.0                   # nesting unit (4 squares)

img = np.zeros((H, W, 3), float)
img[:] = np.array([0.91, 0.89, 0.84])   # paper surround between/around panels


def panel(ox, colours):
    """Draw a Homage-to-the-Square panel at canvas offset ox; colours outer→inner."""
    for i, col in enumerate(colours):
        x0 = int(ox + i * U); x1 = int(ox + S - i * U)
        y0 = int(GAP + 1.5 * i * U); y1 = int(GAP + S - 0.5 * i * U)
        img[y0:y1, x0:x1] = np.array(col)


# the IDENTICAL inner colour in both panels (a muted olive-gold)
inner = (0.78, 0.66, 0.30)
# Panel A: warm grounds → inner reads cool/greenish
panel(GAP, [
    (0.86, 0.55, 0.18),       # warm ochre outer
    (0.80, 0.42, 0.16),       # burnt orange
    (0.74, 0.30, 0.16),       # terracotta
    inner,
])
# Panel B: cool/dark grounds → the SAME inner reads warm/glowing
panel(GAP * 2 + S, [
    (0.16, 0.28, 0.30),       # deep teal outer
    (0.14, 0.36, 0.34),       # pine
    (0.30, 0.46, 0.34),       # sage
    inner,
])

write_png(os.path.join(OUT, "albers_interaction.png"), (np.clip(img, 0, 1) * 255).astype(np.uint8))
print("wrote albers_interaction.png  %dx%d (inner colour identical in both panels)" % (W, H))
