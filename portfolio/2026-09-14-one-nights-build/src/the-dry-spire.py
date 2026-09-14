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
PAD = 1200
land = np.pad(land, PAD, mode='constant', constant_values=land.min())   # open sea beyond the map
N = N + 2 * PAD
W, H = 1600, 900
HORIZON = 300
SKY_TOP, SKY_LOW = np.array([214, 222, 224]), np.array([241, 234, 221])
WATER = np.array([112, 132, 143])
LOW, HIGH = np.array([124, 130, 104]), np.array([206, 194, 164])
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
serif = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf', 26)

zs = np.concatenate([np.linspace(2, 60, 160), np.linspace(61, 900, 420)])
cols = np.arange(W)
rows = np.arange(H)[:, None]

def render(water, label1, label2):
    img = np.zeros((H, W, 3))
    t = np.clip(rows / (HORIZON + 40), 0, 1)
    img[:] = (SKY_TOP * (1 - t) + SKY_LOW * t)[:, None, :]
    ybuf = np.full(W, H)
    cam_x, cam_y, cam_h = 181.0 + PAD, 110.0 + PAD, 112.0
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
        y = (HORIZON + (cam_h - surf) / z * 250.0).astype(int)
        y = np.where(inside, y, H)
        tone = np.clip((h / EX + 14.5 - 14.6) / 1.9, 0, 1)
        shade = np.clip(1.0 + (h - hx) * 0.12, 0.70, 1.25)          # light from the left
        colour = (LOW[None, :] * (1 - tone[:, None]) + HIGH[None, :] * tone[:, None]) * shade[:, None]
        colour = np.where(wet[:, None], WATER[None, :] * (0.975 + 0.012 * np.sin(z * 0.55) + 0.01 * np.random.default_rng(int(z * 10)).standard_normal(W))[:, None], colour)
        fog = np.clip(z / 900.0, 0, 0.9) ** 1.1
        colour = colour * (1 - fog) + SKY_LOW[None, :] * fog
        draw = (y < ybuf) & inside
        if not draw.any():
            continue
        mask = (rows >= y[None, :]) & (rows < ybuf[None, :]) & draw[None, :]
        img[mask] = np.broadcast_to(colour[None, :, :], (H, W, 3))[mask]
        ybuf = np.where(draw, np.minimum(ybuf, y), ybuf)
    out = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))
    d = ImageDraw.Draw(out)
    pass
    d.text((34, H - 52), label1, font=font, fill=(52, 54, 52))
    d.text((34, H - 30), label2, font=font, fill=(52, 54, 52))
    return out


still = render((np.log2(65536) - 14.5) * EX, '', '')
arr = np.asarray(still).copy()
Image.fromarray(arr).save(D + 'the-dry-spire.png')
print('saved')
