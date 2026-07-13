"""NES-style chiptune engine + the SUPER CLAUDIO BROS. score and SFX.
Original melody, loosely in the register of a certain 1985 plumbing sim."""
import numpy as np

SR = 44100


def midi_f(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def _env(n, a=0.004, d=None, sus=1.0, rel=0.02):
    e = np.ones(n, dtype=np.float32) * sus
    na = int(a * SR)
    if na > 0:
        e[:na] *= np.linspace(0, 1, na)
    if d:
        nd = min(n, int(d * SR))
        e[:nd] *= np.linspace(1, sus, nd)
        e = np.maximum(e, np.linspace(1, sus, n) if False else e)
        dec = np.exp(-np.arange(n) / (d * SR)).astype(np.float32)
        e = dec * (1 - sus) + sus
        if na > 0:
            e[:na] *= np.linspace(0, 1, na)
    nr = int(rel * SR)
    if nr > 0 and nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def square(f, dur, duty=0.5, vol=0.5, vib=0.0, decay=None, sweep_to=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    if sweep_to:
        ff = f * (sweep_to / f) ** (t / dur)
    else:
        ff = np.full(n, f, dtype=np.float64)
    if vib:
        ff = ff * (1 + vib * np.sin(2 * np.pi * 5.6 * t))
    ph = np.cumsum(ff) / SR
    x = ((ph % 1.0) < duty).astype(np.float32) * 2 - 1
    return x * _env(n, d=decay) * vol


def triangle(f, dur, vol=0.55, decay=None):
    n = int(dur * SR)
    t = np.arange(n) / SR
    ph = (f * t) % 1.0
    x = (2 * np.abs(2 * ph - 1) - 1).astype(np.float32)
    # NES tri is 4-bit steppy
    x = np.round(x * 7) / 7
    return x * _env(n, d=decay) * vol


def noise(dur, vol=0.4, decay=0.08, lp=None, seed=1):
    n = int(dur * SR)
    rng = np.random.default_rng(seed)
    x = rng.uniform(-1, 1, n).astype(np.float32)
    if lp:  # crude lowpass via box filter
        k = max(1, int(SR / lp / 2))
        x = np.convolve(x, np.ones(k) / k, mode="same").astype(np.float32)
    return x * _env(n, d=decay) * vol


class Mix:
    def __init__(self, total):
        self.buf = np.zeros(int(total * SR) + SR, dtype=np.float32)

    def add(self, t, x, gain=1.0):
        i = int(t * SR)
        if i < 0 or i >= len(self.buf):
            return
        seg = x[: len(self.buf) - i]
        self.buf[i: i + len(seg)] += seg * gain

    def out(self):
        return self.buf


# ---------------- the score ----------------

BPM = 132
BEAT = 60.0 / BPM
SW = (0.58, 0.42)  # swing eighth pair


def eighth_times(bar_t, count=8):
    """Swung eighth onsets within a bar starting at bar_t."""
    ts, t = [], bar_t
    for i in range(count):
        ts.append(t)
        t += BEAT * SW[i % 2]
    return ts


# note grids: (degree offsets in semitones from C4=60)
C4 = 60


def lead(mx, t, n, dur, vol=0.30, duty=0.25, vib=0.0):
    mx.add(t, square(midi_f(n), dur, duty=duty, vol=vol, decay=dur * 0.9, vib=vib))


def harm(mx, t, n, dur, vol=0.14):
    mx.add(t, square(midi_f(n), dur, duty=0.5, vol=vol, decay=dur * 0.9))


def bass(mx, t, n, dur, vol=0.5):
    mx.add(t, triangle(midi_f(n), dur, vol=vol, decay=dur))


def drums_bar(mx, bar_t, pattern="full", vol=1.0):
    ts = eighth_times(bar_t)
    for i, tt in enumerate(ts):
        if pattern == "full":
            if i in (0, 4):
                mx.add(tt, noise(0.09, 0.34 * vol, decay=0.05, lp=900, seed=i + 2))  # kick-ish
            if i in (2, 6):
                mx.add(tt, noise(0.12, 0.30 * vol, decay=0.07, lp=4000, seed=i + 9))  # snare
            mx.add(tt, noise(0.03, 0.10 * vol, decay=0.02, seed=i + 20))  # hat
        elif pattern == "hat":
            mx.add(tt, noise(0.03, 0.08 * vol, decay=0.02, seed=i + 20))


# --- melody data (semitone offsets; None = rest) ---
# A phrase: bouncy call
A_MEL = [(4, .5), (7, .5), (9, .5), (7, .5), (4, .5), (0, .5), (2, .5), (4, 1.0),
         (None, .5), (2, .5), (4, .5), (5, .5), (7, 1.0), (4, .5), (0, .5), (None, .5)]
# A' answer
A2_MEL = [(5, .5), (9, .5), (11, .5), (9, .5), (7, .5), (4, .5), (2, .5), (0, 1.0),
          (None, .5), (4, .5), (2, .5), (4, .5), (0, 1.5), (None, .5), (None, .5), (None, 0.5)]
# B phrase: minor lift
B_MEL = [(9, .5), (12, .5), (16, .5), (14, .5), (12, .5), (9, .5), (7, .5), (9, 1.0),
         (5, .5), (9, .5), (12, .5), (11, .5), (7, 1.0), (2, .5), (4, .5), (None, .5)]

A_CHORDS = [0, -3, 5, 7]   # C Am F G roots (relative)
B_CHORDS = [-3, 5, 0, 7]


def play_phrase(mx, t0, mel, chords, key=C4, drums=True, harm_off=-3, lead_vol=0.30):
    """One 4-bar phrase. mel = list of (semi, dur_in_swung_8ths)."""
    # bass + drums per bar
    for b in range(4):
        bt = t0 + b * 4 * BEAT
        root = key - 12 + chords[b % len(chords)]
        bass(mx, bt, root, BEAT * 1.4)
        bass(mx, bt + 2 * BEAT, root + 7, BEAT * 1.2, vol=0.42)
        if drums:
            drums_bar(mx, bt)
    # melody rides swung eighths
    ts = []
    for b in range(4):
        ts += eighth_times(t0 + b * 4 * BEAT)
    i = 0
    for semi, ln in mel:
        if i >= len(ts):
            break
        tt = ts[i]
        ndur = BEAT * ln * 1.05
        if semi is not None:
            lead(mx, tt, key + 12 + semi, ndur, vol=lead_vol)
            harm(mx, tt, key + 12 + semi + harm_off, ndur)
        i += max(1, int(round(ln * 2)))
    return t0 + 16 * BEAT


def title_fanfare(mx, t0=0.15):
    run = [0, 4, 7, 12, 16, 19, 24]
    for i, s in enumerate(run):
        lead(mx, t0 + i * 0.09, C4 + s, 0.14, vol=0.30, duty=0.5)
    # big chord w/ vibrato
    for s, v in ((0, 0.20), (4, 0.18), (7, 0.18), (12, 0.24)):
        mx.add(t0 + 0.75, square(midi_f(C4 + 12 + s), 1.5, duty=0.25, vol=v,
                                 decay=1.4, vib=0.006))
    bass(mx, t0 + 0.75, C4 - 12, 1.6)
    mx.add(t0 + 0.75, noise(0.5, 0.3, decay=0.3, lp=1200, seed=3))
    # cheeky noodle up to the theme
    nd = [(2.6, 7), (2.85, 9), (3.1, 11), (3.35, 12), (3.9, 11), (4.15, 9), (4.4, 7), (4.65, 4)]
    for tt, s in nd:
        lead(mx, t0 + tt, C4 + s, 0.2, vol=0.22)
        harm(mx, t0 + tt, C4 + s - 12, 0.2)


def underground(mx, t0, t1):
    """Sparse staccato low pairs, echo-y."""
    riff = [(0, 0), (0.5, 12), (1.2, -2), (1.7, 10), (2.4, -4), (2.9, 8),
            (3.6, -2), (4.1, 10)]
    base = C4 - 24 + 10  # Bb-ish gloom
    t = t0
    while t < t1 - 0.5:
        for dt, s in riff:
            if t + dt > t1 - 0.3:
                break
            for echo, g in ((0.0, 0.5), (0.22, 0.22)):
                mx.add(t + dt + echo, triangle(midi_f(base + s), 0.16, vol=0.55 * g,
                                               decay=0.15))
                mx.add(t + dt + echo, square(midi_f(base + s + 12), 0.12, duty=0.5,
                                             vol=0.10 * g, decay=0.1))
        t += 4.8


def flag_run(mx, t0):
    """Descending scale as he slides."""
    sc = [24, 23, 21, 19, 17, 16, 14, 12, 11, 9, 7, 5, 4, 2, 0]
    for i, s in enumerate(sc):
        lead(mx, t0 + i * 0.105, C4 + 12 + s, 0.11, vol=0.26, duty=0.5)


def victory_jingle(mx, t0):
    steps = [(0.0, [0, 4, 7]), (0.35, [5, 9, 12]), (0.7, [7, 11, 14]),
             (1.15, [12, 16, 19])]
    for dt, chord in steps:
        for s in chord:
            mx.add(t0 + dt, square(midi_f(C4 + s), 0.32 if dt < 1 else 1.6, duty=0.25,
                                   vol=0.16, decay=0.3 if dt < 1 else 1.4,
                                   vib=0.007 if dt >= 1 else 0))
        bass(mx, t0 + dt, C4 - 12 + chord[0], 0.35 if dt < 1 else 1.6)
    mx.add(t0 + 1.15, noise(0.6, 0.26, decay=0.35, lp=1500, seed=8))
    # tail melody
    tail = [(2.2, 16), (2.5, 14), (2.8, 12), (3.1, 16), (3.55, 19), (4.1, 24)]
    for tt, s in tail:
        lead(mx, t0 + tt, C4 + s, 0.5 if tt > 4 else 0.28, vol=0.24, vib=0.006)


def end_musicbox(mx, t0, t1):
    arp = [0, 7, 12, 16, 12, 7]
    t = t0
    k = 0
    vol = 0.20
    while t < t1 - 0.3:
        s = arp[k % len(arp)] + (12 if (k // len(arp)) % 2 else 0)
        fade = max(0.25, 1 - (t - t0) / (t1 - t0))
        mx.add(t, square(midi_f(C4 + 12 + s), 0.42, duty=0.5, vol=vol * fade,
                         decay=0.4))
        t += 0.30
        k += 1
    # final held note w/ vibrato, blipped off
    mx.add(t1 - 1.4, square(midi_f(C4 + 24), 1.2, duty=0.25, vol=0.20, decay=1.1,
                            vib=0.009))


# ---------------- SFX ----------------

def sfx_jump():
    return square(220, 0.24, duty=0.5, vol=0.5, decay=0.22, sweep_to=680)


def sfx_hop():
    return square(260, 0.16, duty=0.5, vol=0.4, decay=0.15, sweep_to=560)


def sfx_bonk():
    return (square(110, 0.1, duty=0.5, vol=0.6, decay=0.08)
            + np.pad(noise(0.05, 0.3, decay=0.03, seed=5), (0, int(0.05 * SR))))


def sfx_panel():
    x1 = square(midi_f(76), 0.09, duty=0.25, vol=0.4, decay=0.08)
    x2 = square(midi_f(83), 0.14, duty=0.25, vol=0.4, decay=0.12)
    return np.concatenate([x1, x2])


def sfx_ding():
    x1 = square(midi_f(88), 0.09, duty=0.5, vol=0.45, decay=0.08)
    x2 = (square(midi_f(96), 0.5, duty=0.5, vol=0.4, decay=0.45, vib=0.004)
          + square(midi_f(100), 0.5, duty=0.25, vol=0.12, decay=0.4))
    return np.concatenate([x1, x2])


def sfx_coin():
    x1 = square(midi_f(95), 0.08, duty=0.25, vol=0.5, decay=0.07)
    x2 = square(midi_f(100), 0.55, duty=0.25, vol=0.45, decay=0.5)
    return np.concatenate([x1, x2])


def sfx_stomp():
    a = noise(0.14, 0.55, decay=0.09, lp=2500, seed=11)
    b = square(300, 0.2, duty=0.5, vol=0.5, decay=0.18, sweep_to=70)
    n = max(len(a), len(b))
    return np.pad(a, (0, n - len(a))) + np.pad(b, (0, n - len(b)))


def sfx_warp():
    a = square(700, 0.75, duty=0.5, vol=0.45, decay=0.7, sweep_to=90)
    b = noise(0.7, 0.12, decay=0.5, lp=1000, seed=13)
    n = max(len(a), len(b))
    return np.pad(a, (0, n - len(a))) + np.pad(b, (0, n - len(b)))


def sfx_popout():
    return square(90, 0.5, duty=0.5, vol=0.42, decay=0.45, sweep_to=700)


def sfx_boom(seed=21):
    return noise(0.8, 0.55, decay=0.30, lp=700, seed=seed)


def sfx_sparkle(seed=31):
    rng = np.random.default_rng(seed)
    notes = sorted(rng.integers(88, 103, 6))[::-1]
    out = []
    for n in notes:
        out.append(square(midi_f(n), 0.07, duty=0.25, vol=0.16, decay=0.06))
    return np.concatenate(out)
