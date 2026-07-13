"""Ep3 soundtrack: BATTLE MUSIC. A new composition — dueling motifs, one war.

Structure: ominous drone -> Grokio's phrygian riff -> 168bpm battle theme where
Claudio's ep1 motif and Grokio's riff trade fours -> Grokio dominance -> the
strip-down (near defeat) -> major-key comeback -> stop-time final hit ->
sunset reprise of the ep1 theme, slow and warm -> end sting.
"""
import wave

import numpy as np

import chiptune as ch
from ep3_beats import *  # noqa: F401,F403

SR = ch.SR
TOTAL_S = TOTAL + 0.3

music = ch.Mix(TOTAL_S)
sfx = ch.Mix(TOTAL_S)

BB = 60.0 / 168  # battle beat


def bar8(bar_t):
    """Straight 8th onsets (battle music doesn't swing — it marches)."""
    return [bar_t + i * BB * 0.5 for i in range(8)]


def battle_drums(t0, bars, intensity=1.0, half=False):
    for b in range(bars):
        bt = t0 + b * 4 * BB
        for i, tt in enumerate(bar8(bt)):
            if half:
                if i == 0:
                    music.add(tt, ch.noise(0.1, 0.4 * intensity, decay=0.06, lp=800, seed=i + 2))
                if i == 4:
                    music.add(tt, ch.noise(0.14, 0.34 * intensity, decay=0.08, lp=3500, seed=i + 9))
            else:
                if i in (0, 3, 4, 6):  # driving kick pattern
                    music.add(tt, ch.noise(0.09, 0.36 * intensity, decay=0.05, lp=900, seed=i + 2))
                if i in (2, 6):
                    music.add(tt, ch.noise(0.11, 0.30 * intensity, decay=0.06, lp=3800, seed=i + 9))
                music.add(tt, ch.noise(0.025, 0.10 * intensity, decay=0.015, seed=i + 20))


def tri_bass_16(t0, bars, roots, vol=0.55):
    """Relentless 16th-note triangle bass."""
    for b in range(bars):
        bt = t0 + b * 4 * BB
        root = roots[b % len(roots)]
        for i in range(16):
            n = root if i % 4 != 3 else root + (12 if i % 8 == 7 else 7)
            music.add(bt + i * BB / 4, ch.triangle(ch.midi_f(n), BB / 4 * 0.9,
                                                   vol=vol, decay=BB / 4))


# Claudio's motif (from ep1 A_MEL, battle-hardened) in A minor
CLAUDIO_RIFF = [(0, .5), (3, .5), (5, .5), (3, .5), (0, .5), (-2, .5), (0, 1.0),
                (None, .5), (3, .5), (5, .5), (7, .5), (5, .5), (3, .5), (0, 1.0), (None, .5)]
# Grokio's riff: phrygian menace (b2 stabs)
GROKIO_RIFF = [(0, .5), (1, .5), (0, .5), (None, .5), (7, .5), (6, .5), (7, .5), (None, .5),
               (0, .5), (1, .5), (3, .5), (1, .5), (0, .5), (-5, .5), (0, 1.0), (None, .5)]


def play_riff(t0, riff, key, vol=0.30, duty=0.25, harm_int=-5, detune=0.0):
    ts = []
    for b in range(4):
        ts += bar8(t0 + b * 4 * BB)
    i = 0
    for semi, ln in riff:
        if i >= len(ts):
            break
        if semi is not None:
            f = ch.midi_f(key + semi) * (1 + detune)
            music.add(ts[i], ch.square(f, BB * ln * 1.05, duty=duty, vol=vol,
                                       decay=BB * ln))
            music.add(ts[i], ch.square(ch.midi_f(key + semi + harm_int), BB * ln,
                                       duty=0.5, vol=vol * 0.45, decay=BB * ln))
        i += max(1, int(round(ln * 2)))
    return t0 + 16 * BB


A3 = 57  # A minor home

# ---------------- act 1: arrival ----------------
# ominous drone + timpani booms under the title
music.add(0.0, ch.triangle(ch.midi_f(A3 - 24), 4.2, vol=0.5, decay=None)
          * np.linspace(0.4, 1.0, int(4.2 * SR)))
for bt in (0.8, 2.4, 3.6):
    music.add(bt, ch.noise(0.5, 0.35, decay=0.3, lp=500, seed=int(bt * 10)))
# lightning cracks
for lt in LIGHTNING:
    sfx.add(lt, ch.noise(0.3, 0.65, decay=0.1, lp=None, seed=int(lt * 7)))
    sfx.add(lt + 0.05, ch.noise(0.6, 0.3, decay=0.4, lp=900, seed=int(lt * 9)))
# descent whistle + LAND boom
sfx.add(DESCEND[0], ch.square(1200, DESCEND[1] - DESCEND[0], duty=0.5, vol=0.18,
                              decay=None, sweep_to=140))
sfx.add(LAND, ch.noise(0.7, 0.7, decay=0.25, lp=600, seed=31))
sfx.add(LAND, ch.square(70, 0.5, duty=0.5, vol=0.5, decay=0.45, sweep_to=30))

# grokio's theme while he stares (half-time, phrygian)
gk = A3 - 12
play_riff(LAND + 0.4, GROKIO_RIFF, gk, vol=0.26, duty=0.5)
battle_drums(LAND + 0.4, 2, intensity=0.8, half=True)

# snare build into the charge
t = FACEOFF[1] - 1.3
i = 0
while t < CHARGE + 0.7:
    music.add(t, ch.noise(0.06, 0.22 + i * 0.02, decay=0.04, lp=3800, seed=i))
    t += 0.12 - min(0.06, i * 0.004)
    i += 1

# ---------------- act 2: THE BATTLE THEME ----------------
bt0 = KNOCKBACK_END  # theme slams in as they land from the clash
# trade fours: claudio riff / grokio riff / claudio var / grokio var
t = bt0
t = play_riff(t, CLAUDIO_RIFF, A3 + 12, vol=0.30)
t = play_riff(t, GROKIO_RIFF, A3 + 12, vol=0.30, duty=0.5)
t = play_riff(t, CLAUDIO_RIFF, A3 + 15, vol=0.31)          # up a third — escalating
tri_bass_16(bt0, 12, (A3 - 12, A3 - 12, A3 - 14, A3 - 16))
battle_drums(bt0, 12, intensity=1.0)

# grokio dominance (pipe smash -> down): his riff, lower, slower feel
gd0 = t
play_riff(gd0, GROKIO_RIFF, A3, vol=0.30, duty=0.5, detune=0.004)
tri_bass_16(gd0, 4, (A3 - 24, A3 - 24, A3 - 23, A3 - 24), vol=0.6)
battle_drums(gd0, 4, intensity=0.9, half=True)

# ---------------- act 3: near defeat (strip down) ----------------
sd0 = DOWN[0] + 0.5
# lone heartbeat + a slow sad fragment of Claudio's ep1 melody
tt = sd0
while tt < POWERUP[0] - 0.4:
    music.add(tt, ch.square(55, 0.22, duty=0.5, vol=0.30, decay=0.2))
    tt += 1.1
frag = [(4, 1.0), (0, 1.0), (2, 1.0), (4, 2.0)]
ft = sd0 + 0.8
for semi, ln in frag:
    music.add(ft, ch.square(ch.midi_f(60 + semi), ln * 0.62, duty=0.5, vol=0.14,
                            decay=ln * 0.6, vib=0.005))
    ft += ln * 0.72
# mega ball charge rumble
n_ch = int((MEGA_CHARGE[1] - MEGA_CHARGE[0]) * SR)
rumble = ch.noise(MEGA_CHARGE[1] - MEGA_CHARGE[0], 0.16, decay=None, lp=300, seed=77)[:n_ch]
rumble *= np.linspace(0.2, 1.0, len(rumble)) ** 2
music.add(MEGA_CHARGE[0], rumble)

# bug cap moment: tiny music-box tenderness
for i, s in enumerate((7, 12, 16)):
    music.add(BUG_CAP[0] + 1.2 + i * 0.35, ch.square(ch.midi_f(72 + s), 0.4, duty=0.5,
                                                     vol=0.13, decay=0.35))
sfx.add(CAP_ON, ch.sfx_coin(), 0.7)

# ---------------- act 4: comeback ----------------
# power-up shimmer
pu = POWERUP[0] + 0.3
for i in range(14):
    music.add(pu + i * 0.11, ch.square(ch.midi_f(64 + i * 2), 0.14, duty=0.25,
                                       vol=0.16 + i * 0.008, decay=0.12))
# A MAJOR, fast — claudio's riff triumphant, key up
cb0 = POWERUP[1]
maj = [(0, .5), (4, .5), (7, .5), (4, .5), (0, .5), (-3, .5), (0, 1.0),
       (None, .5), (4, .5), (7, .5), (9, .5), (7, .5), (12, .5), (12, 1.0), (None, .5)]
play_riff(cb0, maj, A3 + 12, vol=0.33)
tri_bass_16(cb0, 4, (A3 - 12, A3 - 8, A3 - 7, A3 - 12), vol=0.6)
battle_drums(cb0, 4, intensity=1.1)

# stop-time: everything cuts for the final hit, then a huge stab
stab_t = FINAL_HIT + 0.06
for s, v in ((0, 0.26), (4, 0.22), (7, 0.22), (12, 0.3)):
    music.add(stab_t, ch.square(ch.midi_f(A3 + 12 + s), 1.6, duty=0.25, vol=v,
                                decay=1.5, vib=0.006))
music.add(stab_t, ch.triangle(ch.midi_f(A3 - 12), 1.6, vol=0.6, decay=1.5))
music.add(stab_t, ch.noise(0.7, 0.4, decay=0.4, lp=1200, seed=88))

# ---------------- act 5: aftermath (sunset reprise) ----------------
# the ep1 A melody, half speed, warm — grief and relief
af0 = AFTERMATH[0] + 0.6


def sunset_phrase(t0, key=60):
    ts = t0
    for semi, ln in ch.A_MEL:
        if semi is not None:
            music.add(ts, ch.square(ch.midi_f(key + 12 + semi), ln * 0.95, duty=0.5,
                                    vol=0.17, decay=ln * 0.9, vib=0.004))
            music.add(ts, ch.square(ch.midi_f(key + semi - 5), ln * 0.95, duty=0.5,
                                    vol=0.08, decay=ln * 0.9))
        ts += ln * 0.95
    return ts


te = sunset_phrase(af0)
roots = (48, 45, 41, 43)
for b in range(4):
    music.add(af0 + b * 2.85, ch.triangle(ch.midi_f(roots[b % 4] - 12), 2.7, vol=0.42,
                                          decay=2.6))
sunset_phrase(te + 0.3)
for b in range(2):
    music.add(te + 0.3 + b * 2.85, ch.triangle(ch.midi_f(roots[b % 4] - 12), 2.7,
                                               vol=0.4, decay=2.6))

# end sting
es = END_CARD + 0.4
for i, s in enumerate((0, 4, 7, 12)):
    music.add(es + i * 0.16, ch.square(ch.midi_f(60 + s), 0.9 if i == 3 else 0.2,
                                       duty=0.25, vol=0.2, decay=0.8 if i == 3 else 0.18,
                                       vib=0.006 if i == 3 else 0))
sfx.add(TOTAL - 1.2, ch.sfx_coin(), 0.55)

# ---------------- combat SFX ----------------
whoosh = lambda seed=1: ch.noise(0.25, 0.3, decay=0.15, lp=2200, seed=seed)


def hit_sfx(big=False, seed=1):
    a = ch.noise(0.16 if big else 0.1, 0.6 if big else 0.45, decay=0.08, lp=2000, seed=seed)
    b = ch.square(220 if big else 300, 0.18, duty=0.5, vol=0.5, decay=0.15,
                  sweep_to=60 if big else 90)
    n = max(len(a), len(b))
    return np.pad(a, (0, n - len(a))) + np.pad(b, (0, n - len(b)))


events = [
    (CHARGE, whoosh(3), 0.8), (CHARGE + 0.3, whoosh(4), 0.8),
    (CLASH, hit_sfx(True, 5), 1.2),
    (CLASH, ch.noise(0.5, 0.4, decay=0.3, lp=700, seed=6), 1.0),
]
for fi, ft in enumerate(FIREBALLS):
    events.append((ft, ch.square(500, 0.4, duty=0.5, vol=0.35, decay=0.35, sweep_to=160), 1.0))
    events.append((ft, ch.noise(0.4, 0.22, decay=0.25, lp=1500, seed=40 + fi), 1.0))
events += [
    (DODGE1, whoosh(7), 0.7), (DODGE2, whoosh(8), 0.7),
    (BLOCKS_BOOM, ch.sfx_boom(50), 1.3),
    (BLOCKS_BOOM + 0.1, ch.noise(0.8, 0.4, decay=0.4, lp=2500, seed=51), 0.9),  # debris clatter
    (STARSHOT, ch.square(700, 0.5, duty=0.25, vol=0.4, decay=0.4, sweep_to=1400), 0.9),
    (STARSHOT_HIT, hit_sfx(False, 9), 1.0),
]
for i, ht in enumerate(MELEE_HITS):
    events.append((ht, hit_sfx(i == 5, 10 + i), 1.0))
events += [
    (PIPE_SMASH, hit_sfx(True, 20), 1.1),
    (PIPE_SMASH + 0.05, ch.square(880, 0.9, duty=0.5, vol=0.3, decay=0.8, sweep_to=440), 0.9),  # clang
    (UPPERCUT1 + 0.25, hit_sfx(True, 21), 1.2),
    (UPPERCUT1 + 0.3, ch.square(200, 0.8, duty=0.5, vol=0.35, decay=0.7, sweep_to=900), 0.8),  # rising launch
    (HILL_CRASH, ch.sfx_boom(52), 1.2),
    (HILL_CRASH, ch.noise(0.9, 0.5, decay=0.5, lp=400, seed=53), 1.0),
    (MEGA_THROW, ch.square(300, 0.7, duty=0.5, vol=0.45, decay=0.6, sweep_to=80), 1.0),
    (MEGA_MISS, whoosh(60), 1.0),
    (HORIZON_BOOM, ch.sfx_boom(61), 1.4),
    (HORIZON_BOOM + 0.2, ch.noise(1.6, 0.5, decay=0.9, lp=350, seed=62), 1.1),
    (FINAL_HIT, hit_sfx(True, 70), 1.35),
    (FINAL_HIT + 0.5, ch.square(150, 1.4, duty=0.5, vol=0.25, decay=1.2, sweep_to=1500), 0.7),  # fly off
    (TWINKLE, ch.square(ch.midi_f(100), 0.5, duty=0.25, vol=0.35, decay=0.45), 0.9),
    (TWINKLE + 0.08, ch.square(ch.midi_f(104), 0.4, duty=0.25, vol=0.25, decay=0.35), 0.9),
]
for i in range(4):  # combo flurry
    events.append((COMBO[0] + 0.25 + i * 0.45, hit_sfx(False, 30 + i), 1.0))
for et, ex, eg in events:
    sfx.add(et, ex, eg)
# fire crackle through the aftermath
rng = np.random.default_rng(90)
tt = HILL_CRASH + 1
while tt < END_CARD:
    sfx.add(tt, ch.noise(0.05, 0.09, decay=0.03, seed=int(tt * 37)), 1.0)
    tt += rng.uniform(0.25, 0.7)

# ---------------- master ----------------
master = music.out() * 0.92 + sfx.out()
peak = np.abs(master).max()
master *= 0.86 / peak
st = np.stack([master, master], axis=1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("out/ep3_audio.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print(f"ep3 audio {len(master)/SR:.2f}s peak {peak:.3f}")
