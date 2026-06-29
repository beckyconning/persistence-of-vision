# Session 11 — 2026-06-29 — Halftone / print (the reproduction mark)

A new axis from session 10's watercolour: same physical-media family, the opposite MARK —
**reproduction printing**. Tone is built from discrete marks (dots, lines) and separated
colour, composited **subtractively** on paper. Six pieces sweeping the axis across colour
models, scales, sub-aesthetics — and pulling the untouched **face** subject (FRONTIERS #1)
into the medium.

## Pieces
1. **`halftone.py` → `images/halftone.png`** — a lit sphere as a CMYK amplitude-modulated
   halftone (dots grow highlight→shadow; rosette angles C15/M75/Y0/K45; UCR pulls grey into
   K). *Critique:* a warm subject only fired Y+K — barely exercised C/M.
2. **`stilllife.py` → `images/stilllife.png`** — four lit spheres across the hue wheel so
   ALL four screens fire and the offset **rosette + registration** show. The strong one.
3. **`profile.py` → `images/profile.png`** — a **profile portrait** (FRONTIERS #1, the face
   axis) as a silhouette-contour relief height-field, Lambert-shaded, halftoned. *Iterated:*
   rounded the occiput + strengthened the relief (was a flat slab). Reads as a face in dots.
4. **`riso.py` → `images/riso.png`** — risograph **duotone**: fluoro pink + teal, two screen
   angles, **deliberate misregistration** (each plate offset a few px) so overlaps stack dark
   and edges fringe. The beloved print error.
5. **`benday.py` → `images/benday.png`** — pop-art **benday**: coarse dots (CELL 22), primary
   palette, solid sun + bold black key line. Distinct *scale*/aesthetic (Lichtenstein).
   *Critique:* a touch busy where red+blue dots overlap.
6. **`engraving.py` → `images/engraving.png`** — line **engraving / crosshatch**: tone by
   LINES not dots — hatch sets added at new angles as tone darkens, plus longitude lines
   wrapping the sphere. The woodcut/banknote mark. **The most refined of the set.**

## Techniques banked
- Amplitude-modulated halftone via a rotated cosine **spot function**, thresholded by ink
  intensity (dot radius tracks tone); classic screen angles; UCR (grey→K).
- Subtractive spot-ink compositing (paper × per-channel ink transmittance).
- Duotone + **misregistration** (offset each plate's screen sample) = riso glow/fringe.
- Coarse benday (big CELL) + posterized tone + key line = pop-art.
- Crosshatch engraving: stacked directional hatch ladders keyed to a tone threshold; longitude
  lines for form; crisp contour.

## Next (FRONTIERS)
- A FULL-COLOUR halftone of a photo-grade source (feed the s5 PNG decoder → CMYK screens).
- Engraving a face (the engraving mark is the strongest; apply it to the profile relief).
- Mezzotint / stipple (random-dot, not screened) for a softer reproduction mark.
