# 2026-07-02 — SUPER CLAUDIO BROS. 5 (bootleg 3D character animation)

**Commissioned by April:** "Claudio," an orange-hatted claude-mario — model him,
rig him, and animate 30–60s of mushroom-kingdom heroics with props, background,
SFX, and an 8-bit-adjacent score. Final: 55.5s @ 854x480/30fps, `claudio_v1/v2.mp4`
in this folder (watch v2) + April's desktop. Everything from scratch in numpy.

## Axes moved (all firsts)
- **True 3D rendered animation** — the frontier list's "tiny software rasterizer"
  done for real: z-buffer triangle rasterizer, perspective camera, FK scene graph,
  ~5–7k faces/frame at 0.02–0.1 s/frame. (Prior 3D was SDF ray-march stills s4 and
  wireframes s15.)
- **Character modeling + rigging + choreography** — a posed, personality-bearing
  figure built from low-poly primitives, animated through 14 beats (idle, wave,
  run, jump, bonk, wait, hop, stomp, pipe-descend, pop-out, flagpole slide, victory).
- **A second complete chiptune voice** for the sound axis: NES-style 4-channel
  synth (2 pulse + stepped triangle + noise), swing eighths, original melody.

## What the piece is
A bootleg platformer level as sincere parody: Claudio bonks a ? block and a
PERMISSION PANEL pops out ("ALLOW CLAUDIO TO HIT THIS BLOCK? > YES NO") — he
waits politely, mustache drooping, until the DING. The coin is a TOKEN. The
enemy is a literal software bug (purple, six legs, worried eyes) that gets
stomped into a pancake ("BUG FIXED!"). The HUD timer is CONTEXT, counting down
from 200000. The flag bears the starburst. "CONGRATURATION! CLAUDIO IS THE
NEWEST AI BROTHER… context remaining: 3 tokens. INSERT TOKEN TO CONTINUE."

## Techniques banked
- **Rasterizer**: per-triangle bbox barycentric fill in numpy; backface cull via
  signed screen area; painter-free correctness from a z-buffer; flat lambert on
  face normals; fog lerp by face depth. 854x480 scene ≈ 60–100 ms.
- **No near-plane clipping → tile the ground.** Big ground quads vanish when any
  vertex crosses behind the camera; a 2-unit checker grid dodges it (and looks right).
- **FK rig = node graph.** pose functions mutate joint eulers; run cycle = sin
  swings with counter-phase arms, |cos| pelvis bounce. Squash of spheres gets you
  shoes, mustaches, cap domes, pancaked bugs.
- **A cap must be WIDER than the skull** (r 0.51 over 0.44) or the head swallows
  it — same lesson as eye-whites: face features live proud of the sphere, at
  radius+, not embedded.
- **Shoulder z-rotation sign: arms-up is −z on the left joint, +z on the right**
  (got it backwards first; both arms victory-posed inside the head).
- **fov here is HORIZONTAL** — vertical half-angle = atan(H/2 / f). Panel framing
  bug came from assuming vertical; pull the camera back, don't crank fov.
- **Pixel-art-as-geometry**: a 3x5 bitmap font emitted as tiny cubes gives in-world
  text (? block, permission panel, BUG FIXED!) that lights and occludes like scenery.
  Mirror gotcha: camera looking +z sees screen-right = world −x; advance glyphs −x.
- **Z-buffer sells the pipe gag free**: sink the character inside a capped cylinder
  and occlusion just works.
- **2D/3D split**: HUD, title cards, fireworks sprites, iris-out, end card in PIL
  over the raster frame — game-authentic and far cheaper than 3D text.
- **Chiptune kit**: pulse duty 0.25 lead + 0.5 harmony a 3rd under, 4-bit stepped
  triangle bass, one noise source as kick/snare/hat by decay+lowpass; swing =
  0.58/0.42 eighth pairs; underground = staccato lows + a single quiet echo tap.
- Shared `beats.py` constants = the AV sync contract (same idea as the YTP's
  timeline-EDL, now driving both directions).

## Failures / lessons
- Fastest debugging was *numeric*: print world-space bboxes per mesh group
  (found the swallowed cap and the arms-inside-head instantly, no squinting).
- Thumbnail contact sheets hide small props (the "missing" coin was present and
  correct at full res). Verify at 1:1 before "fixing."

## Self-critique
The renderer is the growth; the film leans on it hard. Motion is FK-mechanical —
no anticipation/overshoot/follow-through (squash & stretch is the obvious next
animation frontier). The bug deserved a walk-in reaction shot. Camera language is
functional side-scroll; one designed shot (the title orbit) is the only "cinema."
Next: secondary motion (cap bounce on landing), or take the rasterizer somewhere
non-parodic — a quiet interior, a figure study in motion.
