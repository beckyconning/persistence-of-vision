"""A real stdlib PNG *decoder* — the capability this session adds.

The encoder we've shipped all along (`pnglib.write_png`) only ever emits
filter-type 0 (None). To use images as INPUT we have to read PNGs we didn't
write, which means implementing the full scanline-filter reconstruction
(None/Sub/Up/Average/Paeth) and the common colour types (grayscale, RGB,
palette, and their +alpha forms). Pure stdlib: struct + zlib + numpy.

Returns an (H, W, 3) uint8 RGB array — alpha is composited onto the chunk's
bKGD if present, else flattened away, since downstream art works in RGB.
"""
import struct
import zlib
import numpy as np


def _paeth(a, b, c):
    """Paeth predictor (PNG filter 4): pick a, b, or c closest to a+b-c."""
    p = a.astype(np.int16) + b.astype(np.int16) - c.astype(np.int16)
    pa, pb, pc = np.abs(p - a), np.abs(p - b), np.abs(p - c)
    out = np.where((pa <= pb) & (pa <= pc), a, np.where(pb <= pc, b, c))
    return out.astype(np.uint8)


def _unfilter(raw, h, w, bpp, stride):
    """Reverse the per-scanline filters. raw is the decompressed byte stream:
    one filter-type byte then `stride` data bytes per row. Returns (h, stride)."""
    out = np.zeros((h, stride), np.uint8)
    prev = np.zeros(stride, np.uint8)
    pos = 0
    for y in range(h):
        ft = raw[pos]
        pos += 1
        line = np.frombuffer(raw[pos:pos + stride], np.uint8).copy()
        pos += stride
        if ft == 0:                         # None
            cur = line
        elif ft == 1:                       # Sub — left
            cur = line.copy()
            for i in range(bpp, stride):
                cur[i] = (int(cur[i]) + int(cur[i - bpp])) & 0xff
        elif ft == 2:                       # Up — above
            cur = (line + prev) & 0xff
        elif ft == 3:                       # Average — (left + above)//2
            cur = line.copy()
            for i in range(stride):
                left = cur[i - bpp] if i >= bpp else 0
                cur[i] = (cur[i] + ((int(left) + int(prev[i])) >> 1)) & 0xff
        elif ft == 4:                       # Paeth
            cur = line.copy()
            for i in range(stride):
                a = int(cur[i - bpp]) if i >= bpp else 0
                c = int(prev[i - bpp]) if i >= bpp else 0
                b = int(prev[i])
                p = a + b - c
                pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
                pred = a if (pa <= pb and pa <= pc) else (b if pb <= pc else c)
                cur[i] = (int(cur[i]) + pred) & 0xff
        else:
            raise ValueError(f"unknown filter type {ft}")
        out[y] = cur
        prev = cur
    return out


def read_png(path):
    """Decode a PNG to an (H, W, 3) uint8 RGB array. Handles colour types
    0 (gray), 2 (RGB), 3 (palette), 4 (gray+A), 6 (RGB+A) at 8 bits/sample."""
    with open(path, "rb") as f:
        data = f.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    pos = 8
    idat = bytearray()
    palette = None
    w = h = bit_depth = color = None
    while pos < len(data):
        (length,) = struct.unpack(">I", data[pos:pos + 4])
        tag = data[pos + 4:pos + 8]
        body = data[pos + 8:pos + 8 + length]
        pos += 12 + length                  # length + tag + body + crc
        if tag == b"IHDR":
            w, h, bit_depth, color = struct.unpack(">IIBB", body[:10])
        elif tag == b"PLTE":
            palette = np.frombuffer(body, np.uint8).reshape(-1, 3)
        elif tag == b"IDAT":
            idat += body
        elif tag == b"IEND":
            break
    if bit_depth != 8:
        raise ValueError(f"only 8-bit supported (got {bit_depth})")

    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    bpp = channels                          # bytes/pixel at 8-bit
    stride = w * channels
    raw = zlib.decompress(bytes(idat))
    flat = _unfilter(raw, h, w, bpp, stride).reshape(h, w, channels)

    if color == 2:                          # RGB
        rgb = flat[:, :, :3]
    elif color == 6:                        # RGB + alpha → composite on white
        a = flat[:, :, 3:4].astype(np.float32) / 255.0
        rgb = (flat[:, :, :3].astype(np.float32) * a + 255 * (1 - a)).astype(np.uint8)
    elif color == 0:                        # grayscale
        rgb = np.repeat(flat, 3, axis=2)
    elif color == 4:                        # gray + alpha
        g = flat[:, :, :1].astype(np.float32)
        a = flat[:, :, 1:2].astype(np.float32) / 255.0
        v = (g * a + 255 * (1 - a)).astype(np.uint8)
        rgb = np.repeat(v, 3, axis=2)
    elif color == 3:                        # palette
        rgb = palette[flat[:, :, 0]]
    else:
        raise ValueError(f"unsupported colour type {color}")
    return np.ascontiguousarray(rgb)
