"""
Reaction-diffusion — a NEW technique for the corpus (not packing, not flow-field streamlines,
not hard-edge planes, not orbit-density attractors): a Gray-Scott PDE simulated on a grid.
Two virtual chemicals U and V diffuse at different rates and react U + 2V -> 3V; the standing
pattern that emerges — coral, labyrinth, mitosing cells — is a SOLUTION of the equations, not a
drawn form. Nobody places the filaments; they are where the chemistry settles.

  dU/dt = Du·∇²U − U·V² + F·(1−U)
  dV/dt = Dv·∇²V + U·V² − (F+k)·V

Regime F=0.055, k=0.062 sits on the coral/mitosis boundary: growing lobes that split and crowd,
never quite filling the field. Seeded from a handful of asymmetric blobs so the growth has a
direction and the frame reads as one organism, not a tiling.

Palette (grows the corpus away from the cold clifford ramp): a WARM membrane — near-black ground,
deep plum in the quiescent voids, burning up through magenta/amber along the reacting fronts to a
pale cream at the crests where V is densest. V-concentration (not a stroke) IS the image.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
GW, GH = 440, 320           # simulation grid (kept modest; RD cost = steps × pixels)
STEPS = 12000
# F=0.037 k=0.062 = the "worms" regime (found by a (F,k) reconnaissance sweep — see sweep.py:
# it lands V-coverage ~0.32, the living band between dead <0.03 and saturated >0.6). Seeded
# spots elongate into connected winding filaments that fill the frame without clogging it.
Du, Dv, F, k, dt = 0.16, 0.08, 0.037, 0.062, 1.0
rng = np.random.default_rng(7)   # fixed seed → reproducible organism

U = np.ones((GH, GW), np.float64)
V = np.zeros((GH, GW), np.float64)
# scatter V-seeds over ~35% of cells → coral nucleates everywhere and grows to fill the frame
seed = rng.random((GH, GW)) > 0.65
V[seed] = 0.25
U[seed] = 0.50
np.clip(V, 0, 1, out=V)


def lap(Z):
    # 9-point Laplacian stencil (periodic edges via roll) — smoother fronts than the 5-point
    return (
        -Z
        + 0.20 * (np.roll(Z, 1, 0) + np.roll(Z, -1, 0) + np.roll(Z, 1, 1) + np.roll(Z, -1, 1))
        + 0.05 * (np.roll(np.roll(Z, 1, 0), 1, 1) + np.roll(np.roll(Z, 1, 0), -1, 1)
                  + np.roll(np.roll(Z, -1, 0), 1, 1) + np.roll(np.roll(Z, -1, 0), -1, 1))
    )


for step in range(STEPS):
    uvv = U * V * V
    U += (Du * lap(U) - uvv + F * (1 - U)) * dt
    V += (Dv * lap(V) + uvv - (F + k) * V) * dt

# normalise V to [0,1] for the ramp
v = V - V.min()
v /= (v.max() or 1.0)
v = np.power(v, 0.85)   # slight lift so the mid fronts read

# warm membrane ramp: near-black ground -> plum -> magenta -> amber -> cream crest
stops = np.array([
    [0.03, 0.02, 0.05],   # ground
    [0.24, 0.06, 0.22],   # deep plum void
    [0.62, 0.10, 0.34],   # magenta front
    [0.92, 0.45, 0.20],   # amber reacting edge
    [0.99, 0.93, 0.80],   # pale cream crest
])
t = v * (len(stops) - 1)
i0 = np.clip(t.astype(int), 0, len(stops) - 2)
f = (t - i0)[..., None]
img = stops[i0] + (stops[i0 + 1] - stops[i0]) * f
np.clip(img, 0, 1, out=img)

# upscale 3× (nearest) so the export is gallery-sized without re-simulating
S = 3
img = np.repeat(np.repeat(img, S, 0), S, 1)
write_png(os.path.join(OUT, "grayscott.png"), (img * 255).astype(np.uint8))

# small preview for quick inspection
k2 = 3
hh, ww = (img.shape[0] // k2) * k2, (img.shape[1] // k2) * k2
prev = img[:hh, :ww].reshape(hh // k2, k2, ww // k2, k2, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/rd_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote grayscott.png ({GW*S}x{GH*S}, {STEPS} steps, F={F} k={k})")
