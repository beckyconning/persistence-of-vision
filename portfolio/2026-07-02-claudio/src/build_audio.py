"""Arrange the Claudio score + SFX along beats.py; writes out/claudio_audio.wav."""
import wave

import numpy as np

import chiptune as ch
from beats import *  # noqa: F401,F403

TOTAL_S = TOTAL + 0.2
PHRASE = 16 * ch.BEAT  # 7.27s

music_main = ch.Mix(TOTAL_S)   # theme + reprise (gets ducked at section cuts)
music_other = ch.Mix(TOTAL_S)  # fanfare / underground / flag / victory / end
sfx = ch.Mix(TOTAL_S)

# --- score ---
ch.title_fanfare(music_other, 0.15)

t = 6.0
t = ch.play_phrase(music_main, t, ch.A_MEL, ch.A_CHORDS)
t = ch.play_phrase(music_main, t, ch.A2_MEL, ch.A_CHORDS)
t = ch.play_phrase(music_main, t, ch.B_MEL, ch.B_CHORDS)
t = ch.play_phrase(music_main, t, ch.A_MEL, ch.A_CHORDS)
# reprise in D for the final stretch
ch.play_phrase(music_main, 38.2, ch.A2_MEL, ch.A_CHORDS, key=ch.C4 + 2, lead_vol=0.33)

ch.underground(music_other, 34.0, 37.8)
ch.flag_run(music_other, 42.35)
ch.victory_jingle(music_other, 44.6)
ch.end_musicbox(music_other, 50.9, 55.3)

# duck envelope for the main theme at section boundaries
env = np.ones(len(music_main.buf), dtype=np.float32)


def duck(t0, t1, v0, v1):
    i0, i1 = int(t0 * ch.SR), int(t1 * ch.SR)
    env[i0:i1] = np.linspace(v0, v1, i1 - i0)
    env[i1:] = v1


duck(33.45, 33.80, 1, 0)
duck(38.05, 38.15, 0, 1)
duck(42.05, 42.35, 1, 0)
music = music_main.out() * env + music_other.out()

# --- SFX ---
events = [
    (JUMP1, ch.sfx_jump(), 1.0),
    (BONK, ch.sfx_bonk(), 1.0),
    (PANEL_ON + 0.05, ch.sfx_panel(), 0.9),
    (DING, ch.sfx_ding(), 1.0),
    (DING + 0.15, ch.sfx_hop(), 0.6),
    (COIN_POP, ch.sfx_coin(), 1.0),
    (HOP, ch.sfx_hop(), 0.9),
    (JUMP2, ch.sfx_jump(), 1.0),
    (STOMP, ch.sfx_stomp(), 1.1),
    (SIGN_ON + 0.05, ch.sfx_panel(), 0.55),
    (PIPE_JUMP, ch.sfx_hop(), 0.9),
    (PIPE_DOWN[0], ch.sfx_warp(), 1.0),
    (POP_OUT[0], ch.sfx_popout(), 1.0),
    (POP_OUT[1] + 0.1, ch.sfx_hop(), 0.7),
    (FLAG_JUMP, ch.sfx_jump(), 1.0),
    (FIREWORKS[0], ch.sfx_boom(21), 1.0), (FIREWORKS[0] + 0.3, ch.sfx_sparkle(31), 1.0),
    (FIREWORKS[1], ch.sfx_boom(22), 1.0), (FIREWORKS[1] + 0.3, ch.sfx_sparkle(32), 1.0),
    (FIREWORKS[2], ch.sfx_boom(23), 1.0), (FIREWORKS[2] + 0.3, ch.sfx_sparkle(33), 1.0),
    (54.55, ch.sfx_coin(), 0.7),  # INSERT TOKEN
]
for et, ex, eg in events:
    sfx.add(et, ex, eg)

master = music * 0.9 + sfx.out() * 1.0
peak = np.abs(master).max()
master = master * (0.86 / peak)
st = np.stack([master, master], axis=1)
pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
with wave.open("out/claudio_audio.wav", "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(ch.SR)
    w.writeframes(pcm.tobytes())
print(f"audio {len(master)/ch.SR:.2f}s peak {peak:.3f} -> normalized 0.86")
