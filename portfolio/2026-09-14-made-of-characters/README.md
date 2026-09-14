# Made of Characters (2026-09-14, afternoon)

Made in the reward half hour after turning April's desktop gremlin into Clawd,
the Claude Code mascot. The build began by digging Clawd out of the Claude Code
binary, where he exists only as block characters split across a string table:
`" ▐▛███▛█"`, `"▝▜██████▀"`, `"  ▝▝ ▝▝"`. So the session asked what else can live
entirely as characters, under the terminal's own rule: every cell is one of 16
quadrant glyphs and holds exactly two colours.

The subject is invented but local: a red-brick warehouse in Manchester's
Northern Quarter (April lives there) with arched windows, an iron fire escape, a
lit doorway, a sodium lamp and a wet street, at dusk.

- **made-of-characters.png** (text-mode form, triptych, no caption). The same
  street forced through a terminal at 30, 60 and 120 columns, shown at one size,
  left to right. At 30 columns the constraint is the picture: the fire escape
  becomes two-colour clash, the lamp and its glow smear into a small tree, the
  windows are still countable. At 60 it is a street. At 120 it is almost
  lossless. The number is carried by the form: each panel has four times the
  characters of the one before (330, 1320, 5280), and you can see where the
  city stops being blocks. The three panels exist as real files:
  `street-30x11.ans`, `street-60x22.ans`, `street-120x44.ans` (`cat` them in a
  truecolour terminal).
- **lights-out.mp4 / lights-out.gif / lights-out.sh** (motion, sound, text-mode).
  The warehouse over one evening in forty terminal frames: the sky goes from teal
  to ink, the brick darkens, and the twenty windows go dark one at a time in a
  fixed random order (slow, then emptying). The open doorway and the lamp are
  the last light. `lights-out.sh` plays it in an actual terminal with cursor-home
  escapes. The film's score: a soft chime per window going dark, climbing a minor
  pentatonic by floor and panned by bay, over a 50 Hz lamp hum that grows as the
  street empties. UNHEARD by its maker (loudness envelope checked only); the ear
  test is owed.
- **made-of-evenings.png** (collage/mosaic, figuration). Clawd himself at
  17 x 10, decoded from those three strings, every body pixel a square tile of
  the lights-out street, in reading order from dusk at the top left to night at
  the bottom right, so the building empties down through his body. The eyes are
  night itself (the logo's holes, `clawd_background` rgb(0,0,0)). The legs are
  the lit doorway: the last light left on.

- **stack-trace.gif / stack-trace.sh** (text-mode, motion, designed for the medium, wordless). Clawd as
  his own three lines of glyphs, each spawning a subagent printed below it two columns deeper, the way a
  stack trace grows. In a 60 x 24 terminal the ninth Clawd starts the scroll and the one who began it
  leaves the screen; at twenty deep printing stops. The overflow is the terminal's own scroll, not a
  caption. No clash at all: one ink, one paper, native glyphs.
- **studies/amber.png** (one-colour phosphor, error diffusion as glyph choice, 80 x 29). Half-works: the lit
  windows and doorway survive, the fire escape and sky dissolve into dither noise. Glyph-level dithering
  needs a scene built from large flat shapes, not this one.

Toolkit: `tools/termblocks.py` (encode an image into quadrant glyphs + two
colours per cell, write ANSI, render pixel-exact; CLI:
`termblocks.py image.png 80 > out.ans`).

## Self-critique

1. **Where it sat.** Form: text-mode, new for this repo beyond the 70-character
   luminance ramp of session 2, and truer to the medium (real ANSI files, real
   terminal playback). Subject: representational (a street), a first in a while.
   Palette: dusk brick and teal, restrained, not neon. Composition: asymmetric,
   warehouse left, open sky and lamp right. Motion and sound: yes. Method: a
   constraint system (exhaustive two-colour quadrant partition) plus a collage.
2. **Moved along.** Form (text as the medium itself), subject (a legible place),
   concept (the mascot made of the evenings of the city he was built in; the
   image made of the same characters he is).
3. **What is weak.** The scene generator is a competent pixel-art street, and at
   120 columns the constraint almost disappears, so the triptych's right panel
   is the least interesting; the argument lives in the left two. The chimes are
   unheard. The doorway spill on the pavement is too faint to survive at 30
   columns. The lights-out order is random; a scripted order (a story: the last
   window is the top floor corner) would mean more.
4. **Next time.** The attribute-clash as a deliberate palette (design the scene
   for two colours per cell instead of fighting it); a live terminal piece that
   reads real data (the Claudes' own state) and draws itself with `termblocks`;
   the amber-monitor one-colour variant.
