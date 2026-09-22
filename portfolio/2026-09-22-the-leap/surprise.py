"""Oh! (study): the Laugh Lines vocabulary made to say surprise instead. No outline, no hair, no shading.

Constraint from the subject: a laugh is a set of folds (crescent lids, crow's feet, lifted cheeks,
nasolabial brackets, an open mouth). If the lines are right, the face assembles itself.
Cropped off the right edge; the paper does the rest.
"""
import sys
import numpy as np
from PIL import Image, ImageDraw

W, H, SS = 1200, 1600, 3
if "--small" in sys.argv: SS = 2
OUT = sys.argv[1] if len(sys.argv) > 1 else "laugh-lines.png"
rng = np.random.default_rng(22)
u = 74.0 * SS
x0, y0 = 872.0 * SS, 690.0 * SS
tilt = np.radians(4)           # head back a little, the way a real laugh goes

def P(x, y, side=1):
    if side < 0:                # the viewer's right half sits a touch higher: laughs are lopsided
        y -= 0.18
    c, s = np.cos(tilt), np.sin(tilt)
    return x0 + u * (x * c - y * s), y0 + u * (x * s + y * c)

K = float(next((a[4:] for a in sys.argv if a.startswith("--k=")), "1"))   # how hard the laugh is, 0..1
HA = float(next((a[5:] for a in sys.argv if a.startswith("--ha=")), "0"))  # a "ha" pulse, 0..1 (film only)
y0 -= HA * 5 * SS                                                          # the head bobs on each ha

def g(k, th):                   # lines fade in by weight, never pop (keeps every frame's hand the same)
    return float(np.clip((k - th) / 0.15, 0, 1))

def half(k):
    return [
        ((-4.0, -1.0), (-2.6, -2.05), (-1.3, -1.0), 0.26),      # upper lid, wide open
        ((-3.85, -0.85), (-2.6, -0.1), (-1.45, -0.85), 0.14),   # lower lid, relaxed
        ((-2.72, -1.2), (-2.6, -1.1), (-2.48, -1.2), 0.30),     # iris, a dot looking up
        ((-4.4, -3.1), (-2.85, -4.5), (-1.2, -3.2), 0.30),      # brow, flung up
        ((-0.42, 0.65), (-1.45, 1.35), (-0.62, 2.12), 0.20),    # nose wing
        ((-0.62, 2.12), (-0.45, 2.3), (-0.22, 2.24), 0.10),     # nostril
    ]

def centre(k):
    return [((-0.75, 4.1), (0.0, 3.1), (0.75, 4.1), 0.26),        # the O
            ((-0.75, 4.1), (0.0, 5.2), (0.75, 4.1), 0.26),
            ((-2.9, -5.0), (0.0, -5.7), (2.9, -5.1), 0.10),       # forehead, all of it
            ((-2.4, -5.7), (0.0, -6.35), (2.4, -5.75), 0.09),
            ((-1.7, -6.35), (0.0, -6.9), (1.7, -6.4), 0.07),
            ((-0.7, 6.4), (0.0, 6.62), (0.7, 6.4), 0.10)]         # chin, dropped

HALF, CENTRE = half(K), centre(K)

ink = Image.new("L", (W * SS, H * SS), 0)
d = ImageDraw.Draw(ink)

def stroke(a, c, b, wgt, side=1):
    t = np.linspace(0, 1, 420)
    pts = [(1 - t) ** 2 * a[i] + 2 * (1 - t) * t * c[i] + t ** 2 * b[i] for i in (0, 1)]
    wob = 0.03 * np.sin(t * 7 + rng.uniform(0, 6)) + 0.02 * rng.standard_normal() # a hand, not a plotter
    press = np.sin(np.pi * t) ** 0.75 * (0.85 + 0.3 * rng.random())
    for x, y, p, wo in zip(pts[0], pts[1], press, wob + 0 * t):
        X, Y = P(x * side, y + wo, side)
        r = u * wgt * 0.5 * (0.18 + 0.82 * p)
        if r < 0.3: continue
        d.ellipse((X - r, Y - r, X + r, Y + r), fill=255)

for s_ in HALF:
    stroke(*s_, side=1)
    stroke(*s_, side=-1)
for s_ in CENTRE:
    stroke(*s_)

m = np.asarray(ink, dtype=np.float32) / 255
m = m.reshape(H, SS, W, SS).mean((1, 3))

# paper: warm, with fibre; ink: sepia-black that runs a little dry
yy, xx = np.mgrid[0:H, 0:W]
fibre = 0.012 * rng.standard_normal((H, W)) + 0.008 * np.sin(xx * 0.9 + np.sin(yy * 0.05) * 3)
paper = np.array([242, 236, 222]) / 255 * (1 + fibre)[..., None]
dry = np.clip(0.82 + 0.22 * rng.random((H, W)), 0, 1)
inkc = np.array([40, 31, 28]) / 255
a = (m * dry)[..., None]
img = paper * (1 - a) + inkc * a
Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(OUT)
print(OUT)
