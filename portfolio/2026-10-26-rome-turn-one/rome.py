"""Rome, turn 1: the thirty-five tiles the settler could see.

An ink map in the manner of a surveyor's sheet, drawn from the real map read
of game 3 of the Civ VI Deity campaign (get_map_area at (73,11), radius 3,
2026-10-26). Civ 6 hexes are pointy-topped with odd rows shifted half a hex
to the east; higher y is north. Terrain by conventional signs: hachures for
hills, peaks for mountains, tree marks for forest, stipple for plains and
desert, dashes for tundra, waves for coast, a ribbon for a river tile and a
fine band for floodplains. Resources are named where they lie. No invention:
every sign stands on a tile the game reported.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

SS = 2
PAPER = (236, 228, 206)
INK = (38, 30, 22)
FAINT = (120, 108, 92)
WATER = (70, 84, 96)
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"

# (x, y): terrain, features, resource, flags  (verbatim from the read)
TILES = {
    (72, 8): ("TUNDRA", [], "DEER", []),
    (73, 8): ("TUNDRA", [], None, ["river"]),
    (74, 8): ("TUNDRA", [], None, ["river"]),
    (75, 8): ("TUNDRA", ["hills"], None, ["river", "coast"]),
    (71, 9): ("MOUNTAIN", [], None, []),
    (72, 9): ("TUNDRA", [], None, ["river"]),
    (73, 9): ("TUNDRA", [], None, ["river"]),
    (74, 9): ("TUNDRA", [], None, ["river"]),
    (75, 9): ("TUNDRA", [], None, ["coast"]),
    (71, 10): ("TUNDRA", ["hills", "forest"], None, []),
    (72, 10): ("TUNDRA", ["hills"], None, ["river"]),
    (73, 10): ("GRASS", [], None, ["river"]),
    (74, 10): ("GRASS", ["floodplains"], None, ["river"]),
    (75, 10): ("PLAINS", ["floodplains"], "MAIZE", ["river", "coast"]),
    (76, 10): ("WATER", [], None, []),
    (70, 11): ("PLAINS", [], "MERCURY", ["river"]),
    (71, 11): ("TUNDRA", ["hills"], None, ["river"]),
    (72, 11): ("GRASS", ["hills"], None, ["river", "warrior"]),
    (73, 11): ("GRASS", ["hills", "forest"], None, ["river", "settler"]),
    (74, 11): ("GRASS", ["floodplains"], None, ["river"]),
    (75, 11): ("PLAINS", ["floodplains"], None, ["river", "coast"]),
    (76, 11): ("WATER", [], None, []),
    (71, 12): ("PLAINS", [], None, ["river"]),
    (72, 12): ("PLAINS", ["hills"], None, ["river"]),
    (73, 12): ("PLAINS", ["forest"], None, []),
    (74, 12): ("PLAINS", [], "WHEAT", []),
    (75, 12): ("PLAINS", [], "GYPSUM", ["coast"]),
    (76, 12): ("WATER", [], None, []),
    (71, 13): ("PLAINS", ["floodplains"], None, ["river"]),
    (72, 13): ("PLAINS", ["hills", "forest"], "TRUFFLES", ["river"]),
    (73, 13): ("PLAINS", [], None, []),
    (74, 13): ("PLAINS", [], None, []),
    (75, 13): ("PLAINS", [], None, ["coast"]),
    (74, 14): ("DESERT", ["hills"], None, []),
    (75, 14): ("DESERT", [], None, []),
}

R = 78.0  # hex circumradius at 1x
W = math.sqrt(3) * R
HROW = 1.5 * R


class Pen:
    """A tapered pen in pixel units (the studio's inkfigure.Pen resamples in
    metres, far too fine for a map drawn in pixels)."""

    def __init__(self, draw, to_px, rng, ink_colour=INK):
        self.d, self.to_px, self.rng, self.ink = draw, to_px, rng, ink_colour

    def stroke(self, pts, w0, w1, wobble=0.3, ink=None, taper=True):
        ink = ink or self.ink
        if len(pts) < 2:
            return
        seg = [math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1]) for i in range(len(pts) - 1)]
        total = sum(seg)
        if total < 1e-6:
            return
        n = max(3, int(total / 3.0))
        samp = []
        i, acc = 0, 0.0
        for k in range(n + 1):
            s_ = total * k / n
            while i < len(seg) - 1 and acc + seg[i] < s_:
                acc += seg[i]
                i += 1
            u = max(0.0, min(1.0, (s_ - acc) / (seg[i] or 1e-6)))
            samp.append((pts[i][0] + (pts[i + 1][0] - pts[i][0]) * u, pts[i][1] + (pts[i + 1][1] - pts[i][1]) * u))
        left, right, drift = [], [], 0.0
        for k, q in enumerate(samp):
            t = k / n
            a, b = samp[max(0, k - 1)], samp[min(n, k + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1e-6
            nx, ny = -dy / L, dx / L
            w = w0 + (w1 - w0) * t
            if taper:
                w *= 0.35 + 0.65 * math.sin(math.pi * t) ** 0.55
            drift = 0.7 * drift + self.rng.uniform(-wobble, wobble)
            px, py = q[0] + nx * drift, q[1] + ny * drift
            left.append((px + nx * w, py + ny * w))
            right.append((px - nx * w, py - ny * w))
        self.d.polygon([self.to_px(z) for z in left + list(reversed(right))], fill=ink)


def centre(x: int, y: int) -> tuple[float, float]:
    """Scene position of a tile centre (y up): odd rows shift east half a hex."""
    return ((x + 0.5 * (y % 2)) * W, y * HROW)


def hexagon(cx: float, cy: float, r: float = R) -> list[tuple[float, float]]:
    return [(cx + r * math.cos(math.radians(60 * i + 30)), cy + r * math.sin(math.radians(60 * i + 30))) for i in range(6)]


def box(to_px, p, r):
    """An ellipse box in image space for a scene circle (y is flipped by to_px)."""
    x0, y0 = to_px((p[0] - r, p[1] + r))
    x1, y1 = to_px((p[0] + r, p[1] - r))
    return [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]


def inside(cx, cy, r, rng, n):
    """n random points inside the hex (rejection on the inscribed circle, then the hex)."""
    pts = []
    while len(pts) < n:
        px, py = rng.uniform(-r, r), rng.uniform(-r, r)
        if abs(px) <= W / 2 * 0.9 * (r / R) and abs(py) + abs(px) / math.sqrt(3) <= r * 0.9:
            pts.append((cx + px, cy + py))
    return pts


def draw_tile(pen: Pen, d, to_px, xy, spec, rng):
    terrain, feats, res, flags = spec
    cx, cy = centre(*xy)
    hexp = hexagon(cx, cy)
    # the hex edge, faint
    pen.stroke(hexp + hexp[:1], 0.6, 0.6, wobble=0.3, ink=FAINT, taper=False)
    if terrain == "WATER":
        for k in range(5):
            y = cy - R * 0.55 + k * R * 0.28
            pts = [(cx - W * 0.36 + t * W * 0.72 / 12, y + 2.5 * math.sin(t * 1.6 + k)) for t in range(13)]
            pen.stroke(pts, 0.9, 0.9, wobble=0.2, ink=WATER, taper=False)
        return
    if "coast" in flags:
        # a shoreline wave along the eastern edge of a land tile that touches the sea
        for k in range(2):
            x0 = cx + W * 0.30 + k * 6
            pts = [(x0 + 2.0 * math.sin(t * 1.4), cy - R * 0.5 + t * R / 10) for t in range(11)]
            pen.stroke(pts, 0.8, 0.8, wobble=0.15, ink=WATER, taper=False)
    if terrain == "MOUNTAIN":
        # two peaks in outline, hachured on their shaded (eastern) flanks
        base_y = cy - 18
        for ox, h, wl, wr in ((-14, 44, 30, 26), (18, 32, 20, 24)):
            apex = (cx + ox, base_y + h)
            pen.stroke([(cx + ox - wl, base_y), apex, (cx + ox + wr, base_y)], 1.8, 1.8, wobble=0.4, taper=False)
            for j in range(5):
                t = 0.2 + 0.16 * j
                a = (apex[0] + (cx + ox + wr - apex[0]) * t, apex[1] - (apex[1] - base_y) * t)
                pen.stroke([a, (a[0] - 5 - j, a[1] - 7 - j)], 1.1, 0.5, wobble=0.3)
        return
    if terrain == "PLAINS":
        for p in inside(cx, cy, R * 0.8, rng, 55):
            d.ellipse(box(to_px, p, 0.9), fill=FAINT)
    elif terrain == "DESERT":
        for p in inside(cx, cy, R * 0.8, rng, 120):
            d.ellipse(box(to_px, p, 0.8), fill=INK)
    elif terrain == "TUNDRA":
        for p in inside(cx, cy, R * 0.8, rng, 22):
            pen.stroke([(p[0] - 5, p[1]), (p[0] + 5, p[1])], 0.7, 0.7, wobble=0.2, ink=FAINT, taper=False)
    # grass: left as paper
    if "floodplains" in feats:
        for k in range(7):
            y = cy - R * 0.45 + k * R * 0.15
            pen.stroke([(cx - W * 0.30, y), (cx + W * 0.30, y)], 0.5, 0.5, wobble=0.6, ink=FAINT, taper=False)
    if "hills" in feats:
        # hachures: short slanted strokes in two bands, as on a surveyor's sheet
        for band, y0 in ((0, cy + 6), (1, cy + 26)):
            for k in range(7):
                x = cx - W * 0.30 + k * W * 0.10 + (6 if band else 0)
                pen.stroke([(x, y0), (x + 7, y0 - 11)], 1.3, 0.5, wobble=0.3)
    if "forest" in feats:
        for p in inside(cx, cy, R * 0.55, rng, 6):
            # a tree: trunk and a round canopy of two short arcs
            pen.stroke([(p[0], p[1] + 2), (p[0], p[1] + 9)], 1.2, 0.8, taper=False)
            arc = [(p[0] + 7 * math.cos(math.radians(a)), p[1] - 2 + 6 * math.sin(math.radians(a))) for a in range(200, 341, 20)]
            pen.stroke(arc, 1.1, 1.1, wobble=0.4, taper=False)
            arc2 = [(p[0] + 7 * math.cos(math.radians(a)), p[1] - 2 + 6 * math.sin(math.radians(a))) for a in range(20, 161, 20)]
            pen.stroke(arc2, 1.1, 1.1, wobble=0.4, taper=False)
    if "river" in flags:
        # a ribbon: the read names the tile, not the bank, so the sign sits in the tile
        pts = [(cx - W * 0.34 + t * W * 0.68 / 14, cy - R * 0.62 + 5 * math.sin(t * 0.9 + xy[0])) for t in range(15)]
        pen.stroke(pts, 1.4, 1.4, wobble=0.3, ink=WATER, taper=False)
        pen.stroke([(q[0], q[1] + 4) for q in pts], 0.7, 0.7, wobble=0.3, ink=WATER, taper=False)


def label(d, to_px, pos, text, size=13, font=FONT_I, fill=INK, anchor="mm"):
    f = ImageFont.truetype(font, int(size * SS))
    d.text(to_px(pos), text, font=f, fill=fill, anchor=anchor)


def main():
    rng = random.Random(1106)
    xs = [centre(*k)[0] for k in TILES]
    ys = [centre(*k)[1] for k in TILES]
    minx, maxx, miny, maxy = min(xs) - R, max(xs) + R, min(ys) - R, max(ys) + R
    margin = 60
    legend_w = 300
    Wpx = int((maxx - minx) + 2 * margin + legend_w)
    Hpx = int((maxy - miny) + 2 * margin + 110)
    img = Image.new("RGB", (Wpx * SS, Hpx * SS), PAPER)
    d = ImageDraw.Draw(img)

    def to_px(p):
        # scene y up -> image y down; the map sits left, the legend right
        return ((p[0] - minx + margin) * SS, (maxy - p[1] + margin + 70) * SS)

    pen = Pen(d, to_px, rng)
    # tiles, north first so southern signs overprint northern edges
    for xy in sorted(TILES, key=lambda k: -k[1]):
        draw_tile(pen, d, to_px, xy, TILES[xy], rng)
    # the city, the warrior, the resources
    for xy, spec in TILES.items():
        cx, cy = centre(*xy)
        terrain, feats, res, flags = spec
        if "settler" in flags:
            # Rome: a walled ring with a tower, the founding mark
            ring = [(cx + 16 * math.cos(math.radians(a)), cy + 16 * math.sin(math.radians(a))) for a in range(0, 361, 20)]
            d.polygon([to_px(q) for q in ring], fill=PAPER)
            pen.stroke(ring, 2.2, 2.2, wobble=0.3, taper=False)
            pen.stroke([(cx - 5, cy - 16), (cx - 5, cy + 2), (cx + 5, cy + 2), (cx + 5, cy - 16)], 1.6, 1.6, taper=False)
            pen.stroke([(cx - 7, cy - 16), (cx + 7, cy - 16)], 1.6, 1.6, taper=False)
            label(d, to_px, (cx, cy - 30), "ROME", 15, FONT_B)
            label(d, to_px, (cx, cy - 44), "founded turn 1", 10, FONT_I, FAINT)
        if "warrior" in flags:
            # a small figure with a spear
            pen.stroke([(cx - 20, cy - 10), (cx - 20, cy + 6)], 1.6, 1.0, taper=False)
            d.ellipse(box(to_px, (cx - 20, cy + 9), 3), outline=INK, width=2)
            pen.stroke([(cx - 14, cy - 14), (cx - 14, cy + 4)], 1.0, 0.8, taper=False)
            label(d, to_px, (cx - 20, cy - 22), "warrior", 9, FONT_I, FAINT)
        if res:
            label(d, to_px, (cx, cy - 46 if "settler" not in flags else cy - 58), res.title(), 11, FONT_I)
    # coordinates along the edges: columns and rows
    for x in range(70, 77):
        cx, _ = centre(x, 14)
        label(d, to_px, (cx + 0.25 * W, maxy + 10), str(x), 11, FONT, FAINT)
    for y in range(8, 15):
        _, cy = centre(70, y)
        label(d, to_px, (minx - 8, cy), str(y), 11, FONT, FAINT, anchor="rm")
    # title and legend
    tx = maxx + 40
    ty = maxy - 10
    label(d, to_px, (tx, ty), "ROME, TURN 1", 22, FONT_B, anchor="lm")
    label(d, to_px, (tx, ty - 28), "the thirty-five tiles the settler could see", 12, FONT_I, anchor="lm")
    label(d, to_px, (tx, ty - 46), "Deity, Fractal, Standard, 2026-10-26", 11, FONT, FAINT, anchor="lm")
    label(d, to_px, (tx, ty - 64), "north is up; odd rows sit half a hex east", 11, FONT, FAINT, anchor="lm")
    items = [
        ("hills", "hachures"), ("mountain", "peaks"), ("forest", "tree marks"),
        ("plains", "light stipple"), ("desert", "dense stipple"), ("tundra", "dashes"),
        ("grass", "clear paper"), ("floodplains", "fine band"), ("river tile", "a ribbon"),
        ("coast", "waves"),
    ]
    yy = ty - 100
    for name, sign in items:
        label(d, to_px, (tx, yy), f"{name}:  {sign}", 11, FONT, anchor="lm")
        yy -= 18
    label(d, to_px, (tx, yy - 10), "Drawn from get_map_area(73,11), radius 3.", 10, FONT_I, FAINT, anchor="lm")
    label(d, to_px, (tx, yy - 26), "Nothing added; the river sign names the tile,", 10, FONT_I, FAINT, anchor="lm")
    label(d, to_px, (tx, yy - 42), "not the bank, because that is what the read says.", 10, FONT_I, FAINT, anchor="lm")
    # compass
    cxp, cyp = tx + 200, ty - 300
    pen.stroke([(cxp, cyp - 40), (cxp, cyp + 40)], 1.4, 1.4, taper=False)
    pen.stroke([(cxp - 40, cyp), (cxp + 40, cyp)], 1.0, 1.0, taper=False)
    pen.stroke([(cxp - 8, cyp + 22), (cxp, cyp + 44), (cxp + 8, cyp + 22)], 1.8, 1.8, taper=False)
    label(d, to_px, (cxp, cyp + 58), "N", 13, FONT_B)

    out = img.resize((Wpx, Hpx), Image.LANCZOS)
    out.save(HERE / "rome-turn-one.png")
    print(out.size)


if __name__ == "__main__":
    main()
