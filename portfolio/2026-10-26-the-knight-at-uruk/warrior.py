"""Ten turns at the wall: the Dutch warrior of turns 73 to 83, one walking stride in
ten frames (one per turn), from the same human proportions as the rider and the
archer. He never got past the Ancient Walls; white peace came on turn 83."""
import math
from PIL import Image, ImageDraw, ImageFont
import knight as K

H = 1.75
TORSO, THIGH, SHIN, UARM, FARM, HEAD = 0.288 * H, 0.245 * H, 0.246 * H, 0.186 * H, 0.146 * H, 0.130 * H
STANCE = 0.60


def foot_path(phase, reach=0.36, lift=0.13):
    p = phase % 1.0
    if p < STANCE:
        return (reach - 2 * reach * p / STANCE, 0.0)
    q = (p - STANCE) / (1 - STANCE)
    return (-reach + 2 * reach * (0.5 - 0.5 * math.cos(math.pi * q)), lift * math.sin(math.pi * q))


def draw_warrior(pen, far, d, to_px, body, t):
    x0 = 0.0
    hip = (x0, THIGH + SHIN - 0.02 - 0.02 * math.cos(4 * math.pi * t))
    legs = {}
    for name, off in (("far", 0.5), ("near", 0.0)):
        fx, fy = foot_path(t + off)
        foot = (x0 + fx, fy + 0.03)
        knee, foot = K.ik2(hip, THIGH, SHIN, foot, bend=1.0)
        legs[name] = (hip, knee, foot)
    lean = math.radians(6)
    sh = (hip[0] + TORSO * math.sin(lean), hip[1] + TORSO * math.cos(lean))
    head = (sh[0] + 0.03, sh[1] + 0.20)
    arms = {}
    for name, off in (("far", 0.0), ("near", 0.5)):
        swing = math.radians(28) * math.sin(2 * math.pi * (t + off))
        el = (sh[0] + UARM * math.sin(swing), sh[1] - UARM * math.cos(swing))
        hd = (el[0] + FARM * math.sin(swing + 0.6), el[1] - FARM * math.cos(swing + 0.6))
        arms[name] = (sh, el, hd)

    def leg(p, which):
        p.outline(K.limb_polygon(legs[which][:2], [(0.085, 0.085), (0.06, 0.06)], hoof=False), 0.011 if which == "near" else 0.008, pieces=2)
        p.outline(K.limb_polygon(legs[which][1:], [(0.055, 0.06), (0.045, 0.045)], hoof=False), 0.011 if which == "near" else 0.008, pieces=2)
        f = legs[which][2]
        p.stroke([f, (f[0] + 0.19, f[1] + 0.01)], 0.012, 0.008)

    def arm(p, which):
        s_, e, h = arms[which]
        p.outline(K.limb_polygon([s_, e], [(0.055, 0.055), (0.04, 0.04)], hoof=False), 0.011 if which == "near" else 0.008, pieces=2)
        p.outline(K.limb_polygon([e, h], [(0.045, 0.045), (0.035, 0.035)], hoof=False), 0.011 if which == "near" else 0.008, pieces=2)
        return h

    leg(far, "far")
    hf = arm(far, "far")
    # shield on the far arm: a round disc
    far.outline([(hf[0] + 0.30 * math.cos(a), hf[1] + 0.30 * math.sin(a)) for a in [i * 2 * math.pi / 24 for i in range(24)]], 0.008, pieces=2)
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
    leg(pen, "near")
    r = HEAD * 0.5
    pen.outline([(head[0] + r * 0.92 * math.cos(a), head[1] + r * math.sin(a)) for a in [i * 2 * math.pi / 18 for i in range(18)]], 0.011, pieces=2)
    pen.stroke([(head[0] - r, head[1] + 0.02), (head[0] - r * 0.6, head[1] + r + 0.03), (head[0] + r * 0.5, head[1] + r + 0.02)], 0.009, 0.005)  # hair
    hn = arm(pen, "near")
    # club in the near hand, resting on the shoulder when the arm is back
    pen.stroke([(hn[0] - 0.08, hn[1] - 0.12), (hn[0] + 0.18, hn[1] + 0.55)], 0.014, 0.026, taper=False)


def main():
    K.EXTRA = draw_warrior
    K.SCENE_W = 2.6
    K.PX = 360 / K.SCENE_W
    K.GROUND_Y = 0.25
    K.SKIP_HORSE = True
    frames = [K.render_frame(i / 10, rng_seed=900 + i, number=73 + i, px_w=360, px_h=330) for i in range(10)]
    cols, gap, m = 5, 10, 36
    W = m * 2 + cols * 360 + (cols - 1) * gap
    Hh = m * 2 + 2 * 330 + gap + 110
    sheet = Image.new("RGB", (W, Hh), K.PAPER)
    for i, f in enumerate(frames):
        x = m + (i % cols) * (360 + gap); y = m + (i // cols) * (330 + gap)
        sheet.paste(f, (x, y)); ImageDraw.Draw(sheet).rectangle([x, y, x + 359, y + 329], outline=K.INK_FAR, width=1)
    d = ImageDraw.Draw(sheet)
    y0 = m + 2 * 330 + gap + 20
    d.text((m, y0), "TEN TURNS AT THE WALL.  The Dutch warrior, turns 73 to 83, one stride in ten frames, one per turn.", font=ImageFont.truetype(K.FONT_BOLD, 20), fill=K.INK)
    d.text((m, y0 + 34), "He never got past the Ancient Walls. White peace on turn 83. The same walls, thirty-nine turns before the knight.", font=ImageFont.truetype(K.FONT_PATH, 15), fill=K.INK)
    K.paper_texture(sheet, seed=9).save(K.HERE / "ten-turns-at-the-wall.png")


if __name__ == "__main__":
    main()
