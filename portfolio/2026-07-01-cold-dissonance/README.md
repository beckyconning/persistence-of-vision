# Cold Dissonance (2026-07-01)

Hard-edge geometric composition in a deliberately **cool / dissonant** palette — two axes the
corpus kept dodging (every prior palette is warm-harmonious or neon-glow; the one successful colour
study, albers_proof, was a lab plate not a composition).

`images/cold.png` — flat crisp-edged planes (Kelly / Herrera / Lohse concrete-art vocabulary),
hand-placed for asymmetric balance, portrait format. Steel/teal/indigo/cold-violet planes soured
by a single **acid-chartreuse** diagonal (the sour focal note, small + off-centre = tension not
decoration). Carries Albers forward compositionally: the two identical cold-grey squares read
light on indigo and leaden on the icy ground — simultaneous contrast working *inside* a picture.

Src: `src/cold.py` (numpy hard fills + convex-quad half-plane test; no blending, no glow).

## Lesson banked (bit me first): pnglib.write_png expects **uint8**, not float
`write_png` does `rgb.reshape(...).tobytes()` assuming 8-bit. Passing a float64 (0..1) array
serialises 8 bytes/float → the PNG reads garbage → a fine grey MESH. Always
`write_png(path, (img*255).astype(np.uint8))`. This mesh bug (not the technique) is what wrecked
the same-day flow-field attempts.
