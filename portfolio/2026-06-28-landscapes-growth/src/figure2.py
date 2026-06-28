#!/usr/bin/env python3
"""Figure, take 2 — make it COHERE. The v1 read as nested stones because each
ellipsoid was shaded separately. Here the volumes are fused into ONE continuous
surface: per pixel take the nearest (max-height) ellipsoid and shade that single
unified normal — a metaball-style union — in a clearer reclining pose (propped
head, raised knee). Lambert + soft specular + real cast shadow. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1500, 1000
GROUND = int(H * 0.70)
L = np.array([-0.5, -0.7, 0.55]); L = L / np.linalg.norm(L)
RNG = np.random.default_rng(8)
Y, X = np.mgrid[0:H, 0:W].astype(float)
BRONZE = np.array([0.50, 0.38, 0.26])


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


# heavily-overlapping volumes forming one reclining body, head(left)→feet(right)
PARTS = [
    (470, GROUND - 150, 70, 78, 0.0),     # head (propped up)
    (560, GROUND - 95, 55, 50, 0.0),      # neck
    (720, GROUND - 95, 180, 130, 0.08),   # torso (big)
    (915, GROUND - 80, 150, 100, -0.04),  # hip
    (1040, GROUND - 150, 95, 130, 0.6),   # raised thigh/knee (vertical, iconic)
    (1140, GROUND - 60, 150, 62, 0.15),   # shin
    (1255, GROUND - 40, 55, 40, 0.0),     # foot
]


def height_and_normal():
    """Union: per pixel keep the ellipsoid with max surface height (nz*scale)."""
    best_h = np.full((H, W), -1.0)
    nrm = np.zeros((H, W, 3))
    for (cx, cy, a, b, tilt) in PARTS:
        ct, st = np.cos(tilt), np.sin(tilt)
        xr = (X - cx) * ct + (Y - cy) * st
        yr = -(X - cx) * st + (Y - cy) * ct
        u, v = xr / a, yr / b
        d2 = u * u + v * v
        m = d2 <= 1.0
        nz = np.sqrt(np.clip(1 - d2, 0, 1))
        h = nz * min(a, b)                                  # surface height proxy
        take = m & (h > best_h)
        best_h = np.where(take, h, best_h)
        nx = u / a; ny = v / b
        sx = nx * ct - ny * st; sy = nx * st + ny * ct
        for i, comp in enumerate((sx, sy, nz)):
            nrm[..., i] = np.where(take, comp, nrm[..., i])
    return best_h >= 0, nrm


def main():
    img = np.zeros((H, W, 3))
    top = np.array([0.87, 0.83, 0.76]); bot = np.array([0.72, 0.67, 0.58])
    g = np.clip(Y / H, 0, 1)
    img[:] = top[None, None, :] + (bot - top)[None, None, :] * g[..., None]
    img = np.where((Y >= GROUND)[..., None],
                   np.array([0.80, 0.75, 0.66])[None, None, :] * (0.9 + 0.1 * g[..., None]), img)

    mask, nrm = height_and_normal()

    # cast shadow from the unified silhouette, projected along L, blurred
    sh = np.zeros((H, W))
    ys, xs = np.where(mask)
    if len(xs):
        ox = int(-L[0] / L[2] * 70)
        proj = np.zeros((H, W))
        yy = np.clip(GROUND + 22 + (GROUND - ys) * 0.05, 0, H - 1).astype(int)
        xx = np.clip(xs + ox, 0, W - 1)
        proj[yy, xx] = 1.0
        sh = box_blur(proj, 55); sh = sh / sh.max() if sh.max() else sh
    img = img * (1 - 0.36 * (sh * (Y >= GROUND))[..., None])

    nx, ny, nz = nrm[..., 0], nrm[..., 1], nrm[..., 2]
    ndl = np.clip(nx * L[0] + (-ny) * L[1] + nz * L[2], 0, 1)
    shade = 0.18 + 0.95 * ndl
    refz = 2 * ndl * nz - L[2]
    spec = (np.clip(refz, 0, 1) ** 28) * (ndl > 0)
    body = BRONZE[None, None, :] * shade[..., None] + np.array([1, 0.96, 0.9])[None, None, :] * (0.32 * spec)[..., None]
    img = np.where(mask[..., None], np.clip(body, 0, 1), img)

    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.014
    write_png("figure2.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote figure2.png")


if __name__ == "__main__":
    main()
