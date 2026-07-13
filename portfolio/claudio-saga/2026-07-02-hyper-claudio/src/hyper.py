"""HYPER-REALISTIC CLAUDIO — vectorized SDF raymarcher.

A portrait bust sculpted from smooth-blended SDFs, shaded with a 3-light rig,
soft shadows, AO, subsurface approximation, procedural skin/hair/fabric
micro-detail, and a photographic post stack (DOF, bloom, CA, grain).

Mouth is parametric (jaw / width / pucker / lipcurl) for viseme lipsync.
"""
import numpy as np

# ---------------- noise ----------------

def _hash3(p):
    return np.modf(np.sin(p @ np.array([12.9898, 78.233, 37.719])) * 43758.5453)[0]


_P = np.random.default_rng(7).permutation(256).astype(np.int32)
_PERM = np.concatenate([_P, _P])


def vnoise(x, y, z):
    """Value noise, vectorized over arrays."""
    xi = np.floor(x).astype(np.int64)
    yi = np.floor(y).astype(np.int64)
    zi = np.floor(z).astype(np.int64)
    xf, yf, zf = x - xi, y - yi, z - zi
    u = xf * xf * (3 - 2 * xf)
    v = yf * yf * (3 - 2 * yf)
    w = zf * zf * (3 - 2 * zf)

    def h(ix, iy, iz):
        return _PERM[(_PERM[(_PERM[ix & 255] + (iy & 255)) & 511] + (iz & 255)) & 511] / 255.0

    n000 = h(xi, yi, zi)
    n100 = h(xi + 1, yi, zi)
    n010 = h(xi, yi + 1, zi)
    n110 = h(xi + 1, yi + 1, zi)
    n001 = h(xi, yi, zi + 1)
    n101 = h(xi + 1, yi, zi + 1)
    n011 = h(xi, yi + 1, zi + 1)
    n111 = h(xi + 1, yi + 1, zi + 1)
    nx00 = n000 * (1 - u) + n100 * u
    nx10 = n010 * (1 - u) + n110 * u
    nx01 = n001 * (1 - u) + n101 * u
    nx11 = n011 * (1 - u) + n111 * u
    nxy0 = nx00 * (1 - v) + nx10 * v
    nxy1 = nx01 * (1 - v) + nx11 * v
    return nxy0 * (1 - w) + nxy1 * w


def fbm(x, y, z, octaves=3, lac=2.1, gain=0.5):
    a, f, out = 1.0, 1.0, 0.0
    for _ in range(octaves):
        out = out + a * vnoise(x * f, y * f, z * f)
        a *= gain
        f *= lac
    return out


# ---------------- SDF primitives (vectorized: p is (N,3)) ----------------

def sd_sphere(p, c, r):
    return np.linalg.norm(p - c, axis=-1) - r


def sd_ellip(p, c, r):
    q = (p - c) / r
    k0 = np.linalg.norm(q, axis=-1)
    return (k0 - 1.0) * np.minimum(np.minimum(r[0], r[1]), r[2])


def sd_capsule(p, a, b, r):
    pa = p - a
    ba = np.asarray(b) - np.asarray(a)
    h = np.clip((pa @ ba) / (ba @ ba), 0, 1)
    return np.linalg.norm(pa - h[..., None] * ba, axis=-1) - r


def sd_rbox(p, c, b, r):
    q = np.abs(p - c) - b
    return (np.linalg.norm(np.maximum(q, 0), axis=-1)
            + np.minimum(np.max(q, axis=-1), 0) - r)


def sd_torus(p, c, R, r):
    q = p - c
    l = np.sqrt(q[..., 0] ** 2 + q[..., 2] ** 2) - R
    return np.sqrt(l ** 2 + q[..., 1] ** 2) - r


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0, 1)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


# ---------------- the bust ----------------
# Params dict: jaw (0..1), width (-1..1), pucker (0..1), blink (0..1),
#              browup (-1..1), eyex/eyey (gaze), headrx/headry (nod/turn)

MAT_SKIN, MAT_STACHE, MAT_BROW, MAT_EYE, MAT_TEETH, MAT_LIP, MAT_MOUTH, \
    MAT_CAP, MAT_SHIRT, MAT_STRAP, MAT_BUTTON, MAT_BACK, MAT_HAIR = range(13)


def rot_xy(p, rx, ry):
    cx, sx = np.cos(rx), np.sin(rx)
    cy, sy = np.cos(ry), np.sin(ry)
    y = p[..., 1] * cx - p[..., 2] * sx
    z = p[..., 1] * sx + p[..., 2] * cx
    x = p[..., 0] * cy + z * sy
    z2 = -p[..., 0] * sy + z * cy
    return np.stack([x, y, z2], axis=-1)


def scene(p, prm):
    """Returns (distance, material_id) for points p (N,3). Camera looks +z; face at -z."""
    # head-local coords (head nods/turns around neck pivot at (0,-1.1,0))
    piv = np.array([0.0, -1.1, 0.0])
    hp = rot_xy(p - piv, prm.get("headrx", 0.0), prm.get("headry", 0.0)) + piv

    jaw = prm.get("jaw", 0.0)
    width = prm.get("width", 0.0)
    pucker = prm.get("pucker", 0.0)
    blink = prm.get("blink", 0.0)

    # ---- skull mass ----
    d = sd_ellip(hp, np.array([0, 0.08, 0.12]), np.array([1.0, 1.08, 1.02]))
    d = smin(d, sd_sphere(hp, np.array([-0.52, -0.42, -0.62]), 0.40), 0.25)   # cheeks
    d = smin(d, sd_sphere(hp, np.array([0.52, -0.42, -0.62]), 0.40), 0.25)
    # jaw drops with mouth open
    jawc = np.array([0, -0.78 - 0.16 * jaw, -0.42])
    d = smin(d, sd_ellip(hp, jawc, np.array([0.62, 0.5 + 0.06 * jaw, 0.55])), 0.22)
    d = smin(d, sd_ellip(hp, np.array([0, 0.42, -0.72]), np.array([0.72, 0.28, 0.42])), 0.18)  # brow ridge
    # ears
    d = smin(d, sd_ellip(hp, np.array([-1.02, -0.12, 0.05]), np.array([0.16, 0.30, 0.22])), 0.08)
    d = smin(d, sd_ellip(hp, np.array([1.02, -0.12, 0.05]), np.array([0.16, 0.30, 0.22])), 0.08)
    # THE NOSE (load-bearing)
    d = smin(d, sd_sphere(hp, np.array([0, -0.28, -1.02]), 0.40), 0.16)
    d = smin(d, sd_capsule(hp, np.array([0, 0.18, -0.86]), np.array([0, -0.16, -1.0]), 0.16), 0.12)
    d = smin(d, sd_sphere(hp, np.array([-0.28, -0.38, -0.88]), 0.16), 0.10)  # alae
    d = smin(d, sd_sphere(hp, np.array([0.28, -0.38, -0.88]), 0.16), 0.10)
    # nostrils (subtract)
    d = smax(d, -sd_sphere(hp, np.array([-0.15, -0.49, -1.06]), 0.085), 0.05)
    d = smax(d, -sd_sphere(hp, np.array([0.15, -0.49, -1.06]), 0.085), 0.05)
    mat = np.full(d.shape, MAT_SKIN, dtype=np.int8)

    # ---- mouth ----
    mo = np.array([0, -0.85, -0.78])
    lipw = 0.33 * (1 + 0.22 * width) * (1 - 0.42 * pucker)
    liph = 0.075 + 0.15 * jaw + 0.09 * pucker
    lipz = -0.78 - 0.10 * pucker
    lips = sd_ellip(hp, np.array([0, -0.85, lipz]),
                    np.array([lipw, liph + 0.09, 0.22]))
    d2 = smin(d, lips, 0.06)
    lip_zone = lips < 0.05
    # cavity opens with jaw
    cav = sd_ellip(hp, np.array([0, -0.86 - 0.05 * jaw, lipz + 0.02]),
                   np.array([lipw * 0.8, (liph) * np.maximum(jaw, 0.02) * 1.1 + 0.005, 0.18]))
    d3 = smax(d2, -cav, 0.03)
    in_cavity = (cav < 0.06) & (d3 > d2 - 1e-4)
    # teeth: upper arc inside the cavity
    teeth = sd_rbox(hp, np.array([0, -0.80, lipz - 0.02]),
                    np.array([lipw * 0.62, 0.045, 0.045]), 0.02)
    show_teeth = jaw > 0.12
    if show_teeth:
        d3 = np.minimum(d3, teeth)
    d = d3
    mat = np.where(lip_zone & (d < 0.1), MAT_LIP, mat)
    mat = np.where(in_cavity & (d < 0.12), MAT_MOUTH, mat)
    if show_teeth:
        mat = np.where(teeth < 0.02, MAT_TEETH, mat)

    # ---- eyes ----
    for sx in (-1, 1):
        ec = np.array([sx * 0.40, 0.02, -0.84])
        socket = sd_sphere(hp, ec + np.array([0, 0.02, 0.12]), 0.30)
        d = smax(d, -socket, 0.10)
        eye = sd_sphere(hp, ec, 0.24)
        closer = eye < d
        d = np.minimum(d, eye)
        mat = np.where(closer, MAT_EYE, mat)
        # eyelids: shell over the eyeball, opening controlled by blink (per-eye for winks)
        bl = prm.get("blinkR" if sx > 0 else "blinkL", blink)
        lid_open = 0.205 * (1 - bl) + 0.006
        lid = sd_sphere(hp, ec + np.array([0, 0.005, 0]), 0.262)
        lid_cut = (ec[1] + lid_open) - hp[..., 1]          # keep ABOVE the lash line
        upper = smax(lid, lid_cut, 0.03)
        low_cut = hp[..., 1] - (ec[1] - lid_open * 0.85)   # keep BELOW the lower line
        lower = smax(lid, low_cut, 0.03)
        lids = np.minimum(upper, lower)
        closer = lids < d
        d = np.where(closer, smin(d, lids, 0.02), d)
        mat = np.where(closer, MAT_SKIN, mat)

    # ---- brows ----
    for sx in (-1, 1):
        brow = sd_capsule(hp, np.array([sx * 0.16, 0.30 + 0.05 * prm.get("browup", 0), -0.90]),
                          np.array([sx * 0.62, 0.24 + 0.08 * prm.get("browup", 0), -0.72]), 0.085)
        closer = brow < d
        d = smin(d, brow, 0.04)
        mat = np.where(closer & (d < 0.06), MAT_BROW, mat)

    # ---- THE MUSTACHE (volume + strand field handled in material) ----
    st = np.minimum(
        sd_capsule(hp, np.array([-0.05, -0.62, -0.98]), np.array([-0.55, -0.72, -0.72]), 0.16),
        sd_capsule(hp, np.array([0.05, -0.62, -0.98]), np.array([0.55, -0.72, -0.72]), 0.16))
    st = smin(st, sd_capsule(hp, np.array([-0.5, -0.72, -0.74]), np.array([-0.72, -0.86, -0.55]), 0.11), 0.08)
    st = smin(st, sd_capsule(hp, np.array([0.5, -0.72, -0.74]), np.array([0.72, -0.86, -0.55]), 0.11), 0.08)
    # subtle strand ripple
    st = st + 0.0045 * np.sin(hp[..., 0] * 52 + hp[..., 1] * 14) * np.clip(1 - np.abs(st) * 6, 0, 1)
    closer = st < d
    d = smin(d, st, 0.05)
    mat = np.where(closer & (d < 0.08), MAT_STACHE, mat)

    # ---- sideburns / back hair under cap ----
    hair = np.minimum(
        sd_ellip(hp, np.array([-0.92, -0.30, -0.02]), np.array([0.16, 0.34, 0.30])),
        sd_ellip(hp, np.array([0.92, -0.30, -0.02]), np.array([0.16, 0.34, 0.30])))
    hair = np.minimum(hair, sd_ellip(hp, np.array([0, -0.10, 0.75]), np.array([0.85, 0.75, 0.55])))
    closer = hair < d
    d = smin(d, hair, 0.06)
    mat = np.where(closer & (d < 0.08), MAT_HAIR, mat)

    # ---- cap (fabric) ----
    dome = sd_sphere(hp, np.array([0, 0.72, 0.10]), 1.12)
    dome = smax(dome, -(hp[..., 1] - 0.42), 0.10)  # only above
    # panel seams: shallow grooves
    seam_a = np.abs(np.arctan2(hp[..., 0], -(hp[..., 2] - 0.1)))
    groove = np.minimum(np.abs(seam_a - 0.55), np.abs(seam_a + 0.55))
    dome = dome + 0.008 * np.clip(1 - groove * 14, 0, 1)
    brim = sd_torus(hp, np.array([0, 0.44, -0.72]), 0.52, 0.16)
    brim = smax(brim, hp[..., 1] - 0.50, 0.05)
    brim = smax(brim, -(hp[..., 1] - 0.34), 0.05)
    capd = smin(dome, brim, 0.09)
    closer = capd < d
    d = smin(d, capd, 0.03)
    mat = np.where(closer, MAT_CAP, mat)

    # ---- bust: shoulders, shirt, straps, buttons ----
    body = sd_ellip(p, np.array([0, -2.75, 0.15]), np.array([1.9, 1.35, 1.1]))
    closer = body < d
    d = smin(d, body, 0.15)
    mat = np.where(closer, MAT_SHIRT, mat)
    for sx in (-1, 1):
        strap = sd_rbox(p, np.array([sx * 0.62, -2.05, -0.78]), np.array([0.22, 0.65, 0.05]), 0.03)
        closer = strap < d
        d = np.minimum(d, strap)
        mat = np.where(closer, MAT_STRAP, mat)
        btn = sd_sphere(p, np.array([sx * 0.62, -1.62, -0.90]), 0.11)
        closer = btn < d
        d = np.minimum(d, btn)
        mat = np.where(closer, MAT_BUTTON, mat)

    # ---- backdrop ----
    back = -(p[..., 2] - 4.5)
    closer = back < d
    d = np.minimum(d, back)
    mat = np.where(closer, MAT_BACK, mat)
    return d, mat


# ---------------- march / shade ----------------

SUN = np.array([-0.55, 0.55, -0.62])
SUN /= np.linalg.norm(SUN)
FILL = np.array([0.7, -0.1, -0.7])
FILL /= np.linalg.norm(FILL)
RIM = np.array([0.35, 0.4, 0.85])
RIM /= np.linalg.norm(RIM)


def march(ro, rd, prm, max_steps=110, tmax=14.0):
    N = rd.shape[0]
    t = np.zeros(N)
    hit = np.zeros(N, dtype=bool)
    alive = np.ones(N, dtype=bool)
    for _ in range(max_steps):
        p = ro + rd * t[:, None]
        dist, _ = scene(p[alive], prm)
        d_full = np.full(N, 1e9)
        d_full[alive] = dist
        newly = alive & (d_full < 0.004)
        hit |= newly
        t = np.where(alive, t + np.clip(d_full, 0.004, 0.5) * 0.9, t)
        alive = alive & ~newly & (t < tmax)
        if not alive.any():
            break
    return t, hit


def normals(p, prm, eps=0.004):
    d0, _ = scene(p, prm)
    n = np.zeros_like(p)
    for i in range(3):
        q = p.copy()
        q[:, i] += eps
        d1, _ = scene(q, prm)
        n[:, i] = d1 - d0
    ln = np.linalg.norm(n, axis=1, keepdims=True)
    return n / np.maximum(ln, 1e-9)


def soft_shadow(p, ldir, prm, k=10.0, steps=20):
    t = np.full(p.shape[0], 0.06)
    res = np.ones(p.shape[0])
    for _ in range(steps):
        q = p + ldir * t[:, None]
        d, _ = scene(q, prm)
        res = np.minimum(res, np.clip(k * d / t, 0, 1))
        t += np.clip(d, 0.02, 0.3)
        if (t > 5).all():
            break
    return np.clip(res, 0, 1)


def ambient_occ(p, n, prm):
    occ = 0.0
    for i in range(1, 6):
        h = 0.03 + 0.12 * i / 5
        d, _ = scene(p + n * h, prm)
        occ += (h - d) * (0.75 ** i)
    return np.clip(1 - 1.6 * occ, 0.15, 1.0)


# ---------------- materials ----------------

SKIN_BASE = np.array([0.90, 0.60, 0.44])
SKIN_RED = np.array([0.80, 0.38, 0.32])
LIP_COL = np.array([0.80, 0.50, 0.42])
STACHE_COL = np.array([0.16, 0.10, 0.07])
HAIR_COL = np.array([0.19, 0.12, 0.08])
CAP_COL = np.array([0.95, 0.40, 0.10])
SHIRT_COL = np.array([0.78, 0.42, 0.31])
STRAP_COL = np.array([0.30, 0.21, 0.16])
TEETH_COL = np.array([0.88, 0.84, 0.74])
MOUTH_COL = np.array([0.25, 0.08, 0.08])
BACK_COL = np.array([0.10, 0.095, 0.11])


def material_props(p, n, mat, prm):
    """Returns albedo (N,3), roughness (N,), spec_gain (N,), bump-perturbed n."""
    N = p.shape[0]
    alb = np.zeros((N, 3))
    rough = np.full(N, 60.0)     # phong exponent
    spec = np.full(N, 0.25)
    n2 = n.copy()

    skin = (mat == MAT_SKIN) | (mat == MAT_LIP)
    if skin.any():
        sp = p[skin]
        # blotchy subdermal redness
        blotch = fbm(sp[:, 0] * 3.1, sp[:, 1] * 3.1, sp[:, 2] * 3.1, 3)
        base = SKIN_BASE[None, :] * (0.92 + 0.16 * blotch[:, None] - 0.08)
        redness = np.clip(fbm(sp[:, 0] * 5.7 + 9, sp[:, 1] * 5.7, sp[:, 2] * 5.7, 2) - 0.45, 0, 1)
        # red concentrates on nose/cheeks
        nose_cheek = np.exp(-((sp[:, 1] + 0.3) ** 2) * 2.2) * np.clip(-sp[:, 2] - 0.4, 0, 1)
        base = base * (1 - (redness * 0.55 + nose_cheek * 0.35)[:, None]) \
            + SKIN_RED[None, :] * (redness * 0.55 + nose_cheek * 0.35)[:, None]
        # pores: high-freq speckle
        pores = vnoise(sp[:, 0] * 60, sp[:, 1] * 60, sp[:, 2] * 60)
        base *= (0.90 + 0.13 * pores)[:, None]
        # stubble on jaw/upper-lip periphery
        stub_zone = np.clip((-sp[:, 1] - 0.55), 0, 1) * np.clip((-sp[:, 2] - 0.15), 0, 1) * 1.4
        stub = (vnoise(sp[:, 0] * 90, sp[:, 1] * 90, sp[:, 2] * 90) > 0.62) * np.clip(stub_zone, 0, 0.8)
        base *= (1 - 0.35 * stub)[:, None]
        alb[skin] = base
        # oily zones: nose tip, forehead
        oily = np.exp(-np.linalg.norm(sp - np.array([0, -0.28, -1.02]), axis=1) ** 2 * 3.5) \
            + np.exp(-((sp[:, 1] - 0.45) ** 2) * 3.0) * 0.6
        rough[skin] = 90.0 + 160.0 * np.clip(oily, 0, 1)
        spec[skin] = 0.18 + 0.5 * np.clip(oily, 0, 1)
        # pore bump
        eps = 0.012
        bx = vnoise(sp[:, 0] * 55 + eps, sp[:, 1] * 55, sp[:, 2] * 55) - pores
        by = vnoise(sp[:, 0] * 55, sp[:, 1] * 55 + eps, sp[:, 2] * 55) - pores
        bz = vnoise(sp[:, 0] * 55, sp[:, 1] * 55, sp[:, 2] * 55 + eps) - pores
        n2[skin] += np.stack([bx, by, bz], axis=1) * 0.55
    lip = mat == MAT_LIP
    if lip.any():
        lp = p[lip]
        cracks = vnoise(lp[:, 0] * 90, lp[:, 1] * 30, lp[:, 2] * 90)
        alb[lip] = LIP_COL[None, :] * (0.85 + 0.2 * cracks[:, None])
        rough[lip] = 190.0
        spec[lip] = 0.55

    for m_, col, rg, sg, strand_axis in ((MAT_STACHE, STACHE_COL, 34.0, 0.5, 0),
                                         (MAT_BROW, STACHE_COL * 1.25, 34.0, 0.4, 0),
                                         (MAT_HAIR, HAIR_COL, 40.0, 0.35, 1)):
        msk = mat == m_
        if msk.any():
            hp_ = p[msk]
            strands = vnoise(hp_[:, 0] * 24, hp_[:, 1] * 130, hp_[:, 2] * 24) if strand_axis \
                else vnoise(hp_[:, 0] * 130, hp_[:, 1] * 24, hp_[:, 2] * 24)
            alb[msk] = col[None, :] * (0.55 + 0.9 * strands[:, None])
            rough[msk] = rg
            spec[msk] = sg

    capm = mat == MAT_CAP
    if capm.any():
        cp = p[capm]
        # twill weave
        weave = (np.sin(cp[:, 0] * 210 + cp[:, 1] * 90) * np.sin(cp[:, 1] * 210 - cp[:, 0] * 90))
        base = CAP_COL[None, :] * (0.90 + 0.10 * weave[:, None]) \
            * (0.85 + 0.25 * fbm(cp[:, 0] * 6, cp[:, 1] * 6, cp[:, 2] * 6, 2)[:, None])
        # emblem decal: white disc + coral starburst on front of dome
        ec = np.array([0, 0.78, -0.95])
        er = np.linalg.norm(cp - ec, axis=1)
        in_disc = er < 0.26
        ang = np.arctan2(cp[:, 1] - ec[1], cp[:, 0] - ec[0])
        burst = (np.abs(np.sin(ang * 2)) > 0.86) | (np.abs(np.cos(ang * 2)) > 0.86)
        star = in_disc & (er < 0.20) & burst
        base[in_disc] = np.array([0.93, 0.91, 0.86])
        base[star] = np.array([0.85, 0.40, 0.18])
        alb[capm] = base
        rough[capm] = 26.0
        spec[capm] = 0.12

    for m_, col, rg, sg in ((MAT_SHIRT, SHIRT_COL, 20.0, 0.08),
                            (MAT_STRAP, STRAP_COL, 30.0, 0.15),
                            (MAT_MOUTH, MOUTH_COL, 40.0, 0.2),
                            (MAT_BACK, BACK_COL, 10.0, 0.0)):
        msk = mat == m_
        if msk.any():
            pp = p[msk]
            tex = fbm(pp[:, 0] * 22, pp[:, 1] * 22, pp[:, 2] * 22, 2)
            alb[msk] = col[None, :] * (0.85 + 0.3 * tex[:, None])
            rough[msk] = rg
            spec[msk] = sg

    teeth = mat == MAT_TEETH
    if teeth.any():
        tp = p[teeth]
        gaps = np.clip(np.abs(np.sin(tp[:, 0] * 34)) ** 0.5, 0.55, 1)
        alb[teeth] = TEETH_COL[None, :] * gaps[:, None]
        rough[teeth] = 240.0
        spec[teeth] = 0.7

    btn = mat == MAT_BUTTON
    if btn.any():
        alb[btn] = np.array([0.85, 0.72, 0.30])
        rough[btn] = 300.0
        spec[btn] = 0.9

    eye = mat == MAT_EYE
    if eye.any():
        ep = p[eye]
        alb_e = np.zeros((eye.sum(), 3))
        for sx in (-1, 1):
            ec = np.array([sx * 0.40, 0.02, -0.84])
            rel = ep - ec
            side = np.abs(rel[:, 0]) < 0.5  # both handled; mask by nearest
            gaze = np.array([prm.get("eyex", 0.0) * 0.25 + 0.0, prm.get("eyey", 0.0) * 0.2, -1.0])
            gaze = gaze / np.linalg.norm(gaze)
            cosang = (rel / np.maximum(np.linalg.norm(rel, axis=1, keepdims=True), 1e-9)) @ gaze
            iris = cosang > 0.86
            pupil = cosang > 0.975
            sclera = ~iris
            veins = vnoise(ep[:, 0] * 40, ep[:, 1] * 40, ep[:, 2] * 40)
            col = np.where(sclera[:, None],
                           np.array([0.92, 0.88, 0.84])[None, :] * (0.9 + 0.1 * veins[:, None])
                           - np.array([0, 0.25, 0.3])[None, :] * np.clip(veins - 0.62, 0, 1)[:, None],
                           np.array([0.35, 0.22, 0.12])[None, :]
                           * (0.6 + 0.8 * vnoise(ep[:, 0] * 90, ep[:, 1] * 90, ep[:, 2] * 90)[:, None]))
            col = np.where(pupil[:, None], np.array([0.03, 0.02, 0.02])[None, :], col)
            near = np.abs(rel[:, 0]) < 0.45
            alb_e = np.where(near[:, None], col, alb_e)
        alb[eye] = alb_e
        rough[eye] = 420.0
        spec[eye] = 1.0

    ln = np.linalg.norm(n2, axis=1, keepdims=True)
    return alb, rough, spec, n2 / np.maximum(ln, 1e-9)


# ---------------- shading ----------------

KEY_COL = np.array([1.0, 0.90, 0.78]) * 1.4
FILL_COL = np.array([0.55, 0.65, 0.85]) * 0.35
RIM_COL = np.array([1.0, 0.75, 0.55]) * 0.9


def shade(p, rd, mat, prm):
    n = normals(p, prm)
    alb, rough, spec, nb = material_props(p, n, mat, prm)
    skinlike = (mat == MAT_SKIN) | (mat == MAT_LIP) | (mat == MAT_STACHE)

    sh = soft_shadow(p + n * 0.02, SUN, prm)
    ao = ambient_occ(p, n, prm)

    ndl = np.clip((nb @ SUN), 0, 1)
    # subsurface: wrap + red-shifted terminator on skin
    wrap = np.clip((nb @ SUN) * 0.5 + 0.5, 0, 1) ** 1.4
    band = np.clip(1 - np.abs((nb @ SUN)), 0, 1) ** 2.5
    diff_key = np.where(skinlike, wrap, ndl) * sh
    col = alb * (diff_key[:, None] * KEY_COL[None, :])
    col += alb * np.where(skinlike, band * sh * 0.35, 0)[:, None] * np.array([0.9, 0.25, 0.15])[None, :]
    ndf = np.clip((nb @ FILL), 0, 1)
    col += alb * ndf[:, None] * FILL_COL[None, :]
    ndr = np.clip((nb @ RIM), 0, 1) ** 3
    col += ndr[:, None] * RIM_COL[None, :] * 0.7
    col += alb * 0.16 * ao[:, None]                     # ambient
    # spec (blinn-ish)
    h = SUN - rd
    h = h / np.maximum(np.linalg.norm(h, axis=1, keepdims=True), 1e-9)
    sp = np.clip((nb * h).sum(1), 0, 1) ** rough * spec * sh
    col += sp[:, None] * KEY_COL[None, :]
    h2 = RIM - rd
    h2 /= np.maximum(np.linalg.norm(h2, axis=1, keepdims=True), 1e-9)
    sp2 = np.clip((nb * h2).sum(1), 0, 1) ** (rough * 0.7) * spec * 0.5
    col += sp2[:, None] * RIM_COL[None, :]
    col *= ao[:, None]
    return col


def render_frame(prm, W=640, H=360, cam_pos=(0.0, -0.35, -4.6), cam_tgt=(0, -0.35, 0),
                 fov=26.0, focus=3.6):
    ro = np.array(cam_pos, dtype=np.float64)
    tgt = np.array(cam_tgt, dtype=np.float64)
    fwd = tgt - ro
    fwd /= np.linalg.norm(fwd)
    right = np.cross(fwd, (0, 1, 0))
    right /= np.linalg.norm(right)
    up = np.cross(right, fwd)
    f = 0.5 / np.tan(np.radians(fov) / 2)

    xs = (np.arange(W) + 0.5) / W - 0.5
    ys = -((np.arange(H) + 0.5) / H - 0.5) * (H / W)
    gx, gy = np.meshgrid(xs, ys)
    rd = (gx[..., None] * right + gy[..., None] * up + f * fwd)
    rd = rd.reshape(-1, 3)
    rd /= np.linalg.norm(rd, axis=1, keepdims=True)
    ro_all = np.tile(ro, (rd.shape[0], 1))

    t, hit = march(ro_all, rd, prm)
    p = ro_all + rd * t[:, None]
    _, mat = scene(p, prm)
    col = np.zeros((rd.shape[0], 3))
    if hit.any():
        col[hit] = shade(p[hit], rd[hit], mat[hit], prm)
    # background: dark studio falloff
    bg = BACK_COL[None, :] * (0.7 + 0.5 * np.clip(1 - np.abs(gx.reshape(-1)) * 2.2, 0, 1)
                              * np.clip(1 - np.abs(gy.reshape(-1) + 0.1) * 2.2, 0, 1))[:, None]
    col = np.where(hit[:, None], col, bg)
    img = col.reshape(H, W, 3)
    depth = t.reshape(H, W)
    return img, depth


# ---------------- photographic post ----------------

def box_blur(img, r):
    if r < 1:
        return img
    k = 2 * int(r) + 1
    c = np.cumsum(np.pad(img, ((int(r) + 1, int(r)), (0, 0), (0, 0)), mode="edge"), axis=0)
    img = (c[k:] - c[:-k]) / k
    c = np.cumsum(np.pad(img, ((0, 0), (int(r) + 1, int(r)), (0, 0)), mode="edge"), axis=1)
    return (c[:, k:] - c[:, :-k]) / k


def post(img, depth, focus=3.6, grain_seed=0):
    H_, W_ = img.shape[:2]
    # depth of field: 3-level gather
    blur1 = box_blur(img, max(1, W_ // 320))
    blur2 = box_blur(img, max(2, W_ // 110))
    coc = np.clip(np.abs(depth - focus) * 1.1, 0, 1.6)
    m1 = np.clip(coc, 0, 1)[..., None]
    m2 = np.clip(coc - 0.7, 0, 1)[..., None]
    out = img * (1 - m1) + blur1 * m1
    out = out * (1 - m2) + blur2 * m2
    # bloom
    bright = np.clip(out - 0.75, 0, None)
    out = out + box_blur(bright, max(2, W_ // 90)) * 0.6
    # chromatic aberration
    yy, xx = np.mgrid[0:H_, 0:W_]
    cx, cy = W_ / 2, H_ / 2
    r2 = (((xx - cx) / cx) ** 2 + ((yy - cy) / cy) ** 2)
    shift = (r2 * 2.2).astype(np.int32)
    out_r = out[..., 0]
    out_b = out[..., 2]
    xr = np.clip(xx + shift, 0, W_ - 1)
    xb = np.clip(xx - shift, 0, W_ - 1)
    out[..., 0] = out_r[yy, xr]
    out[..., 2] = out_b[yy, xb]
    # vignette + grade + grain
    out *= (1 - 0.42 * r2[..., None] ** 1.2)
    out = out / (1 + out * 0.55)                       # filmic-ish rolloff
    out = out ** (1 / 1.9)                             # gamma
    out = out * np.array([1.04, 1.0, 0.94])[None, None, :]  # warm grade
    rng = np.random.default_rng(grain_seed)
    out += rng.normal(0, 0.014, out.shape)
    return np.clip(out * 255, 0, 255).astype(np.uint8)
