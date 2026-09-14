"""Force the scene through a terminal at three widths. Each character cell holds 2x2 quadrants: one of
16 block glyphs and exactly two colours. Each width is written as a real ANSI truecolour text file and
rendered pixel-exact at the same physical size, left to right from 30 to 120 columns."""
import numpy as np
from PIL import Image

GLYPH = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"                        # bit order: UL=1 UR=2 LL=4 LR=8
MASKS = np.array([[(m >> b) & 1 for b in range(4)] for m in range(16)], bool)

def area_down(img, k):
    H, W, _ = img.shape
    return img[:H // k * k, :W // k * k].reshape(H // k, k, W // k, k, 3).mean(axis=(1, 3))

def encode(img):
    H, W, _ = img.shape
    q = img[:H // 2 * 2].reshape(H // 2, 2, W, 3).mean(axis=1)          # quadrants are 1 wide x 2 tall
    rows, cols = q.shape[0] // 2, q.shape[1] // 2
    cells = q[:rows * 2, :cols * 2].reshape(rows, 2, cols, 2, 3).transpose(0, 2, 1, 3, 4).reshape(rows, cols, 4, 3)
    best_err = np.full((rows, cols), np.inf); best_m = np.zeros((rows, cols), int)
    fg = np.zeros((rows, cols, 3)); bg = np.zeros((rows, cols, 3))
    for m in range(1, 15):
        on = MASKS[m][None, None, :, None]
        f = (cells * on).sum(axis=2) / on.sum(); b = (cells * ~on).sum(axis=2) / (4 - on.sum())
        err = ((cells - np.where(on, f[:, :, None], b[:, :, None])) ** 2).sum(axis=(2, 3))
        better = err < best_err
        best_err[better] = err[better]; best_m[better] = m; fg[better] = f[better]; bg[better] = b[better]
    flat = cells.mean(axis=2)
    use_flat = ((cells - flat[:, :, None]) ** 2).sum(axis=(2, 3)) <= best_err + 1e-9
    best_m[use_flat] = 15; fg[use_flat] = flat[use_flat]; bg[use_flat] = flat[use_flat]
    to8 = lambda a: np.clip(a * 255 + 0.5, 0, 255).astype(int)
    return best_m, to8(fg), to8(bg)

def write_ans(path, m, fg, bg):
    rows, cols = m.shape
    with open(path, "w", encoding="utf-8") as f:
        for r in range(rows):
            out, last = [], None
            for c in range(cols):
                key = (*fg[r, c], *bg[r, c])
                if key != last:
                    out.append("\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm" % key); last = key
                out.append(GLYPH[m[r, c]])
            f.write("".join(out) + "\x1b[0m\n")

def render(m, fg, bg, cw):
    rows, cols = m.shape; ch = cw * 2
    img = np.zeros((rows * ch, cols * cw, 3), np.uint8)
    for r in range(rows):
        for c in range(cols):
            for b in range(4):
                colour = fg[r, c] if (m[r, c] >> b) & 1 else bg[r, c]
                x0 = c * cw + (b & 1) * (cw // 2); y0 = r * ch + (b >> 1) * (ch // 2)
                img[y0:y0 + ch // 2, x0:x0 + cw // 2] = colour
    return img

src = np.load("street.npy")
plates = []
for k, cw in ((4, 32), (2, 16), (1, 8)):              # 30, 60 and 120 columns, all 960 px wide
    m, fg, bg = encode(area_down(src, k))
    rows, cols = m.shape
    write_ans(f"street-{cols}x{rows}.ans", m, fg, bg)
    plates.append(render(m, fg, bg, cw))
    print(f"{cols} x {rows} = {rows * cols} characters")
Hs = max(p.shape[0] for p in plates); gap = 24
sheet = np.full((Hs, sum(p.shape[1] for p in plates) + gap * (len(plates) - 1), 3), 16, np.uint8)
x = 0
for p in plates:
    sheet[Hs - p.shape[0]:, x:x + p.shape[1]] = p; x += p.shape[1] + gap
Image.fromarray(sheet).save("made-of-characters.png")
Image.fromarray(plates[-1]).save("street-120.png")
