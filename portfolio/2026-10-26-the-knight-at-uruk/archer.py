"""Uruk, turn 123: the garrison. The gathered knight (phase 0.85 of the stride)
under the parapet, and the city's whole defence above him: Ancient Walls and one
archer, drawn from the same Drillis and Contini proportions as the rider."""
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import knight as K

HERE = Path(__file__).resolve().parent
H = 1.75
TORSO, THIGH, SHIN, UARM, FARM, HEAD = 0.288 * H, 0.245 * H, 0.246 * H, 0.186 * H, 0.146 * H, 0.130 * H
WALL_TOP = 2.0


def draw_archer(pen, far, d, to_px, body, t):
    x0 = 1.40  # standing ahead of the knight, facing him (left)
    top = WALL_TOP
    hip = (x0, top + THIGH * 0.98 + SHIN * 0.98)
    # legs: a braced stance, front foot toward the knight
    feet = [(x0 - 0.22, top), (x0 + 0.16, top)]
    legs = []
    for ft in feet:
        knee, foot = K.ik2(hip, THIGH, SHIN, ft, bend=1.0)  # knee forward (left)
        legs.append((hip, knee, foot))
    # torso leaning slightly back, shoulders
    lean = math.radians(-8)
    sh = (hip[0] + TORSO * math.sin(lean), hip[1] + TORSO * math.cos(lean))
    # aim line toward the knight's chest, 32 degrees below horizontal to the left
    aim = math.radians(180 + 52)
    ax, ay = math.cos(aim), math.sin(aim)
    bow_hand = (sh[0] + (UARM + FARM) * 0.96 * ax, sh[1] + (UARM + FARM) * 0.96 * ay)
    draw_hand = (sh[0] - 0.02 * ax + 0.02, sh[1] - 0.02 * ay + 0.08)  # at the cheek
    elbow_draw = (sh[0] + 0.30, sh[1] + 0.06)
    head = (sh[0] + 0.02, sh[1] + 0.21)

    # far leg first
    far.outline(K.limb_polygon(legs[1][:2], [(0.085, 0.085), (0.06, 0.06)], hoof=False), 0.008, pieces=2)
    far.outline(K.limb_polygon(legs[1][1:], [(0.055, 0.06), (0.045, 0.045)], hoof=False), 0.008, pieces=2)
    # far (draw) arm: upper arm goes back, forearm comes to the cheek
    far.outline(K.limb_polygon([sh, elbow_draw], [(0.055, 0.055), (0.04, 0.04)], hoof=False), 0.008, pieces=2)
    # torso
    bx, by = math.cos(lean), -math.sin(lean)
    torso = [
        (hip[0] - 0.15 * bx, hip[1] - 0.15 * by),
        (hip[0] + 0.28 * math.sin(lean) - 0.17 * bx, hip[1] + 0.28 * math.cos(lean) - 0.17 * by),
        (sh[0] - 0.19 * bx, sh[1] - 0.19 * by),
        (sh[0] + 0.05 * math.sin(lean), sh[1] + 0.05 * math.cos(lean)),
        (sh[0] + 0.19 * bx, sh[1] + 0.19 * by),
        (hip[0] + 0.28 * math.sin(lean) + 0.17 * bx, hip[1] + 0.28 * math.cos(lean) + 0.17 * by),
        (hip[0] + 0.15 * bx, hip[1] + 0.15 * by),
    ]
    pen.outline(K.catmull(torso, n=6, closed=True), 0.011, pieces=3)
    # near leg
    pen.outline(K.limb_polygon(legs[0][:2], [(0.085, 0.085), (0.06, 0.06)], hoof=False), 0.011, pieces=2)
    pen.outline(K.limb_polygon(legs[0][1:], [(0.055, 0.06), (0.045, 0.045)], hoof=False), 0.011, pieces=2)
    pen.stroke([legs[0][2], (legs[0][2][0] - 0.18, legs[0][2][1] + 0.02)], 0.012, 0.008)
    # head and cap
    r = HEAD * 0.5
    pen.outline([(head[0] + r * 0.92 * math.cos(a), head[1] + r * math.sin(a)) for a in [i * 2 * math.pi / 18 for i in range(18)]], 0.011, pieces=2)
    pen.outline(K.catmull([(head[0] - r, head[1] + 0.03), (head[0], head[1] + r + 0.06), (head[0] + r, head[1] + 0.03)], n=6, closed=True), 0.011, pieces=2)
    # forearm of the draw arm comes in front of the face to the cheek
    pen.outline(K.limb_polygon([elbow_draw, draw_hand], [(0.045, 0.045), (0.035, 0.035)], hoof=False), 0.011, pieces=2)
    # bow arm
    pen.outline(K.limb_polygon([sh, (sh[0] + UARM * ax, sh[1] + UARM * ay)], [(0.055, 0.055), (0.045, 0.045)], hoof=False), 0.011, pieces=2)
    pen.outline(K.limb_polygon([(sh[0] + UARM * ax, sh[1] + UARM * ay), bow_hand], [(0.045, 0.045), (0.035, 0.035)], hoof=False), 0.011, pieces=2)
    # bow: an arc perpendicular to the aim, 1.6 m tip to tip, bellied toward the knight
    nx, ny = -ay, ax
    tip1 = (bow_hand[0] + 0.62 * nx - 0.10 * ax, bow_hand[1] + 0.62 * ny - 0.10 * ay)
    tip2 = (bow_hand[0] - 0.62 * nx - 0.10 * ax, bow_hand[1] - 0.62 * ny - 0.10 * ay)
    belly = (bow_hand[0] + 0.05 * ax, bow_hand[1] + 0.05 * ay)
    pen.stroke(K.catmull([tip1, (bow_hand[0] + 0.35 * nx + 0.04 * ax, bow_hand[1] + 0.35 * ny + 0.04 * ay), belly,
                          (bow_hand[0] - 0.35 * nx + 0.04 * ax, bow_hand[1] - 0.35 * ny + 0.04 * ay), tip2], n=10), 0.012, 0.012, wobble=0.002, taper=False)
    # string to the draw hand, arrow along the aim
    pen.stroke([tip1, draw_hand], 0.003, 0.003, wobble=0.001, taper=False)
    pen.stroke([tip2, draw_hand], 0.003, 0.003, wobble=0.001, taper=False)
    pen.stroke([draw_hand, (bow_hand[0] + 0.22 * ax, bow_hand[1] + 0.22 * ay)], 0.005, 0.004, wobble=0.001, taper=False)
    pen.stroke([(draw_hand[0] - 0.02 * ax + 0.03 * nx, draw_hand[1] - 0.02 * ay + 0.03 * ny), (draw_hand[0] + 0.10 * ax, draw_hand[1] + 0.10 * ay),
                (draw_hand[0] - 0.02 * ax - 0.03 * nx, draw_hand[1] - 0.02 * ay - 0.03 * ny)], 0.004, 0.004, taper=False)
    # merlons last, filled with paper so they hide the archer's shins
    x = -5 + 0.15
    while x < 5:
        d.rectangle([to_px((x, top + 0.26)), to_px((x + 0.45, top))], fill=K.PAPER, outline=K.WALL_DARK, width=int(1.2 * K.SS))
        x += 0.9


def main():
    K.WALL_TOP = WALL_TOP
    K.MERLONS = False
    K.EXTRA = draw_archer
    K.SCENE_W = 3.6
    K.PX = 1000 / K.SCENE_W
    K.GROUND_Y = 0.30
    img = K.render_frame(0.85, rng_seed=777, number=None, px_w=1000, px_h=1250)
    sheet = Image.new("RGB", (1000 + 60, 1250 + 150), K.PAPER)
    sheet.paste(img, (30, 30))
    d = ImageDraw.Draw(sheet)
    d.rectangle([30, 30, 1029, 1279], outline=K.INK_FAR, width=1)
    tf = ImageFont.truetype(K.FONT_BOLD, 22)
    bf = ImageFont.truetype(K.FONT_PATH, 15)
    d.text((30, 1300), "URUK, TURN 123.  The garrison: Ancient Walls and one archer.", font=tf, fill=K.INK)
    d.text((30, 1338), "The same morning as the plate. Inside the walls, one archer per city; outside, the war-cart and both field archers had died in the night.", font=bf, fill=K.INK)
    d.text((30, 1360), "campaign game 2, Sumeria, 2026-10-26", font=bf, fill=K.INK_FAR)
    sheet = K.paper_texture(sheet, seed=11)
    sheet.save(HERE / "the-garrison.png")


if __name__ == "__main__":
    main()
