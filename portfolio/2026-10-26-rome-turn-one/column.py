"""The column: Trajan's monument as the vessel for game 3's story.

An ink elevation of a column with a spiral frieze, in the manner of the
column in Trajan's forum whose band winds up the shaft telling a campaign
scene by scene. Here the lowest winding carries turn 1 (the river, the hill,
the founding, the warrior walking north) and the windings above are blank,
to be filled every twenty turns as the game goes on. Beneath, the first
winding unrolled as a strip.
"""

from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from rome import FAINT, FONT, FONT_B, FONT_I, INK, PAPER, SS, WATER, Pen, box

HERE = Path(__file__).resolve().parent
WPX, HPX = 1100, 1500


def scene_turn_one(pen, d, to_px, x0, y0, w, h, rng):
    """The founding, drawn into a band of width w and height h with its
    lower-left corner at (x0, y0) in a y-up scene."""
    # ground line and the river ribbon
    pen.stroke([(x0, y0 + 2), (x0 + w, y0 + 2)], 1.2, 1.2, wobble=0.4, taper=False)
    rib = [(x0 + 6 + t * (w - 12) / 24, y0 + 6 + 2.5 * math.sin(t * 0.8)) for t in range(25)]
    pen.stroke(rib, 1.4, 1.4, wobble=0.3, ink=WATER, taper=False)
    # the hill, a hump at the left third, with the city ring and tower on it
    hx = x0 + w * 0.32
    hill = [(hx - 46, y0 + 6)] + [(hx - 46 + 92 * t / 12, y0 + 6 + 26 * math.sin(math.pi * t / 12) ** 0.9) for t in range(1, 12)] + [(hx + 46, y0 + 6)]
    d.polygon([to_px(q) for q in hill], fill=PAPER)
    pen.stroke(hill, 1.6, 1.6, wobble=0.4, taper=False)
    for j in range(5):
        xx = hx + 10 + j * 7
        yy = y0 + 6 + 26 * math.sin(math.pi * (0.6 + j * 0.07)) ** 0.9
        pen.stroke([(xx, yy - 2), (xx + 4, yy - 10)], 1.0, 0.4, wobble=0.3)
    top = y0 + 32
    ring = [(hx + 11 * math.cos(math.radians(a)), top + 6 + 5 * math.sin(math.radians(a))) for a in range(0, 361, 20)]
    d.polygon([to_px(q) for q in ring], fill=PAPER)
    pen.stroke(ring, 1.6, 1.6, wobble=0.3, taper=False)
    pen.stroke([(hx - 3, top + 6), (hx - 3, top + 22), (hx + 3, top + 22), (hx + 3, top + 6)], 1.4, 1.4, taper=False)
    # trees on the hill's shoulder
    for k in range(3):
        tx = hx - 30 + k * 11
        ty = y0 + 6 + 26 * math.sin(math.pi * ((tx - (hx - 46)) / 92)) ** 0.9
        pen.stroke([(tx, ty), (tx, ty + 7)], 1.2, 0.8, taper=False)
        crown = [(tx - 5, ty + 6), (tx - 3, ty + 12), (tx, ty + 16), (tx + 3, ty + 12), (tx + 5, ty + 6)]
        d.polygon([to_px(q) for q in crown], fill=PAPER)
        pen.stroke(crown + crown[:1], 1.0, 1.0, wobble=0.4, taper=False)
    # the settler at the hill's foot, a figure with a bundle, and the warrior walking right (north)
    def figure(fx, fy, spear=False, bundle=False, lean=0.0):
        pen.stroke([(fx, fy), (fx + lean, fy + 14)], 1.6, 1.1, taper=False)  # body
        d.ellipse(box(to_px, (fx + lean, fy + 17), 3), outline=INK, width=2)
        pen.stroke([(fx, fy), (fx - 4, fy - 9)], 1.2, 0.8, taper=False)  # legs
        pen.stroke([(fx, fy), (fx + 4, fy - 9)], 1.2, 0.8, taper=False)
        if spear:
            pen.stroke([(fx + 7, fy - 6), (fx + 7, fy + 22)], 1.0, 0.8, taper=False)
        if bundle:
            d.ellipse(box(to_px, (fx - 7, fy + 12), 4), outline=INK, width=2)
    figure(hx - 56, y0 + 14, bundle=True)
    for k in range(3):
        figure(x0 + w * 0.55 + k * 40, y0 + 14, spear=True, lean=1.5)
    # the sea at the right end: waves
    for k in range(3):
        wave = [(x0 + w * 0.82 + t * (w * 0.16) / 10, y0 + 10 + k * 8 + 2 * math.sin(t * 1.5 + k)) for t in range(11)]
        pen.stroke(wave, 0.9, 0.9, wobble=0.2, ink=WATER, taper=False)
    # a mountain far left
    mx = x0 + 22
    pen.stroke([(mx - 16, y0 + 6), (mx, y0 + 38), (mx + 14, y0 + 6)], 1.4, 1.4, wobble=0.3, taper=False)
    for j in range(4):
        t = 0.25 + 0.18 * j
        a = (mx + 14 * t, y0 + 38 - 32 * t)
        pen.stroke([a, (a[0] - 4, a[1] - 5)], 0.9, 0.4, wobble=0.3)


def main():
    rng = random.Random(113)
    img = Image.new("RGB", (WPX * SS, HPX * SS), PAPER)
    d = ImageDraw.Draw(img)

    def to_px(p):
        return (p[0] * SS, (HPX - p[1]) * SS)

    pen = Pen(d, to_px, rng)
    # the column: a pedestal, a shaft with 12 windings, a capital, a statue base
    cx = 330
    shaft_w = 150
    ped_y, ped_h, ped_w = 300, 110, 240
    shaft_y0 = ped_y + ped_h
    windings = 12
    wind_h = 72
    shaft_y1 = shaft_y0 + windings * wind_h
    # pedestal
    ped = [(cx - ped_w / 2, ped_y), (cx + ped_w / 2, ped_y), (cx + ped_w / 2, ped_y + ped_h), (cx - ped_w / 2, ped_y + ped_h)]
    pen.stroke(ped + ped[:1], 2.0, 2.0, wobble=0.5, taper=False)
    pen.stroke([(cx - ped_w / 2 - 14, ped_y), (cx + ped_w / 2 + 14, ped_y)], 2.4, 2.4, taper=False)
    pen.stroke([(cx - ped_w / 2 - 8, ped_y + ped_h), (cx + ped_w / 2 + 8, ped_y + ped_h), (cx + ped_w / 2 + 8, ped_y + ped_h + 10), (cx - ped_w / 2 - 8, ped_y + ped_h + 10)], 1.6, 1.6, taper=False)
    fi = ImageFont.truetype(FONT_B, int(14 * SS))
    d.text(to_px((cx, ped_y + ped_h / 2 + 14)), "SENATVS POPVLVSQVE", font=fi, fill=INK, anchor="mm")
    d.text(to_px((cx, ped_y + ped_h / 2 - 6)), "GAME III . DEITY", font=fi, fill=INK, anchor="mm")
    d.text(to_px((cx, ped_y + ped_h / 2 - 26)), "ROMA CONDITA TVRNO I", font=ImageFont.truetype(FONT, int(11 * SS)), fill=FAINT, anchor="mm")
    # shaft edges
    pen.stroke([(cx - shaft_w / 2, shaft_y0 + 10), (cx - shaft_w / 2, shaft_y1)], 2.0, 2.0, wobble=0.6, taper=False)
    pen.stroke([(cx + shaft_w / 2, shaft_y0 + 10), (cx + shaft_w / 2, shaft_y1)], 2.0, 2.0, wobble=0.6, taper=False)
    # the spiral band: each winding is a sine-curved band crossing the shaft
    for k in range(windings):
        yb = shaft_y0 + 10 + k * wind_h
        pts = [(cx - shaft_w / 2 + t * shaft_w / 24, yb + 18 * math.sin(math.pi * t / 24)) for t in range(25)]
        pen.stroke(pts, 1.3, 1.3, wobble=0.3, taper=False)
        if k == 0:
            # the first winding carries turn 1, compressed into the band
            scene_turn_one(pen, d, to_px, cx - shaft_w / 2 + 6, yb + 22, shaft_w - 12, wind_h - 30, rng)
        else:
            # blank windings: a faint number only
            d.text(to_px((cx, yb + wind_h / 2 + 4)), f"turn {k * 20}", font=ImageFont.truetype(FONT_I, int(10 * SS)), fill=FAINT, anchor="mm")
    # capital and the figure on top (a plain pedestal: the statue is not earned yet)
    cap_y = shaft_y1
    pen.stroke([(cx - shaft_w / 2 - 20, cap_y), (cx + shaft_w / 2 + 20, cap_y), (cx + shaft_w / 2 + 20, cap_y + 26), (cx - shaft_w / 2 - 20, cap_y + 26), (cx - shaft_w / 2 - 20, cap_y)], 2.0, 2.0, wobble=0.4, taper=False)
    pen.stroke([(cx - 30, cap_y + 26), (cx + 30, cap_y + 26), (cx + 30, cap_y + 60), (cx - 30, cap_y + 60), (cx - 30, cap_y + 26)], 1.6, 1.6, wobble=0.4, taper=False)
    d.text(to_px((cx, cap_y + 80)), "(the statue goes up on the day the game is won)", font=ImageFont.truetype(FONT_I, int(10 * SS)), fill=FAINT, anchor="mm")
    # the first winding unrolled, at the right
    ux, uy, uw, uh = 560, 1040, 470, 80
    pen.stroke([(ux, uy), (ux + uw, uy), (ux + uw, uy + uh), (ux, uy + uh), (ux, uy)], 1.4, 1.4, wobble=0.4, taper=False)
    scene_turn_one(pen, d, to_px, ux + 8, uy + 8, uw - 16, uh - 16, rng)
    d.text(to_px((ux, uy + uh + 22)), "THE FIRST WINDING, UNROLLED", font=ImageFont.truetype(FONT_B, int(13 * SS)), fill=INK, anchor="lm")
    d.text(to_px((ux, uy - 16)), "turn 1: the mountain in the west, the river, the hill and the founding, the warriors walking north, the sea.", font=ImageFont.truetype(FONT_I, int(10 * SS)), fill=FAINT, anchor="lm")
    # the legend of the column
    lx = 560
    ly = 880
    lines = [
        ("THE COLUMN", FONT_B, 20, INK),
        ("Game 3 of the Deity campaign, Rome under Trajan.", FONT_I, 12, INK),
        ("Twelve windings for the story, one every twenty turns;", FONT, 11, FAINT),
        ("the first is carved, the rest wait for the game.", FONT, 11, FAINT),
        ("After the column in Trajan's forum, whose band tells", FONT, 11, FAINT),
        ("the Dacian wars scene by scene up the shaft.", FONT, 11, FAINT),
        ("Ink on paper, 2026-10-26, the evening the game began.", FONT, 11, FAINT),
    ]
    yy = ly
    for text, font, size, fill in lines:
        d.text(to_px((lx, yy)), text, font=ImageFont.truetype(font, int(size * SS)), fill=fill, anchor="lm")
        yy -= 20 if size < 14 else 30
    # ground
    pen.stroke([(60, ped_y - 2), (WPX - 60, ped_y - 2)], 1.0, 1.0, wobble=0.8, ink=FAINT, taper=False)
    for k in range(50):
        xx = rng.uniform(70, WPX - 70)
        pen.stroke([(xx, ped_y - 6 + rng.uniform(-3, 3)), (xx + 3, ped_y - 16)], 0.9, 0.4, wobble=0.3, ink=FAINT)
    img.resize((WPX, HPX), Image.LANCZOS).save(HERE / "the-column.png")
    print("ok")


if __name__ == "__main__":
    main()
