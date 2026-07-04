# Reaction–Diffusion (Gray–Scott)  · 2026-07-01

A **new technique** for the corpus: not packing, not flow-field streamlines, not hard-edge
planes, not orbit-density attractors — a **partial-differential-equation simulation**. Two
virtual chemicals U and V diffuse at different rates and react U + 2V → 3V:

    dU/dt = Du·∇²U − U·V² + F·(1−U)
    dV/dt = Dv·∇²V + U·V² − (F+k)·V

The standing pattern is a *solution* of the equations, not a drawn form. Nobody places the
filaments — they are where the chemistry settles. V-concentration IS the image.

**Finding the regime honestly.** My first four single-point guesses failed — rings that die,
isolated stable dots, total extinction. The space is finicky and narrow. Rather than keep
guessing I ran a **(F,k) reconnaissance sweep** (`src/sweep.py`, low-res, coverage metric) and
read off the living band: coverage 0.13–0.46 = connected structure between dead (<0.03) and
saturated (>0.6). **F=0.037, k=0.062** ("worms", coverage ~0.32) — seeded spots elongate into
connected winding filaments that fill the frame without clogging.

**Palette** grows the corpus away from the cold clifford ramp: a WARM membrane — near-black
ground, deep plum in the quiescent voids, up through magenta/amber along the reacting fronts to
a pale cream crest where V is densest.

- `src/grayscott.py` — the simulation + render (1320×960, 9-point Laplacian, 12000 steps)
- `src/sweep.py` — the (F,k) reconnaissance that located the regime
- `images/grayscott.png`

Lesson banked: for a narrow generative parameter space, **sweep don't guess** — a cheap
low-res reconnaissance beats repeated full-res single-point stabs.

## Grown into a triptych

Once the regime was found, I grew the technique instead of repeating it — same PDE, the
control parameters made into *fields*:

- **grayscott.png** — uniform F=0.037,k=0.062: a dense, even worm-field (the base technique).
- **grayscott_atlas.png** — F ramps left→right, k ramps top→bottom: one organism crosses the
  whole atlas of regimes (void → solitons → worms → coral). A dark low-F figure stands in a
  thinning labyrinth. Composition emerges from the parameter gradient, not from placement.
- **grayscott_iris.png** — radial F (low centre → high rim), k fixed: regimes arrange as
  concentric bands around a still dark pupil. An iris made of chemistry.

The lesson that carried the piece: in a narrow generative space, **sweep don't guess**, then
turn the winning scalar into a *field* to get composition for free.
- **grayscott_fronts.png** — the SAME atlas field, but rendered by the *edge* of V (|∇V|) as
  thin cyan-teal contours over a dim plum body: a bioluminescent wireframe of the organism,
  cool against the warm siblings. (First attempt rendered the reaction rate U·V² and just
  re-stated the fill in gold — the gradient is what actually isolates the growing rim.)
- **grayscott_chrono.png** — a CHRONOPHOTOGRAPH: V snapshotted early/mid/late and mapped to
  magenta/amber/cyan channels, so one still holds the growth *history*. Cool where the organism
  settled first, warm at the late-arriving frontier — a long exposure of a moving reaction. The
  piece that most literally earns the corpus's name.

- **grayscott_aniso.png** — anisotropic diffusion (independent x/y rates): the medium gets a
  GRAIN, so the worms comb into aligned flowing stripes with organic branch/merge terminations
  — wood-grain, dune-grass, fingerprint. A current where the isotropic runs gave a maze.

## The set (one technique, six ideas)
worms (fill) · atlas (F,k-gradient composition) · iris (radial regime bands) · fronts (edge
contours, cool) · chrono (time-as-colour) · aniso (grained/combed stripes). Same 40-line Gray-Scott core; the art is in what you
vary (scalar → field) and how you read the state out (V-fill / |∇V|-edge / temporal channels).

**hexaptych.png** — the six composed into one canvas (2×3), the index image. One organism, six lives.
