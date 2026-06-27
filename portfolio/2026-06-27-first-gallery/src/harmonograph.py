#!/usr/bin/env python3
"""A harmonograph: two damped pendulums per axis trace a slowly-decaying curve.
Near-integer frequency ratios with a touch of detune make the figure precess,
sweeping a luminous rosette. We sample the curve densely and lay it down with a
small soft brush, hue drifting along the curve's lifetime. numpy + stdlib PNG.

    x(t) = A1 e^{-d1 t} sin(f1 t + p1) + A2 e^{-d2 t} sin(f2 t + p2)
    y(t) = A3 e^{-d3 t} sin(f3 t + p3) + A4 e^{-d4 t} sin(f4 t + p4)
"""
import numpy as np
from pnglib import write_png

W = H = 1500
N = 1_200_000           # samples along the curve
TMAX = 90.0

# frequencies near 2:3 / integer ratios, lightly detuned so the figure precesses
f = [2.001, 3.000, 3.002, 2.000]
p = [np.pi / 2, 0.0, np.pi / 4, np.pi / 3]
A = [1.0, 0.7, 1.0, 0.7]
d = [0.0045, 0.0030, 0.0042, 0.0028]

PAL = np.array([
    [0.30, 0.85, 0.95],   # cyan
    [0.40, 0.55, 0.97],   # blue
    [0.75, 0.40, 0.95],   # violet
    [0.98, 0.45, 0.70],   # pink
    [0.99, 0.80, 0.55],   # warm
])


def main():
    t = np.linspace(0, TMAX, N)
    x = (A[0] * np.exp(-d[0] * t) * np.sin(f[0] * t + p[0])
         + A[1] * np.exp(-d[1] * t) * np.sin(f[1] * t + p[1]))
    y = (A[2] * np.exp(-d[2] * t) * np.sin(f[2] * t + p[2])
         + A[3] * np.exp(-d[3] * t) * np.sin(f[3] * t + p[3]))

    m = 0.92 * W / (2 * 2.0)             # fit (curve spans ~[-2,2])
    px = (W / 2 + x * m)
    py = (H / 2 + y * m)
    ix = px.astype(np.intp); iy = py.astype(np.intp)

    # hue along lifetime
    seg = (t / TMAX) * (len(PAL) - 1)
    j = np.clip(seg.astype(np.intp), 0, len(PAL) - 2)
    fr = (seg - j)[:, None]
    col = PAL[j] + (PAL[j + 1] - PAL[j]) * fr

    acc = np.zeros((H, W, 3))
    good = (ix >= 1) & (ix < W - 1) & (iy >= 1) & (iy < H - 1)
    ix, iy, col = ix[good], iy[good], col[good]
    # soft 4-neighbour brush so the thread has a glow
    for dx, dy, wgt in [(0, 0, 1.0), (1, 0, .4), (-1, 0, .4),
                        (0, 1, .4), (0, -1, .4)]:
        np.add.at(acc, (iy + dy, ix + dx, slice(None)), col * (0.06 * wgt))

    img = 1 - np.exp(-acc * 2.2)         # tone-map the additive thread
    img = np.power(img, 0.9)
    bg = np.array([0.02, 0.02, 0.05])
    lum = img.sum(2, keepdims=True)
    img = np.where(lum < 0.01, bg, img)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    write_png("harmonograph.png", out)
    print("wrote harmonograph.png")


if __name__ == "__main__":
    main()
