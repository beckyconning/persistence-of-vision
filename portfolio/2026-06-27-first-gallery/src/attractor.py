#!/usr/bin/env python3
"""A Peter de Jong strange attractor, rendered to a PNG using nothing but the
Python standard library. No numpy, no PIL — just math, a density histogram, and
a hand-rolled PNG encoder (zlib + struct).

    x' = sin(a*y) - cos(b*x)
    y' = sin(c*x) - cos(d*y)

We iterate a few million points, bin them into a grid, then map density through
a log curve and a midnight->magenta->gold colour ramp.
"""
import math, struct, zlib

W = H = 1000
A, B, C, D = -2.24, 0.99, -2.86, -2.31   # a pretty parameter set
ITERS = 6_000_000
SPAN = 2.35  # attractor lives roughly in [-2,2]; pad a touch


def iterate():
    """Bin ITERS points of the attractor into a W*H density grid."""
    grid = [0] * (W * H)
    x, y = 0.123, 0.456
    scale = (W - 1) / (2 * SPAN)
    for _ in range(ITERS):
        x, y = math.sin(A * y) - math.cos(B * x), math.sin(C * x) - math.cos(D * y)
        px = int((x + SPAN) * scale)
        py = int((y + SPAN) * scale)
        if 0 <= px < W and 0 <= py < H:
            grid[py * W + px] += 1
    return grid


def ramp(t):
    """t in [0,1] -> (r,g,b). midnight blue -> magenta -> warm gold."""
    stops = [(0.02, 0.01, 0.09), (0.45, 0.05, 0.45),
             (0.95, 0.25, 0.55), (1.0, 0.85, 0.45)]
    seg = t * (len(stops) - 1)
    i = min(int(seg), len(stops) - 2)
    f = seg - i
    a, b = stops[i], stops[i + 1]
    return tuple(int(255 * (a[k] + (b[k] - a[k]) * f)) for k in range(3))


def colorize(grid):
    peak = max(grid)
    lp = math.log1p(peak)
    raw = bytearray()
    for v in grid:
        if v == 0:
            raw += b"\x05\x02\x17"          # near-black background
        else:
            r, g, b = ramp(math.log1p(v) / lp)
            raw += bytes((r, g, b))
    return raw


def write_png(path, rgb):
    def chunk(tag, data):
        return (struct.pack(">I", len(data)) + tag + data
                + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff))
    # prepend the mandatory filter byte (0) to each scanline
    stride = W * 3
    rows = bytearray()
    for y in range(H):
        rows.append(0)
        rows += rgb[y * stride:(y + 1) * stride]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(rows), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)


if __name__ == "__main__":
    print(f"iterating {ITERS:,} points of the de Jong attractor...")
    g = iterate()
    hits = sum(1 for v in g if v)
    print(f"lit {hits:,}/{W*H:,} pixels ({100*hits/(W*H):.1f}%); peak density {max(g)}")
    write_png("dejong_stdlib.png", colorize(g))
    print("wrote dejong_stdlib.png")
