# the-cast: the 1e250 Misiurewicz spiral's escape counts as a plaster relief under raking daylight.
# Height = -log(n + frac) (smooth). No palette gradient: form is carried only by light on a stone surface.
import numpy as np
from PIL import Image, ImageFilter

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
W, H = 640, 400
v = np.fromfile(D + 'spiral.bin', dtype=np.float32).reshape(H, W).astype(np.float64)
h = -np.log(v)
h = (h - h.min()) / (h.max() - h.min())          # 0 (slowest escapes, the filaments) .. 1 (fastest)
h = 1.0 - h                                       # filaments stand proud
h = np.asarray(Image.fromarray((h * 65535).astype(np.uint16)).resize((W * 2, H * 2), Image.BICUBIC)).astype(np.float64) / 65535
h = np.asarray(Image.fromarray((h * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(1.1))).astype(np.float64) / 255

relief = 38.0
gy, gx = np.gradient(h * relief)
nx, ny, nz = -gx, -gy, np.ones_like(h)
norm = np.sqrt(nx * nx + ny * ny + nz * nz)
nx, ny, nz = nx / norm, ny / norm, nz / norm

light = np.array([-0.78, -0.42, 0.46])            # low raking light from the upper left
light /= np.linalg.norm(light)
lambert = np.clip(nx * light[0] + ny * light[1] + nz * light[2], 0, 1)

# cheap ambient occlusion: how far a point sits below its neighbourhood
blur = np.asarray(Image.fromarray((h * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(9))).astype(np.float64) / 255
ao = np.clip(1.0 - 2.2 * np.maximum(0, blur - h), 0.45, 1.0)

stone_lit = np.array([236, 229, 214])
stone_shadow = np.array([122, 112, 101])
shade = (0.18 + 0.82 * lambert) * ao
rgb = stone_shadow[None, None, :] + (stone_lit - stone_shadow)[None, None, :] * shade[:, :, None]

rng = np.random.default_rng(7)
rgb += rng.normal(0, 2.4, (h.shape[0], h.shape[1], 1))          # plaster grain
Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8)).save(D + 'the-cast.png')
print('saved', h.shape)
