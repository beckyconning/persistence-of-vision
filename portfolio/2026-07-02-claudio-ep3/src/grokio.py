"""SUPER GROKIO — the evil brother. Claudio's silhouette, villain's everything else."""
import numpy as np

from engine import Node, box, cylinder, merge, tf, uv_sphere

# villain palette
CAP = (38, 36, 42)          # black cap
SHIRT = (150, 40, 46)       # aggressive red
OVERALLS = (52, 50, 58)     # charcoal
GLOVE = (30, 28, 34)        # black gloves
SHOE = (28, 26, 30)
SKIN = (232, 190, 150)      # a shade paler
STACHE = (24, 20, 18)       # jet black
EYE_W = (250, 250, 250)
PUPIL = (200, 30, 30)       # red
BUCKLE = (200, 200, 210)    # silver


def build():
    """Same rig contract as claudio.build(): returns (root, joints)."""
    root = Node("grokio")
    pelvis = root.add(Node("pelvis", pos=(0, 0.62, 0)))

    for side, sx in (("L", -1), ("R", 1)):
        hip = pelvis.add(Node(f"hip{side}", pos=(sx * 0.17, -0.05, 0)))
        leg = merge(
            tf(cylinder(0.13, 0.46, 8, OVERALLS), pos=(0, -0.22, 0)),
            tf(uv_sphere(0.17, 8, 6, SHOE, squash=0.62), pos=(0, -0.49, 0.07)),
        )
        hip.mesh(*leg)

    torso = pelvis.add(Node("torso", pos=(0, 0.12, 0)))
    body = merge(
        tf(uv_sphere(0.44, 12, 9, OVERALLS, squash=0.9), pos=(0, 0.14, 0)),
        tf(uv_sphere(0.39, 12, 8, SHIRT, squash=0.78), pos=(0, 0.44, 0)),
        tf(box(0.34, 0.24, 0.07, OVERALLS), pos=(0, 0.44, -0.29)),
        # silver buckles instead of gold buttons
        tf(box(0.09, 0.09, 0.05, BUCKLE), pos=(-0.11, 0.49, -0.335), rot=(0, 0, np.pi / 4)),
        tf(box(0.09, 0.09, 0.05, BUCKLE), pos=(0.11, 0.49, -0.335), rot=(0, 0, np.pi / 4)),
    )
    torso.mesh(*body)

    for side, sx in (("L", -1), ("R", 1)):
        sh = torso.add(Node(f"shoulder{side}", pos=(sx * 0.42, 0.50, 0)))
        arm = merge(
            tf(cylinder(0.10, 0.42, 8, SHIRT), pos=(sx * 0.05, -0.21, 0), rot=(0, 0, -sx * 0.25)),
            tf(uv_sphere(0.15, 8, 6, GLOVE), pos=(sx * 0.11, -0.46, 0)),
        )
        sh.mesh(*arm)

    head = torso.add(Node("head", pos=(0, 0.80, 0)))
    face = merge(
        tf(uv_sphere(0.43, 14, 11, SKIN), pos=(0, 0.06, 0)),
        tf(uv_sphere(0.09, 7, 5, SKIN), pos=(-0.42, 0.03, 0)),
        tf(uv_sphere(0.09, 7, 5, SKIN), pos=(0.42, 0.03, 0)),
        # sharper nose
        tf(uv_sphere(0.13, 8, 6, SKIN, squash=0.9), pos=(0, -0.02, -0.47)),
        # VILLAIN mustache: thin pads angled UP at the ends (the twirl)
        tf(uv_sphere(0.14, 8, 6, STACHE, squash=0.34), pos=(-0.13, -0.15, -0.41)),
        tf(uv_sphere(0.14, 8, 6, STACHE, squash=0.34), pos=(0.13, -0.15, -0.41)),
        tf(uv_sphere(0.09, 8, 6, STACHE, squash=0.36), pos=(-0.30, -0.10, -0.33)),
        tf(uv_sphere(0.09, 8, 6, STACHE, squash=0.36), pos=(0.30, -0.10, -0.33)),
        tf(uv_sphere(0.055, 6, 5, STACHE), pos=(-0.40, -0.04, -0.27)),
        tf(uv_sphere(0.055, 6, 5, STACHE), pos=(0.40, -0.04, -0.27)),
        # narrowed eyes + RED pupils
        tf(uv_sphere(0.10, 8, 6, EYE_W, squash=0.85), pos=(-0.15, 0.15, -0.405)),
        tf(uv_sphere(0.10, 8, 6, EYE_W, squash=0.85), pos=(0.15, 0.15, -0.405)),
        tf(uv_sphere(0.05, 6, 5, PUPIL), pos=(-0.14, 0.14, -0.485)),
        tf(uv_sphere(0.05, 6, 5, PUPIL), pos=(0.14, 0.14, -0.485)),
        # ANGRY BROWS: angled dark slats over the eyes
        tf(box(0.22, 0.06, 0.06, STACHE), pos=(-0.15, 0.30, -0.40), rot=(0, 0, -0.45)),
        tf(box(0.22, 0.06, 0.06, STACHE), pos=(0.15, 0.30, -0.40), rot=(0, 0, 0.45)),
        # black sideburns + back hair
        tf(uv_sphere(0.10, 7, 5, STACHE, squash=1.1), pos=(-0.35, 0.02, -0.12)),
        tf(uv_sphere(0.10, 7, 5, STACHE, squash=1.1), pos=(0.35, 0.02, -0.12)),
        tf(uv_sphere(0.30, 10, 6, STACHE, squash=0.6), pos=(0, 0.05, 0.22)),
    )
    head.mesh(*face)

    cap = head.add(Node("cap", pos=(0, 0.30, 0)))
    capm = merge(
        tf(uv_sphere(0.50, 12, 8, CAP, squash=0.58), pos=(0, 0.06, 0.02)),
        tf(cylinder(0.34, 0.06, 12, CAP), pos=(0, 0.0, -0.42), scale=(1.05, 1.0, 1.25)),
        # emblem: white disc + jagged black X
        tf(cylinder(0.12, 0.05, 10, EYE_W), pos=(0, 0.16, -0.44), rot=(1.15, 0, 0)),
        tf(box(0.045, 0.17, 0.03, CAP), pos=(0, 0.16, -0.48), rot=(0.42, 0, np.pi / 4)),
        tf(box(0.045, 0.17, 0.03, CAP), pos=(0, 0.16, -0.48), rot=(0.42, 0, -np.pi / 4)),
    )
    cap.mesh(*capm)

    joints = {n: root.find(n) for n in
              ("pelvis", "hipL", "hipR", "torso", "shoulderL", "shoulderR", "head", "cap")}
    joints["root"] = root
    # a touch taller and leaner than his brother
    root.scale[:] = (0.97, 1.06, 0.97)
    return root, joints
