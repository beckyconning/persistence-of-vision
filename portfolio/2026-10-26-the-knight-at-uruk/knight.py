"""The Knight at Uruk, turn 122.

A Persian knight at full gallop, one stride in twelve phases after Muybridge's
1878 "Sallie Gardner at a Gallop", drawn in ink on paper against the Ancient
Walls of Uruk (the walls that held a Dutch warrior army for ten turns in
campaign game 2 and fell in one night to this unit). Horse proportions from the
usual equine canon (body and leg lengths as fractions of the 1.55 m withers
height); footfalls from the transverse gallop (LH, RH, LF, RF, then suspension
with the legs gathered, Muybridge's finding); rider from human segment lengths
(Drillis and Contini fractions of a 1.75 m stature). No capsules, no silhouette
fill: every part is a contour drawn as tapered pen strokes, with hidden lines
removed by painting the paper back under each nearer part.
"""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
SS = 3  # supersample
CELL_W, CELL_H = 400, 300  # 1x pixels per frame
SCENE_W = 4.05  # metres across a frame
PX = CELL_W / SCENE_W  # 1x px per metre
GROUND_Y = 0.34  # metres from the frame bottom to the ground line
PAPER = (236, 226, 202)
INK = (34, 27, 20)
INK_FAR = (96, 84, 68)
WALL = (186, 168, 136)
WALL_DARK = (160, 142, 110)

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# ---------------------------------------------------------------- geometry

def lerp(a, b, t):
    return a + (b - a) * t


def catmull(points, n=12, closed=False):
    pts = list(points)
    if closed:
        pts = [pts[-1]] + pts + [pts[0], pts[1]]
    else:
        pts = [pts[0]] + pts + [pts[-1]]
    out = []
    for i in range(1, len(pts) - 2):
        p0, p1, p2, p3 = pts[i - 1], pts[i], pts[i + 1], pts[i + 2]
        for k in range(n):
            t = k / n
            t2, t3 = t * t, t * t * t
            x = 0.5 * ((2 * p1[0]) + (-p0[0] + p2[0]) * t + (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 + (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
            y = 0.5 * ((2 * p1[1]) + (-p0[1] + p2[1]) * t + (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 + (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
            out.append((x, y))
    if not closed:
        out.append(pts[-2])
    return out


def ik2(root, l1, l2, target, bend=1.0):
    """Two-link inverse kinematics. bend=+1 puts the middle joint on the left of
    root->target (seen with y up), -1 on the right."""
    dx, dy = target[0] - root[0], target[1] - root[1]
    d = math.hypot(dx, dy)
    d = max(1e-6, min(d, l1 + l2 - 1e-4))
    a = math.atan2(dy, dx)
    cos_k = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    cos_k = max(-1.0, min(1.0, cos_k))
    k = math.acos(cos_k)
    ang = a + bend * k
    mid = (root[0] + l1 * math.cos(ang), root[1] + l1 * math.sin(ang))
    # re-aim the second link exactly at the (possibly clamped) target
    ang2 = math.atan2(target[1] - mid[1], target[0] - mid[0])
    end = (mid[0] + l2 * math.cos(ang2), mid[1] + l2 * math.sin(ang2))
    return mid, end


def leg_chain(root, lengths, target, first_angle, bend):
    """Three links: the first at a given angle (measured from straight down,
    positive forward), the other two by IK."""
    l1, l2, l3 = lengths
    a = -math.pi / 2 + first_angle
    j1 = (root[0] + l1 * math.cos(a), root[1] + l1 * math.sin(a))
    j2, j3 = ik2(j1, l2, l3, target, bend)
    return [root, j1, j2, j3]


def hoof_path(phase, x_td, x_lo, lift, stance):
    """Hoof position relative to the body: on the ground sliding back during
    stance, then an arc forward during swing."""
    p = phase % 1.0
    if p < stance:
        s = p / stance
        return (lerp(x_td, x_lo, s), 0.0)
    q = (p - stance) / (1.0 - stance)
    # ease: tuck back and up first, then reach forward
    x = lerp(x_lo, x_td, 0.5 - 0.5 * math.cos(math.pi * q))
    y = lift * math.sin(math.pi * q) ** 0.9
    # the hind hoof flicks further back before coming forward
    x -= 0.10 * math.sin(math.pi * q) ** 2 * (1 - q)
    return (x, y)


# ---------------------------------------------------------------- the horse

WITHERS = 1.55
STANCE = 0.32
# footfalls of a right-lead transverse gallop, as fractions of the stride
CONTACT = {"LH": 0.00, "RH": 0.12, "LF": 0.28, "RF": 0.40}
FORE_ROOT = (0.62, 1.10)   # shoulder joint, body frame (metres)
HIND_ROOT = (-0.72, 1.06)  # hip joint
FORE_LEN = (0.33, 0.40, 0.50)   # humerus, forearm, cannon+pastern
HIND_LEN = (0.40, 0.45, 0.50)   # femur, gaskin, cannon+pastern


def horse_pose(t):
    """All joints of the horse in a frame whose origin is on the ground under
    the barrel centre, x forward, y up. Returns a dict."""
    bob = 0.045 * math.cos(2 * math.pi * (t - 0.82))
    pitch = math.radians(3.0) * math.sin(2 * math.pi * (t - 0.30))

    def body(p):
        # rotate about the barrel centre (0, 1.15) by pitch, then bob
        cx, cy = 0.0, 1.15
        x, y = p[0] - cx, p[1] - cy
        xr = x * math.cos(pitch) - y * math.sin(pitch)
        yr = x * math.sin(pitch) + y * math.cos(pitch)
        return (xr + cx, yr + cy + bob)

    legs = {}
    for name, c in CONTACT.items():
        fore = name[1] == "F"
        root = body(FORE_ROOT if fore else HIND_ROOT)
        phase = t - c
        if fore:
            tgt = hoof_path(phase, root[0] + 0.62, root[0] - 0.52, 0.42, STANCE)
        else:
            tgt = hoof_path(phase, root[0] + 0.50, root[0] - 0.70, 0.44, STANCE)
        tgt = (tgt[0], tgt[1] + 0.0)
        # first link swings with the hoof
        if fore:
            # the humerus runs back and down from the shoulder joint to the elbow
            ang = math.radians(max(-60.0, min(-5.0, -35 + 30 * (tgt[0] - root[0]) / 0.6)))
            chain = leg_chain(root, FORE_LEN, tgt, ang, bend=-1.0)  # knee folds back
        else:
            # the femur points forward and down from the hip to the stifle
            ang = math.radians(max(-5.0, min(55.0, 30 + 40 * (tgt[0] - root[0]) / 0.7)))
            chain = leg_chain(root, HIND_LEN, tgt, ang, bend=-1.0)  # hock points back
        legs[name] = chain

    # neck and head: extended forward in suspension, lifts a little mid-stance
    neck_lift = math.radians(8) * math.sin(2 * math.pi * (t - 0.45))
    poll = body((1.30, 1.62 + 0.25 * math.sin(neck_lift)))
    ha = math.radians(-36) + neck_lift
    muzzle = (poll[0] + 0.62 * math.cos(ha), poll[1] + 0.62 * math.sin(ha))
    return {"body": body, "legs": legs, "poll": poll, "muzzle": muzzle, "bob": bob}


def horse_barrel(body):
    """Closed outline of the barrel and quarters (no neck, no legs)."""
    pts = [
        (0.30, 1.55),   # withers
        (-0.10, 1.50),  # back
        (-0.50, 1.52),  # loin
        (-0.80, 1.47),  # croup
        (-1.02, 1.30),  # dock / point of buttock
        (-1.00, 1.08),  # buttock
        (-0.88, 0.92),  # haunch
        (-0.62, 0.84),  # flank
        (-0.25, 0.84),  # belly
        (0.20, 0.82),   # girth
        (0.52, 0.86),   # chest floor
        (0.74, 1.00),   # chest
        (0.76, 1.22),   # point of shoulder
        (0.62, 1.42),   # shoulder
    ]
    return catmull([body(p) for p in pts], n=8, closed=True)


def horse_neck(body, poll, muzzle):
    """Neck from the withers to the poll along its own axis, then a 0.62 m
    head on an axis of its own: forehead, eye, cheek, jaw, chin, nostril."""
    base_top = body((0.34, 1.57))
    base_bot = body((0.80, 1.18))
    # neck axis
    ndx, ndy = poll[0] - base_top[0], poll[1] - base_top[1]
    nL = math.hypot(ndx, ndy) or 1e-6
    nux, nuy = ndx / nL, ndy / nL
    nnx, nny = nuy, -nux  # normal pointing down-forward (under the neck)
    throat = (poll[0] + 0.26 * nnx + 0.02 * nux, poll[1] + 0.26 * nny + 0.02 * nuy)
    crest_mid = (lerp(base_top[0], poll[0], 0.5) - 0.03 * nnx, lerp(base_top[1], poll[1], 0.5) - 0.03 * nny)
    under_mid = (lerp(base_bot[0], throat[0], 0.5) + 0.04 * nnx, lerp(base_bot[1], throat[1], 0.5) + 0.04 * nny)
    # head axis
    dx, dy = muzzle[0] - poll[0], muzzle[1] - poll[1]
    L = math.hypot(dx, dy) or 1e-6
    ux, uy = dx / L, dy / L
    nx, ny = -uy, ux  # normal pointing up (forehead side)
    forehead = (poll[0] + 0.14 * ux + 0.06 * nx, poll[1] + 0.14 * uy + 0.06 * ny)
    nose_top = (poll[0] + 0.50 * ux + 0.03 * nx, poll[1] + 0.50 * uy + 0.03 * ny)
    nose_tip = (muzzle[0] + 0.01 * ux - 0.02 * nx, muzzle[1] + 0.01 * uy - 0.02 * ny)
    chin = (poll[0] + 0.56 * ux - 0.13 * nx, poll[1] + 0.56 * uy - 0.13 * ny)
    jaw = (poll[0] + 0.36 * ux - 0.19 * nx, poll[1] + 0.36 * uy - 0.19 * ny)
    cheek = (poll[0] + 0.16 * ux - 0.25 * nx, poll[1] + 0.16 * uy - 0.25 * ny)
    outline = [base_top, crest_mid, poll, forehead, nose_top, nose_tip, chin, jaw, cheek, throat, under_mid, base_bot]
    ear_base = (poll[0] - 0.01 * ux + 0.01 * nx, poll[1] - 0.01 * uy + 0.01 * ny)
    ear_tip = (poll[0] - 0.11 * ux + 0.15 * nx, poll[1] - 0.11 * uy + 0.15 * ny)
    eye = (poll[0] + 0.19 * ux - 0.04 * nx, poll[1] + 0.19 * uy - 0.04 * ny)
    return catmull(outline, n=8, closed=True), (ear_base, ear_tip), eye, (ux, uy, nx, ny)


def limb_polygon(chain, widths, hoof=True):
    """Contour of a limb from its joints and (front, back) half-widths."""
    n = len(chain)
    dirs = []
    for i in range(n - 1):
        dx, dy = chain[i + 1][0] - chain[i][0], chain[i + 1][1] - chain[i][1]
        L = math.hypot(dx, dy) or 1e-6
        dirs.append((dx / L, dy / L))
    front, back = [], []
    for i in range(n):
        if i == 0:
            d = dirs[0]
        elif i == n - 1:
            d = dirs[-1]
        else:
            # bisector of the two bone normals; at a sharp fold fall back to the lower bone
            n0 = (-dirs[i - 1][1], dirs[i - 1][0])
            n1 = (-dirs[i][1], dirs[i][0])
            bx, by = n0[0] + n1[0], n0[1] + n1[1]
            L = math.hypot(bx, by)
            if L < 0.35:
                d = dirs[i]
            else:
                d = (by / L, -bx / L)  # a direction whose left normal is the bisector
        # the dorsal (front) side of a bone is its left normal when it points down;
        # it turns with the bone when the leg folds, as the real surface does
        nx, ny = -d[1], d[0]
        wf, wb = widths[i]
        front.append((chain[i][0] + nx * wf, chain[i][1] + ny * wf))
        back.append((chain[i][0] - nx * wb, chain[i][1] - ny * wb))
    if hoof:
        d = dirs[-1]
        toe = (chain[-1][0] + d[0] * 0.08 + d[1] * 0.07, chain[-1][1] + d[1] * 0.08 - d[0] * 0.07)
        heel = (chain[-1][0] + d[0] * 0.07 - d[1] * 0.06, chain[-1][1] + d[1] * 0.07 + d[0] * 0.06)
        return front + [toe, heel] + list(reversed(back))
    return front + list(reversed(back))


FORE_W = [(0.10, 0.10), (0.085, 0.075), (0.052, 0.062), (0.046, 0.046)]
HIND_W = [(0.17, 0.12), (0.11, 0.11), (0.052, 0.085), (0.046, 0.046)]

# ---------------------------------------------------------------- the rider

H = 1.75
R_TORSO, R_THIGH, R_SHIN, R_UARM, R_FARM, R_HEAD = 0.288 * H, 0.245 * H, 0.246 * H, 0.186 * H, 0.146 * H, 0.130 * H


def rider_pose(body, t):
    seat = body((-0.12, 1.50))
    lean = math.radians(34 + 3 * math.sin(2 * math.pi * (t - 0.6)))
    shoulder = (seat[0] + R_TORSO * math.sin(lean), seat[1] + R_TORSO * math.cos(lean))
    neck = (shoulder[0] + 0.06 * math.sin(lean), shoulder[1] + 0.06 * math.cos(lean))
    head_c = (neck[0] + 0.12 * math.sin(lean - 0.2), neck[1] + 0.12 * math.cos(lean - 0.2))
    hip = (seat[0] + 0.02, seat[1] - 0.04)
    knee = (hip[0] + R_THIGH * math.sin(math.radians(62)), hip[1] - R_THIGH * math.cos(math.radians(62)))
    foot = (knee[0] - R_SHIN * math.sin(math.radians(22)), knee[1] - R_SHIN * math.cos(math.radians(22)))
    elbow = (shoulder[0] - R_UARM * math.sin(math.radians(18)), shoulder[1] - R_UARM * math.cos(math.radians(18)))
    hand = (elbow[0] + R_FARM * math.cos(math.radians(-28)), elbow[1] + R_FARM * math.sin(math.radians(-28)))
    # lance: couched under the arm, from behind the elbow to past the muzzle
    la = math.radians(-13)
    lx, ly = math.cos(la), math.sin(la)
    lance_tail = (hand[0] - 0.9 * lx, hand[1] - 0.9 * ly)
    lance_tip = (hand[0] + 2.35 * lx, hand[1] + 2.35 * ly)
    return {"seat": seat, "shoulder": shoulder, "neck": neck, "head": head_c, "hip": hip, "knee": knee,
            "foot": foot, "elbow": elbow, "hand": hand, "lance": (lance_tail, lance_tip, lx, ly), "lean": lean}


# ---------------------------------------------------------------- drawing

class Pen:
    def __init__(self, draw: ImageDraw.ImageDraw, to_px, rng: random.Random, ink=None):
        self.d = draw
        self.to_px = to_px
        self.rng = rng
        self.ink = ink or INK  # resolved at call time, so a palette swap on the module takes

    def stroke(self, pts, w0, w1, wobble=0.004, ink=None, taper=True):
        """A tapered ink stroke along a polyline (scene coords, metres)."""
        ink = ink or self.ink
        if len(pts) < 2:
            return
        # resample
        seg = []
        total = 0.0
        for i in range(len(pts) - 1):
            L = math.hypot(pts[i + 1][0] - pts[i][0], pts[i + 1][1] - pts[i][1])
            seg.append(L)
            total += L
        if total < 1e-6:
            return
        n = max(4, int(total / 0.012))
        samp = []
        dist = 0.0
        i = 0
        acc = 0.0
        for k in range(n + 1):
            s = total * k / n
            while i < len(seg) - 1 and acc + seg[i] < s:
                acc += seg[i]
                i += 1
            u = (s - acc) / (seg[i] or 1e-6)
            u = max(0.0, min(1.0, u))
            samp.append((lerp(pts[i][0], pts[i + 1][0], u), lerp(pts[i][1], pts[i + 1][1], u)))
        left, right = [], []
        drift = 0.0
        for k, p in enumerate(samp):
            s = k / n
            a = samp[max(0, k - 1)]
            b = samp[min(n, k + 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            L = math.hypot(dx, dy) or 1e-6
            nx, ny = -dy / L, dx / L
            w = lerp(w0, w1, s)
            if taper:
                w *= (0.35 + 0.65 * math.sin(math.pi * s) ** 0.55)
            drift = 0.7 * drift + self.rng.uniform(-wobble, wobble)
            px, py = p[0] + nx * drift, p[1] + ny * drift
            left.append((px + nx * w, py + ny * w))
            right.append((px - nx * w, py - ny * w))
        poly = [self.to_px(q) for q in left + list(reversed(right))]
        self.d.polygon(poly, fill=ink)

    def outline(self, poly, w, ink=None, pieces=3, fill="paper", wobble=0.004):
        """Paint the paper back under a part, then draw its contour as a few
        overlapping pen strokes."""
        if fill == "paper":
            fill = PAPER
        if fill is not None:
            self.d.polygon([self.to_px(p) for p in poly], fill=fill)
        n = len(poly)
        closed = poly + poly[:1]
        start = self.rng.randrange(n)
        step = n // pieces
        for k in range(pieces):
            a = start + k * step - self.rng.randrange(0, max(1, step // 6))
            b = start + (k + 1) * step + self.rng.randrange(0, max(1, step // 5))
            seg = [closed[i % n] for i in range(a, b + 1)]
            self.stroke(seg, w * self.rng.uniform(0.75, 1.1), w * self.rng.uniform(0.75, 1.1), wobble=wobble, ink=ink)


WALL_TOP = 2.35
MERLONS = True
EXTRA = None
SKIP_HORSE = False


def draw_wall(d, to_px, frame_w, frame_h, rng):
    """The Ancient Walls as the Muybridge backdrop: ashlar courses, a parapet,
    the ground line."""
    course = 0.33
    block = 0.72
    top = WALL_TOP
    # wall face
    y = 0.0
    row = 0
    while y < top:
        d.line([to_px((-5, y)), to_px((5, y))], fill=WALL, width=max(1, int(0.9 * SS)))
        off = (row % 2) * block / 2
        x = -5 + off
        while x < 5:
            d.line([to_px((x, y)), to_px((x, min(y + course, top)))], fill=WALL, width=max(1, int(0.9 * SS)))
            x += block
        y += course
        row += 1
    d.line([to_px((-5, top)), to_px((5, top))], fill=WALL_DARK, width=max(1, int(1.4 * SS)))
    # merlons
    x = -5 + 0.15
    while MERLONS and x < 5:
        d.rectangle([to_px((x, top + 0.26)), to_px((x + 0.45, top))], outline=WALL_DARK, width=max(1, int(1.2 * SS)))
        x += 0.9
    # ground line
    d.line([to_px((-5, 0)), to_px((5, 0))], fill=INK_FAR, width=max(1, int(1.6 * SS)))


def render_frame(t, rng_seed, number=None, px_w=CELL_W, px_h=CELL_H):
    W, Hh = px_w * SS, px_h * SS
    img = Image.new("RGB", (W, Hh), PAPER)
    d = ImageDraw.Draw(img)
    rng = random.Random(rng_seed)

    scale = PX * SS
    ox = W * 0.43
    oy = Hh - GROUND_Y * scale

    def to_px(p):
        return (ox + p[0] * scale, oy - p[1] * scale)

    draw_wall(d, to_px, W, Hh, rng)

    hp = horse_pose(t)
    body = hp["body"]
    legs = hp["legs"]
    pen = Pen(d, to_px, rng)
    far = Pen(d, to_px, rng, ink=INK_FAR)
    w_main = 0.011
    w_far = 0.008

    if SKIP_HORSE:
        if EXTRA is not None:
            EXTRA(pen, far, d, to_px, body, t)
        if number is not None:
            font = ImageFont.truetype(FONT_PATH, int(15 * SS))
            d.text((int(8 * SS), int(5 * SS)), str(number), font=font, fill=INK)
        return img.resize((px_w, px_h), Image.LANCZOS)

    # far legs first (the right side)
    for name, widths in (("RH", HIND_W), ("RF", FORE_W)):
        far.outline(limb_polygon(legs[name], widths), w_far, pieces=2)

    # tail
    dock = body((-1.00, 1.34))
    for k in range(5):
        a = math.radians(178 + rng.uniform(-6, 6) + 7 * k)
        L = rng.uniform(0.70, 0.95)
        mid = (dock[0] + 0.5 * L * math.cos(a), dock[1] + 0.5 * L * math.sin(a) + 0.06 + rng.uniform(-0.03, 0.03))
        end = (dock[0] + L * math.cos(a), dock[1] + L * math.sin(a) - 0.10)
        pen.stroke(catmull([dock, mid, end], n=8), 0.006, 0.002, wobble=0.006)

    # barrel
    barrel = horse_barrel(body)
    pen.outline(barrel, w_main, pieces=4)
    # modelling lines: shoulder blade, flank, stifle
    pen.stroke(catmull([body((0.55, 1.40)), body((0.42, 1.18)), body((0.50, 0.98))], n=8), 0.006, 0.003, wobble=0.004)
    pen.stroke(catmull([body((-0.60, 1.40)), body((-0.70, 1.15)), body((-0.60, 0.95))], n=8), 0.006, 0.003, wobble=0.004)
    pen.stroke(catmull([body((-0.20, 0.95)), body((0.05, 1.00))], n=6), 0.004, 0.002)

    # near legs
    for name, widths in (("LH", HIND_W), ("LF", FORE_W)):
        poly = limb_polygon(legs[name], widths)
        pen.outline(poly, w_main, pieces=3)
        ch = legs[name]
        # tendon line down the back of the cannon
        a, b = ch[2], ch[3]
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy) or 1e-6
        nx, ny = -dy / L, dx / L
        pen.stroke([(a[0] - nx * 0.03, a[1] - ny * 0.03), (b[0] - nx * 0.028 + dx * 0.1 / L, b[1] - ny * 0.028 + dy * 0.1 / L)], 0.004, 0.002)

    # neck and head
    neck, ear, eye, (ux, uy, nx, ny) = horse_neck(body, hp["poll"], hp["muzzle"])
    pen.outline(neck, w_main, pieces=4)
    pen.stroke([ear[0], ear[1], (ear[0][0] + 0.07 * ux, ear[0][1] + 0.07 * uy)], 0.007, 0.004)
    d.ellipse([to_px((eye[0] - 0.022, eye[1] + 0.022)), to_px((eye[0] + 0.022, eye[1] - 0.022))], fill=INK)
    # nostril, mouth
    m = hp["muzzle"]
    pen.stroke([(m[0] - 0.06 * ux + 0.05 * nx, m[1] - 0.06 * uy + 0.05 * ny), (m[0] - 0.02 * ux + 0.02 * nx, m[1] - 0.02 * uy + 0.02 * ny)], 0.005, 0.003)
    pen.stroke([(m[0] - 0.14 * ux - 0.05 * nx, m[1] - 0.14 * uy - 0.05 * ny), (m[0] - 0.03 * ux - 0.05 * nx, m[1] - 0.03 * uy - 0.05 * ny)], 0.004, 0.002)
    # mane
    for k in range(7):
        s = 0.12 + 0.12 * k
        bt = body((0.34, 1.57))
        base = (lerp(bt[0], hp["poll"][0], s), lerp(bt[1], hp["poll"][1], s) + 0.04)
        pen.stroke(catmull([base, (base[0] - 0.14, base[1] + 0.09 + rng.uniform(-0.03, 0.03)), (base[0] - 0.30, base[1] + 0.06)], n=6), 0.006, 0.002, wobble=0.006)

    # rider
    rp = rider_pose(body, t)
    lean = rp["lean"]
    # torso polygon (back and chest contours)
    seat, sh = rp["seat"], rp["shoulder"]
    ax, ay = math.sin(lean), math.cos(lean)   # along the spine
    bx, by = ay, -ax                           # toward the chest (forward)
    torso = [
        (seat[0] - 0.15 * bx, seat[1] - 0.15 * by),
        (seat[0] + 0.28 * ax - 0.19 * bx, seat[1] + 0.28 * ay - 0.19 * by),
        (sh[0] - 0.16 * bx, sh[1] - 0.16 * by),
        (sh[0] + 0.05 * ax + 0.02 * bx, sh[1] + 0.05 * ay + 0.02 * by),
        (sh[0] + 0.17 * bx, sh[1] + 0.17 * by),
        (seat[0] + 0.28 * ax + 0.20 * bx, seat[1] + 0.28 * ay + 0.20 * by),
        (seat[0] + 0.15 * bx, seat[1] + 0.15 * by),
    ]
    pen.outline(catmull(torso, n=6, closed=True), w_main, pieces=3)
    # near thigh and shin
    hip, knee, foot = rp["hip"], rp["knee"], rp["foot"]
    thigh = limb_polygon([hip, knee], [(0.085, 0.085), (0.06, 0.06)], hoof=False)
    pen.outline(thigh, w_main, pieces=2)
    shin = limb_polygon([knee, foot], [(0.055, 0.06), (0.045, 0.045)], hoof=False)
    pen.outline(shin, w_main, pieces=2)
    pen.stroke([foot, (foot[0] + 0.16, foot[1] - 0.04)], 0.012, 0.008)  # boot
    # head: helmet with a nasal, a neck
    hc = rp["head"]
    r = R_HEAD * 0.5
    head = [(hc[0] + r * math.cos(a) * 0.92, hc[1] + r * math.sin(a)) for a in [i * 2 * math.pi / 18 for i in range(18)]]
    pen.outline(head, w_main, pieces=2)
    # conical helm
    helm = [(hc[0] - r * 0.95, hc[1] + 0.02), (hc[0] - 0.03, hc[1] + r + 0.17), (hc[0] + r * 0.95, hc[1] + 0.02)]
    pen.outline(catmull(helm, n=6, closed=True), w_main, pieces=2)
    pen.stroke([(hc[0] + r * 0.6, hc[1] + 0.02), (hc[0] + r * 0.55, hc[1] - 0.08)], 0.006, 0.004)  # nasal
    # near arm and the couched lance
    el, hand = rp["elbow"], rp["hand"]
    uarm = limb_polygon([sh, el], [(0.055, 0.055), (0.04, 0.04)], hoof=False)
    pen.outline(uarm, w_main, pieces=2)
    farm = limb_polygon([el, hand], [(0.045, 0.045), (0.035, 0.035)], hoof=False)
    pen.outline(farm, w_main, pieces=2)
    tail_, tip, lx, ly = rp["lance"]
    pen.stroke([tail_, tip], 0.012, 0.006, wobble=0.002, taper=False)
    # lance head
    pen.stroke([(tip[0] - 0.2 * lx, tip[1] - 0.2 * ly), (tip[0] + 0.1 * lx, tip[1] + 0.1 * ly)], 0.02, 0.002, taper=False)
    # fist
    d.ellipse([to_px((hand[0] - 0.04, hand[1] + 0.04)), to_px((hand[0] + 0.04, hand[1] - 0.04))], fill=PAPER, outline=INK, width=int(2 * SS))

    if EXTRA is not None:
        EXTRA(pen, far, d, to_px, body, t)

    # frame number
    if number is not None:
        font = ImageFont.truetype(FONT_PATH, int(15 * SS))
        d.text((int(8 * SS), int(5 * SS)), str(number), font=font, fill=INK)

    # paper grain and a soft vignette, then downsample
    out = img.resize((px_w, px_h), Image.LANCZOS)
    return out


def paper_texture(img: Image.Image, seed=7):
    import numpy as np
    rng = np.random.default_rng(seed)
    a = np.asarray(img).astype(np.float32)
    h, w = a.shape[:2]
    grain = rng.normal(0, 3.2, (h, w, 1)).astype(np.float32)
    yy, xx = np.mgrid[0:h, 0:w]
    vign = 1.0 - 0.10 * (((xx / w - 0.5) ** 2 + (yy / h - 0.5) ** 2) * 2.2)
    a = a * vign[..., None] + grain
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def plate(path: Path):
    cols, rows = 6, 2
    gap, margin = 10, 36
    caption_h = 150
    W = margin * 2 + cols * CELL_W + (cols - 1) * gap
    Hh = margin * 2 + rows * CELL_H + (rows - 1) * gap + caption_h
    sheet = Image.new("RGB", (W, Hh), PAPER)
    frames = []
    for i in range(12):
        t = i / 12
        fr = render_frame(t, rng_seed=100 + i, number=i + 1)
        frames.append(fr)
        c, r = i % cols, i // cols
        x = margin + c * (CELL_W + gap)
        y = margin + r * (CELL_H + gap)
        sheet.paste(fr, (x, y))
        ImageDraw.Draw(sheet).rectangle([x, y, x + CELL_W - 1, y + CELL_H - 1], outline=INK_FAR, width=1)
    d = ImageDraw.Draw(sheet)
    title_f = ImageFont.truetype(FONT_BOLD, 22)
    body_f = ImageFont.truetype(FONT_PATH, 15)
    y0 = margin + rows * CELL_H + (rows - 1) * gap + 22
    d.text((margin, y0), "THE KNIGHT AT URUK, TURN 122.  Transverse gallop, one stride in twelve phases, after Muybridge (1878).", font=title_f, fill=INK)
    lines = [
        "Behind him the Ancient Walls of Uruk, bought on turn 70, which held a Dutch army of warriors for ten turns until white peace on turn 83.",
        "Cyrus declared on turn 121. Overnight into turn 123 the walls saw two knights (50), three men-at-arms (45), a pikeman (45), a horseman (36),",
        "two heavy chariots (28), a crossbowman (30/40) and two catapults (25). The walls were gone on turn 124. Uruk fell on turn 125. Walls are era-relative.",
    ]
    for k, line in enumerate(lines):
        d.text((margin, y0 + 36 + k * 22), line, font=body_f, fill=INK)
    d.text((W - margin - 300, Hh - margin - 2), "campaign game 2, Sumeria, 2026-10-26", font=body_f, fill=INK_FAR)
    sheet = paper_texture(sheet)
    sheet.save(path, quality=92)
    return frames


def film(path_gif: Path, path_mp4: Path, n=24, stride_s=0.5):
    frames = []
    for i in range(n):
        t = i / n
        fr = render_frame(t, rng_seed=300 + i, number=None, px_w=CELL_W * 2, px_h=CELL_H * 2)
        frames.append(paper_texture(fr, seed=i))
    ms = int(1000 * stride_s / n)
    frames[0].save(path_gif, save_all=True, append_images=frames[1:], duration=ms, loop=0, optimize=False)
    tmp = path_gif.parent / "_film"
    tmp.mkdir(exist_ok=True)
    for i, fr in enumerate(frames):
        fr.save(tmp / f"f{i:03d}.png")
    import subprocess
    fps = n / stride_s
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(fps), "-i", str(tmp / "f%03d.png"),
                    "-stream_loop", "5", "-i", str(tmp / "f%03d.png"), "-framerate", str(fps),
                    "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0,format=yuv420p", str(path_mp4)], check=False)
    for f in tmp.glob("*.png"):
        f.unlink()
    tmp.rmdir()


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "plate"
    if what in ("plate", "all"):
        plate(HERE / "the-knight-at-uruk.png")
    if what in ("one",):
        render_frame(float(sys.argv[2]) if len(sys.argv) > 2 else 0.1, 1, number=1, px_w=800, px_h=600).save(HERE / "test.png")
    if what in ("film", "all"):
        film(HERE / "the-knight-at-uruk.gif", HERE / "the-knight-at-uruk.mp4")
