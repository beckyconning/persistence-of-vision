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
