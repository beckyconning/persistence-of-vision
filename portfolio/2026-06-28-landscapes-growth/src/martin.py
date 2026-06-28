#!/usr/bin/env python3
"""Growth piece #4 — CONCEPT/LINEAGE + RESTRAINT axes. An homage to Agnes Martin:
near-empty, pale washed bands and a faint hand-wavering pencil grid on warm paper.
Everything in session 1 was dense/maximal; this lets emptiness do the work.
"""
import numpy as np
from pnglib import write_png

W, H = 1200, 1500            # tall, like Martin's square-ish canvases
RNG = np.random.default_rng(3)


def main():
    paper = np.array([0.93, 0.90, 0.84])
    img = np.broadcast_to(paper, (H, W, 3)).astype(float).copy()
    # faint horizontal wash bands (alternating barely-warm / barely-cool), Martin's stripes
    band_colors = [np.array([0.95, 0.92, 0.86]), np.array([0.90, 0.89, 0.85]),
                   np.array([0.92, 0.90, 0.83]), np.array([0.89, 0.90, 0.87])]
    n_bands = 24
    margin = int(W * 0.08)
    top, bot = int(H * 0.06), int(H * 0.94)
    band_h = (bot - top) / n_bands
    for b in range(n_bands):
        y0 = int(top + b * band_h); y1 = int(top + (b + 1) * band_h)
        col = band_colors[b % len(band_colors)]
        img[y0:y1, margin:W - margin] = col

    # faint, imperfect pencil grid lines (hand-wavering — the human trace)
    pencil = np.array([0.62, 0.60, 0.57])
    def draw_hline(y):
        for x in range(margin, W - margin):
            yy = int(y + 1.2 * np.sin(x * 0.012) + RNG.normal(0, 0.4))
            for d in (0, 1):
                if 0 <= yy + d < H:
                    img[yy + d, x] = img[yy + d, x] * 0.55 + pencil * 0.45
    def draw_vline(x):
        for y in range(top, bot):
            xx = int(x + 1.2 * np.sin(y * 0.012) + RNG.normal(0, 0.4))
            if 0 <= xx < W:
                img[y, xx] = img[y, xx] * 0.55 + pencil * 0.45

    for b in range(n_bands + 1):
        draw_hline(int(top + b * band_h))
    for c in range(7):
        draw_vline(int(margin + c * (W - 2 * margin) / 6))

    # the faintest paper grain
    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.015
    write_png("martin.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote martin.png")


if __name__ == "__main__":
    main()
