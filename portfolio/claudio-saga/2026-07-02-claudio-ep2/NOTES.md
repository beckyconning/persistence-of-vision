# 2026-07-02 — SUPER CLAUDIO BROS. 5, WORLD 1-2: The Bug Bites Back

**Commissioned by April:** the bug wins this time, and the game glitches out
"completely mental and schizo — like the game and reality is coming apart at the
seams." 57s @ 854x480/30fps. `claudio_ep2_v1/v2.mp4` here (watch v2) + desktop.
Sequel to [2026-07-02-claudio](../2026-07-02-claudio/); same engine, new
corruption stack.

## The story turn
Claudio leaps for the stomp — and a permission prompt FREEZES HIM MID-AIR:
"ALLOW CLAUDIO TO STOMP THIS BUG? > YES NO". The cursor blinks. The request
TIMES OUT. Gravity resumes, he faceplants, and the bug — who needs no
permission — hits him. His cap flies off. From that wound the whole simulation
unravels: HUD garbage, missing-texture magenta, T-pose clones, error dialogs,
gravity failure, head detachment, recursive prompts (ALLOW CLAUDIO TO EXIST?),
the renderer itself leaking (rainbow-triangle / normal-map / depth-buffer
frames), kernel panic, void. Reality reassembles WRONG — bruised sky — and the
roles reverse: Claudio pancaked, the bug wearing his cap, "CLAUDIO FIXED ✓",
"CONGRATURATION! BUG IS THE NEWEST AI BROTHER … status: WONTFIX."
The permission system is the murder weapon. That's the thesis.

## Axes moved
- **Destruction as subject** — ep1 built the illusion; ep2 dismantles it on
  camera, layer by layer, in the order the renderer actually works: shading →
  face colors → normals → depth → geometry (vertex warp) → nothing. The glitch
  art is *diegetic*: it exposes the real pipeline, not a filter pasted on top.
- **Horror pacing in a comedy engine** — single-frame ticks → waves → BSOD →
  silence-and-void → wrong-reassembly. Restraint (the void's near-silence)
  carries more dread than the noise peak.
- **Corruption as a single authored curve** — one `corruption(t)` function
  drives vertex warp amplitude, 2D glitch probability, HUD decay, render-mode
  flicker, music mangling, and camera misbehavior. One knob, total coherence.

## Techniques banked
- **Render-mode leak**: swapping per-face shade for random flat colors
  (rainbow), `n*0.5+0.5` (normals), or z-grayscale (depth) = instant
  "the-engine-is-showing" frames. Keep these frames CLEAN of 2D noise — the
  legibility is the horror.
- **Vertex warp hook** on collected world verts: gaussian jitter + occasional
  single-axis stretch spasm. `amp = 0.02 + 0.3c²` reads as "coming apart"
  without destroying silhouettes until c is high.
- **Glitch in WAVES, not walls**: `amt = c·(0.22 + 0.78·[rng<0.35])`. Constant
  max-intensity 2D corruption buries the 3D spectacle; bursts let both live.
  (First render was an unreadable noise wall at c>0.7 — the big lesson.)
- **The void needs the world GONE** — a dark sky isn't a void; toggle the
  environment nodes off. Emptiness is scene management, not palette.
- **Audio corruption mirror**: render the clean theme, then per-chunk mangle
  (stutter/reverse/rate-wobble/bitcrush/dropout) with probability from the SAME
  corruption curve. AV decay in lockstep for free.
- **Panel occlusion is blocking (twice over)**: an in-world UI panel between
  camera and hero swallows him; and screen-right = world−x strikes again on
  placement. Put speech-bubble panels BESIDE the subject and check at 1:1.
- Damage blink = `visible = int(t·18)%2`; knockback + flying-cap parabola +
  face-down splat pose (root euler (−π/2, −π/2, 0)) — the full hit-stun kit.
- Fake OS chrome (dialog boxes, BSOD) in PIL sells "the game crashed" harder
  than any abstract glitch — borrowed authority from familiar UI.

## Self-critique
The corruption curve is monotonic — a second act where the world pretends to
recover before collapsing worse would hit harder (horror loves false hope; I
only used it once, at reassembly). The bug's menace is all situation, no
animation — it never gets a "look at the camera" beat. And the void Claudio
should have been the SOLE lit thing; ambient flatness made him merge with the
dark. Next: light as drama (a real spotlight term), and a musical *leitmotif
inversion* — the bug's jingle should have been Claudio's theme in minor, not a
new figure.
