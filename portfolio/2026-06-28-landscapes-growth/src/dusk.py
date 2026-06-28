#!/usr/bin/env python3
"""Growth piece #2 — MOTION axis (unmoved in session 1): an animated day->dusk
landscape as an APNG. Includes a tiny hand-rolled APNG encoder (acTL/fcTL/fdAT)
extending the stdlib PNG machinery — building the tool to make the thing I
couldn't make before. Earth/paper palette shifts to rose-dusk as the sun sinks.
"""
import struct, zlib
import numpy as np

W, H = 1100, 760
RNG = np.random.default_rng(11)
HORIZON = int(H * 0.62)


def crc_chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)


def frame_zlib(rgb):
    h, w = rgb.shape[:2]
    raw = np.hstack([np.zeros((h, 1), np.uint8), rgb.reshape(h, w * 3)]).tobytes()
    return zlib.compress(raw, 9)


def write_apng(path, frames, delay_num=8, delay_den=100):
    """frames: list of (H,W,3) uint8. Loops forever. Full-frame APNG."""
    h, w = frames[0].shape[:2]
    out = [b"\x89PNG\r\n\x1a\n", crc_chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))]
    out.append(crc_chunk(b"acTL", struct.pack(">II", len(frames), 0)))   # num_frames, 0=inf loop
    seq = 0
    for i, fr in enumerate(frames):
        out.append(crc_chunk(b"fcTL", struct.pack(">IIIIIHHBB", seq, w, h, 0, 0,
                                                  delay_num, delay_den, 0, 0)))
        seq += 1
        data = frame_zlib(fr)
        if i == 0:
            out.append(crc_chunk(b"IDAT", data))
        else:
            out.append(crc_chunk(b"fdAT", struct.pack(">I", seq) + data))
            seq += 1
    out.append(crc_chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(b"".join(out))


def smooth_profile(width, octaves, seed, rough=0.5):
    rng = np.random.default_rng(seed)
    x = np.linspace(0, 1, width); out = np.zeros(width); amp = 1.0; freq = 2.0; norm = 0.0
    for _ in range(octaves):
        n = rng.random(int(freq) + 2)
        xi = x * (len(n) - 1); i0 = np.floor(xi).astype(int); f = xi - i0; f = f * f * (3 - 2 * f)
        out += amp * (n[i0] * (1 - f) + n[np.minimum(i0 + 1, len(n) - 1)] * f)
        norm += amp; amp *= rough; freq *= 2.2
    return out / norm


PROFILES = [(0.50, 0.06, np.array([0.62, 0.64, 0.60]), 31, 3),
            (0.58, 0.10, np.array([0.55, 0.58, 0.45]), 47, 4),
            (0.68, 0.14, np.array([0.45, 0.46, 0.32]), 59, 4),
            (0.80, 0.20, np.array([0.36, 0.32, 0.22]), 71, 5)]
RIDGES = [((top - ampf * smooth_profile(W, oc, sd)) * H, col)
          for (top, ampf, col, sd, oc) in PROFILES]
Y, X = np.mgrid[0:H, 0:W]


def render(t):
    """t in [0,1]: 0 = warm day, 1 = rose dusk; sun sinks toward the horizon."""
    # palette interpolates day -> dusk
    day_top, dusk_top = np.array([0.93, 0.90, 0.82]), np.array([0.28, 0.24, 0.40])
    day_hz, dusk_hz = np.array([0.97, 0.88, 0.72]), np.array([0.95, 0.55, 0.42])
    top = day_top + (dusk_top - day_top) * t
    hz = day_hz + (dusk_hz - day_hz) * t
    g = np.clip(np.arange(H) / HORIZON, 0, 1)
    sky = top[None, :] + (hz - top)[None, :] * g[:, None]
    img = np.broadcast_to(sky[:, None, :], (H, W, 3)).copy()

    sun_x = int(W * 0.72)
    sun_y = int(H * (0.26 + 0.34 * t))                      # sinks
    d = np.sqrt(((X - sun_x) / W) ** 2 + ((Y - sun_y) / H) ** 2)
    glow = np.clip(1 - d / (0.5 + 0.15 * t), 0, 1) ** 2.2
    sun_col = np.array([1.0, 0.95, 0.82]) + (np.array([1.0, 0.55, 0.30]) - np.array([1.0, 0.95, 0.82])) * t
    img = img * (1 - glow[..., None]) + sun_col[None, None, :] * glow[..., None]
    disc = (np.clip(1 - np.sqrt((X - sun_x) ** 2 + (Y - sun_y) ** 2) / 34, 0, 1)) ** 0.6
    img = img * (1 - disc[..., None]) + (sun_col * 1.02)[None, None, :] * disc[..., None]

    for li, (ridge, col) in enumerate(RIDGES):
        haze = 1.0 - li / (len(RIDGES) - 0.2)
        dusk_col = col * (1 - 0.45 * t)                     # hills darken into dusk
        colcol = dusk_col[None, :] * (0.7 + 0.3 * np.linspace(0.6, 1.0, W)[:, None] * 0)  # flat per col
        colcol = np.broadcast_to(dusk_col[None, :], (W, 3)).copy()
        colcol = colcol * (1 - 0.55 * haze) + hz[None, :] * (0.55 * haze)
        below = Y >= ridge[None, :]
        img = np.where(below[..., None], np.broadcast_to(colcol[None, :, :], (H, W, 3)), img)

    img = img + (RNG.random((H, W, 1)) - 0.5) * 0.025
    return (np.clip(img, 0, 1) * 255).astype(np.uint8)


def main():
    ts = list(np.linspace(0, 1, 9))
    frames = [render(t) for t in ts] + [render(t) for t in reversed(ts[1:-1])]  # ping-pong loop
    print(f"rendering {len(frames)} frames…")
    write_apng("dusk.png", frames, delay_num=9, delay_den=100)
    print("wrote dusk.png (APNG)")


if __name__ == "__main__":
    main()
