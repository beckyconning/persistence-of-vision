#!/usr/bin/env python3
"""Growth piece #6 — SUBJECT: the FIGURE (never attempted). An abstracted reclining
figure (Henry Moore / Brancusi register) built from Lambert-shaded ELLIPSOID volumes
on a plinth, with a real soft cast shadow. Reuses + generalises the still-life
renderer (sphere→ellipsoid). Earthy bronze palette. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1500, 1000
GROUND = int(H * 0.66)
L = np.array([-0.55, -0.65, 0.52]); L = L / np.linalg.norm(L)
RNG = np.random.default_rng(8)
Y, X = np.mgrid[0:H, 0:W].astype(float)


def box_blur(a, k):
    for ax in (0, 1):
        c = np.cumsum(a, axis=ax)
        if ax == 0:
            c = np.vstack([np.zeros((1, a.shape[1])), c]); a = (c[k:] - c[:-k]) / k
            a = np.vstack([a, np.repeat(a[-1:], H - a.shape[0], 0)])
        else:
            c = np.hstack([np.zeros((a.shape[0], 1)), c]); a = (c[:, k:] - c[:, :-k]) / k
            a = np.hstack([a, np.repeat(a[:, -1:], W - a.shape[1], 1)])
    return a


# reclining figure as overlapping ellipsoids: (cx, cy, a, b, tilt)
# a Moore-esque body: head, neck, chest, belly, hip, thigh, calf — left→right
BRONZE = np.array([0.52, 0.40, 0.27])
PARTS = [
    (430, GROUND - 150, 78, 92, 0.2),    # head
    (545, GROUND - 95, 70, 60, 0.0),     # shoulder/neck mass
    (700, GROUND - 110, 165, 120, 0.05), # chest
    (905, GROUND - 70, 150, 110, -0.05), # belly/hip
    (1080, GROUND - 110, 120, 95, 0.5),  # raised knee
    (1180, GROUND - 35, 175, 70, 0.1),   # lower leg
]


def ellipsoid_normal(cx, cy, a, b, tilt):
    ct, st = np.cos(tilt), np.sin(tilt)
    xr = (X - cx) * ct + (Y - cy) * st
    yr = -(X - cx) * st + (Y - cy) * ct
    u, v = xr / a, yr / b
    d2 = u * u + v * v
    m = d2 <= 1.0
    nz = np.sqrt(np.clip(1 - d2, 0, 1))
    # surface normal (approx): gradient of implicit, rotated back to screen
    nx = u / a; ny = v / b
    nl = nx * ct - ny * st, nx * st + ny * ct
    return m, nl[0], nl[1], nz


def main():
    img = np.zeros((H, W, 3))
    # backdrop: warm studio gradient; plinth band
    top = np.array([0.86, 0.82, 0.75]); bot = np.array([0.74, 0.69, 0.60])
    g = np.clip(Y / H, 0, 1)
    img[:] = (top[None, None, :] + (bot - top)[None, None, :] * g[..., None])
    plinth = np.array([0.80, 0.75, 0.66])
    img = np.where((Y >= GROUND)[..., None], plinth[None, None, :] * (0.9 + 0.1 * g[..., None]), img)

    # cast shadow: union of parts' silhouettes projected along L onto the plinth, blurred
    shadow = np.zeros((H, W))
    for (cx, cy, a, b, tilt) in PARTS:
        ox = -L[0] / L[2] * 80; sy = GROUND + 30
        ell = ((X - (cx + ox)) / (a * 1.1)) ** 2 + ((Y - sy) / 55) ** 2
        shadow += np.clip(1 - ell, 0, 1)
    shadow = box_blur(np.clip(shadow, 0, 1) * (Y >= GROUND), 51)
    img = img * (1 - 0.34 * shadow[..., None])

    # the figure — shade each volume; later (front) parts overwrite, building one mass
    for (cx, cy, a, b, tilt) in PARTS:
        m, nx, ny, nz = ellipsoid_normal(cx, cy, a, b, tilt)
        ndl = np.clip(nx * L[0] + (-ny) * L[1] + nz * L[2], 0, 1)
        shade = 0.20 + 0.92 * ndl
        refz = 2 * ndl * nz - L[2]
        spec = (np.clip(refz, 0, 1) ** 30) * (ndl > 0)
        body = BRONZE[None, None, :] * shade[..., None] + np.array([1, 0.96, 0.9])[None, None, :] * (0.35 * spec)[..., None]
        img = np.where(m[..., None], np.clip(body, 0, 1), img)

    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.015
    write_png("figure.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote figure.png")


if __name__ == "__main__":
    main()
