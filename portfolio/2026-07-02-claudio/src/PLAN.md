# SUPER CLAUDIO BROS. 5 — "The Newest AI Brother"
### a bootleg 3D short, ~55s @ 854x480 30fps

**Aesthetic:** flat-shaded low-poly (PS1 bootleg), warm Claude palette on a
mushroom-kingdom hillside. Everything hand-rolled: numpy triangle rasterizer
with z-buffer, FK-rigged character, pixel-art-as-quads for in-world text,
PIL HUD overlays, chiptune score loosely in the register of a certain 1985
plumbing simulator (original melody — bootleg, not stolen).

**Claudio:** round low-poly hero. Coral-orange cap (starburst emblem, not an M),
cream shirt, warm-brown overalls, white gloves, big nose, magnificent dark
mustache. Rig: root → pelvis → torso → head(+cap+nose+stache+eyes),
shoulders → arms, hips → legs. Enough for run/jump/wave/stomp/victory.

## Beat timeline (seconds — shared constants in beats.py)
- 0.0–6.0   TITLE: slow orbit around idle Claudio on a hill; he waves.
            Cards: "SUPER CLAUDIO BROS. 5" / "THE NEWEST AI BROTHER"
- 6.0–7.0   Cut to side-scroll framing. HUD on: CLAUDIO / TOKENS / WORLD 1-1 / CONTEXT 200000 (counts down)
- 7.0–13.0  Run right to the ? block.
- 13.0–15.0 Jump, bonk block (block bounces). Permission panel pops out above:
            "ALLOW CLAUDIO TO HIT THIS BLOCK? > YES  NO"
- 15.0–19.5 He waits politely. Mustache droops slightly. At 18.5: DING — YES.
- 19.5–22.5 Coin pops + spins; TOKENS +1. Victory hop.
- 22.5–30.0 A BUG (purple software bug, six legs, walks in from right).
            Claudio runs, jumps, STOMPS at ~28.2. Bug flattens; "BUG FIXED ✓".
- 30.0–36.0 Camera pans; Claudio runs to the warp pipe, hops on, descends in
            (warp sound). Screen dark beat.
- 36.0–38.0 Pops out of the pipe by the flagpole.
- 38.0–44.0 Runs, leaps to the flagpole at ~42.2, slides down. Flag = starburst.
- 44.0–50.0 Fireworks ×3, "TASK COMPLETE", victory pose, slow zoom.
- 50.0–55.0 Iris-out → end card: "CONGRATURATION!" / "CLAUDIO IS NEWEST AI BROTHER" /
            "thank you for playing. context remaining: 3 tokens"

## Files
- beats.py — timeline constants shared by animation + audio
- engine.py — rasterizer: Node graph, camera, z-buffer, flat lambert
- claudio.py — character mesh + rig + pose helpers
- world.py — ground/hills/clouds/blocks/pipe/flag/bug/coin/panel + pixel-font quads
- animate.py — per-frame scene state → frames → ffmpeg pipe + PIL HUD
- chiptune.py — square/triangle/noise synth, the score, all SFX
- build_audio.py — mix score + SFX at beat times (reuses ytp Timeline)
- Output: out/claudio_v1.mp4 → desktop + persistence-of-vision portfolio

## Sound plan
Music (one continuous piece): title fanfare → bouncy overworld theme (swing
8ths, square lead + pulse thirds, triangle walking bass, noise drums) →
underground minor breakdown during the pipe → theme reprise → flag fanfare →
end jingle. SMB *register*, original tune.
SFX: jump sweep, block bump, permission ding, coin, stomp squish, warp gliss,
flag slide arpeggio, firework booms+sparkles, HUD tick.
