#!/usr/bin/env python3
"""Phyllotaxis: 6000 florets placed at successive golden-angle turns,
radius ~ sqrt(n) (Vogel's model). Each floret is a soft radial disc; colour
cycles with the generative angle. numpy + stdlib PNG.

    theta_n = n * 137.507 deg ,  r_n = c * sqrt(n)
"""
import numpy as np
from pnglib import write_png, ramp

W = H = 1400
N = 6000
GOLDEN = np.deg2rad(137.5077640)
C = 15.5                 # spacing constant
DOT = 11                 # disc radius in px

# violet -> blue -> green -> gold -> coral, cycled
STOPS = [
    [0.45, 0.16, 0.62],
    [0.16, 0.34, 0.74],
    [0.16, 0.70, 0.58],
    [0.96, 0.83, 0.30],
    [0.95, 0.45, 0.34],
    [0.45, 0.16, 0.62],
]


def main():
    n = np.arange(N)
    theta = n * GOLDEN
    r = C * np.sqrt(n)
    cx = W / 2 + r * np.cos(theta)
    cy = H / 2 + r * np.sin(theta)
    # colour by petal index modulo a cycle, plus gentle radial fade
    t = (n % 600) / 600.0
    col = ramp(t, STOPS)
    bright = 0.35 + 0.65 * (1 - r / r.max())[:, None]
    col = col * bright

    acc = np.zeros((H, W, 3), float)
    # soft disc stamp (gaussian falloff)
    k = DOT
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    stamp = np.exp(-(xx**2 + yy**2) / (2 * (k / 2.1) ** 2))

    for i in range(N):
        x0 = int(round(cx[i])); y0 = int(round(cy[i]))
        xa, xb = x0 - k, x0 + k + 1
        ya, yb = y0 - k, y0 + k + 1
        if xa < 0 or ya < 0 or xb > W or yb > H:
            continue
        acc[ya:yb, xa:xb] += stamp[..., None] * col[i]

    img = 1 - np.exp(-acc * 1.3)             # tone-map
    bg = np.array([0.02, 0.02, 0.05])
    lum = img.sum(2, keepdims=True)
    img = np.where(lum < 0.015, bg, img)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    write_png("phyllotaxis.png", out)
    print("wrote phyllotaxis.png")


if __name__ == "__main__":
    main()
