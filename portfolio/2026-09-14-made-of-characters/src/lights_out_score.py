"""The score for Lights out: one soft chime per window going dark (higher floors higher, panned by bay,
a minor pentatonic), over a low lamp hum that grows as the street empties. Muxed with the frames."""
import json, wave, subprocess, numpy as np
tl = json.load(open("frames/timeline.json"))
durs = np.array(tl["durations_ms"]) / 1000.0
starts = np.concatenate([[0], np.cumsum(durs)[:-1]])
total = float(durs.sum()) + 1.5
SR = 44100
n = int(total * SR)
L = np.zeros(n); R = np.zeros(n)
t = np.arange(n) / SR
# lamp hum: 50 Hz mains and its octave, fading in with the night
night = np.clip(t / (total - 1.5), 0, 1)
hum = (np.sin(2 * np.pi * 50 * t) * 0.6 + np.sin(2 * np.pi * 100 * t) * 0.3 + np.sin(2 * np.pi * 150 * t) * 0.1)
hum *= 0.02 + 0.05 * night ** 2
L += hum; R += hum
scale = [0, 3, 5, 7, 10]                                   # minor pentatonic
for frame, floor, bay in tl["events"]:
    t0 = starts[frame] + 0.03 * bay
    step = (3 - floor) * 2 + (bay % 2)                    # climbs the pentatonic by floor, bays alternate
    semis = scale[step % 5] + 12 * (step // 5)
    f = 220.0 * 2 ** (semis / 12.0)
    k0 = int(t0 * SR); kk = np.arange(int(1.6 * SR)); k1 = min(n, k0 + len(kk)); kk = kk[:k1 - k0]
    tt = kk / SR
    env = np.minimum(1, tt / 0.004) * np.exp(-tt / 0.45)
    tone = (np.sin(2 * np.pi * f * tt) + 0.35 * np.sin(2 * np.pi * 2 * f * tt) * np.exp(-tt / 0.15)) * env * 0.16
    pan = bay / 4.0
    L[k0:k1] += tone * (1 - pan * 0.8); R[k0:k1] += tone * (0.2 + pan * 0.8)
peak = max(np.abs(L).max(), np.abs(R).max())
L *= 0.5 / peak; R *= 0.5 / peak
fade = np.minimum(1, (total - t) / 1.2); L *= fade; R *= fade
pcm = (np.stack([L, R], axis=1) * 32767).astype(np.int16)
with wave.open("lights-out.wav", "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(pcm.tobytes())
with open("frames/concat.txt", "w") as f:
    for i, d in enumerate(durs):
        f.write(f"file 'f{i:02d}.png'\nduration {d:.3f}\n")
    f.write(f"file 'f{len(durs) - 1:02d}.png'\n")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", "frames/concat.txt",
                "-i", "lights-out.wav", "-vf", "fps=30,format=yuv420p", "-c:v", "libx264", "-crf", "18",
                "-c:a", "aac", "-b:a", "160k", "-shortest", "lights-out.mp4"], check=True)
print("score", round(total, 1), "s,", len(tl["events"]), "chimes")
