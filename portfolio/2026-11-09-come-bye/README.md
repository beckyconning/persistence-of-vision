# Come Bye (2026-11-09)

April asked to be entertained, with full freedom. The answer was a playable sheepdog trial:
https://claude.ai/artifact/9c98BKpFTb8gjLHW7kZrFJ (source: `come-bye.html`, also on her Desktop).

Five Lonk ewes (the Rossendale breed, black faces, curled horns, a red smit mark on the shoulder,
one with a blue raddle spot and opinions) at the top of a walled Pennine field at Cribden Side.
You never steer the dog. You whistle four real commands (come bye, away to me, walk up, lie down)
and she holds the last one until told otherwise. Outrun, lift, fetch gates, drive, cross-drive,
pen, scored on a judge's card out of 90, placed against a field of 30 invented handlers from
Bacup and Waterfoot, with a dry PA commentator throughout. Synthesised whistles, ewes, wind and a curlew.

## What was new

- **A game in daylight, hard-edge flat colour.** The FRONTIERS ask since s22/s23: no glow, no dark
  ground. Flat fills, one fixed light direction (every shadow is a darker flat shape offset to the
  south-east, cloud shadows as one union path so overlaps never double), hurdles and dry stone
  coping drawn as plain rectangles.
- **Depth that emerges from simulation.** The other s22/s23 door. The sheep are boids with a flight
  zone, fear that spreads between neighbours and decays, and one stubborn ewe with a smaller flight
  zone and weaker cohesion. Nothing is choreographed; every split, wall-hug and bolt at the pen
  comes out of the rules.
- **Indirect control as the game.** The player commands an agent with instincts: a natural outrun,
  a balance point opposite the handler on the fetch only (so driving away is harder, as in life),
  and covering (a stray gets fetched back before she walks on).
- **Headless playtest as design tool.** An autopilot (the demo, "last year's winner") and a sloppy
  scripted human with 0.4 to 0.8 s reactions both ran 16+ full trials per change. The sloppy player
  found the two real design bugs: flanks too fast for human reaction near the sheep, and walk-up
  aimed at the flock's centre splitting a strung-out flock. Both fixed in the dog, not the player.

## Self-critique

1. **Axes:** form (an interactive game, top-down flat vector), palette (daylight, earth and grass,
   one red), method (simulation-emergent), concept (a place and a sport, with a voice).
2. **Moved along:** palette and method. First game that is not dark-ground-plus-glow, and first
   whose difficulty is not placed by hand.
3. **Most over-used move now:** the hidden personal reference (Cribden Side is April's family's
   hillside; nobody else will see it). Fine once, but it is becoming the default way to make a
   piece "mean" something.
4. **Avoided:** the ear. Every sound is synthesised blind and nobody has heard it yet. Also avoided
   any perspective view; it is all straight down.
5. **Next:** the same field seen from the wall at eye level (an oblique, painterly view of the run as
   a replay), or a game where sound is the primary channel and has had an ear test before shipping.
