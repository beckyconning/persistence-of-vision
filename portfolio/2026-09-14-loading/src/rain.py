"""Rain, lit by windows: a Spectrum screen where the clash is the lighting. Lit windows exist only as attribute
cells (PAPER yellow, never a pixel); the rain exists only as bitmap. Because a cell has one INK, a falling streak
takes the colour of whatever it crosses: dim blue against dark brick, cyan against the glowing sky, bright white
across a lit window, magenta through the neon. Writes rain.png (bitmap alone | attributes alone | the screen),
rain.gif (the loop: attributes never change, only the rain moves), rain.scr."""
import os, numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE = range(8)
def rgb(i, br):
    v = 0xFF if br else 0xD7
    return ((i >> 1) & 1) * v, ((i >> 2) & 1) * v, (i & 1) * v

rng = np.random.default_rng(1405)
paper = np.full((24, 32), BLACK, np.uint8); ink = np.full((24, 32), BLUE, np.uint8); bright = np.zeros((24, 32), np.uint8)
paper[5:14, :] = BLUE                                               # city glow low in the sky
ink[:14, :] = CYAN
# towers: column spans and heights (in cells), dark brick is BLACK paper
skyline = [(0, 3, 9), (3, 8, 13), (8, 10, 7), (10, 15, 16), (15, 17, 10), (17, 22, 12), (22, 24, 6), (24, 29, 15), (29, 32, 8)]
for c0, c1, h in skyline:
    top = 22 - h
    paper[top:22, c0:c1] = BLACK; ink[top:22, c0:c1] = BLUE
    for r in range(top + 1, 21):
        for c in range(c0, c1):
            if (c - c0) % 2 == 1 or c1 - c0 <= 2:
                if rng.random() < 0.38:
                    paper[r, c] = YELLOW; ink[r, c] = WHITE; bright[r, c] = int(rng.random() < 0.7)
# a neon sign down one tower, and the street
for r in range(10, 15): paper[r, 16] = MAGENTA; ink[r, 16] = WHITE; bright[r, 16] = 1
paper[22:, :] = BLACK; ink[22:, :] = BLUE
for c in range(32):                                                 # the street reflects the lowest lit window above
    lit = [r for r in range(21, 5, -1) if paper[r, c] in (YELLOW, MAGENTA)]
    if lit: ink[22:, c] = paper[lit[0], c]; bright[22:, c] = bright[lit[0], c]

N_DROPS, LOOP = 150, 12
drops = np.stack([rng.integers(0, 256, N_DROPS), rng.integers(0, 192, N_DROPS), rng.integers(5, 10, N_DROPS)], 1)

def bitmap(t):
    bm = np.zeros((192, 256), np.uint8)
    for x, y, L in drops:
        y0 = (y + t * 16) % 192                                      # 16 px a frame: loops after 12
        for k in range(L):
            yy, xx = int(y0 + k * 2) % 192, int(x - k) % 256         # a slanting streak
            bm[yy, xx] = 1
    for c in range(32):                                             # reflections: broken vertical strokes in the wet street
        if ink[22, c] != BLUE:
            for k in range(0, 16, 3):
                if (c * 7 + k + t) % 4: bm[176 + k, c * 8 + 3:c * 8 + 5] = 1
    return bm

def render(bm, use_attrs=True, use_bitmap=True, scale=3):
    img = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            if use_attrs: i, p, br = ink[r, c], paper[r, c], bright[r, c]
            else: i, p, br = WHITE, BLACK, 0
            m = bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8].astype(bool) if use_bitmap else np.zeros((8, 8), bool)
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(m[..., None], rgb(i, br), rgb(p, br))
    return np.repeat(np.repeat(img, scale, 0), scale, 1)

bm0 = bitmap(0)
gap = np.full((576, 18, 3), 255, np.uint8)
Image.fromarray(np.concatenate([render(bm0, use_attrs=False), gap, render(bm0, use_bitmap=False), gap, render(bm0)], 1)).save(os.path.join(OUT, "rain.png"))
frames = [Image.fromarray(render(bitmap(t), scale=2)) for t in range(LOOP)]
frames[0].save(os.path.join(OUT, "rain.gif"), save_all=True, append_images=frames[1:], duration=80, loop=0)
scr = np.packbits(bm0, axis=1).tobytes() + bytes((bright << 6 | paper << 3 | ink).astype(np.uint8).flatten())
open(os.path.join(OUT, "rain.scr"), "wb").write(scr)
