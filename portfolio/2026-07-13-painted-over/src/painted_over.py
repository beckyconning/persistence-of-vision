"""PAINTED OVER — five studies in occlusion.

One luminous scene — a reload-cue demo: three countdown rings (cyan, amber, red)
around a crosshair over a dusk field — rendered five ways it can exist and not
be seen. Each panel is one real bug from a real day of engine work:

  I.   State Guard      the draw call returned early; the scene at 2% luminance
  II.  Under the GUI    painted every frame, then a settings panel painted over it
  III. Wrong Matrix     drawn through a near-singular transform; the world as a smear
  IV.  Unbound Texture  right geometry, wrong memory: gui skin in the rings,
                        the notexture checker where the crosshair should be
  V.   Overlay Pass     drawn after everything else; the ready flash fires

Pure numpy. No fonts, no assets — geometry, gradients, and noise only.
"""
import numpy as np
from pnglib import write_png, ramp
from apnglib import write_apng

W, H = 1200, 750
RNG = np.random.default_rng(713)

CX, CY = 0.5, 0.44          # ring/crosshair centre (normalised)
HORIZON = 0.66

CYAN  = np.array([0.30, 0.92, 1.00])
AMBER = np.array([1.00, 0.72, 0.22])
RED   = np.array([1.00, 0.30, 0.24])
GREEN = np.array([0.35, 1.00, 0.50])


def grids(w=W, h=H):
    y, x = np.mgrid[0:h, 0:w]
    return x / w, y / h


def gauss_band(d, r, width):
    return np.exp(-((d - r) / width) ** 2)


def scene(w=W, h=H, beat=0.0, flash=0.0, ghost=1.0):
    """The demo scene. beat in [0,1) subtly breathes the rings; flash in [0,1]
    fires the green ready flash; ghost scales overall presence."""
    x, y = grids(w, h)
    aspect = w / h
    img = np.zeros((h, w, 3))

    # dusk sky -> ember horizon -> dark ground
    sky_t = np.clip(y / HORIZON, 0, 1)
    sky = ramp(sky_t, [(0.05, 0.05, 0.14), (0.10, 0.07, 0.20),
                       (0.28, 0.10, 0.22), (0.75, 0.32, 0.13)])
    ground_t = np.clip((y - HORIZON) / (1 - HORIZON), 0, 1)
    ground = ramp(ground_t, [(0.10, 0.05, 0.06), (0.03, 0.02, 0.04)])
    img += np.where((y < HORIZON)[..., None], sky, ground)

    # sparse stars in the upper third (own rng: static across animation frames)
    star_rng = np.random.default_rng(42)
    stars = (star_rng.random((h, w)) > 0.9994) & (y < 0.35)
    star_img = np.zeros((h, w))
    star_img[stars] = star_rng.random(stars.sum()) * 0.8 + 0.2
    k = np.array([[0.05, 0.2, 0.05], [0.2, 1.0, 0.2], [0.05, 0.2, 0.05]])
    pad = np.pad(star_img, 1)
    soft = sum(k[i, j] * pad[i:i + h, j:j + w] for i in range(3) for j in range(3))
    img += soft[..., None] * np.array([0.9, 0.95, 1.0]) * (1 - sky_t[..., None]) * 0.9

    # low sun bloom on the horizon, off-centre left
    dsun = np.hypot((x - 0.30) * aspect, (y - HORIZON) * 1.6)
    img += np.outer(np.ones(1), AMBER).reshape(1, 1, 3) * \
        (np.exp(-(dsun / 0.16) ** 2) * 0.55 + np.exp(-(dsun / 0.5) ** 2) * 0.18)[..., None] * \
        ramp(np.clip(dsun, 0, 1), [(1.0, 0.72, 0.3), (1.0, 0.4, 0.2)]) / np.array([1.0, 0.72, 0.3])

    # the three countdown rings (colour journey), breathing on the beat
    d = np.hypot((x - CX) * aspect, y - CY)
    pop = 1.0 + 0.035 * np.sin(beat * 2 * np.pi)
    for r, col, wdt, amp in [(0.075, CYAN, 0.006, 1.00),
                             (0.135, AMBER, 0.007, 0.85),
                             (0.21, RED, 0.009, 0.78)]:
        rr = r * pop
        band = gauss_band(d, rr, wdt) * amp
        halo = gauss_band(d, rr, wdt * 6) * amp * 0.22 + gauss_band(d, rr, wdt * 16) * amp * 0.08
        img += (band + halo)[..., None] * col

    # crosshair: thin plus, additive white
    px = np.abs(x - CX) * aspect
    py = np.abs(y - CY)
    arm, thick = 0.020, 0.0016
    ch = (((px < arm) & (py < thick)) | ((py < arm) & (px < thick))).astype(float)
    gap = (px < 0.004) & (py < 0.004)
    ch[gap] = 0
    chsoft = ch.copy()
    padc = np.pad(ch, 1)
    chsoft = sum(k[i, j] * padc[i:i + h, j:j + w] for i in range(3) for j in range(3))
    img += np.clip(chsoft, 0, 1.2)[..., None] * np.array([0.95, 0.98, 1.0])

    # ready flash (panel V / animation payoff)
    if flash > 0:
        fr = 0.075 + 0.16 * flash
        img += (gauss_band(d, fr, 0.012 + 0.02 * flash) * (1 - flash) * 1.2)[..., None] * GREEN
        img += (np.exp(-(d / 0.10) ** 2) * (1 - flash) * 0.30)[..., None] * GREEN

    # water-ish reflection of the rings below the horizon
    yr = HORIZON + (HORIZON - y)                       # mirrored y
    ripple = 0.004 * np.sin(y * 260) * (y > HORIZON)
    dref = np.hypot((x - CX + ripple) * aspect, yr - CY)
    refl = np.zeros((h, w, 3))
    for r, col, wdt, amp in [(0.075, CYAN, 0.010, 0.35),
                             (0.135, AMBER, 0.012, 0.28),
                             (0.21, RED, 0.014, 0.22)]:
        refl += (gauss_band(dref, r * pop, wdt) * amp)[..., None] * col
    img += refl * ((y > HORIZON) * np.clip((y - HORIZON) * 6, 0, 1) *
                   np.clip(1 - (y - HORIZON) * 2.2, 0, 1))[..., None]

    # vignette + grain
    dv = np.hypot((x - 0.5) * 1.1, (y - 0.5))
    img *= (1 - 0.35 * np.clip(dv - 0.35, 0, 1) ** 1.5)[..., None]
    img += (RNG.random((h, w, 1)) - 0.5) * 0.012
    return np.clip(img * ghost, 0, 1)


# ---------- panel II: the settings panel ----------
def gui_panel(img, slide=1.0):
    """Paint an opaque settings window over the scene. slide in [0,1]: 1 = fully in."""
    h, w = img.shape[:2]
    x, y = grids(w, h)
    out = img.copy()
    # panel rect (normalised), slides up from below the frame
    x0, x1 = 0.38, 0.62
    y1 = 0.885
    y0 = y1 - 0.76 * slide
    inpanel = (x > x0) & (x < x1) & (y > y0) & (y < y1)

    # drop shadow
    sh = (x > x0 + 0.008) & (x < x1 + 0.012) & (y > y0 + 0.012) & (y < y1 + 0.018) & ~inpanel
    out[sh] *= 0.45

    # skin: flat grey with plate noise + vertical shading
    noise = RNG.random((h, w)) * 0.05
    skin_v = 0.24 + 0.05 * (1 - (y - y0) / max(y1 - y0, 1e-6)) + noise
    skin = np.stack([skin_v * 0.98, skin_v, skin_v * 1.03], -1)
    out[inpanel] = skin[inpanel]

    # border: 2px light rim
    bw = 0.0035
    border = inpanel & (~((x > x0 + bw) & (x < x1 - bw) & (y > y0 + bw * 1.6) & (y < y1 - bw * 1.6)))
    out[border] = np.array([0.42, 0.43, 0.45])

    # header strip
    head = inpanel & (y < y0 + 0.055) & (y > y0 + bw * 1.6)
    out[head] = np.array([0.30, 0.31, 0.34])

    def bar(cx0, cx1, cy, ht, col):
        m = (x > cx0) & (x < cx1) & (np.abs(y - cy) < ht) & inpanel
        out[m] = col

    grey_txt = np.array([0.55, 0.56, 0.58])
    green = np.array([0.35, 0.75, 0.40])
    rows = np.linspace(y0 + 0.11, y1 - 0.10, 7)
    widths = [0.15, 0.11, 0.17, 0.09, 0.13, 0.16, 0.10]
    for i, (ry, rw) in enumerate(zip(rows, widths)):
        if y0 + 0.08 > ry:
            continue
        # radio dot
        dd = np.hypot((x - (x0 + 0.035)) * (w / h), y - ry)
        ring = (dd > 0.0065) & (dd < 0.0095)
        out[ring & inpanel] = grey_txt
        if i == 2:
            out[(dd < 0.005) & inpanel] = green
        # fake label bar
        bar(x0 + 0.06, x0 + 0.06 + rw, ry, 0.0055, grey_txt * (0.9 + 0.1 * (i % 2)))
    # a slider near the bottom
    sy = y1 - 0.055
    bar(x0 + 0.03, x1 - 0.03, sy, 0.0018, grey_txt * 0.8)
    dd = np.hypot((x - (x0 + 0.15)) * (w / h), y - sy)
    out[(dd < 0.007) & inpanel] = np.array([0.75, 0.76, 0.78])
    return out


# ---------- panel III: the wrong matrix ----------
def wrong_matrix(src, t=1.0):
    """Resample the scene through a matrix that collapses toward singular as t->1."""
    h, w = src.shape[:2]
    x, y = grids(w, h)
    # interpolate identity -> near-singular shear
    m00 = 1.0 + 1.9 * t
    m01 = 2.6 * t
    m10 = 0.0 + 0.012 * t
    m11 = 1.0 - 0.985 * t
    u = (x - CX) * m00 + (y - CY) * m01 + CX
    v = (x - CX) * m10 + (y - CY) * m11 + CY
    out = np.zeros_like(src)
    # slight per-channel offset: matrices break into rainbows
    for c, off in enumerate([-0.006 * t, 0.0, 0.006 * t]):
        uu = np.clip(((u + off) % 2), 0, 2)
        uu = np.where(uu > 1, 2 - uu, uu)          # mirror wrap
        vv = np.clip((v % 2), 0, 2)
        vv = np.where(vv > 1, 2 - vv, vv)
        xi = np.clip((uu * (w - 1)).astype(int), 0, w - 1)
        yi = np.clip((vv * (h - 1)).astype(int), 0, h - 1)
        out[..., c] = src[yi, xi, c]
    # the degenerate axis glows: energy has nowhere to go
    return np.clip(out * (1.0 + 0.20 * t), 0, 1)


# ---------- panel IV: the unbound texture ----------
def gui_skin_tex(w=W, h=H):
    """What the gui pass left bound: a riveted grey plate, tiled too small."""
    x, y = grids(w, h)
    tile = 0.045
    u, v = (x % tile) / tile, (y % tile) / tile
    val = 0.30 + 0.06 * np.sin(u * np.pi) * np.sin(v * np.pi) + RNG.random((h, w)) * 0.07
    rivet = (np.hypot(u - 0.5, v - 0.5) < 0.10).astype(float) * 0.12
    seam = ((u < 0.03) | (v < 0.03)).astype(float) * -0.08
    g = np.clip(val + rivet + seam, 0, 1)
    return np.stack([g * 0.98, g, g * 1.04], -1)


def notexture_checker(w=W, h=H, cells=9):
    x, y = grids(w, h)
    cx = (x * w / 14).astype(int)
    cy = (y * h / 14 * (h / w) * 1.6).astype(int)
    chk = ((cx + cy) % 2).astype(float)
    mag = np.array([1.0, 0.0, 0.9])
    blk = np.array([0.05, 0.0, 0.05])
    return chk[..., None] * mag + (1 - chk[..., None]) * blk


def unbound_texture(w=W, h=H):
    x, y = grids(w, h)
    aspect = w / h
    # keep the sky (the world was fine; only OUR draws sampled garbage)
    img = scene(w, h, ghost=0.55)
    skin = gui_skin_tex(w, h)
    chk = notexture_checker(w, h)
    d = np.hypot((x - CX) * aspect, y - CY)
    # rings as HARD bands filled with mis-scaled gui skin (no glow: wrong sampler, flat result)
    for r, wdt in [(0.075, 0.012), (0.135, 0.013), (0.21, 0.014)]:
        band = np.abs(d - r) < wdt
        img[band] = skin[band]
    # the crosshair: a solid quad of notexture checker (the corrupted box)
    box = (np.abs(x - CX) * aspect < 0.026) & (np.abs(y - CY) < 0.026)
    img[box] = chk[box]
    # faint seam highlight so the box reads as a quad someone MEANT to draw
    edge = box & ~((np.abs(x - CX) * aspect < 0.024) & (np.abs(y - CY) < 0.024))
    img[edge] = np.array([1.0, 0.35, 0.95])
    return np.clip(img, 0, 1)


def to8(img):
    # gentle filmic-ish curve
    img = np.clip(img, 0, 1) ** (1 / 1.9)
    return (img * 255).astype(np.uint8)


if __name__ == "__main__":
    import os
    OUT = os.path.join(os.path.dirname(__file__), "..", "images")
    os.makedirs(OUT, exist_ok=True)

    base = scene()

    # I. State Guard — it returned before drawing (2% ghost + one thin rule)
    p1 = scene(ghost=0.015)
    yy = np.linspace(0, 1, H)[:, None]
    rule = np.exp(-((yy - HORIZON) / 0.0012) ** 2) * 0.10
    p1 += rule[..., None] * np.array([0.5, 0.52, 0.55]) * np.ones((H, W, 3))
    write_png(f"{OUT}/1-state-guard.png", to8(p1))

    # II. Under the GUI
    write_png(f"{OUT}/2-under-the-gui.png", to8(gui_panel(base)))

    # III. Wrong Matrix
    write_png(f"{OUT}/3-wrong-matrix.png", to8(wrong_matrix(base, 1.0)))

    # IV. Unbound Texture
    write_png(f"{OUT}/4-unbound-texture.png", to8(unbound_texture()))

    # V. Overlay Pass — drawn last, ready flash mid-fire
    write_png(f"{OUT}/5-overlay-pass.png", to8(scene(flash=0.45)))

    # contact sheet
    gap = np.full((H, 14, 3), 8, np.uint8)
    row = []
    for n in ["1-state-guard", "2-under-the-gui", "3-wrong-matrix", "4-unbound-texture", "5-overlay-pass"]:
        import zlib, struct  # noqa
    sheet = np.hstack([to8(p1), gap, to8(gui_panel(base)), gap, to8(wrong_matrix(base, 1.0)),
                       gap, to8(unbound_texture()), gap, to8(scene(flash=0.45))])
    write_png(f"{OUT}/0-contact-sheet.png", sheet)
    print("stills written")
