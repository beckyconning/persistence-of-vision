# Circle Packing — warm mosaic (2026-07-01)

`images/circlepack.png` — a NON-GRID generative technique new to the corpus. Greedy largest-first
packing (throw darts per radius, keep if it clears all placed circles + frame by a gap); small
circles crowd the interstices between big ones → an organic gap-filling mosaic. Filled ANTI-ALIASED
discs (1px rim feather). Deliberately WARM / harmonious jewel palette (rust, burnt orange, amber,
pale gold, oxblood) on deep slate, with muted-teal circles as sparse cool tension notes — a
considered warm scheme as counterpoint to the same day's cold-dissonance + cold flow-field.

`images/circlepack_field.png` — GROWTH variant: same packing, but each circle is coloured by an
underlying smooth field (diagonal warm→cool ramp × radial luminosity), so the packing RENDERS a soft
luminous form rather than decorating the frame — circle-packing as a representational medium.

Src: `src/circlepack.py`, `src/circlepack_field.py`. uint8 write contract correct from the start
(lesson from the flow-field mesh bug earlier the same day).
