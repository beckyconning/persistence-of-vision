#!/usr/bin/env python3
"""Domain-warped fBm (after Inigo Quilez): evaluate noise at coordinates that
have themselves been displaced by noise, twice over. The recursive warping
turns smooth noise into marbled, smoke-like filaments. Colour is mixed from the
intermediate warp fields so structure and hue move together. numpy + stdlib PNG.

    q = fbm(p)
    r = fbm(p + 4q + c1)
    f = fbm(p + 4r + c2)
"""
import numpy as np
from pnglib import write_png, ramp

W = H = 1500
LAT = 256                       # periodic value-noise lattice size
OCTAVES = 6
RNG = np.random.default_rng(20260627)
LATTICE = RNG.random((LAT, LAT))


def smoothstep(t):
    return t * t * (3 - 2 * t)


def noise(x, y):
    """Bilinear value noise sampled at arbitrary float coords (periodic)."""
    xi = np.floor(x).astype(np.intp); yi = np.floor(y).astype(np.intp)
    fx = smoothstep(x - xi); fy = smoothstep(y - yi)
    x0 = xi % LAT; x1 = (xi + 1) % LAT
    y0 = yi % LAT; y1 = (yi + 1) % LAT
    a = LATTICE[y0, x0]; b = LATTICE[y0, x1]
    c = LATTICE[y1, x0]; d = LATTICE[y1, x1]
    return (a * (1 - fx) + b * fx) * (1 - fy) + (c * (1 - fx) + d * fx) * fy


def fbm(x, y):
    val = np.zeros_like(x); amp = 0.5; freq = 1.0; norm = 0.0
    for o in range(OCTAVES):
        # offset each octave so they don't share lattice alignment
        val += amp * noise(x * freq + o * 37.2, y * freq + o * 17.9)
        norm += amp; amp *= 0.5; freq *= 2.0
    return val / norm


# deep space -> indigo -> magenta nebula -> cyan rim -> warm star-glow
STOPS = [
    [0.02, 0.02, 0.07],
    [0.12, 0.06, 0.34],
    [0.55, 0.12, 0.52],
    [0.95, 0.40, 0.55],
    [0.45, 0.85, 0.92],
    [1.00, 0.96, 0.86],
]


def main():
    lin = np.linspace(0, 6, W)
    X, Y = np.meshgrid(lin, np.linspace(0, 6, H))

    print("warping pass 1...")
    qx = fbm(X, Y)
    qy = fbm(X + 5.2, Y + 1.3)
    print("warping pass 2...")
    rx = fbm(X + 4 * qx + 1.7, Y + 4 * qy + 9.2)
    ry = fbm(X + 4 * qx + 8.3, Y + 4 * qy + 2.8)
    print("final field...")
    f = fbm(X + 4 * rx, Y + 4 * ry)

    # colour: base ramp on f, brightened where the warp fields pile up
    t = np.clip(f * 1.1, 0, 1)
    rgb = ramp(t, STOPS)
    glow = np.clip((rx * ry) * 1.6, 0, 1)[..., None]
    rgb = rgb + glow * np.array([0.25, 0.18, 0.30])
    rgb *= (0.55 + 0.55 * qx)[..., None]          # large-scale luminance drift
    out = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    write_png("domainwarp.png", out)
    print("wrote domainwarp.png")


if __name__ == "__main__":
    main()
