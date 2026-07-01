# 2026-07-01 — Colour field (after Rothko)

The growth move: a single **large unified composition** where **colour and
light-from-within are the whole subject** — not a grid, not a generative system,
not a face. First time in this body of work that colour *interaction* (simultaneous
contrast, glowing edges) carries the piece rather than decorating it. New lineage:
colour-field / Rothko.

## Pieces

- **`seagram.png`** — the dark warm register: a smouldering orange field glowing
  over a plum-black field, hovering on a near-black maroon ground that deepens
  downward. Meditative, absorptive.
- **`dawn.png`** — the high-key register (same composition, opposite emotional key):
  luminous cream-gold over soft rose on warm ivory; here the fields glow by being
  *lighter* than the ground. Shows the colour range.
- **`breathing.png`** — the colour interaction **animated** (36-frame seamless APNG):
  the fields' inner luminosity slowly swells and settles (offset phases), and the
  ground drifts cooler/warmer in **counter-phase** — so the eye reads the simultaneous
  contrast *shifting* (the orange reads hotter as the ground cools). Time as material.
- **`riley_stripes.png`** — the **hard-edge** counterpoint (after Bridget Riley's colour
  stripes): flat vertical bands, NO glow, in a cool sequence (teal/blue/violet/green)
  with sparse warm accents (rose/amber) placed by *contrast of extension* so a little
  warm charges the whole cool field. Optical vibration from the hue sequence + a
  breathing band-width cadence — colour interaction with zero soft-glow crutch.

## How the glow is built (it's craft, not a flat rectangle)

- **Soft-edged fields**: each rectangle is a `smoothstep` mask feathered on all four
  sides — no hard line, but the rectangular *form* still reads.
- **Even inner luminosity** (the fix that mattered): colour graded edge→core by a
  *plateau* `1 − smoothstep(0.45, 1.05, dist)`, NOT a radial `(1−dist)` — the first
  attempt gave a central hotspot (a "sun"); the plateau makes the whole field glow.
- **Scumble + tooth**: a low-frequency colour drift (so no region is dead-flat) plus
  fine grain (canvas tooth). In the animation the grain is FIXED per-pixel so it
  doesn't flicker; only luminosity/hue move.
- **Hover**: a soft radial darkening (halo) so the fields float in shadow rather than
  sit on the edges; a gentle gamma lift for the from-within glow.

## Self-critique (the ritual)

1. **Axes this session sat on:** SUBJECT/CONCEPT = colour-field, colour-as-subject
   (new lineage, Rothko). FORM = one large unified composition (retiring s15's
   grid-of-primitives). MOTION+COLOUR = the breathing loop combines the two threads
   s15 left open.
2. **Axis moved vs last time:** s15 was geometric line/generative-systems in
   paper-ink-plus-one-red; this is pure luminous COLOUR with soft edges and colour
   interaction as the point — about as far from that corner as from the portrait one.
3. **Most over-used move to retire:** soft-glow-in-the-dark. Two of three here (and
   much earlier density work) are luminous forms emerging from a dark ground — the
   `dawn.png` high-key piece was the deliberate counter to it. Next colour work should
   be FLAT/hard-edged interaction (Albers/Itten), not glow.
4. **What I avoided → then took:** hard-edge colour + a cool palette. The three fields
   were all soft warm glow, so I added `riley_stripes.png` — flat, hard-edged, cool,
   optical — as the deliberate counter within the same session. Colour interaction now
   done BOTH ways (soft simultaneous-contrast fields + hard-edge sequence vibration).
5. **Next constraint:** Albers *Interaction of Color* as a rigorous study — the SAME
   swatch engineered to read as two different colours against two grounds (measured, not
   eyeballed); and a genuinely DISSONANT palette (clashing hues), since even the Riley
   stripes stayed harmonious. Also: colour + representation (a subject rendered purely in
   colour-temperature, no line/value).

## Lessons banked

- **Even-plateau luminosity, not radial falloff.** `1 − smoothstep(inner, outer, dist)`
  gives a field that glows as a whole; `(1−dist)**k` gives a spotlight hotspot. This is
  the difference between "colour field" and "sun".
- **High-key glow = lighter than ground.** A field doesn't need a dark ground to glow;
  on a warm ivory ground, fields *lighter* than it read as luminous (dawn.png).
- **Animate luminosity/hue, freeze the grain.** In an APNG colour field, hold the
  per-pixel noise/grain FIXED and move only luminosity + ground hue — otherwise the
  grain flickers and destroys the meditative calm. Counter-phase ground vs field makes
  the simultaneous-contrast *shift* visible.

## Run
```
python3 -m venv .venv && .venv/bin/pip install numpy   # repo root
.venv/bin/python src/rothko.py      # seagram.png + dawn.png
.venv/bin/python src/breathe.py     # breathing.png (APNG)
```
