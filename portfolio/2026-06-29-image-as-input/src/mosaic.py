"""Photomosaic — a single image rebuilt entirely from tiles of the whole
portfolio. The body of work composing one new picture. This is the payoff of
the decoder: every tile is an image we DECODED (input), not generated.

Target: the frontal portrait (a face that recognisably reads). Tiles: every
atomic PNG across all four prior sessions, each sliced into sub-crops so the
palette is rich. Each target cell is matched to its nearest-colour tile, then
the tile is nudged toward the cell's colour so the face holds at a distance
while the constituent artworks stay legible up close.
"""
import glob
import os
import sys
import numpy as np
from pngdecode import read_png
from pnglib import write_png

HERE = os.path.dirname(__file__)
PORT = os.path.abspath(os.path.join(HERE, "..", ".."))   # portfolio/

# Two targets of deliberately different tonal structure — a face (high spatial
# detail, warm midtones) and the reflected stone (smooth gradient, dark ground)
# — to argue the corpus can become *any* image, not just one lucky match.
TARGETS = {
    "portrait": os.path.join(PORT, "2026-06-28-portrait", "images", "portrait.png"),
    "stone": os.path.join(PORT, "2026-06-28-raymarch-computed-light", "images", "raymarch4.png"),
}
WHICH = sys.argv[1] if len(sys.argv) > 1 else "portrait"
TARGET = TARGETS[WHICH]
CELL = 26            # px per mosaic cell (also the tile thumbnail size)
GRID_W = 58          # cells across → output ~1508px wide
SUBCROPS = 4         # slice each source image into SUBCROPS×SUBCROPS tiles
CORRECT = 0.52       # 0=pure tile, 1=pure target colour. Fidelity vs legibility.
REPEAT_PENALTY = 140.0  # discourage the same tile landing adjacent to itself


def box_resize(img, oh, ow):
    """Average-pooling resize (downscale) to (oh, ow, 3). Good enough + no deps."""
    h, w = img.shape[:2]
    ys = (np.linspace(0, h, oh + 1)).astype(int)
    xs = (np.linspace(0, w, ow + 1)).astype(int)
    out = np.empty((oh, ow, 3), np.float32)
    for j in range(oh):
        for i in range(ow):
            patch = img[ys[j]:max(ys[j] + 1, ys[j + 1]),
                        xs[i]:max(xs[i] + 1, xs[i + 1])].astype(np.float32)
            out[j, i] = patch.reshape(-1, 3).mean(0)
    return out


def build_tiles():
    """Decode every atomic portfolio PNG, slice into sub-crops, return
    (thumbs[N,CELL,CELL,3] float32, avg[N,3] float32)."""
    paths = []
    for p in glob.glob(os.path.join(PORT, "*", "images", "*.png")):
        name = os.path.basename(p).upper()
        if "GALLERY" in name or "FRAME_" in name:   # skip contact sheets / anim frames
            continue
        if os.path.abspath(os.path.join(p, "..", "..")) == os.path.abspath(
                os.path.join(HERE, "..")):           # skip this session's own outputs
            continue
        paths.append(p)
    thumbs, avgs, srcs = [], [], []
    for p in sorted(paths):
        try:
            img = read_png(p)
        except Exception as e:
            print(f"  skip {os.path.basename(p)}: {e}")
            continue
        h, w = img.shape[:2]
        for sj in range(SUBCROPS):
            for si in range(SUBCROPS):
                crop = img[sj * h // SUBCROPS:(sj + 1) * h // SUBCROPS,
                           si * w // SUBCROPS:(si + 1) * w // SUBCROPS]
                if crop.shape[0] < 2 or crop.shape[1] < 2:
                    continue
                th = box_resize(crop, CELL, CELL)
                thumbs.append(th)
                avgs.append(th.reshape(-1, 3).mean(0))
                srcs.append(os.path.basename(p))
    print(f"  {len(set(srcs))} source images → {len(thumbs)} tiles")
    return np.array(thumbs), np.array(avgs)


def main():
    print("decoding portfolio into tiles...")
    thumbs, avgs = build_tiles()

    print("decoding target...")
    tgt = read_png(TARGET).astype(np.float32)
    th, tw = tgt.shape[:2]
    gw = GRID_W
    gh = int(round(gw * th / tw))
    cells = box_resize(tgt, gh, gw)              # (gh, gw, 3) target cell colours

    out = np.zeros((gh * CELL, gw * CELL, 3), np.float32)
    last_row = [-1] * gw
    for j in range(gh):
        last = -1
        for i in range(gw):
            want = cells[j, i]
            d = np.sum((avgs - want) ** 2, axis=1)
            if last >= 0:
                d[last] += REPEAT_PENALTY ** 2
            if last_row[i] >= 0:
                d[last_row[i]] += (REPEAT_PENALTY * 0.6) ** 2
            k = int(np.argmin(d))
            last, last_row[i] = k, k
            tile = thumbs[k]
            # nudge the tile toward the cell colour so the face holds at distance
            tile = tile + (want - avgs[k]) * CORRECT
            out[j * CELL:(j + 1) * CELL, i * CELL:(i + 1) * CELL] = tile
    out = np.clip(out, 0, 255).astype(np.uint8)
    outpath = os.path.join(HERE, "..", "images", f"mosaic_{WHICH}.png")
    write_png(outpath, out)
    print(f"wrote {outpath}  ({out.shape[1]}x{out.shape[0]})")


if __name__ == "__main__":
    main()
