# the-ratchet: cyanotype-palette animated GIF of the auto iteration limit across one night's visits.
# Old rule (lower only from the slowest sample) vs histogram replay. Values from the build's reviews:
# old: home 1024, classic1e30 131072, home again 65536, seahorse 131072, deep1e250 65536, seahorse 131072
# new: home 1024, classic1e30 131072, home again 1024, seahorse 16384, deep1e250 32768, seahorse 16384
import math, random
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
W, H = 1200, 720
BLUE = (22, 52, 96)
PALE = (226, 234, 238)
visits = ['home', 'classic 1e30', 'home (R)', 'seahorse 1e6', 'spiral 1e250', 'seahorse 1e6']
old = [1024, 131072, 65536, 131072, 65536, 131072]
new = [1024, 131072, 1024, 16384, 32768, 16384]
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 18)
big = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 30)

rng = np.random.default_rng(9)
grain = (rng.normal(0, 7, (H, W))).astype(np.int16)
exposure = np.fromfunction(lambda y, x: 10 * np.sin(x / 190.0) * np.cos(y / 160.0), (H, W))

def ground():
    base = np.zeros((H, W, 3), np.int16)
    for c in range(3):
        base[:, :, c] = BLUE[c] + grain + exposure.astype(np.int16)
    return Image.fromarray(np.clip(base, 0, 255).astype(np.uint8), 'RGB')

x0, x1 = 140, 1080
def X(i):
    return x0 + (x1 - x0) * i / (len(visits) - 1)
def Y(v, lane):
    top, bottom = (110, 330) if lane == 0 else (420, 640)
    t = (math.log2(v) - 10) / 7.0
    return bottom - t * (bottom - top)

def staircase(draw, seq, lane, progress, pawls):
    pts = []
    for i, v in enumerate(seq):
        pts.append((X(i), Y(v, lane)))
    total = len(seq) - 1
    p = progress * total
    for i in range(total):
        if p <= i:
            break
        f = min(1.0, p - i)
        (ax, ay), (bx, by) = pts[i], pts[i + 1]
        # horizontal to the next visit, then vertical settle
        hx = ax + (bx - ax) * min(1.0, f * 2)
        draw.line([ax, ay, hx, ay], fill=PALE, width=3)
        if f > 0.5:
            vy = ay + (by - ay) * min(1.0, (f - 0.5) * 2)
            draw.line([bx, ay, bx, vy], fill=PALE, width=3)
        if pawls and f >= 1.0 and seq[i + 1] >= seq[i]:
            # a pawl tooth under every level the old rule refused to leave
            draw.polygon([(bx - 9, by + 4), (bx + 9, by + 4), (bx, by + 16)], outline=PALE)
    for i in range(len(seq)):
        if p >= i:
            draw.ellipse([X(i) - 5, Y(seq[i], lane) - 5, X(i) + 5, Y(seq[i], lane) + 5], outline=PALE, width=2)
            draw.text((X(i) + 10, Y(seq[i], lane) - 26), str(seq[i]), font=font, fill=PALE)

frames = []
N = 70
for k in range(N + 25):
    progress = min(1.0, k / N)
    img = ground()
    d = ImageDraw.Draw(img)
    d.text((x0, 40), 'the ratchet: the old rule climbs with every dive and keeps its height', font=big, fill=PALE)
    d.text((x0, 360), 'the replay: the limit follows the terrain', font=big, fill=PALE)
    staircase(d, old, 0, progress, True)
    staircase(d, new, 1, progress, False)
    for i, name in enumerate(visits):
        d.text((X(i) - 40, 675), name, font=font, fill=PALE)
    # cyanotype bleed: slight softening of the pale chemistry, no additive glow
    img = img.filter(ImageFilter.GaussianBlur(0.6))
    frames.append(img.quantize(colors=48, method=Image.Quantize.MEDIANCUT))

frames[0].save(D + 'the-ratchet.gif', save_all=True, append_images=frames[1:], duration=[90] * N + [1200] + [90] * 24, loop=0, optimize=True)
frames[-1].convert('RGB').save(D + 'the-ratchet-final.png')
print('frames', len(frames))
