"""
Serene face — the control experiment. Same value-blocking + hatch engine as
hatched_face.py, but a DIFFERENT mood, to prove the kit isn't a one-trick
(every face this repo has made so far is melancholy). Here: level open eyes,
relaxed unfurrowed brow, a gentle upturned mouth, an even frontal key.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 900
rng = np.random.default_rng(11)
ys, xs = np.mgrid[0:H, 0:W]
x = (xs - W / 2) / (W * 0.42)
y = (ys - H * 0.46) / (H * 0.42)


def gauss(cx, cy, sx, sy, rot=0.0):
    dx, dy = x - cx, y - cy
    c, s = np.cos(rot), np.sin(rot)
    u, v = dx * c + dy * s, -dx * s + dy * c
    return np.exp(-((u / sx) ** 2 + (v / sy) ** 2))


face = gauss(0.0, 0.08, 0.60, 0.86)
inside = face > 0.20
sx_, sy_ = x / 0.60, (y - 0.08) / 0.86
r2 = np.clip(sx_ ** 2 + sy_ ** 2, 0, 1)
snz = np.sqrt(1 - r2)
L = np.array([-0.34, -0.22, 0.91]); L /= np.linalg.norm(L)   # gentler, frontal key
form = np.clip(sx_ * L[0] + sy_ * L[1] + snz * L[2], 0, 1)
light = 0.54 + 0.36 * form ** 0.85                           # higher-key, calmer


def dark(a, cx, cy, sx, sy, rot=0.0):
    global light
    light = light - a * gauss(cx, cy, sx, sy, rot)


def lit(a, cx, cy, sx, sy, rot=0.0):
    global light
    light = light + a * gauss(cx, cy, sx, sy, rot)


# highlights — a smile lifts the cheeks; smooth open forehead
lit(0.13, -0.04, -0.30, 0.42, 0.27)          # forehead (unfurrowed)
lit(0.12, -0.04, 0.10, 0.055, 0.30)          # nose ridge
lit(0.09, 0.0, 0.30, 0.07, 0.06)             # nose tip
lit(0.15, -0.30, 0.27, 0.22, 0.17)           # raised cheek (smile) L
lit(0.13, 0.30, 0.27, 0.20, 0.16)            # raised cheek (smile) R
lit(0.09, -0.03, 0.74, 0.22, 0.12)           # chin
lit(0.05, -0.22, 0.00, 0.16, 0.05)           # open upper-lid plane L
lit(0.05, 0.22, 0.00, 0.16, 0.05)            # open upper-lid plane R

# core shadows — lighter, no brow furrow; eyes OPEN and level (not downcast)
dark(0.18, -0.215, 0.015, 0.130, 0.055)      # eye L (level, lidded-calm)
dark(0.18, 0.215, 0.015, 0.130, 0.055)       # eye R
dark(0.13, -0.215, -0.005, 0.140, 0.020)     # lash line L (softer than the sad one)
dark(0.13, 0.215, -0.005, 0.140, 0.020)      # lash line R
dark(0.09, -0.205, -0.11, 0.16, 0.040)       # under-brow L (relaxed, high)
dark(0.09, 0.205, -0.11, 0.16, 0.040)        # under-brow R
dark(0.13, 0.075, 0.10, 0.050, 0.25)         # nose side (gentle)
dark(0.13, 0.0, 0.355, 0.13, 0.052)          # under nose
dark(0.10, -0.075, 0.335, 0.034, 0.030)      # nostril L
dark(0.10, 0.075, 0.335, 0.034, 0.030)       # nostril R
# mouth: corners turned UP (parabola opens downward) → a calm half-smile
lipy = 0.49 - 0.055 * (x / 0.24) ** 2
light = light - 0.17 * np.exp(-((x / 0.21) ** 2 + ((y - lipy) / 0.013) ** 2))
lit(0.07, 0.0, 0.455, 0.14, 0.020)           # upper-lip catch (smile)
dark(0.08, 0.0, 0.560, 0.16, 0.040)          # soft shadow under lower lip
# smile creases (nasolabial) — subtle, the readable sign of a smile
dark(0.06, -0.20, 0.40, 0.05, 0.13, 0.5)
dark(0.06, 0.20, 0.40, 0.05, 0.13, -0.5)
dark(0.14, 0.42, 0.26, 0.24, 0.44)           # shadow-side form (soft)
dark(0.08, 0.0, 0.93, 0.40, 0.13)            # under-jaw
dark(0.07, -0.52, -0.05, 0.15, 0.40)         # temple L
dark(0.07, 0.54, -0.05, 0.15, 0.40)          # temple R

light = np.clip(light, 0.06, 1.0)
D = np.where(inside, 1.0 - light, 0.0)
D = np.clip(D, 0, 1)


def vnoise(freq):
    g = rng.standard_normal((freq + 2, freq + 2))
    yy = np.linspace(0, freq, H)[:, None] * np.ones((1, W))
    xx = np.linspace(0, freq, W)[None, :] * np.ones((H, 1))
    x0, y0 = np.floor(xx).astype(int), np.floor(yy).astype(int)
    fx, fy = xx - x0, yy - y0
    sx2, sy2 = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - sx2) + g[y0, x0 + 1] * sx2
    b = g[y0 + 1, x0] * (1 - sx2) + g[y0 + 1, x0 + 1] * sx2
    return a * (1 - sy2) + b * sy2


waver = 6.0 * vnoise(14)
grain = vnoise(120)


def hatch(th, sp, t, soft=0.10, width=0.36, breakup=0.55):
    c, s = np.cos(th), np.sin(th)
    phase = (xs * s - ys * c + waver) / sp
    d = np.abs(phase - np.round(phase))
    line = np.clip((width - d) / width, 0, 1) ** 0.6
    line = line * (1.0 - breakup * np.clip(grain * 0.5 + 0.5, 0, 1))
    return line * np.clip((D - t) / soft, 0, 1)


ink = np.zeros_like(D)
for th, sp, t in [(np.radians(32), 6.2, 0.16), (np.radians(-32), 6.2, 0.34),
                  (np.radians(78), 5.6, 0.50), (np.radians(8), 5.0, 0.64),
                  (np.radians(-60), 4.4, 0.76), (np.radians(50), 3.8, 0.86)]:
    ink = ink + hatch(th, sp, t)
ink = np.clip(ink + 0.9 * hatch(np.radians(-32), 2.6, 0.88, width=0.42, breakup=0.35), 0, 1)

paper = np.array([0.93, 0.90, 0.83])
inkc = np.array([0.10, 0.09, 0.12])
paper_t = paper[None, None, :] * (1.0 + 0.03 * vnoise(40)[..., None])
rgb = np.clip(paper_t * (1 - ink[..., None]) + inkc[None, None, :] * ink[..., None], 0, 1)
write_png(os.path.join(OUT, "serene_face.png"), (rgb * 255).astype(np.uint8))
print("wrote serene_face.png  ink coverage = %.3f" % ink.mean())
