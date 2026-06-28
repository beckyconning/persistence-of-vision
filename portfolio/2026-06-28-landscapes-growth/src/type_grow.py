#!/usr/bin/env python3
"""Growth piece #8 — FORM/SUBJECT: TYPOGRAPHY (never attempted). The word GROW as
a letterform subject, built from an inline 5x7 bitmap font and then GROWN/eroded by
a process (each cell sprouts a soft noisy bloom; edges dissolve). Earth palette on
paper. Ties the session's theme. numpy + stdlib PNG.
"""
import numpy as np
from pnglib import write_png

FONT = {
    "G": ["01110", "10001", "10000", "10111", "10001", "10001", "01111"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "O": ["01110", "10001", "10001", "10001", "10001", "10001", "01110"],
    "W": ["10001", "10001", "10001", "10101", "10101", "11011", "10001"],
}
WORD = "GROW"
RNG = np.random.default_rng(20260628)
W, H = 1500, 620
CELL = 46           # px per font cell
PAD = 14            # cells between letters scaled


def main():
    paper = np.array([0.92, 0.89, 0.81])
    img = np.broadcast_to(paper, (H, W, 3)).astype(float).copy()
    ink = np.array([0.34, 0.30, 0.22])
    bloom = np.array([0.70, 0.45, 0.30])     # warm "growth" colour

    gw = (5 * len(WORD) + (len(WORD) - 1) * 2) * CELL
    x0 = (W - gw) // 2
    y0 = (H - 7 * CELL) // 2
    # accumulate ink mask in cell space, then process
    mask = np.zeros((H, W))
    cx = x0
    for ch in WORD:
        rows = FONT[ch]
        for r, line in enumerate(rows):
            for c, bit in enumerate(line):
                if bit == "1":
                    yy = y0 + r * CELL; xx = cx + c * CELL
                    mask[yy:yy + CELL, xx:xx + CELL] = 1.0
        cx += (5 + 2) * CELL

    # --- GROW process: blur the mask into soft blooms + add sprouting speckle ---
    def box(a, k):
        c = np.cumsum(np.cumsum(a, 0), 1)
        c = np.pad(c, ((1, 0), (1, 0)))
        s = (c[k:, k:] - c[:-k, k:] - c[k:, :-k] + c[:-k, :-k]) / (k * k)
        return np.pad(s, ((0, H - s.shape[0]), (0, W - s.shape[1])), mode="edge")

    soft = box(mask, 25)
    # ink core (hard-ish) + warm bloom halo (soft), edges dissolved by noise
    noise = RNG.random((H, W))
    core = (mask > 0.5) & (noise > 0.18)                 # erode core edges
    halo = np.clip(soft * 1.4, 0, 1) * (noise > 0.5)     # speckled bloom
    img = img * (1 - halo[..., None] * 0.6) + bloom[None, None, :] * (halo[..., None] * 0.6)
    img = np.where(core[..., None], ink[None, None, :], img)
    # sprouting flecks drifting up from the letters (growth)
    ys, xs = np.where(mask > 0.5)
    if len(xs):
        sel = RNG.integers(0, len(xs), 1400)
        fx = np.clip(xs[sel] + RNG.integers(-6, 7, 1400), 0, W - 1)
        fy = np.clip(ys[sel] - RNG.integers(0, 90, 1400), 0, H - 1)
        for x, y in zip(fx, fy):
            img[y, x] = img[y, x] * 0.4 + bloom * 0.6

    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.02
    write_png("type_grow.png", (np.clip(img, 0, 1) * 255).astype(np.uint8))
    print("wrote type_grow.png")


if __name__ == "__main__":
    main()
