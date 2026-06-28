#!/usr/bin/env python3
"""Session-3 #2 — break the centred-symmetric-face habit (my own s3 critique):
a HEAD IN PROFILE, facing left. The defining feature of a profile is the front
CONTOUR (forehead→nose→lips→chin), so it's built differently from the frontal
relief: per row, the head spans [front(t), back(t)] interpolated from control
points; the nose protrudes on the front edge. Interior is sculpted as a relief
(brow, recessed eye + eyeball, cheekbone, ear, lips, jaw) with a raised dark hair
mass, then normals from the height gradient + Lambert under a front-left key light.
Earth/skin palette, neutral ground. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1150, 1400
RNG = np.random.default_rng(11)
ii, jj = np.mgrid[0:H, 0:W]
T = ii / H                      # 0 crown .. 1 neck
X = jj / W                      # 0 left .. 1 right (face faces LEFT)

# --- profile contours as control points (t, x) ---
FRONT = [(0.04, 0.515), (0.055, 0.47), (0.075, 0.435), (0.105, 0.405), (0.15, 0.385),
         (0.24, 0.355), (0.34, 0.355), (0.39, 0.375), (0.45, 0.355), (0.51, 0.315),
         (0.56, 0.235), (0.59, 0.305), (0.625, 0.31), (0.65, 0.29), (0.67, 0.31),
         (0.735, 0.295), (0.78, 0.355), (0.83, 0.43), (0.92, 0.45), (1.0, 0.455)]
BACK = [(0.04, 0.555), (0.055, 0.60), (0.075, 0.635), (0.105, 0.675), (0.15, 0.71),
        (0.33, 0.745), (0.49, 0.73), (0.63, 0.70), (0.75, 0.66), (0.87, 0.63), (1.0, 0.61)]
ft = np.array([p[0] for p in FRONT]); fx = np.array([p[1] for p in FRONT])
bt = np.array([p[0] for p in BACK]); bx = np.array([p[1] for p in BACK])


def smooth1d(a, k):
    """Moving-average a per-row curve so piecewise-linear control points don't
    leave slope creases (which become horizontal ridges in the cross-section)."""
    ker = np.ones(k) / k
    pad = np.r_[np.full(k, a[0]), a, np.full(k, a[-1])]
    return np.convolve(pad, ker, "same")[k:-k]


t1 = np.arange(H) / H
front1 = smooth1d(np.interp(t1, ft, fx), 55)      # nose tip stays sharp enough
back1 = smooth1d(np.interp(t1, bt, bx), 55)
front = front1[:, None]
back = back1[:, None]
mask = (X >= front) & (X <= back) & (T > 0.035) & (T < 0.99)


def bump(t0, x0, at, ax, amp, p=2.0):
    d = ((T - t0) / at) ** 2 + ((X - x0) / ax) ** 2
    return amp * np.clip(1 - d, 0, 1) ** p


def box(a, k):
    c = np.cumsum(np.cumsum(a, 0), 1); c = np.pad(c, ((1, 0), (1, 0)))
    s = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
    return np.pad(s, ((0, H - s.shape[0]), (0, W - s.shape[1])), mode="edge")


def main():
    # rounded cross-section: high in the middle of the head width, falling to edges
    mid = (front + back) / 2.0
    halfw = (back - front) / 2.0 + 1e-6
    cyl = np.sqrt(np.clip(1 - ((X - mid) / halfw) ** 2, 0, 1))   # 0..1 across width
    z = cyl * 0.36

    # brow ridge over the eye
    z += bump(0.40, 0.44, 0.045, 0.10, 0.065)
    # eye socket recess + eyeball + lid (lower & set back from v1)
    z -= bump(0.435, 0.43, 0.05, 0.075, 0.06)
    z += bump(0.438, 0.43, 0.030, 0.05, 0.048)        # eyeball
    # cheekbone
    z += bump(0.50, 0.48, 0.07, 0.10, 0.045)
    # naso-labial + lips (small in profile)
    z += bump(0.635, 0.36, 0.03, 0.055, 0.032)        # mouth area
    z -= bump(0.652, 0.35, 0.018, 0.045, 0.024)       # lip line
    # jaw mass
    z += bump(0.73, 0.49, 0.07, 0.10, 0.028)
    # ear — a raised C on the mid-back of the head
    z += bump(0.50, 0.60, 0.055, 0.04, 0.07)
    z -= bump(0.505, 0.603, 0.028, 0.02, 0.046)       # concha hollow
    # hair mass: crown + back + above forehead — SMOOTH (blurred) so no facets/hard cut
    hairline = np.interp(T, [0.0, 0.30, 0.34, 0.40], [0.30, 0.355, 0.50, 0.56])
    hair_raw = ((T < 0.32) | ((X > hairline) & (T < 0.55))) & mask
    hairmass = box(hair_raw.astype(float), 41)        # feather the boundary
    z = z + hairmass * 0.11

    z = np.where(mask, z, 0.0)
    z = box(z, 13)

    gy, gx = np.gradient(z)
    scale = 900.0
    nx, ny, nz = -gx * scale, -gy * scale, np.ones_like(z)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz); nx, ny, nz = nx / nl, ny / nl, nz / nl
    L = np.array([-0.5, -0.45, 0.74]); L /= np.linalg.norm(L)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    F = np.array([0.5, 0.1, 0.6]); F /= np.linalg.norm(F)
    fill = np.clip(nx * F[0] + ny * F[1] + nz * F[2], 0, 1)
    shade = 0.16 + 0.82 * ndl + 0.12 * fill
    refz = 2 * ndl * nz - L[2]
    spec = (np.clip(refz, 0, 1) ** 30) * (ndl > 0)

    skin = np.array([0.76, 0.57, 0.46])
    haircol = np.array([0.19, 0.14, 0.12])
    hmix = np.clip(hairmass * 1.6, 0, 1)[..., None]
    alb = (1 - hmix) * skin[None, None, :] + hmix * haircol[None, None, :]
    iris = bump(0.438, 0.425, 0.016, 0.022, 1.0) > 0.4
    alb[iris] = np.array([0.18, 0.13, 0.11])
    lips = bump(0.642, 0.355, 0.016, 0.045, 1.0) > 0.4
    alb[lips & (hairmass < 0.2)] = np.array([0.60, 0.33, 0.30])
    alb *= (0.96 + 0.06 * box(RNG.random((H, W)), 9))[..., None]

    bg = np.array([0.80, 0.77, 0.70])
    gg = np.clip(T, 0, 1)
    bgimg = bg[None, None, :] * (0.92 + 0.10 * gg[..., None])
    face = alb * shade[..., None] + np.array([1.0, 0.96, 0.9])[None, None, :] * (0.30 * spec)[..., None]
    # eye catchlight
    cy = int(0.432 * H); cx = int(0.422 * W)
    face[cy-2:cy+2, cx-2:cx+2] = np.array([0.99, 0.97, 0.92])

    img = np.where(mask[..., None], np.clip(face, 0, 1), bgimg)
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.012
    write_png("profile.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote profile.png")


if __name__ == "__main__":
    main()
