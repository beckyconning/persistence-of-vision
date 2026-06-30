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
- **`albers_interaction.png`** — after **Josef Albers**, *Homage to the Square* /
  *Interaction of Color*. The **colour** piece (breaks the paper-ink-plus-one-red
  habit). A diptych: nested flat squares in Albers' geometry (equal sides, ~3× more
  space above than below, so they sit low); the innermost square is the **identical**
  olive-gold in both panels but reads cool/receding on the warm-ochre grounds and
  warm/glowing on the cool-teal grounds — the book's thesis in one image. No tone,
  no line: just flat interacting fields.
- **`truchet.png`** — **Truchet tiles** (Smith arcs): each cell flips a coin to
  place one of two quarter-arc pairs; neighbours connect into long flowing loops —
  a maze of curves from pure local randomness. Multi-scale (some cells subdivide),
  ink + amber on paper. A classic generative tradition, not previously touched.
- **`island_map.png`** — an invented **island map**: cartography, the one major
  SUBJECT untouched across the whole portfolio. A fractal value-noise elevation
  field pulled into an island by a radial falloff, quantised into tinted relief
  bands (deep sea → shoal → beach → lowland → upland → peak) with a thin contour
  line at every band edge — the hand-tinted topographic-atlas look, on aged paper.
- **`flowfield_strokes.png`** — a **flow field as discrete pen strokes** (the one
  classic system not revisited since s1 — but reclaimed from the s1 density-glow-on-
  black corner): 1700 short tapered ink strokes advected along a smooth value-noise
  vector field, hue by direction over blue→green→amber, on paper. Reads as marbled
  paper / wind currents — plotter ink, not accumulated glow.
- **`lsystem_plant.png`** — an **L-system plant**: a formal-grammar method (axiom +
  rules iterated to depth 6, then turtle-interpreted) — recursion, not a grid; the
  organic counterpoint to the rigid homages. Branch width tapers and hue runs
  trunk-brown → leaf-green with nesting depth; per-turn angle jitter makes it read
  grown. Botanical subject + generous negative space.
- **`circle_packing.png`** — the **non-grid coda** (retiring the grid-of-primitives
  rut). A largest-empty-circle packing: 1887 circles, each grown to just touch its
  nearest neighbour; hue by radius (big warm-red focal circles floating in a sea of
  small cool teal). Organic space-filling + colour, distinct from the s1 density-glow.
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
4. **What I avoided → then didn't:** both gaps got taken this session — **motion**
   (the Mohr cube rotates as a seamless APNG) and **colour** (the Albers diptych is
   real interacting hue, no tone/line). The long-standing paper-ink-plus-one-red
   habit is finally broken.
5. **Next constraint:** the grid rut got retired this session (circle-packing +
   L-system are both non-grid), so next is composition at a different scale: ONE
   large unified composition rather than a field of many elements, and push colour
   past a static demo (an Albers/Itten study that's also a *subject*, or animated
   colour interaction). A flow-field remains the one classic generative system not
   yet revisited outside the s1 corner.

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
