"""Charcoal portrait — a 3/4 head with a MOOD. Axis: a TONAL charcoal medium + the expressive
off-axis face (the s3 portrait was frontal/mask-stiff). Approach (v2): don't model relief from
bumps (that read as a mask) — BLOCK IN VALUES the way a charcoal artist does. Lit planes vs core
shadows painted directly, smudged; strokes only in hair + background; crisp dark accents
(eyelid, nostril, lip crease, jaw) for structure; kneaded-eraser highlights on the lit planes.
A downcast gaze + soft-downturned mouth + shadow-side weight give the melancholy.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis); cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def blob(cx, cy, sx, sy, rot=0.0):
    ca, sa = np.cos(rot), np.sin(rot)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    return np.exp(-((u / sx) ** 2 + (v / sy) ** 2))


def ellipse(cx, cy, sx, sy, soft, rot=0.0):
    ca, sa = np.cos(rot), np.sin(rot)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    d = np.sqrt((u / sx) ** 2 + (v / sy) ** 2)
    return np.clip((1 - d) / soft, 0, 1)


# value buffer: 1 = paper, 0 = darkest charcoal. Start on warm paper.
val = np.ones((H, W))

FCX, FCY = 0.47, 0.50
# face mask: egg, narrower at chin; the facial midline sits LEFT of head centre (3/4 turn)
face = np.maximum(ellipse(FCX, FCY - 0.01, 0.20, 0.265, 0.10),
                  ellipse(FCX + 0.01, FCY + 0.13, 0.145, 0.135, 0.10))
face = blur(face, 4)

# 1) base skin midtone with a left key-light ramp (lit left ~0.80 → shadow right ~0.40)
ramp = 0.78 - 0.42 * np.clip((nx - (FCX - 0.16)) / 0.34, 0, 1)   # left bright, right dark
skin = ramp
val = val * (1 - face) + skin * face

# helper to darken a region by `amt` (multiplicative toward black), masked + soft
def shade(reg, amt):
    global val
    val = val * (1 - amt * reg)

def lift(reg, amt):
    global val
    val = np.clip(val + amt * reg, 0, 1)

# 2) core shadows
shade(blur(blob(FCX + 0.085, FCY - 0.02, 0.085, 0.16), 2) * face, 0.30)   # far cheek/temple recede
shade(blur(blob(FCX - 0.075, FCY - 0.045, 0.05, 0.03), 2), 0.55)          # near eye socket
shade(blur(blob(FCX + 0.055, FCY - 0.05, 0.045, 0.028), 2), 0.50)         # far eye socket
shade(blur(blob(FCX - 0.005, FCY - 0.085, 0.10, 0.02), 2) * face, 0.22)   # brow shadow band
shade(blur(blob(FCX + 0.01, FCY + 0.005, 0.022, 0.07), 2), 0.30)          # nose side shadow (right of ridge)
shade(blur(blob(FCX - 0.03, FCY + 0.06, 0.05, 0.022), 2), 0.20)           # under-nose
shade(blur(blob(FCX - 0.02, FCY + 0.135, 0.06, 0.03), 2), 0.28)           # under-lip / chin shadow
shade(blur(blob(FCX + 0.0, FCY + 0.205, 0.13, 0.045), 3), 0.34)           # under-jaw

# 3) hair — dark mass framing crown + far side + a near lock; directional stick strokes
hair = np.maximum.reduce([
    blob(FCX, FCY - 0.215, 0.205, 0.12),
    blob(FCX + 0.175, FCY - 0.02, 0.085, 0.205),
    blob(FCX - 0.165, FCY - 0.07, 0.06, 0.13),
])
hair = np.clip((hair - 0.32) / 0.18, 0, 1)
hair = hair * (1 - blur(face, 5) * 0.6)
hair = blur(hair, 2)
strokes = 0.5 + 0.5 * np.sin((nx * 18 + ny * 30) * np.pi + 7 * vnoise(46, 3))
hair_val = 0.10 + 0.12 * strokes
val = val * (1 - hair) + hair_val * hair

# 4) neck — a column connected UNDER the jaw (not a floating disc): tall, overlaps the jaw,
#    darkest at the top (cast shadow from the jaw) easing down; widens to a shoulder hint.
neck_col = ellipse(FCX + 0.01, FCY + 0.30, 0.072, 0.18, 0.16)        # tall column, reaches up to the jaw
shoulder = ellipse(FCX + 0.01, FCY + 0.46, 0.26, 0.12, 0.05)         # shoulders at the very bottom
neck = blur(np.maximum(neck_col, shoulder) * (ny > FCY + 0.14), 5)
neck_ramp = 0.26 + 0.18 * np.clip((ny - (FCY + 0.18)) / 0.16, 0, 1)  # dark under jaw → lighter lower
val = val * (1 - neck) + neck_ramp * neck

# 5) crisp dark accents (drawn AFTER, so smudge doesn't erase the structure lines)
def accent(reg, dark):
    global val
    val = np.minimum(val, 1 - reg * (1 - dark))

# lowered upper-eyelid lines (downcast gaze) — short dark strokes, no bright eyeball
accent(blur(blob(FCX - 0.072, FCY - 0.028, 0.034, 0.006), 1), 0.18)
accent(blur(blob(FCX + 0.052, FCY - 0.034, 0.030, 0.006), 1), 0.20)
accent(blur(blob(FCX - 0.028, FCY + 0.058, 0.006, 0.012), 1), 0.10)       # near nostril
accent(blur(blob(FCX - 0.02, FCY + 0.092, 0.05, 0.006), 1), 0.22)         # lip crease (soft downturn via rot)
accent(blur(blob(FCX - 0.02, FCY + 0.093, 0.05, 0.005, rot=0.10), 1), 0.25)

# 6) smudge everything slightly (charcoal blend)
val = blur(val, 1)

# 7) kneaded-eraser highlights on the lit planes (forehead, near cheek, nose bridge)
lift(blur(blob(FCX - 0.06, FCY - 0.10, 0.07, 0.05), 3) * face, 0.10)
lift(blur(blob(FCX - 0.10, FCY + 0.03, 0.05, 0.05), 3) * face, 0.10)
lift(blur(blob(FCX - 0.045, FCY - 0.01, 0.012, 0.05), 2) * face, 0.12)

# ---- paper + charcoal palette ----
val = np.clip(val, 0, 1)
paper = np.array([0.81, 0.78, 0.72])
charc = np.array([0.10, 0.10, 0.12])
img = charc[None, None, :] + (paper - charc)[None, None, :] * val[..., None]
# background: faint diagonal charcoal hatching, loose, only outside the figure
figure = np.clip(blur(np.maximum.reduce([face, hair, neck]), 10), 0, 1)
bg_hatch = 0.5 + 0.5 * np.sin((nx - ny) * 55 + 3 * vnoise(40, 9))
img = img - (0.028 * (1 - figure) * (bg_hatch - 0.5))[..., None]
# paper tooth + vignette
img = img * (1 - 0.045 * (vnoise(W // 2, 11) - 0.5))[..., None]
vig = 1 - 0.20 * ((nx - 0.46) ** 2 + (ny - 0.48) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/charcoal.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/charcoal.png")
