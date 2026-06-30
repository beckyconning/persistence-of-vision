"""
Mohr cube, animated — the motion the s15 stills wanted and didn't take.

A single large "Cubic Limit" cube completing ONE seamless rotation loop (APNG),
with its four space-diagonals in red. Reuses the wireframe projection + the
vectorised line-stamp; the only new axis is TIME. Loop closes because the rotation
angles are exact multiples of 2π over the frame count.
"""
import os
import numpy as np
from apnglib import write_apng

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W = H = 520 * SS
N = 48                                   # frames in the loop
rng = np.random.default_rng(5)

V = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
EDGES = [(i, j) for i in range(8) for j in range(i + 1, 8)
         if np.sum(np.abs(V[i] - V[j])) == 2]
DIAG = [(i, 7 - i) for i in range(4)]


def rot(a, b, g):
    ca, sa = np.cos(a), np.sin(a); cb, sb = np.cos(b), np.sin(b); cg, sg = np.cos(g), np.sin(g)
    Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def stamp(buf, p0, p1, halfw):
    x0, y0 = p0; x1, y1 = p1
    lo_x = int(max(0, np.floor(min(x0, x1) - halfw - 2))); hi_x = int(min(W, np.ceil(max(x0, x1) + halfw + 2)))
    lo_y = int(max(0, np.floor(min(y0, y1) - halfw - 2))); hi_y = int(min(H, np.ceil(max(y0, y1) + halfw + 2)))
    if hi_x <= lo_x or hi_y <= lo_y:
        return
    yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else np.clip(((xx - x0) * dx + (yy - y0) * dy) / L2, 0, 1)
    dist = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
    cov = np.clip((halfw - dist) / 1.4 + 0.5, 0, 1)
    buf[lo_y:hi_y, lo_x:hi_x] = np.maximum(buf[lo_y:hi_y, lo_x:hi_x], cov)


def box(a):
    h, w = a.shape
    return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))


paper = np.array([0.94, 0.91, 0.84]); inkc = np.array([0.11, 0.10, 0.13]); redc = np.array([0.74, 0.13, 0.12])
scale = W * 0.26
ctr = np.array([W / 2, H / 2])
frames = []
for f in range(N):
    ink = np.zeros((H, W)); red = np.zeros((H, W))
    th = 2 * np.pi * f / N
    P = (V @ rot(th, 2 * th, 0.5 * th).T)[:, :2] * scale + ctr   # closed loop
    for i, j in EDGES:
        stamp(ink, P[i], P[j], halfw=1.3 * SS / 2)
    for i, j in DIAG:
        stamp(red, P[i], P[j], halfw=1.0 * SS / 2)
    inkd, redd = box(ink), box(red)
    rgb = paper[None, None, :] * np.ones((H // SS, W // SS, 1))
    rgb = rgb * (1 - inkd[..., None]) + inkc[None, None, :] * inkd[..., None]
    rgb = rgb * (1 - redd[..., None]) + redc[None, None, :] * redd[..., None]
    frames.append((np.clip(rgb, 0, 1) * 255).astype(np.uint8))

write_apng(os.path.join(OUT, "cube_rotating.png"), frames, delay_num=4, delay_den=100)
print("wrote cube_rotating.png  %d frames %dx%d" % (N, W // SS, H // SS))
