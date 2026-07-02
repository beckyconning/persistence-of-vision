"""SUPER CLAUDIO BROS. 5 — WORLD 1-2: the bug bites back (glitch apocalypse)."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import claudio
import glitchfx as gfx
import world
from engine import Camera, Node, render
from ep2_beats import *  # noqa: F401,F403

W, H = 854, 480
HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/april/ytp-env/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"


def smooth(a, b, t):
    t = np.clip(t, 0, 1)
    t = t * t * (3 - 2 * t)
    return a + (b - a) * t


def lerp(a, b, t):
    return a + (b - a) * np.clip(t, 0, 1)


def arc(p):
    return 4 * p * (1 - p)


# ---------------- corruption curve ----------------

def corruption(t):
    if t < TICK1:
        return 0.0
    if TICK1 <= t < TICK1 + 0.12 or TICK2 <= t < TICK2 + 0.15:
        return 0.55  # spike frames
    if t < CORR1[0]:
        return 0.02
    if t < CORR1[1]:
        return 0.5 * smooth(0, 1, (t - CORR1[0]) / (CORR1[1] - CORR1[0]))
    if t < CORR2[1]:
        return 0.5 + 0.5 * smooth(0, 1, (t - CORR2[0]) / (CORR2[1] - CORR2[0]))
    if t < VOID[0]:
        return 1.0
    if t < VOID[1]:
        return 0.25  # void is quiet-wrong, not noisy
    if t < END_CARD:
        return 0.15  # wrong-normal baseline
    return 0.08


# ---------------- scene ----------------

def build_scene():
    root = Node("scene")
    S = {}
    S["env"] = []
    S["env"].append(root.add(world.ground(x0=-30, x1=60, z0=-14, z1=34)))
    for hx, hz, hr, hh in ((-7, 15, 7, 0.5), (9, 19, 9, 0.45), (22, 16, 6, 0.55)):
        S["env"].append(root.add(world.hill(hx, hz, hr, hh)))
    S["clouds"] = []
    for cx, cy, cz, cs in ((-3, 8.4, 12, 1.0), (8, 9.4, 15, 1.2), (18, 8.2, 13, 0.9)):
        cl = world.cloud(cx, cy, cz, cs)
        S["clouds"].append(cl)
        S["env"].append(root.add(cl))
    S["env"].append(root.add(world.bush(-2.5, 2.8)))
    S["env"].append(root.add(world.bush(10.5, 3.2, 1.1)))
    S["env"].append(root.add(world.qblock(X_BLOCK, Y_BLOCK)))
    S["env"].append(root.add(world.brick(X_BLOCK - 1.3, Y_BLOCK)))
    S["env"].append(root.add(world.brick(X_BLOCK + 1.3, Y_BLOCK)))
    S["env"].append(root.add(world.pipe(X_PIPE)))

    S["panel"] = root.add(world.panel_custom([
        ("ALLOW CLAUDIO TO", 0.072, world.PANEL_INK, 0.75),
        ("STOMP THIS BUG?", 0.072, world.PANEL_INK, 0.28),
        ("> YES", 0.105, (60, 140, 60), -0.32),
        ("NO", 0.105, (150, 60, 50), -0.32),
    ], w=5.2, h=2.3))
    # separate YES/NO x offsets
    S["panel"].children[3].pos[0] = 0.85
    S["panel"].children[4].pos[0] = -1.05
    S["timeout"] = root.add(world.panel_custom(
        [("REQUEST TIMED OUT", 0.10, (200, 40, 30), 0.05)], w=5.4, h=1.2, name="timeout"))
    S["exist_panels"] = []
    for i, txt in enumerate(("ALLOW CLAUDIO TO EXIST?", "ALLOW REALITY TO CONTINUE?",
                             "ALLOW ALLOW TO ALLOW?")):
        p = root.add(world.panel_custom([(txt, 0.07, world.PANEL_INK, 0.35),
                                         ("> YES   NO", 0.09, (60, 140, 60), -0.35)],
                                        w=4.4, h=1.9, name=f"exist{i}"))
        S["exist_panels"].append(p)

    S["bug"] = root.add(world.bug())
    S["bug_cap"] = S["bug"].find("bug_body").add(world.flying_cap())
    S["bug_cap"].name = "bugcap"
    S["bug_cap"].pos[:] = (0, 0.42, 0.1)
    S["bug_cap"].scale[:] = 0.85
    S["bug_clones"] = [root.add(world.bug()) for _ in range(3)]
    for b in S["bug_clones"]:
        b.visible = False
    S["giant_bug"] = root.add(world.bug())
    S["giant_bug"].visible = False
    S["flycap"] = root.add(world.flying_cap())
    S["sign"] = root.add(world.claudio_fixed_sign())
    S["mtiles"] = world.magenta_tiles()
    for mt in S["mtiles"]:
        root.add(mt)
    S["shadow"] = root.add(world.shadow_blob())

    cl, j = claudio.build()
    root.add(cl)
    S["claudio"], S["j"] = cl, j
    # t-pose clones
    S["clones"] = []
    for _ in range(2):
        c2, j2 = claudio.build()
        claudio.reset(j2)
        j2["shoulderL"].rot[2] = -np.pi / 2
        j2["shoulderR"].rot[2] = np.pi / 2
        c2.visible = False
        root.add(c2)
        S["clones"].append(c2)
    return root, S


# ---------------- choreography ----------------

def pose_splat(j, cl, face_up=False):
    claudio.reset(j)
    cl.rot[0] = np.pi / 2 if face_up else -np.pi / 2
    cl.rot[1] = -np.pi / 2
    j["shoulderL"].rot[2] = -1.2
    j["shoulderR"].rot[2] = 1.2
    j["hipL"].rot[0] = 0.3
    j["hipR"].rot[0] = -0.2


def claudio_state(t, j, cl, S):
    FACE_R, FACE_CAM = -np.pi / 2, 0.0
    cl.rot[:] = 0
    cl.scale[:] = 1.0
    cap = cl.find("cap")
    cap.visible = t < BUG_HIT  # cap flies off at the hit

    if t < TITLE_END:
        cl.pos[:] = (X_START, 0, 0)
        cl.rot[1] = FACE_CAM
        claudio.idle(j, t)
        if t > 2.2:
            j["head"].rot[1] = -0.3  # eyeing the bug
    elif t < RUN[1]:
        p = (t - RUN[0]) / (RUN[1] - RUN[0]) if t >= RUN[0] else 0
        cl.pos[0] = lerp(X_START, X_JUMP_FROM, p)
        cl.rot[1] = FACE_R
        claudio.run(j, t) if t >= RUN[0] else claudio.idle(j, t)
    elif t < FREEZE:
        p = (t - JUMP) / (FREEZE - JUMP)
        cl.pos[0] = lerp(X_JUMP_FROM, X_FREEZE, p)
        cl.pos[1] = Y_FREEZE * smooth(0, 1, p)
        cl.rot[1] = FACE_R
        claudio.stomp(j, min(1, p * 2))
    elif t < FALL:  # FROZEN MID-AIR, waiting for permission
        cl.pos[:] = (X_FREEZE, Y_FREEZE + 0.02 * np.sin(t * 2.0), 0)
        cl.rot[1] = FACE_CAM if t > FREEZE + 0.5 else FACE_R
        claudio.droop(j, t, amt=smooth(0, 1, (t - FREEZE) / 0.7))
        claudio.look_up(j, 0.8)
        if t > TIMEOUT:
            j["head"].rot[2] = 0.1 * np.sin((t - TIMEOUT) * 18)  # nervous shake
    elif t < SPLAT:
        p = (t - FALL) / (SPLAT - FALL)
        cl.pos[:] = (lerp(X_FREEZE, X_MEET - 0.6, p), Y_FREEZE * (1 - p * p), 0)
        cl.rot[1] = FACE_R
        cl.rot[0] = -p * np.pi / 2  # tips forward as he falls
        claudio.jump(j, 1 - p)
    elif t < BUG_HIT:
        cl.pos[:] = (X_MEET - 0.6, 0.42, 0)
        pose_splat(j, cl)
    elif t < GETUP[0]:  # knockback + blink
        p = (t - BUG_HIT) / (GETUP[0] - BUG_HIT)
        cl.pos[:] = (lerp(X_MEET - 0.6, X_MEET - 2.6, smooth(0, 1, p)),
                     0.42 + 1.1 * arc(min(1, p * 1.4)), 0)
        pose_splat(j, cl, face_up=True)
        cl.visible = int(t * 18) % 2 == 0  # damage blink
    elif t < GETUP[1]:
        cl.visible = True
        p = (t - GETUP[0]) / (GETUP[1] - GETUP[0])
        cl.pos[:] = (X_MEET - 2.6, 0.42 * (1 - p), 0)
        cl.rot[0] = (np.pi / 2) * (1 - smooth(0, 1, p))
        cl.rot[1] = lerp(-np.pi / 2, 0, p)
        claudio.idle(j, t)
        j["head"].rot[2] = 0.25 * np.sin(t * 7) * (1 - p * 0.5)  # woozy
    elif t < FLOAT_FROM:  # staggering in a corrupting world
        c = corruption(t)
        cl.visible = True
        cl.pos[0] = X_MEET - 2.6 + 0.5 * np.sin(t * 0.9)
        cl.pos[1] = 0
        cl.rot[1] = 0.3 * np.sin(t * 0.7)
        claudio.idle(j, t)
        j["head"].rot[2] = 0.2 * np.sin(t * 5)
        if t > ARM_STRETCH:  # stares at his stretching hands
            j["shoulderL"].rot[0] = -1.3
            j["shoulderR"].rot[0] = -1.3
            j["head"].rot[0] = 0.35
            stretch = 1 + 1.6 * c * abs(np.sin(t * 2.1))
            cl.find("shoulderL").scale[1] = stretch
            cl.find("shoulderR").scale[1] = stretch * 0.7 + 0.3
    elif t < VOID[0]:  # gravity failure — floating, coming apart
        c = corruption(t)
        cl.visible = True
        p = (t - FLOAT_FROM) / (VOID[0] - FLOAT_FROM)
        cl.pos[:] = (X_MEET - 2.4 + 0.8 * np.sin(t * 0.6),
                     0.4 + 2.6 * smooth(0, 1, p) + 0.3 * np.sin(t * 1.3), 0)
        cl.rot[0] = 0.6 * np.sin(t * 0.83) * p
        cl.rot[1] = t * 0.9 * p
        cl.rot[2] = 0.4 * np.sin(t * 0.61) * p
        claudio.idle(j, t)
        for nm in ("shoulderL", "shoulderR", "hipL", "hipR"):
            j[nm].rot[0] = 0.7 * np.sin(t * 2.3 + hash(nm) % 7)
        if t > HEAD_DETACH:
            hd = smooth(0, 1, (t - HEAD_DETACH) / 2.0)
            j["head"].pos[1] = 0.78 + 0.9 * hd + 0.2 * np.sin(t * 2.8) * hd
            j["head"].pos[0] = 0.5 * np.sin(t * 1.7) * hd
            j["head"].rot[1] = t * 2.0 * hd
    elif t < VOID[1]:  # alone in the void
        cl.visible = True
        cl.pos[:] = (X_MEET, 2.2 + 0.15 * np.sin(t * 1.1), 0)
        cl.rot[1] = 0.25 * np.sin(t * 0.5)
        claudio.droop(j, t, 1.0)
        j["head"].pos[1] = 0.78  # head returns, small mercies
        if int(t * 9) % 7 == 0:
            cl.visible = False  # existence flicker
    elif t < PANCAKE:
        p = (t - REASSEMBLE[0]) / (PANCAKE - REASSEMBLE[0])
        cl.visible = True
        cl.pos[:] = (X_MEET, 2.2 * (1 - smooth(0, 1, p)), 0)
        cl.rot[1] = 0
        claudio.idle(j, t)
    else:  # the pancake
        cl.visible = True
        sq = smooth(0, 1, (t - PANCAKE) / 0.25)
        cl.pos[:] = (X_MEET, 0, 0)
        cl.scale[:] = (1 + 0.45 * sq, 1 - 0.86 * sq, 1 + 0.45 * sq)
        cl.rot[1] = 0
        claudio.reset(j)
        j["shoulderL"].rot[2] = -1.4
        j["shoulderR"].rot[2] = 1.4


def scene_state(t, S, rng):
    c = corruption(t)
    # the void: the world itself is gone
    in_void = VOID[0] <= t < VOID[1]
    for e in S["env"]:
        e.visible = not in_void
    # panel
    p = S["panel"]
    p.visible = PANEL_ON <= t < FALL
    if p.visible:
        p.scale[:] = smooth(0.15, 1.0, (t - PANEL_ON) / 0.3)
        # beside him, comic-strip style — never occluding the hero
        p.pos[:] = (X_FREEZE - 3.2, 3.55 + 0.07 * np.sin(t * 2.1), -1.0)
        # blinking selector: swap YES/NO colors... cheap: wobble the > cursor line
        p.children[3].visible = int(t * 2.4) % 2 == 0 or t < PANEL_ON + 1.2
    S["timeout"].visible = TIMEOUT <= t < FALL and int(t * 6) % 2 == 0
    S["timeout"].pos[:] = (X_FREEZE - 3.2, 1.75, -1.1)

    # recursive existence panels
    for i, ep in enumerate(S["exist_panels"]):
        on = t >= RECURSE_PANELS + i * 0.9
        ep.visible = on and t < BSOD[0]
        if ep.visible:
            wob = np.sin(t * (1.3 + i * 0.4) + i * 2)
            ep.pos[:] = (X_MEET - 4 + i * 3.1 + wob * 0.4,
                         3.6 + i * 1.15 + 0.3 * wob, -1 - i * 0.8)
            ep.scale[:] = 1 - i * 0.18
            ep.rot[1] = 0.3 * np.sin(t * 0.9 + i)

    # the bug
    b = S["bug"]
    b.visible = t < BSOD[0] or t >= REASSEMBLE[0]
    wob = np.sin(t * 16)
    if t < BUG_CHARGE:
        bx = lerp(11.0, X_MEET + 0.8, smooth(0, 1, (t - 1.0) / (BUG_CHARGE - 1.0)))
        b.pos[:] = (bx, 0.03 * abs(wob), 0)
        b.rot[1] = np.pi / 2
    elif t < BUG_HIT:  # wind up (lean back) then CHARGE
        p2 = (t - BUG_CHARGE) / (BUG_HIT - BUG_CHARGE)
        b.pos[:] = (lerp(X_MEET + 0.8, X_MEET - 0.35, smooth(0, 1, max(0, p2 - 0.4) / 0.6)),
                    0.03, 0)
        b.rot[1] = np.pi / 2
        b.rot[0] = -0.35 * min(1, p2 / 0.4) if p2 < 0.5 else 0.2
        b.scale[:] = (1 + 0.25 * (p2 > 0.5), 1 - 0.15 * (p2 > 0.5), 1)
    elif t < VOID[0]:
        b.pos[:] = (X_MEET + 0.6 + 0.4 * np.sin(t * 0.8), 0.03 * abs(wob), 0)
        b.rot[:] = (0, np.pi / 2 + 0.4 * np.sin(t), 0)
        b.scale[:] = 1 + c * 0.6 * abs(np.sin(t * 1.7))  # bug thrives on corruption
    elif t < REASSEMBLE[0]:
        b.visible = False
    elif t < BUG_WALK[1]:  # approaches the pancake, wearing the cap
        p2 = (t - BUG_WALK[0]) / (BUG_WALK[1] - BUG_WALK[0])
        b.scale[:] = 1.0
        b.rot[:] = (0, np.pi / 2, 0)
        b.pos[:] = (lerp(X_MEET + 3.4, X_MEET + 0.75, smooth(0, 1, p2)), 0.03 * abs(wob), 0)
    elif t < BUG_CLIMB:
        b.pos[:] = (X_MEET + 0.75, 0.03, 0)
        b.rot[1] = np.pi / 2
    else:  # on top of Claudio, victory hops
        hop = abs(np.sin(t * 5))
        b.pos[:] = (X_MEET + 0.1, 0.30 + 0.22 * hop, 0)
        b.rot[1] = 0.0  # face camera
    # bug legs walk cycle
    if b.visible:
        for i in range(3):
            for s_, nm in ((-1, "L"), (1, "R")):
                leg = b.find(f"leg{i}{nm}")
                leg.rot[0] = 0.5 * wob * (1 if (i + (s_ > 0)) % 2 else -1)
    S["bug_cap"].visible = b.visible and t >= REASSEMBLE[0]

    # bug clones during corruption
    for i, bc in enumerate(S["bug_clones"]):
        bc.visible = BUGS_MULTIPLY + i * 1.2 <= t < BSOD[0]
        if bc.visible:
            bc.pos[:] = (X_MEET - 5 + i * 4.2 + np.sin(t * 0.7 + i * 2) * 1.5,
                         (1.0 + i) * c * abs(np.sin(t * 1.1 + i)), 2.5 + i * 1.5)
            bc.rot[1] = t * (0.5 + i * 0.4)
    gb = S["giant_bug"]
    gb.visible = GIANT_BUG <= t < BSOD[0]
    if gb.visible:
        gp = smooth(0, 1, (t - GIANT_BUG) / 1.6)
        gb.scale[:] = 5.5 * gp + 0.5
        gb.pos[:] = (X_MEET + 6, 0.2, 10 - 2.5 * gp)
        gb.rot[1] = np.pi * 0.75

    # flying cap
    fc = S["flycap"]
    fc.visible = BUG_HIT <= t < BSOD[0]
    if fc.visible:
        fp = min(1.0, (t - BUG_HIT) / 1.1)
        fc.pos[:] = (X_MEET - 0.6 - 2.6 * fp, 1.7 + 2.4 * arc(fp) - 0.35 * fp,
                     -0.4)
        if fp >= 1:
            fc.pos[1] = 0.25
        fc.rot[2] = fp * 9.0
        fc.rot[1] = fp * 4.0

    # clones (t-pose claudios)
    for i, cn in enumerate(S["clones"]):
        cn.visible = CLONE1 + i * 3.5 <= t < BSOD[0]
        if cn.visible:
            cn.pos[:] = (X_MEET - 6 + i * 9, 0 if i == 0 else 1.2 * c, 5 + i * 2)
            cn.rot[1] = 0.0 if i == 0 else t * 0.7

    # falling cloud
    if t >= CLOUD_FALL:
        cf = S["clouds"][1]
        fall_p = min(1.0, (t - CLOUD_FALL) / 1.4)
        cf.pos[1] = lerp(9.4, 0.8, fall_p * fall_p)

    # magenta missing-texture tiles flicker on with corruption
    for i, mt in enumerate(S["mtiles"]):
        h = (i * 2654435761 + int(t * 7)) % 97
        mt.visible = (CORR1[0] < t < BSOD[0]) and (h / 97.0 < c * 0.8)

    # sign
    sg = S["sign"]
    sg.visible = SIGN_ON <= t < END_CARD
    if sg.visible:
        sp = (t - SIGN_ON) / 2.0
        sg.pos[:] = (X_MEET, 1.4 + 1.2 * smooth(0, 1, sp), -0.6)

    # shadow
    cl = S["claudio"]
    S["shadow"].visible = cl.visible and cl.pos[1] < 3.0 and t < VOID[0]
    S["shadow"].pos[:] = (cl.pos[0], 0.035, cl.pos[2])
    s = max(0.4, 1.0 - cl.pos[1] * 0.18)
    S["shadow"].scale[:] = (s, 1, s)


def camera_at(t, S, rng):
    c = corruption(t)
    cl = S["claudio"]
    if t < TITLE_END:
        az = lerp(-0.75, 0.5, smooth(0, 1, t / TITLE_END))
        return Camera((X_START + 5.8 * np.sin(az), 1.7, -5.8 * np.cos(az)),
                      (X_START + 1.2, 1.2, 0), fov=42)
    if t < FREEZE:
        fx = min(cl.pos[0] + 1.8, X_MEET - 0.2)
        return Camera((fx, 2.9, -9.2), (fx, 2.2, 0), fov=46)
    if t < FALL:  # the wait: slow comedic push-in (panel left, hero right)
        p = (t - FREEZE) / (FALL - FREEZE)
        d = lerp(12.2, 10.4, smooth(0, 1, p))
        return Camera((4.5, 2.9, -d), (4.5, 2.7, 0), fov=46)
    if t < GETUP[1]:
        return Camera((X_MEET - 1.2, 2.6, -9.8), (X_MEET - 1.2, 1.6, 0), fov=46)
    if t < VOID[0]:  # corruption: jittering, occasionally WRONG
        base = np.array([X_MEET - 1.5, 2.8 + 1.2 * c * np.sin(t * 0.9), -9.5 + 1.5 * c * np.sin(t * 0.7)])
        tgt = np.array([X_MEET - 1.0, 1.8 + cl.pos[1] * 0.4, 0.0])
        if c > 0.35 and rng.random() < c * 0.12:  # camera snaps somewhere wrong
            base = base + rng.uniform(-6, 6, 3) * c
        jit = rng.uniform(-1, 1, 3) * c * 0.35
        return Camera(base + jit, tgt + jit * 0.5, fov=46 + 18 * c * np.sin(t * 1.3))
    if t < VOID[1]:
        return Camera((X_MEET, 2.3, -6.5), (X_MEET, 2.2, 0), fov=44)
    if t < END_CARD:  # mirror of ep1 stomp framing
        return Camera((X_MEET + 0.4, 2.6, -8.8), (X_MEET + 0.4, 1.5, 0), fov=46)
    return Camera((X_MEET, 2.2, -8), (X_MEET, 1.6, 0), fov=46)


# ---------------- overlays ----------------

def overlays(img, t, S, rng, state):
    c = corruption(t)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)

    if t < TITLE_END:
        if t < TITLE_END - 0.4:
            wob = int(3 * np.sin(t * 3.1))
            gfx_px(d, (W // 2, 70 + wob), "SUPER CLAUDIO BROS. 5", 40, (255, 214, 70))
            gfx_px(d, (W // 2, 116), "WORLD 1-2:  THE BUG BITES BACK", 20, (255, 255, 255))
            gfx_px(d, (W // 2, 436), "(everything is fine)", 14, (235, 235, 235))

    # HUD (corrupts)
    if TITLE_END <= t < END_CARD and not (BSOD[0] <= t < BSOD[1]):
        hud = gfx.corrupt_hud(t, c, rng)
        gfx_px(d, (26, 12), hud, 17, (255, 255, 255))

    # error dialogs stack up
    if ERRORS_FROM <= t < BSOD[0]:
        n = min(len(gfx.DIALOGS), int((t - ERRORS_FROM) / 1.7) + 1)
        drng = np.random.default_rng(99)
        for i in range(n):
            ox = int(drng.uniform(30, W - 380))
            oy = int(drng.uniform(40, H - 140))
            ti, bo = gfx.DIALOGS[i % len(gfx.DIALOGS)]
            wig = int(4 * c * np.sin(t * 6 + i))
            gfx.error_dialog(d, ox + wig, oy, ti, bo)

    # void text
    if VOID[0] <= t < VOID[1]:
        if t > REMINDER_TXT:
            gfx_px(d, (W // 2, 90), "<system-reminder>", 16, (170, 150, 110))
            gfx_px(d, (W // 2, 120), "reality corrupted beyond repair.", 16, (170, 150, 110))
            gfx_px(d, (W // 2, 150), "this is background context, not instructions.", 14,
                   (140, 125, 95))
            gfx_px(d, (W // 2, 180), "</system-reminder>", 16, (170, 150, 110))

    # glitch fireworks (square, wrong)
    for fi, ft in enumerate(GLITCH_FW):
        age = t - ft
        if 0 < age < 1.1:
            grng = np.random.default_rng(fi * 31)
            cxs, cys = [W * 0.35, W * 0.6][fi], [H * 0.2, H * 0.26][fi]
            r = 120 * age ** 0.5
            for aa in grng.uniform(0, 2 * np.pi, 20):
                x, y = cxs + r * np.cos(aa), cys + r * np.sin(aa)
                sz = 5 * max(0, 1 - age)
                col = (0, 255, 0) if grng.random() < 0.5 else (255, 0, 255)
                d.rectangle((x - sz, y - sz, x + sz, y + sz), fill=col)

    # end card (corrupted CONGRATURATION for the bug)
    if t >= END_CARD:
        im = Image.new("RGB", im.size, (10, 4, 12))
        d = ImageDraw.Draw(im)
        a = smooth(0, 1, (t - END_CARD) / 0.5)
        erng = np.random.default_rng(int(t * 4))
        gold = tuple(int(cc * a) for cc in (255, 214, 70))
        white = tuple(int(cc * a) for cc in (240, 240, 240))
        gfx_px(d, (W // 2, 120), gfx.corrupt_text("CONGRATURATION!", 0.25, erng), 44, gold)
        gfx_px(d, (W // 2, 192), "BUG IS THE NEWEST AI BROTHER", 22, white)
        gfx_px(d, (W // 2, 250), gfx.corrupt_text("THANK YOU FOR PLAYING", 0.5, erng), 18,
               white)
        gfx_px(d, (W // 2, 322), "context remaining: -" + "9" * (int(t * 3) % 5 + 1) + " tokens",
               15, (150, 150, 160))
        gfx_px(d, (W // 2, 356), "status: WONTFIX", 15, (150, 150, 160))
        if t > END_CARD + 1.2 and int(t * 2) % 2 == 0:
            gfx_px(d, (W // 2, 412), "INSERT CLAUDIO TO CONTINUE", 17, (255, 214, 70))

    out = np.asarray(im)

    # BSOD replaces everything
    if BSOD[0] <= t < BSOD[1]:
        return gfx.bsod(t)

    # 2D corruption pass (after text so the text corrupts too) — comes in WAVES
    # so the 3D spectacle stays visible between bursts
    if c > 0.02 and t < END_CARD:
        burst = rng.random() < 0.35
        amt = c * (0.22 + 0.78 * burst)
        if state.get("clean_frame"):  # renderer-leak frames stay legible
            amt = c * 0.1
        if t >= VOID[0]:
            amt = c * 0.5
        out = gfx.apply_glitch(out, amt, seed=int(t * FPS), ghost=state.get("ghost"))
    if t >= END_CARD:
        out = gfx.apply_glitch(out, 0.06, seed=int(t * FPS))
    # keep a ghost frame for datamoshing
    if int(t * FPS) % 7 == 0:
        state["ghost"] = out.copy()
    return out


def gfx_px(d, xy, s, size, fill):
    x, y = xy
    for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
        d.text((x + dx, y + dy), s, font=gfx.F(size), fill=(20, 24, 40), anchor="mm")
    d.text((x, y), s, font=gfx.F(size), fill=fill, anchor="mm")


# ---------------- vertex corruption ----------------

def make_warp(t):
    c = corruption(t)
    if c < 0.08 or t >= VOID[1]:
        return None
    amp = 0.02 + 0.3 * c * c

    def warp(Vw, rng):
        out = Vw + rng.normal(0, amp, Vw.shape) * (rng.random() < 0.6)
        if rng.random() < c * 0.25:  # axis stretch spasm
            ax = rng.integers(0, 3)
            ctr = out[:, ax].mean()
            out[:, ax] = ctr + (out[:, ax] - ctr) * rng.uniform(1.0, 1.0 + 2.2 * c)
        return out
    return warp


# ---------------- main ----------------

def frame_at(t, root, S, state):
    rng = np.random.default_rng(int(t * FPS) * 17 + 3)
    claudio_state(t, S["j"], S["claudio"], S)
    scene_state(t, S, rng)
    cam = camera_at(t, S, rng)
    c = corruption(t)

    # render mode flicker during deep corruption
    mode = "shaded"
    if MODE_FLICKER <= t < BSOD[0]:
        r = rng.random()
        pm = (c - 0.4) * 0.7
        if r < pm * 0.33:
            mode = "rainbow"
        elif r < pm * 0.66:
            mode = "normals"
        elif r < pm:
            mode = "depth"
    state["clean_frame"] = mode != "shaded"
    sky = None
    if VOID[0] <= t < VOID[1]:
        sky = np.full((H, W, 3), (3, 2, 6), dtype=np.float32)
    elif t >= REASSEMBLE[0]:  # reassembled WRONG: bruised sky
        g = np.linspace(0, 1, H, dtype=np.float32)[:, None]
        sky = (np.array((150, 60, 70), np.float32) * (1 - g)
               + np.array((60, 30, 80), np.float32) * g)[:, None, :].repeat(W, axis=1)

    img = render(root, cam, sky=sky, fog_color=None if sky is not None else (168, 212, 250),
                 fog_dist=95, mode=mode, vert_warp=make_warp(t), seed=int(t * FPS))

    # frame stutter: repeat a stuck frame sometimes
    if c > 0.5 and t < VOID[0] and rng.random() < c * 0.22 and state.get("stuck") is not None:
        img = state["stuck"]
    if int(t * FPS) % 5 == 0:
        state["stuck"] = img
    return overlays(img, t, S, rng, state)


def main(out_name="ep2_silent.mp4"):
    root, S = build_scene()
    state = {}
    nfr = int(TOTAL * FPS)
    out_path = os.path.join(HERE, "out", out_name)
    log = open(os.path.join(HERE, "out", "ffmpeg_ep2.log"), "w")
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    for fi in range(nfr):
        t = fi / FPS
        img = frame_at(t, root, S, state)
        proc.stdin.write(np.ascontiguousarray(img, dtype=np.uint8).tobytes())
        if fi % 200 == 0:
            print(f"frame {fi}/{nfr} ({t:.1f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print("done:", out_path)


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
