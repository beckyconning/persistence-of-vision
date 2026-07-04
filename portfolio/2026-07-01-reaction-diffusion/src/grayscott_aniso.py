"""
Reaction–diffusion, anisotropic: the diffusion is split into independent x and y rates, so the
medium has a GRAIN. V spreads faster along one axis than the other, and the worms can no longer
wander freely — they comb into aligned, flowing stripes, like a fingerprint, a wood grain, or
wind-combed dune grass. Isotropic Gray-Scott gives a maze; anisotropic gives a current.

    ∂U/∂t = (Dux·∂²ₓ + Duy·∂²_y)U − UV² + F(1−U)
    ∂V/∂t = (Dvx·∂²ₓ + Dvy·∂²_y)V + UV² − (F+k)V
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
GW, GH = 480, 340
STEPS = 13000
F, k, dt = 0.037, 0.062, 1.0
# grain: U diffuses fast in x, V fast in y -> stripes comb roughly horizontal
Dux, Duy = 0.20, 0.11
Dvx, Dvy = 0.05, 0.11
rng = np.random.default_rng(5)

U = np.ones((GH, GW), np.float64)
V = np.zeros((GH, GW), np.float64)
seed = rng.random((GH, GW)) > 0.65
V[seed] = 0.25
U[seed] = 0.50


def d2x(Z):
    return np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 2 * Z


def d2y(Z):
    return np.roll(Z, 1, 0) + np.roll(Z, -1, 0) - 2 * Z


for _ in range(STEPS):
    uvv = U * V * V
    U += (Dux * d2x(U) + Duy * d2y(U) - uvv + F * (1 - U)) * dt
    V += (Dvx * d2x(V) + Dvy * d2y(V) + uvv - (F + k) * V) * dt

v = V - V.min(); v /= (v.max() or 1.0)
v = np.power(v, 0.85)
# warm membrane ramp (corpus-coherent)
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
write_png(os.path.join(OUT, "grayscott_aniso.png"), (img * 255).astype(np.uint8))
k2 = 4
hh, ww = (img.shape[0]//k2)*k2, (img.shape[1]//k2)*k2
prev = img[:hh, :ww].reshape(hh//k2, k2, ww//k2, k2, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_aniso_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote grayscott_aniso.png ({GW*S}x{GH*S}, aniso Du=({Dux},{Duy}) Dv=({Dvx},{Dvy}))")
