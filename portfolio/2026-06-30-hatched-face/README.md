# 2026-06-30 — Hatched face (tone from ink strokes)

A full-front, pensive portrait whose every tone is built **only from directional
line-strokes** — pen-and-ink / engraving cross-hatching. The single hidden
gradient (a Lambert value-field) does nothing but *decide where strokes go*; it
never touches the paper. Three registers of the same head.

## Pieces

- **`hatched_face.png`** — the picture. Warm laid paper, near-black ink. Six
  cross-hatch layers at rising darkness thresholds (32°, −32°, 78°, 8°, −60°,
  50°) + a tight core-accent pass. A melancholy downcast head: lit forehead and
  left cheek turning into shadow on the right, eyes lowered, mouth corners bowed
  down.
- **`sanguine_face.png`** — trois-crayons. Same value field; sanguine red-chalk
  darks + **white-chalk highlight hatching** (its own light-gated layers) on a
  café-au-lait toned paper. Moves the palette axis; reads as an Old-Master
  red-chalk study.
- **`contour_face.png`** — experiment (half-works). Strokes follow the **iso-tone
  contours** of the value field instead of fixed angles. Wraps the face like a
  topographic engraving and crowds where the form turns fast — but reads more as
  a thumbprint/wood-grain topo-map than an engraving (see lesson 3).

## How it works

1. **Value-blocking** (the s13 lesson, applied): the face is composed as
   deliberate lit-planes + core-shadows — a clean global sphere form-turn keyed
   from upper-left, then explicit `dark()`/`lit()` gaussian masses for eye
   sockets, lash lines, brow, nose ridge/side/nostrils, lips, chin, jaw. NOT a
   bumpy height-field (which read as a stone in the first attempt).
2. **The hatch engine**: each layer is parallel lines at angle θ, spacing s,
   gated to "on" where darkness D exceeds a threshold t. Hand feel = a low-freq
   value-noise `waver` bends the lines; a high-freq `grain` breaks strokes so ink
   skips. Darker tone recruits more layers → cross-hatch density rises with tone.

## Self-critique (the ritual)

1. **Axes this session sat on:** SUBJECT = the full-front expressive face (the
   marquee-open subject — only frontal-relief s3, profile-relief s11, profile
   charcoal s13 before). METHOD = cross-hatching / mark-making. PALETTE = the
   sanguine variant adds trois-crayons (red+white chalk on toned ground).
2. **Axis actually moved vs last time:** the big one is **METHOD** — every prior
   face was a continuous tonal field (relief shader or charcoal smudge). This is
   the first time tone is *quantised into discrete directional marks*. Plus the
   first **full-front** face (all prior faces were symmetric-frontal-relief or
   profile).
3. **Most over-used move to retire:** the egg/oval silhouette on an empty ground
   — three faces this session and the figure/portrait sessions all sit in a
   centred vignette. Next face wants a real crop, shoulders, or an environment.
4. **What I avoided / scared of:** true form-following engraving strokes (lines
   that run *along* the surface like a banknote portrait). The contour attempt
   went for it and half-missed — see lesson 3. Also avoided: hands, and a
   *second distinct expression* to prove control.
5. **Next constraint:** make the strokes **engraving-correct** — parallel
   directional lines whose *spacing/weight* tracks tone and whose *direction*
   follows the form locally (rotate the hatch angle by the value-gradient
   normal), NOT iso-value contours. And crop the head (shoulders / off-centre /
   out-of-frame) to kill the centred-oval habit.

## Lessons banked

- **Faces read from value-blocking, not height-fields** (confirmed again): the
  first render keyed a smooth summed-gaussian z, and the darkest hatching pooled
  at the silhouette rim → a stone, not a face. Painting explicit lit-plane /
  core-shadow masses fixed it immediately.
- **Hatching = tone-gated line layers.** A clean, reusable lever: `line(θ,s)` ×
  `clip((D−t)/soft)`, summed over layers with rising t. Waver (low-freq) + grain
  (high-freq) give the hand. White-chalk highlights are the same engine gated on
  *light* over a toned ground (trois-crayons).
- **Iso-VALUE contours ≠ engraving.** Hatching the level-sets of the value field
  makes every feature close into concentric loops (whorls) — a topographic /
  thumbprint look, not parallel engraving. Real engraving keeps strokes roughly
  parallel and varies their *spacing* with tone; form-following means rotating
  the stroke *direction* by the local gradient, which is the next experiment.

## Run

```
python3 -m venv .venv && .venv/bin/pip install numpy   # repo root
.venv/bin/python src/hatched_face.py                    # writes all three PNGs
```
