"""Stack trace. Each Clawd (the real logo, three lines of quadrant glyphs) spawns a subagent printed below
it, two columns deeper, the way a stack trace grows. A 60 x 24 terminal: by the ninth frame of the stack
the terminal starts to scroll and the first Clawd, the one who started it, leaves the screen. Twenty deep,
then nothing more is printed. Written as a playable shell script and rendered as a GIF of that terminal."""
import numpy as np
from PIL import Image

LOGO = [" ▐▛███▛█", "▝▜██████▀", "  ▝▝ ▝▝"]
BITS = {" ": 0, "▀": 3, "▄": 12, "█": 15, "▌": 5, "▐": 10, "▖": 4, "▗": 8, "▘": 1, "▙": 13, "▚": 9,
        "▛": 7, "▜": 11, "▝": 2, "▞": 6, "▟": 14}
COLS, ROWS, DEPTH = 60, 24, 20
ORANGE = (215, 119, 87); INK = (0, 0, 0)
lines = []
for d in range(DEPTH):
    for row in LOGO:
        lines.append(" " * (2 * d) + row)
CW, CH = 12, 24
def frame(visible):
    img = np.zeros((ROWS * CH, COLS * CW, 3), np.uint8)
    img[:] = INK
    for r, text in enumerate(visible):
        for c, ch in enumerate(text[:COLS]):
            b = BITS.get(ch, 0)
            for q in range(4):
                if b & (1 << q):
                    x0 = c * CW + (q & 1) * (CW // 2); y0 = r * CH + (q >> 1) * (CH // 2)
                    img[y0:y0 + CH // 2, x0:x0 + CW // 2] = ORANGE
    return Image.fromarray(img)
frames, durs = [], []
shown = []
frames.append(frame([])); durs.append(900)
for i, text in enumerate(lines):
    shown.append(text)
    visible = shown[-ROWS:]
    if (i + 1) % 3 == 0:                       # a whole Clawd has printed
        frames.append(frame(visible)); durs.append(260)
durs[-1] = 3000
small = [f.resize((f.width // 2, f.height // 2), Image.NEAREST) for f in frames]
small[0].save("stack-trace.gif", save_all=True, append_images=small[1:], duration=durs, loop=0)
frames[8].save("stack-trace-full.png"); frames[-1].save("stack-trace-last.png")
with open("stack-trace.sh", "w", encoding="utf-8") as f:
    f.write("#!/bin/sh\n# Stack trace: best in a 60 x 24 truecolour terminal.\nclear\nsleep 0.9\n")
    for i, text in enumerate(lines):
        f.write("printf '\\033[38;2;215;119;87m%s\\033[0m\\n' '" + text + "'\n")
        if (i + 1) % 3 == 0: f.write("sleep 0.26\n")
print(len(frames), "frames;", len(lines), "lines")
