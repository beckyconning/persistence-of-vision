"""inkfigure: contour figure drawing in ink, from a joint chain.

Extracted from portfolio/2026-10-26-the-knight-at-uruk/knight.py (the Muybridge
gallop plate). Scene coordinates are metres with y up; `to_px` maps them to the
image. What it gives you:

- catmull(points, n, closed): Catmull-Rom sampling of a polyline.
- ik2(root, l1, l2, target, bend): two-link inverse kinematics; bend=+1 puts the
  middle joint on the left of root->target, -1 on the right.
- leg_chain(root, lengths, target, first_angle, bend): a three-link limb whose
  first bone is set by angle (from straight down, positive forward) and the other
  two by IK. Lesson from the plate: the first bone's rest angle is what makes a
  leg read (femur forward-down to the stifle, humerus back-down to the elbow).
- limb_polygon(chain, widths, hoof): a contour polygon from joints and per-joint
  (front, back) half-widths, bisector offsets at joints, no normal flipping.
- Pen(draw, to_px, rng, ink): .stroke(pts, w0, w1) draws a tapered pen stroke with
  a slow perpendicular drift; .outline(poly, w, fill=PAPER) paints the paper back
  under a part and draws its contour as a few overlapping strokes, which is the
  hidden-line removal: draw far parts first, near parts last.

Usage: draw at 2x or 3x and downsample with LANCZOS; stroke widths are in metres
(0.011 m read well at 100 px per metre).
"""
from __future__ import annotations

import math
import random

from PIL import ImageDraw

PAPER = (236, 226, 202)
INK = (34, 27, 20)


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


