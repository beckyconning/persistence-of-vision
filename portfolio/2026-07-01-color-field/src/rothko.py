"""
Colour field — homage to Mark Rothko (the Seagram register).

Growth move (from FRONTIERS): a single LARGE unified composition — not a grid, not
a generative system, not a face — where COLOUR and light-from-within ARE the whole
subject. New lineage (colour-field / Rothko), and the first time colour interaction
(simultaneous contrast, glowing edges) carries the piece rather than decorating it.

The Rothko "glow" is craft, not a flat rectangle:
  • stacked soft-edged rectangles (feathered boundaries — smoothstep, no hard line),
  • light from WITHIN each field (centre slightly luminous, falling off to the edge),
  • scumble: low-frequency colour drift + fine grain so no region is dead-flat,
  • simultaneous contrast: a deep ground the floating fields vibrate against,
  • a breathing outer haze so the rectangles hover rather than sit.
"""
import os
import numpy as np
from pnglib import write_png

OUT = os.path.join(os.path.dirname(__file__), "..", "images")
W, H = 900, 1150
rng = np.random.default_rng(7)
yy, xx = np.mgrid[0:H, 0:W].astype(float)
u, v = xx / W, yy / H


def smooth(a, b, t):
    t = np.clip((t - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def vnoise(freq):
    g = rng.standard_normal((freq + 2, freq + 2))
    yv = np.linspace(0, freq, H)[:, None] * np.ones((1, W))
    xv = np.linspace(0, freq, W)[None, :] * np.ones((H, 1))
    x0, y0 = np.floor(xv).astype(int), np.floor(yv).astype(int)
    fx, fy = xv - x0, yv - y0
    sx, sy = fx * fx * (3 - 2 * fx), fy * fy * (3 - 2 * fy)
    a = g[y0, x0] * (1 - sx) + g[y0, x0 + 1] * sx
    b = g[y0 + 1, x0] * (1 - sx) + g[y0 + 1, x0 + 1] * sx
    return a * (1 - sy) + b * sy


def field(cx, cy, w, h, feather, col_edge, col_core):
    """A soft-edged luminous rectangle: mask feathered by `feather`, colour graded
    from edge→core so light seems to come from inside."""
    mx = smooth(cx - w / 2 - feather, cx - w / 2 + feather, u) * \
        (1 - smooth(cx + w / 2 - feather, cx + w / 2 + feather, u))
    my = smooth(cy - h / 2 - feather, cy - h / 2 + feather, v) * \
        (1 - smooth(cy + h / 2 - feather, cy + h / 2 + feather, v))
    mask = mx * my                                  # 0..1 soft rectangle
    # inner luminosity: an EVEN plateau of core colour that softens toward the
    # edge (not a central hotspot) — the field glows as a whole, Rothko-style.
    dist = np.sqrt(((u - cx) / (w / 2)) ** 2 + ((v - cy) / (h / 2)) ** 2)
    glow = 1 - smooth(0.45, 1.05, dist)             # flat core, soft edge falloff
    col = col_edge[None, None, :] + (col_core - col_edge)[None, None, :] * glow[..., None]
    return mask[..., None], col


def compose(name, gtop, gbot, f1e, f1c, f2e, f2c, lift=0.92):
    gtop, gbot = np.array(gtop), np.array(gbot)
    img = gtop[None, None, :] + (gbot - gtop)[None, None, :] * v[..., None]
    m1, c1 = field(0.5, 0.36, 0.62, 0.40, 0.10, np.array(f1e), np.array(f1c))
    m2, c2 = field(0.5, 0.72, 0.62, 0.34, 0.09, np.array(f2e), np.array(f2c))
    img = img * (1 - m1) + c1 * m1
    img = img * (1 - m2) + c2 * m2
    img = img * (1.0 + 0.05 * vnoise(5)[..., None])        # slow luminosity drift
    img = img + 0.012 * vnoise(220)[..., None]             # canvas tooth / grain
    halo = 1 - 0.22 * np.sqrt(((u - 0.5) / 0.62) ** 2 + ((v - 0.5) / 0.62) ** 2)
    img = img * np.clip(halo, 0, 1.2)[..., None]           # fields hover in soft dark
    img = np.clip(img, 0, 1) ** lift                       # gentle inner-glow lift
    write_png(os.path.join(OUT, name), (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote", name)


# 1) warm Seagram register — smouldering orange over plum on near-black maroon
compose("seagram.png",
        gtop=[0.20, 0.03, 0.04], gbot=[0.42, 0.09, 0.07],
        f1e=[0.55, 0.12, 0.06], f1c=[0.93, 0.42, 0.13],
        f2e=[0.10, 0.02, 0.06], f2c=[0.34, 0.08, 0.16])

# 2) high-key "dawn" register — pale gold over soft rose on warm ivory: the
#    opposite emotional key, and the fields glow by being LIGHTER than the ground
compose("dawn.png",
        gtop=[0.86, 0.78, 0.66], gbot=[0.80, 0.60, 0.52],
        f1e=[0.92, 0.82, 0.52], f1c=[0.99, 0.95, 0.80],
        f2e=[0.83, 0.55, 0.52], f2c=[0.96, 0.74, 0.72], lift=1.02)
