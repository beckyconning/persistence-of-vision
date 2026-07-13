"""Choreograph + render SUPER CLAUDIO BROS. 5. Frames -> ffmpeg pipe (+2D overlays)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFont

import claudio
import world
from beats import *  # noqa: F401,F403
from engine import Camera, Node, render

W, H = 854, 480
HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/april/ytp-env/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"
FONT = "/mnt/c/Windows/Fonts/consolab.ttf"


def smooth(a, b, t):
    t = np.clip(t, 0, 1)
    t = t * t * (3 - 2 * t)
    return a + (b - a) * t


def lerp(a, b, t):
    return a + (b - a) * np.clip(t, 0, 1)


def arc(p):
    """0..1 -> parabolic jump arc 0..1..0"""
    return 4 * p * (1 - p)


# ---------------- build the scene ----------------

def build_scene():
    root = Node("scene")
    root.add(world.ground())
    for hx, hz, hr, hh in ((-6, 16, 8, 0.5), (14, 20, 10, 0.45), (30, 17, 7, 0.5),
                           (48, 22, 11, 0.4), (-14, 12, 5, 0.6)):
        root.add(world.hill(hx, hz, hr, hh))
    clouds = []
    for cx, cy, cz, cs in ((-4, 8.5, 12, 1.0), (10, 9.6, 16, 1.3), (24, 8.2, 14, 0.9),
                           (38, 9.2, 15, 1.2), (50, 8.6, 13, 1.0)):
        cl = world.cloud(cx, cy, cz, cs)
        clouds.append(cl)
        root.add(cl)
    for bx, bz, bs in ((3.2, 2.8, 1.0), (13.5, 3.4, 1.2), (26, 2.6, 0.9), (37.5, 3.0, 1.1)):
        root.add(world.bush(bx, bz, bs))

    S = {}
    S["qblock"] = root.add(world.qblock(X_BLOCK, Y_BLOCK))
    root.add(world.brick(X_BLOCK - 1.3, Y_BLOCK))
    root.add(world.brick(X_BLOCK + 1.3, Y_BLOCK))
    S["pipe1"] = root.add(world.pipe(X_PIPE1))
    S["pipe2"] = root.add(world.pipe(X_PIPE2))
    S["flagpole"] = root.add(world.flagpole(X_FLAG))
    S["flag"] = S["flagpole"].find("flag")
    S["panel"] = root.add(world.panel(X_BLOCK + 0.4, 5.55))
    S["coin"] = root.add(world.coin())
    S["bug"] = root.add(world.bug())
    S["bug"].visible = False
    S["bug_flat"] = root.add(world.bug_flat())
    S["sign"] = root.add(world.bugfixed_sign())
    S["shadow"] = root.add(world.shadow_blob())
    cl, j = claudio.build()
    root.add(cl)
    S["claudio"], S["j"], S["clouds"] = cl, j, clouds
    return root, S


# ---------------- choreography ----------------

def claudio_state(t, j, cl):
    """Set Claudio's root pos/rot + pose for time t. Returns dict of extras."""
    ex = {}
    FACE_R, FACE_CAM = -np.pi / 2, 0.0

    if t < TITLE_END:
        cl.pos[:] = (X_START, 0, 0)
        cl.rot[1] = FACE_CAM
        if 2.4 < t < 5.2:
            claudio.wave(j, t, amt=min(1, (t - 2.4) / 0.4) * min(1, (5.2 - t) / 0.4))
        else:
            claudio.idle(j, t)
    elif t < RUN1[1]:  # walk-off then run
        p = (t - RUN1[0]) / (RUN1[1] - RUN1[0]) if t >= RUN1[0] else 0
        cl.pos[0] = lerp(X_START, X_BLOCK, p)
        cl.rot[1] = FACE_R
        claudio.run(j, t) if t >= RUN1[0] else claudio.idle(j, t)
    elif t < JUMP1:  # brake under block, look up
        cl.pos[0] = X_BLOCK
        cl.rot[1] = FACE_R
        claudio.idle(j, t)
        claudio.look_up(j, smooth(0, 1, (t - RUN1[1]) / 0.4))
    elif t < PANEL_ON:  # the jump + bonk
        cl.pos[0] = X_BLOCK
        cl.rot[1] = FACE_R
        p = (t - JUMP1) / 0.75
        cl.pos[1] = 1.30 * arc(p)
        claudio.jump(j, tuck=min(1, p * 3))
    elif t < PANEL_OFF:  # polite wait
        cl.pos[:] = (X_BLOCK, 0, 0)
        cl.rot[1] = FACE_CAM
        claudio.droop(j, t, amt=smooth(0, 1, (t - PANEL_ON) / 0.6))
        claudio.look_up(j, 0.9)
        if t > DING:
            claudio.idle(j, t)
            claudio.look_up(j, 0.7)
            cl.pos[1] = 0.35 * arc((t - DING) / 0.4) if t < DING + 0.4 else 0
    elif t < BUG_ENTER:  # coin joy
        cl.pos[:] = (X_BLOCK, 0, 0)
        cl.rot[1] = FACE_CAM
        if HOP < t < HOP + 0.5:
            cl.pos[1] = 0.5 * arc((t - HOP) / 0.5)
            claudio.victory(j, t)
        else:
            claudio.idle(j, t)
            claudio.look_up(j, 0.5 if t < COIN_END else 0.0)
    elif t < RUN2[0]:  # notice bug
        cl.pos[:] = (X_BLOCK, 0, 0)
        cl.rot[1] = FACE_R
        claudio.idle(j, t)
        j["head"].rot[1] = -0.15
    elif t < JUMP2:  # run at bug
        p = (t - RUN2[0]) / (RUN2[1] - RUN2[0])
        cl.pos[0] = lerp(X_BLOCK, 11.4, min(1, p))
        cl.rot[1] = FACE_R
        claudio.run(j, t)
    elif t < STOMP:  # leap
        p = (t - JUMP2) / (STOMP - JUMP2)
        cl.pos[0] = lerp(11.4, X_STOMP, p)
        cl.pos[1] = 1.5 * arc(p * 0.85)  # land ON the bug (still high at p=1)
        cl.rot[1] = FACE_R
        claudio.stomp(j, min(1, p * 2.5))
    elif t < SIGN_OFF:  # on the pancake
        cl.pos[0] = X_STOMP
        cl.rot[1] = FACE_CAM
        if t < STOMP + 0.35:
            cl.pos[1] = 0.24 + 0.25 * arc((t - STOMP) / 0.35)  # recoil bouncelet
        elif t < STOMP + 0.8:
            cl.pos[1] = 0.24
            claudio.stomp(j, 1)
        else:
            cl.pos[1] = 0.24
            claudio.victory(j, t) if t < SIGN_OFF - 0.6 else claudio.idle(j, t)
    elif t < RUN3[1]:  # run to pipe
        p = (t - RUN3[0]) / (RUN3[1] - RUN3[0]) if t >= RUN3[0] else 0
        cl.pos[0] = lerp(X_STOMP, X_PIPE1 - 1.5, p)
        cl.pos[1] = max(0.0, 0.24 * (1 - p * 6))  # step off pancake
        cl.rot[1] = FACE_R
        claudio.run(j, t)
    elif t < PIPE_TOP:  # hop onto pipe
        p = (t - PIPE_JUMP) / (PIPE_TOP - PIPE_JUMP)
        cl.pos[0] = lerp(X_PIPE1 - 1.5, X_PIPE1, p)
        cl.pos[1] = 2.95 * smooth(0, 1, p) + 0.9 * arc(p)
        cl.rot[1] = FACE_R
        claudio.jump(j, 1)
    elif t < PIPE_DOWN[0]:  # stand on pipe, face camera
        cl.pos[:] = (X_PIPE1, 2.95, 0)
        cl.rot[1] = FACE_CAM
        claudio.idle(j, t)
    elif t < DARK[1]:  # descend
        p = (t - PIPE_DOWN[0]) / (PIPE_DOWN[1] - PIPE_DOWN[0])
        cl.pos[:] = (X_PIPE1, lerp(2.95, 0.2, min(1, p)), 0)
        cl.rot[1] = FACE_CAM
        claudio.idle(j, t)
        j["shoulderL"].rot[2] = -0.4
        j["shoulderR"].rot[2] = 0.4
    elif t < POP_OUT[1]:  # rise from pipe2
        p = (t - POP_OUT[0]) / (POP_OUT[1] - POP_OUT[0])
        cl.pos[:] = (X_PIPE2, lerp(0.2, 2.95, smooth(0, 1, p)), 0)
        cl.rot[1] = FACE_CAM
        claudio.idle(j, t)
    elif t < RUN4[0]:  # hop down
        p = (t - POP_OUT[1]) / (RUN4[0] - POP_OUT[1])
        cl.pos[0] = lerp(X_PIPE2, X_PIPE2 + 1.4, p)
        cl.pos[1] = 2.95 * (1 - smooth(0, 1, p)) + 0.5 * arc(p)
        cl.rot[1] = FACE_R
        claudio.jump(j, 1 - p * 0.7)
    elif t < RUN4[1]:  # final run
        p = (t - RUN4[0]) / (RUN4[1] - RUN4[0])
        cl.pos[0] = lerp(X_PIPE2 + 1.4, 40.4, p)
        cl.pos[1] = 0
        cl.rot[1] = FACE_R
        claudio.run(j, t)
    elif t < FLAG_GRAB:  # leap to pole
        p = (t - FLAG_JUMP) / (FLAG_GRAB - FLAG_JUMP)
        cl.pos[0] = lerp(40.4, X_FLAG - 0.42, p)
        cl.pos[1] = lerp(0, 4.6, smooth(0, 1, p)) + 0.6 * arc(p)
        cl.rot[1] = FACE_R
        claudio.jump(j, 1)
    elif t < SLIDE[1]:  # slide down
        p = (t - SLIDE[0]) / (SLIDE[1] - SLIDE[0])
        cl.pos[0] = X_FLAG - 0.42
        cl.pos[1] = lerp(4.6, 0.05, smooth(0, 1, p))
        cl.rot[1] = FACE_R
        claudio.reset(j)
        j["shoulderR"].rot[2] = 2.9
        j["shoulderL"].rot[2] = -0.3
        j["hipL"].rot[0] = 0.25
        j["hipR"].rot[0] = 0.15
    elif t < END_CARD:  # victory!
        p = smooth(0, 1, (t - SLIDE[1]) / 0.8)
        cl.pos[0] = lerp(X_FLAG - 0.42, X_VICTORY, p)
        cl.pos[1] = 0
        cl.rot[1] = FACE_CAM
        claudio.victory(j, t)
    else:
        cl.pos[:] = (X_VICTORY, 0, 0)
        cl.rot[1] = FACE_CAM
        claudio.victory(j, t)
    return ex


def scene_state(t, S):
    """Props: block bounce, panel, coin, bug, flag, shadow."""
    # ? block bounce on bonk
    q = S["qblock"]
    if BONK <= t < BONK + 0.3:
        q.pos[1] = Y_BLOCK + 0.5 * arc((t - BONK) / 0.3)
    else:
        q.pos[1] = Y_BLOCK

    # panel
    p = S["panel"]
    p.visible = PANEL_ON <= t < PANEL_OFF
    if p.visible:
        pop = smooth(0.15, 1.0, (t - PANEL_ON) / 0.3)
        p.scale[:] = pop
        p.pos[1] = 5.55 + 0.08 * np.sin(t * 2.2)
        ask, yes = p.find("panel_ask"), p.find("panel_yes")
        ask.visible = t < DING
        yes.visible = t >= DING

    # coin
    c = S["coin"]
    c.visible = COIN_POP <= t < COIN_END
    if c.visible:
        cp = (t - COIN_POP) / (COIN_END - COIN_POP)
        c.pos[:] = (X_BLOCK, Y_BLOCK + 0.85 + 1.5 * arc(cp), 0)
        c.rot[1] = t * 14
        c.scale[:] = 1.0 if cp < 0.8 else max(0.05, 1 - (cp - 0.8) * 5)

    # bug walks in, then pancake
    b, bf = S["bug"], S["bug_flat"]
    b.visible = BUG_ENTER <= t < STOMP
    if b.visible:
        wp = (t - BUG_ENTER) / (STOMP - BUG_ENTER)
        b.pos[:] = (lerp(X_BUG_ENTER, X_STOMP, wp), 0, 0)
        b.rot[1] = np.pi / 2  # face -x (toward Claudio)
        wob = np.sin(t * 16)
        b.pos[1] = 0.03 * abs(wob)
        for i in range(3):
            for s_, nm in ((-1, "L"), (1, "R")):
                leg = b.find(f"leg{i}{nm}")
                leg.rot[0] = 0.5 * wob * (1 if (i + (s_ > 0)) % 2 else -1)
    bf.visible = t >= STOMP
    if bf.visible:
        bf.pos[:] = (X_STOMP, 0, 0)
        sq_ = min(1, (t - STOMP) / 0.12)
        bf.scale[:] = (0.8 + 0.5 * sq_, max(0.25, 1.2 - sq_), 0.8 + 0.5 * sq_)

    # BUG FIXED sign floats up
    sg = S["sign"]
    sg.visible = SIGN_ON <= t < SIGN_OFF
    if sg.visible:
        sp = (t - SIGN_ON) / (SIGN_OFF - SIGN_ON)
        sg.pos[:] = (X_STOMP, 1.6 + 1.3 * smooth(0, 1, sp), -0.5)

    # flag slides with Claudio
    fl = S["flag"]
    if t < SLIDE[0]:
        fl.pos[1] = 8.0
    elif t < SLIDE[1]:
        fl.pos[1] = lerp(8.0, 1.6, smooth(0, 1, (t - SLIDE[0]) / (SLIDE[1] - SLIDE[0])))
    else:
        fl.pos[1] = 1.6

    # clouds drift
    for i, clld in enumerate(S["clouds"]):
        clld.pos[0] += 0.0  # static is fine; drift handled by parallax feel

    # shadow follows Claudio
    cl = S["claudio"]
    S["shadow"].visible = cl.pos[1] < 3.2 and not (DARK[0] < t < POP_OUT[0])
    S["shadow"].pos[:] = (cl.pos[0], 0.035, cl.pos[2])
    s = max(0.45, 1.0 - cl.pos[1] * 0.18)
    S["shadow"].scale[:] = (s, 1, s)


def camera_at(t, S):
    cl = S["claudio"]
    cx = cl.pos[0]
    if t < TITLE_END:
        az = lerp(-0.85, 0.55, smooth(0, 1, t / TITLE_END))
        d = lerp(6.5, 5.2, smooth(0, 1, t / TITLE_END))
        return Camera((X_START + d * np.sin(az), lerp(1.3, 1.9, t / TITLE_END),
                       -d * np.cos(az)), (X_START, 1.15, 0), fov=40)
    if t < JUMP1 - 0.2:
        fx = min(cx + 1.8, X_BLOCK + 0.8)
        return Camera((fx, 3.0, -9.4), (fx, 2.4, 0), fov=46)
    if t < BUG_ENTER:  # block + panel framing (fov is horizontal; pull back for height)
        return Camera((X_BLOCK + 0.6, 3.8, -14.0), (X_BLOCK + 0.6, 3.5, 0), fov=46)
    if t < RUN3[0]:  # bug encounter
        fx = np.clip(cx + 1.6, X_BLOCK + 1.5, X_STOMP + 1.2)
        return Camera((fx, 3.1, -9.4), (fx, 2.2, 0), fov=46)
    if t < DARK[1]:  # pipe 1
        fx = min(cx + 1.6, X_PIPE1 - 0.2)
        return Camera((fx, 3.2, -9.4), (fx, 2.3, 0), fov=46)
    if t < RUN4[0] + 0.8:  # pipe 2 pop-out
        return Camera((X_PIPE2 + 0.8, 3.4, -9.0), (X_PIPE2 + 0.8, 2.6, 0), fov=46)
    if t < FLAG_JUMP:
        fx = min(cx + 1.8, X_FLAG - 3.4)
        return Camera((fx, 3.1, -9.6), (fx, 2.4, 0), fov=46)
    if t < SLIDE[1]:  # the pole, full height
        return Camera((X_FLAG - 2.2, 4.6, -12.6), (X_FLAG - 1.0, 4.4, 0), fov=48)
    if t < END_CARD:  # victory dolly-in
        p = smooth(0, 1, (t - SLIDE[1]) / (END_CARD - SLIDE[1]))
        return Camera((lerp(X_FLAG - 2.4, X_VICTORY + 0.2, p), lerp(3.6, 2.2, p),
                       lerp(-12.0, -8.2, p)), (lerp(X_FLAG - 1, X_VICTORY, p), 2.4, 0), fov=46)
    return Camera((X_VICTORY + 0.2, 2.1, -7.8), (X_VICTORY, 2.2, 0), fov=46)


# ---------------- 2D overlays ----------------

_fonts = {}


def F(size):
    if size not in _fonts:
        _fonts[size] = ImageFont.truetype(FONT, size)
    return _fonts[size]


def px_text(d, xy, s, size=13, fill=(255, 255, 255), outline=(20, 24, 40), anchor="la"):
    x, y = xy
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-2, -2), (2, 2), (-2, 2), (2, -2)):
        d.text((x + dx, y + dy), s, font=F(size), fill=outline, anchor=anchor)
    d.text((x, y), s, font=F(size), fill=fill, anchor=anchor)


def overlays(img, t, S):
    im = Image.fromarray(img)

    # underground dark fade
    if DARK[0] - 0.15 < t < POP_OUT[0] + 0.4:
        if t < DARK[0] + 0.5:
            a = smooth(0, 1, (t - (DARK[0] - 0.15)) / 0.6)
        elif t > POP_OUT[0] - 0.2:
            a = 1 - smooth(0, 1, (t - (POP_OUT[0] - 0.2)) / 0.55)
        else:
            a = 1.0
        im = Image.blend(im, Image.new("RGB", im.size, (4, 4, 12)), float(np.clip(a, 0, 1)))

    d = ImageDraw.Draw(im)

    # title cards
    if t < TITLE_END:
        a = 1.0 if t > 0.8 else t / 0.8
        if t < TITLE_END - 0.6:
            wob = int(3 * np.sin(t * 3.1))
            px_text(d, (W // 2, 74 + wob), "SUPER CLAUDIO BROS. 5", 42,
                    (255, 214, 70), (140, 40, 20), anchor="mm")
            px_text(d, (W // 2, 122), "* THE NEWEST AI BROTHER *", 20,
                    (255, 255, 255), (140, 40, 20), anchor="mm")
            px_text(d, (W // 2, 436), "(not affiliated with anyone. do not ask.)", 14,
                    (235, 235, 235), (60, 30, 20), anchor="mm")

    # HUD
    if TITLE_END <= t < END_CARD:
        tokens = 0 if t < TOKENS_AT else 1
        ctx = max(1024, int(200000 - (t - TITLE_END) * 3600))
        hud = f"CLAUDIO*1   TOKENS x{tokens}   WORLD 1-1   CONTEXT {ctx}"
        px_text(d, (26, 12), hud, 17, (255, 255, 255))

    # fireworks (2D sprite bursts)
    for fi, ft in enumerate(FIREWORKS):
        age = t - ft
        if 0 < age < 1.1:
            cxs = [W * 0.3, W * 0.62, W * 0.46][fi]
            cys = [H * 0.22, H * 0.16, H * 0.3][fi]
            cols = [(255, 180, 80), (140, 220, 255), (255, 120, 140)][fi]
            rng = np.random.default_rng(fi * 77)
            n = 26
            angs = rng.uniform(0, 2 * np.pi, n)
            spd = rng.uniform(0.6, 1.0, n)
            r = 130 * (age ** 0.55)
            fade = max(0, 1 - age / 1.1)
            for aa, ss in zip(angs, spd):
                x = cxs + r * ss * np.cos(aa)
                y = cys + r * ss * np.sin(aa) + 40 * age * age
                sz = max(1, int(4 * fade))
                col = tuple(int(cc * fade + 255 * (1 - fade) * 0.2) for cc in cols)
                d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=col)

    # TASK COMPLETE
    if TASK_TEXT < t < IRIS[0]:
        blink = int((t - TASK_TEXT) * 3) % 2 == 0 or t > TASK_TEXT + 2
        if blink:
            px_text(d, (W // 2, 96), "TASK COMPLETE!", 40, (255, 240, 120),
                    (120, 60, 20), anchor="mm")

    # iris out
    if t >= IRIS[0]:
        p = smooth(0, 1, (t - IRIS[0]) / (IRIS[1] - IRIS[0]))
        # project Claudio head to screen for iris center
        cl = S["claudio"]
        cam = camera_at(t, S)
        Vm = cam.view()
        hp = np.array([cl.pos[0], 2.2, 0.0]) - cam.pos
        vc = Vm @ hp
        f = (W / 2) / np.tan(np.radians(cam.fov) / 2)
        sx = vc[0] / max(vc[2], 0.1) * f + W / 2
        sy = -vc[1] / max(vc[2], 0.1) * f + H / 2
        rad = (1 - p) * 700 + 2
        mask = Image.new("L", im.size, 0)
        md = ImageDraw.Draw(mask)
        md.ellipse((sx - rad, sy - rad, sx + rad, sy + rad), fill=255)
        black = Image.new("RGB", im.size, (0, 0, 0))
        black.paste(im, (0, 0), mask)
        im = black
        d = ImageDraw.Draw(im)

    # end card
    if t >= END_CARD:
        im = Image.new("RGB", im.size, (6, 6, 14))
        d = ImageDraw.Draw(im)
        a = smooth(0, 1, (t - END_CARD) / 0.5)
        gold = tuple(int(c * a) for c in (255, 214, 70))
        white = tuple(int(c * a) for c in (240, 240, 240))
        gray = tuple(int(c * a) for c in (150, 150, 160))
        px_text(d, (W // 2, 128), "CONGRATURATION!", 44, gold, (70, 30, 10), anchor="mm")
        px_text(d, (W // 2, 200), "CLAUDIO IS THE NEWEST AI BROTHER", 22, white,
                (40, 40, 60), anchor="mm")
        px_text(d, (W // 2, 258), "THANK YOU FOR PLAYING", 18, white, (40, 40, 60),
                anchor="mm")
        px_text(d, (W // 2, 330), "context remaining: 3 tokens", 15, gray, (30, 30, 40),
                anchor="mm")
        if t > END_CARD + 1.2 and int(t * 2) % 2 == 0:
            px_text(d, (W // 2, 396), "INSERT TOKEN TO CONTINUE", 17, (255, 214, 70),
                    (70, 30, 10), anchor="mm")
    return np.asarray(im)


# ---------------- main render loop ----------------

def frame_at(t, root, S):
    claudio_state(t, S["j"], S["claudio"])
    scene_state(t, S)
    cam = camera_at(t, S)
    img = render(root, cam, fog_color=(168, 212, 250), fog_dist=95)
    return overlays(img, t, S)


def main(out_name="claudio_silent.mp4", t0=0.0, t1=TOTAL):
    root, S = build_scene()
    nfr = int((t1 - t0) * FPS)
    out_path = os.path.join(HERE, "out", out_name)
    log = open(os.path.join(HERE, "out", "ffmpeg_anim.log"), "w")
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    for fi in range(nfr):
        t = t0 + fi / FPS
        img = frame_at(t, root, S)
        proc.stdin.write(img.astype(np.uint8).tobytes())
        if fi % 200 == 0:
            print(f"frame {fi}/{nfr} ({t:.1f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print("done:", out_path)


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
