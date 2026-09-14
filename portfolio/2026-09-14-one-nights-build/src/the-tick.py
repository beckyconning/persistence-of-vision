# the-tick: a typewritten page. One character = 10 ms of the same deep render (deep1e100, 1280x720).
# Before the timer fix: 37.65 s, the GPU computing about 41% of each frame (8.7 ms of ~21 ms), the rest waiting.
# After: 4.27 s. '#' = the GPU computing, '.' = the machine waiting for its next timer tick.
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
PW, PH = 1240, 1754
PAPER = np.array([238, 233, 221])
rng = np.random.default_rng(1913)
font = ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf', 15)
COLS = 104
CHW, LINEH = 10.0, 21

def ribbon(total_ms, duty):
    n = int(round(total_ms / 10))
    out, acc = [], 0.0
    for _ in range(n):          # Bresenham-style spread of compute vs waiting at the measured duty
        acc += duty
        if acc >= 1.0:
            acc -= 1.0
            out.append('#')
        else:
            out.append('.')
    return ''.join(out)

before = ribbon(37650, 0.41)
# after: 4.27 s done vs about 3.05 s headless at the same size, so compute occupies ~0.71 of wall time
after = ribbon(4270, 0.71)

# paper with fibre noise and a faint fold
paper = np.ones((PH, PW, 3)) * PAPER
paper += rng.normal(0, 3.2, (PH, PW, 1))
paper[:, PW // 2 - 1:PW // 2 + 1] -= 6
img = Image.fromarray(np.clip(paper, 0, 255).astype(np.uint8), 'RGB')
layer = Image.new('L', (PW, PH), 0)      # ink coverage
ld = ImageDraw.Draw(layer)

ribbon_ink = rng.uniform(0.55, 1.0)
def strike(x, y, ch, strength):
    # each key strike lands slightly off-grid with its own pressure; the ribbon fades and is re-inked
    dx, dy = rng.normal(0, 0.45), rng.normal(0, 0.55)
    ld.text((x + dx, y + dy), ch, font=font, fill=int(255 * strength))

def type_block(text, x0, y0):
    x, y = x0, y0
    ink = 1.0
    for i, ch in enumerate(text):
        if ch == '\n' or (i > 0 and (x - x0) / CHW >= COLS):
            x, y = x0, y + LINEH
            if ch == '\n':
                continue
        ink = max(0.55, ink - 0.00012)
        if rng.random() < 0.002:
            ink = 1.0
        strike(x, y, ch, ink * rng.uniform(0.78, 1.0))
        x += CHW
    return y + LINEH

X0 = 100
y = 110
y = type_block('the tick', X0, y)
y += 10
y = type_block('one character = ten milliseconds of the same picture: mandelbrot, zoom 1e100, 1280 x 720.', X0, y)
y = type_block('#  the graphics card computing.   .  the program asleep, waiting for the next timer tick.', X0, y)
y += 30
y = type_block('before  (37.65 s)', X0, y)
y += 6
y = type_block(before, X0, y)
y += 30
y = type_block('after timeBeginPeriod(1)  (4.27 s)', X0, y)
y += 6
y = type_block(after, X0, y)
y += 40
y = type_block('same arithmetic, same card, same image. thirty-three seconds of the difference was sleep.', X0, y)
y = type_block('mandeldive build, 13-14 september 2026.', X0, y)

cov = np.asarray(layer).astype(np.float64) / 255.0
ink = np.array([34, 32, 40])
arr = np.asarray(img).astype(np.float64)
arr = arr * (1 - cov[:, :, None]) + ink * cov[:, :, None]
Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8)).save(D + 'the-tick.png')
print(len(before), len(after), 'last y', y)
