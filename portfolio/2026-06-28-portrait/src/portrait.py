#!/usr/bin/env python3
"""Session-3 #1 — SUBJECT: the FACE / PORTRAIT (never attempted; FRONTIERS up-next #2).
Technique extension: a BAS-RELIEF sculpt. Build a height field z(x,y) by composing
facial structures (dome, brow, nose ridge, cheeks, lips, chin, eyeballs), derive
normals from the height gradient, then Lambert + soft specular under one key light —
turning the still-life's "computed light on volumes" into a sculpted relief portrait.
Skin/earth palette, paper-dark ground. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 1400
RNG = np.random.default_rng(7)
# normalized face coords: u right, v UP (so +v = up on the face)
xs = np.linspace(-1, 1, W)
ys = np.linspace(1.25, -1.25, H)            # top row = +1.25 (up)
U, V = np.meshgrid(xs, ys)


def bump(u0, v0, au, av, amp, p=2.0):
    """A smooth raised (or sunken) mound centred at (u0,v0)."""
    d = ((U - u0) / au) ** 2 + ((V - v0) / av) ** 2
    return amp * np.clip(1 - d, 0, 1) ** p


def box(a, k):
    c = np.cumsum(np.cumsum(a, 0), 1)
    c = np.pad(c, ((1, 0), (1, 0)))
    s = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
    return np.pad(s, ((0, H - s.shape[0]), (0, W - s.shape[1])), mode="edge")


def main():
    # ---- base head: ovoid, tapered to a jaw/chin below centre ----
    au = 0.60 - 0.20 * np.clip(-V, 0, 1)        # narrows toward the chin
    av = 0.92
    dome = 1 - (U / au) ** 2 - (V / av) ** 2
    head = np.sqrt(np.clip(dome, 0, 1))         # 0..1 rounded mass
    mask = dome > 0

    z = head * 0.62                              # overall relief depth

    # ---- brow ridges (above the eyes) ----
    z += bump(-0.23, 0.34, 0.26, 0.10, 0.10)
    z += bump(0.23, 0.34, 0.26, 0.10, 0.10)
    # ---- eye sockets: gentle recess, then a raised eyeball in each ----
    z -= bump(-0.23, 0.20, 0.20, 0.13, 0.07)
    z -= bump(0.23, 0.20, 0.20, 0.13, 0.07)
    eyeL = bump(-0.23, 0.19, 0.115, 0.075, 0.085)
    eyeR = bump(0.23, 0.19, 0.115, 0.075, 0.085)
    z += eyeL + eyeR
    # upper-lid overhang (small ridge just above each eye)
    z += bump(-0.23, 0.255, 0.135, 0.045, 0.05)
    z += bump(0.23, 0.255, 0.135, 0.045, 0.05)
    # ---- nose: bridge ridge down the midline, bulb tip, nostril flares ----
    z += bump(0.0, 0.13, 0.088, 0.33, 0.105, p=1.4)    # bridge (softer, wider)
    z += bump(0.0, -0.055, 0.105, 0.09, 0.095)         # tip bulb
    z += bump(-0.092, -0.05, 0.062, 0.055, 0.055)      # left ala
    z += bump(0.092, -0.05, 0.062, 0.055, 0.055)       # right ala
    z -= bump(-0.058, -0.07, 0.024, 0.026, 0.028)      # nostril hollows (subtler)
    z -= bump(0.058, -0.07, 0.024, 0.026, 0.028)
    # ---- cheeks ----
    z += bump(-0.36, 0.0, 0.24, 0.26, 0.05)
    z += bump(0.36, 0.0, 0.24, 0.26, 0.05)
    # ---- mouth: ONE lip-mass swell, split by a single thin groove ----
    z += bump(0.0, -0.335, 0.205, 0.072, 0.075)        # unified lip mound
    z -= bump(0.0, -0.335, 0.20, 0.0085, 0.052)        # the mouth line (one seam)
    z -= bump(0.0, -0.205, 0.026, 0.055, 0.024)        # philtrum groove
    # ---- chin (wide & close so no bright sulcus band) ----
    z += bump(0.0, -0.56, 0.23, 0.17, 0.066)
    z -= bump(0.0, -0.44, 0.21, 0.022, 0.012)          # whisper of a crease

    z = np.where(mask, z, 0.0)
    z = box(z, 7)                                       # smooth → clean normals

    # ---- normals from the height gradient ----
    gy, gx = np.gradient(z)
    scale = 950.0                                       # relief strength
    nx, ny, nz = -gx * scale, -gy * scale, np.ones_like(z)
    nl = np.sqrt(nx * nx + ny * ny + nz * nz)
    nx, ny, nz = nx / nl, ny / nl, nz / nl

    # key light upper-left-front (y is image-down, so up = -y)
    L = np.array([-0.42, -0.52, 0.74]); L /= np.linalg.norm(L)
    ndl = np.clip(nx * L[0] + ny * L[1] + nz * L[2], 0, 1)
    # soft fill from the right so the shadow side isn't dead
    F = np.array([0.55, -0.1, 0.55]); F /= np.linalg.norm(F)
    fill = np.clip(nx * F[0] + ny * F[1] + nz * F[2], 0, 1)
    shade = 0.16 + 0.86 * ndl + 0.16 * fill
    # soft specular highlight (sheen on nose tip / cheeks / lower lip)
    refz = 2 * ndl * nz - L[2]
    spec = (np.clip(refz, 0, 1) ** 22) * (ndl > 0)

    # ---- albedo: skin, with darker iris, redder lips, warm subsurface ----
    skin = np.array([0.74, 0.56, 0.45])
    alb = np.broadcast_to(skin, (H, W, 3)).astype(float).copy()
    lips = bump(0.0, -0.335, 0.195, 0.066, 1.0) > 0.32
    alb[lips] = np.array([0.62, 0.34, 0.31])
    # irises: dark, slightly off-centre toward the light (gaze)
    iris = (bump(-0.215, 0.185, 0.04, 0.045, 1.0) + bump(0.245, 0.185, 0.04, 0.045, 1.0)) > 0.4
    alb[iris] = np.array([0.20, 0.15, 0.13])
    # subtle skin warmth variation
    alb *= (0.96 + 0.06 * box(RNG.random((H, W)), 9))[..., None]

    img_top = np.array([0.12, 0.11, 0.13]); img_bot = np.array([0.05, 0.045, 0.06])
    g = np.clip((1.25 - V) / 2.5, 0, 1)
    bg = img_top[None, None, :] + (img_bot - img_top)[None, None, :] * g[..., None]

    face = alb * shade[..., None] + np.array([1.0, 0.96, 0.9])[None, None, :] * (0.5 * spec)[..., None]
    # catchlights in the eyes (single bright fleck each) — the cue that sells a face
    for (cu, cv) in [(-0.205, 0.205), (0.255, 0.205)]:
        cy = int((1.25 - cv) / 2.5 * H); cx = int((cu + 1) / 2 * W)
        face[cy-2:cy+2, cx-2:cx+2] = np.array([0.99, 0.97, 0.92])

    img = np.where(mask[..., None], np.clip(face, 0, 1), bg)
    # gentle vignette
    rad = np.sqrt((U / 1.1) ** 2 + (V / 1.4) ** 2)
    img *= np.clip(1.15 - 0.35 * rad, 0.55, 1)[..., None]
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.012
    write_png("portrait.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote portrait.png")


if __name__ == "__main__":
    main()
