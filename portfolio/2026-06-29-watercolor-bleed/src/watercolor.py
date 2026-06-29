"""Wet-on-wet watercolour / ink-bleed on paper.

A genuinely new axis (FRONTIERS: physical-media simulation — never done):
  * PIGMENT IS SUBTRACTIVE. Light passes through washes and is absorbed
    (Beer-Lambert: T = exp(-density * k_channel)). Overlapping washes MULTIPLY,
    so they darken and shift hue naturally — the opposite of every prior
    additive-glow-on-black piece. The ground is warm PAPER, not black.
  * EDGE-BLOOMING. Real watercolour migrates pigment to the drying boundary of
    the wet region, leaving a dark "cauliflower" rim and a paler centre. Modelled
    as a boundary ring = relu(wet - blur(wet)).
  * GRANULATION. Pigment settles into the paper tooth — density is modulated by
    fine paper-grain noise, so washes look grainy, not flat.
  * NEGATIVE SPACE + OFF-CENTRE. Three washes on a loose diagonal; most of the
    sheet is left untouched paper. Breaks the logged dusk-gradient / centred habit.

Pure numpy + the shared stdlib PNG writer. No additive accumulation anywhere.
"""
import numpy as np
from pnglib import write_png

H = W = 1000
rng = np.random.default_rng(7)

ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


# ---- fast separable box blur (×3 ≈ gaussian), O(n), no scipy ----
def _box1d(a, r, axis):
    if r < 1:
        return a
    k = 2 * r + 1
    cs = np.cumsum(a, axis=axis)
    cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    n = a.shape[axis]
    lo = np.clip(np.arange(n) - r, 0, n)
    hi = np.clip(np.arange(n) + r + 1, 0, n)
    sl_hi = np.take(cs, hi, axis=axis)
    sl_lo = np.take(cs, lo, axis=axis)
    cnt = (hi - lo).astype(np.float64)
    shape = [1, 1]
    shape[axis] = n
    return (sl_hi - sl_lo) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0)
        a = _box1d(a, r, 1)
    return a


def value_noise(scale, seed):
    """Smooth low-freq noise in [0,1] via upsampled-and-blurred white noise."""
    g = np.random.default_rng(seed).random((scale, scale))
    yi = (ys / H * (scale - 1)).astype(int)
    xi = (xs / W * (scale - 1)).astype(int)
    fine = g[yi, xi]
    return blur(fine, max(1, W // scale // 2))


def fbm(seed, octaves=5):
    out = np.zeros((H, W))
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        out += amp * value_noise(4 * 2 ** o, seed + o)
        tot += amp
        amp *= 0.5
    out /= tot
    return out


# ---- paper ground: warm off-white with fibre tooth + a faint deckle vignette ----
paper_rgb = np.array([248, 243, 231], np.float64)        # warm rag paper
fibre = fbm(101, 6)
grain = value_noise(W // 3, 202)                          # fine tooth for granulation
tooth = 0.5 + 0.5 * grain
paper = np.ones((H, W, 3)) * paper_rgb / 255.0
paper *= (1.0 - 0.05 * (fibre - 0.5)[..., None])          # subtle mottle
# faint cool shadow in the deep corners (paper lying on a surface), very gentle
vign = ((nx - 0.5) ** 2 + (ny - 0.5) ** 2)
paper *= (1.0 - 0.04 * np.clip(vign * 2 - 0.4, 0, 1))[..., None]

img = paper.copy()


def wet_blob(cx, cy, rad, wob_seed, wob=0.34):
    """Organic wet region: a radial mask whose edge is perturbed by angular noise."""
    dx, dy = nx - cx, ny - cy
    ang = np.arctan2(dy, dx)
    r = np.sqrt(dx * dx + dy * dy)
    rg = np.random.default_rng(wob_seed)
    # a few angular harmonics → lobed, leaf/petal-like boundary
    edge = rad * (1.0 + wob * sum(
        (0.6 ** k) * np.sin((k + 2) * ang + rg.uniform(0, 6.28)) for k in range(4)))
    m = np.clip((edge - r) / 0.02, 0.0, 1.0)               # soft 1-px-ish falloff
    m *= (0.85 + 0.15 * fbm(wob_seed + 50, 4))             # ragged interior wetness
    return m


def lay_wash(cx, cy, rad, k_absorb, strength, seed, edge_gain=1.7):
    """Deposit one subtractive wash. k_absorb: per-channel absorption (the pigment)."""
    wet = wet_blob(cx, cy, rad, seed)
    # pigment density: a soft interior + the blooming boundary ring
    interior = blur(wet, int(W * rad * 0.08)) * wet
    ring = np.clip(wet - blur(wet, max(2, int(W * rad * 0.05))), 0, 1)
    dens = strength * (0.55 * interior + edge_gain * ring)
    # back-runs: a couple of secondary blooms inside, where water pooled
    rg = np.random.default_rng(seed + 9)
    for _ in range(2):
        bx, by = cx + rg.uniform(-rad, rad) * 0.5, cy + rg.uniform(-rad, rad) * 0.5
        bwet = wet_blob(bx, by, rad * rg.uniform(0.25, 0.45), int(rg.integers(1e6)))
        bwet *= wet  # only where the sheet is already wet
        dens += strength * 0.9 * np.clip(bwet - blur(bwet, max(2, int(W * rad * 0.03))), 0, 1)
    # granulation: pigment settles into the tooth
    dens *= (0.7 + 0.6 * tooth)
    dens = np.clip(dens, 0, None)
    # SUBTRACTIVE compositing — multiply the sheet by transmittance
    trans = np.exp(-dens[..., None] * k_absorb[None, None, :])
    img[:] = img * trans


# Pigment absorption coefficients (earth palette). Higher k = absorbs that channel
# more → leaves the complementary hue. Tuned so washes read as real pigments.
RAW_SIENNA  = np.array([0.35, 1.05, 2.4])    # absorbs blue/green → warm ochre
PAYNES_GREY = np.array([1.7, 1.35, 1.0])     # absorbs all, red most → cool slate
SAP_GREEN   = np.array([1.5, 0.7, 1.9])      # absorbs red+blue → muted olive
BURNT_UMBER = np.array([1.0, 1.7, 2.6])      # deep warm brown

# Off-centre diagonal composition; large untouched paper margins (negative space).
lay_wash(0.30, 0.28, 0.20, RAW_SIENNA,  1.15, seed=11, edge_gain=1.9)
lay_wash(0.40, 0.40, 0.16, SAP_GREEN,   0.95, seed=23, edge_gain=1.6)
lay_wash(0.62, 0.66, 0.235, PAYNES_GREY, 1.25, seed=31, edge_gain=2.1)
lay_wash(0.70, 0.60, 0.12, BURNT_UMBER, 1.0,  seed=44, edge_gain=1.7)
# a tiny far accent for asymmetric tension (rule-of-thirds, lower-left void answered)
lay_wash(0.18, 0.78, 0.055, PAYNES_GREY, 1.1, seed=57, edge_gain=2.3)

# final paper-tooth bite over everything (very slight), then to 8-bit
img *= (0.985 + 0.015 * tooth)[..., None]
out = np.clip(img * 255.0 + 0.5, 0, 255).astype(np.uint8)
write_png("../images/watercolor.png", out)
print("wrote images/watercolor.png", out.shape)
