"""Ten: snow on a Game Boy. 160 x 144, four greens, 40 sprites in OAM, and the hardware's rule: a scan line shows
at most ten sprites, the lowest OAM indexes first. Forty flakes fall toward a street lamp and settle. The ground
line can never show more than ten of them; the rest are there, and drawn nowhere. A flake that lands after the
tenth vanishes as it touches down, and falling flakes blink out as they cross a line already full.
Writes ten.gif and ten.png (the last frame)."""
import os, numpy as np
from PIL import Image

OUT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAL = np.array([(0x9B, 0xBC, 0x0F), (0x8B, 0xAC, 0x0F), (0x30, 0x62, 0x30), (0x0F, 0x38, 0x0F)], np.uint8)
W, H, GROUND = 160, 144, 128
bg = np.full((H, W), 3, np.uint8)                          # night
yy, xx = np.mgrid[0:H, 0:W]
cone = (yy > 30) & (np.abs(xx - 118) < (yy - 30) * 0.55) & (yy < GROUND)
bg[cone] = 2                                                 # lamp light
bg[GROUND:] = 1                                              # snowy ground
bg[GROUND:GROUND + 1] = 3                                    # its edge
bg[GROUND:][(xx[GROUND:] - 118) ** 2 < 900] = 0             # the pool of light on it
bg[24:GROUND, 117:119] = 3                                   # the post (dark against the light)
bg[22:30, 113:123] = 3; bg[26:30, 115:121] = 0               # the lamp head, lit underside
bg[70:GROUND, 10:52] = 2; bg[58:70, 16:46] = 2               # a house, dimly
bg[84:96, 24:32] = 0                                         # one lit window

rng = np.random.default_rng(10)
N = 40
x = rng.integers(60, 150, N).astype(float)                   # the flakes gather around the light
start = np.sort(rng.integers(0, 150, N))                     # OAM order = order of falling
speed = rng.uniform(0.7, 1.3, N)
FLAKE = np.array([[0, 1, 0], [1, 1, 1], [0, 1, 0]], bool)
frames = []
for t in range(0, 260, 2):
    img = bg.copy()
    tops = np.clip((t - start) * speed - 8, -16, GROUND - 5)      # sprite top; flakes sit on the ground line
    alive = t >= start
    for line in range(H):
        on = [k for k in range(N) if alive[k] and tops[k] <= line < tops[k] + 8]
        for k in on[:10]:                                          # the rule: ten per line, lowest index wins
            dy = line - int(tops[k]) - 2
            if 0 <= dy < 3:
                for dx in range(3):
                    if FLAKE[dy, dx]:
                        px = int(x[k]) + 2 + dx + int(2 * np.sin((t + k * 9) / 14)) * (tops[k] < GROUND - 5)
                        if 0 <= px < W: img[line, px] = 0
    frames.append(Image.fromarray(np.repeat(np.repeat(PAL[img], 3, 0), 3, 1)))
frames += [frames[-1]] * 20
frames[0].save(os.path.join(OUT, "ten.gif"), save_all=True, append_images=frames[1:], duration=66, loop=0)
frames[-1].save(os.path.join(OUT, "ten.png"))
landed = int(((np.clip((258 - start) * speed - 8, -16, GROUND - 5)) >= GROUND - 5).sum())
print("flakes landed", landed, "of", N)
