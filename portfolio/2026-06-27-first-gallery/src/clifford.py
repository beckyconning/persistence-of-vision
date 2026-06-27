#!/usr/bin/env python3
"""Clifford attractor - 120k walkers in lockstep onto the same bounded orbit,
~60M points, density -> log -> gamma -> ember palette. numpy + stdlib PNG.

    x' = sin(a*y) + c*cos(a*x)
    y' = sin(b*x) + d*cos(b*y)
"""
import numpy as np
from pnglib import write_png, ramp

W = H = 1500
A, B, C, D = -1.7, 1.8, -1.9, -0.4
WALKERS, STEPS, BURN = 120_000, 520, 20
SPAN = 3.2

STOPS = [[0.02, 0.01, 0.05], [0.18, 0.03, 0.22], [0.55, 0.10, 0.32],
         [0.92, 0.34, 0.20], [0.99, 0.72, 0.34], [1.0, 0.97, 0.85]]


def main():
    rng = np.random.default_rng(20260627)
    x = rng.uniform(-1, 1, WALKERS); y = rng.uniform(-1, 1, WALKERS)
    grid = np.zeros((H, W)); scale = (W - 1) / (2 * SPAN)
    print(f"tracing {WALKERS*STEPS:,} Clifford points...")
    for s in range(STEPS):
        x, y = (np.sin(A * y) + C * np.cos(A * x),
                np.sin(B * x) + D * np.cos(B * y))
        if s < BURN:
            continue
        px = ((x + SPAN) * scale).astype(np.intp)
        py = ((y + SPAN) * scale).astype(np.intp)
        m = (px >= 0) & (px < W) & (py >= 0) & (py < H)
        np.add.at(grid, (py[m], px[m]), 1.0)
    dens = np.log1p(grid); dens /= dens.max(); dens = np.power(dens, 0.7)
    rgb = ramp(dens, STOPS); rgb[grid == 0] = STOPS[0]
    out = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    write_png("clifford.png", out)
    print(f"lit {int((grid>0).sum()):,} px; peak {int(grid.max())}; wrote clifford.png")


if __name__ == "__main__":
    main()
