# 2026-07-01 flow-field — DEAD-END (logged, not shipped)

Attempted two frontiers at once (post-s16): a **non-grid generative flow field**
+ a deliberately **cool/dissonant palette**. Value-noise angle field + two off-centre
vortices produced genuine flow STRUCTURE (curved sweeps read clearly). But the RENDER
never resolved into bold cold ribbons — three iterations all collapsed to a desaturated
grey/mauve haze with a fine grid-noise texture, even at full-res crop.

## Why it failed (lessons for next flow-field attempt)
1. **Per-step alpha-disc deposition averages to mud.** Thousands of overlapping
   semi-transparent brush stamps of clashing hues composite toward the mean → grey.
   Coverage math is unforgiving: ribbon_len × brush_width × N must be « canvas area,
   or the ground never breathes. Even at ~20-28% core coverage the soft AA disc RIMS
   spread low-alpha colour everywhere and lift the dark ground to grey.
2. **Clashing palette + blending = grey.** Steel-blue/teal/cyan/chartreuse/violet only
   stay dissonant if they DON'T blend. Alpha compositing blends them → neutral.
3. **1px/soft threads read as noise, not line,** on a 1400px canvas; and downsampled
   viewing destroys them entirely.

## What to try instead (banked to FRONTIERS)
- Draw ribbons as **opaque HARD-EDGE vector polylines** (constant colour, no per-step
  alpha, no soft rim) — few (~120), thick (6-10px), long — so each is a solid pure
  band. Composite OVER (top wins) for a woven, non-muddy overlap.
- Or keep the field but render **streamlines as single strokes** with a proper AA line
  routine (Wu), one colour per stroke, high opacity.
- Cool/dissonant palette needs **hard adjacency (Albers), not blending** to stay sour.

src/flowfield.py kept for reference. The 18MB render was not a keeper (removed).

## Take 2 (opaque hard-edge ribbons) — ALSO a dead-end
Switched to opaque, constant-colour, hard-edged brush swept along streamlines (top-wins OVER,
no alpha). Still resolved to high-entropy grey noise (18MB incompressible png = the tell).
Verified NOT a viewing/pnglib artifact: an existing shipped piece (albers_proof.png) renders
crisply through the same sips path.

ROOT cause of the noise (new lesson): the ANGLE FIELD is too high-frequency/turbulent
(value-noise octaves at cells=5 & 11 + two tight vortices) so streamlines change direction
almost every pixel → each "ribbon" scribbles chaotically → dense scribble = noise, not flow.
Classic flow-field art uses a VERY SMOOTH, low-frequency field (few large cells, one octave)
and/or a curvature clamp so streamlines sweep in long smooth arcs.

NEXT flow-field attempt (banked to FRONTIERS): single low-freq noise octave (cells≈2-3), no
tight vortices (or one broad one), clamp per-step turning angle, ≤80 long smooth ribbons.
For now: the CLEAN, CONCEPTUAL approach (cf. albers_proof) is what's actually working this
era — hard-edge colour interaction beats generative turbulence. Flow-field parked, not solved.

## POSTMORTEM CORRECTION (same day)
The grey MESH was largely the **pnglib uint8 bug** (passed float64 to write_png, which expects
uint8 → 8-bytes/float serialised as garbage), NOT purely the flow-field technique. Confirmed by
the cold-dissonance piece: identical symptom, fixed instantly by `(img*255).astype(np.uint8)`.
The over-density concern (too many/too-long streamlines) was real but secondary. Flow-field is
worth RE-TRYING with the uint8 fix + smooth low-freq field — it was never fairly evaluated.

## SOLVED
Fixed via uint8 write + smooth single-octave field + shorter ribbons — see README. images/ribbons.png is a keeper. The dead-end was the pnglib float/uint8 contract, not the flow-field idea.
