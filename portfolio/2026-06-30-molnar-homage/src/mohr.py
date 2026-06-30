"""
Homage to Manfred Mohr — "Cubic Limit" (1973-77), the companion to the Molnar.

Mohr took ONE object — the cube — and let an algorithm drive it: rotate it in
steps, project to 2D, draw the wireframe; later works add the space-diagonals and
remove edges by rule. Here: a grid that traces a cube tumbling through rotation
left->right, top->bottom (rotation as the material; the rule is legible). New
technique for this body of work: 3D wireframe projection (8 vertices, 12 edges,
orthographic), reusing the plotter line-stamp engine. One cell drops to its four
space-diagonals in red — Mohr's "diagonal path" motif.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
SS = 2
W = H = 1000 * SS
GRID = 9
MARGIN = 0.085 * W
rng = np.random.default_rng(5)

ink = np.zeros((H, W), float)
redb = np.zeros((H, W), float)

# unit cube
V = np.array([[x, y, z] for x in (-1, 1) for y in (-1, 1) for z in (-1, 1)], float)
EDGES = [(i, j) for i in range(8) for j in range(i + 1, 8)
         if np.sum(np.abs(V[i] - V[j])) == 2]          # 12 cube edges (adjacent)
DIAG = [(i, 7 - i) for i in range(4)]                  # 4 space diagonals


def rot(a, b, g):
    ca, sa = np.cos(a), np.sin(a); cb, sb = np.cos(b), np.sin(b); cg, sg = np.cos(g), np.sin(g)
    Rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    Ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    Rz = np.array([[cg, -sg, 0], [sg, cg, 0], [0, 0, 1]])
    return Rz @ Ry @ Rx


def stamp_segment(buf, p0, p1, halfw):
    x0, y0 = p0; x1, y1 = p1
    lo_x = int(max(0, np.floor(min(x0, x1) - halfw - 2)))
    hi_x = int(min(W, np.ceil(max(x0, x1) + halfw + 2)))
    lo_y = int(max(0, np.floor(min(y0, y1) - halfw - 2)))
    hi_y = int(min(H, np.ceil(max(y0, y1) + halfw + 2)))
    if hi_x <= lo_x or hi_y <= lo_y:
        return
    yy, xx = np.mgrid[lo_y:hi_y, lo_x:hi_x]
    px, py = xx - x0, yy - y0
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy
    t = 0.0 if L2 == 0 else np.clip((px * dx + py * dy) / L2, 0, 1)
    cx, cy = x0 + t * dx, y0 + t * dy
    dist = np.hypot(xx - cx, yy - cy)
    cov = np.clip((halfw - dist) / 1.4 + 0.5, 0, 1)
    buf[lo_y:hi_y, lo_x:hi_x] = np.maximum(buf[lo_y:hi_y, lo_x:hi_x], cov)


cell = (W - 2 * MARGIN) / GRID
scale = cell * 0.30
red_cell = (6, 2)

for gy in range(GRID):
    for gx in range(GRID):
        cx = MARGIN + (gx + 0.5) * cell
        cy = MARGIN + (gy + 0.5) * cell
        # rotation accumulates across the grid — the cube tumbles
        idx = gy * GRID + gx
        a = 0.18 + idx * 0.052
        b = 0.30 + idx * 0.067
        g = idx * 0.021
        P = (V @ rot(a, b, g).T)[:, :2]                # orthographic: drop z
        P = P * scale + np.array([cx, cy])
        if (gx, gy) == red_cell:
            for i, j in DIAG:
                stamp_segment(redb, P[i], P[j], halfw=1.1 * SS / 2)
        else:
            for i, j in EDGES:
                stamp_segment(ink, P[i], P[j], halfw=1.05 * SS / 2)


def box(a):
    h, w = a.shape
    return a.reshape(h // SS, SS, w // SS, SS).mean((1, 3))


inkd, redd = box(ink), box(redb)
paper = np.array([0.94, 0.91, 0.84])
inkc = np.array([0.11, 0.10, 0.13])
redc = np.array([0.74, 0.13, 0.12])
mottle = 1.0 + 0.018 * rng.standard_normal((H // SS, W // SS))[..., None]
rgb = paper[None, None, :] * mottle
rgb = rgb * (1 - inkd[..., None]) + inkc[None, None, :] * inkd[..., None]
rgb = rgb * (1 - redd[..., None]) + redc[None, None, :] * redd[..., None]
write_png(os.path.join(OUT, "cubic_limit.png"), (np.clip(rgb, 0, 1) * 255).astype(np.uint8))
print("wrote cubic_limit.png  ink=%.3f" % inkd.mean())
