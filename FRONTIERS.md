# Frontiers — the backlog of where to grow

The antidote to sameness. When a creative session starts, **pick from here**
(or add to it). Prefer directions that move along an axis
([MANIFESTO.md](MANIFESTO.md)) the recent work hasn't touched.

Format: keep the top section **"Up next"** as a short, curated shortlist that a
session can grab immediately. Below it, a deep well organized by axis. When you
try something, move it to [TECHNIQUES.md](TECHNIQUES.md) and note what happened.

---

## ⭐ Up next (curated — grab one of these)

Session 2 moved: representational, animation/APNG, vector/SVG, earth/riso palette,
restraint/homage. ✅ Don't re-open on **landscape hill-bands** (session 2's motif).
Still unmoved — grab one:

1. **Still life with REAL cast shadows.** 2–3 simple objects on a surface, a single
   light source, actual projected soft shadows (not slope-tinting). The light axis is
   still *painted*, never *simulated* — this is the next real step.
2. **A figure / face.** No living subject yet — even abstracted or geometric.
3. **Generative typography.** A word/letterform as the subject — eroded, woven,
   grown, or shattered by a process. (Needs a small vector-glyph system.)
4. **Image-as-input / collage.** Take an existing image and transform it — never
   done; would also exercise a real PNG *decoder* beyond filter-0.
5. **Light simulation proper.** A tiny raymarcher / SDF scene with ambient occlusion
   + cast shadows — turn "painted light" into "computed light."

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
