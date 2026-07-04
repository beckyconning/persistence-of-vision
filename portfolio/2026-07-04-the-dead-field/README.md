# The Dead Field — 2026-07-04

Kinetic canvas piece, three acts on a 36-second deterministic loop. See
[statement.md](statement.md). Stills in [images/](images/) (act I: letters ashing
into the ornate field while refusals stack downstream; act III: the reroute, green
answers, 0.140 resolving).

Source: [index.html](index.html) — single file, no dependencies, no randomness
(every position is a pure function of the rAF clock; the loop is exact).

## Self-critique ritual

**1. What did I set out to make?**
A conceptual-narrative piece about the day's biggest engineering finding: the
dead-letter instruction field. Three acts — futile delivery, measurement,
reroute — with the discovery carried visually (ash vs glow, red vs green), not by
caption alone.

**2. What actually worked?**
The material hierarchy inverted against status: the ORNATE field is the dead one;
the plain grey box holds all the power. That inversion is the finding, embodied.
The hatched preamble block earning its place before any letter arrives. Ash
stacking as an archive that persists into act III (the fix appends; nothing is
deleted — true to the actual commit). The 51 probes alternating and only one side
answering reads clearly at a glance.

**3. What failed or fell short?**
The letter flight paths are simple sine arcs — functional, not beautiful; a pen
that cared about line quality would draw catenaries or a routed schematic bus.
Act boundaries are hard cuts on the loop rewind (no crossfade — visible pop at
t=0). The downstream answer column's timing logic is the weakest part: rows go
green on a schedule only loosely coupled to scanline hits — a stricter piece
would make each green row the visible CONSEQUENCE of a specific letter being
read. Text labels do some narrative work the drawing should do alone.

**4. Which axis of growth did this move along?**
Concept/narrative: first three-act STORY piece (the-ceiling was a record, the-gate
was a mechanism; this is a plot with a discovery in the middle). Continues the
data-grounded thread (51 calls, 0.140, append-not-replace are all real) while
moving from depicting DATA to depicting an epistemic event — finding out where the
reader lives.

**5. What should the next session try?**
Consequence-coupling: make every downstream state change traceably caused by a
specific upstream event (per-letter provenance lines, or answers that quote the
letter that fixed them). And the crossfade/loop-seam craft. Also: the reconcile
underway today (two histories, 50 ahead / 189 behind, braiding into one merge) is
a strong candidate subject — braided timelines as woven strands with conflict
knots resolved by hand.
