"""The view from the hill: a 360-degree ink panorama from Rome at (73,11),
turn 1 of game 3, built from the same thirty-five tiles as the map sheet.

Each tile stands at its bearing from the city (north at the left edge, east a
quarter along, south at the centre, west at three quarters) and at a depth by
its ring: the nearest ring lowest and largest, the third ring small on the
horizon. Terrain gives the silhouette: a hump for hills, a peak for the
mountain, a row of trees for forest, a flat band for plains, grass and
tundra, waves for floodplains, coast and sea. Nothing is placed by eye.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rome import FAINT, FONT, FONT_B, FONT_I, INK, PAPER, SS, TILES, WATER, Pen, centre

HERE = Path(__file__).resolve().parent
ORIGIN = (73, 11)
WPX, HPX = 1700, 460
HORIZON = 150  # image y (1x) of the horizon line
RING_BASE = {3: HORIZON + 16, 2: HORIZON + 66, 1: HORIZON + 150}
RING_SCALE = {3: 0.5, 2: 0.78, 1: 1.0}


def ring_and_bearing(xy):
    ox, oy = centre(*ORIGIN)
    cx, cy = centre(*xy)
    dx, dy = cx - ox, cy - oy
    dist = math.hypot(dx, dy)
    ring = int(round(dist / (math.sqrt(3) * 78.0)))  # hex widths
    ring = max(1, min(3, ring))
    bearing = (math.degrees(math.atan2(dx, dy)) + 360.0) % 360.0  # 0 north, 90 east
    return ring, bearing


def main():
    rng = random.Random(7311)
    img = Image.new("RGB", (WPX * SS, HPX * SS), PAPER)
    d = ImageDraw.Draw(img)

    def to_px(p):
        return (p[0] * SS, p[1] * SS)

    pen = Pen(d, to_px, rng)
    left, right = 40, WPX - 40
    span = right - left

    def xb(bearing):
        return left + (bearing / 360.0) * span

    # the horizon
    pen.stroke([(left, HORIZON), (right, HORIZON)], 0.8, 0.8, wobble=0.6, ink=FAINT, taper=False)

    items = []
    for xy, spec in TILES.items():
        if xy == ORIGIN:
            continue
        ring, bearing = ring_and_bearing(xy)
        items.append((ring, bearing, xy, spec))
    # far rings first; within a ring, any order
    items.sort(key=lambda it: -it[0])

    # each ring is a continuous ridge: a paper band from its base down to the
    # next ring's base, with a faint ground line, which the tiles overprint
    ring_order = [3, 2, 1]
    for ring in ring_order:
        base = RING_BASE[ring]
        below = RING_BASE[ring - 1] if ring > 1 else HPX - 90
        d.polygon([to_px((left, base)), to_px((right, base)), to_px((right, below)), to_px((left, below))], fill=PAPER)
        pen.stroke([(left, base), (right, base)], 1.0, 1.0, wobble=0.5, ink=FAINT, taper=False)

    for ring, bearing, xy, spec in items:
        terrain, feats, res, flags = spec
        s = RING_SCALE[ring]
        base = RING_BASE[ring]
        half = (60.0 / ring) / 360.0 * span / 2.0  # half the angular width in px
        for wrap in (-360.0, 0.0, 360.0):
            x = xb(bearing + wrap)
            if x + half < left - 10 or x - half > right + 10:
                continue
            x0, x1 = x - half, x + half
            if terrain == "WATER":
                for k in range(3):
                    y = base - 4 - k * 5 * s
                    pts = [(x0 + t * (x1 - x0) / 10, y + 1.5 * s * math.sin(t * 1.5 + k)) for t in range(11)]
                    pen.stroke(pts, 0.9, 0.9, wobble=0.2, ink=WATER, taper=False)
                continue
            # ground silhouette
            if terrain == "MOUNTAIN":
                top = base - 120 * s
                poly = [(x0, base), (x0 + (x1 - x0) * 0.38, top), (x0 + (x1 - x0) * 0.55, base - 88 * s), (x0 + (x1 - x0) * 0.7, base - 100 * s), (x1, base)]
            elif "hills" in feats:
                top = base - 46 * s
                poly = [(x0, base)] + [(x0 + (x1 - x0) * t / 12, base - 46 * s * math.sin(math.pi * t / 12) ** 0.8) for t in range(1, 12)] + [(x1, base)]
            else:
                top = base - 7 * s
                poly = [(x0, base), (x0 + 3, base - 7 * s), (x1 - 3, base - 6 * s), (x1, base)]
            d.polygon([to_px(q) for q in poly], fill=PAPER)
            pen.stroke(poly, 1.6 * s, 1.6 * s, wobble=0.5, taper=False)
            if terrain == "MOUNTAIN":
                for j in range(6):
                    t = 0.15 + 0.12 * j
                    a = (poly[1][0] + (x1 - poly[1][0]) * t, top + (base - top) * t)
                    pen.stroke([a, (a[0] - 6 * s, a[1] + 10 * s)], 1.0, 0.4, wobble=0.3)
            if "hills" in feats and terrain != "MOUNTAIN":
                for j in range(5):
                    xx = x0 + (x1 - x0) * (0.55 + 0.08 * j)
                    yy = base - 46 * s * math.sin(math.pi * (0.55 + 0.08 * j)) ** 0.8
                    pen.stroke([(xx, yy + 4 * s), (xx + 5 * s, yy + 16 * s)], 1.0 * s, 0.4 * s, wobble=0.3)
            # texture on the flat
            if terrain == "PLAINS" and "hills" not in feats:
                for _ in range(int(14 * s)):
                    px = rng.uniform(x0 + 4, x1 - 4)
                    py = base - rng.uniform(1, 5 * s)
                    d.ellipse([to_px((px - 0.6, py - 0.6)), to_px((px + 0.6, py + 0.6))], fill=FAINT)
            elif terrain == "DESERT" and "hills" not in feats:
                for _ in range(int(30 * s)):
                    px = rng.uniform(x0 + 4, x1 - 4)
                    py = base - rng.uniform(1, 5 * s)
                    d.ellipse([to_px((px - 0.6, py - 0.6)), to_px((px + 0.6, py + 0.6))], fill=INK)
            elif terrain == "TUNDRA" and "hills" not in feats:
                for _ in range(int(6 * s)):
                    px = rng.uniform(x0 + 6, x1 - 6)
                    py = base - rng.uniform(1, 5 * s)
                    pen.stroke([(px - 4 * s, py), (px + 4 * s, py)], 0.7, 0.7, ink=FAINT, taper=False)
            if "floodplains" in feats or "coast" in flags:
                for k in range(2):
                    y = base - 2 - k * 4 * s
                    pts = [(x0 + 3 + t * (x1 - x0 - 6) / 8, y + 1.2 * s * math.sin(t * 1.7 + k)) for t in range(9)]
                    pen.stroke(pts, 0.8, 0.8, wobble=0.15, ink=WATER, taper=False)
            if "forest" in feats:
                n = max(3, int((x1 - x0) / (14 * s)))
                for k in range(n):
                    tx = x0 + 6 + (x1 - x0 - 12) * (k + 0.5) / n
                    # ground height under the tree
                    if "hills" in feats:
                        ty = base - 46 * s * math.sin(math.pi * (tx - x0) / (x1 - x0)) ** 0.8
                    else:
                        ty = base - 6 * s
                    h = 16 * s
                    pen.stroke([(tx, ty), (tx, ty - h * 0.45)], 1.2 * s, 0.9 * s, taper=False)
                    crown = [(tx - 6 * s, ty - h * 0.4), (tx - 4 * s, ty - h * 0.85), (tx, ty - h * 1.15), (tx + 4 * s, ty - h * 0.85), (tx + 6 * s, ty - h * 0.4)]
                    d.polygon([to_px(q) for q in crown], fill=PAPER)
                    pen.stroke(crown + crown[:1], 1.0 * s, 1.0 * s, wobble=0.5, taper=False)
            if res and ring <= 2:
                f = ImageFont.truetype(FONT_I, int(10 * SS))
                d.text(to_px((x, base + 11 * s + 2)), res.title(), font=f, fill=INK, anchor="mm")
            if "warrior" in flags:
                hx, hy = x, base - 46 * s - 2
                pen.stroke([(hx, hy), (hx, hy - 14)], 1.6, 1.0, taper=False)
                d.ellipse([to_px((hx - 3, hy - 20)), to_px((hx + 3, hy - 14))], outline=INK, width=2)
                pen.stroke([(hx + 5, hy - 22), (hx + 5, hy - 2)], 1.0, 0.8, taper=False)
                f = ImageFont.truetype(FONT_I, int(9 * SS))
                d.text(to_px((hx, hy - 28)), "warrior", font=f, fill=FAINT, anchor="mm")

    # the near ground: the hill Rome stands on, as a dark foreground band
    fg = [(left, HPX - 60), (left + span * 0.2, HPX - 84), (left + span * 0.5, HPX - 70), (left + span * 0.8, HPX - 88), (right, HPX - 62), (right, HPX - 30), (left, HPX - 30)]
    d.polygon([to_px(q) for q in fg], fill=PAPER)
    pen.stroke(fg[:5], 2.0, 2.0, wobble=0.8, taper=False)
    for k in range(40):
        xx = left + rng.uniform(10, span - 10)
        pen.stroke([(xx, HPX - 58 + rng.uniform(-6, 6)), (xx + 3, HPX - 46)], 1.0, 0.5, wobble=0.3)

    # bearings
    fb = ImageFont.truetype(FONT_B, int(13 * SS))
    for bearing, name in ((0, "N"), (90, "E"), (180, "S"), (270, "W"), (360, "N")):
        x = xb(bearing)
        pen.stroke([(x, 36), (x, 48)], 1.2, 1.2, taper=False)
        d.text(to_px((x, 26)), name, font=fb, fill=INK, anchor="mm")
    for bearing in range(0, 361, 30):
        x = xb(bearing)
        pen.stroke([(x, 42), (x, 48)], 0.8, 0.8, ink=FAINT, taper=False)
    pen.stroke([(left, 48), (right, 48)], 0.8, 0.8, ink=FAINT, taper=False)

    ft = ImageFont.truetype(FONT_B, int(18 * SS))
    fi = ImageFont.truetype(FONT_I, int(11 * SS))
    d.text(to_px((left, HPX - 18)), "THE VIEW FROM THE HILL.  Rome, turn 1: all round the compass from (73,11), the three rings of tiles at their bearings.", font=ft, fill=INK, anchor="lm")
    d.text(to_px((right, HPX - 40)), "the mountain west-south-west, the sea east, the tundra south; the warrior on the next hill west", font=fi, fill=FAINT, anchor="rm")
    img.resize((WPX, HPX), Image.LANCZOS).save(HERE / "the-view-from-the-hill.png")
    print("ok")


if __name__ == "__main__":
    main()
