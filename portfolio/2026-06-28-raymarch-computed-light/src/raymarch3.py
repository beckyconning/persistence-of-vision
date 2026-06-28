#!/usr/bin/env python3
"""Session-4 #3 — same ray-marcher, NEW ENVIRONMENT: hard key light in the dark.
Self-critique from #1/#2 said: stop defaulting to the dusk-gradient sky. So: a near-black
void, a single hard, slightly-warm key from the upper-left, deep shadows, a tight
spotlight falloff on the floor — chiaroscuro. The smin stone from #2, now dramatic
instead of atmospheric. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 850
RNG = np.random.default_rng(3)
MAXST, EPS, FAR = 110, 0.0015, 40.0
KEY = np.array([-0.6, 0.72, 0.30]); KEY = KEY / np.linalg.norm(KEY)   # hard key, upper-left, slightly front
KEYPOS = np.array([-3.4, 4.0, 2.0])                                   # for distance spotlight falloff


def smin(a, b, k=0.40):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


BLOBS = [
    (np.array([-0.6, 0.62, 0.0]), 0.62),
    (np.array([-0.30, 1.05, 0.10]), 0.42),
    (np.array([-0.05, 1.42, 0.05]), 0.30),
    (np.array([-0.55, 0.30, 0.35]), 0.34),
]


def sdf(p):
    body = np.full(p.shape[:-1], 1e9)
    for c, r in BLOBS:
        body = smin(body, np.sqrt(((p - c) ** 2).sum(-1)) - r)
    ground = p[..., 1]
    d = np.minimum(body, ground)
    return d, np.where(body < ground, 1.0, 0.0)


def sdf_d(p):
    return sdf(p)[0]


def normals(p):
    e = 0.0012; out = []
    for ax in (np.array([e, 0, 0]), np.array([0, e, 0]), np.array([0, 0, e])):
        out.append(sdf_d(p + ax) - sdf_d(p - ax))
    n = np.stack(out, -1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def soft_shadow(p, ldir, k=16.0):     # harder shadow edge for drama
    res = np.ones(p.shape[:-1]); t = np.full(p.shape[:-1], 0.12); alive = np.ones(p.shape[:-1], bool)
    for _ in range(48):
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

    t = np.zeros((H, W)); hit = np.zeros((H, W), bool)
    for _ in range(MAXST):
        d = sdf_d(ro_f + rd * t[..., None])
        t = np.where(~hit, t + d * 0.80, t); hit |= (~hit) & (d < EPS)
        t = np.where(~hit & (t > FAR), FAR, t)
    pos = ro_f + rd * t[..., None]; far = t >= FAR

    # near-black void with a faint warm haze low down (no dusk gradient)
    void = np.array([0.03, 0.03, 0.045])
    bg = np.broadcast_to(void, rd.shape).astype(float).copy()

    n = normals(pos); _, mat = sdf(pos); body = mat == 1
    ndl = np.clip(np.einsum("...i,i->...", n, KEY), 0, 1)
    sh = soft_shadow(pos + n * 0.004, KEY); occ = ao(pos, n)
    # distance falloff from the key (spotlight pool on the floor)
    dist = np.linalg.norm(KEYPOS[None, None] - pos, axis=-1)
    falloff = np.clip(1.0 / (1.0 + 0.16 * dist ** 2) * 3.2, 0, 1.1)   # tighter, dimmer pool
    alb = np.where(body[..., None], np.array([0.82, 0.54, 0.40]), np.array([0.22, 0.20, 0.20]))
    key_col = np.array([1.0, 0.84, 0.62])
    direct = key_col[None, None] * (ndl * sh * falloff)[..., None]
    ambient = np.array([0.07, 0.08, 0.11])[None, None] * occ[..., None]   # tiny cool fill only
    col = alb * (direct + ambient)
    # cool rim from behind to separate the stone from the void
    fres = (1.0 - np.clip(np.einsum("...i,...i->...", n, -rd), 0, 1)) ** 3
    col = col + np.array([0.30, 0.40, 0.55])[None, None] * (0.35 * fres * body)[..., None]
    h = KEY[None, None] - rd; h = h / (np.linalg.norm(h, axis=-1, keepdims=True) + 1e-9)
    spec = np.clip(np.einsum("...i,...i->...", n, h), 0, 1) ** 60 * sh * body
    col = col + key_col[None, None] * (0.6 * spec)[..., None]

    img = np.where(far[..., None], bg, col)
    img = np.clip(img, 0, 1) ** (1 / 2.2)
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.012
    write_png("raymarch3.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote raymarch3.png")


if __name__ == "__main__":
    main()
