"""
Reaction–diffusion, grown once more: a RADIAL feed-rate field. F is low at the centre (a
quiescent void) and rises with radius, so the regimes arrange themselves as concentric bands —
a dark still eye, a ring of dividing spots, an annulus of worms, a coral rim. k held fixed;
the radial F alone drives the bifurcation sequence outward. An iris made of chemistry.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
GW, GH = 480, 340
STEPS = 12000
Du, Dv, dt = 0.16, 0.08, 1.0
rng = np.random.default_rng(11)

yy, xx = np.mgrid[0:GH, 0:GW]
r = np.sqrt(((xx - GW / 2) / (GW / 2)) ** 2 + ((yy - GH / 2) / (GH / 2)) ** 2)  # 0 centre -> ~1.4 corner
F = np.clip(0.020 + 0.030 * r, 0.020, 0.052).astype(np.float64)   # void centre, coral rim
k = np.full((GH, GW), 0.062)

U = np.ones((GH, GW), np.float64)
V = np.zeros((GH, GW), np.float64)
seed = rng.random((GH, GW)) > 0.65
V[seed] = 0.25
U[seed] = 0.50


def lap(Z):
    return (-Z + 0.20*(np.roll(Z,1,0)+np.roll(Z,-1,0)+np.roll(Z,1,1)+np.roll(Z,-1,1))
            + 0.05*(np.roll(np.roll(Z,1,0),1,1)+np.roll(np.roll(Z,1,0),-1,1)
                    + np.roll(np.roll(Z,-1,0),1,1)+np.roll(np.roll(Z,-1,0),-1,1)))


for _ in range(STEPS):
    uvv = U * V * V
    U += (Du * lap(U) - uvv + F * (1 - U)) * dt
    V += (Dv * lap(V) + uvv - (F + k) * V) * dt

v = V - V.min()
v /= (v.max() or 1.0)
v = np.power(v, 0.85)

stops = np.array([
    [0.03, 0.02, 0.05], [0.24, 0.06, 0.22], [0.62, 0.10, 0.34],
    [0.92, 0.45, 0.20], [0.99, 0.93, 0.80],
])
t = v * (len(stops) - 1)
i0 = np.clip(t.astype(int), 0, len(stops) - 2)
f = (t - i0)[..., None]
img = np.clip(stops[i0] + (stops[i0 + 1] - stops[i0]) * f, 0, 1)

S = 3
img = np.repeat(np.repeat(img, S, 0), S, 1)
write_png(os.path.join(OUT, "grayscott_iris.png"), (img * 255).astype(np.uint8))
k2 = 4
hh, ww = (img.shape[0]//k2)*k2, (img.shape[1]//k2)*k2
prev = img[:hh, :ww].reshape(hh//k2, k2, ww//k2, k2, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_iris_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote grayscott_iris.png ({GW*S}x{GH*S}, radial F void->rim, k=0.062)")
