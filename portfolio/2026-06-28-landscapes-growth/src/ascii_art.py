#!/usr/bin/env python3
"""Growth piece #7 — METHOD: image-as-INPUT (never done) + FORM: ASCII/text.
Decodes my own landscape PNG (a real PNG decoder — first time an image is an
*input*, not just output), reduces it to a luminance grid, and re-renders it as
ASCII art (text is the canvas). numpy + stdlib.
"""
import struct, zlib
import numpy as np

RAMP = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
# coarse, dark→light (classic 70-char ramp). We index by brightness.


def read_png(path):
    data = open(path, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n"
    pos, w, h, idat = 8, 0, 0, b""
    while pos < len(data):
        ln = struct.unpack(">I", data[pos:pos + 4])[0]; tag = data[pos + 4:pos + 8]
        chunk = data[pos + 8:pos + 8 + ln]
        if tag == b"IHDR":
            w, h = struct.unpack(">II", chunk[:8])
        elif tag == b"IDAT":
            idat += chunk
        elif tag == b"IEND":
            break
        pos += 12 + ln
    raw = zlib.decompress(idat)
    arr = np.frombuffer(raw, np.uint8).reshape(h, w * 3 + 1)
    assert (arr[:, 0] == 0).all(), "expected filter-0"
    return arr[:, 1:].reshape(h, w, 3)


def main():
    img = read_png("landscape.png").astype(float) / 255
    lum = 0.2126 * img[..., 0] + 0.7152 * img[..., 1] + 0.0722 * img[..., 2]
    H, W = lum.shape
    cols, rows = 150, 56                                  # chars; ~2:1 char aspect handled by rows
    ch = H // rows; cw = W // cols
    cells = lum[: rows * ch, : cols * cw].reshape(rows, ch, cols, cw).mean(axis=(1, 3))
    # contrast stretch then map to ramp
    cells = (cells - cells.min()) / (np.ptp(cells) + 1e-9)
    cells = cells ** 0.85
    idx = np.clip((cells * (len(RAMP) - 1)).astype(int), 0, len(RAMP) - 1)
    lines = ["".join(RAMP[i] for i in row) for row in idx]
    open("landscape_ascii.txt", "w").write("\n".join(lines))
    print("\n".join(lines[::2]))                          # preview every other row
    print(f"\nwrote landscape_ascii.txt ({cols}x{rows} chars)")


if __name__ == "__main__":
    main()
