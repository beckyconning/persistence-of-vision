# 2026-07-03 — SUPER CLAUDIO 64 (a full playable video game)

**Commissioned by April:** a bootleg Mario 64 — N64 aesthetics, Mario's moveset,
castle lobby, paintings into 5+ unique levels, stars, a boss battle, soundtrack
and SFX. Delivered: `claudio64.html` — a single self-contained 669KB file
(double-click, press Enter). Copy on April's desktop as `SUPER_CLAUDIO_64.html`.

## The game
- **Castle Claudio lobby**: checkered floor, red carpet, five living paintings,
  a star-gated boss door (6★), and one secret lobby star on a ledge.
- **Five worlds** (2 stars each + lobby secret + grand star = 12):
  TOKEN MEADOWS (rolling gaussian hills, a mountain spiral, patrolling bugs),
  COMPACTION CORE (lava sea, moving platforms, ground-poundable crates),
  FROZEN CACHE (slippery frozen lake, ice-pillar climb, a token slide),
  CONTEXT WINDOW (floating cloud platforms, wind zones, a moving cloud ride),
  LEGACY CODEBASE (haunted bookshelf maze, candlelight, and a GHOST BUG that
  only moves when the camera isn't looking at it).
- **Moveset**: run, jump → double → triple (timed chain), long jump
  (shift+space at speed), ground pound (C mid-air, breaks crates and bosses),
  coyote time, ride-along moving platforms, ice friction, wind forces, lava
  bounce, Q/E orbit camera with zoom.
- **Boss: SUPER GROKIO** — walks, lobs fireballs, telegraphs, CHARGES; crashes
  into the arena rim, gets stunned; ground pound him ×3 → he pinwheels away and
  the GRAND STAR spawns. CONGRATURATION.
- **Soundtrack**: 8 procedural WebAudio chiptune loops (dreamy lobby waltz,
  bouncy overworld, lava ostinato, ice music box, 6/8 sky arps, haunted organ,
  phrygian boss drive, victory) + ~20 synthesized SFX (triple-jump arpeggio,
  star fanfare, permission-style denials). No audio files — all oscillators.
- **N64 look**: 480×360 internal render CSS-upscaled with `image-rendering:
  pixelated`, 4:3, per-level fog + vertex-colored sky domes, MeshLambert
  gouraud, and every texture painted procedurally on 32×32 canvases with
  NearestFilter (grass/lava/ice/books/brick/carpet + the five painting arts).
- Stars persist in localStorage.

## Engineering shape (single HTML, zero dependencies at runtime)
Three.js r128 UMD embedded + 8 concatenated source chunks: audio tracker,
input/physics/camera, characters (Claudio/Grokio/bugs/star/token builders),
canvas textures, levels ×2, songs, game state machine. Physics is classic
platformer: capsule vs AABB/cylinder push-out + "highest support below feet"
ground resolution + analytic gaussian terrain — no physics engine.

## The QA breakthrough: headless playwright playtesting
Chromium's SwiftShader renders WebGL headless. Scripted playtests:
- screenshot sweep of title + lobby + all 6 worlds (caught the lobby camera
  spawning inside a wall);
- functional pass: walk into painting → warp; grab star → STAR GET → lobby;
  denied painting bounces; boss AI reaches stun (caught paintings hung above
  the reachable trigger — a cascade that then broke the star test: headless
  playtests fail like real players, in sequences);
- full scripted BOSS KILL: three stun-pound rounds → dying → grand star →
  victory state. Zero console errors across all runs.
An agent that cannot play the game can still PLAYTEST the game — that's the
banked lesson, and it's the difference between shipping code and shipping a game.

## Self-critique
It's a real game — but the movement lacks SM64's soul polish (no wall kick, no
dive, no momentum-preserving slope physics). Levels are one-idea-each; a great
level braids three. The ghost bug is the best design in it (borrowed authority:
Boo rules teach themselves). Music loops are 8-16 bars — real N64 tracks
develop. If April plays it and wants WORLD 2, the engine is ready.
