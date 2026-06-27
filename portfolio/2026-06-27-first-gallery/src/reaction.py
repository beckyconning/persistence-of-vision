#!/usr/bin/env python3
"""Gray-Scott reaction-diffusion. Two chemicals U and V diffuse and react on a
toroidal grid; from a localized seed they self-organize into a coral / mitosis
texture. 9-point Laplacian via np.roll. numpy + stdlib PNG.

    U' = Du*Lap(U) - U*V^2 + F*(1-U)
    V' = Dv*Lap(V) + U*V^2 - (F+K)*V

LESSON (banked): the NORMALIZED laplacian below (center -1, weights average ~1)
must be paired with Du,Dv = 1.0,0.5 — NOT the raw-finite-difference 0.16,0.08.
Mixing conventions makes diffusion ~6x too weak and every pattern freezes.
"""
import numpy as np
from pnglib import write_png, ramp

N = 340                 # simulation grid (square)
STEPS = 12000
Du, Dv = 1.0, 0.5       # matched to the NORMALIZED laplacian below
F, K = 0.0367, 0.0649   # "mitosis": spots divide and fill the space
SCALE = 5               # upsample factor for the output image
RNG = np.random.default_rng(20260627)

# abyssal blue -> teal -> jade -> bone -> rose-gold
STOPS = [
    [0.03, 0.05, 0.13],
    [0.06, 0.28, 0.40],
    [0.13, 0.55, 0.50],
    [0.62, 0.80, 0.66],
    [0.96, 0.90, 0.78],
    [0.93, 0.55, 0.45],
]


def laplacian(Z):
    return (
        -Z
        + 0.20 * (np.roll(Z, 1, 0) + np.roll(Z, -1, 0)
                  + np.roll(Z, 1, 1) + np.roll(Z, -1, 1))
        + 0.05 * (np.roll(np.roll(Z, 1, 0), 1, 1) + np.roll(np.roll(Z, 1, 0), -1, 1)
                  + np.roll(np.roll(Z, -1, 0), 1, 1) + np.roll(np.roll(Z, -1, 0), -1, 1))
    )


def main():
    # trivial state everywhere, then a noisy central seed; mitosis fills outward.
    U = np.ones((N, N)); V = np.zeros((N, N))
    c = N // 2; r = 14
    U[c - r:c + r, c - r:c + r] = 0.50
    V[c - r:c + r, c - r:c + r] = 0.25
    V[c - r:c + r, c - r:c + r] += 0.05 * RNG.random((2 * r, 2 * r))

    print(f"simulating Gray-Scott on {N}x{N} for {STEPS} steps (F={F}, K={K})...")
    for s in range(STEPS):
        uvv = U * V * V
        U += Du * laplacian(U) - uvv + F * (1 - U)
        V += Dv * laplacian(V) + uvv - (F + K) * V
        if s % 3000 == 0:
            print(f"  step {s}: V range [{V.min():.3f}, {V.max():.3f}]")

    t = (V - V.min()) / (np.ptp(V) + 1e-9)   # numpy 2.0: np.ptp, not V.ptp()
    t = np.power(t, 0.85)
    rgb = ramp(t, STOPS)
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    img = np.repeat(np.repeat(img, SCALE, 0), SCALE, 1)   # nearest upsample
    write_png("reaction.png", img)
    print(f"wrote reaction.png ({img.shape[1]}x{img.shape[0]})")


if __name__ == "__main__":
    main()
