"""Cyanotype contact print — a circular LACE doily. Axis: a human-made, OPENWORK translucent
specimen (vs. the botanical/insect ones). Lace blocks light only where thread is — so the
print is a white filigree of rings, radial spokes, scalloped edge and a dense mesh field, with
deep Prussian blue showing through every hole. The thread prints crisp-white; the open ground
prints blue. A few "missed" cells (folds where the lace lifted) leak.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H
cx, cy = 0.5, 0.5
dx, dy = nx - cx, ny - cy
r = np.sqrt(dx * dx + dy * dy)
th = np.arctan2(dy, dx)


def _box1d(a, rr, axis):
    if rr < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis); cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - rr, 0, n); hi = np.clip(np.arange(n) + rr + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, rr):
    for _ in range(3):
        a = _box1d(a, rr, 0); a = _box1d(a, rr, 1)
    return a


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def ring(radius, width):
    return np.clip((width - np.abs(r - radius)) / 0.0015, 0, 1)


thread = np.zeros((H, W))
R = 0.43  # outer radius

# concentric structural rings
for rad, w in [(0.10, 0.006), (0.17, 0.004), (0.255, 0.005), (0.34, 0.004), (0.40, 0.006)]:
    thread = np.maximum(thread, ring(rad, w))

# radial spokes (24-fold)
N = 24
spoke = (np.abs(((th * N / (2 * np.pi)) % 1.0) - 0.5) * 2)  # 0 at spoke center
thread = np.maximum(thread, np.clip((spoke - 0.92) / 0.06, 0, 1) * (r < R) * (r > 0.10))

# fine mesh net between r=0.17 and 0.34: square grid in (r, theta) -> diamond filigree
band = (r > 0.17) & (r < 0.34)
mesh_r = np.clip((0.012 - np.abs(((r * 70) % 1.0) - 0.5) / 70 * 1.0 * 0), 0, 1)  # placeholder
# polar lattice: thin lines along constant r-steps and constant angle-steps (finer than spokes)
rg_lines = np.clip((0.18 - np.abs(((r * 60) % 1.0) - 0.5)) / 0.18, 0, 1)
ang_lines = np.clip((0.18 - np.abs(((th * (N * 4) / (2 * np.pi)) % 1.0) - 0.5)) / 0.18, 0, 1)
net = np.maximum(rg_lines * 0.0, np.maximum(rg_lines, ang_lines))
# keep only thin cores -> filigree threads
net = np.clip((net - 0.86) / 0.14, 0, 1)
thread = np.maximum(thread, net * band)

# inner rosette: 8 petals as overlapping small rings near center
for k in range(8):
    a = k / 8 * 2 * np.pi
    px, py = cx + 0.055 * np.cos(a), cy + 0.055 * np.sin(a)
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    thread = np.maximum(thread, np.clip((0.004 - np.abs(d - 0.045)) / 0.0015, 0, 1) * (r < 0.105))
thread = np.maximum(thread, np.clip((0.004 - r) / 0.0015, 0, 1))  # center dot

# scalloped picot edge: bumps riding on the outer ring
scallop = R + 0.022 * np.cos(th * 24) * (np.cos(th * 24) > 0)
edge_loop = np.clip((0.006 - np.abs(r - scallop)) / 0.0015, 0, 1)
thread = np.maximum(thread, edge_loop)
# tiny picot dots at each scallop peak
peaks = (np.abs(((th * 24 / (2 * np.pi)) % 1.0)) < 0.5)
thread = np.maximum(thread, np.clip((0.0035 - np.abs(r - (R + 0.022))) / 0.0012, 0, 1)
                    * (np.abs(((th * 24 / (2 * np.pi)) % 1.0) - 0.0) < 0.04))

# clip everything to the doily disc (outer scallop), nothing beyond
outer = scallop + 0.004
thread *= (r <= outer)
thread = blur(thread, 1)
thread = np.clip(thread, 0, 1)

# a couple of lifted folds where the lace didn't contact -> faint blur (leak), localized
lift = np.zeros((H, W))
for (lx, ly, lr) in [(0.33, 0.40, 0.06), (0.66, 0.63, 0.05)]:
    d = np.sqrt((nx - lx) ** 2 + (ny - ly) ** 2)
    lift = np.maximum(lift, np.clip((lr - d) / 0.04, 0, 1))

# ---- compose ----
expo = 0.73 + 0.40 * blur(vnoise(7, 5), 26) + 0.10 * (1 - ny)
expo = np.clip(expo, 0, 1)
deep = np.array([0.05, 0.19, 0.37])
pale = np.array([0.88, 0.93, 0.97])
blue = deep[None, None, :] * expo[..., None] + np.array([0.10, 0.26, 0.45])[None, None, :] * (1 - expo)[..., None]

m = thread[..., None]
img = blue * (1 - m) + pale * m
# fold-leak: where lace lifted, the white thread there prints softer (let blue bleed up under it)
soft = (lift * thread)[..., None]
img = img * (1 - 0.45 * soft) + blue * (0.45 * soft)
# faint overall halo around the whole doily edge
halo = (blur((r <= outer).astype(float), 10) - (r <= outer)).clip(0, 1)[..., None]
img = img * (1 - 0.18 * halo) + pale * (0.18 * halo)
# paper grain
img *= (1 - 0.04 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/lace.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/lace.png")
