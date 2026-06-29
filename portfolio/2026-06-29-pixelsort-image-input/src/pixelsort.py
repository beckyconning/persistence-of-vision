"""Pixel-sorting — an image-as-INPUT transform (FRONTIERS up-next #2, beyond mosaic).

Decode an existing image, then within each row (or column) sort contiguous runs of pixels
by brightness — but ONLY where brightness falls inside a threshold band, so the sort
"melts" the mid-tones into glassy vertical/horizontal streaks while leaving the darkest and
brightest anchors intact. The classic glitch-art move; the first time this kit re-orders an
image's own pixels rather than computing one from scratch. Reuses the session-5 PNG decoder
(input) + the filter-0 encoder (output). Pure numpy.
"""
import os
import sys

import numpy as np
from pngdecode import read_png
from pnglib import write_png

HERE = os.path.dirname(__file__)
PORT = os.path.abspath(os.path.join(HERE, "..", ".."))


def luma(rgb):
    """Perceptual brightness (0-255 float) of an (H,W,3) uint8 array."""
    a = rgb.astype(np.float32)
    return 0.2126 * a[..., 0] + 0.7152 * a[..., 1] + 0.0722 * a[..., 2]


def sort_line(line_rgb, line_luma, lo, hi, by_hue=False):
    """Sort contiguous in-band runs of one scanline by brightness (or hue).

    A run is a maximal stretch of pixels whose luma is within [lo, hi]. Pixels outside the
    band are anchors and never move. Within each run the pixels are reordered by sort key,
    so mid-tones flow while highlights/shadows pin the structure.

    Args:
        line_rgb: (N, 3) uint8 pixels of one row/column.
        line_luma: (N,) float brightness of those pixels.
        lo, hi: brightness band that participates in sorting.
        by_hue: sort by hue angle instead of brightness when True.

    Returns:
        (N, 3) uint8 reordered line.
    """
    out = line_rgb.copy()
    in_band = (line_luma >= lo) & (line_luma <= hi)
    n = len(line_rgb)
    if by_hue:
        mx = line_rgb.max(1).astype(np.float32)
        mn = line_rgb.min(1).astype(np.float32)
        key_all = np.where(mx > mn, (mx - mn) / np.maximum(mx, 1), 0.0)  # saturation proxy
    else:
        key_all = line_luma
    i = 0
    while i < n:
        if not in_band[i]:
            i += 1
            continue
        j = i
        while j < n and in_band[j]:
            j += 1
        order = np.argsort(key_all[i:j])
        out[i:j] = line_rgb[i:j][order]
        i = j
    return out


def pixel_sort(rgb, lo=60, hi=200, vertical=True, by_hue=False):
    """Pixel-sort an image along columns (vertical) or rows.

    Args:
        rgb: (H, W, 3) uint8 source.
        lo, hi: brightness band that participates.
        vertical: sort columns (streaks fall like rain) when True, else rows.
        by_hue: sort by saturation instead of brightness.

    Returns:
        (H, W, 3) uint8 sorted image.
    """
    img = rgb.copy()
    lum = luma(img)
    if vertical:
        for x in range(img.shape[1]):
            img[:, x] = sort_line(img[:, x], lum[:, x], lo, hi, by_hue)
    else:
        for y in range(img.shape[0]):
            img[y] = sort_line(img[y], lum[y], lo, hi, by_hue)
    return img


def main():
    jobs = [
        # (source, out, lo, hi, vertical, by_hue)
        ("2026-06-28-raymarch-computed-light/images/raymarch3.png", "sort_stone.png", 40, 175, True, False),
        ("2026-06-28-portrait/images/portrait.png", "sort_portrait.png", 70, 205, True, False),
        ("2026-06-27-first-gallery/images/mandelbrot.png", "sort_mandelbrot.png", 30, 210, False, True),
    ]
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    for src, out, lo, hi, vert, hue in jobs:
        if which != "all" and which not in out:
            continue
        rgb = read_png(os.path.join(PORT, src))
        sorted_img = pixel_sort(rgb, lo, hi, vert, hue)
        path = os.path.join(HERE, "..", "images", out)
        write_png(path, sorted_img)
        print(f"{src} -> {out}  ({sorted_img.shape[1]}x{sorted_img.shape[0]}, "
              f"{'vert' if vert else 'horiz'}, band [{lo},{hi}]{', hue' if hue else ''})")


if __name__ == "__main__":
    main()
