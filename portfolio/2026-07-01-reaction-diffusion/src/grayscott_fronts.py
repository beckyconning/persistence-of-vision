"""
Reaction–diffusion, final grow: render by the REACTION RATE, not the concentration. R = U·V² is
where U is actively being converted to V — the living fronts, the growing edges. Most RD art
shows V (where the reaction HAS been); this shows where it IS, right now. The V-membrane is laid
down cool and dim; the instantaneous reaction zone is painted hot over it, so the piece reads as
an organism caught mid-metabolism — quiet in its settled body, incandescent along its growing rim.
Uses the spatially-varying (atlas) field so the front intensity itself varies across regimes.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
GW, GH = 480, 340
STEPS = 12000
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


for step in range(STEPS):
    uvv = U * V * V
    U += (Du * lap(U) - uvv + F * (1 - U)) * dt
    V += (Dv * lap(V) + uvv - (F + k) * V) * dt

# EDGE of V = the interface between body and void — the true growing rim (thin contour, not fill)
gx = np.roll(V, -1, 1) - np.roll(V, 1, 1)
gy = np.roll(V, -1, 0) - np.roll(V, 1, 0)
edge = np.sqrt(gx * gx + gy * gy)
edge /= (edge.max() or 1.0)
edge = np.power(edge, 0.6)[..., None]        # lift so thin contours read

# filled dim body from V (interior), so the neon rim sits on a faint plum membrane
v = V - V.min(); v /= (v.max() or 1.0)
body = np.stack([0.14 * v + 0.02, 0.05 * v + 0.01, 0.16 * v + 0.03], -1)   # dim plum fill
neon = np.array([0.30, 0.95, 0.90])          # cyan-teal contour
img = body + edge * (neon - body)            # paint the rim over the body
img += (edge ** 3) * np.array([0.35, 0.05, 0.0])   # warm spark on the sharpest edges
np.clip(img, 0, 1, out=img)

S = 3
img = np.repeat(np.repeat(img, S, 0), S, 1)
write_png(os.path.join(OUT, "grayscott_fronts.png"), (img * 255).astype(np.uint8))
k2 = 4
hh, ww = (img.shape[0]//k2)*k2, (img.shape[1]//k2)*k2
prev = img[:hh, :ww].reshape(hh//k2, k2, ww//k2, k2, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_fronts_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote grayscott_fronts.png ({GW*S}x{GH*S}, reaction-rate render)")
