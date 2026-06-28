#!/usr/bin/env python3
"""Growth piece #5 — LIGHT axis from painted to COMPUTED. A small still life:
earthy spheres on a paper table, Lambert-shaded by a single light with a soft
specular highlight, and REAL soft cast shadows (each sphere's silhouette projected
onto the ground along the light direction, then blurred). First simulated (not
painted) light + shadow. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1400, 1000
GROUND = int(H * 0.46)                       # table horizon
L = np.array([-0.5, -0.7, 0.5]); L = L / np.linalg.norm(L)   # light: upper-left, toward viewer


def box_blur(a, k):
    """Cheap separable box blur via cumulative sums (for soft shadows)."""
    for ax in (0, 1):
        c = np.cumsum(a, axis=ax)
        if ax == 0:
            c = np.vstack([np.zeros((1, a.shape[1])), c])
            a = (c[k:] - c[:-k]) / k if k < a.shape[0] else a
            a = np.vstack([a, np.repeat(a[-1:], H - a.shape[0], 0)]) if a.shape[0] < H else a
        else:
            c = np.hstack([np.zeros((a.shape[0], 1)), c])
            a = (c[:, k:] - c[:, :-k]) / k if k < a.shape[1] else a
            a = np.hstack([a, np.repeat(a[:, -1:], W - a.shape[1], 1)]) if a.shape[1] < W else a
    return a


def main():
    Y, X = np.mgrid[0:H, 0:W].astype(float)
    img = np.zeros((H, W, 3))

    # --- table: warm paper, gently darker toward the back; a soft wall above ---
    wall = np.array([0.82, 0.78, 0.70]); table = np.array([0.90, 0.85, 0.74])
    img[:] = wall[None, None, :]
    tmask = Y >= GROUND
    depth = np.clip((Y - GROUND) / (H - GROUND), 0, 1)            # 0 back → 1 front
    table_shaded = table[None, None, :] * (0.86 + 0.14 * depth[..., None])
    img = np.where(tmask[..., None], table_shaded, img)

    # spheres: (cx, cy, r, colour) — back-to-front
    spheres = [
        (560, GROUND + 120, 90, np.array([0.50, 0.55, 0.46])),   # sage
        (760, GROUND + 175, 130, np.array([0.70, 0.40, 0.30])),  # terracotta
        (960, GROUND + 120, 80, np.array([0.85, 0.80, 0.62])),   # cream
    ]

    # --- REAL soft cast shadows: project each disc onto the table along L, blur ---
    shadow = np.zeros((H, W))
    for (cx, cy, r, _c) in spheres:
        # shadow offset grows with the light's grazing angle; flatten vertically (ground plane)
        ox, oy = -L[0] / L[2] * r * 1.6, abs(L[1] / L[2]) * r * 0.5
        sx, sy = cx + ox, cy + oy
        ell = ((X - sx) / (r * 1.15)) ** 2 + ((Y - sy) / (r * 0.45)) ** 2
        shadow += np.clip(1 - ell, 0, 1)
    shadow = np.clip(shadow, 0, 1) * tmask
    shadow = box_blur(shadow, 41)
    img = img * (1 - 0.38 * shadow[..., None])

    # --- spheres: Lambert + ambient + soft specular ---
    for (cx, cy, r, col) in spheres:
        nx = (X - cx) / r; ny = (Y - cy) / r
        d2 = nx * nx + ny * ny
        m = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        ndl = np.clip(nx * L[0] + (-ny) * L[1] + nz * L[2], 0, 1)   # screen y is down → flip
        shade = 0.22 + 0.9 * ndl                                    # ambient + diffuse
        # specular: reflect light about normal, view = +z
        refz = 2 * ndl * nz - L[2]
        spec = np.clip(refz, 0, 1) ** 24 * (ndl > 0)
        body = col[None, None, :] * shade[..., None] + np.array([1, 1, 1])[None, None, :] * (0.5 * spec)[..., None]
        # contact ambient occlusion: tiny darkening at the very bottom rim
        img = np.where(m[..., None], np.clip(body, 0, 1), img)

    img = img + (np.random.default_rng(5).random((H, W, 1)) - 0.5) * 0.015
    write_png("stilllife.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote stilllife.png")


if __name__ == "__main__":
    main()
