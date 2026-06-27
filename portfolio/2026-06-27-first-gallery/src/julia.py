#!/usr/bin/env python3
"""Julia set for f(z) = z^2 + c, with smooth (continuous) escape colouring
and a touch of supersampling. Pure numpy + the stdlib PNG writer.
"""
import numpy as np
from pnglib import write_png, ramp

W = H = 1400
SS = 2                      # supersample factor (renders at SS*W then downsamples)
C = complex(-0.8, 0.156)    # a classic dendrite-y Julia constant
MAXIT = 400
ZOOM = 1.45                 # half-height of the view in complex units

# deep teal -> aqua -> cream -> amber -> near-black (interior)
STOPS = [
    [0.01, 0.03, 0.08],
    [0.04, 0.30, 0.38],
    [0.20, 0.65, 0.62],
    [0.86, 0.93, 0.80],
    [0.95, 0.62, 0.20],
    [0.18, 0.06, 0.10],
]


def render(w, h):
    ar = w / h
    xs = np.linspace(-ZOOM * ar, ZOOM * ar, w)
    ys = np.linspace(-ZOOM, ZOOM, h)
    zx, zy = np.meshgrid(xs, ys)
    z = zx + 1j * zy
    nu = np.zeros(z.shape, float)      # smooth escape value
    alive = np.ones(z.shape, bool)
    for i in range(MAXIT):
        z[alive] = z[alive] * z[alive] + C
        mag = np.abs(z)
        escaped = alive & (mag > 2.0)
        # smooth iteration count: i + 1 - log(log|z|)/log2
        nu[escaped] = i + 1 - np.log(np.log(mag[escaped])) / np.log(2)
        alive &= ~escaped
        if not alive.any():
            break
    nu[alive] = MAXIT                  # interior
    t = nu / nu.max()
    t = np.power(t, 0.55)              # pull detail out of the low end
    rgb = ramp(t, STOPS)
    rgb[nu >= MAXIT] = STOPS[-1]       # solid interior colour
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def downsample(img, k):
    h, w = img.shape[:2]
    return (img.reshape(h // k, k, w // k, k, 3)
               .mean(axis=(1, 3)).astype(np.uint8))


if __name__ == "__main__":
    print(f"rendering Julia c={C} at {W*SS}x{H*SS}, {MAXIT} iters, {SS}x SSAA")
    big = render(W * SS, H * SS)
    img = downsample(big, SS) if SS > 1 else big
    write_png("julia.png", img)
    print("wrote julia.png")
