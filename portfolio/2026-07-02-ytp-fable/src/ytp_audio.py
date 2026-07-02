"""YTP audio toolkit: piper TTS + numpy mangling + a mixing timeline.

Everything is float32 mono @ 44100 until final stereo export.
"""
import hashlib
import json
import os
import wave

import numpy as np

SR = 44100
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
CACHE = os.path.join(ASSETS, "tts_cache")
os.makedirs(CACHE, exist_ok=True)

_voice = None


def _load_voice():
    global _voice
    if _voice is None:
        from piper import PiperVoice
        _voice = PiperVoice.load(os.path.join(ASSETS, "en_US-lessac-medium.onnx"))
    return _voice


def _read_wav_mono(path):
    with wave.open(path, "rb") as w:
        sr = w.getframerate()
        n = w.getnframes()
        raw = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
        if w.getnchannels() == 2:
            raw = raw.reshape(-1, 2).mean(axis=1)
    if sr != SR:
        raw = resample_to(raw, sr, SR)
    return raw


def resample_to(x, sr_from, sr_to):
    n_out = int(round(len(x) * sr_to / sr_from))
    return np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x).astype(np.float32)


def say(text, length_scale=1.0):
    """TTS a line (cached). length_scale >1 = slower speech."""
    key = hashlib.md5(f"{text}|{length_scale}".encode()).hexdigest()[:16]
    path = os.path.join(CACHE, key + ".wav")
    if not os.path.exists(path):
        from piper import SynthesisConfig
        v = _load_voice()
        cfg = SynthesisConfig(length_scale=length_scale)
        with wave.open(path, "wb") as w:
            v.synthesize_wav(text, w, syn_config=cfg)
    return _read_wav_mono(path)


# ---------------- effects ----------------

def gain(x, db):
    return (x * (10 ** (db / 20))).astype(np.float32)


def pitch(x, semitones):
    """Resample pitch shift — changes duration too (the YTP way)."""
    factor = 2 ** (semitones / 12)
    n_out = int(len(x) / factor)
    return np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x).astype(np.float32)


def speed(x, factor):
    n_out = int(len(x) / factor)
    return np.interp(np.linspace(0, len(x) - 1, n_out), np.arange(len(x)), x).astype(np.float32)


def reverse(x):
    return x[::-1].copy()


def stutter(x, ms=90, repeats=3):
    """Repeat the opening chunk: s-s-s-sentence."""
    n = int(SR * ms / 1000)
    chunk = x[:n]
    out = [fade(chunk.copy(), out_ms=8) for _ in range(repeats)] + [x]
    return np.concatenate(out)


def chop(x, start_s, end_s):
    return x[int(start_s * SR):int(end_s * SR)].copy()


def bitcrush(x, bits=5, rate_div=6):
    q = 2 ** (bits - 1)
    y = np.round(x * q) / q
    y = np.repeat(y[::rate_div], rate_div)[: len(x)]
    if len(y) < len(x):
        y = np.pad(y, (0, len(x) - len(y)))
    return y.astype(np.float32)


def distort(x, drive=8.0):
    return np.tanh(x * drive).astype(np.float32) * 0.85


def echo(x, delay_ms=260, feedback=0.45, mix=0.5, tail_s=1.6):
    d = int(SR * delay_ms / 1000)
    out = np.zeros(len(x) + int(tail_s * SR), dtype=np.float32)
    out[: len(x)] = x
    buf = out.copy()
    amp = feedback
    pos = d
    while amp > 0.02 and pos < len(out):
        seg = buf[: len(out) - pos]
        out[pos: pos + len(seg)] += seg * amp * mix
        amp *= feedback
        pos += d
    return out


def lowpass(x, alpha=0.06):
    y = np.empty_like(x)
    acc = 0.0
    for i in range(len(x)):
        acc += alpha * (x[i] - acc)
        y[i] = acc
    return y


def lowpass_fast(x, alpha=0.06):
    # one-pole via lfilter-style vectorization using cumulative trick is messy;
    # do it with a strided pure-numpy IIR approximation: FFT brickwall instead.
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    cutoff = alpha * SR / (2 * np.pi)
    X[freqs > cutoff] *= np.exp(-(freqs[freqs > cutoff] - cutoff) / (cutoff * 0.5 + 1))
    return np.fft.irfft(X, len(x)).astype(np.float32)


def telephone(x):
    X = np.fft.rfft(x)
    freqs = np.fft.rfftfreq(len(x), 1 / SR)
    band = ((freqs > 350) & (freqs < 3200)).astype(np.float32)
    return np.fft.irfft(X * band, len(x)).astype(np.float32) * 1.4


def fade(x, in_ms=0, out_ms=0):
    if in_ms:
        n = min(len(x), int(SR * in_ms / 1000))
        x[:n] *= np.linspace(0, 1, n).astype(np.float32)
    if out_ms:
        n = min(len(x), int(SR * out_ms / 1000))
        x[-n:] *= np.linspace(1, 0, n).astype(np.float32)
    return x


def thump(dur=0.16, f=55.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    x = np.sin(2 * np.pi * f * t) * np.exp(-t * 26)
    return distort(x.astype(np.float32), 2.5)


def bass_drop(dur=1.6, f0=180.0, f1=28.0):
    t = np.linspace(0, dur, int(SR * dur), endpoint=False)
    f = f0 * (f1 / f0) ** (t / dur)
    ph = 2 * np.pi * np.cumsum(f) / SR
    x = np.sin(ph) * np.linspace(1, 0.6, len(t))
    return distort(x.astype(np.float32), 3.0)


def silence(dur):
    return np.zeros(int(SR * dur), dtype=np.float32)


def accelerating_loop(x, n=9, start_factor=1.0, growth=1.22, gap_ms=70, gap_shrink=0.8):
    """The classic YTP speeding-up repeat. Returns concatenated, ever-faster copies."""
    out = []
    f = start_factor
    gap = gap_ms
    for _ in range(n):
        out.append(speed(x, f))
        out.append(silence(gap / 1000))
        f *= growth
        gap *= gap_shrink
    return np.concatenate(out)


# ---------------- timeline ----------------

class Timeline:
    def __init__(self):
        self.tracks = []  # (t_start, samples, db)
        self.events = []

    def add(self, t, x, db=0.0, event=None, **meta):
        self.tracks.append((t, x if db == 0 else gain(x, db)))
        if event:
            self.events.append({"t": round(t, 3), "dur": round(len(x) / SR, 3),
                                "kind": event, **meta})
        return t + len(x) / SR

    def mark(self, t, kind, dur=0.0, **meta):
        self.events.append({"t": round(t, 3), "dur": round(dur, 3), "kind": kind, **meta})

    def mix(self, total_s=None):
        end = max((t + len(x) / SR) for t, x in self.tracks)
        if total_s:
            end = max(end, total_s)
        out = np.zeros(int(SR * end) + 1, dtype=np.float32)
        for t, x in self.tracks:
            i = int(t * SR)
            out[i: i + len(x)] += x
        peak = np.abs(out).max()
        if peak > 0.97:
            out = np.tanh(out / peak * 1.6) * 0.72  # gentle master saturation
            peak = np.abs(out).max()
        if peak > 0.01:
            out *= 0.88 / peak  # normalize master
        return out

    def save(self, path_wav, path_json, total_s=None):
        mono = self.mix(total_s)
        st = np.stack([mono, mono], axis=1)
        pcm = (np.clip(st, -1, 1) * 32767).astype(np.int16)
        with wave.open(path_wav, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(SR)
            w.writeframes(pcm.tobytes())
        self.events.sort(key=lambda e: e["t"])
        with open(path_json, "w") as f:
            json.dump({"sr": SR, "dur": len(mono) / SR, "events": self.events}, f, indent=1)
        return len(mono) / SR
