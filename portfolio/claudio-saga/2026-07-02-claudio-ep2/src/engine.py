"""Tiny software 3D engine: node graph, perspective camera, z-buffer rasterizer,
flat lambert shading. Low-poly bootleg by design."""
import numpy as np

W, H = 854, 480


# ---------------- transforms ----------------

def rot_x(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]], dtype=np.float64)


def rot_y(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]], dtype=np.float64)


def rot_z(a):
    c, s = np.cos(a), np.sin(a)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]], dtype=np.float64)


def euler(rx=0.0, ry=0.0, rz=0.0):
    return rot_y(ry) @ rot_x(rx) @ rot_z(rz)


class Node:
    """FK scene-graph node. pos/rot(euler xyz)/scale are the local pose."""

    def __init__(self, name="", pos=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
        self.name = name
        self.pos = np.array(pos, dtype=np.float64)
        self.rot = np.array(rot, dtype=np.float64)
        self.scale = np.array(scale if np.iterable(scale) else (scale,) * 3, dtype=np.float64)
        self.meshes = []   # list of (V, F, C)
        self.children = []
        self.visible = True

    def add(self, child):
        self.children.append(child)
        return child

    def mesh(self, V, F, C):
        self.meshes.append((np.asarray(V, np.float64), np.asarray(F, np.int32),
                            np.asarray(C, np.float64)))
        return self

    def find(self, name):
        if self.name == name:
            return self
        for c in self.children:
            r = c.find(name)
            if r is not None:
                return r
        return None

    def collect(self, M=None, t=None, out=None):
        """Flatten to world-space triangle soup."""
        if out is None:
            out = []
        if not self.visible:
            return out
        R = euler(*self.rot) * self.scale  # scale then rotate (column scaling)
        Mw = (M @ R) if M is not None else R
        tw = (M @ self.pos + t) if M is not None else self.pos.copy()
        for V, F, C in self.meshes:
            out.append(((V @ Mw.T) + tw, F, C))
        for c in self.children:
            c.collect(Mw, tw, out)
        return out


# ---------------- camera ----------------

class Camera:
    def __init__(self, pos=(0, 2, -8), target=(0, 1, 0), fov=55.0):
        self.pos = np.array(pos, dtype=np.float64)
        self.target = np.array(target, dtype=np.float64)
        self.fov = fov

    def view(self):
        fwd = self.target - self.pos
        fwd = fwd / np.linalg.norm(fwd)
        right = np.cross(fwd, (0.0, 1.0, 0.0))
        rn = np.linalg.norm(right)
        if rn < 1e-6:
            right = np.array((1.0, 0.0, 0.0))
        else:
            right /= rn
        up = np.cross(right, fwd)
        return np.stack([right, up, fwd])  # world->cam rows


# ---------------- rasterizer ----------------

SUN = np.array([0.45, 0.8, -0.4])
SUN_L = SUN / np.linalg.norm(SUN)


def sky_gradient(top=(96, 150, 236), bottom=(168, 212, 250)):
    tcol = np.array(top, np.float32)
    bcol = np.array(bottom, np.float32)
    g = np.linspace(0, 1, H, dtype=np.float32)[:, None]
    img = (tcol * (1 - g) + bcol * g)[:, None, :].repeat(W, axis=1)
    return img


def render(root, cam, sky=None, ambient=0.52, fog_color=None, fog_dist=70.0,
           mode="shaded", vert_warp=None, seed=0):
    """Rasterize the scene. Returns HxWx3 uint8.

    mode: 'shaded' | 'rainbow' (random flat face colors) | 'normals' (n as rgb)
          | 'depth' (z as grayscale). vert_warp(Vw, rng) may mutate world verts.
    """
    if sky is None:
        sky = sky_gradient()
    if mode == "depth":
        sky = np.full((H, W, 3), 8, dtype=np.float32)
    elif mode == "normals":
        sky = np.full((H, W, 3), (128, 128, 255), dtype=np.float32)
    frame = sky.copy()
    zbuf = np.full((H, W), np.inf, dtype=np.float32)

    Vw_list = root.collect()
    Vm = cam.view()
    f = (W / 2) / np.tan(np.radians(cam.fov) / 2)
    rng = np.random.default_rng(seed)

    for gi, (Vw, F, C) in enumerate(Vw_list):
        if vert_warp is not None:
            Vw = vert_warp(Vw, np.random.default_rng(seed * 131 + gi))
        Vc = (Vw - cam.pos) @ Vm.T
        z = Vc[:, 2]
        # per-face world normals for lambert
        v0, v1, v2 = Vw[F[:, 0]], Vw[F[:, 1]], Vw[F[:, 2]]
        n = np.cross(v1 - v0, v2 - v0)
        nl = np.linalg.norm(n, axis=1, keepdims=True)
        n = n / np.maximum(nl, 1e-9)
        if mode == "rainbow":
            shade = np.random.default_rng(gi * 7 + seed).uniform(40, 255, C.shape)
        elif mode == "normals":
            shade = (n * 0.5 + 0.5) * 255
        elif mode == "depth":
            zface = (z[F[:, 0]] + z[F[:, 1]] + z[F[:, 2]]) / 3
            g = np.clip(255 * (1 - zface / 40.0), 0, 255)
            shade = np.stack([g, g, g], axis=1)
        else:
            lam = ambient + (1 - ambient) * np.clip(n @ SUN_L, 0, 1)
            shade = np.clip(C * lam[:, None], 0, 255)
        if fog_color is not None and mode == "shaded":
            zface = (z[F[:, 0]] + z[F[:, 1]] + z[F[:, 2]]) / 3
            fk = np.clip(zface / fog_dist, 0, 1)[:, None] ** 1.5
            shade = shade * (1 - fk) + np.array(fog_color, np.float64) * fk

        # project
        zs = np.maximum(z, 0.05)
        sx = Vc[:, 0] / zs * f + W / 2
        sy = -Vc[:, 1] / zs * f + H / 2

        x0, y0 = sx[F[:, 0]], sy[F[:, 0]]
        x1, y1 = sx[F[:, 1]], sy[F[:, 1]]
        x2, y2 = sx[F[:, 2]], sy[F[:, 2]]
        z0, z1_, z2 = z[F[:, 0]], z[F[:, 1]], z[F[:, 2]]

        area = (x1 - x0) * (y2 - y0) - (x2 - x0) * (y1 - y0)
        behind = (z0 < 0.05) | (z1_ < 0.05) | (z2 < 0.05)
        keep = (area < -0.4) & ~behind  # backface cull (CW front after y-flip)
        xmin = np.maximum(np.floor(np.minimum(np.minimum(x0, x1), x2)), 0)
        xmax = np.minimum(np.ceil(np.maximum(np.maximum(x0, x1), x2)), W - 1)
        ymin = np.maximum(np.floor(np.minimum(np.minimum(y0, y1), y2)), 0)
        ymax = np.minimum(np.ceil(np.maximum(np.maximum(y0, y1), y2)), H - 1)
        keep &= (xmax >= xmin) & (ymax >= ymin)

        idx = np.nonzero(keep)[0]
        # far-to-near helps early z a bit; not required for correctness
        order = np.argsort(-(z0[idx] + z1_[idx] + z2[idx]))
        for i in idx[order]:
            xa, xb = int(xmin[i]), int(xmax[i]) + 1
            ya, yb = int(ymin[i]), int(ymax[i]) + 1
            gx = np.arange(xa, xb, dtype=np.float32) + 0.5
            gy = np.arange(ya, yb, dtype=np.float32)[:, None] + 0.5
            d = area[i]
            w0 = ((x1[i] - x0[i]) * (gy - y0[i]) - (gx - x0[i]) * (y1[i] - y0[i])) / d
            w1 = ((x2[i] - x1[i]) * (gy - y1[i]) - (gx - x1[i]) * (y2[i] - y1[i])) / d
            w2 = 1.0 - w0 - w1
            m = (w0 >= 0) & (w1 >= 0) & (w2 >= 0)
            if not m.any():
                continue
            # perspective-correct-ish depth (linear ok at this art level)
            zt = w1 * z0[i] + w2 * z1_[i] + w0 * z2[i]
            zb = zbuf[ya:yb, xa:xb]
            upd = m & (zt < zb)
            if not upd.any():
                continue
            zb[upd] = zt[upd]
            frame[ya:yb, xa:xb][upd] = shade[i]
    return np.clip(frame, 0, 255).astype(np.uint8)


# ---------------- primitives ----------------

def box(w=1, h=1, d=1, color=(200, 100, 80)):
    x, y, z = w / 2, h / 2, d / 2
    V = np.array([[-x, -y, -z], [x, -y, -z], [x, y, -z], [-x, y, -z],
                  [-x, -y, z], [x, -y, z], [x, y, z], [-x, y, z]], np.float64)
    F = np.array([[0, 2, 1], [0, 3, 2], [4, 5, 6], [4, 6, 7],
                  [0, 1, 5], [0, 5, 4], [3, 7, 6], [3, 6, 2],
                  [0, 4, 7], [0, 7, 3], [1, 2, 6], [1, 6, 5]], np.int32)
    C = np.tile(np.array(color, np.float64), (len(F), 1))
    return V, F, C


def uv_sphere(r=1.0, nu=10, nv=8, color=(220, 180, 160), squash=1.0):
    """Low-poly sphere; squash flattens y."""
    verts, faces = [], []
    for j in range(nv + 1):
        th = np.pi * j / nv
        for i in range(nu):
            ph = 2 * np.pi * i / nu
            verts.append((r * np.sin(th) * np.cos(ph), r * np.cos(th) * squash,
                          r * np.sin(th) * np.sin(ph)))
    for j in range(nv):
        for i in range(nu):
            a = j * nu + i
            b = j * nu + (i + 1) % nu
            c = (j + 1) * nu + i
            dd = (j + 1) * nu + (i + 1) % nu
            faces += [[a, b, dd], [a, dd, c]]
    V = np.array(verts, np.float64)
    F = np.array(faces, np.int32)
    C = np.tile(np.array(color, np.float64), (len(F), 1))
    return V, F, C


def cylinder(r=1.0, h=1.0, n=10, color=(100, 200, 100), cap=True, r_top=None):
    r_top = r if r_top is None else r_top
    verts, faces = [], []
    for i in range(n):
        a = 2 * np.pi * i / n
        verts.append((r * np.cos(a), -h / 2, r * np.sin(a)))
        verts.append((r_top * np.cos(a), h / 2, r_top * np.sin(a)))
    for i in range(n):
        a0, a1 = 2 * i, 2 * i + 1
        b0, b1 = 2 * ((i + 1) % n), 2 * ((i + 1) % n) + 1
        faces += [[a0, b0, b1], [a0, b1, a1]]
    if cap:
        cb = len(verts)
        verts.append((0, -h / 2, 0))
        ct = len(verts)
        verts.append((0, h / 2, 0))
        for i in range(n):
            a0 = 2 * i
            b0 = 2 * ((i + 1) % n)
            faces += [[cb, a0, b0], [ct, b0 + 1, a0 + 1]]
    V = np.array(verts, np.float64)
    F = np.array(faces, np.int32)
    C = np.tile(np.array(color, np.float64), (len(F), 1))
    return V, F, C


def merge(*meshes):
    Vs, Fs, Cs = [], [], []
    off = 0
    for V, F, C in meshes:
        Vs.append(V)
        Fs.append(F + off)
        Cs.append(C)
        off += len(V)
    return np.concatenate(Vs), np.concatenate(Fs), np.concatenate(Cs)


def tf(mesh, pos=(0, 0, 0), rot=(0, 0, 0), scale=1.0):
    """Bake a transform into a mesh (for static composition)."""
    V, F, C = mesh
    R = euler(*np.asarray(rot, np.float64))
    s = np.array(scale if np.iterable(scale) else (scale,) * 3)
    return (V * s) @ R.T + np.asarray(pos, np.float64), F, C


def recolor(mesh, color):
    V, F, C = mesh
    return V, F, np.tile(np.array(color, np.float64), (len(F), 1))
