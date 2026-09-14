"""Loading: a ZX Spectrum SCREEN$ of Clawd peeking over a terminal, designed for the attribute grid, and the
tape load that brings it in (ink first, top to bottom, then the colour, cell by cell).

Constraint: 256 x 192 pixels, 32 x 24 attribute cells, one INK and one PAPER per cell from the Spectrum's
fifteen colours. Clawd is orange; the Spectrum has no orange. His art pixel is exactly one cell, so he never
clashes, and his eyes are paper: the desktop shows through them.

Writes clawd.scr (the 6912 bytes of screen memory), clawd.tap (an autostart loader plus the SCREEN$, loads in
any emulator), loading.png, loading-ink.png (the bitmap loaded, colour not yet), loading.mp4 (the load at
double speed, border stripes computed from the real pulse timings of the real bytes).
"""
import os, subprocess, numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
N, B = 0xD7, 0xFF
def spec(i, bright):
    v = B if bright else N
    return ((i >> 1) & 1) * v, ((i >> 2) & 1) * v, (i & 1) * v      # GRB bits: 1 blue, 2 red, 4 green
BLACK, BLUE, RED, MAGENTA, GREEN, CYAN, YELLOW, WHITE = range(8)

bm = np.zeros((192, 256), np.uint8)           # 1 = ink
ink = np.full((24, 32), CYAN, np.uint8); paper = np.full((24, 32), BLUE, np.uint8); bright = np.ones((24, 32), np.uint8)
used = np.zeros((24, 32), bool)                # cells something has claimed

def cells(r0, r1, c0, c1, i, p, br=0):
    ink[r0:r1, c0:c1] = i; paper[r0:r1, c0:c1] = p; bright[r0:r1, c0:c1] = br; used[r0:r1, c0:c1] = True

CLAWD = ["..#############..", "..#############..", "..##o#######o##..", "..##o#######o##..", "#################",
         "#################", "..#############..", "..#############..", "....#.#...#.#....", "....#.#...#.#...."]

# the terminal: title bar, then code
T_R0, T_R1, T_C0, T_C1 = 11, 22, 10, 31
cells(T_R0, T_R0 + 1, T_C0, T_C1, BLACK, WHITE, 1)
for k in range(3):                                            # window buttons, right end
    x = (T_C1 - 1 - k) * 8 + 1; bm[T_R0 * 8 + 2:T_R0 * 8 + 6, x + 1:x + 5] = 1 if k != 1 else 0
    if k == 1: bm[T_R0 * 8 + 5, x + 1:x + 5] = 1
bm[T_R0 * 8 + 2:T_R0 * 8 + 6, T_C0 * 8 + 3] = 1; bm[T_R0 * 8 + 4, T_C0 * 8 + 4:T_C0 * 8 + 7] = 1   # a tiny prompt mark
cells(T_R0 + 1, T_R1, T_C0, T_C1, GREEN, BLACK, 1)
rng = np.random.default_rng(1226)
indent = 0
for r in range(T_R0 + 1, T_R1 - 1):                           # wordless code: dashes that indent and return
    if r == T_R0 + 1: indent = 0
    else: indent = max(0, min(3, indent + int(rng.choice([-1, 0, 0, 1]))))
    x0 = T_C0 * 8 + 6 + indent * 10
    n = int(rng.integers(2, 6))
    x = x0
    for w in rng.integers(6, 26, n):
        if x + w > T_C1 * 8 - 6: break
        bm[r * 8 + 3:r * 8 + 5, x:x + w] = 1; x += w + 5
yp = (T_R1 - 1) * 8
bm[yp + 3:yp + 5, T_C0 * 8 + 6:T_C0 * 8 + 12] = 1            # the prompt, and a cursor
bm[yp + 1:yp + 7, T_C0 * 8 + 16:T_C0 * 8 + 21] = 1

# Clawd, one cell per art pixel, peeking over the top: rows 0..3 above the edge, the rest behind the window
C_R0, C_C0 = T_R0 - 4, 11
for j in range(4):
    for i, ch in enumerate(CLAWD[j]):
        r, c = C_R0 + j, C_C0 + i
        if ch == '#': cells(r, r + 1, c, c + 1, RED, BLUE, 1); bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = 1
        elif ch == 'o': cells(r, r + 1, c, c + 1, RED, BLUE, 1)          # an eye: paper, so the sky shows
# fingers over the title bar, where his arms (art row 4) reach past the head
for c in (C_C0, C_C0 + 16):
    ink[T_R0, c] = RED; bright[T_R0, c] = 1
    for k in range(3): bm[T_R0 * 8:T_R0 * 8 + 3, c * 8 + 1 + k * 3:c * 8 + 3 + k * 3] = 1

# a small one (half size, art pixel 4 px) on the floor, walking over to see: red on blue only, so no clash
S_X, S_Y = 12, 23 * 8 - 40
for j, row in enumerate(CLAWD):
    for i, ch in enumerate(row):
        if ch == '#': bm[S_Y + j * 4:S_Y + j * 4 + 4, S_X + i * 4:S_X + i * 4 + 4] = 1
for r in range(S_Y // 8, (S_Y + 40 + 7) // 8):
    for c in range(S_X // 8, (S_X + 68 + 7) // 8): cells(r, r + 1, c, c + 1, RED, BLUE, 1)

# the floor: a taskbar
cells(23, 24, 0, 32, BLACK, WHITE, 1)
bm[23 * 8 + 2:23 * 8 + 6, 3:7] = 1; bm[23 * 8 + 3, 4:6] = 0

# wallpaper: a sparse field of cyan dots wherever nothing else lives
for r in range(23):
    for c in range(32):
        if not used[r, c] and (r * 7 + c * 13) % 5 == 0:
            bm[r * 8 + (r * 3 + c) % 7, c * 8 + (c * 5 + r) % 7] = 1

# ---- files --------------------------------------------------------------------------------------------------------
scr = np.packbits(bm, axis=1).tobytes() + bytes((bright << 6 | paper << 3 | ink).astype(np.uint8).flatten())
assert len(scr) == 6912
open(os.path.join(OUT, "clawd.scr"), "wb").write(scr)

def block(flag, payload):
    body = bytes([flag]) + payload
    x = 0
    for b in body: x ^= b
    body += bytes([x])
    return len(body).to_bytes(2, "little") + body
def num(v): return str(v).encode() + bytes([0x0E, 0, 0, v, 0, 0])
line = bytes([0xE7]) + num(0) + b":" + bytes([0xEF]) + b'""' + bytes([0xAA]) + b":" + bytes([0xE7]) + num(1) + b":" + bytes([0xF2]) + num(0) + b"\r"
basic = (10).to_bytes(2, "big") + len(line).to_bytes(2, "little") + line
hdr0 = bytes([0]) + b"clawd     " + len(basic).to_bytes(2, "little") + (10).to_bytes(2, "little") + len(basic).to_bytes(2, "little")
hdr3 = bytes([3]) + b"clawd     " + (6912).to_bytes(2, "little") + (16384).to_bytes(2, "little") + (32768).to_bytes(2, "little")
tap = block(0x00, hdr0) + block(0xFF, basic) + block(0x00, hdr3) + block(0xFF, scr)
open(os.path.join(OUT, "clawd.tap"), "wb").write(tap)

# ---- pictures -----------------------------------------------------------------------------------------------------
def render(bm, attrs_loaded, border, scale=3, bw=16):
    """attrs_loaded: how many attribute cells have arrived (0..768); the rest are white paper, black ink."""
    img = np.zeros((192, 256, 3), np.uint8)
    flat = np.arange(768).reshape(24, 32) < attrs_loaded
    for r in range(24):
        for c in range(32):
            i, p, br = (ink[r, c], paper[r, c], bright[r, c]) if flat[r, c] else (BLACK, WHITE, 0)
            cell = bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8].astype(bool)
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(cell[..., None], spec(i, br), spec(p, br))
    frame = np.zeros((192 + 2 * bw, 256 + 2 * bw, 3), np.uint8)
    frame[:, :] = border if border.ndim == 1 else border[:, None, :]
    frame[bw:bw + 192, bw:bw + 256] = img
    return np.repeat(np.repeat(frame, scale, 0), scale, 1)

Image.fromarray(render(bm, 768, np.array(spec(BLUE, 0)))).save(os.path.join(OUT, "loading.png"))
Image.fromarray(render(bm, 0, np.array(spec(WHITE, 0)))).save(os.path.join(OUT, "loading-ink.png"))
Image.fromarray(render(bm, 768 // 2 + 12, np.array(spec(WHITE, 0)))).save(os.path.join(OUT, "loading-colour-arriving.png"))

# ---- the tape load ------------------------------------------------------------------------------------------------
# ROM timings in T-states (3.5 MHz): pilot 2168 per half pulse, sync 667 + 735, bit 0 = 2 x 855, bit 1 = 2 x 1710.
edges = []                                            # (length, kind) half pulses; kind 0 pilot/sync, 1 data
byte_end = []                                         # T at which each data byte of the screen block is in
def tape_block(data, pilot_pulses, record):
    for _ in range(pilot_pulses): edges.append((2168, 0))
    edges.append((667, 0)); edges.append((735, 0))
    for k, b in enumerate(data):
        for bit in range(7, -1, -1):
            L = 1710 if (b >> bit) & 1 else 855
            edges.append((L, 1)); edges.append((L, 1))
        if record: byte_end.append(len(edges))
tape_block(block(0x00, hdr3)[2:], 8063, False)
gap = len(edges); edges.append((3500000 // 2, 2))    # half a second of silence between blocks
tape_block(block(0xFF, scr)[2:], 3223, True)
lens = np.array([e[0] for e in edges], np.int64); kinds = np.array([e[1] for e in edges])
ends = np.cumsum(lens)
byte_T = ends[np.array(byte_end) - 1][1:]             # skip the flag byte: screen bytes only
total_T = ends[-1]

FPS, SPEED, FRAME_T = 25, 2, 69888
tmp = os.path.join(OUT, "src", "frames"); os.makedirs(tmp, exist_ok=True)
for f in os.listdir(tmp): os.remove(os.path.join(tmp, f))
n_load = int(total_T / (FRAME_T * 50 * SPEED / FPS)) + 1
hold = FPS * 4
blue_border = np.array(spec(BLUE, 0))
for fi in range(n_load + hold):
    T0 = fi * FRAME_T * 50 * SPEED // FPS
    if fi < n_load:
        lines = T0 + (np.arange(192 + 32) + 16) * 224     # one colour sample per displayed line
        idx = np.searchsorted(ends, lines).clip(0, len(ends) - 1)
        level = idx % 2
        kind = kinds[idx]
        col = np.where((kind == 1)[:, None], np.where(level[:, None] == 1, spec(YELLOW, 0), spec(BLUE, 0)),
                       np.where(level[:, None] == 1, spec(CYAN, 0), spec(RED, 0)))
        col[kind == 2] = spec(WHITE, 0)
        border = col.astype(np.uint8)
        loaded = int(np.searchsorted(byte_T, T0, side="right"))
    else:
        border = blue_border; loaded = 6912
    show = bm.copy()
    px = min(loaded, 6144) * 8
    flatbm = show.reshape(-1); flatbm[px:] = 0
    attrs = max(0, loaded - 6144)
    Image.fromarray(render(show, attrs, border)).save(os.path.join(tmp, f"f{fi:05d}.png"))
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS), "-i", os.path.join(tmp, "f%05d.png"),
                "-pix_fmt", "yuv420p", "-vf", "scale=trunc(iw/2)*2:trunc(ih/2)*2", os.path.join(OUT, "loading.mp4")], check=True)
print("frames", n_load + hold, "tape seconds", total_T / 3.5e6)
