"""Rome, turn 1, as a block diagram: the thirty-five tiles as hex prisms in an
oblique projection, hills raised, the mountain a peak, water sunk, signs on
the top faces, the near (southern) tiles overprinting the far. The third
projection of the same read: the sheet (plan), the view (elevation all
round), the block (oblique)."""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rome import FAINT, FONT, FONT_B, FONT_I, INK, PAPER, SS, TILES, WATER, Pen, centre, hexagon, box

HERE = Path(__file__).resolve().parent
KX, KY = 0.42, 0.52  # oblique: north shifts east and shrinks


def iso(p, h=0.0):
    """Scene (x, y north-up) plus elevation h -> drawing plane (y up)."""
    return (p[0] + KX * p[1], KY * p[1] + h)


RISE = 1.0  # 0: the flat plan; 1: full relief


def elevation(spec):
    terrain, feats, _res, _flags = spec
    if terrain == "MOUNTAIN":
        return 70.0 * RISE
    if terrain == "WATER":
        return -10.0 * RISE
    if "hills" in feats:
        return 24.0 * RISE
    return 0.0


def main(out_name="rome-in-block.png", rise=1.0):
    global RISE
    RISE = rise
    rng = random.Random(1173)
    pts = [iso(centre(*k), 80) for k in TILES] + [iso(centre(*k), -20) for k in TILES]
    minx, maxx = min(p[0] for p in pts) - 70, max(p[0] for p in pts) + 70
    miny, maxy = min(p[1] for p in pts) - 90, max(p[1] for p in pts) + 60
    Wpx, Hpx = int(maxx - minx), int(maxy - miny) + 70
    img = Image.new("RGB", (Wpx * SS, Hpx * SS), PAPER)
    d = ImageDraw.Draw(img)

    def to_px(p):
        return ((p[0] - minx) * SS, (maxy - p[1] + 70) * SS)

    pen = Pen(d, to_px, rng)
    # far (north, high y) first, then west to east
    order = sorted(TILES, key=lambda k: (-centre(*k)[1], centre(*k)[0]))
    for xy in order:
        spec = TILES[xy]
        terrain, feats, res, flags = spec
        cx, cy = centre(*xy)
        h = elevation(spec)
        top = [iso(q, h) for q in hexagon(cx, cy)]
        base = [iso(q, 0.0 if h >= 0 else h) for q in hexagon(cx, cy)]
        # walls: the three southern edges (lowest in the scene) down to the ground
        if h > 0:
            for i in range(6):
                a, b = hexagon(cx, cy)[i], hexagon(cx, cy)[(i + 1) % 6]
                if (a[1] + b[1]) / 2 < cy:  # a south-facing edge
                    wall = [iso(a, h), iso(b, h), iso(b, 0.0), iso(a, 0.0)]
                    d.polygon([to_px(q) for q in wall], fill=PAPER)
                    pen.stroke(wall + wall[:1], 1.2, 1.2, wobble=0.3, taper=False)
                    # shade the wall with vertical hachures
                    for j in range(1, 6):
                        t = j / 6
                        u = (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
                        pen.stroke([iso(u, h * 0.9), iso(u, h * 0.1)], 0.9, 0.5, wobble=0.3, ink=FAINT)
        if terrain == "MOUNTAIN":
            # a peak: the top hexagon is the base of a cone; apex above the centre
            apex = iso((cx + 6, cy + 4), h + 55 * RISE)
            ground = [iso(q, 0.0) for q in hexagon(cx, cy)]
            d.polygon([to_px(q) for q in ground], fill=PAPER)
            pen.stroke(ground + ground[:1], 1.0, 1.0, wobble=0.3, taper=False)
            cone = [ground[i] for i in (0, 1, 2, 3)]  # the front edges
            d.polygon([to_px(q) for q in [cone[0], apex, cone[3], cone[2], cone[1]]], fill=PAPER)
            pen.stroke([cone[0], apex, cone[3]], 2.0, 2.0, wobble=0.5, taper=False)
            for j in range(6):
                t = 0.15 + 0.14 * j
                a = (apex[0] + (cone[3][0] - apex[0]) * t, apex[1] + (cone[3][1] - apex[1]) * t)
                pen.stroke([a, (a[0] - 7, a[1] - 9)], 1.1, 0.4, wobble=0.3)
            continue
        d.polygon([to_px(q) for q in top], fill=PAPER)
        pen.stroke(top + top[:1], 1.3 if terrain != "WATER" else 0.8, 1.3 if terrain != "WATER" else 0.8, wobble=0.3, ink=INK if terrain != "WATER" else WATER, taper=False)
        tc = iso((cx, cy), h)
        if terrain == "WATER" or "coast" in flags:
            for k in range(3 if terrain == "WATER" else 1):
                y = tc[1] - 14 + k * 12
                x0 = tc[0] - 38 + (k * 4)
                wave = [(x0 + t * 7, y + 2.2 * math.sin(t * 1.5 + k)) for t in range(11)]
                pen.stroke(wave, 0.9, 0.9, wobble=0.2, ink=WATER, taper=False)
        if terrain == "PLAINS":
            for _ in range(28):
                p = (tc[0] + rng.uniform(-40, 40), tc[1] + rng.uniform(-14, 14))
                d.ellipse(box(to_px, p, 0.9), fill=FAINT)
        elif terrain == "DESERT":
            for _ in range(70):
                p = (tc[0] + rng.uniform(-40, 40), tc[1] + rng.uniform(-14, 14))
                d.ellipse(box(to_px, p, 0.8), fill=INK)
        elif terrain == "TUNDRA":
            for _ in range(10):
                p = (tc[0] + rng.uniform(-36, 36), tc[1] + rng.uniform(-13, 13))
                pen.stroke([(p[0] - 5, p[1]), (p[0] + 5, p[1])], 0.7, 0.7, wobble=0.2, ink=FAINT, taper=False)
        if "floodplains" in feats:
            for k in range(4):
                y = tc[1] - 12 + k * 8
                pen.stroke([(tc[0] - 36, y), (tc[0] + 36, y)], 0.5, 0.5, wobble=0.5, ink=FAINT, taper=False)
        if "river" in flags:
            ribbon = [(tc[0] - 44 + t * 7, tc[1] - 22 + 3 * math.sin(t * 0.9 + xy[0])) for t in range(13)]
            pen.stroke(ribbon, 1.4, 1.4, wobble=0.3, ink=WATER, taper=False)
        if "hills" in feats:
            for j in range(6):
                x = tc[0] - 24 + j * 9
                pen.stroke([(x, tc[1] - 4), (x + 6, tc[1] + 6)], 1.2, 0.5, wobble=0.3)
        if "forest" in feats:
            for _ in range(5):
                p = (tc[0] + rng.uniform(-26, 26), tc[1] + rng.uniform(-8, 8))
                pen.stroke([(p[0], p[1]), (p[0], p[1] + 8)], 1.2, 0.8, taper=False)
                crown = [(p[0] - 6, p[1] + 7), (p[0] - 4, p[1] + 14), (p[0], p[1] + 19), (p[0] + 4, p[1] + 14), (p[0] + 6, p[1] + 7)]
                d.polygon([to_px(q) for q in crown], fill=PAPER)
                pen.stroke(crown + crown[:1], 1.0, 1.0, wobble=0.4, taper=False)
        if "settler" in flags:
            ring = [(tc[0] + 14 * math.cos(math.radians(a)), tc[1] + 8 * math.sin(math.radians(a))) for a in range(0, 361, 20)]
            d.polygon([to_px(q) for q in ring], fill=PAPER)
            pen.stroke(ring, 2.0, 2.0, wobble=0.3, taper=False)
            pen.stroke([(tc[0] - 4, tc[1]), (tc[0] - 4, tc[1] + 18), (tc[0] + 4, tc[1] + 18), (tc[0] + 4, tc[1])], 1.6, 1.6, taper=False)
            f = ImageFont.truetype(FONT_B, int(13 * SS))
            d.text(to_px((tc[0], tc[1] + 34)), "ROME", font=f, fill=INK, anchor="mm")
        if "warrior" in flags:
            pen.stroke([(tc[0], tc[1] + 2), (tc[0], tc[1] + 16)], 1.6, 1.0, taper=False)
            d.ellipse(box(to_px, (tc[0], tc[1] + 19), 3), outline=INK, width=2)
            pen.stroke([(tc[0] + 5, tc[1] + 24), (tc[0] + 5, tc[1] + 4)], 1.0, 0.8, taper=False)
        if res:
            f = ImageFont.truetype(FONT_I, int(10 * SS))
            d.text(to_px((tc[0], tc[1] - 30)), res.title(), font=f, fill=INK, anchor="mm")

    ft = ImageFont.truetype(FONT_B, int(18 * SS))
    fi = ImageFont.truetype(FONT_I, int(11 * SS))
    d.text(to_px((minx + 30, maxy + 46)), "ROME, TURN 1, IN BLOCK.  The thirty-five tiles as hex prisms, north away from the viewer.", font=ft, fill=INK, anchor="lm")
    d.text(to_px((minx + 30, maxy + 26)), "hills raised, the mountain a peak, the sea sunk; walls hachured; the near tiles overprint the far. The sheet, the view, and now the block.", font=fi, fill=FAINT, anchor="lm")
    out = img.resize((Wpx, Hpx), Image.LANCZOS)
    out.save(HERE / out_name)
    return out


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rise":
        frames = []
        for i in range(30):
            t = i / 29
            e = t * t * (3 - 2 * t)  # ease in and out
            frames.append(main(out_name="_rise.png", rise=e))
        frames += [frames[-1]] * 18
        frames[0].save(HERE / "rome-rising.gif", save_all=True, append_images=frames[1:], duration=70, loop=0)
        (HERE / "_rise.png").unlink(missing_ok=True)
        print("gif", len(frames))
    else:
        main()
        print("ok")
