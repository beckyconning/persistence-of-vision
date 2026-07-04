# Phyllotaxis · 2026-07-02

The golden-angle spiral a sunflower/pinecone uses to pack seeds: point i at angle i·137.507°
(360°/φ²), radius c·√i. That one rule fills the disc with no gaps and no preferred direction; the
visible spiral arms (parastichies) emerge for free and their counts fall on Fibonacci numbers —
nobody places them. A parametric point-set generator (new to the corpus). Rendered as additive
glowing seeds, hue cycling gold-core → rose → blue-rim, tone-mapped on black so the packing reads
as light. `src/phyllotaxis.py` · 2600 seeds.

## Bonus: Truchet tiles (`src/truchet.py`)
A second generator: a grid where each cell drops one of two quarter-arc tiles. Edge-matching at the
tile midpoints joins the arcs into long continuous loops — a maze of rings from a purely local
random choice per cell. Glowing arcs, hue drifting diagonally across the grid. `truchet.png`.

## Bonus: Harmonograph (`src/harmonograph.py`)
The Victorian pendulum drawing machine: two decaying sinusoids per axis trace a Lissajous curve
that spirals inward as it damps. Near-rational detuned frequency ratios give the drifting nested-loop
rose, drawn in one unbroken luminous stroke, cool→warm along its length. `harmonograph.png`.

### Harmonograph atlas (`src/harmonograph_grid.py`)
A 2x3 grid of frequency-ratio/phase/damping presets — the same machine in six tunings. `harmonograph_grid.png`.

### Bonus: Wave interference (`src/interference.py`)
A ripple tank: several point sources emit cos(k·r−φ); summed, crests/troughs reinforce and cancel into fringes. Copper antinodes, blue troughs, black nodal filaments. `interference.png`.
