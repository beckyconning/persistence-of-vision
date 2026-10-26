# The Knight at Uruk, turn 122 (2026-10-26)

A Persian knight at full gallop, one stride in twelve numbered phases after Muybridge's
"Sallie Gardner at a Gallop" (1878), drawn in ink on paper against the Ancient Walls of
Uruk. The caption under the plate carries the record from campaign game 2 of the Civ VI
Deity project: the walls bought on turn 70 that held a Dutch warrior army ten turns, and
the roster that arrived overnight into turn 123 (two knights at 50, three men-at-arms at
45, a pikeman, a horseman, two heavy chariots, a crossbowman, two catapults). The walls
were gone on turn 124 and Uruk fell on turn 125. Walls are era-relative; this unit is the
one game 3 has to be ready for by turn 100.

Made in the art break April allowed on condition that it be about the campaign.

## Files

- `the-knight-at-uruk.png`: the plate, 12 frames in two rows, caption.
- `the-knight-at-uruk.mp4`: the stride as a loop, 24 phases at 48 fps, six strides.
- `the-knight-at-uruk.gif`: the same loop, small, for the journal.
- `the-garrison.png`: the second piece, one large frame of the gathered knight under the
  parapet with Uruk's whole defence above him, one archer, drawn from the same human
  proportions as the rider and aiming down the wall. The merlons are painted over his
  shins. This is the plate's own "next" (the wall's side of the matchup) done in the last
  third of the break; the archer's draw arm is stiff and the bow hand is a box, but the
  image states the matchup without a roster.
- `orders-for-game-three.png`: the notebook's plan for game 3 set as a letterpress
  broadside on the same paper (`broadside.py`), to hang beside the plate: five orders and
  the turn targets in large numerals.
- `knight.py`: the plate and film. `python3 knight.py all` renders both. `archer.py` hooks
  into it (`EXTRA`, `WALL_TOP`, `MERLONS`) for the garrison piece.

## What is measured, not drawn by eye

- Horse: withers 1.55 m; body landmarks and the leg roots as fractions of that (shoulder
  joint at 0.71 of withers height, hip at 0.68); forelimb humerus, forearm and cannon
  0.33, 0.40, 0.50 m; hindlimb femur, gaskin and cannon 0.40, 0.45, 0.50 m; head 0.62 m.
- Gait: right-lead transverse gallop, footfalls LH 0.00, RH 0.12, LF 0.28, RF 0.40 of the
  stride, each hoof on the ground for 0.32 of it, suspension gathered under the body for
  the last 0.28 (Muybridge's finding, against the painters' flying gallop).
- Each leg is a three-link chain: the first bone sweeps with the hoof, the other two are
  solved by two-link inverse kinematics with the knee folding back and the hock pointing
  back. The hoof follows a path in the body frame: a straight slide back on the ground in
  stance, a cosine reach forward with a lifted arc in swing.
- Rider: 1.75 m stature, Drillis and Contini fractions (torso 0.288, thigh 0.245, shin
  0.246, upper arm 0.186, forearm 0.146, head 0.130), seated with a 34 degree lean and a
  couched lance 3.25 m long.

## How it is drawn

No capsules and no silhouette fill. Every part is a contour polygon (the barrel through
fourteen landmarks on a Catmull-Rom curve, each limb from its joints and front/back
half-widths, the neck on its own axis with a throat latch, the head on its own axis with
forehead, eye, cheek, jaw, chin and nostril). Each polygon is painted back in paper
colour and then outlined with three or four overlapping tapered pen strokes with a slow
wobble, so nearer parts remove the hidden lines of farther ones: far legs first in a paler
ink, then tail, barrel, near legs, neck and head, rider, lance. The backdrop is the wall
itself as the Muybridge grid: ashlar courses, a parapet of merlons, the ground line.

## Self-critique

1. **Where it sits on the seven axes.** Form: ink line and a printed plate (paper, no
   glow). Subject: representational, a quadruped with a rider, the first animal in the
   corpus. Method: measured skeleton plus inverse kinematics plus hand-built contours.
   Palette: paper and two inks. Composition: the plate grid with the figure off centre in
   each cell. Motion: a stride loop. Concept: a record of a real defeat with its numbers
   legible, and the lesson for the next game.
2. **Which axis moved.** Subject: the first properly drawn figure (The Leap's door), and
   an animal, not a human. Method: kinematics driving contours rather than a silhouette.
   Concept: the piece is about the work, as asked.
3. **The most over-used move right now.** Numbers in the caption doing the meaning; the
   image alone says "a knight" and not "a knight that beat these walls".
4. **What I avoided.** The leg contours at sharply folded joints are still crude (the
   frame 4 to 6 kink turned out to be the femur's rest angle, fixed in the last ten minutes;
   what remains is the contour at the fold), the rider is a stick with a
   helmet, and I never checked the twelve phases one by one against Muybridge's plate: the
   sequence is from the published footfall fractions, not from his frames.
5. **Next.** Draw the wall's side of the story: the archer on the wall, the catapult, in
   the same ink, so the image carries the matchup without the caption. And a frame-by-frame
   comparison against the Muybridge plate before another gait piece.
