#!/usr/bin/env python3
"""A Mandelbrot zoom into the 'seahorse valley' on the neck of the set, with
smooth (fractional) escape colouring and a cyclic palette so the bands flow.
numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W = H = 1400
SS = 2
CX, CY = -0.745, 0.113          # seahorse valley
HALF = 0.022                    # half-height of the view (the zoom level)
MAXIT = 900


def render(w, h):
    ar = w / h
    re = np.linspace(CX - HALF * ar, CX + HALF * ar, w)
    im = np.linspace(CY - HALF, CY + HALF, h)
    c = re[None, :] + 1j * im[:, None]
    z = np.zeros_like(c)
    nu = np.zeros(c.shape)
    alive = np.ones(c.shape, bool)
    for i in range(MAXIT):
        z[alive] = z[alive] * z[alive] + c[alive]
        mag = np.abs(z)
        esc = alive & (mag > 256)
        nu[esc] = i + 1 - np.log(np.log(mag[esc])) / np.log(2)
        alive &= ~esc
        if not alive.any():
            break

    # cyclic palette: map smooth iteration through a sine ramp per channel
    t = np.sqrt(nu / nu.max()) * 7.0        # sqrt spreads the inner bands
    r = 0.5 + 0.5 * np.sin(t + 0.0)
    g = 0.5 + 0.5 * np.sin(t + 2.1)
    b = 0.5 + 0.5 * np.sin(t + 4.2)
    rgb = np.stack([r, g, b], -1)
    rgb[~np.isfinite(nu) | (nu == 0)] = [0.02, 0.02, 0.05]   # interior
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def downsample(img, k):
    h, w = img.shape[:2]
    return img.reshape(h // k, k, w // k, k, 3).mean(axis=(1, 3)).astype(np.uint8)


if __name__ == "__main__":
    print(f"rendering Mandelbrot @ ({CX},{CY}) half={HALF}, {MAXIT} it, {SS}x SSAA...")
    big = render(W * SS, H * SS)
    img = downsample(big, SS) if SS > 1 else big
    write_png("mandelbrot.png", img)
    print("wrote mandelbrot.png")
