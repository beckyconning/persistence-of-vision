"""Lighthouse, teletext: a page where colour costs a character. A teletext row switches colour only with a
control code, and the code occupies a cell that displays as a space. So the tower's stripes are whole rows (free),
the lamp and its beam share one colour (free), and the sea, which needs 'graphics blue, new background, graphics
white' before any wave, spends three cells at the start of every row; the first stays black, so the sea never
quite reaches the left edge, and the glitter under the beam costs a cell of plain water on each side. Mosaic graphics are 2 x 3 sextants per cell. Writes lighthouse.png and lighthouse.tti."""
import os, numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COL = {"black": 0, "red": 1, "green": 2, "yellow": 3, "blue": 4, "magenta": 5, "cyan": 6, "white": 7}
RGB = [(0, 0, 0), (255, 0, 0), (0, 255, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
W, H = 40, 24
sub = np.zeros((H * 3, W * 2), bool)             # the sextant canvas
rows = [[None] * W for _ in range(H)]            # per cell: ("ctl", code) or ("gfx", colour name)

def ctl(r, c, code): rows[r][c] = ("ctl", code)
def paint(r, c0, c1, colour):
    for c in range(c0, c1): rows[r][c] = ("gfx", colour)

TOWER = (14, 18)                                  # cols
LAMP_ROWS = (5, 7)
for r in range(H):                                # every row starts in graphics mode
    for c in range(W): rows[r][c] = ("gfx", None)
# the beam and the lamp: one yellow run per lamp row, starting after a single control cell at col 0
for r in range(*LAMP_ROWS):
    ctl(r, 0, 0x13); paint(r, 1, W, "yellow")
for sy in range(LAMP_ROWS[0] * 3, LAMP_ROWS[1] * 3):     # a wedge that spreads away from the lamp, both ways
    mid = (LAMP_ROWS[0] * 3 + LAMP_ROWS[1] * 3 - 1) / 2
    for sx in range(2, W * 2):
        d = abs(sx - (TOWER[0] + TOWER[1]) * 1.0)
        half = 0.4 + d * 0.085
        if abs(sy - mid) <= half and (d < 5 or (sx + sy) % 3 != 0): sub[sy, sx] = True
# the lantern: a red cap above, the glass as a full yellow block in the middle of the beam
sub[LAMP_ROWS[0] * 3:LAMP_ROWS[1] * 3, TOWER[0] * 2 + 1:TOWER[1] * 2 - 1] = True
for sy in range(LAMP_ROWS[0] * 3 - 3, LAMP_ROWS[0] * 3):
    sub[sy, TOWER[0] * 2 + 1:TOWER[1] * 2 - 1] = True
ctl(LAMP_ROWS[0] - 1, TOWER[0] - 1, 0x11); paint(LAMP_ROWS[0] - 1, TOWER[0], TOWER[1], "red")
# the tower: stripes are whole rows, each row one colour code just left of it, widening to the base
for r in range(LAMP_ROWS[1], 19):
    colour = "red" if ((r - LAMP_ROWS[1]) // 2) % 2 == 0 else "white"
    ctl(r, TOWER[0] - 2, 0x11 if colour == "red" else 0x17); paint(r, TOWER[0] - 1, TOWER[1] + 1, colour)
    spread = (r - LAMP_ROWS[1]) * 0.18
    for sy in range(r * 3, r * 3 + 3):
        l = int(round(TOWER[0] * 2 - spread)); rr = int(round(TOWER[1] * 2 + spread))
        sub[sy, l:rr] = True
# the sea
for r in range(19, H):
    ctl(r, 0, 0x14); ctl(r, 1, 0x1D); ctl(r, 2, 0x17); paint(r, 3, W, "white")     # blue, new background, white
    for c in range(3, W):
        for k in range(6):
            sy, sx = r * 3 + k // 2, c * 2 + k % 2
            if (sx * 5 + sy * 11 + sy * sx) % 17 == 0 and sy % 3 != 2: sub[sy, sx] = True
# the beam's glitter on the water, under the right-hand beam: its own colour code, so a gap of sea before it
for r in range(20, H):
    c0 = 24 + (r - 20) * 2
    ctl(r, c0, 0x13); paint(r, c0 + 1, min(W, c0 + 6), "yellow")
    for c in range(c0 - 0, min(W, c0 + 7)): sub[r * 3:r * 3 + 3, c * 2:c * 2 + 2] = False   # clear the run and its two code cells
    for c in range(c0 + 1, min(W, c0 + 6)):
        sub[r * 3 + (c % 2), c * 2 + (r % 2)] = True
    if c0 + 6 < W: ctl(r, c0 + 6, 0x17)                                    # back to white waves: another cell
# stars: a white run across the top rows
for r in range(0, 4):
    ctl(r, 0, 0x17); paint(r, 1, W, "white")
    for c in range(1, W):
        if (c * 13 + r * 7) % 11 == 0: sub[r * 3 + (c % 3), c * 2 + (c * r) % 2] = True

# ---- render: cell 12 x 20, sextant columns 6/6, rows 7/6/7 ----------------------------------------------------
CW, CH = 12, 20
img = np.zeros((H * CH, W * CW, 3), np.uint8)
ys = [(0, 7), (7, 13), (13, 20)]
lines = []
for r in range(H):
    fg, bg = COL["white"], COL["black"]
    out = ""
    for c in range(W):
        kind, v = rows[r][c]
        cell = np.zeros((CH, CW, 3), np.uint8); cell[:] = RGB[bg]
        if kind == "ctl":
            if 0x11 <= v <= 0x17: fg = v - 0x10
            elif v == 0x1D: bg = fg
            cell[:] = RGB[bg]
            out += "\x1b" + chr(v + 0x40)
            sextants = 0
        else:
            bits = [sub[r * 3 + k // 2, c * 2 + k % 2] for k in range(6)]
            code = 0x20 + sum(1 << k for k in range(5) if bits[k]) + (0x40 if bits[5] else 0)
            if v is None or not any(bits): code = 0x20
            out += chr(code)
            for k in range(6):
                if bits[k] and v is not None:
                    y0, y1 = ys[k // 2]; x0 = (k % 2) * 6
                    cell[y0:y1, x0:x0 + 6] = RGB[fg]
            if v is not None and v in COL and COL[v] != fg and any(bits):
                raise SystemExit(f"row {r} col {c}: painted {v} but the row's colour here is {fg}")
        img[r * CH:(r + 1) * CH, c * CW:(c + 1) * CW] = cell
    lines.append(out)
Image.fromarray(np.repeat(np.repeat(img, 2, 0), 2, 1)).save(os.path.join(OUT, "lighthouse.png"))
with open(os.path.join(OUT, "lighthouse.tti"), "w", encoding="latin-1") as f:
    f.write("DE,lighthouse\nPN,40100\nSC,0000\nPS,8000\n")
    for r, s in enumerate(lines): f.write(f"OL,{r},{s}\n")
