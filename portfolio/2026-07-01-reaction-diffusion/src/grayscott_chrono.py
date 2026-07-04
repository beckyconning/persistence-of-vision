"""
Reaction–diffusion as CHRONOPHOTOGRAPH — the piece that most belongs to a persistence-of-vision
corpus. A single still frame that encodes TIME: V is snapshotted early, mid, and late, and the
three moments are mapped to three colour channels. Where the organism reached early glows one
hue, where it arrived late another; the standing final structure is white (present at all three).
The growth history — normally lost the instant the next step overwrites it — is held in one image,
the way a long exposure holds a moving light. Uses the spatially-varying atlas field.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
GW, GH = 480, 340
STEPS = 12000
SNAPS = (2200, 5200, 11999)   # early / mid / late
Du, Dv, dt = 0.16, 0.08, 1.0
rng = np.random.default_rng(3)

xs = np.linspace(0.022, 0.050, GW)[None, :]
ys = np.linspace(0.058, 0.065, GH)[:, None]
F = np.broadcast_to(xs, (GH, GW)).copy()
k = np.broadcast_to(ys, (GH, GW)).copy()

U = np.ones((GH, GW), np.float64)
V = np.zeros((GH, GW), np.float64)
seed = rng.random((GH, GW)) > 0.65
V[seed] = 0.25
U[seed] = 0.50


def lap(Z):
    return (-Z + 0.20*(np.roll(Z,1,0)+np.roll(Z,-1,0)+np.roll(Z,1,1)+np.roll(Z,-1,1))
            + 0.05*(np.roll(np.roll(Z,1,0),1,1)+np.roll(np.roll(Z,1,0),-1,1)
                    + np.roll(np.roll(Z,-1,0),1,1)+np.roll(np.roll(Z,-1,0),-1,1)))


snaps = {}
for step in range(STEPS):
    uvv = U * V * V
    U += (Du * lap(U) - uvv + F * (1 - U)) * dt
    V += (Dv * lap(V) + uvv - (F + k) * V) * dt
    if step in SNAPS:
        s = V.copy(); s -= s.min(); s /= (s.max() or 1.0)
        snaps[step] = np.power(s, 0.8)

# early->magenta, mid->amber, late->cyan; overlaps sum toward white (present across time)
early, mid, late = (snaps[SNAPS[0]], snaps[SNAPS[1]], snaps[SNAPS[2]])
c_e = np.array([0.95, 0.15, 0.55])   # magenta
c_m = np.array([0.98, 0.65, 0.15])   # amber
c_l = np.array([0.20, 0.85, 0.95])   # cyan
img = (early[..., None] * c_e + mid[..., None] * c_m + late[..., None] * c_l) * 0.62
np.clip(img, 0, 1, out=img)

S = 3
img = np.repeat(np.repeat(img, S, 0), S, 1)
write_png(os.path.join(OUT, "grayscott_chrono.png"), (img * 255).astype(np.uint8))
k2 = 4
hh, ww = (img.shape[0]//k2)*k2, (img.shape[1]//k2)*k2
prev = img[:hh, :ww].reshape(hh//k2, k2, ww//k2, k2, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_chrono_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote grayscott_chrono.png ({GW*S}x{GH*S}, snaps={SNAPS})")
