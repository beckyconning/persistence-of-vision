# Techniques log — what's already been done

Check this **before** starting a creative session. If your idea is already here,
either choose something else or push it into genuinely new territory (a new axis,
not a new parameter set). The point is to stop accidentally re-making the same
thing.

Mark each with the session it first appeared. Add a new block per session.

---

## Session 1 — 2026-06-27 (the first gallery)

**Overall corner:** static raster PNG · pure abstraction · density-accumulated
systems · neon-on-near-black · centered/symmetric · decorative. (See
[MANIFESTO.md](MANIFESTO.md) for why this is a corner to leave.)

### Infrastructure
- **Hand-rolled PNG encoder** in pure stdlib (`zlib` + `struct`), 8-bit RGB,
  filter-0 scanlines. (`pnglib.py`)
- **Matching PNG decoder** for filter-0 files (used by the contact-sheet montage).
- numpy for all the math; a venv because the system Python is externally-managed.
- Density-histogram → `log1p` → gamma → multi-stop color-ramp rendering pipeline
  (the workhorse for every attractor/field). **Heavily reused — retire or evolve.**
- Additive deposit + filmic tone-map (`1 - exp(-acc*k)`) for line/particle work.

### Pieces & methods
- **Strange attractors** (iterate a map for millions of points, density-shade):
  - de Jong map — twice (stdlib-only 1M pts; numpy 80M pts via parallel walkers).
  - Lorenz system — ODE, RK4 integration, 9k trajectories → the "butterfly."
  - Clifford map — ~60M points, interlocked ember rings.
  - *Trick:* run thousands of independent walkers in lockstep; they all fall onto
    the same attractor, which vectorizes beautifully.
- **Escape-time fractals** (per-pixel iteration, smooth/continuous coloring):
  - Julia set (z²+c) with smooth escape + 2× supersampling.
  - Mandelbrot zoom into the seahorse valley, 900 iterations.
  - Newton fractal on z⁵−1 (color = which root each point converges to).
- **Noise fields:**
  - fBm value noise built from scratch (random lattices, smoothstep, octaves).
  - Flow field — 30k particles advected along the fBm; ink-in-water look.
  - Domain-warped fBm (Inigo Quilez: noise feeding noise's coordinates, ×2).
- **Reaction-diffusion:** Gray-Scott, "mitosis" regime, a colony growing/dividing
  from a central seed. *Hard-won lesson below.*
- **Parametric curves:**
  - Harmonograph (two decaying pendulums, 2:3 ratio, detuned to precess).
  - Maurer rose (rose curve walked in fixed angular steps, chords woven).
- **Tilings:**
  - Phyllotaxis (golden-angle floret packing; Fibonacci spirals emerge).
  - Voronoi "stained glass" (nearest-seed cells, edge-darkened for depth).
- **Contact sheet / montage** assembled by decoding the PNGs and tiling thumbnails.

### Lessons banked
- Gray-Scott has two conventions: a **normalized** Laplacian (Karl Sims weights,
  center −1) needs `Du,Dv ≈ 1.0, 0.5`; the raw finite-difference Laplacian uses
  `≈ 0.16, 0.08`. **Mixing them** makes diffusion ~6× too weak and every pattern
  freezes into dead spots. Match the pair to the operator.
- Mitosis fills from a **localized seed**, not a uniform field (uniform low-V
  decays to the trivial state).
- numpy 2.0 removed `ndarray.ptp()` → use `np.ptp(x)`.
- Desktop on macOS is TCC-protected: a sandboxed `ls` is denied even though the
  writes land. Verify with `stat`, not by listing.

### The most over-used move (retire next time)
"Iterate a dynamical system → accumulate density → glow palette on black."
Stunning, and done to death in one sitting. Next session should not open here.

---

## Session 2 — 2026-06-28 (landscapes / leaving the corner)

**Overall:** deliberately spread across axes (vs session 1's single corner). One
subject (a landscape) in four registers.

- **Representational landscape** (raster): layered hill bands via summed 1-D value-noise
  ridges; **atmospheric perspective** (far layers hazed toward the sky colour); soft
  **non-additive** sun (multiplicative lighten, not glow-accumulation); earth/paper palette;
  low horizon + negative-space sky. (`landscape.py`)
- **APNG animation** (`dusk.py`): hand-rolled APNG encoder — `acTL`/`fcTL`/`fdAT` chunks over
  the stdlib PNG machinery; full-frame ping-pong loop; day→dusk palette + sinking sun. First
  motion piece. *Reusable encoder.*
- **Vector / SVG** (`vector_hills.py`): flat-colour hill bands as quadratic `path`s + a hard-edge
  `circle` sun; pure text output, no numpy. First vector piece. View via `cairosvg svg2png`.
- **Agnes Martin homage** (`martin.py`): pale alternating wash bands + a faint hand-wavering
  pencil grid (per-pixel jitter + sine) on warm paper; restraint/negative space.

**New levers banked:** APNG encoding; SVG emission; atmospheric haze; slope/− and
multiplicative (non-additive) lighting; hand-wavering line via per-pixel jitter.

**Retire next:** the receding-hill-bands silhouette (used 3/4 pieces this session).
- **Still life — COMPUTED light** (`stilllife.py`): a tiny analytic renderer. Lambert
  (`n·L`) + ambient + soft specular (reflected-ray `**24`) on spheres via per-pixel
  normals `nz=sqrt(1-x²-y²)`; **real soft cast shadows** = each disc's silhouette
  projected onto the ground along `L`, accumulated, box-blurred (cumsum) for penumbra.
  First *simulated* (not painted) light + shadow. **The big new lever.**
- **Reclining figure** (`figure.py`): generalised the renderer sphere→**ellipsoid**
  (rotated implicit; Lambert + specular) and composed shaded volumes into a Moore/Brancusi
  reclining form on a plinth + soft cast shadow. *Half-works* — reads as nested stones more
  than a body; logged honestly. Figure proportion/pose is the open problem.
- **Figure v2 — metaball union** (`figure2.py`): the fix for v1's "nested stones". Per
  pixel keep the nearest (max surface-height) ellipsoid and shade ONE unified normal →
  overlapping volumes fuse into a single continuous body. Key lever for organic forms.
- **ASCII art / image-as-input** (`ascii_art.py`): first time an image is an *input* —
  a filter-0 PNG **decoder** reads my own landscape, block-averages to a char grid,
  contrast-stretches, maps luminance→70-char ramp → text canvas (`landscape_ascii.txt`).
  New axes: image-as-input + ASCII/text form.
- **Typography "GROW"** (`type_grow.py`): inline 5x7 bitmap font → letter cells; "grown"
  by a process (summed-area-table bloom halo + noise-eroded core + drifting sprout flecks).
  First letterform-as-subject. Moves the typography axis; ties the session theme.
- **Bas-relief portrait** (`portrait.py`): sculpt a face as a height field `z(x,y)` by
  summing smooth mounds/recesses for each structure (dome, brow, nose ridge+bulb+alae,
  recessed eye sockets + raised eyeballs, cheeks, a single lip-mass split by one groove,
  jaw-tapered chin), then derive **normals from `np.gradient(z)`** and Lambert+specular
  under one key light. Lesson: model a mouth as ONE swell cut by ONE seam (two separate
  lip mounds always read as stacked sausages). Eye **catchlights** (a 2px white fleck)
  are the single cue that sells it as a face. First subject = the human face.
- **Profile head from a contour** (`profile.py`): a side-view face is defined by its
  FRONT contour (forehead→nose→lips→chin) — model per-row span `[front(t), back(t)]`
  from control points, fill, and sculpt interior relief. **Bug→lesson:** piecewise-
  linear contours leave a slope crease at every control-point row, and a rounded
  cross-section turns each crease into a horizontal ridge ("melting" face). Fix:
  **smooth the 1-D contour curves** (moving average) before building the section.
  Feather a hair mass with a heavy box-blur of its boolean region (no hard hairline).
- **SDF ray-marcher / computed light** (`raymarch.py`, `raymarch2.py`): vectorised in
  numpy — per-pixel ray marched through a signed-distance scene (sphere-trace, ~100
  steps); **normals = SDF gradient** (6 finite-diff evals); **soft penumbra shadows** by
  marching toward the sun and accumulating `min(k·h/t)`; **AO** by sampling the field
  along the normal; sky-bounce ambient + spec + distance fog + gamma. Lessons: clamp the
  AO term `≥0` and use ≥8 samples or you get concentric rings; start the shadow march a
  bit off the surface (~0.12) to avoid a grazing contact-ring. **`smin`** (polynomial
  smooth-min) fuses primitives into one organic body (SDF metaball) — the path from
  "raytracer demo spheres" to an actual sculpture. Light is now *simulated*, not painted.
- **Ray-marched reflections / second bounce** (`raymarch4.py`): where the primary ray
  hits the floor, reflect it (`rd - 2(rd·n)n`) and **march again** from the hit point,
  shade that second hit, and blend into the floor by a Fresnel weight
  (`0.04 + 0.96·(1-cosθ)^5`, grazing → more mirror). Factor `march()` + `shade()` so the
  same code serves primary and reflection passes. Turns a matte floor into a polished one
  that mirrors the subject — real GI beyond direct light.
- **Real PNG decoder** (`2026-06-29-image-as-input/src/pngdecode.py`): the kit could only
  *write* filter-0 PNGs; to use images as INPUT, decode arbitrary ones. Parse chunks
  (IHDR/PLTE/IDAT*/IEND), `zlib.decompress` the concatenated IDAT, then **reverse the
  per-scanline filter** — None/Sub/Up/Average/**Paeth** (predictor = whichever of left/
  above/upper-left is closest to `a+b-c`). Handle colour types 0/2/3/4/6 (gray, RGB,
  palette, +alpha; composite alpha onto white → RGB). **Lessons:** do the filter
  arithmetic in Python `int` then `& 0xff` (uint8 `+` warns + is easy to reason wrong);
  Sub/Average/Paeth are inherently sequential per row (each pixel depends on the
  reconstructed one to its left) so they don't vectorise — loop them. Proof it's a *real*
  decoder, not a filter-0 reader: matplotlib-produced PNGs in the corpus use adaptive
  filtering, so the Sub/Paeth branches actually fire on them.
- **Photomosaic / image-as-input** (`2026-06-29-image-as-input/src/mosaic.py`): rebuild a
  target image from tiles of a corpus. Decode every source, slice each into N×N sub-crops
  (more crops = richer tonal palette), downscale each to a CELL thumbnail, store its mean
  RGB. Downsample the target to a cell grid; for each cell pick the tile of nearest mean
  colour (squared distance), then **nudge the tile toward the cell colour** by ~0.5 so the
  picture holds at a distance while tiles stay legible up close. Penalise a tile reused
  adjacent to itself (add to its distance) to avoid diagonal striping. **Lessons:** the
  correction-strength is the whole game — too low and it's tile noise, too high and it's a
  blurred target with no tiles; ~0.5 is the sweet spot. Smooth gradient regions (a flat
  sky) have no matching tiles so they collapse to near-flat colour-correction — needs a
  tonally-diverse corpus. Greedy nearest-colour repeats more than a global assignment
  would. Self-referential payoff: tiling the corpus into a *new* image of the work itself.
- **Pixel-sorting / image-as-input transform** (`2026-06-29-pixelsort-image-input/src/pixelsort.py`):
  decode an image (reuse `pngdecode`), then within each column/row sort contiguous runs of
  pixels by a key (luma, or saturation for hue-sorts) — but ONLY where luma is inside a
  threshold band `[lo,hi]`; out-of-band pixels are ANCHORS that never move. Mid-tones melt
  into glassy streaks while highlights/shadows pin the structure, so the result still reads
  as its source. **Lessons:** the threshold band is the entire trick — too wide and it all
  smears to mush, too narrow and nothing moves; pinning darks+brights keeps the silhouette.
  Vertical sort = dripping/melting; horizontal = flowing. Run = maximal in-band stretch,
  reorder by `argsort(key[run])`. First time the kit DERANGES an image vs constructs one.
- **Droste recursion / image-in-itself** (`2026-06-29-droste-recursion/src/droste.py`): paste a
  shrunk+rotated+darkened copy of the whole image into a centred window inside it, N levels deep
  (rebuild outermost-last: each level = fresh source with a resized copy of the running canvas
  pasted in). A per-level rotation turns flat picture-in-picture into a vortex. Needed real
  **bilinear resize** + **center rotation** (nearest, clamp OOB to avoid black corners) in numpy.
  **Lessons:** compounding a <1 brightness factor per level murks a dark source fast — brighten
  WITH depth instead; a fixed centred window gives a head-on tunnel (off-centre = a vanishing
  point); this is discrete nesting, not the true conformal log-spiral Droste warp.
