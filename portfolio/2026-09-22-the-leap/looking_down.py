"""Looking Down (study): someone stands at the far end of the puddle. Their shoes are in frame; their face is only in the water.

Constraints come from the morning itself (Open-Meteo, 2026-09-22 08:30, 53.48N 2.23W):
rain 0.0 mm -> no rain rings; wind 2.9 km/h -> the only ripple; cloud 98 percent -> exactly
2 percent of the reflected sky is blue. No caption: the numbers are carried by the water.
"""
import sys
import numpy as np
from PIL import Image

RAIN_MM, WIND_KMH, CLOUD_PCT = 0.0, 2.9, 98
W, H, SS = 1200, 1600, 2                     # output size, supersampling
OUT = sys.argv[1] if len(sys.argv) > 1 else "looking-down.png"
LEAPER = False
TIME = float(next((a[4:] for a in sys.argv if a.startswith("--t=")), "0"))   # seconds; 0 = the still
if "--small" in sys.argv: W, H, SS = 600, 800, 1
rng = np.random.default_rng(922)

# ---- camera: standing on Stevenson Square, looking down and ahead -------------------
cam = np.array([0.0, 0.0, 1.62])
DETAIL = "--detail" in sys.argv
pitch = np.radians(-50.2 if DETAIL else -45.0)   # the detail looks straight at the face in the water
vfov = np.radians(13.0 if DETAIL else 44.0)
w, h = W * SS, H * SS
fy = np.tan(vfov / 2)
fx = fy * w / h
u = (np.arange(w) + 0.5) / w * 2 - 1
v = 1 - (np.arange(h) + 0.5) / h * 2
U, V = np.meshgrid(u * fx, v * fy)
fwd = np.array([0, np.cos(pitch), np.sin(pitch)])
up = np.array([0, -np.sin(pitch), np.cos(pitch)])
right = np.array([1.0, 0, 0])
D = fwd[None, None] + U[..., None] * right[None, None] + V[..., None] * up[None, None]
D /= np.linalg.norm(D, axis=-1, keepdims=True)

t = -cam[2] / D[..., 2]
P = cam[None, None] + t[..., None] * D          # ground hit (every pixel sees ground)
X, Y = P[..., 0], P[..., 1]

def vnoise(x, y, f, seed):
    r = np.random.default_rng(seed)
    g = r.random((257, 257))
    xs, ys = x * f, y * f
    xs = xs - xs.min(); ys = ys - ys.min()
    i, j = np.floor(xs).astype(int) % 256, np.floor(ys).astype(int) % 256
    fx_, fy_ = xs - np.floor(xs), ys - np.floor(ys)
    fx_ = fx_ * fx_ * (3 - 2 * fx_); fy_ = fy_ * fy_ * (3 - 2 * fy_)
    a = g[j, i] * (1 - fx_) + g[j, i + 1] * fx_
    b = g[j + 1, i] * (1 - fx_) + g[j + 1, i + 1] * fx_
    return a * (1 - fy_) + b * fy_ - 0.5

def vfbm(x, y, oct, f, seed):
    return sum(0.5 ** o * vnoise(x, y, f * 2.1 ** o, seed + o) for o in range(oct))

def fbm(x, y, oct=5, f=1.0, seed=0):
    r = np.random.default_rng(seed)
    s = np.zeros_like(x)
    a = 1.0
    for _ in range(oct):
        th = r.uniform(0, 2 * np.pi, 3)
        ph = r.uniform(0, 2 * np.pi, 3)
        for k in range(3):
            s += a * np.sin(f * (x * np.cos(th[k]) + y * np.sin(th[k])) + ph[k]) / 3
        a *= 0.5
        f *= 2.03
    return s

# ---- puddle: off-centre, a real outline, not an ellipse ---------------------------
cx, cy, rx, ry = 0.10, 1.86, 0.62, 0.86
blob = ((X - cx) / rx) ** 2 + ((Y - cy) / ry) ** 2 + 0.55 * fbm(X, Y, 4, 3.0, 7)
puddle = blob < 1.0
edge = np.clip((1.0 - blob) / 0.018, 0, 1)        # soft shoreline

# ---- the water's surface: wind is the only thing moving it ------------------------
slope = 0.0007 * WIND_KMH          # light air: a shiver, not a chop
k = 2 * np.pi / 0.035
hx = np.zeros_like(X); hy = np.zeros_like(X)
for i in range(7):
    th = rng.uniform(-0.6, 0.6) + np.radians(20)  # a breath from roughly one side
    kk = k * rng.uniform(0.6, 1.6)
    ph = rng.uniform(0, 2 * np.pi) + TIME * np.sqrt(9.81 * kk + 0.074 / 1000 * kk ** 3)   # capillary-gravity dispersion
    c = np.cos(kk * (X * np.cos(th) + Y * np.sin(th)) + ph) * slope / 7 * 2.2
    hx += c * np.cos(th); hy += c * np.sin(th)
# RAIN_MM == 0: no rings. (Each mm/h would add expanding rings here.)
N = np.stack([-hx, -hy, np.ones_like(X)], -1)
N /= np.linalg.norm(N, axis=-1, keepdims=True)
R = D - 2 * np.sum(D * N, -1, keepdims=True) * N  # reflected ray, going up

# ---- what the water sees ------------------------------------------------------
refl = np.zeros(X.shape + (3,))
hit = np.zeros(X.shape, bool)

# sky: overcast, with a gap that is exactly (100 - CLOUD_PCT) percent of the reflected sky
sx = X + R[..., 0] / R[..., 2] * 900.0
sy = Y + R[..., 1] / R[..., 2] * 900.0
cloud = vfbm(sx / 260.0, sy / 700.0, 4, 1.0, 3) + 0.12 * vfbm(sx / 40.0, sy / 90.0, 3, 1.0, 5)   # one torn gap, stretched by the breeze
overcast = np.array([226, 228, 229]) / 255
grey = np.array([196, 200, 204]) / 255
elev = np.arcsin(np.clip(R[..., 2], 0, 1))
cie = ((1 + 2 * np.sin(elev)) / 3)[..., None]                 # CIE overcast: brightest overhead
mix = 0.35 * np.clip(cloud * 2 + 0.5, 0, 1)[..., None]
sky = (overcast[None, None] * (1 - mix) + grey[None, None] * mix) * (0.72 + 0.34 * cie)

# buildings across the street: brick, windows that hold more sky
by, bh = 26.0, 16.0
tb = (by - Y) / R[..., 1]
bz = tb * R[..., 2]
bx = X + tb * R[..., 0]
onb = (R[..., 1] > 0) & (bz < bh)
brick = np.array([124, 84, 70]) / 255
col = ((bx + 40) // 3.4).astype(int)
tone = 0.9 + 0.12 * np.sin(col * 12.9898) * np.sin(col * 78.233)
bcol = brick[None, None] * tone[..., None]
wx = np.mod(bx + 40, 3.4); wz = np.mod(bz, 3.2)
win = (wx > 0.9) & (wx < 2.5) & (wz > 0.9) & (wz < 2.7) & (bz > 3.0)
bcol = np.where(win[..., None], bcol * 0.35 + sky * 0.45, bcol)
cornice = (bz > bh - 0.7)
bcol = np.where(cornice[..., None], bcol * 0.7, bcol)
refl = np.where(onb[..., None], bcol, sky)

# the leaper: a figure mid-air, in a plane just past the puddle, out of the camera's own view
def capsule(px, pz, a, b, r):
    a = np.array(a); b = np.array(b)
    ba = b - a
    t_ = np.clip(((px - a[0]) * ba[0] + (pz - a[1]) * ba[1]) / (ba @ ba), 0, 1)
    return (px - a[0] - t_ * ba[0]) ** 2 + (pz - a[1] - t_ * ba[1]) ** 2 < r * r

if LEAPER:
    fyp = 4.1
    tf = (fyp - Y) / R[..., 1]
    run = 3.4 * TIME                                 # m/s across the square; t=0 is the still
    arc = 0.9 * (TIME / 0.42) ** 2 if abs(TIME) < 0.42 else 2.0   # up and down a parabola, off the ground outside
    fxp = X + tf * R[..., 0] - 0.30 - run
    fzp = tf * R[..., 2] + min(arc, 2.0) * 0.5
    s = np.zeros(X.shape, bool)
    hip, sho = (0.00, 1.38), (0.20, 1.88)
    ph = np.clip(TIME / 0.42, -1, 1)                           # -1 take-off, 0 peak, 1 landing
    spread = 0.55 + 0.45 * np.cos(np.pi * ph / 2)              # legs gather at either end
    reach = 0.25 * max(ph, 0)                                  # the front foot drops towards the ground
    lift = 0.12 * np.cos(np.pi * ph / 2)                       # arms highest at the peak
    def L(p):                                                  # a leg point, relative to the hip
        return (hip[0] + (p[0] - hip[0]) * spread, hip[1] + (p[1] - hip[1]) * spread - (reach if p[0] > 0 else 0))
    def A(p):
        return (p[0], p[1] + lift)
    s |= capsule(fxp, fzp, hip, sho, 0.13)                         # torso, leaning into it
    s |= capsule(fxp, fzp, (0.02, 1.50), (0.16, 1.80), 0.125)        # coat
    s |= ((fxp - 0.30) ** 2 + (fzp - 2.06) ** 2) < 0.105 ** 2       # head
    s |= capsule(fxp, fzp, (0.22, 2.16), (0.44, 2.13), 0.035)       # cap brim
    s |= capsule(fxp, fzp, (0.20, 2.14), (0.36, 2.17), 0.07)        # cap
    s |= capsule(fxp, fzp, hip, L((0.40, 1.28)), 0.062)               # front thigh
    s |= capsule(fxp, fzp, L((0.40, 1.28)), L((0.74, 1.10)), 0.05)        # front shin, reaching
    s |= capsule(fxp, fzp, L((0.72, 1.10)), L((0.86, 1.12)), 0.045)       # front foot
    s |= capsule(fxp, fzp, hip, L((-0.30, 1.16)), 0.062)              # back thigh
    s |= capsule(fxp, fzp, L((-0.30, 1.16)), L((-0.50, 1.46)), 0.05)      # back shin, kicked up
    s |= capsule(fxp, fzp, L((-0.50, 1.46)), L((-0.62, 1.40)), 0.045)     # back foot
    s |= capsule(fxp, fzp, sho, A((0.46, 2.10)), 0.046)               # arm up
    s |= capsule(fxp, fzp, A((0.46, 2.10)), A((0.60, 2.38)), 0.038)       # forearm, flung high
    s |= capsule(fxp, fzp, A((0.14, 1.85)), A((-0.14, 1.96)), 0.046)      # other arm, back
    s |= capsule(fxp, fzp, A((-0.14, 1.96)), A((-0.36, 2.16)), 0.038)
    s |= capsule(fxp, fzp, (-0.02, 1.46), (-0.24, 1.32), 0.05)      # coat tail flying
    s &= (R[..., 1] > 0) & (tf > 0)
    dark = np.array([44, 42, 44]) / 255
    refl = np.where(s[..., None], dark[None, None], refl)

# the person: a billboard facing us at the puddle's far end
from PIL import ImageDraw
yp = 2.78
FT = 400                                            # face texture: px per metre... (0.26 m x 0.30 m face)
F = 4
face = Image.new("RGB", (104 * F, 120 * F), (206, 160, 134))
fd = ImageDraw.Draw(face)
inkc_ = (58, 40, 36)
def S(*b): return tuple(v * F for v in b)
fd.arc(S(14, 34, 46, 58), 200, 340, fill=inkc_, width=3 * F)      # crescent eyes
fd.arc(S(58, 34, 90, 58), 200, 340, fill=inkc_, width=3 * F)
fd.line(S(8, 44, 13, 40), fill=inkc_, width=F); fd.line(S(8, 47, 13, 46), fill=inkc_, width=F)   # crow's feet
fd.line(S(96, 40, 91, 44), fill=inkc_, width=F); fd.line(S(96, 46, 91, 46), fill=inkc_, width=F)
fd.arc(S(12, 22, 46, 38), 200, 330, fill=inkc_, width=3 * F)      # brows
fd.arc(S(58, 22, 92, 38), 210, 340, fill=inkc_, width=3 * F)
fd.chord(S(30, 72, 74, 104), 0, 180, fill=(120, 48, 48))          # open laugh
fd.line(S(32, 84, 72, 84), fill=(236, 226, 214), width=3 * F)     # teeth
fd.arc(S(22, 60, 38, 96), 110, 200, fill=inkc_, width=2 * F)      # laugh brackets
fd.arc(S(66, 60, 82, 96), 340, 70, fill=inkc_, width=2 * F)
fd.line(S(52, 50, 48, 70), fill=(170, 120, 100), width=2 * F)     # nose
fd.arc(S(42, 64, 54, 72), 20, 160, fill=(170, 120, 100), width=2 * F)
face = np.asarray(face, dtype=np.float32) / 255

def person_at(px, pz):
    """colour and mask of the person at plane coords (x across, z up)"""
    col = np.zeros(px.shape + (3,)); m = np.zeros(px.shape, bool)
    def put(mask, c):
        nonlocal col, m
        col = np.where(mask[..., None], np.array(c) / 255, col); m |= mask
    put(capsule(px, pz, (-0.11, 0.08), (-0.10, 0.86), 0.075) | capsule(px, pz, (0.11, 0.08), (0.10, 0.86), 0.075), (58, 68, 96))  # jeans
    put(capsule(px, pz, (-0.13, 0.04), (-0.07, 0.04), 0.05) | capsule(px, pz, (0.07, 0.04), (0.13, 0.04), 0.05), (236, 234, 228))  # white trainers
    put(capsule(px, pz, (0.0, 0.92), (0.0, 1.38), 0.21) | capsule(px, pz, (-0.02, 0.82), (0.02, 0.9), 0.2), (196, 150, 58))        # mustard coat
    put(capsule(px, pz, (-0.22, 1.36), (-0.27, 0.95), 0.06) | capsule(px, pz, (0.22, 1.36), (0.27, 0.95), 0.06), (186, 140, 52)) # sleeves
    put(capsule(px, pz, (0.0, 1.42), (0.0, 1.5), 0.05), (196, 152, 128))                                                       # neck
    head = ((px / 0.105) ** 2 + ((pz - 1.62) / 0.13) ** 2) < 1
    fu = np.clip(((px + 0.105) / 0.21 * 104 * F).astype(int), 0, 104 * F - 1)
    fv = np.clip(((1.75 - pz) / 0.26 * 120 * F).astype(int), 0, 120 * F - 1)
    col = np.where(head[..., None], face[fv, fu], col); m |= head
    hair = head & (pz > 1.70) | (((px / 0.115) ** 2 + ((pz - 1.68) / 0.13) ** 2) < 1) & ((pz > 1.72) | (np.abs(px) > 0.09))
    put(hair, (62, 40, 30))
    return col, m

# seen in the water
tp = (yp - Y) / R[..., 1]
pc, pm = person_at(X + tp * R[..., 0], tp * R[..., 2])
pm &= (R[..., 1] > 0)
refl = np.where(pm[..., None], pc * 0.92, refl)
s = pm                                               # for the gap mask below
LEAPER = True
# seen directly (only what the frame reaches: shoes and shins at the top edge)
td = (yp - cam[1]) / D[..., 1]
dc, dm = person_at(cam[0] + td * D[..., 0], cam[2] + td * D[..., 2])
dm &= (D[..., 1] > 0) & (cam[2] + td * D[..., 2] > 0)

# the gap: exactly 2 percent of the sky pixels the puddle shows are blue
skymask = puddle & ~onb                                          # the sky itself, leaper or not
thr = np.quantile(cloud[skymask], 1 - (100 - CLOUD_PCT) / 100)
gap = skymask & (cloud >= thr) & ~(s if LEAPER else np.zeros_like(puddle))   # he can hide part of it
blue = np.array([150, 176, 204]) / 255
refl = np.where(gap[..., None], blue[None, None], refl)

# ---- the pavement: York stone flags, wet from the night -------------------------
fw, fl = 0.60, 0.90
row = np.floor(Y / fl)
xo = X + (row % 2) * fw * 0.5
colf = np.floor(xo / fw)
jx = np.mod(xo, fw); jy = np.mod(Y, fl)
joint = (jx < 0.008) | (jx > fw - 0.008) | (jy < 0.008) | (jy > fl - 0.008)
seed = np.sin(colf * 12.9898 + row * 78.233) * 43758.5453
ftone = 0.86 + 0.14 * (seed - np.floor(seed))
grain = 0.16 * vfbm(X, Y, 5, 14.0, 11) + 0.10 * vfbm(X, Y, 3, 90.0, 23) + 0.025 * rng.standard_normal(X.shape)
stone = np.array([132, 128, 120]) / 255
pav = stone[None, None] * (ftone + grain)[..., None]
wet = np.clip((1.45 - blob) / 0.45, 0, 1) ** 1.6 * (0.8 + 0.4 * vfbm(X, Y, 3, 8.0, 31))                        # darker towards the water
pav = pav * (1 - 0.42 * wet[..., None])
pav = np.where(joint[..., None], pav * 0.45, pav)
lichen = (vfbm(X, Y, 4, 6.0, 17) > 0.33) & ~puddle
pav = np.where(lichen[..., None], pav * 0.92 + np.array([0.03, 0.035, 0.01]), pav)

# ---- water over stone: the bottom shows a little, the reflection most ------------
cos_i = np.clip(-np.sum(D * N, -1), 0, 1)
fres = 0.02 + 0.98 * (1 - cos_i) ** 5
Rw = np.clip(0.60 + 1.2 * fres, 0, 0.95)
bottom = np.where(joint[..., None], pav / 0.45 * 0.8, pav) * 0.55   # joints soften under water
water = bottom * (1 - Rw[..., None]) + refl * Rw[..., None]
img = pav * (1 - edge[..., None]) + water * edge[..., None]

# soft overcast light: a gentle fall-off away from the viewer, no cast shadows
img = np.where(dm[..., None], dc, img)
img *= (0.93 + 0.07 * (V + 1) / 2)[..., None]
img = np.clip(img, 0, 1) ** (1 / 1.05)
out = (img * 255).reshape(H, SS, W, SS, 3).mean((1, 3)).astype(np.uint8)
Image.fromarray(out).save(OUT)
print(OUT, "gap px", int(gap.sum()), "sky px", int(skymask.sum()),
      "ratio %.4f" % (gap.sum() / max(1, skymask.sum())))
