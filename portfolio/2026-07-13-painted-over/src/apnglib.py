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

