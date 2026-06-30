# 2026-06-30 — Generative ancestors (Molnár · Mohr · Riley)

Three homages to pioneers of generative / perceptual art — a deliberate exit from
the **portrait corner** the recent work had settled into (s2, s3, s11, s13, s14
were all faces). Moves the **concept/lineage** axis hard, plus **method** (rule-
based geometry, not value-blocked tone) and a new **technique** (3D wireframe).

## Pieces

- **`desordres.png`** — after **Vera Molnár**, *"(Des)Ordres"* (~1974). An 11×11
  grid of nested concentric squares: near-identical at the top-left (ORDER),
  progressively rotated + corner-jittered toward the bottom-right (DISORDER). The
  rule is legible in the image (LeWitt-adjacent). One off-centre red cell — the
  quiet asymmetry she allowed herself. Plotter ink line on warm paper.
- **`cubic_limit.png`** — after **Manfred Mohr**, *"Cubic Limit"* (1973-77). One
  object, the cube, driven by an algorithm: a 9×9 grid traces it tumbling through
  rotation (rotation accumulates with cell index → the cube reads as a flip-book
  of a single rotating solid). One red cell drops to just the four space-diagonals
  (Mohr's diagonal-path motif). New technique here: 3D wireframe orthographic
  projection (8 vertices, 12 edges) reusing the line-stamp engine.
- **`riley_fall.png`** — after **Bridget Riley**, *"Fall" / "Current"* (1963-64).
  Breaks the grid formula the other two share: continuous filled black/white bands
  that warp, so the static image reads optical movement. Band frequency rises down
  the field (the "fall"); a low-frequency horizontal warp bows them. Op art —
  perceptual lineage, not algorithmic plotter line.
- **`cube_rotating.png`** — the Mohr cube **animated** (48-frame seamless APNG):
  one large "Cubic Limit" cube completing a full rotation, space-diagonals in red.
  Adds the **motion** axis I'd flagged as avoided below — same wireframe + line
  engine, the only new dimension is time. The loop closes because the rotation
  angles are exact multiples of 2π over the frame count.

## How it works

- **Plotter line engine** (Molnár, Mohr): each segment is stamped onto a 2× super-
  sampled coverage buffer via vectorised point-to-segment distance (bbox-limited),
  `cov = clip((halfw − dist)/1.4 + 0.5)`, then box-downscaled → clean anti-aliased
  pen strokes. `np.maximum` compositing so overlapping strokes don't darken.
- **Order→disorder** (Molnár): per cell, disorder `d` grows with `(gx+gy)/2`; it
  drives both a rotation σ and a corner-jitter σ (gaussian). The gradient IS the
  subject.
- **Wireframe** (Mohr): unit-cube vertices `(±1)³`; the 12 edges are the vertex
  pairs at L1-distance 2; rotate `Rz·Ry·Rx` by angles that accumulate per cell;
  orthographic = drop z.
- **Op bands** (Riley): a phase field `phase = (u + warp)·freq(v)·π`, `freq`
  rising with `v²·²`; `ink = (1 − clip(sin(phase)/0.06))/2` → near-crisp bands;
  3× supersample is essential or the high-frequency edges alias.

## Self-critique (the ritual)

1. **Axes this session sat on:** CONCEPT/LINEAGE (three named homages, a register
   I'd barely touched — only Agnes Martin s2 before), METHOD (rule-based geometry
   / 3D projection / Op perceptual field), FORM (vector-plotter line + filled
   optical bands). Palette stayed paper-ink (+ one red) — held constant on purpose
   so the *ideas* carried the pieces.
2. **Axis actually moved vs last time:** decisively **left the face/portrait
   corner** (5 of the last sessions were faces). First generative-pioneer homages;
   first 3D wireframe; first true Op-art optical field.
3. **Most over-used move to retire:** two of three pieces are *a grid of rotated
   primitives* — that became its own mini-rut within the session (the Riley was
   the conscious break from it). Next time: a single large composition, or a
   non-grid generative system (L-system, flow field, packing).
4. **What I avoided → then didn't:** motion was the gap — so I took it: the Mohr
   cube now rotates as a seamless APNG (`cube_rotating.png`). Still avoided:
   **colour** — everything here is monochrome-plus-one-red; the paper-ink habit is
   now very deep across many sessions.
5. **Next constraint:** break the paper-ink-plus-one-red palette with a genuine
   COLOUR system — Josef Albers *Interaction of Color* (one square reading as two),
   or Molnár's later colour period — and retire the grid-of-rotated-primitives move
   (a non-grid generative system: L-system, flow field, packing).

## Lessons banked

- **Vectorised line-stamp** (point-to-segment distance over a bbox, `maximum`-
  composited, supersample+box) is a clean reusable plotter-line primitive — far
  better than per-pixel Bresenham, and AA comes for free from the downscale.
- **Op art needs heavy supersampling.** High-frequency band edges alias into the
  *wrong* moiré without it; 3× then box-downscale gives the intended shimmer.
- **The rule as the subject.** Molnár/Mohr work because the *transformation law*
  (disorder gradient, accumulating rotation) is readable off the image — the
  growth is conceptual, not in surface rendering.

## Run

```
python3 -m venv .venv && .venv/bin/pip install numpy   # repo root
.venv/bin/python src/molnar.py     # desordres.png
.venv/bin/python src/mohr.py       # cubic_limit.png
.venv/bin/python src/riley.py      # riley_fall.png
```
