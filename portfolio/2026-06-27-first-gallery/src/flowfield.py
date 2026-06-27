#!/usr/bin/env python3
"""Flow field: 30k particles drift along an fBm noise field, depositing ink.
fBm value-noise is built from scratch (random lattices, smoothstep-interpolated,
summed over octaves). Colour shifts along each particle's life. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W = H = 1500
PARTICLES = 30_000
STEPS = 320
STEP_LEN = 1.15
TURNS = 2.6                 # how many full turns the noise maps to
RNG = np.random.default_rng(7)


def smoothstep(t):
    return t * t * (3 - 2 * t)


def value_noise(w, h, cells):
    """Smooth value noise in [0,1], (h,w), from a (cells+1)^2 random lattice."""
    lat = RNG.random((cells + 1, cells + 1))
    gx = np.linspace(0, cells, w)
    gy = np.linspace(0, cells, h)
    x0 = np.floor(gx).astype(int); fx = smoothstep(gx - x0)
    y0 = np.floor(gy).astype(int); fy = smoothstep(gy - y0)
    x1 = np.minimum(x0 + 1, cells); y1 = np.minimum(y0 + 1, cells)
    # gather corners (h,w)
    a = lat[np.ix_(y0, x0)]; b = lat[np.ix_(y0, x1)]
    c = lat[np.ix_(y1, x0)]; d = lat[np.ix_(y1, x1)]
    top = a + (b - a) * fx[None, :]
    bot = c + (d - c) * fx[None, :]
    return top + (bot - top) * fy[:, None]


def fbm(w, h, octaves=5):
    out = np.zeros((h, w)); amp = 0.5; freq = 3; norm = 0
    for _ in range(octaves):
        out += amp * value_noise(w, h, freq)
        norm += amp; amp *= 0.5; freq *= 2
    return out / norm


# warm-to-cool dusk palette, indexed by particle age
PAL = np.array([
    [0.99, 0.78, 0.35],
    [0.95, 0.42, 0.33],
    [0.72, 0.20, 0.45],
    [0.30, 0.18, 0.55],
    [0.12, 0.32, 0.62],
    [0.45, 0.82, 0.85],
])


def age_color(frac):
    seg = frac * (len(PAL) - 1)
    i = np.clip(seg.astype(int), 0, len(PAL) - 2)
    f = (seg - i)[:, None]
    return PAL[i] + (PAL[i + 1] - PAL[i]) * f


def main():
    print("building fBm field...")
    field = fbm(W, H, octaves=6)
    angle = field * (2 * np.pi * TURNS)

    px = RNG.uniform(0, W, PARTICLES)
    py = RNG.uniform(0, H, PARTICLES)
    acc = np.zeros((H, W, 3), float)

    print(f"advecting {PARTICLES:,} particles x {STEPS} steps...")
    for s in range(STEPS):
        ix = np.clip(px.astype(int), 0, W - 1)
        iy = np.clip(py.astype(int), 0, H - 1)
        col = age_color(np.full(PARTICLES, s / STEPS))
        np.add.at(acc, (iy, ix, slice(None)), col * 0.5)
        a = angle[iy, ix]
        px += np.cos(a) * STEP_LEN
        py += np.sin(a) * STEP_LEN
        # wrap so the canvas stays full
        px %= W; py %= H

    # tone-map the additive buffer
    img = 1 - np.exp(-acc * 0.65)          # filmic-ish saturation
    img = np.power(img, 0.85)
    bg = np.array([0.03, 0.02, 0.06])
    lum = img.sum(2, keepdims=True)
    img = np.where(lum < 0.02, bg, img)
    out = (np.clip(img, 0, 1) * 255).astype(np.uint8)
    write_png("flowfield.png", out)
    print("wrote flowfield.png")


if __name__ == "__main__":
    main()
