# Strange Attractors — density fields (2026-07-01)

A chaotic dynamical system rendered as a DENSITY FIELD — new technique for the corpus (not packing,
not flow streamlines, not hard-edge planes). Iterate a 2-D map for millions of steps, histogram
where the orbit lands, log-map density to a luminance palette. The filaments/caustics emerge from
the maths; nothing is placed.

- `images/clifford.png` — Clifford map (a,b,c,d = -1.7, 1.8, -1.9, -0.4), 4M-step orbit. Cold ramp
  (indigo→teal→cyan→white on near-black): two interlocking luminous loops, dense folds burning white.
- `images/dejong.png` — de Jong map (1.641, 1.902, 0.316, 1.525), warm ramp (ember→gold→cream): a
  silken asymmetric swirl — same technique, opposite temperature, to show the palette lever.

Src: `src/clifford.py` (+ inline de Jong variant). A recurrence can't be numpy-vectorised (each step
needs the prior), so the orbit is a scalar `math.sin/cos` loop (~4M in ~3s); density accumulation +
colour-map are vectorised. uint8 write contract correct.
