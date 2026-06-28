#!/usr/bin/env python3
"""Session-4 #4 — push the marcher: REFLECTIONS (a second bounce).
Polished dark floor: where the primary ray hits the ground, reflect it and march AGAIN,
shading that second hit (the stone) and blending it into the floor by a Fresnel-ish
weight. The stone now appears mirrored in the floor — a real GI step beyond direct light.
Dark key-lit environment (keeps the chiaroscuro). numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 850
RNG = np.random.default_rng(5)
MAXST, EPS, FAR = 110, 0.0015, 40.0
KEY = np.array([-0.6, 0.72, 0.30]); KEY = KEY / np.linalg.norm(KEY)
KEYPOS = np.array([-3.4, 4.0, 2.0])
VOID = np.array([0.035, 0.035, 0.05])


def smin(a, b, k=0.40):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


BLOBS = [(np.array([-0.6, 0.62, 0.0]), 0.62), (np.array([-0.30, 1.05, 0.10]), 0.42),
         (np.array([-0.05, 1.42, 0.05]), 0.30), (np.array([-0.55, 0.30, 0.35]), 0.34)]


def sdf(p):
    body = np.full(p.shape[:-1], 1e9)
    for c, r in BLOBS:
        body = smin(body, np.sqrt(((p - c) ** 2).sum(-1)) - r)
    ground = p[..., 1]
    return np.minimum(body, ground), np.where(body < ground, 1.0, 0.0)


def sdf_d(p):
    return sdf(p)[0]


def normals(p):
    e = 0.0012; out = []
    for ax in (np.array([e, 0, 0]), np.array([0, e, 0]), np.array([0, 0, e])):
        out.append(sdf_d(p + ax) - sdf_d(p - ax))
    n = np.stack(out, -1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def soft_shadow(p, ldir, k=16.0):
    res = np.ones(p.shape[:-1]); t = np.full(p.shape[:-1], 0.16); alive = np.ones(p.shape[:-1], bool)
    for _ in range(40):
        h = sdf_d(p + ldir * t[..., None])
        res = np.where(alive, np.minimum(res, k * h / np.maximum(t, 1e-4)), res)
        t = t + np.clip(h, 0.01, 0.3); alive &= (h > 0.001) & (t < 16.0)
    return np.clip(res, 0, 1)


def ao(p, n):
    occ = np.zeros(p.shape[:-1]); sca = 1.0
    for i in range(8):
        hr = 0.015 + 0.07 * i
        occ += np.clip(hr - sdf_d(p + n * hr), 0, None) * sca; sca *= 0.80
    return np.clip(1.0 - 1.6 * occ, 0, 1)


def march(ro, rd):
    t = np.zeros(ro.shape[:-1]); hit = np.zeros(ro.shape[:-1], bool)
    for _ in range(MAXST):
        d = sdf_d(ro + rd * t[..., None])
        t = np.where(~hit, t + d * 0.80, t); hit |= (~hit) & (d < EPS)
        t = np.where(~hit & (t > FAR), FAR, t)
    return ro + rd * t[..., None], hit & (t < FAR)


def shade(pos, rd, hit):
    """Direct key + ambient + rim + spec for a set of surface hits. Returns colour."""
    n = normals(pos); _, mat = sdf(pos); body = mat == 1
    ndl = np.clip(np.einsum("...i,i->...", n, KEY), 0, 1)
    sh = soft_shadow(pos + n * 0.004, KEY); occ = ao(pos, n)
    dist = np.linalg.norm(KEYPOS[None, None] - pos, axis=-1)
    falloff = np.clip(1.0 / (1.0 + 0.16 * dist ** 2) * 3.2, 0, 1.1)
    alb = np.where(body[..., None], np.array([0.82, 0.54, 0.40]), np.array([0.20, 0.18, 0.18]))
    key_col = np.array([1.0, 0.84, 0.62])
    direct = key_col[None, None] * (ndl * sh * falloff)[..., None]
    ambient = np.array([0.06, 0.07, 0.10])[None, None] * occ[..., None]
    col = alb * (direct + ambient)
    fres = (1.0 - np.clip(np.einsum("...i,...i->...", n, -rd), 0, 1)) ** 3
    col = col + np.array([0.30, 0.40, 0.55])[None, None] * (0.35 * fres * body)[..., None]
    h = KEY[None, None] - rd; h = h / (np.linalg.norm(h, axis=-1, keepdims=True) + 1e-9)
    spec = np.clip(np.einsum("...i,...i->...", n, h), 0, 1) ** 60 * sh * body
    col = col + key_col[None, None] * (0.6 * spec)[..., None]
    return np.where(hit[..., None], col, VOID[None, None]), n, mat


def main():
    ro = np.array([1.7, 0.95, 3.6]); ta = np.array([-0.35, 0.85, 0.0])
    fwd = ta - ro; fwd /= np.linalg.norm(fwd)
    rgt = np.cross(fwd, np.array([0, 1.0, 0])); rgt /= np.linalg.norm(rgt)
    up = np.cross(rgt, fwd)
    xs = (np.arange(W) - W / 2) / H; ys = (H / 2 - np.arange(H)) / H
    px, py = np.meshgrid(xs, ys)
    rd = fwd[None, None] + px[..., None] * rgt[None, None] * 1.1 + py[..., None] * up[None, None] * 1.1
    rd = rd / np.linalg.norm(rd, axis=-1, keepdims=True)
    ro_f = np.broadcast_to(ro, rd.shape).astype(float)

    pos, hit = march(ro_f, rd)
    col, n, mat = shade(pos, rd, hit)
    floor = (mat == 0) & hit

    # ---- reflection bounce off the floor (n = +y) ----
    refl_dir = rd - 2 * np.einsum("...i,...i->...", rd, n)[..., None] * n
    refl_dir = refl_dir / np.linalg.norm(refl_dir, axis=-1, keepdims=True)
    rpos, rhit = march(pos + n * 0.01, refl_dir)
    rcol, _, _ = shade(rpos, refl_dir, rhit)
    # Fresnel: grazing floor angles reflect more; polished but not a mirror
    cosi = np.clip(-np.einsum("...i,...i->...", rd, n), 0, 1)
    fres = (0.04 + 0.96 * (1 - cosi) ** 5)
    refl_w = np.clip(fres * 0.85, 0, 0.8) * floor
    col = np.where(floor[..., None], col * (1 - refl_w[..., None]) + rcol * refl_w[..., None], col)

    img = np.clip(col, 0, 1) ** (1 / 2.2)
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.012
    write_png("raymarch4.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote raymarch4.png")


if __name__ == "__main__":
    main()
