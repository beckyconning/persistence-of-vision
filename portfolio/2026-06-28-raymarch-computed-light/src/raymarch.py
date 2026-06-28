#!/usr/bin/env python3
"""Session-4 #1 — LIGHT SIMULATION PROPER (FRONTIERS up-next #3) + off-centre comp (#4).
A fully vectorised SDF ray-marcher in numpy: march a ray per pixel through a signed-
distance scene (ground + three spheres), find surfaces, then COMPUTE the light —
normals from the SDF gradient, Lambert, soft (penumbra) shadows by marching toward the
sun, and ambient occlusion by sampling the field along the normal. Turns the prior
"painted / relief" light into genuinely simulated light. Dusk/earth palette, subject
pushed to the lower-left third (no centred symmetry). numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 820
RNG = np.random.default_rng(4)
MAXST, EPS, FAR = 96, 0.0015, 40.0
SUN = np.array([-0.5, 0.62, -0.35]); SUN = SUN / np.linalg.norm(SUN)

# scene primitives: spheres (centre, radius) — placed off-centre, varied sizes
SPH = [
    (np.array([-1.15, 0.70, 0.0]), 0.70),   # hero, lower-left third
    (np.array([0.55, 0.45, -0.9]), 0.45),    # smaller, behind-right
    (np.array([1.5, 0.30, 0.4]), 0.30),      # small accent, far right
]


def sdf(p):
    """p: (...,3). Union of ground plane (y=0) and spheres. Returns distance + which."""
    d = p[..., 1].copy()                       # ground plane
    mat = np.zeros(p.shape[:-1])               # 0 = ground
    for i, (c, r) in enumerate(SPH, start=1):
        ds = np.sqrt(((p - c) ** 2).sum(-1)) - r
        closer = ds < d
        d = np.where(closer, ds, d)
        mat = np.where(closer, i, mat)
    return d, mat


def sdf_d(p):
    return sdf(p)[0]


def normals(p):
    e = 0.0012
    ex = np.array([e, 0, 0]); ey = np.array([0, e, 0]); ez = np.array([0, 0, e])
    nx = sdf_d(p + ex) - sdf_d(p - ex)
    ny = sdf_d(p + ey) - sdf_d(p - ey)
    nz = sdf_d(p + ez) - sdf_d(p - ez)
    n = np.stack([nx, ny, nz], -1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def soft_shadow(p, ldir, k=9.0):
    """March from p toward the sun; penumbra from closest-approach ratio."""
    res = np.ones(p.shape[:-1])
    t = np.full(p.shape[:-1], 0.12)
    alive = np.ones(p.shape[:-1], bool)
    for _ in range(40):
        pos = p + ldir * t[..., None]
        h = sdf_d(pos)
        res = np.where(alive, np.minimum(res, k * h / np.maximum(t, 1e-4)), res)
        t = t + np.clip(h, 0.01, 0.3)
        alive &= (h > 0.001) & (t < 12.0)
    return np.clip(res, 0.0, 1.0)


def ao(p, n):
    occ = np.zeros(p.shape[:-1]); sca = 1.0
    for i in range(8):                              # more samples → no concentric banding
        hr = 0.015 + 0.07 * i
        d = sdf_d(p + n * hr)
        occ += np.clip(hr - d, 0, None) * sca       # clamp ≥0 kills the ring overshoot
        sca *= 0.80
    return np.clip(1.0 - 1.6 * occ, 0.0, 1.0)


def main():
    # camera
    ro = np.array([0.0, 1.5, 4.4])
    ta = np.array([-0.25, 0.55, 0.0])
    fwd = ta - ro; fwd /= np.linalg.norm(fwd)
    rgt = np.cross(fwd, np.array([0, 1.0, 0])); rgt /= np.linalg.norm(rgt)
    up = np.cross(rgt, fwd)
    xs = (np.arange(W) - W / 2) / H            # square pixels
    ys = (H / 2 - np.arange(H)) / H
    px, py = np.meshgrid(xs, ys)
    rd = fwd[None, None, :] + px[..., None] * rgt[None, None, :] * 1.15 + py[..., None] * up[None, None, :] * 1.15
    rd = rd / np.linalg.norm(rd, axis=-1, keepdims=True)
    ro_f = np.broadcast_to(ro, rd.shape).astype(float)

    # raymarch
    t = np.zeros((H, W)); hit = np.zeros((H, W), bool)
    for _ in range(MAXST):
        pos = ro_f + rd * t[..., None]
        d = sdf_d(pos)
        t = np.where(~hit, t + d * 0.82, t)         # smaller step → precise contact, no shimmer
        newhit = (~hit) & (d < EPS)
        hit |= newhit
        t = np.where(~hit & (t > FAR), FAR, t)
    pos = ro_f + rd * t[..., None]
    far = t >= FAR

    # ---- sky (dusk gradient) for misses ----
    sky_t = np.clip(rd[..., 1] * 0.5 + 0.5, 0, 1)
    top = np.array([0.20, 0.26, 0.42]); horizon = np.array([0.86, 0.62, 0.42])
    sky = horizon[None, None, :] + (top - horizon)[None, None, :] * sky_t[..., None]
    glow = np.clip(np.einsum("...i,i->...", rd, SUN), 0, 1) ** 8
    sky = sky + np.array([1.0, 0.85, 0.55])[None, None, :] * (0.5 * glow[..., None])

    # ---- shade hits ----
    n = normals(pos)
    _, mat = sdf(pos)
    ndl = np.clip(np.einsum("...i,i->...", n, SUN), 0, 1)
    sh = soft_shadow(pos + n * 0.003, SUN)
    occ = ao(pos, n)
    # albedo by material
    alb = np.empty((H, W, 3))
    ground = mat == 0
    alb[ground] = np.array([0.46, 0.40, 0.33])           # warm earth floor
    alb[mat == 1] = np.array([0.75, 0.32, 0.26])         # terracotta hero
    alb[mat == 2] = np.array([0.30, 0.42, 0.48])         # slate blue
    alb[mat == 3] = np.array([0.80, 0.70, 0.40])         # ochre accent
    skyfill = np.array([0.35, 0.42, 0.55])               # cool sky bounce (ambient)
    sun_col = np.array([1.0, 0.86, 0.62])
    direct = sun_col[None, None, :] * (ndl * sh)[..., None]
    ambient = skyfill[None, None, :] * (0.30 + 0.20 * n[..., 1])[..., None] * occ[..., None]
    col = alb * (direct + ambient)
    # specular sheen on the spheres
    h = SUN[None, None, :] - rd; h = h / (np.linalg.norm(h, axis=-1, keepdims=True) + 1e-9)
    spec = np.clip(np.einsum("...i,...i->...", n, h), 0, 1) ** 40 * sh * (~ground)
    col = col + sun_col[None, None, :] * (0.5 * spec)[..., None]

    img = np.where(far[..., None], sky, col)
    # subtle haze toward distance + gentle vignette + grain
    fog = np.clip(t / FAR, 0, 1)[..., None]
    img = img * (1 - 0.25 * fog) + horizon[None, None, :] * (0.25 * fog)
    img = np.clip(img, 0, 1) ** (1 / 2.2)                # gamma
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.015
    write_png("raymarch.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote raymarch.png")


if __name__ == "__main__":
    main()
