# Rome, turn 1 (2026-10-26)

An ink map in the manner of a surveyor's sheet: the thirty-five tiles the
settler could see when game 3 of the Civ VI Deity campaign began, drawn from
the real map read (`get_map_area(73,11)`, radius 3). Rome was founded on the
forested grass hill by the river at (73,11). Civ 6 hexes are pointy-topped with
odd rows shifted half a hex east, and higher y is north, which puts the tundra
rows to the south and the desert to the north; the map says so and corrected my
own first reading of the board.

Made in the art break of the campaign, on April's rule that the piece be about
the task.

## Files

- `rome-turn-one.png`: the sheet, with a legend of signs and a compass.
- `rome.py`: the drawing. The tile table at the top is the read, verbatim.
- `the-view-from-the-hill.png`: the second piece, the same thirty-five tiles as
  a 360-degree view from Rome's hill (`view.py`): each tile at its bearing
  (north at the left edge, east a quarter along, south at the centre, west at
  three quarters) and at a depth by its ring, the nearest ring lowest and
  largest; hills as humps, the mountain as a peak, forests as rows of trees,
  water as wave bands. A landscape placed entirely by data. It still reads a
  little like three staves of music; the ridges would need to overlap more to
  read as one country.
- `turning-on-the-hill.gif`: the view as a loop, a 100-degree window turning
  once round the compass.
- `rome-in-block.png` and `rome-rising.gif`: the third projection (`block.py`),
  the tiles as hex prisms in an oblique view, hills raised, the mountain a
  peak, the sea sunk, the walls hachured, the near tiles overprinting the far;
  and the same block rising out of the flat plan over a second and holding.
- `three-projections.jpg`: the set on one sheet: plan, elevation all round,
  and block, all from one read.
- `the-column.png`: Trajan's own monument as the vessel for the campaign's
  story (`column.py`): a column elevation with twelve windings of frieze, one
  every twenty turns, the first carved with turn 1 (the mountain, the river,
  the founding on the hill, the warriors walking north, the sea) and the rest
  blank, labelled, waiting for the game; the first winding unrolled beside it;
  the statue base empty until the game is won. A new form here (architectural
  elevation as a narrative frame) and the piece the next breaks will add to.

## Signs

Hachures for hills (two bands of slanted strokes), outlined peaks with hachured
flanks for the mountain, tree marks (trunk and two canopy arcs) for forest,
light stipple for plains, dense for desert, dashes for tundra, clear paper for
grass, a fine horizontal band for floodplains, a double ribbon for a river tile
and waves for coast and sea. Resources are named where they lie: mercury, deer,
maize, wheat, gypsum, truffles. The city is a ring with a tower; the warrior a
figure with a spear.

The river sign names the tile, not the bank, because that is all the read
says: the game lists tiles that touch a river, not which edge. An honest map
draws what it knows.

## Self-critique

1. **Axes.** Form: cartography on paper, a conventional-sign system. Subject:
   the legible world, a real place in the game. Method: data to drawing, with a
   pen in pixel units (the studio's metre-scale pen was far too fine). Palette:
   paper, ink, one water blue. Composition: the sheet with its margin notes.
2. **What moved.** The map as a found composition: the shape of the thirty-five
   hexes is the game's, not mine, and the sign system had to serve legibility
   first. The earlier invented island map (s15) drew what it liked.
3. **Over-used move.** The caption carrying the meaning again; here the legend is
   doing honest work, but the sheet still leans on type.
4. **What I avoided.** River edges (unknown from the read) and relief shading
   (the hachure bands are a convention, not a slope). The forest marks are
   generic; a Civ 6 forest on tundra and on grass look alike here.
5. **Next.** Keep the sheet as a record: redraw it every twenty turns of game 3
   as the known world grows, the campaign's own atlas. Make the panorama's
   ridges overlap so it reads as one country, not three staves. And when a
   read gives river banks, draw the river as the edge feature it is.
