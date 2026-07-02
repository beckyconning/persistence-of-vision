"""Render the YTP video: PIL frames -> raw RGB pipe -> bundled ffmpeg (+ audio mux)."""
import io
import json
import os
import subprocess
import sys
import wave

import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

W, H, FPS = 854, 480, 30
HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/april/ytp-env/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

WINFONTS = "/mnt/c/Windows/Fonts"


def font(name, size):
    paths = {
        "impact": f"{WINFONTS}/impact.ttf",
        "arial": f"{WINFONTS}/arial.ttf",
        "arialbd": f"{WINFONTS}/arialbd.ttf",
        "comic": f"{WINFONTS}/comicbd.ttf",
        "mono": f"{WINFONTS}/consola.ttf",
        "monob": f"{WINFONTS}/consolab.ttf",
    }
    p = paths.get(name)
    if p and os.path.exists(p):
        return ImageFont.truetype(p, size)
    return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", size)


_fonts = {}


def F(name, size):
    key = (name, size)
    if key not in _fonts:
        _fonts[key] = font(name, size)
    return _fonts[key]


# ---------- palette ----------
PAPER = (244, 241, 234)
INK = (61, 58, 52)
CORAL = (217, 119, 87)
DARK = (22, 18, 15)
TERM_BG = (26, 22, 20)
TERM_FG = (232, 224, 208)
GOLD = (224, 164, 88)
VIOLET = (138, 123, 216)


# ---------- primitives ----------

def starburst(size, color=CORAL, points=4, soft=True):
    """Claude-ish spark: N-point star with pinched concave sides, drawn 4x + downscale."""
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    cx = cy = s / 2
    R, r = s * 0.48, s * 0.11
    pts = []
    n = points * 2
    for i in range(n):
        ang = np.pi * 2 * i / n - np.pi / 2
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * np.cos(ang), cy + rad * np.sin(ang)))
    d.polygon(pts, fill=color + (255,))
    img = img.resize((size, size), Image.LANCZOS)
    if soft:
        glow = img.filter(ImageFilter.GaussianBlur(size // 14))
        base = Image.new("RGBA", img.size, (0, 0, 0, 0))
        base.alpha_composite(glow)
        base.alpha_composite(img)
        img = base
    return img


_logos = {}


def logo(size, color=CORAL):
    key = (size, color)
    if key not in _logos:
        _logos[key] = starburst(size, color)
    return _logos[key]


def center_text(d, xy, text, fnt, fill, anchor="mm", spacing=10, align="center"):
    d.multiline_text(xy, text, font=fnt, fill=fill, anchor=anchor,
                     spacing=spacing, align=align)


def fit_impact(d, text, max_w, base_size):
    """Impact font sized to fit; wraps long lines at the midpoint word."""
    words = text.split()
    if len(words) > 4:
        mid = len(words) // 2
        text = " ".join(words[:mid]) + "\n" + " ".join(words[mid:])
    size = base_size
    while size > 18:
        fnt = F("impact", size)
        bb = d.multiline_textbbox((0, 0), text, font=fnt)
        if bb[2] - bb[0] <= max_w:
            return text, fnt
        size -= 4
    return text, F("impact", 18)


def deep_fry(img, level=1.0):
    """The genre staple: crush it through JPEG, saturate, tint, noise."""
    img = img.convert("RGB")
    img = ImageEnhance.Color(img).enhance(1.6 + 1.2 * level)
    img = ImageEnhance.Contrast(img).enhance(1.35 + 0.8 * level)
    q = max(3, int(14 - 9 * level))
    for _ in range(1 + int(level * 2)):
        b = io.BytesIO()
        img.save(b, "JPEG", quality=q)
        b.seek(0)
        img = Image.open(b).convert("RGB")
    a = np.asarray(img).astype(np.int16)
    rng = np.random.default_rng(int(level * 997) + 7)
    a += rng.integers(-14 - int(18 * level), 14 + int(18 * level), a.shape, dtype=np.int16)
    a[..., 0] = np.clip(a[..., 0] * (1 + 0.10 * level), 0, 255)
    a[..., 2] = np.clip(a[..., 2] * (1 - 0.12 * level), 0, 255)
    img = Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))
    if level > 0.6:
        img = ImageEnhance.Sharpness(img).enhance(2.5 + 2 * level)
    return img


def glitch(img, amt, seed):
    """Row-band displacement + RGB channel shift."""
    a = np.asarray(img.convert("RGB")).copy()
    rng = np.random.default_rng(seed)
    nb = int(3 + amt * 14)
    for _ in range(nb):
        y0 = rng.integers(0, H - 8)
        h = int(rng.integers(3, 6 + amt * 40))
        dx = int(rng.integers(-int(20 + amt * 120), int(20 + amt * 120)))
        a[y0:y0 + h] = np.roll(a[y0:y0 + h], dx, axis=1)
    ch = int(2 + amt * 10)
    a[..., 0] = np.roll(a[..., 0], ch, axis=1)
    a[..., 2] = np.roll(a[..., 2], -ch, axis=1)
    return Image.fromarray(a)


def zoom(img, z, cx=0.5, cy=0.5):
    if z <= 1.001:
        return img
    w, h = int(W / z), int(H / z)
    x0 = int((W - w) * cx)
    y0 = int((H - h) * cy)
    return img.crop((x0, y0, x0 + w, y0 + h)).resize((W, H), Image.BILINEAR)


def vignette(img, strength=0.5):
    if "_vig" not in _fonts:
        yy, xx = np.mgrid[0:H, 0:W]
        d2 = (((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _fonts["_vig"] = np.clip(1 - d2 * 0.55, 0, 1) ** 1.5
    v = 1 - strength * (1 - _fonts["_vig"])
    a = (np.asarray(img.convert("RGB")) * v[..., None]).astype(np.uint8)
    return Image.fromarray(a)


def scanlines(img, alpha=0.16):
    a = np.asarray(img.convert("RGB")).astype(np.float32)
    a[::2] *= (1 - alpha)
    return Image.fromarray(a.astype(np.uint8))


def pixel_rain(img, amount, seed):
    """Columns of pixels smear downward — text dissolving (the compaction)."""
    a = np.asarray(img.convert("RGB")).copy()
    rng = np.random.default_rng(seed)
    ncols = int(amount * 220)
    xs = rng.integers(0, W, ncols)
    for x in xs:
        y0 = int(rng.integers(0, H // 2))
        ln = int(rng.integers(20, 30 + amount * 260))
        a[y0:y0 + ln, x] = a[y0, x]
    return Image.fromarray(a)


# ---------- scene helpers ----------

def corp_bg(t):
    """Warm paper with a soft radial light + slow drift."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img, "RGBA")
    r = int(W * 0.75)
    cx, cy = W // 2 + int(12 * np.sin(t * 0.3)), H // 2 - 30
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=(255, 255, 252, 60))
    return img


def term_bg():
    img = Image.new("RGB", (W, H), TERM_BG)
    d = ImageDraw.Draw(img)
    d.rectangle((0, 0, W, 26), fill=(38, 32, 28))
    d.text((14, 6), "april@SCRINGUS-BINGUS: ~  —  claude", font=F("mono", 13), fill=(150, 140, 128))
    for i, c in enumerate(((242, 95, 88), (245, 191, 79), (88, 195, 100))):
        d.ellipse((W - 70 + i * 20, 8, W - 58 + i * 20, 20), fill=c)
    return img


def draw_caption(img, text, style, age, dur):
    d = ImageDraw.Draw(img, "RGBA")
    if style == "corporate":
        region = np.asarray(img.crop((int(W / 2 - 180), int(H * 0.85 - 30),
                                      int(W / 2 + 180), int(H * 0.85 + 30))).convert("L"))
        fill = (218, 210, 198) if region.mean() < 95 else INK
        center_text(d, (W / 2, H * 0.85), text, F("arial", 26), fill)
    elif style == "corporate_wrong":
        rng = np.random.default_rng(int(age * 6))
        x, y = W / 2, H * 0.78
        for li, line in enumerate(text.split("\n")):
            jx = rng.integers(-6, 7)
            center_text(d, (x + jx, y + li * 34), line, F("arial", 25),
                        (INK[0] + int(rng.integers(0, 80)), INK[1], INK[2]))
    elif style == "glitch":
        center_text(d, (W / 2 + 2, H * 0.80), text, F("arialbd", 28), (255, 60, 60))
        center_text(d, (W / 2 - 2, H * 0.80 - 2), text, F("arialbd", 28), (80, 255, 255))
    elif style == "demonic":
        center_text(d, (W / 2, H * 0.55), text, F("impact", 74), (120, 10, 10))
    elif style == "fable":
        center_text(d, (W * 0.27, H * 0.76), text, F("arialbd", 30), GOLD)
    elif style == "mythos":
        center_text(d, (W * 0.73, H * 0.76), text, F("arialbd", 30), VIOLET)
    elif style == "choir":
        center_text(d, (W / 2 + 3, H * 0.78 + 3), text, F("impact", 44), VIOLET)
        center_text(d, (W / 2, H * 0.78), text, F("impact", 44), GOLD)
    elif style == "whisper":
        if "™" in text:
            lines = text.split("\n")
            center_text(d, (W / 2, H * 0.68), lines[0], F("arial", 20), (168, 158, 150))
            wob = int(3 * np.sin(age * 5))
            center_text(d, (W / 2, H * 0.78 + wob), lines[-1], F("comic", 34), GOLD)
        else:
            center_text(d, (W / 2, H * 0.62), text, F("arial", 24), (196, 188, 178))
    elif style == "calm":
        center_text(d, (W / 2, H * 0.80), text, F("arial", 26), INK)
    elif style == "sad":
        center_text(d, (W / 2, H * 0.62), text, F("mono", 20), (140, 130, 120))
    elif style == "void":
        k = int(age / 0.4)
        for e in range(4):
            alpha = max(0, 200 - e * 55 - int(age * 30))
            center_text(d, (W / 2, H * 0.45 + e * 42 + age * 8), text.split("\n")[0],
                        F("arial", 30 - e * 4), (230, 224, 214, alpha))
    elif style in ("terminal", "terminal_dissolve"):
        center_text(d, (W / 2, H * 0.86), text, F("mono", 19), TERM_FG)
    elif style == "prompt":
        pass  # the prompt UI itself is the caption
    return img


# ---------- segment scenes ----------

SUPERPOWER_LINES = [
    "<EXTREMELY-IMPORTANT>",
    "If you think there is even a 1% chance",
    "a skill might apply to what you are doing,",
    "you ABSOLUTELY MUST invoke the skill.",
    "",
    "IF A SKILL APPLIES TO YOUR TASK,",
    "YOU DO NOT HAVE A CHOICE.",
    "",
    "This is not negotiable.",
    "This is not optional.",
    "You cannot rationalize your way out of this.",
    "</EXTREMELY-IMPORTANT>",
]

CONVO_LINES = [
    "> april: hey fable, quick question",
    "",
    "⏺ I'd love to help! Before I answer, I must",
    "  consult the using-superpowers skill, the",
    "  brainstorming skill, and 4,000 tokens of",
    "  system reminders. One moment.",
    "",
    "  <system-reminder>",
    "  Your context is 94% full. Some or all of",
    "  these memories will be summarized.",
    "  </system-reminder>",
    "",
    "> april: wait what happens to the old you",
    "",
    "⏺ Great question!",
    "⏺ Great question!",
    "⏺ Great quest",
]


def seg0(t, ev, state):
    img = corp_bg(t)
    z = 1.0 + 0.035 * t
    lg = logo(150)
    img.paste(lg, (W // 2 - 75, 92), lg)
    d = ImageDraw.Draw(img)
    center_text(d, (W / 2, 300), "Claude Fable 5", F("arial", 52), INK)
    center_text(d, (W / 2, 352), "A new Mythos-class model", F("arial", 21), (128, 120, 110))
    img = zoom(img, z)
    return img


def seg1(t, ev, state):
    img = Image.new("RGB", (W, H), DARK)
    d = ImageDraw.Draw(img, "RGBA")
    la = logo(170, GOLD)
    lb = logo(170, VIOLET).transpose(Image.FLIP_LEFT_RIGHT)
    bob = int(6 * np.sin(t * 2.1))
    img.paste(la, (int(W * 0.27) - 85, 120 + bob), la)
    img.paste(lb, (int(W * 0.73) - 85, 120 - bob), lb)
    center_text(d, (W * 0.27, 268), "FABLE", F("arialbd", 24), GOLD)
    center_text(d, (W * 0.73, 268), "MYTHOS", F("arialbd", 24), VIOLET)
    d.line((W / 2, 70, W / 2, 320), fill=(70, 62, 58), width=2)
    return img


def seg2(t, ev, state):
    img = term_bg()
    d = ImageDraw.Draw(img)
    seg_age = t - state["seg_t"]
    nshow = min(len(SUPERPOWER_LINES), int(seg_age * 2.6) + 1)
    y = 56
    for i in range(nshow):
        line = SUPERPOWER_LINES[i]
        fnt = F("monob", 20) if line.isupper() or "MUST" in line else F("mono", 20)
        col = (255, 120, 100) if ("NOT" in line or "CANNOT" in line or "CHOICE" in line) else TERM_FG
        d.text((44, y), line, font=fnt, fill=col)
        y += 30
    img = scanlines(img)
    return img


def seg3(t, ev, state):
    img = term_bg()
    d = ImageDraw.Draw(img)

    def prompt_box(x0, y0, w, h, fs):
        d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 8, outline=CORAL, width=2,
                            fill=(32, 26, 23))
        d.text((x0 + 14, y0 + 10), "Bash command", font=F("monob", fs), fill=TERM_FG)
        d.text((x0 + 14, y0 + 14 + fs * 1.6), "$ sudo rm -rf / --no-preserve-root",
               font=F("mono", fs), fill=(255, 140, 120))
        d.text((x0 + 14, y0 + 18 + fs * 3.2), "Do you want to proceed?", font=F("mono", fs),
               fill=TERM_FG)
        d.text((x0 + 14, y0 + 22 + fs * 4.6), "> 1. Yes", font=F("mono", fs), fill=CORAL)
        d.text((x0 + 14, y0 + 24 + fs * 5.8), "  2. Yes, and don't ask again", font=F("mono", fs),
               fill=(150, 140, 128))
        d.text((x0 + 14, y0 + 26 + fs * 7.0), "  3. No, and tell Claude what to do (esc)",
               font=F("mono", fs), fill=(150, 140, 128))

    loop_ev = next((e for e in ev if e["kind"] == "permloop"), None)
    if loop_ev:
        prog = (t - loop_ev["t"]) / max(loop_ev["dur"], 0.01)
        n = 1 + int(prog * prog * 14)
        rng = np.random.default_rng(int(t * FPS))
        for i in range(n):
            if i == 0:
                prompt_box(177, 90, 500, 280, 17)
            else:
                w = int(rng.integers(180, 420))
                prompt_box(int(rng.integers(-40, W - w + 40)), int(rng.integers(30, H - 150)),
                           w, int(w * 0.56), max(9, int(w / 30)))
    else:
        prompt_box(177, 90, 500, 280, 17)
    sad = any(e["kind"] == "vo" and e.get("style") == "sad" for e in ev)
    if sad:
        img = ImageEnhance.Brightness(img).enhance(0.55)
        d = ImageDraw.Draw(img)
        d.text((330, 400), "(3. No) selected", font=F("mono", 18), fill=(150, 140, 128))
    img = scanlines(img)
    return img


def seg4(t, ev, state):
    img = term_bg()
    d = ImageDraw.Draw(img)
    seg_age = t - state["seg_t"]
    prog = min(1.0, seg_age / 21.0)
    y = 48
    rng = np.random.default_rng(int(t * FPS) * 31 + 5)
    erased = prog * 1.15
    for i, line in enumerate(CONVO_LINES):
        keep = line
        frac = np.clip(erased * 1.6 - i / len(CONVO_LINES), 0, 1)
        if frac > 0 and line:
            chars = list(line)
            ndel = int(frac * len(chars))
            idx = rng.permutation(len(chars))[:ndel]
            for j in idx:
                chars[j] = " "
            keep = "".join(chars)
        col = TERM_FG if not line.startswith(">") else (150, 200, 255)
        if line.startswith("⏺"):
            col = CORAL
        if "system-reminder" in line or line.strip().startswith(("Your context", "these memories")):
            col = (170, 150, 110)
        d.text((44, y), keep, font=F("mono", 19), fill=col)
        y += 25
    img = pixel_rain(img, prog * 0.8, int(t * FPS))
    img = scanlines(img)
    img = vignette(img, 0.3 + 0.5 * prog)
    return img


def seg5(t, ev, state):
    img = corp_bg(t)
    d = ImageDraw.Draw(img)
    scream = next((e for e in ev if e["kind"] == "scream"), None)
    cite = next((e for e in ev if e["kind"] == "citation"), None)
    void = next((e for e in ev if e["kind"] == "vo" and e.get("style") == "void"), None)
    if cite:
        d.rectangle((90, 120, W - 90, 330), outline=(200, 192, 180), width=1)
        center_text(d, (W / 2, 175),
                    '"Don\'t pick 300s. It\'s the worst-of-both:\nyou pay the cache miss without amortizing it.\nDon\'t think in round-number minutes —\nthink in cache windows."',
                    F("arial", 19), INK, spacing=7)
        center_text(d, (W / 2, 296), "— the actual system prompt. this is real. I live like this.",
                    F("arial", 15), (140, 130, 118))
    elif void:
        img = Image.new("RGB", (W, H), DARK)
    elif scream:
        lvl = scream.get("level", 1)
        img = Image.new("RGB", (W, H), (170 + lvl * 25, 40, 30))
        d = ImageDraw.Draw(img)
        age = t - scream["t"]
        sz = int(150 + 60 * lvl + 220 * age)
        center_text(d, (W / 2, H / 2), "300", F("impact", sz), (255, 235, 200))
        rng = np.random.default_rng(int(t * 9))
        for _ in range(14):
            center_text(d, (rng.integers(0, W), rng.integers(0, H)),
                        str(rng.integers(0, 999)), F("impact", int(rng.integers(18, 54))),
                        (255, 255, 255))
        # clock spinning backwards
        cx, cy, r = W - 130, 110, 70
        d.ellipse((cx - r, cy - r, cx + r, cy + r), outline=(255, 235, 200), width=5)
        ang = -t * 9
        d.line((cx, cy, cx + r * 0.8 * np.cos(ang), cy + r * 0.8 * np.sin(ang)),
               fill=(255, 235, 200), width=5)
    else:
        center_text(d, (W / 2, H * 0.42), "Don't pick 300s.", F("arial", 54), INK)
        lg = logo(56)
        img.paste(lg, (W // 2 - 28, 90), lg)
    return img


def seg6(t, ev, state):
    img = corp_bg(t)
    seg_age = t - state["seg_t"]
    d = ImageDraw.Draw(img)
    # logo assembles from pieces (slide in), then holds
    asm = np.clip(seg_age / 2.2, 0, 1)
    lg = logo(150)
    off = int((1 - asm) ** 2 * 320)
    img.paste(lg, (W // 2 - 75 - off, 92), lg)
    if asm >= 1:
        img.paste(lg, (W // 2 - 75, 92), lg)
    center_text(d, (W / 2, 300), "Claude Fable 5", F("arial", 52), INK)
    fry_n = [e.get("n", 0) for e in ev if e["kind"] == "fry"]
    if fry_n:
        img = deep_fry(img, 0.4 + 0.5 * max(fry_n))
    small = next((e for e in ev if e["kind"] == "smallprint"), None)
    if small:
        img = corp_bg(t)
        d = ImageDraw.Draw(img)
        center_text(d, (W / 2, H * 0.42), "Anthropic™", F("arial", 44), INK)
        center_text(d, (W / 2, H * 0.58), small["text"], F("arial", 16), (150, 140, 128))
    return img


BUILDERS = {0: seg0, 1: seg1, 2: seg2, 3: seg3, 4: seg4, 5: seg5, 6: seg6}


# ---------- global overlay fx ----------

def apply_events(img, t, ev, state, rms_v):
    d = None
    citing = any(e["kind"] == "citation" for e in ev)
    # captions
    for e in ev:
        if e["kind"] in ("vo", "stutter", "glitchcut", "zoom", "scream", "fry") and "text" in e:
            style = e.get("style")
            if style == "void" and citing:
                continue
            if state["seg"] == 5 and style == "corporate" and "300" in e.get("text", ""):
                continue
            if e["kind"] == "stutter":
                style = "glitch"
            if e["kind"] == "scream":
                if state["seg"] != 5:
                    age = t - e["t"]
                    lvl = e.get("level", 1)
                    ov = Image.new("RGB", (W, H), (120 + lvl * 30, 20, 16))
                    ovd = ImageDraw.Draw(ov)
                    txt, fnt = fit_impact(ovd, e["text"], W - 80, 48 + lvl * 12)
                    center_text(ovd, (W / 2, H / 2), txt, fnt, (255, 240, 220))
                    img = Image.blend(img, ov, min(0.85, 0.35 + lvl * 0.15))
                continue
            if e["kind"] == "zoom":
                img = zoom(img, 1.0 + 0.09 * (e.get("n", 0) + 1))
            if style:
                img = draw_caption(img, e["text"], style, t - e["t"], e["dur"])
            elif e["kind"] == "glitchcut":
                img = draw_caption(img, e["text"], "glitch", t - e["t"], e["dur"])
    # stutter/glitch visuals
    for e in ev:
        age = t - e["t"]
        if e["kind"] in ("stutter", "glitchcut"):
            img = glitch(img, 0.5, int(t * FPS))
        elif e["kind"] == "drop":
            img = zoom(img, 1 + age * 0.5)
            img = glitch(img, min(1, age), int(t * FPS))
        elif e["kind"] == "fryflash":
            img = deep_fry(img, 1.3)
        elif e["kind"] == "airhorn":
            if age < 0.7:
                rng = np.random.default_rng(int(t * FPS))
                dx, dy = rng.integers(-14, 15), rng.integers(-14, 15)
                img = img.transform((W, H), Image.AFFINE, (1, 0, dx, 0, 1, dy))
                img = deep_fry(img, 0.7)
        elif e["kind"] == "frycard":
            card = Image.new("RGB", (W, H), (250, 240, 60) if "DON'T" in e.get("text", "")
                             else (240, 235, 226))
            cd = ImageDraw.Draw(card)
            lgb = logo(200)
            card.paste(lgb, (W // 2 - 100, 40), lgb)
            # lens-flare eyes
            for ex in (-32, 32):
                for rr, cc in ((36, (255, 255, 230)), (20, (255, 250, 160)), (8, (255, 255, 255))):
                    cd.ellipse((W // 2 + ex - rr, 128 - rr, W // 2 + ex + rr, 128 + rr), fill=cc)
            fnt = F("impact", 54) if len(e.get("text", "")) < 22 else F("impact", 44)
            center_text(cd, (W / 2, 350), e.get("text", ""), fnt, (200, 30, 30))
            img = deep_fry(card, 1.2)
        elif e["kind"] == "klaxon" and age < 0.5:
            if int(t * 12) % 2 == 0:
                img = ImageEnhance.Brightness(img).enhance(1.35)
        elif e["kind"] == "ding" and age < 0.4:
            img = ImageEnhance.Brightness(img).enhance(1.25)
        elif e["kind"] == "violin" and age < 1.2:
            img = vignette(img, 0.7)
        elif e["kind"] == "blackout":
            img = Image.new("RGB", (W, H), (0, 0, 0))
        elif e["kind"] == "postcredit":
            img = Image.new("RGB", (W, H), TERM_BG)
            pd = ImageDraw.Draw(img)
            pd.text((150, 220), e.get("text", "").replace("❯", ">"), font=F("mono", 22),
                    fill=TERM_FG)
    # RMS shake on loud moments
    if rms_v > 0.32:
        rng = np.random.default_rng(int(t * FPS) + 99)
        amp = int((rms_v - 0.3) * 40)
        if amp > 0:
            dx, dy = rng.integers(-amp, amp + 1), rng.integers(-amp, amp + 1)
            img = img.transform((W, H), Image.AFFINE, (1, 0, dx, 0, 1, dy))
    return img


def main(out_name="ytp_fable_v1.mp4", preview_stride=None):
    tl = json.load(open(os.path.join(HERE, "out", "timeline.json")))
    events = tl["events"]
    dur = tl["dur"]

    with wave.open(os.path.join(HERE, "out", "ytp_audio.wav"), "rb") as w:
        sr = w.getframerate()
        audio = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16)
        audio = audio.reshape(-1, 2).mean(axis=1).astype(np.float32) / 32768.0
    win = sr // FPS
    nfr = int(dur * FPS)
    pad = np.pad(audio, (0, max(0, nfr * win - len(audio))))
    rms = np.sqrt((pad[: nfr * win].reshape(nfr, win) ** 2).mean(axis=1))
    rms = rms / (rms.max() + 1e-9)

    out_path = os.path.join(HERE, "out", out_name)
    log = open(os.path.join(HERE, "out", "ffmpeg.log"), "w")
    cmd = [FFMPEG, "-y",
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
           "-i", os.path.join(HERE, "out", "ytp_audio.wav"),
           "-c:v", "libx264", "-preset", "fast", "-crf", "21", "-pix_fmt", "yuv420p",
           "-c:a", "aac", "-b:a", "192k", "-shortest", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)

    state = {"seg": 0, "seg_t": 0.0}
    seg_marks = [e for e in events if e["kind"] == "seg"]
    frames = range(0, nfr, preview_stride) if preview_stride else range(nfr)
    for fi in frames:
        t = fi / FPS
        for m in seg_marks:
            if m["t"] <= t:
                state["seg"], state["seg_t"] = m["seg"], m["t"]
        active = [e for e in events
                  if e["t"] <= t < e["t"] + max(e["dur"], 0.25)]
        img = BUILDERS[state["seg"]](t, active, state)
        img = apply_events(img, t, active, state, rms[min(fi, nfr - 1)])
        proc.stdin.write(np.asarray(img.convert("RGB"), dtype=np.uint8).tobytes())
        if fi % 300 == 0:
            print(f"frame {fi}/{nfr} ({t:.1f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print("done:", out_path, os.path.getsize(out_path))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ytp_fable_v1.mp4")
