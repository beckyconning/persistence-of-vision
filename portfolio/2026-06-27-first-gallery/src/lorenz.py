#!/usr/bin/env python3
"""The Lorenz attractor - the original butterfly of chaos theory (1963).
A 3-variable ODE for atmospheric convection whose trajectory never repeats yet
stays bound to a two-lobed wing. We integrate 9000 trajectories in parallel
(RK4), project onto the x-z plane, and accumulate a density glow.

    x' = s(y - x)   y' = x(r - z) - y   z' = xy - b z      (s=10, r=28, b=8/3)
"""
import numpy as np
from pnglib import write_png, ramp

W = H = 1500
TRAJ = 9000
STEPS = 900
BURN = 80
DT = 0.0045
S, R, B = 10.0, 28.0, 8.0 / 3.0
RNG = np.random.default_rng(20260627)

# black -> violet -> magenta -> amber -> white-hot
STOPS = [
    [0.02, 0.01, 0.06],
    [0.28, 0.07, 0.42],
    [0.80, 0.16, 0.50],
    [0.99, 0.62, 0.28],
    [1.00, 0.98, 0.90],
]


def deriv(x, y, z):
    return S * (y - x), x * (R - z) - y, x * y - B * z


def step_rk4(x, y, z):
    k1 = deriv(x, y, z)
    k2 = deriv(x + 0.5 * DT * k1[0], y + 0.5 * DT * k1[1], z + 0.5 * DT * k1[2])
    k3 = deriv(x + 0.5 * DT * k2[0], y + 0.5 * DT * k2[1], z + 0.5 * DT * k2[2])
    k4 = deriv(x + DT * k3[0], y + DT * k3[1], z + DT * k3[2])
    x += DT / 6 * (k1[0] + 2 * k2[0] + 2 * k3[0] + k4[0])
    y += DT / 6 * (k1[1] + 2 * k2[1] + 2 * k3[1] + k4[1])
    z += DT / 6 * (k1[2] + 2 * k2[2] + 2 * k3[2] + k4[2])
    return x, y, z


def main():
    x = RNG.uniform(-15, 15, TRAJ)
    y = RNG.uniform(-20, 20, TRAJ)
    z = RNG.uniform(5, 40, TRAJ)

    grid = np.zeros((H, W))
    # view bounds for the x-z projection
    xmin, xmax = -23, 23
    zmin, zmax = -2, 50
    sx = (W - 1) / (xmax - xmin)
    sz = (H - 1) / (zmax - zmin)

    print(f"integrating {TRAJ:,} Lorenz trajectories x {STEPS} steps (RK4)...")
    for s in range(STEPS):
        x, y, z = step_rk4(x, y, z)
        if s < BURN:
            continue
        px = ((x - xmin) * sx).astype(np.intp)
        pz = ((zmax - z) * sz).astype(np.intp)          # flip z for image coords
        m = (px >= 0) & (px < W) & (pz >= 0) & (pz < H)
        np.add.at(grid, (pz[m], px[m]), 1.0)

    dens = np.log1p(grid)
    dens /= dens.max()
    dens = np.power(dens, 0.72)
    rgb = ramp(dens, STOPS)
    rgb[grid == 0] = STOPS[0]
    out = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    write_png("lorenz.png", out)
    lit = int((grid > 0).sum())
    print(f"lit {lit:,} px; peak {int(grid.max())}; wrote lorenz.png")


if __name__ == "__main__":
    main()
