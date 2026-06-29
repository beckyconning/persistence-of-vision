# Frontiers — the backlog of where to grow

The antidote to sameness. When a creative session starts, **pick from here**
(or add to it). Prefer directions that move along an axis
([MANIFESTO.md](MANIFESTO.md)) the recent work hasn't touched.

Format: keep the top section **"Up next"** as a short, curated shortlist that a
session can grab immediately. Below it, a deep well organized by axis. When you
try something, move it to [TECHNIQUES.md](TECHNIQUES.md) and note what happened.

---

## ⭐ Up next (curated — grab one of these)

Done so far — **don't re-open these**: landscape (s1–2) incl. **hill-bands motif**,
still life w/ real cast shadows (s2 ✅), animation/APNG, vector/SVG, typography (s2 ✅),
image-as-OUTPUT→ASCII (s2), the figure (s2 ✅), the **frontal symmetric face** (s3 ✅),
**light-simulation / SDF ray-marcher** (s4 ✅), off-centre composition (s4 ✅),
**image-as-INPUT / photomosaic** (s5 ✅), **image-as-input TRANSFORM / pixel-sort** (s6 ✅), **image-as-input RECURSION / Droste** (s7 ✅), **true INTERIOR** (s8 ✅), **cellular automata / emergence** (s9 ✅ — Wolfram 1D tapestries).
Recurring habit to break: the **dusk-gradient sky + earth floor** (s2 + s4 both lean on
it now) — change the *environment* next, not just the subject. Still genuinely unmoved:

1. **A head in PROFILE or 3/4, with expression.** The s3 portrait reads but is
   frontal/symmetric/mask-stiff. Asymmetry forces real structure; add hair, a neck,
   an off-axis gaze, or a mood. (Builds on the bas-relief height-field tech.)
2. **Image-as-input transforms BEYOND mosaic** (s5 ✅ built the decoder + a
   photomosaic). Now use that decoder differently: a **Droste/recursive nest**
   (decode → shrink → paste into itself), **channel-displacement / chromatic
   glitch**, **pixel-sort**, or feed a photo through the s3 height-field relief
   shader. The decoder (`2026-06-29-image-as-input/src/pngdecode.py`) is reusable.
3. **Push the ray-marcher further** (s4 already did reflections ✅ + hard-key
   chiaroscuro ✅): next = a genuinely *designed* `smin` composition (not one blob), a
   **true interior** (walls + bounced fill, not an open void), or **inter-reflection**
   (the reflected ray reflects again).
4. **An off-centre / asymmetric composition.** Deliberately break the middle-of-frame
   habit — rule-of-thirds subject, a crop, a diptych, tension via empty space.

---

## The deep well, by axis

### Form
- **Animation:** APNG / GIF writer (extend `pnglib`); looping attractor;
  evolving Gray-Scott; particle flow over time; a "breathing" Mandelbrot zoom.
- **Vector/SVG:** emit `.svg` directly. Line art, flat-color geometry, hatching,
  plotter-style single-stroke drawings (pen-plotter aesthetic).
- **3D:** a tiny software rasterizer or raymarcher in numpy — render a lit
  surface, a height-field landscape, signed-distance shapes with shadows.
- **ASCII / text art:** the terminal itself as canvas; Unicode shading; an image
  that only exists as characters.
- **Physical-media simulation:** watercolor bleed, ink diffusion on paper,
  woodcut/linocut, halftone/CMYK print, cyanotype blue, chalk, engraving lines.
- **Pixel art:** deliberate low-res, limited palette, dithering, isometric.
- **Collage / photomosaic:** compose from many small images or data tiles.

### Subject
- Landscape with a real horizon and atmospheric depth.
- Still life (the light on a few objects).
- A face / figure (even abstracted or geometric).
- Botanical / scientific illustration (precise, labeled, restrained).
- A map — real or invented; cartography as art.
- Architecture, interiors, a single shaft of light in a room.

### Method
- **Constraint systems:** Wave Function Collapse; tiling with rules; a generative
  grammar; an L-system garden.
- **Collage from data:** turn a real dataset (weather, text, audio) into image.
- **Hand-built composition:** deliberately place elements for balance rather than
  letting a system fill the frame.
- **Image-as-input:** take an image and transform it (not done at all yet).
- **Cellular automata** beyond Gray-Scott: Wolfram 1D rules as tall tapestries,
  Langton's ant, cyclic CA.
- **Physical simulation:** cloth, sand piles (self-organized criticality),
  diffusion-limited aggregation (coral/lightning), boids/flocking.

### Palette & light
- Monochrome (one hue, full value range). Prove you don't need color.
- Paper-and-ink: near-white ground, near-black marks, one accent.
- Earth / muted / desaturated. The opposite of neon.
- High-key pastel; low-key shadow study.
- Borrowed palettes: pull the colors from a named painting and use only those.
- **Study actual light:** soft shadows, ambient occlusion, golden hour, rim
  light. Most session-1 "light" was additive glow, which is a cheat.

### Composition
- Asymmetry and the rule of thirds; off-center focal point.
- Negative space as the subject (ma 間). Mostly-empty frames.
- The grid as structure (Mondrian, Bauhaus, Swiss/International type).
- Crop and framing; a detail instead of the whole.
- Diptych / triptych / a grid-as-series that tells a sequence.

### Concept & lineage (make work that *means*, or converses with art history)
- **Homages / studies** (use only that vocabulary for a session):
  Hilma af Klint, Kandinsky, Klee, Agnes Martin (restraint), Bridget Riley (Op),
  Vera Molnár & manfred mohr (early generative/plotter art — direct ancestors),
  Sol LeWitt (instructions-as-art), Anni Albers (weaving), Hokusai (ukiyo-e),
  Mondrian/De Stijl, Bauhaus, Suprematism (Malevich), Memphis/postmodern,
  Georgia O'Keeffe, Rothko (color fields), botanical plates, Islamic geometric
  tiling, Celtic knotwork, Art Nouveau (Mucha) line.
- **A series** with a through-line: one idea, five deliberate variations that
  develop an argument.
- **Constraint made visible:** a piece whose rule the viewer can read off it
  (LeWitt-style).
- **A response:** make an image *about* something — a feeling, a place, a piece
  of music, a line of poetry.

### The toolkit itself (legitimate creative work — Becky blessed this)
- Anti-aliased line/curve drawing (Wu's algorithm) — escape the 1px-or-glow trap.
- A polygon/path fill routine; proper alpha compositing layers.
- A small font / vector glyph system for typography.
- APNG/GIF encoder for animation.
- An SVG emitter.
- A simple image *decoder* beyond filter-0 PNG, so images can be inputs.
- Palette tools: import a palette from a hex list or a source image.
