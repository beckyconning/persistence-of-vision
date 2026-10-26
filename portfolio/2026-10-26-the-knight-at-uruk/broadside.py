"""Orders for game three: the notebook's current hypothesis set as a broadside."""
from PIL import Image, ImageDraw, ImageFont
import knight as K

W, H = 1000, 1400
img = Image.new("RGB", (W, H), K.PAPER)
d = ImageDraw.Draw(img)
B = lambda n: ImageFont.truetype(K.FONT_BOLD, n)
R = lambda n: ImageFont.truetype(K.FONT_PATH, n)
INK, FAR = K.INK, K.INK_FAR
m = 70


def rule(y, w=3):
    d.line([(m, y), (W - m, y)], fill=INK, width=w)


def centered(y, text, font, fill=INK):
    tw = d.textlength(text, font=font)
    d.text(((W - tw) / 2, y), text, font=font, fill=fill)


rule(60, 6); rule(70, 2)
centered(92, "ORDERS FOR GAME THREE", B(54))
centered(160, "ROME UNDER TRAJAN, DEITY, SCORE VICTORY OFF", R(22))
rule(200, 2)
centered(214, "Written after two lost games on 2026-10-26: Maya, turn 36, no walls; Sumeria, turn 125, two cities and Ancient Walls against knights.", R(14), FAR)
rule(246, 2)

y = 275
d.text((m, y), "I.", font=B(30), fill=INK); d.text((m + 60, y + 4), "Open warrior, slinger, settler, slinger, settler.", font=R(24), fill=INK)
y += 46
d.text((m, y), "II.", font=B(30), fill=INK); d.text((m + 60, y + 4), "Settle toward the strongest neighbour. Claim the contested land first.", font=R(24), fill=INK)
y += 46
d.text((m, y), "III.", font=B(30), fill=INK); d.text((m + 60, y + 4), "Walls in every border city on founding. Escort every settler.", font=R(24), fill=INK)
y += 46
d.text((m, y), "IV.", font=B(30), fill=INK); d.text((m + 60, y + 4), "District adjacency scored by hand, from the map, and said in the log.", font=R(24), fill=INK)
y += 46
d.text((m, y), "V.", font=B(30), fill=INK); d.text((m + 60, y + 4), "No unit on a tile beside the city when the enemy fields cavalry.", font=R(24), fill=INK)
y += 70
rule(y, 2); y += 18
centered(y, "BY THE TURN", B(26)); y += 50

targets = [
    ("30", "Archery"), ("40", "Masonry"), ("60", "Four cities. Political Philosophy"),
    ("90", "Six cities"), ("100", "Construction and Castles: Medieval Walls"), ("110", "Machinery: crossbows"),
]
for n, what in targets:
    d.text((m + 40, y - 14), n, font=B(64), fill=INK)
    d.text((m + 230, y + 14), what, font=R(26), fill=INK)
    d.line([(m + 200, y + 10), (m + 200, y + 50)], fill=FAR, width=2)
    y += 84

y += 10; rule(y, 2); y += 22
centered(y, "A legitimate win is Science, Culture, Religion, Diplomacy or Domination.", R(22)); y += 36
centered(y, "Walls are era-relative. Expansion is defence.", B(24)); y += 60
rule(y, 2); rule(y + 10, 6)
centered(H - 70, "campaign/NOTEBOOK.md, Current hypothesis, 2026-10-26", R(14), FAR)

img = K.paper_texture(img, seed=3)
img.save(K.HERE / "orders-for-game-three.png")
