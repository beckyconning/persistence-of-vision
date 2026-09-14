"""The clash: the same tower of three Claudes ("Look how tall we are!") forced through the Spectrum's rule twice.
Left, it stands on plain desktop: every cell holds at most two colours and the rule costs nothing. Right, the
tower stands half on the terminal: cells that need red, blue and black at once must drop one, and the Claudes
break into the grid. The picture is drawn in full colour first; only the encoder decides what survives.
Writes clash.png (the diptych), tower-free.scr and tower-clash.scr."""
import os, numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACK, BLUE, RED, GREEN, WHITE = 0, 1, 2, 4, 7
def rgb(i, br=1):
    v = 0xFF if br else 0xD7
    return ((i >> 1) & 1) * v, ((i >> 2) & 1) * v, (i & 1) * v
CLAWD = ["..#############..", "..#############..", "..##o#######o##..", "..##o#######o##..", "#################",
         "#################", "..#############..", "..#############..", "....#.#...#.#....", "....#.#...#.#...."]

def scene(tower_x):
    img = np.full((192, 256), BLUE, np.uint8)                   # full colour, one Spectrum index per pixel
    img[96:184, 136:256] = BLACK                                  # the terminal, running off the right edge
    img[88:96, 136:256] = WHITE
    rng = np.random.default_rng(3)
    for r in range(99, 180, 8):
        x = 142 + int(rng.integers(0, 3)) * 8
        while x < 250:
            w = int(rng.integers(6, 22)); img[r:r + 2, x:min(x + w, 256)] = GREEN; x += w + 5
    img[184:192] = WHITE
    for k in range(3):                                            # the tower, bottom first
        y0 = 184 - 40 * (k + 1)
        for j, row in enumerate(CLAWD):
            for i, ch in enumerate(row):
                y, x = y0 + j * 4, tower_x + i * 4
                if ch == '#': img[y:y + 4, x:x + 4] = RED
    return img

def encode(img):
    """Per 8x8 cell: the two most used colours win; every pixel takes the nearer of the two (by RGB)."""
    bm = np.zeros((192, 256), np.uint8); ink = np.zeros((24, 32), np.uint8); paper = np.zeros((24, 32), np.uint8)
    pal = np.array([rgb(i) for i in range(8)], float)
    for r in range(24):
        for c in range(32):
            cell = img[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
            counts = np.bincount(cell.flatten(), minlength=8)
            order = np.argsort(-counts, kind="stable")
            p, i = int(order[0]), int(order[1]) if counts[order[1]] > 0 else int(order[0])
            d_i = ((pal[cell] - pal[i]) ** 2).sum(-1); d_p = ((pal[cell] - pal[p]) ** 2).sum(-1)
            bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = (d_i < d_p) | (cell == i)
            ink[r, c], paper[r, c] = i, p
    return bm, ink, paper

def show(bm, ink, paper, scale=3, bw=12):
    out = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            m = bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8].astype(bool)[..., None]
            out[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(m, rgb(ink[r, c]), rgb(paper[r, c]))
    frame = np.zeros((192 + 2 * bw, 256 + 2 * bw, 3), np.uint8); frame[:] = rgb(BLUE, 0)
    frame[bw:bw + 192, bw:bw + 256] = out
    return np.repeat(np.repeat(frame, scale, 0), scale, 1)

plates = []
for name, x in (("tower-free", 36), ("tower-clash", 106)):
    bm, ink, paper = encode(scene(x))
    scr = np.packbits(bm, axis=1).tobytes() + bytes((1 << 6 | paper << 3 | ink).astype(np.uint8).flatten())
    open(os.path.join(OUT, name + ".scr"), "wb").write(scr)
    plates.append(show(bm, ink, paper))
gap = np.full((plates[0].shape[0], 24, 3), 255, np.uint8)
Image.fromarray(np.concatenate([plates[0], gap, plates[1]], axis=1)).save(os.path.join(OUT, "clash.png"))
