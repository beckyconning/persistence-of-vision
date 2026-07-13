"""Battle FX for ep3: projectiles, explosions, debris, fires, dust, aura, 2D impact kit."""
import numpy as np
from PIL import ImageDraw

from engine import Node, box, cylinder, merge, tf, uv_sphere

FIRE_CORE = (255, 230, 120)
FIRE_MID = (250, 140, 50)
FIRE_DARK = (180, 60, 30)
SMOKE = (132, 124, 120)
DARKBALL = (60, 30, 90)
DARKBALL_RIM = (150, 60, 200)
CORAL = (217, 119, 87)
DUST = (210, 190, 160)


# ---------------- projectiles ----------------

def fireball(dark=True):
    """Grokio's dark orb (or Claudio's coral star-shot)."""
    n = Node("fireball")
    if dark:
        m = merge(
            uv_sphere(0.32, 10, 7, DARKBALL),
            tf(uv_sphere(0.2, 8, 6, DARKBALL_RIM), pos=(0, 0, 0.28)),
            tf(uv_sphere(0.13, 8, 6, DARKBALL_RIM), pos=(0, 0, 0.52)),
        )
    else:
        m = merge(
            uv_sphere(0.28, 10, 7, (255, 200, 150)),
            tf(box(0.1, 0.62, 0.1, CORAL), pos=(0, 0, 0)),
            tf(box(0.1, 0.62, 0.1, CORAL), pos=(0, 0, 0), rot=(0, 0, np.pi / 2)),
            tf(box(0.08, 0.44, 0.08, CORAL), pos=(0, 0, 0), rot=(0, 0, np.pi / 4)),
            tf(box(0.08, 0.44, 0.08, CORAL), pos=(0, 0, 0), rot=(0, 0, -np.pi / 4)),
        )
    n.mesh(*m)
    n.visible = False
    return n


def mega_ball():
    """The kingdom-killer. Grows overhead."""
    n = Node("megaball")
    m = merge(
        uv_sphere(1.0, 12, 9, DARKBALL),
        tf(uv_sphere(0.75, 10, 7, DARKBALL_RIM, squash=0.9), pos=(0, 0.1, 0.3)),
        tf(uv_sphere(0.4, 9, 6, (240, 120, 255)), pos=(0, 0.2, 0.55)),
    )
    n.mesh(*m)
    n.visible = False
    return n


# ---------------- explosions ----------------

def explosion():
    """Three concentric shells, scaled+recolored over life. One per explosion site."""
    n = Node("boom")
    n.mesh(*uv_sphere(1.0, 12, 9, FIRE_CORE))
    mid = n.add(Node("boom_mid"))
    mid.mesh(*uv_sphere(0.75, 12, 9, FIRE_MID))
    dark = n.add(Node("boom_dark"))
    dark.mesh(*uv_sphere(0.55, 10, 7, FIRE_DARK))
    n.visible = False
    return n


def animate_explosion(n, age, max_r=2.6, life=0.9):
    """age in seconds since detonation; hides itself after life."""
    if age < 0 or age > life:
        n.visible = False
        return
    n.visible = True
    p = age / life
    n.scale[:] = 0.3 + max_r * p ** 0.6
    n.find("boom_mid").scale[:] = 1.0 + 0.25 * np.sin(age * 40)
    n.find("boom_dark").scale[:] = 0.7 + 0.5 * p


# ---------------- debris (exploding blocks) ----------------

def make_debris(rng, n_pieces=26, colors=((238, 176, 50), (176, 96, 60), (120, 60, 36))):
    """Returns list of (node, vel3, spin). Animate with animate_debris."""
    out = []
    parent = Node("debris_field")
    for i in range(n_pieces):
        d = Node(f"d{i}")
        s = rng.uniform(0.12, 0.38)
        d.mesh(*box(s, s, s, colors[i % len(colors)]))
        d.visible = False
        parent.add(d)
        vel = np.array([rng.uniform(-5, 5), rng.uniform(3.5, 9.5), rng.uniform(-3, 3)])
        spin = rng.uniform(-9, 9, 3)
        out.append((d, vel, spin))
    return parent, out


def animate_debris(pieces, origin, age, grav=14.0):
    for d, vel, spin in pieces:
        if age < 0 or age > 3.0:
            d.visible = False
            continue
        d.visible = True
        d.pos[:] = (origin[0] + vel[0] * age,
                    max(0.08, origin[1] + vel[1] * age - 0.5 * grav * age * age),
                    origin[2] + vel[2] * age)
        d.rot[:] = spin * age


# ---------------- fires & smoke ----------------

def fire_patch(x, z, s=1.0, seed=1):
    """Flickering flame cones + smoke puffs. Animate via animate_fire."""
    n = Node("fire", pos=(x, 0, z), scale=s)
    for i, (fx, fz, fs) in enumerate(((0, 0, 1.0), (-0.5, 0.2, 0.7), (0.45, -0.15, 0.8))):
        fl = n.add(Node(f"flame{i}", pos=(fx, 0, fz)))
        fl.mesh(*merge(
            tf(cylinder(0.28 * fs, 0.9 * fs, 6, FIRE_MID, r_top=0.02), pos=(0, 0.45 * fs, 0)),
            tf(cylinder(0.16 * fs, 0.55 * fs, 6, FIRE_CORE, r_top=0.02), pos=(0, 0.3 * fs, 0)),
        ))
    for i in range(3):
        sm = n.add(Node(f"smoke{i}"))
        sm.mesh(*uv_sphere(0.28, 8, 6, SMOKE))
    n.visible = False
    return n


def animate_fire(n, t, seed=1):
    if not n.visible:
        return
    rng = np.random.default_rng(seed)
    ph = rng.uniform(0, 7, 6)
    for i in range(3):
        fl = n.find(f"flame{i}")
        fl.scale[:] = (1, 0.75 + 0.35 * abs(np.sin(t * 9 + ph[i])), 1)
    for i in range(3):
        sm = n.find(f"smoke{i}")
        cyc = (t * 0.45 + ph[3 + i] / 7) % 1.0
        sm.pos[:] = (0.3 * np.sin(t * 0.8 + ph[i] * 3), 0.9 + cyc * 2.0, 0.1)
        sm.scale[:] = (0.45 + cyc * 0.75) * (1 - cyc * 0.35)


# ---------------- dust ring / aura ----------------

def dust_ring():
    n = Node("dustring")
    m = []
    for i in range(10):
        a = 2 * np.pi * i / 10
        m.append(tf(uv_sphere(0.22, 7, 5, DUST, squash=0.6),
                    pos=(np.cos(a), 0.12, np.sin(a))))
    n.mesh(*merge(*m))
    n.visible = False
    return n


def animate_dust(n, age, life=0.8):
    if age < 0 or age > life:
        n.visible = False
        return
    n.visible = True
    p = age / life
    n.scale[:] = (0.5 + 2.6 * p ** 0.7, max(0.15, 1 - p), 0.5 + 2.6 * p ** 0.7)


def aura():
    """Power-up starburst behind Claudio."""
    n = Node("aura")
    m = []
    for i in range(8):
        a = np.pi * i / 4
        m.append(tf(box(0.18, 1.5, 0.06, (255, 220, 120)), pos=(0, 0, 0.3),
                    rot=(0, 0, a)))
    m.append(tf(uv_sphere(0.85, 10, 7, (255, 240, 180), squash=1.0), pos=(0, 0, 0.4)))
    n.mesh(*merge(*m))
    n.visible = False
    return n


# ---------------- 2D impact kit ----------------

def flash(im_draw, alpha_img, strength):
    pass  # (white flashes handled by frame blend in animate)


def speed_lines(d, W, H, cx, cy, rng, n=26, color=(255, 255, 255)):
    for _ in range(n):
        a = rng.uniform(0, 2 * np.pi)
        r0 = rng.uniform(90, 190)
        r1 = r0 + rng.uniform(120, 420)
        d.line((cx + r0 * np.cos(a), cy + r0 * np.sin(a),
                cx + r1 * np.cos(a), cy + r1 * np.sin(a)), fill=color,
               width=int(rng.integers(2, 5)))


def impact_star(d, cx, cy, r, color=(255, 255, 255)):
    pts = []
    for i in range(16):
        a = np.pi * i / 8
        rad = r if i % 2 == 0 else r * 0.38
        pts.append((cx + rad * np.cos(a), cy + rad * np.sin(a)))
    d.polygon(pts, fill=color)


def shock_ring(d, cx, cy, age, life=0.5, color=(255, 255, 255)):
    if age < 0 or age > life:
        return
    p = age / life
    r = 30 + 520 * p ** 0.7
    w = max(2, int(16 * (1 - p)))
    d.ellipse((cx - r, cy - r * 0.45, cx + r, cy + r * 0.45), outline=color, width=w)


def twinkle(d, cx, cy, age, life=0.7):
    if age < 0 or age > life:
        return
    p = age / life
    r = 26 * (1 - abs(2 * p - 1))
    impact_star(d, cx, cy, max(2, r), (255, 255, 230))
