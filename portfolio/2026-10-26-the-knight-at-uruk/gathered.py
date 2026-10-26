"""All four off the ground: the gathered phase of the gallop as a single print.
Muybridge's 1878 finding, against the painters' flying gallop with the legs
stretched fore and aft. The one moment in the stride when the knight is
unsupported, and the only one the archer on the wall would want."""
from PIL import Image, ImageDraw, ImageFont
import knight as K

K.SCENE_W = 3.7
K.PX = 1200 / K.SCENE_W
K.GROUND_Y = 0.30
img = K.render_frame(0.86, rng_seed=4242, number=None, px_w=1200, px_h=1000)
sheet = Image.new("RGB", (1260, 1120), K.PAPER)
sheet.paste(img, (30, 30))
d = ImageDraw.Draw(sheet)
d.rectangle([30, 30, 1229, 1029], outline=K.INK_FAR, width=1)
d.text((30, 1046), "ALL FOUR OFF THE GROUND.  The gathered phase, 0.86 of the stride.", font=ImageFont.truetype(K.FONT_BOLD, 22), fill=K.INK)
d.text((30, 1082), "Muybridge's finding of 1878: the horse leaves the ground with its legs under it, not stretched out as the painters had it.", font=ImageFont.truetype(K.FONT_PATH, 15), fill=K.INK)
K.paper_texture(sheet, seed=5).save(K.HERE / "all-four-off-the-ground.png")
