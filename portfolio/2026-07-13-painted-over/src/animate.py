"""PAINTED OVER — the day as one loop (720x450 APNG)."""
import numpy as np
from painted_over import scene, gui_panel, wrong_matrix, unbound_texture, to8
from apnglib import write_apng

W2, H2 = 720, 450
frames = []

# 1) the demo, playing (2 beats)
for i in range(8):
    frames.append(to8(scene(W2, H2, beat=i / 4.0)))
# 2) the state guard: suppressed
for i in range(6):
    g = 1.0 * (1 - (i + 1) / 6.0) ** 2 + 0.015
    frames.append(to8(scene(W2, H2, beat=(8 + i) / 4.0, ghost=g)))
# 3) it comes back - and the menu slides over it
base = scene(W2, H2)
for i in range(8):
    frames.append(to8(gui_panel(base, slide=(i + 1) / 8.0)))
# 4) the wrong matrix: menu AND world collapse into the smear
covered = gui_panel(base, slide=1.0)
for i in range(8):
    frames.append(to8(wrong_matrix(covered, t=(i + 1) / 8.0)))
# 5) unbound texture: hold the corruption (checker phase jitters via grain)
ub = unbound_texture(W2, H2)
for i in range(8):
    frames.append(to8(np.clip(ub * (0.96 + 0.04 * ((i % 2) * 2 - 1) * 0.5), 0, 1)))
# 6) the overlay pass: revealed, flash fires, then peace
for i in range(8):
    frames.append(to8(scene(W2, H2, beat=i / 4.0, flash=(i + 1) / 8.0)))
for i in range(6):
    frames.append(to8(scene(W2, H2, beat=i / 4.0)))

write_apng("../images/painted-over-loop.png", frames, delay_num=9, delay_den=100)
print(f"{len(frames)} frames written")
