#!/usr/bin/env python3
"""Session-4 #2 — raymarcher, take 2: SMOOTH-MIN blended SDF (organic fused forms).
Extends the ray-marcher (#1) with `smin` (polynomial smooth minimum) so primitives melt
into one continuous sculpture instead of separate balls — the SDF equivalent of the
session-2 metaball move, but with real computed light (soft shadows + AO). A low camera,
off-centre, dusk back-light for rim. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 850
RNG = np.random.default_rng(9)
MAXST, EPS, FAR = 110, 0.0015, 40.0
SUN = np.array([-0.55, 0.40, -0.55]); SUN = SUN / np.linalg.norm(SUN)   # low, raking → long shadow + rim


def smin(a, b, k=0.45):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


# fused blob: a stack of offset spheres + a leaning capsule, smin'd into one body
BLOBS = [
    (np.array([-0.6, 0.62, 0.0]), 0.62),
    (np.array([-0.30, 1.05, 0.10]), 0.42),
    (np.array([-0.05, 1.42, 0.05]), 0.30),
    (np.array([-0.55, 0.30, 0.35]), 0.34),
]


def sdf(p):
    body = np.full(p.shape[:-1], 1e9)
    for c, r in BLOBS:
        body = smin(body, np.sqrt(((p - c) ** 2).sum(-1)) - r, k=0.40)
    ground = p[..., 1]
    d = np.minimum(body, ground)
    mat = np.where(body < ground, 1.0, 0.0)
    return d, mat


def sdf_d(p):
    return sdf(p)[0]


def normals(p):
    e = 0.0012
    out = []
    for ax in (np.array([e, 0, 0]), np.array([0, e, 0]), np.array([0, 0, e])):
        out.append(sdf_d(p + ax) - sdf_d(p - ax))
    n = np.stack(out, -1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def soft_shadow(p, ldir, k=8.0):
    res = np.ones(p.shape[:-1]); t = np.full(p.shape[:-1], 0.12); alive = np.ones(p.shape[:-1], bool)
    for _ in range(48):
        h = sdf_d(p + ldir * t[..., None])
        res = np.where(alive, np.minimum(res, k * h / np.maximum(t, 1e-4)), res)
        t = t + np.clip(h, 0.01, 0.3); alive &= (h > 0.001) & (t < 14.0)
    return np.clip(res, 0, 1)


def ao(p, n):
    occ = np.zeros(p.shape[:-1]); sca = 1.0
    for i in range(8):
        hr = 0.015 + 0.07 * i
        occ += np.clip(hr - sdf_d(p + n * hr), 0, None) * sca; sca *= 0.80
    return np.clip(1.0 - 1.6 * occ, 0, 1)


def main():
    ro = np.array([1.7, 0.85, 3.6]); ta = np.array([-0.35, 0.85, 0.0])   # low, off to the side
    fwd = ta - ro; fwd /= np.linalg.norm(fwd)
    rgt = np.cross(fwd, np.array([0, 1.0, 0])); rgt /= np.linalg.norm(rgt)
    up = np.cross(rgt, fwd)
    xs = (np.arange(W) - W / 2) / H; ys = (H / 2 - np.arange(H)) / H
    px, py = np.meshgrid(xs, ys)
    rd = fwd[None, None] + px[..., None] * rgt[None, None] * 1.1 + py[..., None] * up[None, None] * 1.1
    rd = rd / np.linalg.norm(rd, axis=-1, keepdims=True)
    ro_f = np.broadcast_to(ro, rd.shape).astype(float)

    t = np.zeros((H, W)); hit = np.zeros((H, W), bool)
    for _ in range(MAXST):
        d = sdf_d(ro_f + rd * t[..., None])
        t = np.where(~hit, t + d * 0.80, t)
        hit |= (~hit) & (d < EPS)
        t = np.where(~hit & (t > FAR), FAR, t)
    pos = ro_f + rd * t[..., None]; far = t >= FAR

    sky_t = np.clip(rd[..., 1] * 0.5 + 0.5, 0, 1)
    top = np.array([0.16, 0.20, 0.34]); horizon = np.array([0.90, 0.58, 0.40])
    sky = horizon[None, None] + (top - horizon)[None, None] * sky_t[..., None]
    glow = np.clip(np.einsum("...i,i->...", rd, SUN), 0, 1) ** 6
    sky = sky + np.array([1.0, 0.80, 0.5])[None, None] * (0.6 * glow[..., None])

    n = normals(pos); _, mat = sdf(pos)
    ndl = np.clip(np.einsum("...i,i->...", n, SUN), 0, 1)
    sh = soft_shadow(pos + n * 0.004, SUN); occ = ao(pos, n)
    body = mat == 1
    alb = np.where(body[..., None], np.array([0.72, 0.45, 0.34]), np.array([0.42, 0.38, 0.34]))
    sun_col = np.array([1.0, 0.82, 0.58]); skyfill = np.array([0.40, 0.46, 0.6])
    direct = sun_col[None, None] * (ndl * sh)[..., None]
    ambient = skyfill[None, None] * (0.30 + 0.22 * n[..., 1])[..., None] * occ[..., None]
    # rim light: back-lit edges glow (fresnel-ish, from the low sun behind)
    fres = (1.0 - np.clip(np.einsum("...i,...i->...", n, -rd), 0, 1)) ** 3
    rim = np.array([1.0, 0.7, 0.45])[None, None] * (fres * np.clip(np.einsum("...i,i->...", n, SUN) + 0.3, 0, 1))[..., None] * body[..., None]
    col = alb * (direct + ambient) + 0.5 * rim
    h = SUN[None, None] - rd; h = h / (np.linalg.norm(h, axis=-1, keepdims=True) + 1e-9)
    spec = np.clip(np.einsum("...i,...i->...", n, h), 0, 1) ** 36 * sh * body
    col = col + sun_col[None, None] * (0.45 * spec)[..., None]

    img = np.where(far[..., None], sky, col)
    fog = np.clip(t / FAR, 0, 1)[..., None]
    img = img * (1 - 0.28 * fog) + horizon[None, None] * (0.28 * fog)
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.015
    write_png("raymarch2.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote raymarch2.png")


if __name__ == "__main__":
    main()
