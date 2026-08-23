#!/usr/bin/env python3
"""The Linden and the Banner - one canvas, one parameter t=x/W, the rule printed in the piece.
Left: engraved linden over field rows. Right: the same scene under a quantised rule -
flat poster shapes, collectivised bands, the red wedge. The ground never changes; only the rule."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, STRIP = 1680, 1000, 120
rng = np.random.default_rng(1381)
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
t = xx / W

def blur(a, r, n=3):
    for _ in range(n):
        k = np.ones(2*r+1, np.float32)/(2*r+1)
        a = np.apply_along_axis(lambda v: np.convolve(v, k, 'same'), 0, a)
        a = np.apply_along_axis(lambda v: np.convolve(v, k, 'same'), 1, a)
    return a

HOR = int(H*0.80)
cx, cy = W*0.44, H*0.40

# ---------- scene masks ----------
crown = np.zeros((H, W), np.float32)
for bx, by, r in [(cx, cy, 205), (cx-165, cy+55, 140), (cx+170, cy+50, 150),
                  (cx-80, cy-130, 125), (cx+90, cy-125, 115), (cx+5, cy+140, 150)]:
    crown = np.maximum(crown, ((xx-bx)**2+(yy-by)**2 < r*r).astype(np.float32))
crown = blur(crown, 6, 2)
tt_ = np.clip((yy-(cy+120))/(HOR-(cy+120)), 0, 1)
spine = cx + 14*np.sin(tt_*2.0)
trunk = ((yy > cy+80) & (yy < HOR+6) & (np.abs(xx-spine) < 14+46*tt_**1.7)).astype(np.float32)

# tone: light upper-left on the crown, dark core, solid trunk
lightd = np.clip(((xx-cx)+ (yy-cy))/430 + 0.42, 0.06, 1.0)
tone = np.clip(crown*(0.16 + 0.62*lightd), 0, 1)
tone = np.maximum(tone, trunk*0.92)
ground = (yy > HOR).astype(np.float32)
rowph = (yy-HOR)*(0.11 - 0.00004*(yy-HOR))
tone = np.maximum(tone, ground*(0.30+0.16*np.sin(rowph*6.0 + 0.002*xx)))

# ---------- the rule, as functions of t (printed below) ----------
cell  = 1 + 18*t
fills = np.clip((t-0.52)/0.30, 0, 1)
period = 6.5 + 5.5*t
lw_gain = 1 + 1.6*t

qs = (cell*5).astype(np.int32).clip(1, None)
qx = (xx//qs*qs).astype(np.int32).clip(0, W-1)
qy = (yy//qs*qs).astype(np.int32).clip(0, H-1)
tone_q = tone[qy, qx]
tone_m = tone*(1-fills) + tone_q*fills

# engraving: horizontal lines displaced upward by the crown (engraver's bulge)
bulge = blur(crown, 10, 2)*46 + blur(trunk, 8, 2)*18
phase = (yy - bulge*(1-0.65*fills))
stripes = 0.5+0.5*np.sin(2*np.pi*phase/period)
duty = np.clip(tone_m*1.02, 0, 0.80)*np.clip(0.40+0.34*lw_gain, 0, 1)
lines = (stripes < duty).astype(np.float32)
lines *= (rng.random((H, W)) > 0.03)

scene = np.clip(crown+trunk+ground, 0, 1)
scene_q = scene[qy, qx]
band = (np.sin(np.floor(rowph[qy, qx]*6.0/1.6)*1.6 + 0.002*qx) > 0).astype(np.float32)
poster_tree = ((tone_q > 0.42) & (scene_q > 0.55) & (yy < HOR+8)).astype(np.float32)
poster = np.clip(poster_tree + ground*band, 0, 1)
ink_mask = np.clip(lines*(1-fills) + poster*fills, 0, 1)*(tone_m > 0.10)

# ---------- colour ----------
cream = np.array([233, 220, 192], np.float32)
inkC = np.array([46, 34, 21], np.float32); inkV = np.array([22, 17, 15], np.float32)
red = np.array([194, 31, 28], np.float32)
img = np.ones((H, W, 3), np.float32)*cream
ink = inkC*(1-t[..., None]) + inkV*t[..., None]
img = img*(1-ink_mask[..., None]) + ink*ink_mask[..., None]

# the red wedge: apex in the crown's heart, opening right, entering at t=0.42
apex_x, apex_y = cx+150, cy-5
wt = np.clip((t-0.42)/0.58, 0, 1)
half = 8 + 235*np.clip((xx-apex_x)/(W-apex_x), 0, 1)
wmask = ((xx > apex_x) & (np.abs(yy-(apex_y+(xx-apex_x)*0.06)) < half)).astype(np.float32)*(wt**0.75)*0.94
img = img*(1-wmask[..., None]) + red*wmask[..., None]
img[(wmask > 0.45) & (ink_mask > 0.5)] = inkV  # ink overprints inside the wedge

out = Image.fromarray(img.clip(0, 255).astype(np.uint8))
# ---------- rule strip ----------
strip = Image.new("RGB", (W, STRIP), (233, 220, 192)); d = ImageDraw.Draw(strip)
try:
    fm = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 15)
    fs = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 12)
except OSError:
    fm = fs = ImageFont.load_default()
d.line([(0, 0), (W, 0)], fill=(46, 34, 21), width=3)
for name, b in [("FREE COMMUNE", 0.0), ("SYNDICALIST LEAGUE", 0.2), ("POPULAR REPUBLIC", 0.4),
                ("VANGUARD STATE", 0.6), ("DICTATORSHIP OF THE TOILERS", 0.8)]:
    x = int(b*W); d.line([(x, 0), (x, 26)], fill=(46, 34, 21), width=2)
    d.text((x+6, 8), name, font=fs, fill=(46, 34, 21))
d.text((14, 44), ("t = x/W      cell(t) = 1+18t      fills(t) = clip((t-.52)/.30)      "
                  "period(t) = 6.5+5.5t      w(t) = 1+1.6t      red: t > 0.42"), font=fm, fill=(46, 34, 21))
d.text((14, 72), "the ground never changes. only the rule.", font=fm, fill=(158, 43, 37))
d.line([(int(0.42*W), 0), (int(0.42*W), STRIP)], fill=(194, 31, 28), width=2)
d.text((int(0.42*W)+6, 96), "red enters", font=fs, fill=(194, 31, 28))
final = Image.new("RGB", (W, H+STRIP)); final.paste(out, (0, 0)); final.paste(strip, (0, H))
final.save("the-linden-and-the-banner.png"); print("saved", final.size)
