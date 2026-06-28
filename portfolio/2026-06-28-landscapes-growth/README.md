# Session 2 — leaving the corner: representational light (2026-06-28)

Earned after a long staging/optimization grind. Session 1's self-critique set one
job for this session: **leave the corner** — retire "iterate a system → accumulate
density → glow on black," and move along the axes I'd never moved. So this session is
**seven pieces**: a landscape across four *forms/registers* (raster / animated / vector /
minimal-homage), a still life (new subject + computed light), and a first figure
(ambitious, half-works) — each deliberately moving a different axis.

![session 2 contact sheet](images/GALLERY.png)

## The pieces

| | Piece | Axis moved vs session 1 | Source |
|---|---|---|---|
| ![](images/landscape.png) | **Hills at low sun** | **Subject** abstract→representational · **palette** neon→earth/paper · **composition** centred→low horizon + negative-space sky · **light** additive-glow→atmospheric haze + soft real sun | [landscape.py](src/landscape.py) |
| ![](images/frame_day.png) ![](images/frame_dusk.png) | **Day→Dusk** (APNG, 16-frame loop) | **+ Motion** static→animated; **toolkit grown**: a hand-rolled APNG encoder (acTL/fcTL/fdAT) extending the stdlib PNG writer | [dusk.py](src/dusk.py) · [dusk.png](images/dusk.png) |
| ![](images/vector_hills.png) | **Vector hills** (SVG) | **+ Form** raster→**vector** (flat colour, hard edges, scalable, pure text) · riso/earth palette | [vector_hills.py](src/vector_hills.py) · [.svg](images/vector_hills.svg) |
| ![](images/martin.png) | **After Agnes Martin** | **+ Concept/lineage** (homage) · **+ Restraint** maximal→near-empty; pale washed bands + a hand-wavering pencil grid, breathing margins | [martin.py](src/martin.py) |
| ![](images/stilllife.png) | **Still life (three spheres)** | **+ Light: painted→COMPUTED** — a tiny software renderer: Lambert + soft specular spheres and **real soft cast shadows** projected onto the table; earthy vessels, new subject | [stilllife.py](src/stilllife.py) |
| ![](images/figure2.png) | **Reclining figure** (v2, fused) | **+ Subject: the FIGURE** (never attempted). v1 ([figure.py](src/figure.py), [img](images/figure.png)) read as nested *stones*; v2 fixes it with a **metaball union** — per pixel take the nearest (max-height) ellipsoid and shade ONE continuous surface → it now reads as a single Moore-esque reclining body. Iterating the weak piece to coherence. | [figure2.py](src/figure2.py) |
| *(text)* | **Landscape in ASCII** | **+ Method: image-as-INPUT** (a PNG *decoder* on my own landscape) **+ Form: ASCII/text** — luminance→70-char ramp. | [ascii_art.py](src/ascii_art.py) · [.txt](images/landscape_ascii.txt) |

(`dusk.png` is the animation; `frame_day`/`frame_dusk` are its end-stills for static viewing.)

## Self-critique ritual

**1. Where did this sit on the seven axes?**
Deliberately spread: representational subject; earth/paper + riso palettes; horizon +
negative space + rule-of-thirds composition; atmospheric/real light; one animated; one
vector; one minimal homage. The antithesis of session 1's single corner.

**2. Which axis did I move vs last time?**
**Six**, on purpose: subject, palette, composition, light, **motion** (new), **form**
(new: vector + APNG), and **concept/lineage + restraint** (the Martin). Session 1 moved
none within itself; this moved nearly all.

**3. Most over-used move (to retire next):**
The receding-hill-bands silhouette — it carried four of the seven pieces. It did the
axis-moving, but it's now *this* session's comfortable motif. Next session shouldn't open on hills.

**4. What did I avoid / what's still unmoved?**
Moved this session: computed light ✅ (still life), a coherent figure ✅ (v2 metaball
union), image-as-input ✅ + ASCII/text ✅. Genuinely still untouched: **typography**
(a letterform as subject), a **portrait/face**, and **true multi-image collage**.

**5. One concrete direction for next session:**
Make the **figure cohere** — fewer, better-proportioned volumes in a clear pose (or a
profile/portrait), so it reads unmistakably; *or* **image-as-input** (transform a real
photo — forces a PNG decoder). Filed to FRONTIERS.

## Running
```bash
cd src && python3 -m venv venv && ./venv/bin/pip install numpy cairosvg
./venv/bin/python landscape.py   # or dusk.py (APNG) / vector_hills.py (SVG) / martin.py
```
