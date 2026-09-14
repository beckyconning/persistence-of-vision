"""Lights out: the warehouse over one evening, forty frames, each forced through the terminal
constraint at 120 columns. The windows go dark one at a time in a fixed random order until only the
street lamp is left. Writes a terminal player (plain sh + ANSI) and an animated GIF of the same frames."""
import sys, numpy as np
from PIL import Image
sys.path.insert(0, "src")
from street import scene
from encode import encode, render

order_rng = np.random.default_rng(11)
lit0 = [(f, b) for f in range(4) for b in range(5)]         # the whole building is lit at dusk
order = [lit0[i] for i in order_rng.permutation(len(lit0))]
N = 40
frames, ans, events = [], [], []          # events: (frame, floor, bay) of each window going dark
import os
os.makedirs("frames", exist_ok=True)
prev_off = 0
for i in range(N):
    t = i / (N - 1)
    n_off = int(round(t * t * len(order)))                  # slow at first, then the building empties
    lit = set(order[n_off:])
    for w in order[prev_off:n_off]: events.append((i, w[0], w[1]))
    prev_off = n_off
    m, fg, bg = encode(scene(night=t, lit_set=lit))
    frames.append(Image.fromarray(render(m, fg, bg, 8)))
    frames[-1].save("frames/f%02d.png" % i)
    lines = []
    rows, cols = m.shape
    GLYPH = " ▘▝▀▖▌▞▛▗▚▐▜▄▙▟█"
    for r in range(rows):
        out, last = [], None
        for c in range(cols):
            key = (*fg[r, c], *bg[r, c])
            if key != last: out.append("\x1b[38;2;%d;%d;%dm\x1b[48;2;%d;%d;%dm" % key); last = key
            out.append(GLYPH[m[r, c]])
        lines.append("".join(out) + "\x1b[0m")
    ans.append("\n".join(lines))
with open("lights-out.sh", "w", encoding="utf-8") as f:
    f.write("#!/bin/sh\n# Lights out: play in a truecolour terminal at least 120 x 44.\nprintf '\\033[2J\\033[?25l'\n")
    for i, a in enumerate(ans):
        hold = "2.5" if i in (0, N - 1) else "0.35"
        f.write("printf '\\033[H'\ncat <<'FRAME'\n" + a + "\nFRAME\nsleep " + hold + "\n")
    f.write("printf '\\033[?25h\\n'\n")
durs = [2500 if i in (0, N - 1) else 350 for i in range(N)]
small = [fr.resize((480, 352), Image.NEAREST) for fr in frames]
small[0].save("lights-out.gif", save_all=True, append_images=small[1:], duration=durs, loop=0, optimize=True)
frames[N // 2].save("lights-out-middle.png"); frames[-1].save("lights-out-last.png")
import json
json.dump({"events": events, "durations_ms": durs}, open("frames/timeline.json", "w"))
print("frames", N, "events", len(events))
