"""2D corruption toolkit for ep2: post-fx, HUD garbage, error dialogs, BSOD."""
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H = 854, 480
FONT = "/mnt/c/Windows/Fonts/consolab.ttf"
_fonts = {}


def F(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


def channel_shift(a, amt, rng):
    sh = int(2 + amt * 22)
    a[..., 0] = np.roll(a[..., 0], rng.integers(-sh, sh + 1), axis=1)
    a[..., 2] = np.roll(a[..., 2], rng.integers(-sh, sh + 1), axis=1)
    return a


def row_tears(a, amt, rng):
    for _ in range(int(1 + amt * 12)):
        y0 = int(rng.integers(0, H - 6))
        h = int(rng.integers(2, 5 + amt * 50))
        a[y0:y0 + h] = np.roll(a[y0:y0 + h], int(rng.integers(-140, 140)), axis=1)
    return a


def vroll(a, amt, rng):
    """Vertical hold failure."""
    return np.roll(a, int(rng.integers(1, int(30 + amt * 300))), axis=0)


def pixelate(a, k):
    k = max(2, int(k))
    small = a[::k, ::k]
    return np.repeat(np.repeat(small, k, axis=0), k, axis=1)[:H, :W]


def static_noise(a, amt, rng):
    n = rng.integers(0, 256, (H, W, 1), dtype=np.int16).repeat(3, axis=2)
    m = (rng.random((H, W, 1)) < amt * 0.6)
    return np.where(m, n, a.astype(np.int16)).astype(np.uint8)


def invert(a):
    return 255 - a


def quantize(a, levels=4):
    q = 256 // levels
    return (a // q * q).astype(np.uint8)


def block_corrupt(a, amt, rng):
    """Macroblock displacement (datamosh flavor)."""
    for _ in range(int(amt * 14)):
        bw, bh = int(rng.integers(24, 120)), int(rng.integers(16, 80))
        x0, y0 = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
        x1, y1 = int(rng.integers(0, W - bw)), int(rng.integers(0, H - bh))
        a[y1:y1 + bh, x1:x1 + bw] = a[y0:y0 + bh, x0:x0 + bw]
    return a


def apply_glitch(img_arr, amt, seed, ghost=None):
    """Compose 2D corruption at intensity amt (0..1). Returns array (+ maybe ghost mix)."""
    if amt <= 0.005:
        return img_arr
    rng = np.random.default_rng(seed)
    a = img_arr.copy()
    if ghost is not None and rng.random() < amt * 0.45:
        k = 0.3 + 0.35 * rng.random()
        a = (a * (1 - k) + ghost * k).astype(np.uint8)
    a = row_tears(a, amt, rng)
    a = channel_shift(a, amt, rng)
    if rng.random() < amt * 0.5:
        a = block_corrupt(a, amt, rng)
    if rng.random() < amt * 0.35:
        a = pixelate(a, 2 + amt * 8)
    if rng.random() < amt * 0.3:
        a = quantize(a, max(2, int(8 - amt * 6)))
    if rng.random() < amt * 0.25:
        a = vroll(a, amt, rng)
    if rng.random() < amt * 0.18:
        a = invert(a)
    a = static_noise(a, amt * 0.38, rng)
    return a


# ---------------- text corruption ----------------

GARBAGE = list("▓▒░█@#%&$?!/\\|<>~^*ΩΣΞ¤§Ø01")
ZALGO = ["́", "̶", "̴", "͓", "҉"]


def corrupt_text(s, amt, rng):
    out = []
    for ch in s:
        r = rng.random()
        if r < amt * 0.35:
            out.append(str(rng.choice(GARBAGE)))
        elif r < amt * 0.55:
            out.append(ch + str(rng.choice(ZALGO)))
        else:
            out.append(ch)
    return "".join(out)


def corrupt_hud(t, amt, rng):
    if amt < 0.1:
        return f"CLAUDIO*1   TOKENS x1   WORLD 1-2   CONTEXT {max(0,int(180000 - t*3600))}"
    if amt < 0.3:
        return f"CLAUDIO*0   TOKENS x1   WORLD 1-2   CONTEXT {int(-(t*7919) % 99999)}"
    if amt < 0.6:
        base = f"CLAUD1O*-1  TOKENS xNaN  WORLD ?-?  CONTEXT 0x{int(t*1e6)%0xFFFFFF:06X}"
        return corrupt_text(base, amt * 0.6, rng)
    base = "BUG*1   CLAUDIO xNULL   WORLD -1--1   CONTEXT undefined"
    return corrupt_text(base, amt * 0.8, rng)


# ---------------- dialogs / screens ----------------

def error_dialog(d, x, y, title, body, w=340, h=96):
    d.rectangle((x, y, x + w, y + h), fill=(200, 198, 192), outline=(60, 60, 70), width=2)
    d.rectangle((x, y, x + w, y + 22), fill=(28, 40, 120))
    d.text((x + 8, y + 4), title, font=F(13), fill=(255, 255, 255))
    d.text((x + w - 18, y + 3), "X", font=F(14), fill=(255, 255, 255))
    d.text((x + 14, y + 34), body, font=F(13), fill=(20, 20, 24))
    d.rectangle((x + w // 2 - 34, y + h - 28, x + w // 2 + 34, y + h - 8),
                fill=(224, 222, 216), outline=(60, 60, 70))
    d.text((x + w // 2, y + h - 18), "OK", font=F(12), fill=(20, 20, 24), anchor="mm")


DIALOGS = [
    ("claudio.exe", "claudio.exe is not responding"),
    ("RuntimeError", "pose 'victory' not found"),
    ("zbuffer.sys", "depth integrity check FAILED"),
    ("PermissionError", "stomp request timed out"),
    ("physics.dll", "gravity returned NaN"),
    ("mustache.dll", "asset corrupted beyond repair"),
    ("reality.exe", "reality.exe has stopped working"),
]


def bsod(t):
    im = Image.new("RGB", (W, H), (8, 30, 160))
    d = ImageDraw.Draw(im)
    lines = [
        "CLAUDIO_PANIC: unhandled BUG at 0x00000000",
        "",
        "The simulation has been halted to prevent",
        "damage to your mushroom kingdom.",
        "",
        "*** STOP: 0xBADSTOMP (0xDEADBEEF, 0x00000001,",
        "          0xC0FFEE42, 0xFFFFFFFF)",
        "",
        "beginning dump of context window . . .",
        "context dumped. it's gone. sorry.",
        "",
        "contact your system administrator or a",
        "plumber, whichever responds first.",
    ]
    y = 90
    for ln in lines:
        d.text((90, y), ln, font=F(17), fill=(235, 240, 255))
        y += 24
    return np.asarray(im)


def hold_frame_bar(d, t):
    """Fake 'buffering' bar for stutters."""
    d.rectangle((0, H - 6, int((t * 2.4 % 1) * W), H), fill=(255, 60, 60))
