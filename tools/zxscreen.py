"""zxscreen: ZX Spectrum screens as a medium. 256 x 192 one-bit pixels, colour in a 32 x 24 attribute grid
(INK, PAPER, BRIGHT per 8 x 8 cell), fifteen colours, a border that cannot be bright.

    from zxscreen import encode, pack, unpack, render, write_tap
    bm, ink, paper, bright = encode(indexed, bright=1)     # H x W Spectrum colour indexes 0..7 -> the cell rule
    scr = pack(bm, ink, paper, bright)                    # the 6912 bytes of screen memory
    png = render(*unpack(scr), border=1, scale=3)         # RGB array, the way a TV showed it
    write_tap("x.tap", "name", scr)                       # autostart loader + SCREEN$, loads in an emulator

encode keeps each cell's two most used colours and maps every other pixel to the nearer of the two, which is
where the attribute clash comes from. See portfolio/2026-09-14-loading.
"""
import numpy as np

def rgb(i, bright):
    v = 0xFF if bright else 0xD7
    return ((i >> 1) & 1) * v, ((i >> 2) & 1) * v, (i & 1) * v

PALETTE = np.array([[rgb(i, b) for i in range(8)] for b in (0, 1)], float)

def encode(indexed, bright=1):
    bright = np.broadcast_to(np.asarray(bright, np.uint8), (24, 32)).copy()
    bm = np.zeros((192, 256), np.uint8); ink = np.zeros((24, 32), np.uint8); paper = np.zeros((24, 32), np.uint8)
    for r in range(24):
        for c in range(32):
            cell = indexed[r * 8:r * 8 + 8, c * 8:c * 8 + 8]
            counts = np.bincount(cell.flatten(), minlength=8); order = np.argsort(-counts, kind="stable")
            p = int(order[0]); i = int(order[1]) if counts[order[1]] else p
            pal = PALETTE[bright[r, c]]
            bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = (cell == i) | ((cell != p) & (((pal[cell] - pal[i]) ** 2).sum(-1) < ((pal[cell] - pal[p]) ** 2).sum(-1)))
            ink[r, c], paper[r, c] = i, p
    return bm, ink, paper, bright

def pack(bm, ink, paper, bright):
    attrs = (np.asarray(bright, np.uint8) << 6 | np.asarray(paper, np.uint8) << 3 | np.asarray(ink, np.uint8)).astype(np.uint8)
    return np.packbits(np.asarray(bm, np.uint8), axis=1).tobytes() + attrs.tobytes()

def unpack(scr):
    assert len(scr) == 6912
    bm = np.unpackbits(np.frombuffer(scr[:6144], np.uint8)).reshape(192, 256)
    a = np.frombuffer(scr[6144:], np.uint8).reshape(24, 32)
    return bm, a & 7, (a >> 3) & 7, (a >> 6) & 1

def render(bm, ink, paper, bright, border=0, scale=3, border_px=16):
    img = np.zeros((192, 256, 3), np.uint8)
    for r in range(24):
        for c in range(32):
            m = bm[r * 8:r * 8 + 8, c * 8:c * 8 + 8].astype(bool)[..., None]
            img[r * 8:r * 8 + 8, c * 8:c * 8 + 8] = np.where(m, rgb(ink[r, c], bright[r, c]), rgb(paper[r, c], bright[r, c]))
    frame = np.zeros((192 + 2 * border_px, 256 + 2 * border_px, 3), np.uint8); frame[:] = rgb(border, 0)
    frame[border_px:border_px + 192, border_px:border_px + 256] = img
    return np.repeat(np.repeat(frame, scale, 0), scale, 1)

def _block(flag, payload):
    body = bytes([flag]) + payload; x = 0
    for b in body: x ^= b
    body += bytes([x]); return len(body).to_bytes(2, "little") + body

def write_tap(path, name, scr, border=1):
    """BASIC 10 BORDER 0: LOAD "" SCREEN$: BORDER <border>: PAUSE 0, autostarting, then the screen."""
    num = lambda v: str(v).encode() + bytes([0x0E, 0, 0, v, 0, 0])
    line = bytes([0xE7]) + num(0) + b":" + bytes([0xEF]) + b'""' + bytes([0xAA]) + b":" + bytes([0xE7]) + num(border) + b":" + bytes([0xF2]) + num(0) + b"\r"
    basic = (10).to_bytes(2, "big") + len(line).to_bytes(2, "little") + line
    nm = name.encode()[:10].ljust(10)
    h0 = bytes([0]) + nm + len(basic).to_bytes(2, "little") + (10).to_bytes(2, "little") + len(basic).to_bytes(2, "little")
    h3 = bytes([3]) + nm + (6912).to_bytes(2, "little") + (16384).to_bytes(2, "little") + (32768).to_bytes(2, "little")
    open(path, "wb").write(_block(0, h0) + _block(0xFF, basic) + _block(0, h3) + _block(0xFF, scr))

if __name__ == "__main__":                       # round trip every .scr given, compare to a fresh pack
    import sys
    for p in sys.argv[1:]:
        scr = open(p, "rb").read(); again = pack(*unpack(scr))
        print(p, "round trip", "ok" if again == scr else "MISMATCH")
