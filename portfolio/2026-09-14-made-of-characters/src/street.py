"""Northern Quarter at dusk, generated as a square-pixel image, then forced through the terminal's
constraint: 16 quadrant block characters, one foreground and one background colour per cell.
scene(night, lit) is used by lights_out.py; running this file writes the dusk still."""
import numpy as np
from PIL import Image

W, H = 240, 176                      # square pixels; becomes 120 x 44 character cells
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)

def mix(a, b, t):
    t = np.clip(t, 0, 1)[..., None] if np.ndim(t) else np.clip(t, 0, 1)
    return np.asarray(a, np.float32) * (1 - t) + np.asarray(b, np.float32) * t

def hexc(h): return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], np.float32) / 255

def scene(night=0.0, lit_set=None):
    rng = np.random.default_rng(1904)
    if lit_set is None:
        r0 = np.random.default_rng(7)
        lit_set = {(f, b) for f in range(4) for b in range(5) if r0.random() < 0.45}
    # sky: deep teal at the top to a thin peach band at the horizon
    sky_t = yy / 118.0
    img = np.zeros((H, W, 3), np.float32)
    img[:] = mix(mix(hexc("16303f"), hexc("070b12"), night), mix(hexc("5f7f86"), hexc("1b2733"), night), sky_t * 1.1)
    img = mix(img, hexc("e8a47c"), np.clip((sky_t - 0.72) * 3.2, 0, 1) * (1 - night))

    # far terrace roofline to the right (behind the street)
    far = np.full(W, 118.0)
    x = 0
    while x < W:
        w = rng.integers(10, 26); h = rng.integers(70, 104)
        far[x:x + w] = h; x += w
    chimneys = rng.integers(130, W, 7)
    for c in chimneys: far[c:c + 2] = np.minimum(far[c:c + 2], far[c] - 6)
    far_mask = yy >= far[None, :]
    img[far_mask] = hexc("2a2f3a")
    # a few lit windows in the far terrace
    for i in range(34):
        wx, wy = rng.integers(128, W - 3), rng.integers(80, 116)
        if wy > far[wx] + 3 and rng.random() > night * 0.8:
            img[wy:wy + 2, wx:wx + 2] = hexc("f2c46a") * rng.uniform(0.7, 1.0)

    # street and pavement
    ground = yy >= 150
    img[ground] = hexc("22242b")
    img[150:154, 0:W] = hexc("34363e")                     # pavement edge in front of everything
    # wet reflections: lamp glow and window light smeared vertically
    lamp_x, lamp_y = 178, 112
    glow = np.exp(-(((xx - lamp_x) / 16) ** 2 + ((yy - lamp_y) / 13) ** 2))
    img = mix(img, hexc("ffb45a"), glow * (0.55 + 0.25 * night))
    refl = np.exp(-((xx - lamp_x) / 5.5) ** 2) * np.clip((yy - 150) / 26, 0, 1) * (0.55 + 0.45 * np.sin(yy * 1.7) ** 2)
    img = mix(img, hexc("e79a52"), np.where(ground, refl * 0.8, 0))
    # lamp post
    img[108:150, lamp_x:lamp_x + 2] = hexc("111318")
    img[106:109, lamp_x - 3:lamp_x + 5] = hexc("111318")
    img[109:112, lamp_x - 1:lamp_x + 3] = hexc("fff0c2")
    # kerb line
    img[150:152, 118:W] = hexc("3b3d45")

    # the warehouse: left 55 percent, red brick, receding a little toward the right
    face_r = 132
    face = (xx < face_r) & (yy >= 14) & (yy < 150)
    brick = mix(hexc("7a3526"), hexc("9a4a33"), rng.random((H, W)) * 0.6)
    mortar = ((yy.astype(int) % 4) == 0) | (((xx.astype(int) + (yy.astype(int) // 4) * 3) % 8) == 0)
    brick = np.where(mortar[..., None], brick * 0.78, brick)
    shade = np.clip(1.0 - (xx / face_r) * 0.35 - (yy / H) * 0.15, 0.45, 1)[..., None] * (1 - 0.55 * night)
    img = np.where(face[..., None], brick * shade, img)
    # cornice and the warehouse name band
    img[14:18, 0:face_r + 3] = hexc("4b2219")
    img[40:43, 0:face_r] = hexc("5a2a1e")
    # arched windows, 4 floors x 5 bays; lit ones warm, some half-lit
    for floor, fy in enumerate((22, 50, 82, 112)):
        for bay, bx in enumerate((10, 34, 58, 82, 106)):
            wh = 20 if floor else 14
            win = (xx >= bx) & (xx < bx + 14) & (yy >= fy) & (yy < fy + wh)
            arch = (xx - (bx + 7)) ** 2 + ((yy - (fy + 6)) * 1.3) ** 2 <= 49
            shape = win & ((yy >= fy + 6) | arch)
            lit = (floor, bay) in lit_set
            colour = hexc("f6c870") if lit else hexc("1c2129")
            if lit:
                inner = mix(colour, hexc("fff1c7"), np.exp(-(((xx - bx - 7) / 7) ** 2 + ((yy - fy - wh * 0.6) / 8) ** 2)))
                img = np.where(shape[..., None], inner, img)
            else:
                img = np.where(shape[..., None], mix(colour, hexc("3a5566"), np.clip((fy + wh - yy) / wh, 0, 1) * 0.35), img)
            # sill
            img[fy + wh:fy + wh + 1, bx - 1:bx + 15] = hexc("c9b8a0")
    # ground-floor doorway, open and lit
    img[137:150, 118:132] = hexc("1a1512")
    img[139:150, 120:130] = mix(hexc("ffcf86"), hexc("a2612e"), np.clip((yy[139:150, 120:130] - 139) / 11, 0, 1))
    # the fire escape: iron zigzag down the right edge of the facade
    iron = hexc("0f1115")
    for k, fy in enumerate((46, 78, 110)):
        img[fy:fy + 2, 96:132] = iron                       # landing
        for s in range(30):                                  # stair diagonal
            sx = 128 - s if k % 2 == 0 else 100 + s
            img[fy + 2 + s: fy + 4 + s, sx:sx + 2] = iron
        img[fy - 6:fy, 96:98] = iron; img[fy - 6:fy, 130:132] = iron   # railings
        img[fy - 6:fy - 5, 96:132] = iron

    # the lit doorway spills onto the wet pavement
    spill = np.exp(-((xx - 125) / 7) ** 2) * np.clip((yy - 150) / 20, 0, 1) * (0.5 + 0.5 * np.sin(yy * 2.3) ** 2)
    img = mix(img, hexc("d99256"), spill * 0.55)
    np.clip(img, 0, 1, out=img)
    return img

if __name__ == '__main__':
    img = scene()
    Image.fromarray((img * 255).astype(np.uint8)).save('street-source.png')
    np.save('street.npy', img)
