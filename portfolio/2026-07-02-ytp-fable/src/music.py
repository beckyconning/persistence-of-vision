"""FluidSynth muzak for the YTP: clean corporate -> minor dread -> detuned wrong.

Renders MIDI via ctypes libfluidsynth + FluidR3_GM (real samples, per April's
standing preference). Each piece cached as a WAV in assets/.
"""
import ctypes
import glob
import os

import numpy as np
from midiutil import MIDIFile

FS_DIR = "/home/april/fluidsynth-local"
SF2 = os.path.join(FS_DIR, "sf2", "FluidR3_GM.sf2")
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
SR = 44100

_fl = None


def _lib():
    global _fl
    if _fl is None:
        libdir = os.path.join(FS_DIR, "lib")
        for so in sorted(glob.glob(os.path.join(libdir, "*.so*"))):
            try:
                ctypes.CDLL(so, mode=ctypes.RTLD_GLOBAL)
            except OSError:
                pass
        _fl = ctypes.CDLL(os.path.join(libdir, "libfluidsynth.so.3"), mode=ctypes.RTLD_GLOBAL)
        for fn in ("new_fluid_settings", "new_fluid_synth", "new_fluid_player"):
            getattr(_fl, fn).restype = ctypes.c_void_p
    return _fl


def render_midi(mid_path, tail_s=3.5):
    fl = _lib()
    st = fl.new_fluid_settings()
    fl.fluid_settings_setnum(ctypes.c_void_p(st), b"synth.sample-rate", ctypes.c_double(SR))
    fl.fluid_settings_setnum(ctypes.c_void_p(st), b"synth.gain", ctypes.c_double(0.6))
    syn = fl.new_fluid_synth(ctypes.c_void_p(st))
    fl.fluid_synth_sfload(ctypes.c_void_p(syn), SF2.encode(), 1)
    pl = fl.new_fluid_player(ctypes.c_void_p(syn))
    fl.fluid_player_add(ctypes.c_void_p(pl), mid_path.encode())
    fl.fluid_player_play(ctypes.c_void_p(pl))

    chunks = []
    buf = (ctypes.c_int16 * (1024 * 2))()
    while fl.fluid_player_get_status(ctypes.c_void_p(pl)) == 1:
        fl.fluid_synth_write_s16(ctypes.c_void_p(syn), 1024, buf, 0, 2, buf, 1, 2)
        chunks.append(np.frombuffer(buf, dtype=np.int16).copy())
    for _ in range(int(tail_s * SR / 1024)):
        fl.fluid_synth_write_s16(ctypes.c_void_p(syn), 1024, buf, 0, 2, buf, 1, 2)
        chunks.append(np.frombuffer(buf, dtype=np.int16).copy())

    fl.delete_fluid_player(ctypes.c_void_p(pl))
    fl.delete_fluid_synth(ctypes.c_void_p(syn))
    fl.delete_fluid_settings(ctypes.c_void_p(st))
    audio = np.concatenate(chunks).astype(np.float32) / 32768.0
    return audio.reshape(-1, 2).mean(axis=1)  # mono


def _cached(name, build):
    """build(mid_path) writes a MIDI; returns rendered mono float32."""
    wav = os.path.join(ASSETS, name + ".npy")
    if os.path.exists(wav):
        return np.load(wav)
    mid = os.path.join(ASSETS, name + ".mid")
    build(mid)
    audio = render_midi(mid)
    np.save(wav, audio)
    return audio


# GM: 4=EPiano1 12=Marimba 33=FingerBass 48=Strings 14=TubularBells 61=Brass
EP, MAR, BASS, STR, BELL, BRASS = 4, 12, 33, 48, 14, 61
HAT, KICK, SNARE = 42, 36, 40  # ch9 percussion keys


def muzak_clean():
    """Chirpy hold-music. C-G-Am-F, EP + marimba + bass + hats, 104bpm, 8 bars."""
    def build(path):
        m = MIDIFile(4)
        for tr, prog, ch in ((0, EP, 0), (1, MAR, 1), (2, BASS, 2)):
            m.addTempo(tr, 0, 104)
            m.addProgramChange(tr, ch, 0, prog)
        m.addTempo(3, 0, 104)
        chords = [(48, [60, 64, 67]), (43, [59, 62, 67]), (45, [60, 64, 69]), (41, [60, 65, 69])]
        for bar in range(8):
            root, notes = chords[bar % 4]
            t0 = bar * 4
            for b in (0, 2):  # EP comp on 1 and 3
                for n in notes:
                    m.addNote(0, 0, n, t0 + b, 1.6, 52)
            arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 12] * 2
            for i, n in enumerate(arp):  # marimba 8ths
                m.addNote(1, 1, n, t0 + i * 0.5, 0.45, 58)
            m.addNote(2, 2, root, t0, 1.8, 62)
            m.addNote(2, 2, root + 7, t0 + 2, 1.8, 55)
            for i in range(8):
                m.addNote(3, 9, HAT, t0 + i * 0.5, 0.3, 30 if i % 2 else 40)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("muzak_clean", build)


def muzak_minor():
    """The same tune gone cold: Am-Em-F-Dm, slower, strings, no hats."""
    def build(path):
        m = MIDIFile(3)
        for tr, prog, ch in ((0, EP, 0), (1, STR, 1), (2, BASS, 2)):
            m.addTempo(tr, 0, 76)
            m.addProgramChange(tr, ch, 0, prog)
        chords = [(45, [57, 60, 64]), (40, [55, 59, 64]), (41, [57, 60, 65]), (38, [53, 57, 62])]
        for bar in range(8):
            root, notes = chords[bar % 4]
            t0 = bar * 4
            for n in notes:
                m.addNote(0, 0, n, t0, 3.6, 44)
                m.addNote(1, 1, n + 12, t0, 4.0, 30)
            m.addNote(2, 2, root - 12, t0, 3.8, 56)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("muzak_minor", build)


def muzak_wrong():
    """The clean tune, but wrong: detune drift + sour notes + a hiccup."""
    def build(path):
        m = MIDIFile(4)
        for tr, prog, ch in ((0, EP, 0), (1, MAR, 1), (2, BASS, 2)):
            m.addTempo(tr, 0, 96)
            m.addProgramChange(tr, ch, 0, prog)
        m.addTempo(3, 0, 96)
        chords = [(48, [60, 64, 67]), (43, [59, 62, 66]),  # G with F# -> sour
                  (45, [60, 63, 69]), (41, [61, 65, 69])]  # Am w/ Eb, F w/ Db
        for bar in range(6):
            root, notes = chords[bar % 4]
            t0 = bar * 4
            # pitch wheel drifts progressively flat
            m.addPitchWheelEvent(0, 0, t0, -int(300 * bar))
            m.addPitchWheelEvent(1, 1, t0, int(200 * bar))
            for b in (0, 2):
                for n in notes:
                    m.addNote(0, 0, n, t0 + b, 1.6, 52)
            arp = [notes[0] + 12, notes[1] + 12, notes[2] + 12, notes[1] + 13] * 2
            for i, n in enumerate(arp):
                m.addNote(1, 1, n, t0 + i * 0.5, 0.45, 58)
            m.addNote(2, 2, root, t0, 1.8, 62)
            for i in range(8):
                m.addNote(3, 9, HAT, t0 + i * 0.5, 0.3, 30 if i % 2 else 40)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("muzak_wrong", build)


def sting_bell():
    def build(path):
        m = MIDIFile(1)
        m.addTempo(0, 0, 120)
        m.addProgramChange(0, 0, 0, BELL)
        m.addNote(0, 0, 84, 0, 2, 100)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("sting_bell", build)


def sting_brass():
    """The airhorn-adjacent cluster blast."""
    def build(path):
        m = MIDIFile(1)
        m.addTempo(0, 0, 120)
        m.addProgramChange(0, 0, 0, BRASS)
        for n in (70, 72, 74, 78):
            m.addNote(0, 0, n, 0, 1.2, 127)
            m.addNote(0, 0, n, 0.05, 1.2, 127)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("sting_brass", build)


def sting_violin():
    def build(path):
        m = MIDIFile(1)
        m.addTempo(0, 0, 120)
        m.addProgramChange(0, 0, 0, 40)
        m.addNote(0, 0, 95, 0, 1.5, 110)
        m.addNote(0, 0, 94, 0.12, 1.4, 100)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("sting_violin", build)


def sting_klaxon():
    """Low brass stabs, repeated — the DON'T PICK 300s klaxon."""
    def build(path):
        m = MIDIFile(1)
        m.addTempo(0, 0, 140)
        m.addProgramChange(0, 0, 0, BRASS)
        for i in range(4):
            for n in (46, 47, 53):
                m.addNote(0, 0, n, i * 1.0, 0.6, 127)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("sting_klaxon", build)


def sting_timpani():
    def build(path):
        m = MIDIFile(1)
        m.addTempo(0, 0, 120)
        m.addProgramChange(0, 0, 0, 47)
        m.addNote(0, 0, 43, 0, 2, 115)
        m.addNote(0, 0, 36, 0.5, 2.5, 120)
        with open(path, "wb") as f:
            m.writeFile(f)
    return _cached("sting_timpani", build)
