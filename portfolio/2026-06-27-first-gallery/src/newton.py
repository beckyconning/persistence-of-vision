#!/usr/bin/env python3
"""Newton fractal for p(z) = z^5 - 1. Every starting point is iterated by
Newton's method until it lands on one of the five roots; colour = which root
it fell into, brightness = how fast it got there. The basin boundaries are a
fractal where all five colours meet arbitrarily close together. numpy + stdlib.
"""
import numpy as np
from pnglib import write_png

W = H = 1400
SS = 2
MAXIT = 60
TOL = 1e-6
SPAN = 1.6

roots = np.exp(2j * np.pi * np.arange(5) / 5)        # fifth roots of unity
# one hue per root (root index -> base colour)
ROOTCOL = np.array([
    [0.95, 0.35, 0.45],   # rose
    [0.98, 0.72, 0.30],   # amber
    [0.40, 0.80, 0.55],   # jade
    [0.30, 0.55, 0.92],   # azure
    [0.70, 0.45, 0.92],   # violet
])


def render(w, h):
    ar = w / h
    re = np.linspace(-SPAN * ar, SPAN * ar, w)
    im = np.linspace(-SPAN, SPAN, h)
    z = re[None, :] + 1j * im[:, None]
    it = np.zeros(z.shape, np.int32)
    active = np.ones(z.shape, bool)
    for i in range(MAXIT):
        z4 = z * z * z * z
        z[active] = z[active] - (z[active] * z4[active] - 1) / (5 * z4[active])
        # converged where close to any root
        done = np.zeros(z.shape, bool)
        for r in roots:
            done |= np.abs(z - r) < TOL
        newly = active & done
        it[newly] = i
        active &= ~newly
        if not active.any():
            break

    # nearest root index for each pixel
    dist = np.abs(z[..., None] - roots[None, None, :])
    which = dist.argmin(axis=2)
    base = ROOTCOL[which]
    # shade by iteration speed: fast convergence bright, slow -> dark (the boundaries)
    shade = (1 - it / MAXIT)[..., None]
    shade = np.power(np.clip(shade, 0, 1), 0.7) * 0.85 + 0.15
    rgb = base * shade
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def downsample(img, k):
    h, w = img.shape[:2]
    return img.reshape(h // k, k, w // k, k, 3).mean(axis=(1, 3)).astype(np.uint8)


if __name__ == "__main__":
    print(f"rendering Newton z^5-1 at {W*SS}x{H*SS}, {SS}x SSAA...")
    big = render(W * SS, H * SS)
    img = downsample(big, SS) if SS > 1 else big
    write_png("newton.png", img)
    print("wrote newton.png")
