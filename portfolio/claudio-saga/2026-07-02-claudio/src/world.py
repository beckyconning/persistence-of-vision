"""The bootleg mushroom kingdom: ground, props, enemies, and pixel-quad text."""
import numpy as np

from engine import Node, box, cylinder, merge, recolor, tf, uv_sphere

GRASS_A = (112, 192, 88)
GRASS_B = (100, 178, 78)
HILL = (78, 156, 92)
BUSH = (66, 160, 74)
CLOUD = (250, 250, 252)
BLOCK_GOLD = (238, 176, 50)
BLOCK_DARK = (120, 74, 20)
BRICK = (176, 96, 60)
BRICK_DARK = (120, 60, 36)
PIPE = (72, 176, 72)
PIPE_DARK = (52, 140, 52)
POLE = (190, 195, 200)
FLAG_BG = (246, 240, 226)
CORAL = (217, 119, 87)
COIN = (252, 208, 60)
BUG_BODY = (150, 92, 190)
BUG_DARK = (90, 50, 120)
PANEL_BG = (248, 244, 234)
PANEL_INK = (70, 56, 46)
SHADOW = (62, 120, 56)

# ---------------- 3x5 pixel font (bootleg-grade) ----------------
GLYPHS = {
    "A": "010 101 111 101 101", "B": "110 101 110 101 110", "C": "011 100 100 100 011",
    "D": "110 101 101 101 110", "E": "111 100 110 100 111", "F": "111 100 110 100 100",
    "G": "111 100 101 101 111", "H": "101 101 111 101 101", "I": "111 010 010 010 111",
    "K": "101 110 100 110 101", "L": "100 100 100 100 111", "M": "101 111 101 101 101",
    "N": "110 101 101 101 101", "O": "111 101 101 101 111", "P": "110 101 110 100 100",
    "R": "110 101 110 110 101", "S": "011 100 010 001 110", "T": "111 010 010 010 010",
    "U": "101 101 101 101 111", "V": "101 101 101 101 010", "W": "101 101 101 111 101",
    "X": "101 101 010 101 101", "Y": "101 101 010 010 010", "Z": "111 001 010 100 111",
    "?": "111 001 010 000 010", "!": "010 010 010 000 010", ">": "100 010 001 010 100",
    "-": "000 000 111 000 000", ".": "000 000 000 000 010", "1": "010 110 010 010 111",
    "5": "111 100 110 001 110", "0": "111 101 101 101 111",
    "/": "001 001 010 100 100", "+": "000 010 111 010 000",
    "✓": "000 001 001 110 010", " ": "000 000 000 000 000",
}


def text3d(s, px=0.1, color=PANEL_INK, depth=0.05):
    """A string as a mesh of tiny cubes, reading correctly from the -z side
    (camera looks along +z, so screen-right = world -x)."""
    meshes = []
    cx = 0.0
    for ch in s.upper():
        g = GLYPHS.get(ch, GLYPHS["?"]).split()
        for r, row in enumerate(g):
            for c, bit in enumerate(row):
                if bit == "1":
                    meshes.append(tf(box(px, px, depth, color),
                                     pos=(-(cx + c * px), -r * px, 0)))
        cx += 4 * px
    if not meshes:
        meshes = [tf(box(0.001, 0.001, 0.001, color), pos=(0, 0, 0))]
    V, F, C = merge(*meshes)
    return V, F, C


def text_node(s, px=0.1, color=PANEL_INK, center=True, depth=0.05):
    n = Node(f"txt_{s[:6]}")
    V, F, C = text3d(s, px, color, depth)
    if center:
        V = V - [(V[:, 0].min() + V[:, 0].max()) / 2, 0, 0]
    n.mesh(V, F, C)
    return n


# ---------------- terrain / scenery ----------------

def ground(x0=-40, x1=100, z0=-14, z1=40, tile=2.0):
    """Checkered tile ground (small tris dodge the near-plane cull)."""
    n = Node("ground")
    verts, faces, cols = [], [], []
    nx = int((x1 - x0) / tile)
    nz = int((z1 - z0) / tile)
    for i in range(nx):
        for k in range(nz):
            x = x0 + i * tile
            z = z0 + k * tile
            b = len(verts)
            verts += [(x, 0, z), (x + tile, 0, z), (x + tile, 0, z + tile), (x, 0, z + tile)]
            faces += [[b, b + 2, b + 1], [b, b + 3, b + 2]]
            c = GRASS_A if (i + k) % 2 == 0 else GRASS_B
            cols += [c, c]
    n.mesh(np.array(verts, float), np.array(faces, np.int32), np.array(cols, float))
    return n


def hill(x, z, r=6.0, h=0.55):
    n = Node("hill", pos=(x, 0, z))
    n.mesh(*uv_sphere(r, 14, 8, HILL, squash=h))
    return n


def cloud(x, y, z, s=1.0):
    n = Node("cloud", pos=(x, y, z), scale=s)
    m = merge(
        tf(uv_sphere(1.0, 9, 6, CLOUD, squash=0.75), pos=(0, 0, 0)),
        tf(uv_sphere(0.75, 9, 6, CLOUD, squash=0.75), pos=(-1.2, -0.1, 0.2)),
        tf(uv_sphere(0.8, 9, 6, CLOUD, squash=0.75), pos=(1.15, -0.08, -0.1)),
    )
    n.mesh(*m)
    return n


def bush(x, z, s=1.0):
    n = Node("bush", pos=(x, 0, z), scale=s)
    m = merge(
        tf(uv_sphere(0.55, 9, 6, BUSH, squash=0.8), pos=(0, 0.35, 0)),
        tf(uv_sphere(0.4, 9, 6, BUSH, squash=0.8), pos=(-0.6, 0.28, 0)),
        tf(uv_sphere(0.42, 9, 6, BUSH, squash=0.8), pos=(0.6, 0.28, 0)),
    )
    n.mesh(*m)
    return n


# ---------------- blocks ----------------

def qblock(x, y, z=0.0):
    """? block: gold cube, corner rivets, pixel '?' on front and back."""
    n = Node("qblock", pos=(x, y, z))
    m = [box(1.3, 1.3, 1.3, BLOCK_GOLD)]
    for fz in (-0.66, 0.66):
        for cx, cy in ((-0.5, -0.5), (0.5, -0.5), (-0.5, 0.5), (0.5, 0.5)):
            m.append(tf(box(0.12, 0.12, 0.06, BLOCK_DARK), pos=(cx, cy, fz)))
    q_front = tf(text3d("?", px=0.17, color=BLOCK_DARK, depth=0.06),
                 pos=(0.17 * 1.5 - 0.08, 0.42, -0.66))
    q_back = tf(text3d("?", px=0.17, color=BLOCK_DARK, depth=0.06),
                pos=(0.17 * 1.5 - 0.08, 0.42, 0.66))
    m += [q_front, q_back]
    n.mesh(*merge(*m))
    return n


def brick(x, y, z=0.0):
    n = Node("brick", pos=(x, y, z))
    m = [box(1.3, 1.3, 1.3, BRICK)]
    for gy in (-0.22, 0.22):
        m.append(tf(box(1.32, 0.07, 1.32, BRICK_DARK), pos=(0, gy, 0)))
    n.mesh(*merge(*m))
    return n


def used_block(x, y, z=0.0):
    n = Node("used", pos=(x, y, z))
    n.mesh(*box(1.3, 1.3, 1.3, (150, 110, 70)))
    return n


# ---------------- pipe / flag / coin ----------------

def pipe(x, z=0.0, h=2.4):
    n = Node("pipe", pos=(x, 0, z))
    m = merge(
        tf(cylinder(0.95, h, 14, PIPE), pos=(0, h / 2, 0)),
        tf(cylinder(1.12, 0.55, 14, PIPE_DARK), pos=(0, h + 0.27, 0)),
    )
    n.mesh(*m)
    return n


def flagpole(x, z=0.0, h=9.0):
    n = Node("flagpole", pos=(x, 0, z))
    m = merge(
        tf(cylinder(0.09, h, 8, POLE), pos=(0, h / 2, 0)),
        tf(uv_sphere(0.28, 9, 7, COIN), pos=(0, h + 0.2, 0)),
    )
    n.mesh(*m)
    flag = n.add(Node("flag", pos=(0, h - 1.0, 0)))
    fm = [tf(box(1.9, 1.5, 0.06, FLAG_BG), pos=(-1.05, 0, 0))]
    # coral starburst on both sides
    for fz in (-0.05, 0.05):
        fm.append(tf(box(0.16, 1.0, 0.05, CORAL), pos=(-1.05, 0, fz)))
        fm.append(tf(box(1.0, 0.16, 0.05, CORAL), pos=(-1.05, 0, fz)))
        fm.append(tf(box(0.13, 0.7, 0.05, CORAL), pos=(-1.05, 0, fz), rot=(0, 0, np.pi / 4)))
        fm.append(tf(box(0.13, 0.7, 0.05, CORAL), pos=(-1.05, 0, fz), rot=(0, 0, -np.pi / 4)))
    flag.mesh(*merge(*fm))
    return n


def coin():
    n = Node("coin")
    m = merge(
        cylinder(0.42, 0.1, 12, COIN),
        tf(cylinder(0.2, 0.12, 10, (255, 235, 140)), pos=(0, 0, 0)),
    )
    V, F, C = m
    # coins face the camera: rotate disc upright (axis z->y)
    n.mesh(*tf((V, F, C), rot=(np.pi / 2, 0, 0)))
    n.visible = False
    return n


# ---------------- the BUG ----------------

def bug():
    """A software bug. Six legs, sad antennae, walks. Stompable."""
    root = Node("bug")
    body = root.add(Node("bug_body", pos=(0, 0.42, 0)))
    m = [tf(uv_sphere(0.5, 11, 8, BUG_BODY, squash=0.78), pos=(0, 0, 0)),
         tf(uv_sphere(0.34, 9, 6, BUG_DARK, squash=0.8), pos=(0, 0.1, 0.38)),
         # eyes (big, worried)
         tf(uv_sphere(0.14, 8, 6, (252, 252, 252), squash=1.2), pos=(-0.18, 0.18, -0.40)),
         tf(uv_sphere(0.14, 8, 6, (252, 252, 252), squash=1.2), pos=(0.18, 0.18, -0.40)),
         tf(uv_sphere(0.06, 6, 5, (30, 20, 40)), pos=(-0.16, 0.16, -0.52)),
         tf(uv_sphere(0.06, 6, 5, (30, 20, 40)), pos=(0.16, 0.16, -0.52)),
         # antennae
         tf(box(0.05, 0.4, 0.05, BUG_DARK), pos=(-0.14, 0.5, -0.25), rot=(0.4, 0, 0.3)),
         tf(box(0.05, 0.4, 0.05, BUG_DARK), pos=(0.14, 0.5, -0.25), rot=(0.4, 0, -0.3)),
         tf(uv_sphere(0.07, 6, 5, BUG_BODY), pos=(-0.25, 0.68, -0.32)),
         tf(uv_sphere(0.07, 6, 5, BUG_BODY), pos=(0.25, 0.68, -0.32))]
    body.mesh(*merge(*m))
    for i, lz in enumerate((-0.28, 0.0, 0.28)):
        for sx in (-1, 1):
            leg = root.add(Node(f"leg{i}{'L' if sx < 0 else 'R'}",
                                pos=(sx * 0.42, 0.3, lz)))
            leg.mesh(*tf(box(0.09, 0.5, 0.09, BUG_DARK), pos=(sx * 0.08, -0.18, 0),
                         rot=(0, 0, -sx * 0.5)))
    return root


def bug_flat():
    """Post-stomp pancake, with a small ✓."""
    n = Node("bug_flat")
    m = merge(
        tf(uv_sphere(0.62, 11, 6, BUG_BODY, squash=0.16), pos=(0, 0.09, 0)),
        tf(uv_sphere(0.16, 8, 4, (252, 252, 252), squash=0.3), pos=(-0.2, 0.14, -0.3)),
        tf(uv_sphere(0.16, 8, 4, (252, 252, 252), squash=0.3), pos=(0.2, 0.14, -0.3)),
        tf(box(0.09, 0.02, 0.09, (30, 20, 40)), pos=(-0.2, 0.19, -0.3)),
        tf(box(0.09, 0.02, 0.09, (30, 20, 40)), pos=(0.2, 0.19, -0.3)),
    )
    n.mesh(*m)
    n.visible = False
    return n


# ---------------- permission panel ----------------

def panel(x, y, z=0.0):
    """Floating permission prompt. Children: ask / yes states."""
    root = Node("panel", pos=(x, y, z))
    back = root.add(Node("panel_back"))
    back.mesh(*merge(
        tf(box(6.2, 2.7, 0.12, PANEL_INK), pos=(0, 0, 0.02)),
        tf(box(6.0, 2.5, 0.12, PANEL_BG), pos=(0, 0, -0.04)),
    ))
    ask = root.add(Node("panel_ask"))
    t1 = text_node("ALLOW CLAUDIO TO", px=0.085, color=PANEL_INK)
    t1.pos[:] = (0, 0.90, -0.12)
    t2 = text_node("HIT THIS BLOCK?", px=0.085, color=PANEL_INK)
    t2.pos[:] = (0, 0.35, -0.12)
    t3 = text_node("> YES", px=0.13, color=(60, 140, 60))
    t3.pos[:] = (1.0, -0.35, -0.12)
    t4 = text_node("NO", px=0.13, color=(150, 60, 50))
    t4.pos[:] = (-1.2, -0.35, -0.12)
    for t in (t1, t2, t3, t4):
        ask.add(t)
    yes = root.add(Node("panel_yes"))
    ty = text_node("✓ ALLOWED", px=0.16, color=(60, 140, 60))
    ty.pos[:] = (0, 0.25, -0.12)
    yes.add(ty)
    yes.visible = False
    root.visible = False
    return root


def shadow_blob():
    n = Node("shadow")
    n.mesh(*cylinder(0.55, 0.02, 12, SHADOW))
    return n


def bugfixed_sign():
    n = Node("bugfixed", pos=(0, 0, 0))
    t = text_node("BUG FIXED!", px=0.14, color=(255, 255, 255), depth=0.06)
    t.pos[:] = (0, 0.3, 0)
    n.add(t)
    n.visible = False
    return n
