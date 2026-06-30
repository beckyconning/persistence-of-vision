"""Charcoal still life — an egg on draped cloth. The foundational atelier value study, in the
same charcoal medium: a single ovoid with the full lighting vocabulary (highlight → light →
core shadow → reflected light → cast shadow), resting on folded cloth, raking key from upper-left.
New for the session: a composed STILL LIFE (object + ground + cast shadow) rather than a subject
in isolation — tests whether the value-blocking reads as believable 3D form, not just a face.
"""
import numpy as np
from pnglib import write_png

H = W = 1200
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis); cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def vnoise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


# ---- cloth ground (lower 2/3): soft horizontal folds receding, raking light ----
rg = np.random.default_rng(2)
zc = np.zeros((H, W))
for i in range(7):
    cy = 0.50 + 0.07 * i + 0.015 * rg.random()
    zc = zc + np.exp(-((ny - cy - 0.02 * np.sin(nx * 5 + i)) / (0.022 + 0.006 * rg.random())) ** 2)
zc = blur(zc, 3)
gyc, gxc = np.gradient(zc)
Lc = np.array([-0.6, -0.3, 0.6]); Lc /= np.linalg.norm(Lc)
nlc = np.stack([-gxc * 70, -gyc * 70, np.ones_like(zc)]);
nlc = nlc / (np.linalg.norm(nlc, axis=0) + 1e-9)
cloth = 0.42 + 0.5 * np.clip(nlc[0] * Lc[0] + nlc[1] * Lc[1] + nlc[2] * Lc[2], 0, 1)
cloth = cloth * (0.7 + 0.3 * ny)               # nearer cloth (lower) lighter
val = np.where(ny > 0.46, cloth, 0.62)         # wall behind = flat mid grey

# ---- egg: ovoid sphere with full lighting model ----
ECX, ECY, ER = 0.46, 0.55, 0.17
u = (nx - ECX) / (ER * 0.78); v = (ny - ECY) / (ER * 1.02)   # taller than wide
r2 = u * u + v * v
inside = r2 < 1.0
# surface normal of the ovoid
nzz = np.sqrt(np.clip(1 - r2, 0, 1))
nlen = np.sqrt(u * u + v * v + nzz * nzz) + 1e-9
N = np.stack([u / nlen, v / nlen, nzz / nlen])
Le = np.array([-0.5, -0.55, 0.67]); Le /= np.linalg.norm(Le)
lam = np.clip(N[0] * Le[0] + N[1] * Le[1] + N[2] * Le[2], 0, 1)
egg = 0.18 + 0.80 * lam ** 0.85                 # light → core shadow
# reflected light: faint lift on the shadow side from the lit cloth bouncing up
refl = np.clip(-(N[0] * Le[0] + N[1] * Le[1]), 0, 1) * np.clip(N[1], 0, 1)
egg = egg + 0.10 * refl
# specular highlight (eraser-bright) where N points at the light
spec = np.clip(N[0] * Le[0] + N[1] * Le[1] + N[2] * Le[2], 0, 1) ** 14
egg = egg + 0.5 * spec
egg = np.clip(egg, 0, 1)
egg_m = blur(inside.astype(float), 2)
val = val * (1 - egg_m) + egg * egg_m

# ---- cast shadow: an ellipse to the lower-right of the egg, soft, darkening the cloth ----
sx = (nx - (ECX + 0.10)) / 0.20; sy = (ny - (ECY + 0.135)) / 0.075
cast = np.clip(1 - (sx * sx + sy * sy), 0, 1)
cast = blur(cast, 6) * (ny > 0.5) * (1 - egg_m)
val = val * (1 - 0.5 * cast)

# contact shadow (darkest right under the egg)
con = np.clip(1 - (((nx - ECX) / 0.13) ** 2 + ((ny - (ECY + ER * 0.95)) / 0.025) ** 2), 0, 1)
val = val * (1 - 0.45 * blur(con, 2) * (1 - egg_m))

val = blur(val, 1)
val = np.clip(val, 0, 1)

# ---- palette ----
paper = np.array([0.83, 0.80, 0.73])
charc = np.array([0.10, 0.10, 0.12])
img = charc[None, None, :] + (paper - charc)[None, None, :] * val[..., None]
img = img * (1 - 0.05 * (vnoise(W // 2, 11) - 0.5))[..., None]
vig = 1 - 0.22 * ((nx - 0.47) ** 2 + (ny - 0.5) ** 2) / 0.5
img = img * vig[..., None]

write_png("../images/stilllife.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/stilllife.png")
