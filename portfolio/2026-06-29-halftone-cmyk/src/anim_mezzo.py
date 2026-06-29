"""Animated mezzotint — the PROCESS, not the state: a plate worked from solid black up to a
luminous sphere as it is burnished (the lit areas brought out of the dark over time). Motion
axis + the new stipple mark. Hand-rolled APNG (acTL/fcTL/fdAT), looping with a hold."""
import struct, zlib
import numpy as np

W = Hh = 640
ys, xs = np.mgrid[0:Hh, 0:W].astype(np.float64)
nx, ny = (xs - W / 2) / (W / 2), (ys - Hh / 2) / (Hh / 2)
rng = np.random.default_rng(21)


def crc_chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


def fz(rgb):
    h, w = rgb.shape[:2]
    raw = np.hstack([np.zeros((h, 1), np.uint8), rgb.reshape(h, w * 3)]).tobytes()
    return zlib.compress(raw, 6)


def write_apng(path, frames, dn=8, dd=100):
    h, w = frames[0].shape[:2]
    out = [b"\x89PNG\r\n\x1a\n", crc_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)),
           crc_chunk(b"acTL", struct.pack(">II", len(frames), 0))]
    seq = 0
    for i, fr in enumerate(frames):
        out.append(crc_chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, w, h, 0, 0, dn, dd, 0, 0))); seq += 1
        d = fz(fr)
        out.append(crc_chunk(b"IDAT", d) if i == 0 else crc_chunk(b"fdAT", struct.pack(">I", seq) + d))
        if i: seq += 1
    out.append(crc_chunk(b"IEND", b""))
    open(path, "wb").write(b"".join(out))


cx, cy, R = 0.0, 0.0, 0.6
d2 = (nx - cx) ** 2 + (ny - cy) ** 2
inside = d2 < R * R
z = np.sqrt(np.clip(R * R - d2, 0, None))
nn = np.stack([(nx - cx) / R, (ny - cy) / R, z / R], -1)
L = np.array([-0.4, -0.5, 0.77]); L /= np.linalg.norm(L)
lam = np.clip(nn @ L, 0, 1)
tone = np.where(inside, 0.05 + 0.92 * lam ** 1.3, 0.06 + 0.08 * (ny + 1))
tone = np.clip(tone, 0, 1)
g = rng.random((Hh, W))  # fixed rocker grain
paper = np.array([0.95, 0.93, 0.88]); INKC = np.array([0.05, 0.04, 0.06])

frames = []
N = 26
for f in range(N):
    burnish = f / (N - 1)            # 0 = raw black plate, 1 = fully worked
    eff_tone = tone * burnish        # lit areas emerge as the plate is burnished
    ink = (g < (1 - eff_tone)).astype(float)
    img = paper[None, None, :] * (1 - ink[..., None]) + INKC[None, None, :] * ink[..., None]
    frames.append(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))
frames += [frames[-1]] * 8
write_apng("../images/anim_mezzo.png", frames)
print(f"wrote images/anim_mezzo.png {len(frames)} frames {W}x{Hh}")
