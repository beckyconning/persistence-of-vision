"""Cyanotype contact print — a dragonfly. New axis within the cyanotype set: a TRANSLUCENT
specimen. A pressed fern blocks light fully (solid white); a dragonfly's WINGS are gauze —
they let most UV through, so they print as the faintest blue veil with the venation darker
where chitin is thicker. The body/thorax/eyes are opaque → white. This is the light-leak halo
of cyanotype used as the SUBJECT, not just an edge effect.
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


# two masks: opaque (fully blocks → white) and gauze (thin wing membrane → faint veil)
opaque = np.zeros((H, W))
gauze = np.zeros((H, W))


def stroke(x0, y0, x1, y1, w0, w1, soft=0.004):
    dx, dy = x1 - x0, y1 - y0
    L2 = dx * dx + dy * dy + 1e-9
    t = np.clip(((nx - x0) * dx + (ny - y0) * dy) / L2, 0, 1)
    px, py = x0 + t * dx, y0 + t * dy
    d = np.sqrt((nx - px) ** 2 + (ny - py) ** 2)
    w = w0 + (w1 - w0) * t
    return np.clip((w - d) / soft, 0, 1)


def disc(cx, cy, r, soft=0.004):
    d = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
    return np.clip((r - d) / soft, 0, 1)


def wing(cx, cy, ang, length, width, seed):
    """A teardrop membrane (gauze) with a leading-edge rib + radiating cross-veins (opaque-ish)."""
    ca, sa = np.cos(ang), np.sin(ang)
    u = (nx - cx) * ca + (ny - cy) * sa
    v = -(nx - cx) * sa + (ny - cy) * ca
    # teardrop: wide near base, tapering to a rounded tip; slightly asymmetric (front fuller)
    s = np.clip(u / length, 0, 1)
    halfw = width * np.sqrt(np.clip(s * (1.08 - s), 0, 1)) * 1.9
    front = halfw * 1.12   # leading edge fuller than trailing
    back = halfw * 0.9
    inside = (u > 0) & (u < length) & (v < front) & (v > -back)
    membrane = inside.astype(float)
    gauze[:] = np.maximum(gauze, blur(membrane, 2))
    # leading-edge rib (pterostigma-ward), darker
    lead = stroke(cx, cy, cx + ca * length * 0.97 - sa * width * 1.6,
                  cy + sa * length * 0.97 + ca * width * 1.6, 0.006, 0.0015, soft=0.003) * inside
    # cross-veins: many fine ribs fanning from base across the membrane
    veins = np.zeros((H, W))
    rg = np.random.default_rng(seed)
    for f in np.linspace(0.06, 0.97, 22):
        tx = cx + ca * length * f
        ty = cy + sa * length * f
        spread = (front + back) * 0.5
        ex = tx - sa * spread * 1.2 + rg.uniform(-0.004, 0.004)
        ey = ty + ca * spread * 1.2
        ex2 = tx + sa * back * 1.1
        ey2 = ty - ca * back * 1.1
        veins = np.maximum(veins, stroke(tx, ty, ex, ey, 0.0016, 0.0008, soft=0.0022) * inside)
        veins = np.maximum(veins, stroke(tx, ty, ex2, ey2, 0.0016, 0.0008, soft=0.0022) * inside)
    # a couple of longitudinal veins
    for off in (-0.6, -0.2, 0.2, 0.5):
        veins = np.maximum(veins, stroke(
            cx - sa * off * width, cy + ca * off * width,
            cx + ca * length * 0.95 - sa * off * width * 0.4,
            cy + sa * length * 0.95 + ca * off * width * 0.4,
            0.0016, 0.0009, soft=0.0022) * inside)
    rib = np.maximum(lead, veins)
    # pterostigma: small opaque cell near the leading tip
    px = cx + ca * length * 0.82 - sa * front * 0.7
    py = cy + sa * length * 0.82 + ca * front * 0.7
    rib = np.maximum(rib, disc(px, py, 0.011, soft=0.003))
    opaque[:] = np.maximum(opaque, rib * 0.85)


CX, CY = 0.5, 0.5
ang_body = -np.radians(90)  # head up, abdomen down

# four wings (fore + hind, both sides), swept like a resting/flying dragonfly
wing(CX, CY - 0.02, np.radians(18), 0.34, 0.052, seed=1)    # right fore
wing(CX, CY - 0.02, np.radians(-198), 0.34, 0.052, seed=2)  # left fore  (162deg)
wing(CX, CY + 0.04, np.radians(40), 0.30, 0.060, seed=3)    # right hind (broader base)
wing(CX, CY + 0.04, np.radians(-220), 0.30, 0.060, seed=4)  # left hind  (140deg)

# --- opaque body ---
# head + compound eyes
opaque[:] = np.maximum(opaque, disc(CX, CY - 0.085, 0.028))
opaque[:] = np.maximum(opaque, disc(CX - 0.022, CY - 0.092, 0.020))
opaque[:] = np.maximum(opaque, disc(CX + 0.022, CY - 0.092, 0.020))
# thorax (robust)
opaque[:] = np.maximum(opaque, stroke(CX, CY - 0.07, CX, CY + 0.04, 0.030, 0.024, soft=0.005))
# abdomen: long tapering, faintly segmented
ax0, ay0, ax1, ay1 = CX, CY + 0.04, CX, CY + 0.44
opaque[:] = np.maximum(opaque, stroke(ax0, ay0, ax1, ay1, 0.020, 0.006, soft=0.004))
# segment notches (let a sliver of blue between segments)
for seg in np.linspace(0.08, 0.40, 9):
    yy = CY + seg
    w = 0.020 + (0.006 - 0.020) * (seg - 0.04) / 0.40
    notch = (np.abs(ny - yy) < 0.004) & (np.abs(nx - CX) < w * 0.9)
    opaque[notch] *= 0.35
# legs (thin, opaque), three each side from thorax
for k, ly in enumerate((-0.04, -0.01, 0.02)):
    for s in (+1, -1):
        kx = CX + s * 0.012
        opaque[:] = np.maximum(opaque, stroke(
            kx, CY + ly, CX + s * (0.10 + 0.02 * k), CY + ly + 0.06 + 0.02 * k,
            0.0022, 0.0010, soft=0.0024))

opaque[:] = np.clip(opaque, 0, 1)
gauze[:] = np.clip(gauze - opaque, 0, 1)  # body sits on top of wings

# ---- compose ----
expo = 0.74 + 0.42 * blur(vnoise(7, 5), 24) + 0.10 * (1 - ny) - 0.06 * np.abs(nx - 0.5)
expo = np.clip(expo, 0, 1)
deep = np.array([0.06, 0.20, 0.38])
pale = np.array([0.87, 0.92, 0.96])
blue = deep[None, None, :] * expo[..., None] + np.array([0.10, 0.26, 0.45])[None, None, :] * (1 - expo)[..., None]

# wing veil: gauze blocks only ~30% of light → pale-ish blue, not white; veins darker (toward pale)
veil = 0.30 * gauze[..., None]
img = blue * (1 - veil) + pale * veil
# opaque: full white with translucent halo at edges
mo = opaque[..., None]
halo = (blur(opaque, 7) - opaque).clip(0, 1)[..., None]
img = img * (1 - mo) + pale * mo
img = img * (1 - 0.5 * halo) + blue * (0.5 * halo)
# paper grain
img *= (1 - 0.04 * (vnoise(W // 3, 9) - 0.5))[..., None]

write_png("../images/dragonfly.png", np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
print("wrote images/dragonfly.png")
