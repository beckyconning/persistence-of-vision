"""Clawd, made of evenings. The Claude Code logo (17 x 10 square pixels, decoded from its quadrant block
characters) as a mosaic: every body pixel is a square crop of the lights-out street, in reading order from
dusk to night; the eyes are night itself; the legs are the doorway, the last light left on."""
import numpy as np
from PIL import Image

ROWS = [" ▐▛███▛█", "▝▜██████▀", "  ▝▝ ▝▝"]
BITS = {" ": 0, "▀": 3, "▄": 12, "█": 15, "▌": 5, "▐": 10, "▖": 4, "▗": 8, "▘": 1, "▙": 13, "▚": 9,
        "▛": 7, "▜": 11, "▝": 2, "▞": 6, "▟": 14}
logo = np.zeros((12, 18), int)
for r, row in enumerate(ROWS):
    for c, ch in enumerate(row):
        b = BITS[ch]
        for q in range(4):
            if b & (1 << q):
                x, qr = 2 * c + (q & 1), 2 * r + (q >> 1)
                logo[2 * qr, x] = logo[2 * qr + 1, x] = 1
logo = logo[:10, 1:18]                                   # 17 wide, 10 tall
eyes = {(2, 4), (3, 4), (2, 12), (3, 12)}                # the holes inside the body

gif = Image.open("lights-out.gif")
frames = []
try:
    while True:
        frames.append(gif.convert("RGB").copy()); gif.seek(gif.tell() + 1)
except EOFError:
    pass
T = 110; GAP = 3
def crop(fr, box): return fr.crop(box).resize((T, T), Image.LANCZOS)
street_box = (0, 0, 352, 352)                            # the warehouse, full height of the frame
door_box = (226, 262, 278, 314)                          # the lit doorway and its wet reflection

body = [(r, c) for r in range(10) for c in range(17) if logo[r, c] and r < 8]
legs = [(r, c) for r in range(10) for c in range(17) if logo[r, c] and r >= 8]
H, W = 10 * (T + GAP) + GAP, 17 * (T + GAP) + GAP
sheet = Image.new("RGB", (W, H), (0, 0, 0))
for k, (r, c) in enumerate(body):
    f = frames[int(round(k / (len(body) - 1) * (len(frames) - 1)))]
    sheet.paste(crop(f, street_box), (GAP + c * (T + GAP), GAP + r * (T + GAP)))
for (r, c) in legs:
    sheet.paste(crop(frames[-1], door_box), (GAP + c * (T + GAP), GAP + r * (T + GAP)))
# the eyes stay empty: clawd_background, rgb(0, 0, 0)
out = Image.new("RGB", (W + 2 * 120, H + 2 * 120), (0, 0, 0))
out.paste(sheet, (120, 120))
out.save("made-of-evenings.png")
print(out.size, len(body), "evening tiles,", len(legs), "doorway tiles")
