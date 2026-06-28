#!/usr/bin/env python3
"""Reward / growth piece — a REPRESENTATIONAL landscape.

Deliberately leaving session 1's corner (neon density-glow on black, abstract,
centered): this depicts a *thing* (receding hills to a horizon under a low sun),
with EARTH/PAPER colour, ATMOSPHERIC perspective + REAL slope-shaded light (not
additive glow), and large NEGATIVE-SPACE sky. numpy + the hand-rolled PNG writer.
"""
import numpy as np
from pnglib import write_png

W, H = 1600, 1100
RNG = np.random.default_rng(11)
HORIZON = int(H * 0.62)            # low-ish horizon → sky as negative space (upper 62%)
SUN_X, SUN_Y = int(W * 0.72), int(H * 0.30)   # off-centre sun (rule of thirds)


def lerp(a, b, t):
    return a + (b - a) * t


def smooth_profile(width, octaves, seed, rough=0.5):
    """A 1-D ridge height in [0,1] from summed value-noise octaves (a hill skyline)."""
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, width)
    out = np.zeros(width); amp = 1.0; freq = 2.0; norm = 0.0
    for _ in range(octaves):
        n = rng.random(int(freq) + 2)
        xi = x * (len(n) - 1)
        i0 = np.floor(xi).astype(int); f = xi - i0
        f = f * f * (3 - 2 * f)
        out += amp * (n[i0] * (1 - f) + n[np.minimum(i0 + 1, len(n) - 1)] * f)
        norm += amp; amp *= rough; freq *= 2.2
    return out / norm


def main():
    img = np.zeros((H, W, 3))
    yy = np.arange(H)[:, None]

    # --- SKY: warm paper gradient, cream high → pale ochre at the horizon (negative space) ---
    sky_top = np.array([0.93, 0.90, 0.82])      # warm paper / bone
    sky_horizon = np.array([0.97, 0.88, 0.72])  # pale ochre haze
    t = np.clip(yy / HORIZON, 0, 1)[:, :, None] if False else np.clip((np.arange(H) / HORIZON), 0, 1)
    sky = sky_top[None, :] + (sky_horizon - sky_top)[None, :] * t[:, None]   # (H,3)
    img[:] = sky[:, None, :]

    # soft, NON-additive sun: gently lighten the sky toward warm near the sun (multiplicative blend)
    Y, X = np.mgrid[0:H, 0:W]
    d = np.sqrt(((X - SUN_X) / W) ** 2 + ((Y - SUN_Y) / H) ** 2)
    glow = np.clip(1 - d / 0.55, 0, 1) ** 2.2
    sun_col = np.array([1.0, 0.95, 0.82])
    img = img * (1 - glow[..., None]) + sun_col[None, None, :] * glow[..., None]
    # the sun disc itself (soft warm, not neon)
    disc = (np.clip(1 - np.sqrt((X - SUN_X) ** 2 + (Y - SUN_Y) ** 2) / 46, 0, 1)) ** 0.6
    img = img * (1 - disc[..., None]) + np.array([1.0, 0.97, 0.88])[None, None, :] * disc[..., None]

    # --- HILL LAYERS: far → near, atmospheric perspective + slope shading ---
    # earth palette, each layer earthier/darker/more saturated as it nears the viewer
    layers = [
        # (base_top_frac, amplitude_frac, colour,            seed, octaves)
        (0.50, 0.06, np.array([0.62, 0.64, 0.60]), 31, 3),   # distant ridge — hazed sage-grey
        (0.58, 0.10, np.array([0.55, 0.58, 0.45]), 47, 4),   # olive
        (0.68, 0.14, np.array([0.45, 0.46, 0.32]), 59, 4),   # darker olive
        (0.80, 0.20, np.array([0.36, 0.32, 0.22]), 71, 5),   # umber foreground
    ]
    sun_dir = np.array([SUN_X / W - 0.5, -0.25])             # light comes from the sun
    for li, (top, ampf, col, seed, oct_) in enumerate(layers):
        prof = smooth_profile(W, oct_, seed)
        ridge = (top - ampf * prof) * H                      # y of the ridge per column
        # slope shading: dridge/dx → faces; lit where slope opposes the sun's x-direction
        slope = np.gradient(ridge)
        shade = np.clip(0.5 - np.sign(sun_dir[0]) * slope / (ampf * H) * 0.9, 0.15, 1.0)
        # atmospheric haze: far layers blend toward the horizon sky colour
        haze = 1.0 - li / (len(layers) - 0.2)
        below = Y >= ridge[None, :]
        # build per-column colour (H via broadcast): start from layer colour shaded, then haze
        colcol = (col[None, :] * (0.62 + 0.55 * shade[:, None]))            # (W,3)
        colcol = colcol * (1 - 0.55 * haze) + sky_horizon[None, :] * (0.55 * haze)
        layer_rgb = np.broadcast_to(colcol[None, :, :], (H, W, 3))
        img = np.where(below[..., None], layer_rgb, img)

    # --- earthy paper grain (subtle, kills the digital flatness) ---
    grain = (RNG.random((H, W)) - 0.5) * 0.03
    img = img + grain[..., None]

    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    write_png("landscape.png", out)
    print("wrote landscape.png")


if __name__ == "__main__":
    main()
