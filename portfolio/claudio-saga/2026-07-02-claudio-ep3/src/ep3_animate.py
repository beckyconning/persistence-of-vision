"""SUPER CLAUDIO BROS. 5 — EPISODE 3: BROTHER VS BROTHER."""
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw

import claudio
import ep3_fx as fx
import glitchfx as gfx
import grokio
import world
from engine import Camera, Node, render, sky_gradient
from ep3_beats import *  # noqa: F401,F403

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


# ---------------- fight poses (rig-agnostic: work on both brothers) ----------------

def stance(j, t):
    claudio.reset(j)
    j["shoulderL"].rot[:] = (-1.25, 0, -0.45)
    j["shoulderR"].rot[:] = (-1.25, 0, 0.45)
    j["torso"].rot[0] = 0.12
    j["pelvis"].pos[1] = 0.60 + 0.03 * abs(np.sin(t * 4.2))
    j["hipL"].rot[0] = 0.15
    j["hipR"].rot[0] = -0.1


def punch(j, t, rate=9.0):
    claudio.reset(j)
    ph = np.sin(t * rate)
    j["shoulderL"].rot[:] = (-1.6 + 0.7 * ph, 0, -0.15)
    j["shoulderR"].rot[:] = (-1.6 - 0.7 * ph, 0, 0.15)
    j["torso"].rot[0] = 0.22
    j["torso"].rot[1] = 0.25 * ph
    j["pelvis"].pos[1] = 0.60 + 0.02 * abs(np.sin(t * rate))


def uppercut(j, p):
    """p 0..1: wind-up then swing."""
    claudio.reset(j)
    if p < 0.4:
        k = p / 0.4
        j["shoulderR"].rot[:] = (0.9 * k, 0, 0.3)
        j["torso"].rot[0] = 0.3 * k
        j["pelvis"].pos[1] = 0.62 - 0.12 * k
    else:
        k = (p - 0.4) / 0.6
        j["shoulderR"].rot[:] = (0.9 - 3.4 * k, 0, 0.3)
        j["torso"].rot[0] = 0.3 - 0.55 * k
        j["pelvis"].pos[1] = 0.5 + 0.2 * k
    j["shoulderL"].rot[:] = (-1.0, 0, -0.4)


def knocked(j, t):
    claudio.reset(j)
    j["shoulderL"].rot[:] = (-2.2, 0, -1.0)
    j["shoulderR"].rot[:] = (-2.2, 0, 1.0)
    j["hipL"].rot[0] = -0.7
    j["hipR"].rot[0] = 0.5
    j["head"].rot[0] = -0.3


def lying(j):
    claudio.reset(j)
    j["shoulderL"].rot[2] = -1.5
    j["shoulderR"].rot[2] = 1.5
    j["hipL"].rot[0] = 0.2
    j["hipR"].rot[0] = -0.15


def loom(j, t):
    """One arm up, charging the mega ball."""
    claudio.reset(j)
    j["shoulderR"].rot[:] = (-2.9, 0, 0.35)
    j["shoulderL"].rot[:] = (-0.3, 0, -0.3)
    j["torso"].rot[0] = -0.08
    j["head"].rot[0] = -0.25
    j["pelvis"].pos[1] = 0.62 + 0.015 * np.sin(t * 3)


def dash(j):
    claudio.reset(j)
    j["torso"].rot[0] = 0.55
    j["shoulderL"].rot[:] = (1.9, 0, -0.3)
    j["shoulderR"].rot[:] = (1.9, 0, 0.3)
    j["hipL"].rot[0] = 1.0
    j["hipR"].rot[0] = -0.9
    j["head"].rot[0] = -0.35


def powerup(j, t):
    claudio.reset(j)
    j["pelvis"].pos[1] = 0.52
    j["shoulderL"].rot[:] = (0.4, 0, -1.2)
    j["shoulderR"].rot[:] = (0.4, 0, 1.2)
    j["torso"].rot[0] = 0.18
    j["head"].rot[0] = -0.3
    sh = 0.02 * np.sin(t * 40)
    j["head"].rot[2] = sh


def sit(j):
    claudio.reset(j)
    j["hipL"].rot[0] = -1.5
    j["hipR"].rot[0] = -1.5
    j["torso"].rot[0] = 0.18
    j["shoulderL"].rot[0] = 0.35
    j["shoulderR"].rot[0] = 0.35
    j["head"].rot[0] = 0.1


# ---------------- scene ----------------

def build_scene():
    root = Node("scene")
    S = {}
    root.add(world.ground(x0=-30, x1=40, z0=-14, z1=34))
    S["hills"] = []
    for hx, hz, hr, hh in ((-8, 16, 7, 0.5), (16, 19, 9, 0.45), (26, 15, 6, 0.55)):
        S["hills"].append(root.add(world.hill(hx, hz, hr, hh)))
    S["crater_hill"] = root.add(world.hill(X_CRATER_HILL, 2.5, 3.6, 0.6))
    S["clouds"] = []
    for cx, cy, cz, cs in ((-2, 8.6, 12, 1.1), (9, 9.6, 15, 1.3), (20, 8.4, 13, 1.0)):
        cl = world.cloud(cx, cy, cz, cs)
        S["clouds"].append(cl)
        root.add(cl)
    root.add(world.bush(4.5, 3.0))
    root.add(world.bush(11.5, 2.6, 0.9))
    S["blocks"] = []
    for bx in (X_BLOCKS - 1.3, X_BLOCKS, X_BLOCKS + 1.3):
        b = world.qblock(bx, Y_BLOCKS) if bx == X_BLOCKS else world.brick(bx, Y_BLOCKS)
        S["blocks"].append(root.add(b))
    S["pipe"] = root.add(world.pipe(X_PIPE))
    S["flagpole"] = root.add(world.flagpole(X_FLAG, z=6.0))

    # fx
    rng = np.random.default_rng(11)
    S["debris_parent"], S["debris"] = fx.make_debris(rng)
    root.add(S["debris_parent"])
    S["boom_blocks"] = root.add(fx.explosion())
    S["boom_horizon"] = root.add(fx.explosion())
    S["dust"] = root.add(fx.dust_ring())
    S["dust2"] = root.add(fx.dust_ring())
    S["aura"] = root.add(fx.aura())
    S["fireball"] = root.add(fx.fireball(dark=True))
    S["starshot"] = root.add(fx.fireball(dark=False))
    S["mega"] = root.add(fx.mega_ball())
    S["fires"] = [root.add(fx.fire_patch(x, z, s, seed=i + 3)) for i, (x, z, s) in
                  enumerate(((8.2, 0.8, 1.1), (2.8, 3.2, 0.9), (12.5, 1.5, 0.8),
                             (5.5, 5.5, 1.2)))]
    S["crater"] = root.add(Node("crater", pos=(2.4, 0.05, 1.8)))
    S["crater"].mesh(*fx.tf_crater() if hasattr(fx, "tf_crater") else
                     world.tf(world.cylinder(1.8, 0.06, 12, (58, 46, 40)), pos=(0, 0, 0)))
    S["crater"].visible = False

    # the rubble Claudio ends up sitting on
    rubble = Node("rubble", pos=(7.3, 0.28, 2.55))
    rubble.mesh(*world.merge(
        world.tf(world.box(1.0, 0.56, 0.9, (150, 96, 64)), pos=(0, 0, 0), rot=(0, 0.3, 0.05)),
        world.tf(world.box(0.5, 0.3, 0.5, (120, 74, 20)), pos=(-0.7, -0.13, 0.2), rot=(0, 0.8, 0)),
        world.tf(world.box(0.4, 0.24, 0.45, (176, 96, 60)), pos=(0.75, -0.16, -0.1), rot=(0, 1.2, 0)),
    ))
    root.add(rubble)

    # cast
    c, cj = claudio.build()
    root.add(c)
    g, gj = grokio.build()
    root.add(g)
    S["c"], S["cj"], S["g"], S["gj"] = c, cj, g, gj
    S["flycap"] = root.add(world.flying_cap())
    S["bug"] = root.add(world.bug())
    S["bug"].visible = False
    S["bugcap"] = S["bug"].find("bug_body").add(world.flying_cap())
    S["bugcap"].pos[:] = (0, 0.42, 0.1)
    S["bugcap"].scale[:] = 0.85
    S["bugcap"].visible = False
    S["shadow_c"] = root.add(world.shadow_blob())
    S["shadow_g"] = root.add(world.shadow_blob())
    return root, S


# ---------------- kingdom damage state ----------------

def kingdom_pct(t):
    steps = [(CLASH, 92), (BLOCKS_BOOM, 78), (PIPE_SMASH, 66), (HILL_CRASH, 52),
             (HORIZON_BOOM, 8), (AFTERMATH[0], 0)]
    pct = 100
    for bt, v in steps:
        if t >= bt:
            pct = v
    return pct


def hearts(t):
    ch = 3 - (t >= PIPE_SMASH) - (t >= HILL_CRASH)
    gh = 3 - (t >= STARSHOT_HIT) - (t >= COMBO[0] + 1.0) - (t >= FINAL_HIT)
    return max(0, ch), max(0, gh)


# ---------------- choreography ----------------

def face(node, tx):
    """Rotate to face world x-target."""
    node.rot[1] = -np.pi / 2 if tx > node.pos[0] else np.pi / 2


def claudio_state(t, S):
    j, cl = S["cj"], S["c"]
    cl.visible = True
    cl.rot[:] = 0
    cl.scale[:] = 1.0
    cl.find("cap").visible = not (HILL_CRASH <= t < CAP_ON)

    if t < CHARGE:
        if t < TITLE_END:
            cl.pos[:] = (X_CLAUDIO_START, 0, 0)
            cl.rot[1] = 0
            claudio.idle(j, t)
        elif t < FACEOFF[0]:  # reacts to arrival
            cl.pos[:] = (X_CLAUDIO_START, 0, 0)
            face(cl, X_GROKIO_LAND)
            stance(j, t) if t > LAND else claudio.idle(j, t)
            if LAND <= t < LAND + 0.4:
                cl.pos[1] = 0.1 * arc((t - LAND) / 0.4)  # startled hop
        else:  # circling
            p = (t - FACEOFF[0]) / (FACEOFF[1] - FACEOFF[0])
            ang = np.pi + 0.55 * np.sin(p * 2.6)
            cx = X_CLASH + 3.6 * np.cos(ang)
            cz = 1.6 * np.sin(ang)
            cl.pos[:] = (cx, 0, cz)
            face(cl, S["g"].pos[0])
            stance(j, t)
    elif t < CLASH:
        p = (t - CHARGE) / (CLASH - CHARGE)
        if p < 0.55:
            cl.pos[:] = (lerp(3.8, 5.6, p / 0.55), 0, 0)
            claudio.run(j, t, rate=13)
        else:
            k = (p - 0.55) / 0.45
            cl.pos[:] = (lerp(5.6, X_CLASH - 0.45, k), 1.65 * smooth(0, 1, k), 0)
            uppercut(j, 0.4 + 0.6 * k)
        face(cl, X_CLASH)
    elif t < CLASH_FREEZE[1]:  # the freeze
        cl.pos[:] = (X_CLASH - 0.45, 1.65, 0)
        face(cl, X_CLASH)
        uppercut(j, 1.0)
    elif t < KNOCKBACK_END:
        p = (t - CLASH_FREEZE[1]) / (KNOCKBACK_END - CLASH_FREEZE[1])
        cl.pos[:] = (lerp(X_CLASH - 0.45, 3.5, smooth(0, 1, p)), 1.65 * (1 - p * p), 0)
        face(cl, X_CLASH)
        knocked(j, t)
    elif t < MELEE[0]:  # dodging fireballs
        cl.pos[:] = (3.5, 0, 0)
        face(cl, S["g"].pos[0])
        stance(j, t)
        if DODGE1 - 0.15 <= t < DODGE1 + 0.55:
            cl.pos[1] = 1.5 * arc((t - (DODGE1 - 0.15)) / 0.7)
            claudio.jump(j, 1)
        elif DODGE2 - 0.1 <= t < DODGE2 + 0.5:
            j["pelvis"].pos[1] = 0.30  # duck
            j["torso"].rot[0] = 0.55
        elif BLOCKS_BOOM - 0.5 <= t < BLOCKS_BOOM + 0.4:
            cl.pos[2] = -1.3 * arc((t - (BLOCKS_BOOM - 0.5)) / 0.9)  # sidestep
        elif STARSHOT - 0.25 <= t < STARSHOT + 0.4:
            p = (t - (STARSHOT - 0.25)) / 0.65
            j["shoulderR"].rot[:] = (-2.6 + 2.2 * p, 0, 0.3)  # throw
            j["torso"].rot[1] = -0.3 + 0.5 * p
    elif t < PIPE_SMASH:  # melee at center
        cl.pos[:] = (X_CLASH - 0.75, 0, 0)
        face(cl, X_CLASH)
        punch(j, t, rate=11)
        for ht in MELEE_HITS[1::2]:  # takes hits on odd beats
            if ht <= t < ht + 0.18:
                cl.pos[0] -= 0.3
                j["head"].rot[2] = 0.3
    elif t < UPPERCUT1:  # smashed into the pipe
        p = (t - PIPE_SMASH) / 0.55
        if p < 1:
            cl.pos[:] = (lerp(X_CLASH - 0.6, X_PIPE - 0.7, smooth(0, 1, p)),
                         1.9 * arc(p * 0.9), 0)
            knocked(j, t)
        else:
            cl.pos[:] = (X_PIPE - 0.7, 0.15, 0)
            lying(j)
            cl.rot[0] = -np.pi / 2 * 0.85
        cl.rot[1] = np.pi / 2
    elif t < HILL_CRASH:  # launched skyward
        p = (t - UPPERCUT1) / (HILL_CRASH - UPPERCUT1)
        if t < UPPERCUT1 + 0.35:
            cl.pos[:] = (X_PIPE - 0.7, 0.15, 0)
            lying(j)
        else:
            k = (t - UPPERCUT1 - 0.35) / (HILL_CRASH - UPPERCUT1 - 0.35)
            cl.pos[:] = (lerp(X_PIPE - 1, 2.4, k), 0.4 + 5.2 * arc(k * 0.85), lerp(0, 1.6, k))
            knocked(j, t)
            cl.rot[2] = k * 7.0  # tumbling
    elif t < POWERUP[0]:  # down
        cl.pos[:] = (2.4, 0.18, 1.8)
        cl.rot[0] = -np.pi / 2 * 0.9
        cl.rot[1] = np.pi / 2
        lying(j)
        if t > BUG_CAP[1]:
            j["head"].rot[0] = -0.3  # stirring
    elif t < MEGA_THROW:  # power up
        p = (t - POWERUP[0]) / 0.6
        cl.rot[:] = 0
        if p < 1:
            cl.pos[:] = (2.4, 0.18 * (1 - p), lerp(1.8, 0.4, p))
            claudio.idle(j, t)
        else:
            cl.pos[:] = (2.6, 0, 0.2)
            powerup(j, t)
        face(cl, S["g"].pos[0])
    elif t < COMBO[0]:  # THE DASH under the mega ball
        p = (t - MEGA_THROW) / (COMBO[0] - MEGA_THROW)
        cl.pos[:] = (lerp(2.6, S["g"].pos[0] - 0.85, smooth(0, 1, p)), 0.12, 0.2 * (1 - p))
        dash(j)
        face(cl, S["g"].pos[0])
    elif t < FINAL_HIT:
        cl.pos[:] = (S["g"].pos[0] - 0.85, 0, 0)
        face(cl, S["g"].pos[0])
        punch(j, t, rate=16)
    elif t < FINAL_FREEZE[1]:
        cl.pos[:] = (S["g"].pos[0] - 0.8, 0.4, 0)
        face(cl, S["g"].pos[0])
        uppercut(j, 1.0)
    elif t < SIT:  # weary walk to the rubble
        if t < AFTERMATH[0]:
            cl.pos[:] = (5.2, 0, 0)
            face(cl, 9)
            claudio.idle(j, t)
            j["head"].rot[0] = -0.4  # watching him fly
        else:
            p = (t - AFTERMATH[0]) / (SIT - AFTERMATH[0])
            cl.pos[:] = (lerp(5.2, 7.3, smooth(0, 1, p)), 0, lerp(0, 2.2, p))
            claudio.run(j, t, rate=4.5)  # trudge
            j["torso"].rot[0] = 0.25
            j["head"].rot[0] = 0.25
            cl.rot[1] = -np.pi / 2 + 0.4
    else:  # sitting on rubble, facing the sunset
        cl.pos[:] = (7.3, 0.55, 2.4)
        cl.rot[1] = np.pi  # back to camera
        sit(j)
        if t > BUG_SIT + 0.8:
            j["shoulderL"].rot[:] = (0.2, 0, -1.15)  # arm toward the bug


def grokio_state(t, S):
    j, g = S["gj"], S["g"]
    g.rot[:] = 0
    base_scale = np.array((0.97, 1.06, 0.97))
    g.scale[:] = base_scale
    g.visible = t >= DESCEND[0] and t < GROKIO_FLY[1]

    if not g.visible:
        return
    if t < LAND:
        p = (t - DESCEND[0]) / (DESCEND[1] - DESCEND[0])
        g.pos[:] = (X_GROKIO_LAND, lerp(13.0, 0.0, smooth(0, 1, min(1, p))), 0)
        g.rot[1] = 0
        claudio.reset(j)
        j["shoulderL"].rot[:] = (0.3, 0, -0.2)
        j["shoulderR"].rot[:] = (0.3, 0, 0.2)
    elif t < FACEOFF[0]:
        g.pos[:] = (X_GROKIO_LAND, 0, 0)
        g.rot[1] = 0 if t < NAMEPLATE[0] + 1.2 else np.pi / 2 * 0 + (np.pi / 2 if False else 0)
        face(g, X_CLAUDIO_START)
        stance(j, t + 3)
        if LAND <= t < LAND + 0.35:
            j["pelvis"].pos[1] = 0.45 + 0.17 * (t - LAND) / 0.35  # landing crouch
    elif t < CHARGE:
        p = (t - FACEOFF[0]) / (FACEOFF[1] - FACEOFF[0])
        ang = 0.55 * np.sin(p * 2.6)
        g.pos[:] = (X_CLASH + 3.6 * np.cos(ang), 0, -1.6 * np.sin(ang) * 0 + 1.6 * np.sin(ang) * -1)
        face(g, S["c"].pos[0])
        stance(j, t + 1.7)
    elif t < CLASH:
        p = (t - CHARGE) / (CLASH - CHARGE)
        if p < 0.55:
            g.pos[:] = (lerp(10.6, 8.8, p / 0.55), 0, 0)
            claudio.run(j, t + 0.3, rate=13)
        else:
            k = (p - 0.55) / 0.45
            g.pos[:] = (lerp(8.8, X_CLASH + 0.45, k), 1.65 * smooth(0, 1, k), 0)
            uppercut(j, 0.4 + 0.6 * k)
        face(g, X_CLASH)
    elif t < CLASH_FREEZE[1]:
        g.pos[:] = (X_CLASH + 0.45, 1.65, 0)
        face(g, X_CLASH)
        uppercut(j, 1.0)
    elif t < KNOCKBACK_END:
        p = (t - CLASH_FREEZE[1]) / (KNOCKBACK_END - CLASH_FREEZE[1])
        g.pos[:] = (lerp(X_CLASH + 0.45, 11.0, smooth(0, 1, p)), 1.65 * (1 - p * p), 0)
        face(g, X_CLASH)
        knocked(j, t)
    elif t < MELEE[0]:  # throwing fireballs
        g.pos[:] = (11.0, 0, 0)
        face(g, S["c"].pos[0])
        stance(j, t)
        for ft in FIREBALLS:
            if ft - 0.3 <= t < ft + 0.25:
                p = (t - (ft - 0.3)) / 0.55
                j["shoulderR"].rot[:] = (-2.8 + 2.6 * p, 0, 0.3)
                j["torso"].rot[1] = 0.4 - 0.7 * p
        if STARSHOT_HIT <= t < STARSHOT_HIT + 0.6:  # takes the star
            g.pos[0] = 11.0 + 1.2 * min(1, (t - STARSHOT_HIT) / 0.3)
            knocked(j, t)
    elif t < PIPE_SMASH:
        g.pos[:] = (X_CLASH + 0.75, 0, 0)
        face(g, X_CLASH)
        punch(j, t + 0.29, rate=11)
        for ht in MELEE_HITS[0::2]:
            if ht <= t < ht + 0.18:
                g.pos[0] += 0.3
                j["head"].rot[2] = -0.3
    elif t < UPPERCUT1 + 0.35:  # strides after Claudio, uppercuts
        p = (t - PIPE_SMASH) / (UPPERCUT1 + 0.35 - PIPE_SMASH)
        g.pos[:] = (lerp(X_CLASH + 0.75, X_PIPE - 1.6, smooth(0, 1, p)), 0, 0)
        face(g, X_PIPE)
        if t < UPPERCUT1 - 0.3:
            claudio.run(j, t, rate=10)
        else:
            uppercut(j, (t - (UPPERCUT1 - 0.3)) / 0.65)
    elif t < DOWN[0]:  # watches him fly
        g.pos[:] = (X_PIPE - 1.6, 0, 0)
        face(g, 2.4)
        stance(j, t)
        j["head"].rot[0] = -0.35
    elif t < MEGA_THROW:  # stalks over, looms, charges
        if t < 34.0:
            p = (t - DOWN[0]) / (34.0 - DOWN[0])
            g.pos[:] = (lerp(X_PIPE - 1.6, 4.9, smooth(0, 1, p)), 0, 0)
            claudio.run(j, t, rate=6)  # slow menace walk
        else:
            g.pos[:] = (4.9, 0, 0)
            loom(j, t)
        face(g, 2.4)
    elif t < COMBO[0]:  # throw follow-through, then surprised
        g.pos[:] = (4.9, 0, 0)
        face(g, 2.4)
        p = min(1, (t - MEGA_THROW) / 0.4)
        j["shoulderR"].rot[:] = (-2.9 + 3.2 * p, 0, 0.35)
        j["torso"].rot[0] = 0.3 * p
    elif t < FINAL_HIT:  # eating the combo
        g.pos[:] = (5.6, 0.05 * abs(np.sin(t * 14)), 0)
        face(g, S["c"].pos[0])
        knocked(j, t)
        j["head"].rot[2] = 0.25 * np.sin(t * 17)
    elif t < FINAL_FREEZE[1]:
        g.pos[:] = (5.65, 0.8, 0)
        g.rot[2] = -0.5
        face(g, S["c"].pos[0])
        knocked(j, t)
    else:  # SKYWARD
        p = (t - FINAL_FREEZE[1]) / (GROKIO_FLY[1] - FINAL_FREEZE[1])
        g.pos[:] = (lerp(5.65, 9.5, p), 0.8 + 11.5 * p * p, lerp(0, 4, p))
        g.rot[:] = (p * 9, p * 13, p * 7)
        knocked(j, t)


def scene_state(t, S, rng):
    # blocks explode
    boom_on = BLOCKS_BOOM <= t
    for b in S["blocks"]:
        b.visible = not boom_on
    fx.animate_explosion(S["boom_blocks"], t - BLOCKS_BOOM, max_r=3.2)
    S["boom_blocks"].pos[:] = (X_BLOCKS, Y_BLOCKS, 0)
    fx.animate_debris(S["debris"], (X_BLOCKS, Y_BLOCKS, 0), t - BLOCKS_BOOM)

    # horizon boom (flagpole dies)
    S["flagpole"].visible = t < HORIZON_BOOM
    fx.animate_explosion(S["boom_horizon"], t - HORIZON_BOOM, max_r=7.0, life=1.6)
    S["boom_horizon"].pos[:] = (X_FLAG, 2.5, 6.0)

    # pipe dents
    if t >= PIPE_SMASH:
        k = min(1, (t - PIPE_SMASH) / 0.3)
        S["pipe"].rot[2] = 0.38 * k
        S["pipe"].pos[0] = X_PIPE + 0.5 * k

    # crater hill sinks
    if t >= HILL_CRASH:
        k = min(1, (t - HILL_CRASH) / 0.5)
        S["crater_hill"].scale[:] = (1, 1 - 0.45 * k, 1)
        S["crater"].visible = True

    # dust rings
    fx.animate_dust(S["dust"], t - LAND)
    S["dust"].pos[:] = (X_GROKIO_LAND, 0.05, 0)
    fx.animate_dust(S["dust2"], t - HILL_CRASH, life=1.0)
    S["dust2"].pos[:] = (2.4, 0.1, 1.8)

    # fires ignite progressively after hill crash
    for i, f in enumerate(S["fires"]):
        f.visible = t >= HILL_CRASH + i * 0.8
        fx.animate_fire(f, t, seed=i + 3)

    # fireballs
    fb = S["fireball"]
    fb.visible = False
    for fi, ft in enumerate(FIREBALLS):
        dur = 0.62
        if ft <= t < ft + dur:
            p = (t - ft) / dur
            fb.visible = True
            if fi < 2:
                fb.pos[:] = (lerp(10.4, 1.5, p), lerp(1.3, 1.0, p), 0)
            else:  # the lob that kills the blocks
                fb.pos[:] = (lerp(10.4, X_BLOCKS, p), 1.3 + 3.4 * arc(p), 0)
            fb.rot[1] = t * 9
            fb.rot[2] = np.pi / 2  # trail points along travel
    ss = S["starshot"]
    ss.visible = STARSHOT <= t < STARSHOT_HIT
    if ss.visible:
        p = (t - STARSHOT) / (STARSHOT_HIT - STARSHOT)
        ss.pos[:] = (lerp(4.2, 11.0, p), 1.3, 0)
        ss.rot[2] = t * 12

    # mega ball
    mg = S["mega"]
    if MEGA_CHARGE[0] <= t < MEGA_THROW:
        mg.visible = True
        p = (t - MEGA_CHARGE[0]) / (MEGA_CHARGE[1] - MEGA_CHARGE[0])
        mg.scale[:] = 0.25 + 2.3 * smooth(0, 1, p)
        mg.pos[:] = (4.9 + 0.05 * np.sin(t * 21), 4.3 + 0.5 * p, 0)
        mg.rot[1] = t * 2.2
    elif MEGA_THROW <= t < HORIZON_BOOM:
        mg.visible = True
        p = (t - MEGA_THROW) / (HORIZON_BOOM - MEGA_THROW)
        mg.pos[:] = (lerp(4.9, X_FLAG, p), lerp(4.5, 2.5, p), lerp(0, 6.0, p))
        mg.rot[1] = t * 6
    else:
        mg.visible = False

    # aura
    au = S["aura"]
    au.visible = POWERUP[0] + 0.5 <= t < COMBO[1]
    if au.visible:
        cl = S["c"]
        au.pos[:] = (cl.pos[0], 1.15 + cl.pos[1], cl.pos[2] + 0.6)
        au.scale[:] = 0.9 + 0.18 * np.sin(t * 13)
        au.rot[2] = t * 1.8

    # the flying cap (knocked off at hill crash, lands mid-arena)
    fc = S["flycap"]
    fc.visible = HILL_CRASH <= t < 34.8
    if fc.visible:
        p = min(1, (t - HILL_CRASH) / 0.9)
        fc.pos[:] = (lerp(2.6, 5.4, p), 0.25 + 1.8 * arc(p), 1.2)
        fc.rot[2] = p * 6

    # the bug: fetches the cap, delivers it, later sits with Claudio
    b = S["bug"]
    wob = np.sin(t * 14)
    if BUG_CAP[0] - 1.0 <= t < BUG_CAP[0] + 0.8:  # enters, reaches cap
        b.visible = True
        p = (t - (BUG_CAP[0] - 1.0)) / 1.8
        b.pos[:] = (lerp(-1.5, 5.4, smooth(0, 1, p)), 0.02 * abs(wob), 1.2)
        b.rot[1] = -np.pi / 2
    elif BUG_CAP[0] + 0.8 <= t < CAP_ON:  # carries it to Claudio
        b.visible = True
        S["bugcap"].visible = True
        p = (t - (BUG_CAP[0] + 0.8)) / (CAP_ON - BUG_CAP[0] - 0.8)
        b.pos[:] = (lerp(5.4, 3.0, smooth(0, 1, p)), 0.02 * abs(wob), lerp(1.2, 1.9, p))
        b.rot[1] = -np.pi / 2
    elif CAP_ON <= t < CAP_ON + 2.0:  # steps back, watches
        b.visible = True
        S["bugcap"].visible = False
        b.pos[:] = (2.2, 0.02 * abs(wob), 2.6)
        b.rot[1] = 0
    elif t >= BUG_SIT - 1.4:  # comes to sit
        b.visible = True
        p = min(1, (t - (BUG_SIT - 1.4)) / 1.4)
        b.pos[:] = (lerp(4.5, 6.55, smooth(0, 1, p)), 0.55 * p + 0.02 * abs(wob) * (1 - p),
                    lerp(1.6, 2.4, p))
        b.rot[1] = np.pi  # faces the sunset too
    else:
        b.visible = False
    if b.visible:
        for i in range(3):
            for s_, nm in ((-1, "L"), (1, "R")):
                b.find(f"leg{i}{nm}").rot[0] = 0.5 * wob * (1 if (i + (s_ > 0)) % 2 else -1)

    # cap back on claudio handled in claudio_state via cap.visible

    # shadows
    for key, actor in (("shadow_c", S["c"]), ("shadow_g", S["g"])):
        sh = S[key]
        sh.visible = actor.visible and actor.pos[1] < 4.0
        sh.pos[:] = (actor.pos[0], 0.035, actor.pos[2])
        k = max(0.35, 1.0 - actor.pos[1] * 0.15)
        sh.scale[:] = (k, 1, k)

    # storm clouds darken (recolor via scale trick not possible — leave geometry, sky sells it)


# ---------------- sky ----------------

def sky_for(t):
    if t < TITLE_END:
        k = t / TITLE_END
        return sky_gradient((int(96 - 40 * k), int(150 - 60 * k), int(236 - 90 * k)),
                            (int(168 - 40 * k), int(212 - 80 * k), (250 - 90 * k)))
    if t < AFTERMATH[0]:
        # storm; darkest during DOWN
        base = 0.75 if t < DOWN[0] else 1.0
        return sky_gradient((int(52 * base), int(58 * base), int(92 * base)),
                            (int(110 * base), int(112 * base), int(140 * base)))
    if t < END_CARD:
        p = smooth(0, 1, (t - AFTERMATH[0]) / 4.0)
        top = (int(52 + p * (150 - 52)), int(58 + p * (70 - 58)), int(92 + p * (90 - 92)))
        bot = (int(110 + p * (255 - 110)), int(112 + p * (150 - 112)), int(140 + p * (70 - 140)))
        return sky_gradient(top, bot)
    return sky_gradient((10, 8, 16), (24, 16, 24))


# ---------------- camera ----------------

def camera_at(t, S, rng):
    c, g = S["c"], S["g"]
    if t < TITLE_END:
        az = lerp(-0.6, 0.4, t / TITLE_END)
        return Camera((2 + 6 * np.sin(az), 1.8, -6 * np.cos(az)), (2.5, 1.4, 0), fov=44)
    if t < DESCEND[1]:  # wide: he falls from the sky
        return Camera((7, 3.4, -13), (8.5, 4.2, 0), fov=52)
    if t < NAMEPLATE[0] + 1.4:  # landing impact
        shake = 0.35 * max(0, 1 - (t - LAND) / 0.5) if t >= LAND else 0
        jx, jy = rng.uniform(-shake, shake, 2)
        return Camera((10.5 + jx, 2.4 + jy, -8.5), (X_GROKIO_LAND, 1.4, 0), fov=44)
    if t < NAMEPLATE[1] - 1.2:  # closeup grokio face
        return Camera((X_GROKIO_LAND + 0.4, 2.2, -3.4), (X_GROKIO_LAND, 2.05, 0), fov=38)
    if t < FACEOFF[1]:  # wide two-shot circling
        return Camera((X_CLASH, 2.8, -11.5), (X_CLASH, 1.8, 0), fov=48)
    if t < KNOCKBACK_END + 0.3:  # the clash
        push = 1.0 if t < CLASH else max(0, 1 - (t - CLASH) * 1.2)
        d = 10.5 - 2.5 * push * (t - CHARGE) / 3
        shake = 0.5 if CLASH <= t < CLASH_FREEZE[1] else 0
        jx, jy = rng.uniform(-shake, shake, 2)
        return Camera((X_CLASH + jx, 2.3 + jy, -max(7.4, d)), (X_CLASH, 1.7, 0), fov=46)
    if t < MELEE[0]:  # fireball exchange — wide side
        return Camera((X_CLASH, 2.9, -11.8), (X_CLASH, 2.1, 0), fov=50)
    if t < PIPE_SMASH:  # melee tight, shakes on hits
        shake = 0.4 if any(ht <= t < ht + 0.15 for ht in MELEE_HITS) else 0.06
        jx, jy = rng.uniform(-shake, shake, 2)
        return Camera((X_CLASH + jx, 2.2 + jy, -7.2), (X_CLASH, 1.7, 0), fov=44)
    if t < HILL_CRASH + 0.6:  # pipe smash + launch: wider
        return Camera((9, 3.2, -12.5), (9, 2.6, 0), fov=52)
    if t < POWERUP[0]:  # down + loom + mega ball: low dramatic (lying Claudio in frame)
        return Camera((2.0, 1.5, -8.4), (3.5, 1.9, 0), fov=48)
    if HORIZON_BOOM - 0.25 <= t < HORIZON_BOOM + 1.0:  # the kingdom dies: cut wide
        return Camera((0.0, 3.0, -10.0), (-9.0, 3.0, 4.0), fov=54)
    if t < COMBO[0]:  # powerup + dash
        shake = 0.25 if t > MEGA_THROW else 0.1 * np.sin(t * 30) * (t > POWERUP[0] + 0.5)
        jx, jy = rng.uniform(-abs(shake), abs(shake), 2)
        return Camera((3.4 + jx, 1.9 + jy, -8.8), (3.4, 1.6, 0), fov=46)
    if t < FINAL_FREEZE[1] + 0.2:  # combo + final hit: tight
        shake = 0.35 if t < FINAL_HIT else 0.15
        jx, jy = rng.uniform(-shake, shake, 2)
        return Camera((5.4 + jx, 1.9 + jy, -6.6), (5.5, 1.8, 0), fov=42)
    if t < AFTERMATH[0]:  # grokio skyward: tilt up
        p = (t - FINAL_FREEZE[1]) / (AFTERMATH[0] - FINAL_FREEZE[1])
        return Camera((6.5, 2 + 1.5 * p, -9), (lerp(6, 9, p), lerp(2.5, 9.5, smooth(0, 1, p)), 0),
                      fov=48)
    if t < SIT:  # the ruins pan
        p = smooth(0, 1, (t - AFTERMATH[0]) / (SIT - AFTERMATH[0]))
        return Camera((lerp(0, 11, p), 2.6, -10.5), (lerp(1, 12, p), 1.9, 0), fov=48)
    if t < END_CARD:  # sunset two-shot from behind, wide enough to breathe
        d = lerp(10.0, 8.6, smooth(0, 1, (t - SIT) / 5))
        return Camera((7.0, 2.6, 2.55 - d), (7.15, 1.5, 5.0), fov=46)
    return Camera((7, 2, -8), (7, 1.5, 0), fov=46)


# ---------------- overlays ----------------

def overlays(img, t, S, rng):
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)

    def px(xy, s, size, fill, outline=(20, 24, 40)):
        x, y = xy
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2)):
            d.text((x + dx, y + dy), s, font=gfx.F(size), fill=outline, anchor="mm")
        d.text((x, y), s, font=gfx.F(size), fill=fill, anchor="mm")

    # title
    if t < TITLE_END - 0.3:
        px((W // 2, 66), "SUPER CLAUDIO BROS. 5", 38, (255, 214, 70), (90, 30, 30))
        px((W // 2, 110), "EPISODE 3:  BROTHER VS BROTHER", 21, (255, 255, 255), (90, 30, 30))
        px((W // 2, 436), "(final episode)", 14, (220, 200, 200), (60, 20, 20))

    # lightning flashes
    for lt in LIGHTNING:
        if lt <= t < lt + 0.12:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 255, 255)), 0.75)
            d = ImageDraw.Draw(im)

    # nameplate
    if NAMEPLATE[0] <= t < NAMEPLATE[1]:
        a = min(1, (t - NAMEPLATE[0]) / 0.3)
        px((W // 2, H - 92), "SUPER GROKIO", 40,
           tuple(int(v * a) for v in (230, 60, 60)), (30, 10, 14))
        px((W // 2, H - 52), "the evil brother", 17,
           tuple(int(v * a) for v in (220, 210, 210)), (30, 10, 14))

    # HUD: hearts + kingdom%
    if TITLE_END <= t < END_CARD:
        ch, gh = hearts(t)

        def draw_hearts(x0, n, col):
            for i in range(3):
                cx = x0 + i * 26
                fill = col if i < n else (70, 60, 66)
                d.ellipse((cx - 8, 14, cx, 22), fill=fill)
                d.ellipse((cx, 14, cx + 8, 22), fill=fill)
                d.polygon([(cx - 8, 20), (cx + 8, 20), (cx, 32)], fill=fill)
        px((70, 16), "CLAUDIO", 15, (255, 255, 255))
        draw_hearts(120, ch, (235, 80, 80))
        px((W - 210, 16), "GROKIO", 15, (255, 255, 255))
        draw_hearts(W - 165, gh, (160, 60, 220))
        px((W // 2, 16), f"KINGDOM {kingdom_pct(t)}%", 15,
           (255, 255, 255) if kingdom_pct(t) > 50 else (255, 120, 90))

    # impact flashes + stars + rings
    events = [(CLASH, X_CLASH, 2.0), (FINAL_HIT, 5.6, 1.8)] + \
             [(ht, X_CLASH, 1.8) for ht in MELEE_HITS] + \
             [(STARSHOT_HIT, 11.0, 1.4), (PIPE_SMASH, X_CLASH - 0.5, 1.5),
              (UPPERCUT1 + 0.3, X_PIPE - 1.2, 1.5)]
    cam = camera_at(t, S, np.random.default_rng(int(t * FPS) * 17 + 3))
    Vm = cam.view()
    f_ = (W / 2) / np.tan(np.radians(cam.fov) / 2)

    def to_screen(wx, wy, wz=0.0):
        v = Vm @ (np.array([wx, wy, wz]) - cam.pos)
        z = max(v[2], 0.2)
        return v[0] / z * f_ + W / 2, -v[1] / z * f_ + H / 2

    for et, ex, ey in events:
        age = t - et
        if 0 <= age < 0.22:
            sx, sy = to_screen(ex, ey)
            fx.impact_star(d, sx, sy, 90 * (1 - age / 0.22) + 20)
        if 0 <= age < 0.5 and et in (CLASH, FINAL_HIT):
            sx, sy = to_screen(ex, ey)
            fx.shock_ring(d, sx, sy, age)
    # white flash frames on the biggest hits
    for et in (CLASH, BLOCKS_BOOM, HORIZON_BOOM, FINAL_HIT):
        if et <= t < et + 0.1:
            im = Image.blend(im, Image.new("RGB", im.size, (255, 245, 230)), 0.65)
            d = ImageDraw.Draw(im)
    # horizon boom: big glow
    if HORIZON_BOOM <= t < HORIZON_BOOM + 1.2:
        p = (t - HORIZON_BOOM) / 1.2
        sx, sy = to_screen(X_FLAG, 3, 6)
        r = 60 + 400 * p
        col = (255, int(200 - 120 * p), 60)
        d.ellipse((sx - r, sy - r * 0.6, sx + r, sy + r * 0.6), outline=col,
                  width=max(2, int(20 * (1 - p))))

    # speed lines during dash + combo
    if MEGA_THROW <= t < COMBO[1]:
        fx.speed_lines(d, W, H, W // 2, H // 2, rng, n=20)

    # powerup pulse
    if POWERUP[0] + 0.4 <= t < POWERUP[1]:
        k = 0.14 + 0.1 * np.sin(t * 22)
        im = Image.blend(im, Image.new("RGB", im.size, (255, 170, 100)), max(0, k))
        d = ImageDraw.Draw(im)

    # twinkle when grokio blinks out
    if TWINKLE <= t < TWINKLE + 0.7:
        sx, sy = to_screen(9.5, 12.3, 4)
        fx.twinkle(d, sx, sy, t - TWINKLE)

    # aftermath text
    if TEXT_WINS <= t < END_CARD:
        px((W // 2, 90), "CLAUDIO WINS.", 34, (255, 240, 200))
    if TEXT_COST <= t < END_CARD:
        px((W // 2, 132), "...but at what cost?", 19, (230, 200, 180))

    # end card
    if t >= END_CARD:
        im = Image.new("RGB", im.size, (8, 6, 10))
        d = ImageDraw.Draw(im)
        a = smooth(0, 1, (t - END_CARD) / 0.5)
        px((W // 2, 120), "A WINNER IS CLAUDIO", 40,
           tuple(int(v * a) for v in (255, 214, 70)), (70, 30, 10))
        px((W // 2, 196), "THE MUSHROOM KINGDOM", 22,
           tuple(int(v * a) for v in (240, 240, 240)))
        px((W // 2, 228), "1985 - 2026", 17, tuple(int(v * a) for v in (170, 170, 175)))
        px((W // 2, 300), "kingdom restoration DLC sold separately", 15,
           tuple(int(v * a) for v in (150, 150, 160)))
        if t > END_CARD + 1.4 and int(t * 2) % 2 == 0:
            px((W // 2, 386), "INSERT 999,999 TOKENS TO REBUILD", 17, (255, 214, 70),
               (70, 30, 10))
    return np.asarray(im)


# ---------------- main ----------------

def frame_at(t, root, S):
    rng = np.random.default_rng(int(t * FPS) * 23 + 7)
    claudio_state(t, S)
    grokio_state(t, S)
    scene_state(t, S, rng)
    cam = camera_at(t, S, rng)
    img = render(root, cam, sky=sky_for(t), fog_color=None, fog_dist=95)
    return overlays(img, t, S, rng)


def main(out_name="ep3_silent.mp4"):
    root, S = build_scene()
    nfr = int(TOTAL * FPS)
    out_path = os.path.join(HERE, "out", out_name)
    log = open(os.path.join(HERE, "out", "ffmpeg_ep3.log"), "w")
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "fast", "-crf", "20",
           "-pix_fmt", "yuv420p", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    for fi in range(nfr):
        t = fi / FPS
        img = frame_at(t, root, S)
        proc.stdin.write(np.ascontiguousarray(img, dtype=np.uint8).tobytes())
        if fi % 200 == 0:
            print(f"frame {fi}/{nfr} ({t:.1f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print("done:", out_path)


if __name__ == "__main__":
    main(*(sys.argv[1:] or []))
