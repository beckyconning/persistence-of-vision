"""A true interior — a room with a single shaft of light (FRONTIERS up-next #3 + the
'change the environment' habit-break). Every prior ray-march (s4) sat in an open dusk void;
this one is ENCLOSED: a box room (walls/floor/ceiling as inward-facing planes), one bright
window-shaft, soft fill bounced off the walls instead of a sky. Vectorised SDF march in numpy.
"""
import numpy as np
from pnglib import write_png

W, H = 1100, 850
MAXD, STEPS, EPS = 40.0, 96, 0.001


def smin(a, b, k=0.4):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def scene(p):
    """SDF of a room (interior of a box) + a low plinth + a sphere on it.
    Room: distance to the nearest wall from INSIDE = min over the 6 inward faces."""
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    # room half-extents centred at origin, floor at y=0
    rx, ry, rz = 6.0, 5.0, 7.0
    room = np.minimum.reduce([rx - np.abs(x), y, ry - y, rz - np.abs(z)])  # inside-positive
    # plinth (rounded box) + sphere, fused
    bx, by, bz = np.abs(x - 1.2) - 1.1, np.abs(y - 0.6) - 0.6, np.abs(z + 0.5) - 1.1
    plinth = np.sqrt(np.maximum(bx, 0) ** 2 + np.maximum(by, 0) ** 2 + np.maximum(bz, 0) ** 2) - 0.15
    sph = np.sqrt((x - 1.2) ** 2 + (y - 1.9) ** 2 + (z + 0.5) ** 2) - 0.95
    obj = smin(plinth, sph, 0.5)
    return np.minimum(room, obj)


def normal(p):
    e = 0.0015
    dx = np.array([e, 0, 0]); dy = np.array([0, e, 0]); dz = np.array([0, 0, e])
    n = np.stack([
        scene(p + dx) - scene(p - dx),
        scene(p + dy) - scene(p - dy),
        scene(p + dz) - scene(p - dz),
    ], axis=-1)
    return n / (np.linalg.norm(n, axis=-1, keepdims=True) + 1e-9)


def march(ro, rd):
    t = np.zeros(ro.shape[:-1])
    hit = np.zeros(ro.shape[:-1], bool)
    for _ in range(STEPS):
        p = ro + rd * t[..., None]
        d = scene(p)
        hit |= d < EPS
        t += np.where(hit, 0.0, np.maximum(d * 0.9, EPS))
        t = np.minimum(t, MAXD)
    return t, hit


def shade(ro, rd):
    t, hit = march(ro, rd)
    p = ro + rd * t[..., None]
    n = normal(p)

    # one warm window-shaft light high on the +x wall, plus cool bounced fill
    lpos = np.array([5.4, 4.2, 3.0])
    ld = lpos - p
    ldist = np.linalg.norm(ld, axis=-1, keepdims=True)
    ldir = ld / (ldist + 1e-9)
    diff = np.clip(np.sum(n * ldir, axis=-1), 0, 1)

    # soft shadow toward the light
    sh = np.ones(p.shape[:-1])
    to = ldir
    ts = np.full(p.shape[:-1], 0.06)
    for _ in range(28):
        ps = p + to * ts[..., None]
        ds = scene(ps)
        sh = np.minimum(sh, np.clip(12.0 * ds / np.maximum(ts, 1e-4), 0, 1))
        ts += np.clip(ds, 0.02, 0.4)
    sh = np.clip(sh, 0, 1)

    warm = np.array([1.0, 0.86, 0.62])
    cool = np.array([0.30, 0.36, 0.5])
    falloff = np.clip(1.0 / (1.0 + 0.02 * ldist[..., 0] ** 2), 0, 1)
    key = (diff * sh * falloff)[..., None] * warm * 2.3
    # ambient fill: cool, modulated by a cheap AO (how open the hemisphere is)
    ao = np.clip(scene(p + n * 0.5) / 0.5, 0, 1)
    fill = (0.18 + 0.32 * ao)[..., None] * cool
    # upward bounce warmth near the floor (light pools on the floor)
    floorglow = np.clip(1.0 - p[..., 1] / 3.0, 0, 1)[..., None] * np.array([0.18, 0.13, 0.08])

    col = key + fill + floorglow
    col = np.where(hit[..., None], col, np.array([0.02, 0.025, 0.04]))  # void = near-black
    return col


def main():
    aspect = W / H
    xs = (np.linspace(-1, 1, W)) * aspect
    ys = np.linspace(1, -1, H)
    gx, gy = np.meshgrid(xs, ys)
    ro = np.array([-3.2, 2.6, 6.4])               # camera inside the room, looking in/down
    target = np.array([0.6, 1.4, -0.5])
    fwd = target - ro; fwd = fwd / np.linalg.norm(fwd)
    right = np.cross(fwd, np.array([0, 1, 0])); right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    rd = fwd[None, None] + (gx[..., None] * right + gy[..., None] * up) * 0.62
    rd = rd / np.linalg.norm(rd, axis=-1, keepdims=True)
    ro_b = np.broadcast_to(ro, rd.shape)

    col = shade(ro_b, rd)
    col = col * 0.85                                # exposure (avoid blow-out)
    col = col / (col + 0.55)                         # filmic-ish tonemap (keeps highlights)
    col = np.power(np.clip(col, 0, 1), 1 / 2.2)      # gamma
    write_png("../images/interior.png", (col * 255).astype(np.uint8))
    print("wrote interior.png")


if __name__ == "__main__":
    main()
