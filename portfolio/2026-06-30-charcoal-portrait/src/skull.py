"""Charcoal — a skull (memento mori). Reuses the value-blocking + ovoid form-shading: a lit
cranium dome, deep black eye sockets + nasal void (the readability anchors), cheekbones/zygomatic
arches catching light, a row of upper teeth, the jaw. Raking key upper-left; warm toned paper.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def _b1(a, r, ax):
    n = a.shape[ax]; cs = np.cumsum(a, axis=ax)
    cs = np.concatenate([np.zeros_like(np.take(cs, [0], ax)), cs], axis=ax)
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(float); sh = [1, 1]; sh[ax] = n
    return (np.take(cs, hi, ax) - np.take(cs, lo, ax)) / cnt.reshape(sh)


def blur(a, r):
    for _ in range(3):
        a = _b1(a, r, 0); a = _b1(a, r, 1)
    return a


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def blob(cx, cy, sx, sy, rot=0.0):
    ca, sa = np.cos(rot), np.sin(rot)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    return np.exp(-((u / sx) ** 2 + (v / sy) ** 2))


CX, CY = 0.5, 0.44
# ---- skull mass: cranium dome (ovoid) + jaw, as a form to shade ----
# height field for form-shading (rounded front)
crani = blob(CX, CY, 0.205, 0.225)
jaw = blob(CX, CY + 0.20, 0.135, 0.105)
zmask = np.clip((np.maximum(crani, jaw) - 0.33) / 0.10, 0, 1)
zmask = blur(zmask, 3)
# pseudo-normal from a rounded ovoid for the cranium/face front
u = (nx - CX) / 0.235; v = (ny - (CY + 0.04)) / 0.30
nzz = np.sqrt(np.clip(1 - (u * u + v * v), 0, 1))
nl = np.sqrt(u * u + v * v + nzz * nzz) + 1e-9
N = np.stack([u / nl, v / nl, nzz / nl])
L = np.array([-0.5, -0.55, 0.66]); L /= np.linalg.norm(L)
lam = np.clip(N[0] * L[0] + N[1] * L[1] + N[2] * L[2], 0, 1)
val = 0.30 + 0.66 * lam ** 0.8
val = val * zmask + 0.62 * (1 - zmask)   # paper-ish behind (overwritten by bg later)

def carve(reg, amt):
    global val
    val = val * (1 - amt * reg)

def lift(reg, amt):
    global val
    val = np.clip(val + amt * reg, 0, 1)

# brow ridge highlight + temple hollows
lift(blur(blob(CX, CY - 0.02, 0.16, 0.03), 2) * zmask, 0.10)
# DEEP eye sockets (the anchor): big dark voids, slightly angled, with a bright superior rim
carve(blur(blob(CX - 0.085, CY + 0.03, 0.058, 0.05), 2), 0.82)
carve(blur(blob(CX + 0.085, CY + 0.03, 0.058, 0.05), 2), 0.82)
lift(blur(blob(CX - 0.085, CY - 0.012, 0.06, 0.012), 1) * zmask, 0.12)   # brow rim over socket
lift(blur(blob(CX + 0.085, CY - 0.012, 0.06, 0.012), 1) * zmask, 0.12)
# nasal aperture (dark inverted teardrop)
carve(blur(blob(CX, CY + 0.10, 0.028, 0.045), 2), 0.78)
carve(blur(blob(CX, CY + 0.072, 0.012, 0.03), 1), 0.6)
# cheekbones / zygomatic — catch light (lift) with a hollow beneath
lift(blur(blob(CX - 0.115, CY + 0.075, 0.05, 0.035), 2) * zmask, 0.12)
lift(blur(blob(CX + 0.115, CY + 0.075, 0.05, 0.035), 2) * zmask, 0.12)
carve(blur(blob(CX - 0.10, CY + 0.135, 0.05, 0.03), 2), 0.20)
carve(blur(blob(CX + 0.10, CY + 0.135, 0.05, 0.03), 2), 0.20)
# under-cheek + temple shadow
carve(blur(blob(CX + 0.165, CY + 0.0, 0.05, 0.10), 3) * zmask, 0.18)

# ---- teeth: a light arc with thin dark gaps ----
tooth_band = blur(blob(CX, CY + 0.175, 0.085, 0.022), 1) * zmask
lift(tooth_band, 0.14)
gaps = (0.5 + 0.5 * np.cos((nx - CX) * 140)) ** 6
carve(blur(tooth_band * gaps, 0) , 0.45)
carve(blur(blob(CX, CY + 0.158, 0.09, 0.004), 0), 0.3)   # gum line

# under-jaw + chin shadow
carve(blur(blob(CX, CY + 0.255, 0.12, 0.04), 3) * zmask, 0.30)

val = blur(val, 1)
val = np.clip(val, 0, 1)

# ---- compose on warm paper, dark ground ----
bg = 0.58 - 0.18 * (ny - 0.5)            # darker low, lighter high (light from behind/above)
bg = blur(bg, 10)
val = np.where(zmask > 0.04, val, bg)
paper = np.array([0.83, 0.80, 0.73]); charc = np.array([0.09, 0.09, 0.12])
img = charc[None, None, :] + (paper - charc)[None, None, :] * np.clip(val, 0, 1)[..., None]
img = img * (1 - 0.05 * (vnoise(W // 2, 11) - 0.5))[..., None]
vig = 1 - 0.24 * ((nx - 0.5) ** 2 + (ny - 0.46) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/skull.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/skull.png")
