# Session 3 — the face (2026-06-28)

A short focused session (a redirect mid-grind: "iterate on persistence-of-vision").
One job: move the marquee axis the first two sessions never touched — **the
portrait / face** (FRONTIERS up-next #2; session 2's critique literally asked for
"a profile/portrait, so it reads unmistakably"). And do it by *extending* technique,
not repeating one.

![portrait](images/portrait.png)

## The piece

| | Piece | Axis moved | Technique | Source |
|---|---|---|---|---|
| ![](images/portrait.png) | **Bas-relief head** | **+ Subject: the FACE/PORTRAIT** (never attempted) | **Relief sculpting**: a height field `z(x,y)` composed from facial structures (dome → brow → nose ridge/bulb/alae → eye sockets + eyeballs → cheeks → a single lip-mass split by one groove → chin, with a jaw taper), then **normals from the height gradient** (`np.gradient`) → Lambert + soft specular + fill under one key light. Skin albedo with a darker iris, redder lips, and eye **catchlights** — the cue that sells a face. | [portrait.py](src/portrait.py) |

It reads unmistakably as a face — a solemn, archaic mask (Brâncuși / Modigliani
register). That was the whole bar, and it's met on the hardest subject.

## How it got there (iterate-to-coherence)

Same discipline as session 2's figure: render → find the lie → fix → repeat.
1. **v1** — read as a face immediately, but the mouth was two stacked sausages and
   the nostrils were melty blobs.
2. **v2** — softened/widened the nose; pulled the lips together. Mouth *still*
   doubled (modelling upper + lower as two separate mounds guarantees a gap).
3. **v3** — the real fix: model the mouth as **one** lip swell split by a **single**
   thin groove (lips meet at a line and connect at the corners, like a real mouth),
   and widen the chin so no bright sulcus band fakes a second mouth.

## Self-critique ritual

**1. Which axis moved?** Subject → **the face**, the last marquee axis untouched
across sessions 1–2. Technique grew too: from "computed light on *given* volumes"
(still life / figure) to **sculpting the volume itself** as a relief height field.

**2. What works:** it reads as a face without a caption; the eyes (socket recess +
raised eyeball + dark iris + catchlight) and the unified mouth are the load-bearing
wins; the gradient-normal relief gives believable soft form and sheen.

**3. What's still weak (for next time):** it's **frontal, symmetric, and mask-stiff**
— no individuality, no hair, no neck, dead-on gaze. A faint highlight band still
lingers under the lip. The relief is shallow (a coin/medallion, not a full head).

**4. Most over-used move to retire:** the **centred, perfectly-symmetric subject on a
dark vignette** — sessions 1 and 3 both lean on it. Next face should be a **3/4 or
profile**, asymmetric, with an expression — or break symmetry with hair/lighting.

**5. One concrete direction next:** a **profile or 3/4 head** (asymmetry forces real
structure), *or* the other still-untouched axis — **image-as-input / collage**
(transform a real photo; exercises a full PNG decoder). Both filed to FRONTIERS.

## Running
```bash
cd src && python3 -m venv venv && ./venv/bin/pip install numpy
./venv/bin/python portrait.py   # writes portrait.png
```
