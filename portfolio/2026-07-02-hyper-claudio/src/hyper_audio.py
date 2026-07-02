"""The line, word by word, with timings for lipsync: pitch-shifted plumber TTS."""
import json
import sys
import wave

import numpy as np

sys.path.insert(0, "/home/april/ytp-fable")
from ytp_audio import SR, gain, pitch, say, silence  # noqa: E402

WORDS = ["Thanks", "a", "so", "much", "for", "a", "to", "playing", "a", "my", "game."]
LEAD_IN = 1.5
GAP = 0.045


def build():
    segs = []
    timings = []
    t = LEAD_IN
    for w in WORDS:
        x = say(w, length_scale=1.02)
        # trim silence piper pads around isolated words
        env = np.abs(x)
        k = int(0.006 * SR)
        c = np.convolve(env, np.ones(k) / k, mode="same")
        nz = np.nonzero(c > 0.01)[0]
        if len(nz):
            x = x[max(0, nz[0] - 220): nz[-1] + 400]
        x = pitch(x, +3.2)  # plumber register
        segs.append(x)
        timings.append({"word": w, "t": round(t, 4), "dur": round(len(x) / SR, 4)})
        t += len(x) / SR + GAP
    total = t + 1.9  # outro hold

    out = np.zeros(int(total * SR), dtype=np.float32)
    for seg, tm in zip(segs, timings):
        i = int(tm["t"] * SR)
        out[i:i + len(seg)] += seg
    # gentle room: two short early reflections
    for dms, g in ((17, 0.22), (31, 0.12)):
        d = int(dms * SR / 1000)
        out[d:] += out[:-d] * g
    out *= 0.82 / np.abs(out).max()

    st = np.stack([out, out], axis=1)
    pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
    with wave.open("out/hyper_voice.wav", "wb") as f:
        f.setnchannels(2)
        f.setsampwidth(2)
        f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    # rms envelope at 24fps for jaw modulation
    fps = 24
    win = SR // fps
    n = len(out) // win
    rms = np.sqrt((out[:n * win].reshape(n, win) ** 2).mean(axis=1))
    rms = (rms / (rms.max() + 1e-9)).tolist()
    json.dump({"total": total, "timings": timings, "rms24": [round(v, 4) for v in rms]},
              open("out/hyper_timings.json", "w"), indent=1)
    print(f"voice: {total:.2f}s, {len(WORDS)} words")
    for tm in timings:
        print(f"  {tm['t']:5.2f}s  {tm['word']}")


if __name__ == "__main__":
    build()
