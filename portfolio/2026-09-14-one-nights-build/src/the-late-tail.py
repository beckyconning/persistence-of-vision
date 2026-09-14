# the-late-tail: seahorse1e6's real level-8 escape histogram (32400 samples) as sound.
# Stages = iteration limits 1024..131072 (2.5 s each). At limit L, every bucket that has escaped by L sounds as a
# partial (a fifth above the last); its loudness is sqrt(count share). The bucket the rule listens to (n in (L/2, L])
# trembles; a tick marks each raise (late >= 162 = 0.5%). The rule settles at 16384; the true tail beyond it
# (buckets 15-17: 36, 19, 5 samples) still sounds afterwards, but barely: what the rule no longer hears.
# A low drone follows the capped samples (inside the set, plus the not-yet-escaped).
import wave
import numpy as np
from PIL import Image

D = '/tmp/claude-1000/-home-april/7aec8f25-c3b5-4b49-8020-6b43fff59a7d/scratchpad/agreement/'
SR = 44100
SAMPLES = 32400
hist = {9: 14053, 10: 3555, 11: 905, 12: 350, 13: 167, 14: 66, 15: 36, 16: 19, 17: 5}
CAPPED_FINAL = 13244
THRESH = 162
stages = [1 << b for b in range(10, 18)]
settle = 16384
seg = 2.5
t_all = np.arange(int(SR * seg * len(stages))) / SR
out = np.zeros_like(t_all)

def freq(b):
    return 110.0 * 1.5 ** (b - 9)

phase_len = int(SR * seg)
for s, L in enumerate(stages):
    lb = L.bit_length() - 1
    i0 = s * phase_len
    t = t_all[i0:i0 + phase_len]
    env = np.minimum(1.0, np.minimum((t - t[0]) / 0.08, (t[-1] - t) / 0.12))
    settled = L > settle
    for b, count in hist.items():
        if b > lb:
            continue
        amp = np.sqrt(count / SAMPLES) * 0.22
        if settled and b > 14:
            amp *= 0.12                         # the tail the rule no longer listens to
        tone = np.sin(2 * np.pi * freq(b) * t) + 0.18 * np.sin(4 * np.pi * freq(b) * t)
        if b == lb and not settled:
            tone *= 0.55 + 0.45 * np.sin(2 * np.pi * 7.0 * t)   # the bucket under the rule's ear trembles
        out[i0:i0 + phase_len] += amp * tone * env
    capped = CAPPED_FINAL + sum(c for b, c in hist.items() if b > lb)
    out[i0:i0 + phase_len] += 0.20 * np.sqrt(capped / SAMPLES) * np.sin(2 * np.pi * 55.0 * t) * env
    late = hist.get(lb, 0)
    if late >= THRESH and not settled:
        k = i0 + phase_len - int(0.06 * SR)
        n = int(0.05 * SR)
        out[k:k + n] += 0.35 * np.exp(-np.arange(n) / (0.006 * SR)) * np.sin(2 * np.pi * 2400 * np.arange(n) / SR)

out /= np.max(np.abs(out)) * 1.05
pcm = (out * 32767).astype(np.int16)
with wave.open(D + 'the-late-tail.wav', 'wb') as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes(pcm.tobytes())

# spectrogram for verification (log magnitude, 0..4 kHz), daylight palette
N, HOP = 4096, 1024
frames = [out[i:i + N] * np.hanning(N) for i in range(0, len(out) - N, HOP)]
spec = np.abs(np.fft.rfft(np.array(frames), axis=1))[:, : int(4000 * N / SR)]
img = np.log1p(spec * 40)
img = (img / img.max()).T[::-1]
rgb = (np.array([242, 237, 227]) * (1 - img[:, :, None]) + np.array([30, 40, 70]) * img[:, :, None]).astype(np.uint8)
Image.fromarray(rgb).resize((1200, 500)).save(D + 'the-late-tail-spectrogram.png')
print('seconds', len(out) / SR)
