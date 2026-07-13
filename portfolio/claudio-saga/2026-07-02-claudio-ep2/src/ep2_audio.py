"""Ep2 soundtrack: the score corrupts along the same curve as the picture."""
import wave

import numpy as np

import chiptune as ch
from ep2_beats import *  # noqa: F401,F403

SR = ch.SR
TOTAL_S = TOTAL + 0.2


def corruption_amt(t):
    if t < CORR1[0]:
        return 0.0
    if t < CORR1[1]:
        return 0.5 * (t - CORR1[0]) / (CORR1[1] - CORR1[0])
    if t < CORR2[1]:
        return 0.5 + 0.5 * (t - CORR2[0]) / (CORR2[1] - CORR2[0])
    return 1.0


def corrupt_audio(x, t0, chunk_s=0.45, seed=5):
    """Progressively derange a rendered music buffer (YTP craft, chip flavor)."""
    rng = np.random.default_rng(seed)
    n = int(chunk_s * SR)
    out = x.copy()
    for i in range(len(x) // n):
        t = t0 + i * chunk_s
        a = corruption_amt(t)
        if a <= 0.02:
            continue
        c0 = i * n
        seg = out[c0:c0 + n].copy()
        if rng.random() < a * 0.55:  # stutter
            piece = seg[: int(n * rng.uniform(0.12, 0.3))]
            reps = int(np.ceil(n / len(piece)))
            seg = np.tile(piece, reps)[:n]
        if rng.random() < a * 0.3:  # reverse
            seg = seg[::-1].copy()
        if rng.random() < a * 0.6:  # rate wobble
            f = 1 + a * 0.45 * np.sin(i * 1.7)
            m = int(n / f)
            seg = np.interp(np.linspace(0, n - 1, m), np.arange(n), seg)
            seg = np.pad(seg, (0, max(0, n - len(seg))))[:n].astype(np.float32)
        if a > 0.35:  # bitcrush deepens
            lv = max(2, int(14 - 12 * a))
            seg = np.round(seg * lv) / lv
            dec = 1 + int(5 * a)
            seg = np.repeat(seg[::dec], dec)[:n]
            seg = np.pad(seg, (0, max(0, n - len(seg))))
        if rng.random() < a * 0.15:  # dropout
            seg *= 0.0
        out[c0:c0 + n] = seg
    return out


def zap(seed=1, dur=0.16, f0=1400, f1=120):
    return (ch.square(f0, dur, duty=0.5, vol=0.4, decay=dur * 0.9, sweep_to=f1)
            + ch.noise(dur, 0.18, decay=dur * 0.5, seed=seed)[: int(dur * SR)])


def hurt_wah():
    a = ch.square(300, 0.5, duty=0.25, vol=0.5, decay=0.45, sweep_to=85)
    t = np.arange(len(a)) / SR
    return (a * (1 + 0.4 * np.sin(2 * np.pi * 11 * t))).astype(np.float32) * 0.8


def detuned_pair(f, dur, beat_hz=2.7, vol=0.1):
    a = ch.square(f, dur, duty=0.5, vol=vol, decay=None)
    b = ch.square(f + beat_hz, dur, duty=0.5, vol=vol, decay=None)
    n = min(len(a), len(b))
    x = a[:n] + b[:n]
    fade = min(n, int(0.4 * SR))
    x[:fade] *= np.linspace(0, 1, fade)
    x[-fade:] *= np.linspace(1, 0, fade)
    return x


music = ch.Mix(TOTAL_S)
sfx = ch.Mix(TOTAL_S)

# --- act 1: innocence ---
ch.title_fanfare(music, 0.15)
theme1 = ch.Mix(10.0)
ch.play_phrase(theme1, 0.0, ch.A_MEL, ch.A_CHORDS)
seg = theme1.out()[: int((FREEZE - 5.0) * SR)]
fade_n = int(0.12 * SR)
seg[-fade_n:] *= np.linspace(1, 0, fade_n)
music.add(5.0, seg)

# needle stop
sfx.add(FREEZE - 0.05, ch.square(420, 0.5, duty=0.5, vol=0.45, decay=0.45, sweep_to=35))
# panel + cursor blinks
sfx.add(PANEL_ON, ch.sfx_panel(), 0.9)
t = PANEL_ON + 0.6
k = 0
while t < TIMEOUT - 0.15:
    f = 660 if k % 2 == 0 else 520
    sfx.add(t, ch.square(f, 0.05, duty=0.25, vol=0.16, decay=0.05))
    t += 0.42
    k += 1
# timeout buzzer
for i in range(2):
    sfx.add(TIMEOUT + i * 0.28, ch.square(96, 0.22, duty=0.5, vol=0.55, decay=0.2))
# fall + splat
sfx.add(FALL, ch.square(900, 0.55, duty=0.5, vol=0.4, decay=0.5, sweep_to=180))
sfx.add(SPLAT, ch.noise(0.25, 0.6, decay=0.12, lp=1600, seed=4))
# bug scuttle + HIT
t = BUG_CHARGE
while t < BUG_HIT:
    sfx.add(t, ch.noise(0.03, 0.14, decay=0.02, seed=int(t * 100)))
    t += 0.07
sfx.add(BUG_HIT, zap(seed=2, dur=0.3, f0=2000, f1=90), 1.1)
sfx.add(BUG_HIT + 0.05, hurt_wah())
sfx.add(BUG_HIT + 0.25, ch.square(240, 0.5, duty=0.25, vol=0.3, decay=0.45, sweep_to=880))  # cap boing
# glitch ticks
sfx.add(TICK1, zap(seed=3), 0.9)
sfx.add(TICK2, zap(seed=4, f0=900, f1=60), 0.9)
# woozy beating tones
sfx.add(GETUP[0], detuned_pair(ch.midi_f(52), GETUP[1] - GETUP[0], 3.1, vol=0.08))

# --- act 2: the corrupted theme ---
theme2 = ch.Mix(CORR2[1] - CORR1[0] + 2)
tt = 0.0
tt = ch.play_phrase(theme2, tt, ch.A_MEL, ch.A_CHORDS)
tt = ch.play_phrase(theme2, tt, ch.A2_MEL, ch.A_CHORDS)
tt = ch.play_phrase(theme2, tt, ch.B_MEL, ch.B_CHORDS, lead_vol=0.33)
half = 8 * ch.BEAT
theme2b = theme2.out()[: int((BSOD[0] - CORR1[0]) * SR)]
corrupted = corrupt_audio(theme2b.astype(np.float32), CORR1[0])
fade_n = int(0.1 * SR)
corrupted[-fade_n:] *= np.linspace(1, 0, fade_n)
music.add(CORR1[0], corrupted)
# zaps synced to dialog toasts
i = 0
while ERRORS_FROM + i * 1.7 < BSOD[0]:
    sfx.add(ERRORS_FROM + i * 1.7, zap(seed=10 + i, f0=1600 - i * 120, f1=70), 0.55)
    i += 1
# ring-mod shriek layer near the peak
shr = ch.square(2200, BSOD[0] - 35.0, duty=0.5, vol=0.06)
tsh = np.arange(len(shr)) / SR
shr = (shr * np.sin(2 * np.pi * (90 + 60 * tsh) * tsh)).astype(np.float32)
shr *= np.linspace(0, 1, len(shr)) ** 2
music.add(35.0, shr)

# --- BSOD ---
sfx.add(BSOD[0], ch.noise(0.45, 0.7, decay=0.28, seed=44))
# then silence

# --- the void ---
t = VOID[0] + 0.4
while t < VOID[1]:
    sfx.add(t, ch.square(52, 0.3, duty=0.5, vol=0.30, decay=0.28))  # heart thump
    sfx.add(t + 0.18, ch.square(48, 0.2, duty=0.5, vol=0.18, decay=0.18))
    t += 1.25
music.add(VOID[0] + 0.3, detuned_pair(ch.midi_f(45), VOID[1] - VOID[0] - 0.6, 2.2, vol=0.05))
music.add(VOID[0], ch.noise(VOID[1] - VOID[0], 0.03, decay=None, lp=3000, seed=50)
          [: int((VOID[1] - VOID[0]) * SR)])
sfx.add(REMINDER_TXT, ch.square(ch.midi_f(88), 0.12, duty=0.25, vol=0.14, decay=0.1))

# --- reassembly, wrong ---
sfx.add(REASSEMBLE[0], ch.square(90, 0.9, duty=0.5, vol=0.4, decay=0.8, sweep_to=800))
for j_, s in enumerate((0, 3, 7, 12)):  # minor stab
    music.add(REASSEMBLE[0] + 0.55, ch.square(ch.midi_f(57 + s) * 1.012 ** j_, 0.9,
                                              duty=0.25, vol=0.13, decay=0.8))
sfx.add(PANCAKE, ch.noise(0.3, 0.65, decay=0.14, lp=1200, seed=45))
sfx.add(PANCAKE + 0.02, ch.square(160, 0.3, duty=0.5, vol=0.5, decay=0.28, sweep_to=45))

# bug steps + climb
t = BUG_WALK[0]
while t < BUG_WALK[1]:
    sfx.add(t, ch.noise(0.03, 0.1, decay=0.02, seed=int(t * 91)), 0.8)
    t += 0.16
sfx.add(BUG_CLIMB, ch.sfx_hop(), 0.7)
sfx.add(SIGN_ON, ch.sfx_panel(), 0.6)

# --- bug's victory: the jingle, minor, detuned, slow ---
def bug_jingle(mx, t0):
    steps = [(0.0, [0, 3, 7]), (0.5, [5, 8, 12]), (1.0, [7, 10, 14]),
             (1.6, [12, 15, 19])]
    for dt, chord in steps:
        for si, s in enumerate(chord):
            f = ch.midi_f(60 + s) * (1 + 0.006 * si)  # sour detune between voices
            mx.add(t0 + dt, ch.square(f, 0.45 if dt < 1.5 else 2.2, duty=0.25,
                                      vol=0.15, decay=0.4 if dt < 1.5 else 2.0,
                                      vib=0.01 if dt >= 1.5 else 0))
        mx.add(t0 + dt, ch.triangle(ch.midi_f(36 + chord[0]), 0.5 if dt < 1.5 else 2.2,
                                    vol=0.5, decay=0.5 if dt < 1.5 else 2.0))


bug_jingle(music, BUG_CLIMB + 0.3)
# glitch fireworks
for gi, gt in enumerate(GLITCH_FW):
    boom = ch.sfx_boom(60 + gi)
    lv = 5
    boom = (np.round(boom * lv) / lv).astype(np.float32)  # crushed boom
    sfx.add(gt, boom, 0.9)
    spark = ch.sfx_sparkle(70 + gi)
    sfx.add(gt + 0.3, spark[::-1].copy(), 0.9)  # reversed sparkle = wrong

# --- corrupted end musicbox ---
def end_musicbox_wrong(mx, t0, t1):
    arp = [0, 7, 12, 16, 12, 7]
    wrong = [0, 6, 13, 16, 11, 8]  # sour variants
    rng = np.random.default_rng(9)
    t = t0
    k = 0
    while t < t1 - 0.4:
        use_wrong = rng.random() < min(0.85, 0.15 + (t - t0) / (t1 - t0))
        s = (wrong if use_wrong else arp)[k % 6] + (12 if (k // 6) % 2 else 0)
        f = ch.midi_f(72 + s) * (1 + 0.02 * np.sin(k * 1.3) * ((t - t0) / (t1 - t0)))
        fade = max(0.2, 1 - (t - t0) / (t1 - t0))
        mx.add(t, ch.square(f, 0.42, duty=0.5, vol=0.19 * fade, decay=0.38))
        t += 0.30 * (1 + 0.15 * np.sin(k * 0.9) * (t - t0) / (t1 - t0))  # flutter
        k += 1
    # final note bends down and dies
    a = ch.square(ch.midi_f(84), 1.3, duty=0.25, vol=0.2, decay=1.2, sweep_to=ch.midi_f(78))
    mx.add(t1 - 1.5, a)


end_musicbox_wrong(music, END_CARD + 0.3, TOTAL - 0.4)
sfx.add(TOTAL - 0.45, zap(seed=99, dur=0.12, f0=800, f1=100), 0.7)

# --- master ---
master = music.out() * 0.95 + sfx.out()
peak = np.abs(master).max()
master *= 0.86 / peak
st = np.stack([master, master], axis=1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("out/ep2_audio.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"ep2 audio {len(master)/SR:.2f}s peak {peak:.3f}")
