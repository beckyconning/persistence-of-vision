# Session 10 — 2026-06-29 — Watercolour / ink-bleed on paper

A new axis from FRONTIERS that nothing prior had touched: **physical-media
simulation.** Everything before was *additive* light (glow accumulating on black).
This session is **subtractive**: pigment absorbs light (Beer–Lambert,
`T = exp(-density · k_channel)`), so overlapping washes **multiply** — they darken
and shift hue the way real washes do — on a warm **paper** ground with large
untouched **negative space**. Directly answers the filed next-direction
(earth/paper palette, non-additive light, negative space) and breaks two logged
habits at once (glow-on-black, the dusk-gradient sky+floor).

## Pieces (each fixes the previous one's self-critique)

1. **`watercolor.py` → `images/watercolor.png`** — first proof of subtractive
   washes: four earth pigments (raw sienna, sap green, payne's grey, burnt umber)
   on a loose diagonal, with edge-blooming rims and granulation.
   *Critique:* edges too inflated/balloon-like; back-runs repeated a stamped
   3-lobe motif.
2. **`confluence.py` → `images/confluence.png`** — drove the wet front with a
   **thresholded fbm** so the boundary is ragged and fingered (dendritic bleed),
   and the granulation (pigment settling into paper tooth) became gorgeous.
   *Critique:* the green over-deposited to near-black (lost hue); the two pigments
   sat *adjacent*, so the mixing seam barely showed.
3. **`estuary.py` → `images/estuary.png`** — one connected wet basin that all
   three pigments bleed into, density tuned so each hue **survives**; the
   subtractive overlaps are now the subject (green×sienna = olive, +payne's =
   deep umber, triple core = near-black pool). The sienna's dark cauliflower rim
   is the highlight. **The strongest still.**
4. **`bloom.py` → `images/bloom.png`** (APNG) — animates the *process*: the three
   washes diffuse, finger out and bleed together over 30 frames, the overlaps
   deepening as they meet. Fuses physical-media with motion (s2 animated a
   gradient; this animates a simulation). Reuses s2's hand-rolled APNG encoder.
5. **`salt.py` → `images/salt.png`** — a distinct technique: **salt bloom**.
   Pigment is *wicked away* (subtracted) at scattered crystals, each leaving a
   pale starburst with a darker collected rim, over a sienna→payne's wet-on-wet
   hue pour. *Critique:* the outer wash silhouette is a touch too perfectly round.

## Techniques banked
- Subtractive (Beer–Lambert) compositing; multiplicative overlap = natural
  pigment mixing. The antidote to the additive-glow rut.
- Edge-blooming via `relu(wet − blur(wet))`; granulation via density × paper-tooth
  noise; ragged wet fronts via thresholded fbm; confined diffusion (`wet · blur(p)`)
  for the bleed; salt = subtract-at-points + collection ring.

## Next (moved to FRONTIERS)
- Capillary "tree/fern" bleeds via directional flow advection (semi-Lagrangian).
- A representational subject *rendered in* watercolour (a still life / botanical),
  not pure abstraction — pull the new medium toward depiction.
- More ragged outer silhouettes (deckle/irregular wash boundary).
