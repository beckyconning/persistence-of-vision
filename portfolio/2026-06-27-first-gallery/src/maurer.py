#!/usr/bin/env python3
"""A Maurer rose: take a rose curve r = sin(n*theta) and visit 361 points at
fixed angular steps of d degrees, joining consecutive points with STRAIGHT
lines. The lines chord across the petals and weave a lacework. The smooth rose
is drawn faintly beneath. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W = H = 1500
N = 6           # petal parameter
D = 71          # degree step
RADIUS = 0.92 * W / 2


def deposit(acc, xs, ys, col, weight):
    ix = xs.astype(np.intp); iy = ys.astype(np.intp)
    m = (ix >= 0) & (ix < W) & (iy >= 0) & (iy < H)
    np.add.at(acc, (iy[m], ix[m], slice(None)), col[m] * weight)


def main():
    acc = np.zeros((H, W, 3))

    # faint continuous rose underneath
    th = np.linspace(0, 2 * np.pi, 4000)
    r = np.sin(N * th)
    rx = W / 2 + RADIUS * r * np.cos(th)
    ry = H / 2 + RADIUS * r * np.sin(th)
    deposit(acc, rx, ry, np.tile([0.20, 0.30, 0.55], (rx.size, 1)), 1.1)

    # the Maurer walk: 361 vertices joined by straight chords
    i = np.arange(361)
    a = np.deg2rad(i * D)
    rr = np.sin(N * a)
    vx = W / 2 + RADIUS * rr * np.cos(a)
    vy = H / 2 + RADIUS * rr * np.sin(a)

    SAMP = 260
    t = np.linspace(0, 1, SAMP)[None, :]
    # segment endpoints
    x0 = vx[:-1, None]; x1 = vx[1:, None]
    y0 = vy[:-1, None]; y1 = vy[1:, None]
    sx = (x0 + (x1 - x0) * t).ravel()
    sy = (y0 + (y1 - y0) * t).ravel()
    # colour by position along the whole walk
    frac = (np.arange(360)[:, None] + t) / 360.0
    hue = frac.ravel()
    col = np.stack([0.5 + 0.5 * np.sin(2 * np.pi * hue + 0.0),
                    0.5 + 0.5 * np.sin(2 * np.pi * hue + 2.1),
                    0.5 + 0.5 * np.sin(2 * np.pi * hue + 4.2)], -1)
    deposit(acc, sx, sy, col, 0.55)

    img = 1 - np.exp(-acc * 3.2)
    img = np.power(img, 0.9)
    bg = np.array([0.02, 0.02, 0.05])
    lum = img.sum(2, keepdims=True)
    img = np.where(lum < 0.012, bg, img)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    write_png("maurer.png", out)
    print("wrote maurer.png")


if __name__ == "__main__":
    main()
