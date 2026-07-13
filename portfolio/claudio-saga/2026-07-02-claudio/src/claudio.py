"""Claudio — the Newest AI Brother. Low-poly model + FK rig + pose library."""
import numpy as np

from engine import Node, box, cylinder, merge, recolor, tf, uv_sphere

# palette
CAP = (235, 118, 48)        # the orange hat
SHIRT = (217, 119, 87)      # claude coral
OVERALLS = (96, 66, 50)     # warm brown
GLOVE = (248, 246, 240)
SHOE = (74, 50, 38)
SKIN = (247, 205, 165)
STACHE = (56, 38, 28)
EYE_W = (250, 250, 250)
PUPIL = (40, 30, 60)
GOLD = (250, 200, 60)


def build():
    """Returns (root, joints dict). Claudio stands ~1.7 units tall at origin."""
    root = Node("claudio")
    pelvis = root.add(Node("pelvis", pos=(0, 0.62, 0)))

    # legs (hip joints on pelvis)
    for side, sx in (("L", -1), ("R", 1)):
        hip = pelvis.add(Node(f"hip{side}", pos=(sx * 0.17, -0.05, 0)))
        leg = merge(
            tf(cylinder(0.13, 0.42, 8, OVERALLS), pos=(0, -0.2, 0)),
            tf(uv_sphere(0.17, 8, 6, SHOE, squash=0.62), pos=(0, -0.45, 0.07)),
        )
        hip.mesh(*leg)

    # torso: overalls belly + coral chest + buttons
    torso = pelvis.add(Node("torso", pos=(0, 0.12, 0)))
    body = merge(
        tf(uv_sphere(0.46, 12, 9, OVERALLS, squash=0.85), pos=(0, 0.12, 0)),
        tf(uv_sphere(0.40, 12, 8, SHIRT, squash=0.75), pos=(0, 0.42, 0)),
        # overalls bib + buttons
        tf(box(0.36, 0.26, 0.07, OVERALLS), pos=(0, 0.42, -0.30)),
        tf(uv_sphere(0.05, 6, 5, GOLD), pos=(-0.11, 0.47, -0.345)),
        tf(uv_sphere(0.05, 6, 5, GOLD), pos=(0.11, 0.47, -0.345)),
    )
    torso.mesh(*body)

    # arms (shoulder joints)
    for side, sx in (("L", -1), ("R", 1)):
        sh = torso.add(Node(f"shoulder{side}", pos=(sx * 0.42, 0.48, 0)))
        arm = merge(
            tf(cylinder(0.105, 0.4, 8, SHIRT), pos=(sx * 0.05, -0.2, 0), rot=(0, 0, -sx * 0.25)),
            tf(uv_sphere(0.15, 8, 6, GLOVE), pos=(sx * 0.11, -0.44, 0)),
        )
        sh.mesh(*arm)

    # head + face + cap
    head = torso.add(Node("head", pos=(0, 0.78, 0)))
    face = merge(
        tf(uv_sphere(0.44, 14, 11, SKIN), pos=(0, 0.06, 0)),
        # ears
        tf(uv_sphere(0.09, 7, 5, SKIN), pos=(-0.43, 0.03, 0)),
        tf(uv_sphere(0.09, 7, 5, SKIN), pos=(0.43, 0.03, 0)),
        # nose (forward = -z toward default camera)
        tf(uv_sphere(0.15, 8, 6, SKIN), pos=(0, -0.03, -0.46)),
        # the magnificent mustache: three squashed pads per side sweep down
        tf(uv_sphere(0.17, 8, 6, STACHE, squash=0.42), pos=(-0.14, -0.16, -0.42)),
        tf(uv_sphere(0.17, 8, 6, STACHE, squash=0.42), pos=(0.14, -0.16, -0.42)),
        tf(uv_sphere(0.11, 8, 6, STACHE, squash=0.45), pos=(-0.29, -0.20, -0.34)),
        tf(uv_sphere(0.11, 8, 6, STACHE, squash=0.45), pos=(0.29, -0.20, -0.34)),
        # eyes: whites + pupils (proud of the head surface)
        tf(uv_sphere(0.105, 8, 6, EYE_W, squash=1.25), pos=(-0.15, 0.16, -0.415)),
        tf(uv_sphere(0.105, 8, 6, EYE_W, squash=1.25), pos=(0.15, 0.16, -0.415)),
        tf(uv_sphere(0.048, 6, 5, PUPIL), pos=(-0.14, 0.15, -0.50)),
        tf(uv_sphere(0.048, 6, 5, PUPIL), pos=(0.14, 0.15, -0.50)),
        # sideburns + back hair under cap
        tf(uv_sphere(0.10, 7, 5, STACHE, squash=1.1), pos=(-0.36, 0.02, -0.12)),
        tf(uv_sphere(0.10, 7, 5, STACHE, squash=1.1), pos=(0.36, 0.02, -0.12)),
        tf(uv_sphere(0.30, 10, 6, STACHE, squash=0.6), pos=(0, 0.05, 0.22)),
    )
    head.mesh(*face)

    cap = head.add(Node("cap", pos=(0, 0.30, 0)))
    capm = merge(
        # dome wraps OVER the skull (r > head 0.44)
        tf(uv_sphere(0.51, 12, 8, CAP, squash=0.58), pos=(0, 0.06, 0.02)),
        # brim: flattened disc sticking forward
        tf(cylinder(0.34, 0.06, 12, CAP), pos=(0, 0.0, -0.42), scale=(1.05, 1.0, 1.25)),
        # emblem: white disc + tiny coral starburst (two crossed slats)
        tf(cylinder(0.12, 0.05, 10, EYE_W), pos=(0, 0.16, -0.45), rot=(1.15, 0, 0)),
        tf(box(0.035, 0.16, 0.03, CAP), pos=(0, 0.16, -0.49), rot=(0.42, 0, 0)),
        tf(box(0.035, 0.16, 0.03, CAP), pos=(0, 0.16, -0.49), rot=(0.42, 0, np.pi / 2)),
    )
    cap.mesh(*capm)

    joints = {n: root.find(n) for n in
              ("pelvis", "hipL", "hipR", "torso", "shoulderL", "shoulderR", "head", "cap")}
    joints["root"] = root
    return root, joints


# ---------------- pose library ----------------
# Convention: Claudio faces -z by default; animate.py rotates root to face travel.

def reset(j):
    for n in ("hipL", "hipR", "torso", "shoulderL", "shoulderR", "head"):
        j[n].rot[:] = 0
    j["pelvis"].pos[1] = 0.62
    j["torso"].pos[1] = 0.12


def idle(j, t):
    reset(j)
    j["pelvis"].pos[1] = 0.62 + 0.012 * np.sin(t * 2.4)
    j["torso"].rot[0] = 0.03 * np.sin(t * 2.4)
    j["head"].rot[0] = 0.04 * np.sin(t * 1.7 + 1)
    j["shoulderL"].rot[2] = -0.12
    j["shoulderR"].rot[2] = 0.12


def wave(j, t, amt=1.0):
    idle(j, t)
    # right arm up, hand wag
    j["shoulderR"].rot[0] = 0
    j["shoulderR"].rot[2] = amt * (2.6 + 0.35 * np.sin(t * 9))
    j["head"].rot[2] = 0.08 * amt


def run(j, t, rate=9.0):
    reset(j)
    ph = t * rate
    swing = np.sin(ph)
    j["hipL"].rot[0] = 0.9 * swing
    j["hipR"].rot[0] = -0.9 * swing
    j["shoulderL"].rot[0] = -0.8 * swing
    j["shoulderR"].rot[0] = 0.8 * swing
    j["shoulderL"].rot[2] = -0.25
    j["shoulderR"].rot[2] = 0.25
    j["torso"].rot[0] = 0.14
    j["pelvis"].pos[1] = 0.62 + 0.05 * abs(np.cos(ph))
    j["head"].rot[0] = -0.06


def jump(j, tuck=1.0):
    reset(j)
    j["hipL"].rot[0] = 1.15 * tuck
    j["hipR"].rot[0] = 0.35 * tuck
    j["shoulderR"].rot[2] = 2.5 * tuck   # fist up!
    j["shoulderL"].rot[0] = 0.7 * tuck
    j["torso"].rot[0] = 0.10 * tuck


def stomp(j, k=1.0):
    reset(j)
    j["hipL"].rot[0] = -0.25 * k
    j["hipR"].rot[0] = -0.25 * k
    j["shoulderL"].rot[2] = -1.9 * k
    j["shoulderR"].rot[2] = 1.9 * k
    j["torso"].rot[0] = 0.22 * k


def victory(j, t):
    reset(j)
    hop = abs(np.sin(t * 5))
    j["pelvis"].pos[1] = 0.62 + 0.10 * hop
    j["shoulderL"].rot[2] = -2.7
    j["shoulderR"].rot[2] = 2.7
    j["head"].rot[0] = -0.15


def look_up(j, amt=1.0):
    j["head"].rot[0] = -0.5 * amt


def droop(j, t, amt=1.0):
    """Waiting politely — slight sag, hands together-ish."""
    reset(j)
    j["pelvis"].pos[1] = 0.60 + 0.008 * np.sin(t * 2.2)
    j["torso"].rot[0] = 0.10 * amt
    j["head"].rot[0] = 0.14 * amt
    j["shoulderL"].rot[0] = 0.5
    j["shoulderR"].rot[0] = 0.5
