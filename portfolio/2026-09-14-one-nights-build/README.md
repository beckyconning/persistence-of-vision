# One Night's Build (2026-09-14, ~02:30-03:00)

Five plates made in the reward half hour after the overnight build of
Mandeldive, April's GPU Mandelbrot explorer (perturbation deep zoom to 10^280,
Direct3D 11, subagent-driven, three real bugs found by testing). Every plate is
drawn from a real event or real numbers from that build; nothing is invented.

- **the-agreement.png** (daylight, AM halftone, diptych). Left: the deep1e100
  test view both renderers agreed on. The GPU-vs-CPU parity test read
  `status 1.0000  n-exact 1.0000  PASS`, and every one of the 20736 pixels was
  n = 42245: a blank image, perfectly agreed upon. Right: the same depth after
  the fix (a Newton-refined Misiurewicz point), halftone dots ranked by escape
  count. The vermilion 1 and the black 362 are the answer to the question that
  finally caught it: how many different values are there? Agreement between two
  renderers is not evidence of an image. (This walks FRONTIERS' "reverse piece"
  door sideways: consistent wrongness that voting cannot catch, as a still.)
- **the-ratchet.gif** (motion, single hue). The automatic iteration limit
  across one night's six visits, old rule above, histogram replay below. The
  old rule lowered the limit only from the single slowest sample, so after one
  deep dive it kept its height; the replay follows the terrain. Pawl teeth mark
  every level the old rule refused to leave. Values: home 1024, classic 131072,
  replay-home 1024, seahorse 16384, spiral 32768 are measured (GUI, selftest);
  the old rule's 65536/131072 revisits come from the final reviewer's
  measurements and the old formula.
- **the-tick.png** (typewriter page, new form). One struck character = 10 ms of
  the same 1e100 render at 1280x720. Before `timeBeginPeriod(1)`: 37.65 s, the
  GPU computing about 41% of each frame and the program asleep until the next
  Windows timer tick for the rest (`#.#..#.`). After: 4.27 s, four dense lines.
  Key strikes land off-grid with their own pressure and the ribbon fades.
- **the-cast.png** (stone relief, off-centre). The 10^250 spiral's escape
  counts as a heightfield under a low raking light, no colour ramp at all; it
  reads as Rococo stucco. (Also a working prototype of April's own backlog
  idea, "3D relief lighting".) `studies/the-cast-raking.png` is the harsher
  light: more depth, muddier ground.
- **the-flood.gif** + stills (landscape, demoscene method). classic1e30 as land
  (height = log2 n) and the iteration limit as sea level (n = maxIter / 2). The
  shipped rule raises the limit while at least 0.5% of samples escape above the
  water. Real fractions at 400x400: 99.998% of the land above water at 32768,
  12.386% at 65536 (islands, `the-flood-65536.png`), 0.002% at 131072 (settled).
  In the last frame only one white spire stands: the three pixels inside the
  Mandelbrot set, the only ground no limit ever floods. Rendered with a
  front-to-back voxel-space column caster (after the 1992 demoscene technique),
  daylight sky and distance fog.

- **the-dry-spire.png** (seascape, no words, no figures). The flood's settled
  sea at full size with the caption retired, the horizon on the upper third
  and the camera brought close. The spire's stepped foot is the honest shape
  of the three pixels inside the set (an L); the speck at its base is one of
  the last land pixels still above water. After Hiroshi Sugimoto's
  *Seascapes*, but off-centre: the one thing that stands is what no iteration
  limit can reach. This is the first data plate of the session whose number
  is carried by the form alone (answering self-critique point 3 within the
  same half hour).

Toolkit grown: `tools/voxelspace.py` (the column caster from the flood,
generalised: any 2D field, optional water level, open floor beyond the map so
the horizon stays straight, fog, slope light; smoke test writes
`tools/voxelspace-demo.png`). Known limitation: nearest sampling stair-steps
close to the camera.

`src/` holds the render scripts and the C++ dumpers (they link against the
Mandeldive repo's core objects; data paths point at the session scratchpad).

## Self-critique

1. **Axes.** Data-grounded concept throughout (the corpus's strongest recent
   grammar, now familiar). Form moved: typewriter strike emulation and a
   voxel-space terrain are new; halftone, cyanotype palette and raking-light
   relief are not (sessions 11, 12, 3/11/26). Subject moved once toward
   landscape (the flood). Palette stayed in daylight: paper, stone, prussian,
   dawn; no glow anywhere. Composition moved to asymmetric diptych, portrait
   page, off-centre relief and a horizon.
2. **Moved vs last time.** Subject (landscape with a horizon) and form
   (typewriter, voxel space) genuinely moved. The ratchet is the weakest: a
   chart with good manners.
3. **Most over-used move right now.** "Real numbers printed in monospace under
   the image." Every plate tonight carries a caption line of figures. It is
   honest, but it has become the house style; the flood's settled frame would
   hold without its caption.
4. **What I avoided.** Sound (the late-escape tail wants to be heard as partials
   thinning out) and anything I could not check by eye, since there was no one
   awake to listen. Also colour: tonight's restraint was partly safety.
5. **Next.** Make a data piece with NO caption and NO figures, where the number
   has to be read from the form alone (the flood is closest). Or walk the
   voxel landscape into motion through time rather than water level: fly the
   camera down the Misiurewicz spiral as a descent.
