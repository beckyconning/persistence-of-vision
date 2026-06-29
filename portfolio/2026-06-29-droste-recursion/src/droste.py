"""Droste recursion — an image nested inside itself, image-as-input (FRONTIERS up-next #2).

Decode an image, then repeatedly paste a shrunk (and slightly rotated + darkened) copy of
the whole image into a window inside itself — N levels deep — so the picture opens into an
infinite tunnel of itself. The recursive cousin of session-5's mosaic: there the corpus
*composed* one image; here one image *contains* itself, the literal "persistence of vision"
recursing inward. Pure numpy; reuses the session-5 PNG decoder (input) + filter-0 encoder.
"""
import math
import os
import sys

import numpy as np
from pngdecode import read_png
from pnglib import write_png

HERE = os.path.dirname(__file__)
PORT = os.path.abspath(os.path.join(HERE, "..", ".."))


def resize_bilinear(img, oh, ow):
    """Bilinear resize of an (H,W,3) uint8 image to (oh, ow, 3)."""
    h, w = img.shape[:2]
    ys = np.linspace(0, h - 1, oh)
    xs = np.linspace(0, w - 1, ow)
    y0 = np.floor(ys).astype(int)
    x0 = np.floor(xs).astype(int)
    y1 = np.minimum(y0 + 1, h - 1)
    x1 = np.minimum(x0 + 1, w - 1)
    fy = (ys - y0)[:, None, None]
    fx = (xs - x0)[None, :, None]
    a = img[y0][:, x0].astype(np.float32)
    b = img[y0][:, x1].astype(np.float32)
    c = img[y1][:, x0].astype(np.float32)
    d = img[y1][:, x1].astype(np.float32)
    top = a + (b - a) * fx
    bot = c + (d - c) * fx
    return (top + (bot - top) * fy).astype(np.uint8)


def rotate_about_center(patch, deg):
    """Rotate an (h,w,3) patch by deg degrees about its centre (nearest-neighbour,
    out-of-bounds stays as the original patch so corners don't go black)."""
    if abs(deg) < 1e-3:
        return patch
    h, w = patch.shape[:2]
    cy, cx = (h - 1) / 2.0, (w - 1) / 2.0
    yy, xx = np.indices((h, w))
    t = math.radians(deg)
    cos, sin = math.cos(t), math.sin(t)
    sy = (yy - cy) * cos - (xx - cx) * sin + cy
    sx = (yy - cy) * sin + (xx - cx) * cos + cx
    sy = np.clip(np.round(sy).astype(int), 0, h - 1)
    sx = np.clip(np.round(sx).astype(int), 0, w - 1)
    return patch[sy, sx]


def droste(rgb, levels=7, scale=0.62, rot=8.0, dim=0.93, win=None):
    """Nest the image inside itself `levels` deep.

    Each level pastes a scaled/rotated/darkened copy of the CURRENT canvas into a centred
    window, so deeper copies (built first, then overpainted by shallower ones around them)
    leave an inward tunnel. Built outermost-last: start from the plain image, and for each
    level composite a shrunk copy of the running result into the window.

    Args:
        rgb: (H, W, 3) uint8 source.
        levels: recursion depth.
        scale: child size as a fraction of the window (the tunnel's contraction).
        rot: degrees of twist added per level (the spiral).
        dim: brightness multiplier per level (depth shading).
        win: (top, left, h, w) window the child occupies; default a centred 62% box.

    Returns:
        (H, W, 3) uint8 nested image.
    """
    H, W = rgb.shape[:2]
    if win is None:
        wh, ww = int(H * 0.62), int(W * 0.62)
        win = ((H - wh) // 2, (W - ww) // 2, wh, ww)
    top, left, wh, ww = win

    canvas = rgb.copy()
    for _ in range(levels):
        child = resize_bilinear(canvas, wh, ww)
        child = rotate_about_center(child, rot)
        child = (child.astype(np.float32) * dim).astype(np.uint8)
        canvas = rgb.copy()
        canvas[top:top + wh, left:left + ww] = child
    return canvas


def main():
    jobs = [
        ("2026-06-29-image-as-input/images/mosaic_portrait.png", "droste_mosaic.png", 7, 8.0),
        ("2026-06-28-raymarch-computed-light/images/raymarch4.png", "droste_stone.png", 8, -6.0),
    ]
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for src, out, levels, rot in jobs:
        if which != "all" and which not in out:
            continue
        rgb = read_png(os.path.join(PORT, src))
        result = droste(rgb, levels=levels, rot=rot)
        write_png(os.path.join(HERE, "..", "images", out), result)
        print(f"{src} -> {out}  ({result.shape[1]}x{result.shape[0]}, {levels} levels, {rot}°/lvl)")


if __name__ == "__main__":
    main()
