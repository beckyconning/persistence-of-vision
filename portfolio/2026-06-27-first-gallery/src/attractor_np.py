#!/usr/bin/env python3
"""De Jong attractor, vectorized. 200k walkers evolved in lockstep all fall
onto the same strange attractor, so we trace 80M points in a few array ops.
Density -> log -> gamma -> a 5-stop colour ramp. PNG via stdlib zlib/struct.

    x' = sin(a*y) - cos(b*x)
    y' = sin(c*x) - cos(d*y)
"""
import struct, zlib
import numpy as np

W = H = 1600
A, B, C, D = -2.24, 0.99, -2.86, -2.31
WALKERS = 200_000
STEPS = 400          # WALKERS*STEPS = 80,000,000 points
BURN = 20            # discard transient before binning
SPAN = 2.3

# midnight -> indigo -> magenta -> coral -> gold
STOPS = np.array([
    [0.02, 0.01, 0.09],
    [0.20, 0.05, 0.42],
    [0.66, 0.10, 0.55],
    [0.97, 0.38, 0.42],
    [1.00, 0.86, 0.52],
])


def build_density():
    rng = np.random.default_rng(20260627)
    x = rng.uniform(-2, 2, WALKERS)
    y = rng.uniform(-2, 2, WALKERS)
    grid = np.zeros((H, W), dtype=np.float64)
    scale = (W - 1) / (2 * SPAN)
    for step in range(STEPS):
        x, y = np.sin(A * y) - np.cos(B * x), np.sin(C * x) - np.cos(D * y)
        if step < BURN:
            continue
        px = ((x + SPAN) * scale).astype(np.intp)
        py = ((y + SPAN) * scale).astype(np.intp)
        m = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        # accumulate hits; np.add.at handles repeated indices correctly
        np.add.at(grid, (py[m], px[m]), 1.0)
    return grid


def colorize(grid):
    dens = np.log1p(grid)
    dens /= dens.max()
    dens = np.power(dens, 0.78)              # gamma: lift the faint filaments
    t = dens * (len(STOPS) - 1)
    i = np.clip(t.astype(np.intp), 0, len(STOPS) - 2)
    f = (t - i)[..., None]
    lo = STOPS[i]
    hi = STOPS[i + 1]
    rgb = lo + (hi - lo) * f                 # (H,W,3) in [0,1]
    rgb[grid == 0] = STOPS[0]                # clean background
    return (np.clip(rgb, 0, 1) * 255).astype(np.uint8)


def write_png(path, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    filtered = np.hstack([np.zeros((H, 1), np.uint8),
                          rgb.reshape(H, W * 3)]).tobytes()
    png = (b"\x89PNG\r\n\x1a\n"
           + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(filtered, 9))
           + chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    print(f"tracing {WALKERS:,} walkers x {STEPS} steps = {WALKERS*STEPS:,} points")
    g = build_density()
    lit = int((g > 0).sum())
    print(f"lit {lit:,}/{W*H:,} px ({100*lit/(W*H):.1f}%); peak {int(g.max())}")
    write_png("dejong_hi.png", colorize(g))
    print("wrote dejong_hi.png")
