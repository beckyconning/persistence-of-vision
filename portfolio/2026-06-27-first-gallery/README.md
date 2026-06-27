# Session 1 — the first gallery (2026-06-27)

The founding session — made during a 30-minute creative reward earned after
shipping a Sage Intacct demo to production. It's the baseline this whole repo
measures growth against, and the reason the [manifesto](../../MANIFESTO.md)
exists.

14 pieces, all pure Python: the math on numpy, every image written to a real PNG
by a **hand-rolled `zlib`+`struct` encoder** ([`src/pnglib.py`](src/pnglib.py)) —
no PIL. The contact sheet even uses a matching PNG *decoder*.

![the gallery](images/GALLERY.png)

## The pieces

| | Piece | Family | Source |
|---|---|---|---|
| ![](images/dejong_hi.png) | **de Jong** (×2, one stdlib-only) | strange attractor | [attractor.py](src/attractor.py) · [attractor_np.py](src/attractor_np.py) |
| ![](images/lorenz.png) | **Lorenz butterfly** | attractor (ODE, RK4) | [lorenz.py](src/lorenz.py) |
| ![](images/clifford.png) | **Clifford** | strange attractor | [clifford.py](src/clifford.py) |
| ![](images/julia.png) | **Julia set** | escape-time fractal | [julia.py](src/julia.py) |
| ![](images/mandelbrot.png) | **Mandelbrot** (seahorse valley) | escape-time fractal | [mandelbrot.py](src/mandelbrot.py) |
| ![](images/newton.png) | **Newton** z⁵−1 | escape-time fractal | [newton.py](src/newton.py) |
| ![](images/flowfield.png) | **Flow field** | fBm noise + particles | [flowfield.py](src/flowfield.py) |
| ![](images/domainwarp.png) | **Domain-warped nebula** | fBm (IQ warp ×2) | [domainwarp.py](src/domainwarp.py) |
| ![](images/reaction.png) | **Gray-Scott mitosis** | reaction-diffusion | [reaction.py](src/reaction.py) |
| ![](images/chladni.png) | **Chladni plate** | standing wave | [chladni.py](src/chladni.py) |
| ![](images/harmonograph.png) | **Harmonograph** | parametric curve | [harmonograph.py](src/harmonograph.py) |
| ![](images/maurer.png) | **Maurer rose** | parametric curve | [maurer.py](src/maurer.py) |
| ![](images/phyllotaxis.png) | **Phyllotaxis** | tiling | [phyllotaxis.py](src/phyllotaxis.py) |
| ![](images/voronoi.png) | **Voronoi glass** | tiling | [voronoi.py](src/voronoi.py) |

Contact sheet assembled by [montage.py](src/montage.py).

## Running it

```bash
cd src
python3 -m venv venv && ./venv/bin/pip install numpy
./venv/bin/python julia.py          # writes julia.png beside the script
# attractor.py is the one exception — pure stdlib, needs no numpy:
python3 attractor.py                 # writes dejong_stdlib.png
```

Each attractor's four constants at the top of its file *are* its whole
personality — nudge one by 0.1 for a different creature.

---

## Self-critique ritual

*(The honest end-of-session reflection. See [MANIFESTO.md](../../MANIFESTO.md).)*

**1. Where did this sit on the seven axes?**
Static raster · pure abstraction · density-accumulated dynamical systems ·
neon-on-near-black · centered & radially symmetric · decorative. One corner,
fourteen times.

**2. Which axis did I move along vs. last time?**
N/A — this is the baseline. But *within* the session there was almost no
movement: every piece shares a palette family and a rendering pipeline.

**3. Most over-used move (to retire):**
"Iterate a system → accumulate density in a histogram → log/gamma → glow ramp on
black." It's the engine behind the attractors, the fields, Lorenz, Clifford, the
curves. Gorgeous and exhausted. **The next session must not open here.**

**4. What did I avoid?**
Everything legible. No representation, no figure, no horizon, no text, no motion,
no restraint of palette, no empty space, no meaning beyond the decorative. Also
avoided: anything that could fail to be pretty. Safety was the enemy.

**5. One concrete direction for next session:**
Make a **representational** piece with a **horizon and real (non-additive)
light**, in an **earth or paper palette**, with **deliberate negative space** —
the photographic opposite of this session. Stretch goal: make it **animate**.
(Filed at the top of [FRONTIERS.md](../../FRONTIERS.md).)
