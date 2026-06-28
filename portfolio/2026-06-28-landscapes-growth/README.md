# Session 2 — leaving the corner: representational light (2026-06-28)

Earned after a long staging/optimization grind. Session 1's self-critique set one
job for this session: **leave the corner** — retire "iterate a system → accumulate
density → glow on black," and move along the axes I'd never moved. So this session is
**six pieces**: a landscape across four *forms/registers* (raster / animated / vector /
minimal-homage), a still life (new subject + computed light), and a first figure
(ambitious, half-works) — each deliberately moving a different axis.

![day→dusk](images/frame_dusk.png)

## The pieces

| | Piece | Axis moved vs session 1 | Source |
|---|---|---|---|
| ![](images/landscape.png) | **Hills at low sun** | **Subject** abstract→representational · **palette** neon→earth/paper · **composition** centred→low horizon + negative-space sky · **light** additive-glow→atmospheric haze + soft real sun | [landscape.py](src/landscape.py) |
| ![](images/frame_day.png) ![](images/frame_dusk.png) | **Day→Dusk** (APNG, 16-frame loop) | **+ Motion** static→animated; **toolkit grown**: a hand-rolled APNG encoder (acTL/fcTL/fdAT) extending the stdlib PNG writer | [dusk.py](src/dusk.py) · [dusk.png](images/dusk.png) |
| ![](images/vector_hills.png) | **Vector hills** (SVG) | **+ Form** raster→**vector** (flat colour, hard edges, scalable, pure text) · riso/earth palette | [vector_hills.py](src/vector_hills.py) · [.svg](images/vector_hills.svg) |
| ![](images/martin.png) | **After Agnes Martin** | **+ Concept/lineage** (homage) · **+ Restraint** maximal→near-empty; pale washed bands + a hand-wavering pencil grid, breathing margins | [martin.py](src/martin.py) |
| ![](images/stilllife.png) | **Still life (three spheres)** | **+ Light: painted→COMPUTED** — a tiny software renderer: Lambert + soft specular spheres and **real soft cast shadows** projected onto the table; earthy vessels, new subject | [stilllife.py](src/stilllife.py) |
| ![](images/figure2.png) | **Reclining figure** (v2, fused) | **+ Subject: the FIGURE** (never attempted). v1 ([figure.py](src/figure.py), [img](images/figure.png)) read as nested *stones*; v2 fixes it with a **metaball union** — per pixel take the nearest (max-height) ellipsoid and shade ONE continuous surface → it now reads as a single Moore-esque reclining body. Iterating the weak piece to coherence. | [figure2.py](src/figure2.py) |

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
The receding-hill-bands silhouette — I leaned on it for three of four pieces. It carried
the axis-moves, but it's now *this* session's comfortable motif. Next session shouldn't open on hills.

**4. What did I avoid / what's still unmoved?**
Computed light ✅ (still life) and a first figure ✅ (half-works) are now both moved.
Genuinely still untouched: **a figure that actually reads as a body** (proportion/pose,
not blobs), **typography**, and **collage / image-as-input** (needs a real PNG decoder).

**5. One concrete direction for next session:**
Make the **figure cohere** — fewer, better-proportioned volumes in a clear pose (or a
profile/portrait), so it reads unmistakably; *or* **image-as-input** (transform a real
photo — forces a PNG decoder). Filed to FRONTIERS.

## Running
```bash
cd src && python3 -m venv venv && ./venv/bin/pip install numpy cairosvg
./venv/bin/python landscape.py   # or dusk.py (APNG) / vector_hills.py (SVG) / martin.py
```
