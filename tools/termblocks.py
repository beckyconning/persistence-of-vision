"""termblocks: force an image through a truecolour terminal.

Each character cell is 2 x 2 quadrants, drawn with one of the 16 Unicode quadrant block glyphs and exactly
two colours (foreground, background). Terminal cells are about 1:2, so a quadrant covers one source pixel
across and two down: a W x H square-pixel image becomes W/2 x H/4 characters.

    from termblocks import encode, write_ans, render
    glyphs, fg, bg = encode(rgb_float_image)          # H x W x 3 in 0..1
    write_ans("out.ans", glyphs, fg, bg)                 # cat it in a truecolour terminal
    png = render(glyphs, fg, bg, cell_w=8)               # pixel-exact picture of that terminal

The per-cell choice is exhaustive: all 14 two-colour partitions of the four quadrants plus the flat cell,
colours are the partition means, least squared error wins. The "attribute clash" this produces at low
column counts is the medium's signature; see portfolio/2026-09-14-made-of-characters.
"""
import numpy as np

GLYPH = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"                        # bit order: UL=1 UR=2 LL=4 LR=8
MASKS = np.array([[(m >> b) & 1 for b in range(4)] for m in range(16)], bool)


def area_down(img, k):
    """Box-filter downscale by an integer factor (for narrower terminals)."""
    H, W, _ = img.shape
    return img[:H // k * k, :W // k * k].reshape(H // k, k, W // k, k, 3).mean(axis=(1, 3))


def encode(img):
    H, W, _ = img.shape
    q = img[:H // 2 * 2].reshape(H // 2, 2, W, 3).mean(axis=1)
    rows, cols = q.shape[0] // 2, q.shape[1] // 2
    cells = q[:rows * 2, :cols * 2].reshape(rows, 2, cols, 2, 3).transpose(0, 2, 1, 3, 4).reshape(rows, cols, 4, 3)
    best = np.full((rows, cols), np.inf); glyphs = np.zeros((rows, cols), int)
    fg = np.zeros((rows, cols, 3)); bg = np.zeros((rows, cols, 3))
    for m in range(1, 15):
        on = MASKS[m][None, None, :, None]
        f = (cells * on).sum(axis=2) / on.sum(); b = (cells * ~on).sum(axis=2) / (4 - on.sum())
        err = ((cells - np.where(on, f[:, :, None], b[:, :, None])) ** 2).sum(axis=(2, 3))
        better = err < best
        best[better] = err[better]; glyphs[better] = m; fg[better] = f[better]; bg[better] = b[better]
    flat = cells.mean(axis=2)
    use_flat = ((cells - flat[:, :, None]) ** 2).sum(axis=(2, 3)) <= best + 1e-9
    glyphs[use_flat] = 15; fg[use_flat] = flat[use_flat]; bg[use_flat] = flat[use_flat]
    to8 = lambda a: np.clip(a * 255 + 0.5, 0, 255).astype(int)
    return glyphs, to8(fg), to8(bg)


def ans_lines(glyphs, fg, bg):
    rows, cols = glyphs.shape
    lines = []
    for r in range(rows):
        out, last = [], None
        for c in range(cols):
            key = (*fg[r, c], *bg[r, c])
            if key != last:
                out.append("\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm" % key); last = key
            out.append(GLYPH[glyphs[r, c]])
        lines.append("".join(out) + "\x1b[0m")
    return lines


def write_ans(path, glyphs, fg, bg):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(ans_lines(glyphs, fg, bg)) + "\n")


def render(glyphs, fg, bg, cell_w=8):
    rows, cols = glyphs.shape; cw, ch = cell_w, cell_w * 2
    img = np.zeros((rows * ch, cols * cw, 3), np.uint8)
    for r in range(rows):
        for c in range(cols):
            for b in range(4):
                colour = fg[r, c] if (glyphs[r, c] >> b) & 1 else bg[r, c]
                x0 = c * cw + (b & 1) * (cw // 2); y0 = r * ch + (b >> 1) * (ch // 2)
                img[y0:y0 + ch // 2, x0:x0 + cw // 2] = colour
    return img


if __name__ == "__main__":
    import sys
    from PIL import Image
    if len(sys.argv) < 3:
        print("usage: termblocks.py <image> <columns> [out.ans]"); sys.exit(1)
    cols = int(sys.argv[2])
    im = Image.open(sys.argv[1]).convert("RGB")
    rows4 = max(4, int(round(im.height / im.width * cols * 2 / 4)) * 4)
    im = im.resize((cols * 2, rows4), Image.LANCZOS)
    g, f, b = encode(np.asarray(im, np.float32) / 255)
    lines = ans_lines(g, f, b)
    if len(sys.argv) > 3:
        write_ans(sys.argv[3], g, f, b)
    else:
        print("\n".join(lines))
