"""
Harmonograph — the Victorian drawing machine: a pen on one pendulum over a table on another, each
swinging and slowly dying away. Two decaying sinusoids per axis trace a looping Lissajous curve
that never quite closes as the amplitude bleeds out:

    x(t) = Σ Aᵢ sin(fᵢ t + pᵢ) e^(−dᵢ t)
    y(t) = Σ Bⱼ sin(gⱼ t + qⱼ) e^(−eⱼ t)

Near-rational frequency ratios give the standing rose; the tiny detuning + damping make it spiral
inward, so the curve is a whole family of nested loops drawn in one unbroken stroke. Rendered as a
thin luminous line accumulated onto black, cool-to-warm along its length (time as colour).
"""
import os
import math
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W = H = 1200
STEPS = 240_000
dt = 0.0009

# two lateral + two lateral, near-rational ratios with slight detune → drifting rose
fx1, fx2 = 2.0, 3.01
fy1, fy2 = 3.0, 2.006
px1, px2 = 0.0, math.pi / 2
py1, py2 = math.pi / 4, 0.0
d = 0.0016   # damping

t = np.arange(STEPS) * dt
ex = np.exp(-d * t)
x = (np.sin(fx1 * t + px1) + 0.7 * np.sin(fx2 * t + px2)) * ex
y = (np.sin(fy1 * t + py1) + 0.7 * np.sin(fy2 * t + py2)) * ex

# map to pixels (curve lives in ~[-1.7,1.7])
m = 1.75
gx = ((x / m * 0.5 + 0.5) * (W - 1)).astype(np.int32)
gy = ((y / m * 0.5 + 0.5) * (H - 1)).astype(np.int32)
gx = np.clip(gx, 0, W - 1); gy = np.clip(gy, 0, H - 1)

# accumulate colour along the stroke (cool start → warm end)
img = np.zeros((H, W, 3), np.float64)
frac = t / t[-1]
cool = np.array([0.25, 0.55, 0.95])
warm = np.array([1.00, 0.72, 0.30])
cols = cool[None, :] + (warm - cool)[None, :] * frac[:, None]
np.add.at(img, (gy, gx), cols * 0.5)

# light bloom via a cheap 3x3 spread, then tone-map
img = 1.0 - np.exp(-1.8 * img)
np.clip(img, 0, 1, out=img)
write_png(os.path.join(OUT, "harmonograph.png"), (img * 255).astype(np.uint8))
k = 3
hh, ww = (H // k) * k, (W // k) * k
prev = img[:hh, :ww].reshape(hh // k, k, ww // k, k, 3).mean(axis=(1, 3))
write_png("/private/tmp/claude-501/-Users-beckyconning-conceptmodel/fafc4c16-3002-4c19-994d-3bed032b12f5/scratchpad/harmo_prev.png",
          (prev * 255).astype(np.uint8))
print(f"wrote harmonograph.png ({W}x{H}, {STEPS} steps)")
