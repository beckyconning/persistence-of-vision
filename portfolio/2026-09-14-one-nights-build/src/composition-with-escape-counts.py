# composition-with-escape-counts: the Mandelbrot home view as a quadtree, split wherever escape counts differ,
# painted in De Stijl primaries (after Mondrian). The subdivision is the progressive-refinement idea made visible.
import numpy as np
from PIL import Image, ImageDraw
D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
N = 512
ys, xs = np.mgrid[0:N, 0:N]
c = (-0.72 + (xs + 0.5 - N / 2) / N * 2.9) + 1j * ((N / 2 - ys - 0.5) / N * 2.9)
z = np.zeros_like(c); n = np.zeros(c.shape, np.int32); alive = np.ones(c.shape, bool)
for k in range(1, 257):
    z[alive] = z[alive] * z[alive] + c[alive]
    esc = alive & (np.abs(z) > 2)
    n[esc] = k
    alive &= ~esc
n[alive] = 999
def band(v):
    if v == 999: return 'black'
    if v < 4: return 'white'
    if v < 7: return 'yellow'
    if v < 14: return 'blue'
    return 'red'
COL = {'white': (240, 238, 232), 'yellow': (244, 204, 42), 'blue': (32, 70, 160), 'red': (206, 40, 36), 'black': (22, 22, 24)}
S = 1400 / N
img = Image.new('RGB', (1400, 1400), COL['white'])
d = ImageDraw.Draw(img)
bands = np.vectorize(band)(n)
def split(x, y, size):
    block = bands[y:y + size, x:x + size]
    if size > 8 and len(np.unique(block)) > 1:
        h = size // 2
        for dx, dy in ((0, 0), (h, 0), (0, h), (h, h)):
            split(x + dx, y + dy, h)
        return
    vals, counts = np.unique(block, return_counts=True)
    colour = COL[vals[counts.argmax()]]
    d.rectangle([x * S, y * S, (x + size) * S, (y + size) * S], fill=colour, outline=COL['black'], width=max(2, int(size / 16)))
split(0, 0, N)
img.save(D + 'composition-with-escape-counts.png')
img.resize((700, 700)).save(D + 'mondrian-preview.png')
print('ok')
