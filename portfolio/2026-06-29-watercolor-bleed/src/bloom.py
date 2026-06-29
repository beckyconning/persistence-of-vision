"""Bloom — the wet-on-wet bleed, ANIMATED (APNG).

Growth: fuses the new physical-media axis with MOTION by capturing the PROCESS,
not a state — three earth pigments are dropped onto a wet basin and we watch them
diffuse, finger out, and bleed together over time, the subtractive overlaps
deepening into umber as the washes meet. (s2's animation was a gradient sweep;
this animates a simulation.) Hand-rolled APNG encoder reused from s2's dusk.py.
"""
import struct, zlib
import numpy as np

H = W = 700
ys, xs = np.mgrid[0:H, 0:W].astype(np.float64)
nx, ny = xs / W, ys / H


def crc_chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


def frame_zlib(rgb):
    h, w = rgb.shape[:2]
    raw = np.hstack([np.zeros((h, 1), np.uint8), rgb.reshape(h, w * 3)]).tobytes()
    return zlib.compress(raw, 6)


def write_apng(path, frames, delay_num=7, delay_den=100):
    h, w = frames[0].shape[:2]
    out = [b"\x89PNG\r\n\x1a\n", crc_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))]
    out.append(crc_chunk(b"acTL", struct.pack(">II", len(frames), 0)))
    seq = 0
    for i, fr in enumerate(frames):
        out.append(crc_chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, w, h, 0, 0, delay_num, delay_den, 0, 0)))
        seq += 1
        data = frame_zlib(fr)
        if i == 0:
            out.append(crc_chunk(b"IDAT", data))
        else:
            out.append(crc_chunk(b"fdAT", struct.pack(">I", seq) + data)); seq += 1
    out.append(crc_chunk(b"IEND", b""))
    open(path, "wb").write(b"".join(out))


def _box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    cs = np.cumsum(a, axis=axis); cs = np.concatenate([np.zeros_like(np.take(cs, [0], axis)), cs], axis=axis)
    lo = np.clip(np.arange(n) - r, 0, n); hi = np.clip(np.arange(n) + r + 1, 0, n)
    cnt = (hi - lo).astype(np.float64); shape = [1, 1]; shape[axis] = n
    return (np.take(cs, hi, axis=axis) - np.take(cs, lo, axis=axis)) / cnt.reshape(shape)


def blur(a, r):
    for _ in range(3):
        a = _box1d(a, r, 0); a = _box1d(a, r, 1)
    return a


def value_noise(scale, seed):
    g = np.random.default_rng(seed).random((scale, scale))
    return blur(g[(ys / H * (scale - 1)).astype(int), (xs / W * (scale - 1)).astype(int)], max(1, W // scale // 2))


def fbm(seed, octaves=5):
    out = np.zeros((H, W)); amp = 1.0; tot = 0.0; freq = 3
    for o in range(octaves):
        out += amp * value_noise(int(freq), seed + o); tot += amp; amp *= 0.5; freq *= 2
    return out / tot


def smoothstep(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0 + 1e-9), 0, 1); return t * t * (3 - 2 * t)


paper_rgb = np.array([249, 244, 233], np.float64)
tooth = 0.5 + 0.5 * value_noise(W // 3, 9)
paper = np.ones((H, W, 3)) * paper_rgb / 255.0
paper *= (1.0 - 0.045 * (fbm(101) - 0.5)[..., None])

cx, cy = 0.47, 0.52
r = np.sqrt((nx - cx) ** 2 + (ny - cy) ** 2)
wet = smoothstep(0.0, 0.16, fbm(7) * 0.5 + (0.34 - r) * 1.7)
wet = np.clip(wet * (0.6 + 0.8 * fbm(33)), 0, 1)
edge = np.clip(wet - blur(wet, 5), 0, 1)

SAP_GREEN = np.array([1.45, 0.65, 1.9]); RAW_SIENNA = np.array([0.32, 1.0, 2.4]); PAYNES = np.array([1.55, 1.3, 1.0])


def seedmap(seed, sx, sy):
    rg = np.random.default_rng(seed); p = np.zeros((H, W))
    for _ in range(4):
        ox, oy = sx + rg.uniform(-.04, .04), sy + rg.uniform(-.04, .04)
        rad = rg.uniform(.05, .09)
        p += np.exp(-(((nx - ox) ** 2 + (ny - oy) ** 2) / (2 * rad * rad)))
    return p * wet


sources = [(seedmap(11, .36, .42), SAP_GREEN, 0.7 + 0.6 * fbm(211)),
           (seedmap(29, .58, .50), RAW_SIENNA, 0.7 + 0.6 * fbm(229)),
           (seedmap(43, .47, .64), PAYNES, 0.7 + 0.6 * fbm(243))]
pig = [s.copy() for s, _, _ in sources]

frames = []
FRAMES, STEP = 30, 2
for f in range(FRAMES):
    for _ in range(STEP):
        for i, (_, _, flow) in enumerate(sources):
            p = wet * blur(pig[i], 4) * flow
            p += 0.06 * edge * blur(p, 7)
            pig[i] = p
    img = paper.copy()
    for i, (_, k, _) in enumerate(sources):
        dens = blur(pig[i], 2) * (0.65 + 0.7 * tooth) * 0.95
        img *= np.exp(-np.clip(dens, 0, None)[..., None] * k[None, None, :])
    frames.append(np.clip(img * 255 + 0.5, 0, 255).astype(np.uint8))

# hold the final bloom a moment, then loop
frames += [frames[-1]] * 8
write_apng("../images/bloom.png", frames)
print(f"wrote images/bloom.png  {len(frames)} frames {W}x{H}")
