# Flow Field — cold vortices (2026-07-01)

`images/ribbons.png` — a NON-GRID generative flow field in a COOL / DISSONANT palette, two
frontiers the corpus kept dodging (every prior palette warm/neon; recent work grid-bound).

150 streamlines integrate a smooth low-frequency value-noise angle field warped by two off-centre
vortices (strong lower-left spiral, smaller upper-right). Each streamline is drawn as a single
CONSTANT-colour OPAQUE hard-edged ribbon (top-wins compositing → woven, never averaged), so the
cold palette stays cold: steel blue / teal / cold cyan flowing on a near-black ground, punctuated
by sparse ACID-CHARTREUSE and cold-VIOLET accent threads (the dissonant sour notes). Negative space
breathes (short ribbons, off-centre void seeding).

Src: `src/ribbons.py`.

## The bug that hid this piece (banked lesson)
Three earlier renders looked like grey mesh — NOT the technique. Root cause: `pnglib.write_png`
expects a **uint8** array; I passed float64 (0..1), so `.tobytes()` serialised 8 bytes/float as
pixels → garbage mesh. Fix: `write_png(path, (img*255).astype(np.uint8))`. Once fixed (+ a smooth
single-octave field instead of a too-turbulent one, + shorter ribbons so the ground shows), the
flow field resolved cleanly. Lesson: verify the output-encoding contract before blaming the art.
