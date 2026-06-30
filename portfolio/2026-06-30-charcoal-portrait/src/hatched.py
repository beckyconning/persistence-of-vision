"""Charcoal portrait #2 — HATCHED, a different mood. Same value-blocking face method as
charcoal.py, but tone is built from VISIBLE DIRECTIONAL STROKES (cross-hatching that thickens as
the form darkens) instead of smooth smudge — the draughtsman's hatch, like the s11 line-engraving
applied to a face. Mirrored 3/4 turn (head to the left), eyes OPEN with a calm upward gaze and a
level mouth → serene rather than melancholy. Light from the right.
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


# MIRRORED about x=0.5 vs charcoal.py: head turned to the LEFT, light from the RIGHT.
FCX, FCY = 0.53, 0.50
val = np.ones((H, W))
face = np.maximum(ellipse(FCX, FCY - 0.01, 0.20, 0.265, 0.10),
                  ellipse(FCX - 0.01, FCY + 0.13, 0.145, 0.135, 0.10))
face = blur(face, 4)
ramp = 0.78 - 0.42 * np.clip(((1 - nx) - ((1 - FCX) - 0.16)) / 0.34, 0, 1)   # right bright → left dark
val = val * (1 - face) + ramp * face


def shade(reg, amt):
    global val
    val = val * (1 - amt * reg)


def lift(reg, amt):
    global val
    val = np.clip(val + amt * reg, 0, 1)


M = -1  # mirror x-offsets
shade(blur(blob(FCX - 0.085, FCY - 0.02, 0.085, 0.16), 2) * face, 0.30)      # far cheek/temple (now left)
shade(blur(blob(FCX + 0.075, FCY - 0.045, 0.05, 0.03), 2), 0.42)             # near eye socket (open → lighter)
shade(blur(blob(FCX - 0.055, FCY - 0.05, 0.045, 0.028), 2), 0.40)            # far eye socket
shade(blur(blob(FCX + 0.005, FCY - 0.085, 0.10, 0.02), 2) * face, 0.20)      # brow band
shade(blur(blob(FCX - 0.01, FCY + 0.005, 0.022, 0.07), 2), 0.30)             # nose side shadow (left of ridge)
shade(blur(blob(FCX + 0.03, FCY + 0.06, 0.05, 0.022), 2), 0.18)              # under-nose
shade(blur(blob(FCX + 0.02, FCY + 0.135, 0.06, 0.03), 2), 0.24)             # under-lip / chin
shade(blur(blob(FCX, FCY + 0.205, 0.13, 0.045), 3), 0.32)                    # under-jaw

# hair (swept, fuller on the right/back)
hair = np.maximum.reduce([blob(FCX, FCY - 0.215, 0.205, 0.12),
                          blob(FCX - 0.175, FCY - 0.02, 0.085, 0.205),
                          blob(FCX + 0.165, FCY - 0.07, 0.06, 0.13)])
hair = np.clip((hair - 0.32) / 0.18, 0, 1) * (1 - blur(face, 5) * 0.6)
hair = blur(hair, 2)
val = val * (1 - hair) + (0.16) * hair

# neck
neck = blur(np.maximum(ellipse(FCX - 0.01, FCY + 0.30, 0.072, 0.18, 0.16),
                       ellipse(FCX - 0.01, FCY + 0.46, 0.26, 0.12, 0.05)) * (ny > FCY + 0.14), 5)
val = val * (1 - neck) + (0.26 + 0.18 * np.clip((ny - (FCY + 0.18)) / 0.16, 0, 1)) * neck

# OPEN eyes — calm, looking up-and-aside: pale eyeball + small dark iris high in the socket
for ex, ey in [(FCX + 0.075, FCY - 0.028), (FCX - 0.052, FCY - 0.034)]:
    lift(blur(blob(ex, ey, 0.026, 0.012), 1), 0.18)                          # eyeball catchlight
    val = np.minimum(val, 1 - blur(blob(ex - 0.004, ey - 0.004, 0.010, 0.011), 1) * 0.78)  # iris (raised gaze)
    val = np.minimum(val, 1 - blur(blob(ex, ey - 0.016, 0.030, 0.004), 1) * 0.55)          # upper lid line
val = np.minimum(val, 1 - blur(blob(FCX + 0.028, FCY + 0.058, 0.006, 0.012), 1) * 0.42)    # nostril
val = np.minimum(val, 1 - blur(blob(FCX + 0.02, FCY + 0.092, 0.05, 0.006), 1) * 0.5)       # level mouth (serene)

val = blur(val, 1)
lift(blur(blob(FCX + 0.06, FCY - 0.10, 0.07, 0.05), 3) * face, 0.10)
lift(blur(blob(FCX + 0.10, FCY + 0.03, 0.05, 0.05), 3) * face, 0.10)
val = np.clip(val, 0, 1)

# ---- HATCH transfer: build tone from layered diagonal strokes that thicken with darkness ----
d = 1 - val                                   # 0 = paper, 1 = darkest
tone = np.ones((H, W))                         # start white(=paper)
wobble = 0.6 * vnoise(70, 5)
# higher first threshold → lit planes (cheek/forehead/nose-bridge) stay PAPER (no hatch);
# darker layers only kick in for real shadows, so the value structure survives.
layers = [(0.62, 0.26, 95.0), (-0.55, 0.42, 90.0), (1.15, 0.58, 105.0), (0.15, 0.72, 120.0)]
for ang, thr, freq in layers:
    ca, sa = np.cos(ang), np.sin(ang)
    coord = (nx * ca + ny * sa) * freq + wobble
    line = np.abs(np.sin(coord * np.pi))       # 0 at stroke centre
    strength = np.clip((d - thr) / 0.22, 0, 1) ** 1.3   # steeper → more contrast light↔dark
    stroke = (1 - line) ** 1.8                  # thin dark lines
    tone = tone - 0.6 * strength * stroke
tone = np.clip(tone, 0, 1)
# keep the darkest masses solid (hair, deep sockets) so hatch doesn't lighten them
tone = np.minimum(tone, 1 - np.clip((d - 0.7) / 0.3, 0, 1))
tone = blur(tone, 1)                            # a touch of blend (charcoal, not pen)
# RE-STAMP the crisp feature accents on top of the hatch (else they wash out): eyes, nose, mouth
feat = np.zeros((H, W))
for ex, ey in [(FCX + 0.075, FCY - 0.028), (FCX - 0.052, FCY - 0.034)]:
    feat = np.maximum(feat, blur(blob(ex - 0.004, ey - 0.004, 0.011, 0.012), 1) * 0.78)   # iris
    feat = np.maximum(feat, blur(blob(ex, ey - 0.017, 0.032, 0.0045), 1) * 0.62)          # upper lid
feat = np.maximum(feat, blur(blob(FCX + 0.028, FCY + 0.058, 0.007, 0.013), 1) * 0.5)      # nostril
feat = np.maximum(feat, blur(blob(FCX + 0.02, FCY + 0.092, 0.052, 0.0065), 1) * 0.58)     # mouth
tone = np.minimum(tone, 1 - feat)
# tiny eraser catchlight in each eye so the gaze reads alive
for ex, ey in [(FCX + 0.075, FCY - 0.030), (FCX - 0.052, FCY - 0.036)]:
    tone = np.maximum(tone, blur(blob(ex + 0.004, ey - 0.002, 0.004, 0.004), 0) * 0.9)

paper = np.array([0.84, 0.81, 0.74])
charc = np.array([0.11, 0.10, 0.12])
img = charc[None, None, :] + (paper - charc)[None, None, :] * tone[..., None]
img = img * (1 - 0.045 * (vnoise(W // 2, 11) - 0.5))[..., None]
vig = 1 - 0.20 * ((nx - 0.54) ** 2 + (ny - 0.48) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/hatched.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/hatched.png")
