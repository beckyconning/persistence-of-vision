# homage-to-the-gradient: Mandeldive's classic palette as an Albers "Homage to the Square".
# Five nested hard-edge squares, outermost first, one per gradient stop; each square's side is (1 - stop position),
# so the gradient's real spacing (0, 0.16, 0.42, 0.6425, 0.8575) is the composition. Albers offset: squares sit low,
# bottom margin a third of the side margins. Colour only; no line, no text on the plate.
from PIL import Image, ImageDraw

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
stops = [(0.0, (0, 7, 100)), (0.16, (32, 107, 203)), (0.42, (237, 255, 255)), (0.6425, (255, 170, 0)), (0.8575, (0, 2, 0))]
S = 1600
img = Image.new('RGB', (S, S), stops[0][1])
d = ImageDraw.Draw(img)
for pos, colour in stops[1:]:
    side = S * (1.0 - pos)
    margin = (S - side) / 2.0
    left = margin
    bottom_margin = (S - side) * 0.25      # Albers: the smaller gap below (1:3 against the gap above)
    top = S - bottom_margin - side
    d.rectangle([left, top, left + side, top + side], fill=colour)
img.save(D + 'homage-to-the-gradient.png')

# study: the same five squares with the order inverted (innermost first), black outermost
inv = Image.new('RGB', (S, S), stops[-1][1])
d = ImageDraw.Draw(inv)
for pos, colour in reversed(stops[:-1]):
    side = S * (1.0 - (0.8575 - pos))
    margin = (S - side) / 2.0
    top = S - (S - side) * 0.25 - side
    d.rectangle([margin, top, margin + side, top + side], fill=colour)
inv.save(D + 'homage-inverted-study.png')
print('ok')
