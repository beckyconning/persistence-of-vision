"""Still (study): the Laugh Lines vocabulary, serene: almost no lines at all. No outline, no hair, no shading.

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
tilt = np.radians(6)           # head back a little, the way a real laugh goes

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
        ((-3.9, -0.85), (-2.6, -0.45), (-1.35, -0.9), 0.24),    # lids resting shut, curving down
        ((-3.0, -0.55), (-2.6, -0.5), (-2.1, -0.58), 0.07),     # a lash line, barely
        ((-4.3, -2.35), (-2.85, -2.9), (-1.3, -2.45), 0.24),    # brow, at ease
        ((-0.42, 0.65), (-1.45, 1.35), (-0.62, 2.12), 0.18),    # nose wing
        ((-0.62, 2.12), (-0.45, 2.3), (-0.22, 2.24), 0.09),     # nostril
    ]

def centre(k):
    return [((-1.35, 3.62), (0.0, 3.82), (1.35, 3.58), 0.20),     # closed mouth, the faintest lift at the ends
            ((-0.55, 4.25), (0.0, 4.36), (0.55, 4.25), 0.07)]     # lower lip, just

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
