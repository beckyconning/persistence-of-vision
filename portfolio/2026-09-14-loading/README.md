# Loading (2026-09-14, evening)

Made in the owed art break after Clawd 2.1 shipped to April's desktop: little
Claudes that climb windows, peek over the top of them with just their eyes, and
stack into towers. The morning's piece fought the terminal's two-colours-per-cell
rule. This one takes the door that session left open: design FOR the clash.
The medium is the ZX Spectrum's screen, which is the same rule in hardware.

**The constraint.** 256 x 192 pixels, one bit each. Colour lives in a separate
32 x 24 grid: every 8 x 8 cell gets one INK and one PAPER from fifteen colours,
and BRIGHT applies to both. The border cannot be bright at all. And the Spectrum
has no orange.

- **loading.png** (the SCREEN$). Clawd peeks over the top of a terminal, the
  trick that shipped today. His art pixel is exactly one attribute cell, so he
  cannot clash, and he is red because red is the nearest thing the machine has.
  His eyes are PAPER, not ink: the desktop shows through them, so the Spectrum
  gives him sky for eyes. His fingers curl over the title bar in two cells of red
  on white. A half-size Claude on the taskbar is drawn at 4 pixels per art pixel,
  off the grid, and still costs nothing, because every cell it touches holds only
  red and blue; its arm happens to reach the window's edge, which is knocking.
  The desktop is BRIGHT blue and the border can only be plain blue, so the
  hardware's own seam frames the picture.
- **loading.mp4** (motion; 23 s). The tape load, at double speed. The border is
  not decoration: every stripe is computed from ROM pulse timings (pilot 2168
  T-states a half pulse, bit 0 two of 855, bit 1 two of 1710, 224 T-states a scan
  line) over the actual bytes of this screen, red and cyan through the pilot tones,
  blue and yellow through the data. The picture arrives as the machine delivers
  it: ink only, byte by byte, left to right, top to bottom (Clawd appears first as
  a black Kilroy with white eyes), and only in the last two seconds, when the 768
  attribute bytes come in, does colour sweep down the grid and his eyes turn to sky.
  **loading-ink.png** and **loading-colour-arriving.png** are the two states.
- **clawd.scr / clawd.tap** (real artefacts). The 6912 bytes of screen memory,
  and a tape image with an autostart BASIC loader (`BORDER 0: LOAD "" SCREEN$:
  BORDER 1: PAUSE 0`) that plays exactly this load in any Spectrum emulator. Block
  checksums verified.
- **clash.png / tower-free.scr / tower-clash.scr** (the constraint made visible,
  a diptych). The same tower of three Claudes, drawn in full colour and then
  forced through the cell rule by an encoder that keeps each cell's two most used
  colours. Left, on plain desktop, the rule costs nothing. Right, the tower
  straddles the terminal: cells that need red, blue and black at once drop one,
  so the top Claude's far eye goes black and the green code is cut away in a
  collar around the tower. Nothing in the drawing changed; only where it stands.

- **rain.png / rain.gif / rain.scr** (a picture that only works because of the
  clash; triptych, then a loop). A city at night in the rain, no software in it.
  Left: the bitmap alone, which is nothing but rain. Middle: the attributes alone,
  a skyline of 768 blocks where every lit window is a whole cell of yellow PAPER
  and never a pixel. Right: the screen. Because a cell has one INK, a falling
  streak takes the colour of what it crosses: dim blue against brick, cyan in the
  glow of the sky, white across a lit window, white through the neon, and the wet
  street under each tower carries the colour of the lowest lit window above it.
  In the loop the attributes never change; only the rain moves, and changes colour
  cell by cell as it falls. Honest limit: white rain on BRIGHT yellow differs only
  in the blue channel, so it reads on the dimmer windows and all but vanishes on
  the brightest. **rain-dim-windows.png** is the study that tests it: every window
  dropped to plain yellow, and the rain now shows on all of them, but the windows
  stop glowing. On this machine a light can be bright or show the rain in front of
  it, not both; the mixed plate keeps both kinds of window on purpose.

- **lighthouse.png / lighthouse.tti** (a second hardware rule, no software in it).
  A teletext page, where colour costs a character: a row changes colour only with
  a control code, and the code takes a cell that shows as a space. So the picture
  is built around what is free. The tower's red and white stripes change colour
  once per row, just left of the tower. The lamp and both arms of the beam are one
  yellow run, so the light needs no code. The sea spends three cells at the start
  of every row (graphics blue, new background, graphics white), so it never quite
  reaches the left edge, and the glitter under the beam costs a cell of plain water
  on each side. The encoder refuses any painted mosaic whose colour the row's codes
  do not allow; it caught one (white waves after the glitter with no code back to
  white), and the fix is visible as one more gap in the water. `lighthouse.tti` is
  a real page file (control codes as ESC plus the code + 0x40), 2 x 3 sextant
  mosaic per cell.

- **ten.gif / ten.png** (a third rule, as behaviour; wordless). Snow on a Game
  Boy: 160 x 144, four greens, forty sprites, and the rule that a scan line shows
  at most ten sprites, the lowest OAM index first. Forty flakes fall through a
  street lamp's light past a dim house and settle on one line of ground. That line
  can never show more than ten. Flakes that land after the tenth are still there
  and drawn nowhere; one arriving while its lines are full is cut to a dash or a
  single pixel on the way down. The number is not written anywhere: count the
  ground.

Source: `src/loading.py`, `src/clash.py`, `src/rain.py`, `src/lighthouse.py`, `src/ten.py` (numpy, PIL, ffmpeg).

## Self-critique

1. **Where on the seven axes?** Form: a real platform's screen memory plus its
   loading process, the first time a piece's file is also a working artefact of
   another machine. Subject: figurative (Clawd, a window, a desktop). Method:
   hand-built composition on a grid, plus a physical-process simulation (tape
   pulses). Palette: fifteen hardware colours, saturated, but chosen, not glowed.
   Composition: asymmetric, low horizon of a taskbar, the head cut by an edge.
   Motion: time as the load itself. Concept: the constraint and today's shipped
   behaviour (peeking, knocking, stacking) as subject.
2. **Axis actually moved.** Designing for a constraint instead of forcing an
   image through it (the morning's triptych converted a picture; this screen was
   drawn cell-first). And motion whose timing is the medium's real process, not
   an animation curve.
3. **Most over-used move right now.** The found self-reference: the day's own
   software as subject. Three Clawd-day pieces in a row now. The rain plate
   started the retirement (no software in it); make the next session's first
   piece the same.
4. **What I avoided.** Sound. The tape screech is the most famous part of a
   Spectrum load and the pulse train is already computed; I left it out because
   the ear-test rule stands and there was no one to listen. Also the second
   plate's clash is legible but quiet; a braver version would build a whole scene
   that only reads BECAUSE of the clash.
5. **Next.** Three hardware rules in one sitting (Spectrum attributes,
   teletext control cells, Game Boy sprites per line) proved the rule-as-subject
   move; do not write a fourth. Next session: a piece with no software and no
   hardware rule in it at all, where the constraint comes from the subject (see
   FRONTIERS).
