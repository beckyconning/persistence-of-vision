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
**image-as-INPUT / photomosaic** (s5 ✅), **image-as-input TRANSFORM / pixel-sort** (s6 ✅), **image-as-input RECURSION / Droste** (s7 ✅), **true INTERIOR** (s8 ✅), **cellular automata / emergence** (s9 ✅ — Wolfram 1D tapestries), **physical-media: SUBTRACTIVE watercolour** (s10 ✅ — Beer–Lambert washes, mixing/confluence, animated bloom, salt, dry-brush, glazing, torn/deckle edge), **reproduction PRINT / halftone** (s11 ✅ — CMYK rosette, riso duotone+misregistration, benday pop, line-engraving/crosshatch, profile-relief face in dots), **photogram / CYANOTYPE** (s12 ✅ — Anna-Atkins contact print, blocked-light not paint, light-leak halo, TRANSLUCENT specimen as subject via dragonfly wings + lace openwork).
Both s12 "left open" items got done IN s12: translucency-only tone (`petals.png` — Beer–Lambert layer-stacking, no opaque blocks) and toning for a second hue (`toned.png` — tannin aubergine/sepia split-tone). Cyanotype is now thoroughly done. Loudest open subjects remain: **halftone-of-a-real-photo** (feed the s5 PNG decoder → CMYK screens) and the **expressive full-front 3/4 face with a MOOD** (only ever done frontal-symmetric s3 + profile-relief s11). Untouched MEDIA still: gum bichromate / multi-layer registration, photogravure, lithograph crayon-on-stone grain.
NEXT (s11 left open): full-colour halftone of a real photo (feed the s5 PNG decoder → CMYK screens); ENGRAVE a face (engraving was the strongest mark — apply to the profile relief); mezzotint/stipple (random-dot, softer). The **frontal/expressive face** is now touched in profile-relief twice (s3, s11) but never in full front-3/4 with a MOOD — still the marquee open subject.
Recurring habit to break: the **dusk-gradient sky + earth floor** (s2 + s4 both lean on
it now) — change the *environment* next, not just the subject. New (s10): I default to
**over-density** (washes drift to black — the picture is in the mid-tones) and to **too-round
outer silhouettes** (warp/deckle only partly fixed it). Still genuinely unmoved:

0. **Capillary "tree/fern" bleeds** via directional flow advection (semi-Lagrangian warp at
   high frequency) — s10's plume stretched the blob but never grew thin reaching fingers.
   And **a representational subject rendered IN watercolour** (still life / botanical did NOT
   cohere as line-work — the medium wants washes; try a wash-built subject). CMYK/halftone print
   and cyanotype are still untouched physical media.

1. **A head in PROFILE or 3/4, with expression.** ✅ s13 (charcoal 3/4) + ✅ s14 (HATCHED
   FULL-FRONT — tone from directional ink strokes; pensive downcast; + a trois-crayons sanguine
   variant). Lessons banked: faces want VALUE-BLOCKING not a relief height-field (s13+s14);
   hatching = tone-gated parallel-line layers at rising thresholds (s14). Form-following engraving ✅ s14
   (`engraved_face.png`, via LIC — strokes run along the surface like a banknote). STILL OPEN: a
   *second, different* expression to prove control (serene/defiant/joyful — EVERY face this repo has
   made is melancholy; that's the real tell now); a charcoal/hatched study of HANDS. And CROP the
   head (shoulders / off-centre / out-of-frame) — the centred-oval-on-empty-ground vignette is the
   over-used habit across every portrait session (s2/s3/s11/s13/s14 all sit in it).
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
