"""
Breathing colour field — the colour interaction, animated (APNG).

Combines the two open FRONTIERS threads at once: a COLOUR-field (not line/geometry)
that also MOVES. The fields' inner luminosity swells and settles in a slow seamless
loop, and the warm ground drifts a touch cooler/warmer in counter-phase — so the eye
reads the simultaneous contrast *shifting* (the orange looks hotter as the ground
cools). Time as the material, colour as the subject.
"""
import os
import numpy as np
from apnglib import write_apng

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 640, 820
N = 36
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(float)
u, v = xx / W, yy / H


def smooth(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def vnoise(freq, seed):
    g = np.random.default_rng(seed).standard_normal((freq + 2, freq + 2))
    yv = np.linspace(0, freq, H)[:, None] * np.ones((1, W))
    xv = np.linspace(0, freq, W)[None, :] * np.ones((H, 1))
    x0, y0 = np.floor(xv).astype(int), np.floor(yv).astype(int)
    fx, fy = xv - x0, yv - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - sx) + g[y0, x0 + 1] * sx
    b = g[y0 + 1, x0] * (1 - sx) + g[y0 + 1, x0 + 1] * sx
    return a * (1 - sy) + b * sy


GRAIN = vnoise(180, 1)          # fixed canvas tooth (doesn't flicker)
DRIFT = vnoise(5, 2)


def field(cx, cy, w, h, feather, edge, core, breath):
    mx = smooth(cx - w / 2 - feather, cx - w / 2 + feather, u) * \
        (1 - smooth(cx + w / 2 - feather, cx + w / 2 + feather, u))
    my = smooth(cy - h / 2 - feather, cy - h / 2 + feather, v) * \
        (1 - smooth(cy + h / 2 - feather, cy + h / 2 + feather, v))
    mask = (mx * my)[..., None]
    dist = np.sqrt(((u - cx) / (w / 2)) ** 2 + ((v - cy) / (h / 2)) ** 2)
    glow = (1 - smooth(0.45, 1.05, dist)) * breath           # breath scales luminosity
    col = edge[None, None, :] + (core - edge)[None, None, :] * glow[..., None]
    return mask, col


frames = []
for f in range(N):
    ph = 2 * np.pi * f / N
    breath1 = 0.80 + 0.20 * np.sin(ph)                       # upper field swells
    breath2 = 0.80 + 0.20 * np.sin(ph + 2.0)                 # lower, offset
    cool = 0.5 + 0.5 * np.sin(ph + np.pi)                    # ground counter-phase
    gtop = np.array([0.20 - 0.03 * cool, 0.03, 0.04 + 0.02 * cool])
    gbot = np.array([0.42 - 0.04 * cool, 0.09, 0.07 + 0.02 * cool])
    img = gtop[None, None, :] + (gbot - gtop)[None, None, :] * v[..., None]
    m1, c1 = field(0.5, 0.36, 0.62, 0.40, 0.10,
                   np.array([0.55, 0.12, 0.06]), np.array([0.95, 0.44, 0.14]), breath1)
    m2, c2 = field(0.5, 0.72, 0.62, 0.34, 0.09,
                   np.array([0.10, 0.02, 0.06]), np.array([0.36, 0.09, 0.17]), breath2)
    img = img * (1 - m1) + c1 * m1
    img = img * (1 - m2) + c2 * m2
    img = img * (1.0 + 0.05 * DRIFT[..., None]) + 0.012 * GRAIN[..., None]
    halo = 1 - 0.22 * np.sqrt(((u - 0.5) / 0.62) ** 2 + ((v - 0.5) / 0.62) ** 2)
    img = np.clip(np.clip(img * halo[..., None], 0, 1) ** 0.92, 0, 1)
    frames.append((img * 255).astype(np.uint8))

write_apng(os.path.join(OUT, "breathing.png"), frames, delay_num=8, delay_den=100)
print("wrote breathing.png (%d frames, seamless)" % N)
