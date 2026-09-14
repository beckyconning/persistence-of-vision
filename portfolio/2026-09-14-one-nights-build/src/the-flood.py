# the-flood: classic1e30's escape counts as land (height = log2 n), the auto limit as sea level (log2 of maxIter / 2).
# The rule raises the limit while >= 0.5% of samples escape above the water. Real fractions at 400x400:
# limit 32768 -> 99.998% above; 65536 -> 12.386%; 131072 -> 0.002% (settled). The 3 capped points (inside the set) never flood.
# Renderer: front-to-back voxel-space terrain (after the 1992 demoscene technique), daylight palette with distance fog.
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
N = 400
v = np.fromfile(D + 'classic.bin', dtype=np.float32).reshape(N, N).astype(np.float64)
v[v < 0] = v.max() * 1.6                       # capped = inside the set: the tallest ground
EX = 40.0
land = (np.log2(v) - 14.5) * EX                  # log2 n of about 14.6 .. 16.3 (interior ~17), exaggerated
W, H = 900, 520
HORIZON = 170
SKY_TOP, SKY_LOW = np.array([214, 222, 224]), np.array([241, 234, 221])
WATER = np.array([112, 132, 143])
LOW, HIGH = np.array([124, 130, 104]), np.array([206, 194, 164])
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
serif = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 26)

zs = np.concatenate([np.linspace(2, 60, 120), np.linspace(61, 520, 240)])
cols = np.arange(W)
rows = np.arange(H)[:, None]

def render(water, label1, label2):
    img = np.zeros((H, W, 3))
    t = np.clip(rows / (HORIZON + 40), 0, 1)
    img[:] = (SKY_TOP * (1 - t) + SKY_LOW * t)[:, None, :]
    ybuf = np.full(W, H)
    cam_x, cam_y, cam_h = 200.0, -30.0, 118.0
    for z in zs:
        px = cam_x + (cols - W / 2) / W * z * 1.25
        py = np.full(W, cam_y + z)
        inside = (px >= 0) & (px < N - 1) & (py >= 0) & (py < N - 1)
        ix = np.clip(px.astype(int), 0, N - 2)
        iy = np.clip(py.astype(int), 0, N - 2)
        h = land[iy, ix]
        hx = land[iy, ix + 1]
        surf = np.maximum(h, water)
        wet = h < water
        y = (HORIZON + (cam_h - surf) / z * 140.0).astype(int)
        y = np.where(inside, y, H)
        tone = np.clip((h / EX + 14.5 - 14.6) / 1.9, 0, 1)
        shade = np.clip(1.0 + (h - hx) * 0.12, 0.70, 1.25)          # light from the left
        colour = (LOW[None, :] * (1 - tone[:, None]) + HIGH[None, :] * tone[:, None]) * shade[:, None]
        colour = np.where(wet[:, None], WATER[None, :] * np.full(W, 0.95 + 0.05 * np.sin(z * 1.3))[:, None], colour)
        fog = np.clip(z / 560.0, 0, 0.85) ** 1.2
        colour = colour * (1 - fog) + SKY_LOW[None, :] * fog
        draw = (y < ybuf) & inside
        if not draw.any():
            continue
        mask = (rows >= y[None, :]) & (rows < ybuf[None, :]) & draw[None, :]
        img[mask] = np.broadcast_to(colour[None, :, :], (H, W, 3))[mask]
        ybuf = np.where(draw, np.minimum(ybuf, y), ybuf)
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    d.text((34, 26), 'the flood', font=serif, fill=(60, 62, 60))
    d.text((34, H - 52), label1, font=font, fill=(52, 54, 52))
    d.text((34, H - 30), label2, font=font, fill=(52, 54, 52))
    return out

stages = [(32768, 99.998), (65536, 12.386), (131072, 0.002)]
frames, durations = [], []
prev_level = (np.log2(stages[0][0] / 2) - 14.5) * EX - 25
for i, (M, pct) in enumerate(stages):
    level = (np.log2(M / 2) - 14.5) * EX
    steps = 10
    for k in range(1, steps + 1):
        wl = prev_level + (level - prev_level) * (k / steps) ** 0.8
        verdict = 'raise' if pct >= 0.5 else 'settled: the limit stops rising'
        frames.append(render(wl, f'iteration limit {M}   sea level n = {M // 2}',
                             f'land above water {pct:.3f}%   (rule: raise while >= 0.500%)   {verdict if k == steps else ""}'))
        durations.append(110)
    durations[-1] = 1800
    prev_level = level
frames[0].save(D + 'the-flood.gif', save_all=True, append_images=frames[1:], duration=durations, loop=0, optimize=True)
frames[19].save(D + 'the-flood-65536.png')
frames[-1].save(D + 'the-flood-settled.png')
print('frames', len(frames))
