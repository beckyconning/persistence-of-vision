"""
Hatched face — a full-front, pensive portrait whose every tone is built ONLY
from directional ink line-strokes. No soft gradients touch the paper: a
continuous Lambert value-field is *re-quantised into cross-hatching*, the way a
pen-and-ink or engraving portrait is.

Two axes move at once vs. the recent work:
  • SUBJECT  — the FULL-FRONT expressive face (marquee-open; only frontal-relief
    s3, profile-relief s11, profile-charcoal s13 done before).
  • METHOD   — CROSS-HATCHING: tone from visible directional strokes, layered at
    angles and thresholded by darkness. s13 was smudge-tone; this is mark-making.

Hard constraint: the final image is paper + ink strokes. The only place a
gradient exists is the hidden value-field that *decides where strokes go*.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 900
rng = np.random.default_rng(7)

# ── coordinate frame ────────────────────────────────────────────────────────
ys, xs = np.mgrid[0:H, 0:W]
x = (xs - W / 2) / (W * 0.42)          # ~[-1.2, 1.2]
y = (ys - H * 0.46) / (H * 0.42)       # face sits a touch high; neck below


def gauss(cx, cy, sx, sy, rot=0.0):
    """A rotated anisotropic gaussian mound, evaluated on the whole grid."""
    dx, dy = x - cx, y - cy
    c, s = np.cos(rot), np.sin(rot)
    u, v = dx * c + dy * s, -dx * s + dy * c
    return np.exp(-((u / sx) ** 2 + (v / sy) ** 2))


# ── VALUE-BLOCKING (the s13 lesson): a face reads from painted lit-plane /
#    core-shadow STRUCTURE, not a smooth height-field (which reads as a stone).
#    So `light` is composed deliberately: a clean global form-turn + explicit
#    core shadows subtracted + explicit highlights added. Darkness D = 1-light.
face = gauss(0.0, 0.08, 0.60, 0.86)           # the facial egg (mask + form)
inside = face > 0.20

# global form turn: treat the egg as a sphere, key from upper-left. SMOOTH —
# uses the egg's analytic normal, so no bumpy rim darkening.
sx_, sy_ = x / 0.60, (y - 0.08) / 0.86
r2 = np.clip(sx_ ** 2 + sy_ ** 2, 0, 1)
snz = np.sqrt(1 - r2)
L = np.array([-0.55, -0.22, 0.81]); L /= np.linalg.norm(L)   # more frontal-left
form = np.clip(sx_ * L[0] + sy_ * L[1] + snz * L[2], 0, 1)
light = 0.48 + 0.40 * form ** 0.85            # bright, clean-turning ground

def dark(amt, cx, cy, sx, sy, rot=0.0):
    global light
    light = light - amt * gauss(cx, cy, sx, sy, rot)

def lit(amt, cx, cy, sx, sy, rot=0.0):
    global light
    light = light + amt * gauss(cx, cy, sx, sy, rot)

# highlights — the planes that catch the key
lit(0.16, -0.06, -0.30, 0.40, 0.26)           # forehead
lit(0.13, -0.05, 0.10, 0.055, 0.30)           # nose ridge
lit(0.10, 0.0, 0.30, 0.07, 0.06)              # nose tip
lit(0.14, -0.33, 0.20, 0.20, 0.17)            # lit cheekbone (key side)
lit(0.09, 0.30, 0.18, 0.17, 0.16)             # far cheekbone (dimmer)
lit(0.10, -0.04, 0.74, 0.22, 0.12)            # chin
lit(0.07, -0.22, -0.015, 0.15, 0.045)         # upper-lid plane L (downcast catch)
lit(0.07, 0.22, -0.015, 0.15, 0.045)          # upper-lid plane R

# core shadows — the structure that makes it a FACE
dark(0.25, -0.215, 0.055, 0.135, 0.060)       # eye socket / eye L (low → downcast)
dark(0.25, 0.215, 0.055, 0.135, 0.060)        # eye socket / eye R
dark(0.17, -0.215, 0.020, 0.150, 0.022)       # upper-lash line L (darkest)
dark(0.17, 0.215, 0.020, 0.150, 0.022)        # upper-lash line R
dark(0.14, -0.205, -0.10, 0.16, 0.045)        # under-brow shadow L
dark(0.14, 0.205, -0.10, 0.16, 0.045)         # under-brow shadow R
dark(0.10, 0.0, -0.13, 0.045, 0.075)          # glabella crease (pensive knit)
dark(0.17, 0.085, 0.10, 0.050, 0.26)          # shadow side of nose (away from key)
dark(0.16, 0.0, 0.355, 0.13, 0.055)           # shadow under the nose
dark(0.12, -0.075, 0.335, 0.035, 0.030)       # nostril L
dark(0.12, 0.075, 0.335, 0.035, 0.030)        # nostril R
# mouth: dark lip-line bowed so corners sit lower (the mood)
lipy = 0.50 + 0.07 * (x / 0.22) ** 2
light = light - 0.22 * np.exp(-(((x) / 0.20) ** 2 + ((y - lipy) / 0.013) ** 2))
dark(0.10, 0.0, 0.585, 0.16, 0.045)           # shadow under lower lip
lit(0.07, -0.02, 0.545, 0.13, 0.022)          # lower-lip catchlight
dark(0.12, 0.46, 0.24, 0.24, 0.46)            # shadow-side cheek/jaw (form, softer)
dark(0.09, 0.0, 0.93, 0.40, 0.13)             # under-jaw / neck shadow
dark(0.08, -0.52, -0.05, 0.15, 0.40)          # temple L
dark(0.09, 0.54, -0.05, 0.15, 0.40)           # temple R
lit(0.05, 0.0, 0.70, 0.26, 0.16)              # recover chin/lower-cheek light

light = np.clip(light, 0.05, 1.0)
D = np.where(inside, 1.0 - light, 0.0)
# faint off-centre backing tone (negative space, lower-right) so the head sits
back = 0.07 * np.clip((x - 0.25), 0, 1) * np.clip((y + 0.55), 0, 1.4) / 1.4
D = np.where(inside, D, np.clip(back, 0, 1))
D = np.clip(D, 0, 1)


# ── value-noise for hand-drawn waver / broken strokes ────────────────────────
def vnoise(freq):
    g = rng.standard_normal((freq + 2, freq + 2))
    yy = np.linspace(0, freq, H)[:, None] * np.ones((1, W))
    xx = np.linspace(0, freq, W)[None, :] * np.ones((H, 1))
    x0, y0 = np.floor(xx).astype(int), np.floor(yy).astype(int)
    fx, fy = xx - x0, yy - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - sx) + g[y0, x0 + 1] * sx
    b = g[y0 + 1, x0] * (1 - sx) + g[y0 + 1, x0 + 1] * sx
    return a * (1 - sy) + b * sy


waver = 6.0 * vnoise(14)        # px: wobbles the stroke lines (hand, not ruler)
grain = vnoise(120)             # along-stroke breakup → ink skips


# ── the hatching engine ──────────────────────────────────────────────────────
# Each layer: parallel lines at angle th, spacing sp; "on" where darkness D
# exceeds threshold t. Darker tone recruits more layers (cross-hatch) → more ink.
def hatch_layer(th, sp, t, soft=0.10, width=0.36, breakup=0.55):
    c, s = np.cos(th), np.sin(th)
    phase = (xs * s - ys * c + waver) / sp          # which line we're near
    d = np.abs(phase - np.round(phase))             # dist to nearest line centre
    line = np.clip((width - d) / width, 0, 1) ** 0.6
    line = line * (1.0 - breakup * np.clip(grain * 0.5 + 0.5, 0, 1))  # ink skips
    strength = np.clip((D - t) / soft, 0, 1)        # tone gate (smooth ramp)
    return line * strength


layers = [
    (np.radians(32),  6.2, 0.16),   # first pass — establishes everything mid+
    (np.radians(-32), 6.2, 0.34),   # cross
    (np.radians(78),  5.6, 0.50),   # third direction
    (np.radians(8),   5.0, 0.64),   # fourth
    (np.radians(-60), 4.4, 0.76),   # tightening the darks
    (np.radians(50),  3.8, 0.86),   # deepest accents
]
ink = np.zeros_like(D)
for th, sp, t in layers:
    ink = ink + hatch_layer(th, sp, t)
ink = np.clip(ink, 0, 1)

# a few decisive contour accents: darkest cores get a denser short-stroke layer
core = hatch_layer(np.radians(-32), 2.6, 0.88, width=0.42, breakup=0.35)
ink = np.clip(ink + 0.9 * core, 0, 1)


# ── paper + ink → RGB ────────────────────────────────────────────────────────
paper = np.array([0.93, 0.90, 0.83])      # warm laid paper
inkc = np.array([0.10, 0.09, 0.12])       # near-black, faintly cool
# subtle paper mottle so the ground isn't dead-flat
paper_t = paper[None, None, :] * (1.0 + 0.03 * vnoise(40)[..., None])
rgb = paper_t * (1 - ink[..., None]) + inkc[None, None, :] * ink[..., None]
rgb = np.clip(rgb, 0, 1)

write_png(os.path.join(OUT, "hatched_face.png"), (rgb * 255).astype(np.uint8))
print("wrote hatched_face.png  ink coverage = %.3f" % ink.mean())


# ── VARIANT: trois-crayons (sanguine) — same value field, three chalks. Moves
#    the PALETTE axis: red-chalk darks + WHITE-chalk highlight hatching on a
#    mid-toned paper. Highlights become their own hatch layers (light, not dark).
def hatch_light(th, sp, t, soft=0.12, width=0.34, breakup=0.45):
    c, s = np.cos(th), np.sin(th)
    phase = (xs * s - ys * c + waver * 0.7) / sp
    d = np.abs(phase - np.round(phase))
    line = np.clip((width - d) / width, 0, 1) ** 0.6
    line = line * (1.0 - breakup * np.clip(grain * 0.5 + 0.5, 0, 1))
    Lf = np.where(inside, light, 0.0)
    strength = np.clip((Lf - t) / soft, 0, 1)
    return line * strength


hi = np.zeros_like(D)
for th, sp, t in [(np.radians(40), 6.6, 0.80), (np.radians(-20), 6.0, 0.88)]:
    hi = hi + hatch_light(th, sp, t)
hi = np.clip(hi, 0, 1)

toned = np.array([0.74, 0.66, 0.57])          # warm mid-toned (café-au-lait) paper
sang = np.array([0.55, 0.16, 0.12])           # sanguine red-chalk
chalk = np.array([0.97, 0.95, 0.90])          # white chalk
toned_t = toned[None, None, :] * (1.0 + 0.03 * vnoise(40)[..., None])
rgb2 = toned_t * (1 - ink[..., None]) + sang[None, None, :] * ink[..., None]
rgb2 = rgb2 * (1 - hi[..., None]) + chalk[None, None, :] * hi[..., None]
rgb2 = np.clip(rgb2, 0, 1)
write_png(os.path.join(OUT, "sanguine_face.png"), (rgb2 * 255).astype(np.uint8))
print("wrote sanguine_face.png  highlight coverage = %.3f" % hi.mean())


# ── VARIANT: CONTOUR engraving — strokes follow the FORM, not a fixed angle.
#    Hatch the iso-tone CONTOURS of the value field: lines of constant `light`
#    wrap the face like a topographic/banknote engraving and crowd where the
#    form turns fast (automatic tonal density). A faint straight cross adds grit.
Lf = np.where(inside, light, 1.0)
contour_phase = Lf * 30.0 + 1.2 * vnoise(22)        # value-bands + slight waver
dc = np.abs(contour_phase - np.round(contour_phase))
cline = np.clip((0.40 - dc) / 0.40, 0, 1) ** 0.7
cline = cline * (1.0 - 0.40 * np.clip(grain * 0.5 + 0.5, 0, 1))
cink = np.where(inside, cline, 0.0)
# deepen darks with a single straight cross only where it's already dark
cink = np.clip(cink + 0.7 * hatch_layer(np.radians(-28), 5.0, 0.62), 0, 1)

paper3 = np.array([0.95, 0.93, 0.87])
ink3 = np.array([0.09, 0.10, 0.13])
paper3_t = paper3[None, None, :] * (1.0 + 0.025 * vnoise(40)[..., None])
rgb3 = paper3_t * (1 - cink[..., None]) + ink3[None, None, :] * cink[..., None]
rgb3 = np.clip(rgb3, 0, 1)
write_png(os.path.join(OUT, "contour_face.png"), (rgb3 * 255).astype(np.uint8))
print("wrote contour_face.png  ink coverage = %.3f" % cink.mean())


# ── VARIANT: form-following engraving — parallel strokes whose DIRECTION is
#    rotated by the local value-gradient (strokes run ALONG the surface), so the
#    hatch lies on the form like a banknote portrait — the fix for the contour
#    topo-map. Spacing stays ~uniform (tone drives stroke WEIGHT, not spacing).
def box_blur(a, k):
    pad = np.pad(a, k, mode="edge")
    c = np.cumsum(np.cumsum(pad, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    s = 2 * k + 1
    out = (c[s:, s:] - c[:-s, s:] - c[s:, :-s] + c[:-s, :-s]) / (s * s)
    return out[: a.shape[0], : a.shape[1]]


Lb = box_blur(np.where(inside, light, 1.0), 9)          # smooth orientation field
gby, gbx = np.gradient(Lb)
mag = np.sqrt(gbx ** 2 + gby ** 2) + 1e-6
tx, ty = -gby / mag, gbx / mag                          # tangent = ALONG contours

# Line Integral Convolution: smear a banded noise ALONG the tangent field, so
# streaks lie on the form (the correct fix for the moiré of global-coord angles).
seed = (rng.random((H, W)) > 0.62).astype(float)        # sparse impulses → LIC
#                                                         smears them into spaced
#                                                         engraving lines w/ gaps


def sample(arr, fy, fx):
    iy = np.clip(np.round(fy).astype(int), 0, H - 1)
    ix = np.clip(np.round(fx).astype(int), 0, W - 1)
    return arr[iy, ix]


def lic(field_x, field_y, steps=14, h=1.3):
    acc = seed.copy(); cnt = np.ones_like(seed)
    for sgn in (1.0, -1.0):
        fx = xs.astype(float).copy(); fy = ys.astype(float).copy()
        for _ in range(steps):
            vx = sample(field_x, fy, fx); vy = sample(field_y, fy, fx)
            fx = fx + sgn * h * vx; fy = fy + sgn * h * vy
            acc = acc + sample(seed, fy, fx); cnt = cnt + 1
    return acc / cnt


S = lic(tx, ty, steps=16, h=1.25)                       # streaks following the form
S = (S - S.min()) / (S.max() - S.min() + 1e-9)
# threshold into discrete dark LINES; darker tone RAISES the threshold so more
# of each streak inks (closer/heavier lines), capped so darks never go fully solid
thr = 0.21 + 0.44 * np.clip(D, 0, 1)
eink = np.clip((thr - S) / 0.10, 0, 1)
# cross-engrave the darks with a second pass along the NORMAL (down-slope)
S2 = lic(gbx / mag, gby / mag, steps=14, h=1.25)
S2 = (S2 - S2.min()) / (S2.max() - S2.min() + 1e-9)
thr2 = 0.18 + 0.34 * np.clip((D - 0.45) / 0.5, 0, 1)
eink2 = np.clip((thr2 - S2) / 0.10, 0, 1) * np.clip((D - 0.5) / 0.4, 0, 1)
eink = np.where(inside, np.clip(eink + eink2, 0, 1), 0.0)

rgb4 = paper_t * (1 - eink[..., None]) + inkc[None, None, :] * eink[..., None]
rgb4 = np.clip(rgb4, 0, 1)
write_png(os.path.join(OUT, "engraved_face.png"), (rgb4 * 255).astype(np.uint8))
print("wrote engraved_face.png  ink coverage = %.3f" % eink.mean())
