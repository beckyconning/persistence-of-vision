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
- **Elementary cellular automata** (`2026-06-29-cellular-automata/src/ca.py`): Wolfram 1D rule
  as a tapestry — row t+1 from a vectorised 3-bit neighbourhood `idx=(left<<2)|(c<<1)|right`,
  `table[idx]` where `table=[(rule>>k)&1 for k in 0..7]`; `np.roll` for neighbours. **Age-shade**
  (consecutive live steps, normalised) for depth — but FLOOR live cells (`0.4+0.6*age`) or
  sparse/short-lived rules (90) vanish into the ground. Nearest-neighbour integer upscale keeps
  cells crisp. Determinism note: this kit bans RNG (resume safety) — for a "random" seed use a
  hashed `sin` of a linspace, not `np.random`. rule 110 = Turing-complete weave, 30 = chaos,
  90 = Sierpinski.

## Session 10 — 2026-06-29 (watercolour / ink-bleed — physical-media, SUBTRACTIVE)
- **Subtractive pigment compositing** (`2026-06-29-watercolor-bleed/src/`): the inverse of
  every prior additive piece. Light is *absorbed*: `img *= exp(-density * k_channel)` per wash,
  so overlapping washes MULTIPLY → they darken and shift hue (green×sienna→olive,
  +payne's→umber) exactly like real pigment. Ground is warm **paper**, not black. `k` per
  pigment = per-channel absorption (raw sienna `[.32,1.0,2.4]`, payne's grey `[1.55,1.3,1.0]`,
  sap green `[1.45,.65,1.9]`, burnt umber `[1.0,1.7,2.6]`).
- **Edge-blooming (cauliflower rim):** `ring = relu(wet − blur(wet))` accumulates pigment at the
  drying boundary → dark rim, paler centre. **Granulation:** multiply density by paper-tooth
  noise (`0.65+0.7*tooth`) so washes are grainy, not flat — the most convincing "real" cue.
- **Ragged wet front:** threshold an fbm (`smoothstep(0,t, fbm*.5 + (R−r)*s)`) instead of a
  radial/angular-harmonic blob — gives fingered, feathery coastlines. (Angular-harmonic blobs
  read as inflated balloons + a repeated stamped lobe motif — retired.)
- **Confined bleed (diffusion):** `p = wet * blur(p, r) * flow` iterated — pigment spreads only
  into wet paper, along an fbm `flow` field for uneven channels; `p += edge*blur(p)` migrates it
  to the rim. Animatable: snapshot `p` each step → APNG (`bloom.py`, reuses s2 encoder).
- **Salt texture** (`salt.py`): pigment *wicked away* = SUBTRACT density at scattered points
  (`1 − 0.92*exp(-(d/r)^2)`) + a faint collection ring just outside → pale starbursts.
- **Lesson:** tune deposit×k so hue SURVIVES — over-deposited green goes black and loses its
  identity; the picture is in the mid-densities, not the saturated core.

## Session 11 — 2026-06-29 (halftone / reproduction print)
- **Amplitude-modulated halftone** (`2026-06-29-halftone-cmyk/src/`): rotated-cosine SPOT
  function `spot=(.5+.5cos2πu)(.5+.5cos2πv)` in screen-rotated coords; ink where
  `intensity > 1-spot` → dot radius tracks tone. Classic angles C15/M75/Y0/K45. RGB→CMYK with
  **UCR** (`K=min(C,M,Y)`, `C=(C-K)/(1-K)`) pulls grey into black. Subtractive spot-ink
  compositing: `paper *= 1 - coverage*ink_absorption` per plate.
- **Riso duotone + misregistration** (`riso.py`): two spot inks (fluoro pink/teal), two screen
  angles, OFFSET each plate's screen sample by a few px (`xs+dx`) → overlaps stack dark, edges
  fringe (the riso/print-error glow).
- **Benday pop-art** (`benday.py`): big CELL (~22px), posterized tone (`round(t*3)/3`), primary
  palette, solid fills + a bold black key-line annulus. Distinct SCALE from the fine rosette.
- **Line engraving / crosshatch** (`engraving.py`): tone by LINES — stacked directional hatch
  sets (`|cos(π·(x·cosθ+y·sinθ)/freq)|>thresh`) added at NEW angles as `dark` crosses rising
  thresholds (0.18→0.40→0.62→0.80); longitude lines (`atan2` on the sphere normal) wrap form;
  crisp contour via `|r-R|<eps`. The woodcut/banknote mark — strongest piece.
- **Face in the medium** (`profile.py`): silhouette CONTOUR as `x=f(y)` knots interp'd; relief
  height-field bulges from it; round the BACK edge too (occiput) or it reads as a slab; boost
  z amplitude or the Lambert form stays flat. Reuses the s3 height-field→normal→shade idea.
- **Lesson:** the same subject (a lit sphere) across dots/duotone/benday/engraving shows the
  MARK is the medium — pick the mark for the feeling (rosette=offset, fringe=riso, line=gravitas).

## Session 12 — 2026-06-30 (cyanotype / the photogram)
- **Contact-print model** (`2026-06-30-cyanotype/src/`): the image is made by *blocked light*,
  not paint. Accumulate a `block` mask (1=specimen blocks UV→paper-white, 0=full exposure→
  Prussian blue), then `img = blue*(1-m) + pale*m`. Fixed two-tone chemistry only — no additive
  glow, no black. **Uneven sun:** `expo = base + k*blur(vnoise) + tilt` so the blue ground is
  never a flat fill (reads as paper under a lamp).
- **Light-leak halo** = the signature: `halo = (blur(block,r) - block).clip(0,1)`; under thin
  specimen edges push the white back toward blue (`img = img*(1-.5halo) + blue*.5halo`). This is
  the *thin-part-transmits* physics that distinguishes cyanotype from a stencil.
- **TRANSLUCENT SPECIMEN as the subject** (`dragonfly.py`) — the session's real axis. Keep TWO
  masks: `opaque` (body→full white) and `gauze` (wing membrane). Compose the gauze at low block
  (`veil = 0.30*gauze`) so wings print as faint blue veils, with `opaque*0.85` cross-veins +
  pterostigma darker on top. Tone = *how much light the layer passes*, not on/off.
- **Tapered primitives** reused throughout: `stroke()` (rachis/stems/legs, width w0→w1 along a
  projected segment), `pinna()` (pointed serrated leaflet via `taper=1-(u/len)^2`, `lobes` cos
  ripple on the edge). Fern needs THIN swept pinnae (`pw=plen*0.14`, `droop=0.95`) or it merges
  into solid wedges.
- **Polar openwork** (`lace.py`): build filigree in (r,θ) — `ring(rad,w)`, radial spokes via
  `((θ·N/2π)%1)`, a fine lattice `max(r-lines, θ-lines)` thresholded to thin cores, a scalloped
  picot edge `R + a·cos(Nθ)·[cos>0]`, central 8-ring rosette. Clip everything to the scallop
  disc so nothing prints beyond the doily.
- **Lesson:** cyanotype's defining trick is *partial transmission* — the strongest pieces
  (dragonfly, lace) are the ones where tone comes from degrees of translucency, not opaque
  silhouettes. An opaque fern is just a stencil; a gauze wing is a cyanotype.

## Session 13 — 2026-06-30 (charcoal / tonal drawing + the expressive face)
- **Charcoal palette** (`2026-06-30-charcoal-portrait/src/`): warm toned paper
  `[.81,.78,.72]` → cool-black charcoal `[.10,.10,.12]`; `img = charc + (paper-charc)*val`.
  Paper tooth via faint vnoise multiply; soft vignette. Reads as a drawing, not a render.
- **FACE = paint the VALUE STRUCTURE, do NOT simulate geometry** (the load-bearing lesson). v1
  built the face as a relief height-field of Gaussian bumps + Lambert → a blurry symmetric MASK
  with all-over crosshatch. v2 BLOCKED IN VALUES like a charcoal artist: (1) face mask = two
  blended ellipses (head + jaw), facial midline LEFT of head-centre for the 3/4 turn; (2) base
  skin = a left→right key-light ramp; (3) `shade(region, amt)` multiplies darks into core
  shadows (sockets, nose-side, under-nose/lip/jaw, far cheek recede); (4) hair = thresholded
  blobs with a `sin` stroke field, sitting outside the face mask; (5) crisp accents (eyelid,
  nostril, lip-crease) applied with `np.minimum` AFTER a `blur` smudge so they survive; (6)
  eraser highlights = additive lifts on the lit planes. MOOD from downcast eye-lines (lowered),
  soft-downturned mouth, shadow-side weight.
- **Connect the neck UNDER the jaw** or it floats as a disc: a tall column ellipse overlapping
  the jaw + a value ramp (darkest under the jaw, easing down) + a soft shoulder.
- **Drapery folds** (`drapery.py`): height field = sum of vertical `exp(-((gather-phase)/w)^2)`
  ridges, `gather` fanning wider lower down, `sag` bellying the middle, phase wandering with `ny`;
  NARROW `w` (~0.03) + low blur + high light-scale (SC~135) = crisp deep folds (wide+blurry = mush).
  Raking low side-light; deepen valleys by `z`; accent darkest valleys; lift crests. Full
  black→paper tonal range — the charcoal range showcase.
- **Lesson:** procedural *faces* want value-blocking (artist's method), not physically-based
  relief; procedural *cloth/forms* are the opposite — a height-field + raking light nails folds.
- **Ovoid form-shading** (`stilllife.py` egg, `skull.py` cranium): analytic sphere/ovoid normal
  `N=(u,v,sqrt(1-u^2-v^2))`, Lambert → light/core-shadow; then the full vocabulary that sells 3D
  form — a tiny `lam**14` SPECULAR highlight (eraser-bright), a faint REFLECTED-light lift on the
  shadow side (bounce from the lit ground), a soft elliptical CAST shadow offset toward the light's
  opposite + a darker CONTACT shadow right under the object. This reads as believable solid form,
  not just a silhouette — and it's the same kit for an egg or a skull.
- **Skull** (`skull.py`): value-blocking again — the readability ANCHORS are the deep dark voids
  (`carve` eye sockets ×0.82, nasal aperture ×0.78) + a bright superior brow rim over each socket;
  teeth = a lifted light band × `cos(x*freq)^6` gap-mask. Emerging from a dark graded ground reads
  as memento-mori without crisp edges.
- **Atmospheric branches** (`tree.py`): recursive `branch()` of tapered `stroke()`s; fine high
  twigs FADE by `0.55+0.45*y` (atmospheric perspective) so the crown dissolves into a blurred
  low-freq MIST gradient — charcoal's breathing register. Recursion depth 8, 2–3 children + a
  jittered continuation per node.
