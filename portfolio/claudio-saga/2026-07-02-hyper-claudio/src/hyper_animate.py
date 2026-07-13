"""Animate + render the hyper-realistic Claudio lipsync. 24fps, 640x360 -> 854x480."""
import json
import os
import subprocess

import numpy as np
from PIL import Image

import hyper

FPS = 24
RW, RH = 640, 360
OW, OH = 854, 480
HERE = os.path.dirname(os.path.abspath(__file__))
FFMPEG = "/home/april/ytp-env/lib/python3.12/site-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2"

# viseme mini-tracks: fraction-of-word -> (jaw, width, pucker)
VISEMES = {
    "Thanks": [(0.0, .12, .2, 0), (0.25, .52, .35, 0), (0.7, .35, .3, 0), (1.0, .15, .1, 0)],
    "a": [(0.0, .15, 0, 0), (0.4, .32, 0, 0), (1.0, .1, 0, 0)],
    "so": [(0.0, .15, 0, .3), (0.4, .26, -.1, .6), (1.0, .15, 0, .2)],
    "much": [(0.0, .35, 0, .1), (0.5, .45, .1, 0), (0.85, .05, 0, 0), (1.0, .02, 0, 0)],
    "for": [(0.0, .2, 0, .5), (0.5, .3, -.1, .55), (1.0, .15, 0, .2)],
    "to": [(0.0, .1, 0, .5), (0.4, .28, 0, .68), (1.0, .12, 0, .25)],
    "playing": [(0.0, .02, 0, .2), (0.15, .52, .4, 0), (0.55, .42, .5, 0),
                (0.8, .25, .3, 0), (1.0, .15, .2, 0)],
    "my": [(0.0, .02, 0, 0), (0.3, .5, .3, 0), (1.0, .25, .2, 0)],
    "game.": [(0.0, .25, .1, 0), (0.35, .52, .3, 0), (0.75, .1, 0, 0), (1.0, .02, 0, 0)],
}
BLINKS = [0.7, 4.15, 6.25]      # full blinks
WINK_T = 6.85                   # right-eye wink
BROW_HITS = [1.5, 3.9, 5.01]    # raise on stressed words


def key_interp(keys, f):
    for (f0, *v0), (f1, *v1) in zip(keys, keys[1:]):
        if f0 <= f <= f1:
            k = (f - f0) / max(f1 - f0, 1e-6)
            return [a + (b - a) * k for a, b in zip(v0, v1)]
    return list(keys[-1][1:]) if f > keys[-1][0] else list(keys[0][1:])


def build_tracks():
    data = json.load(open(os.path.join(HERE, "out", "hyper_timings.json")))
    total = data["total"]
    rms = np.array(data["rms24"])
    n = int(total * FPS)
    jaw = np.full(n, 0.06)
    width = np.zeros(n)
    pucker = np.zeros(n)
    for tm in data["timings"]:
        w = tm["word"]
        keys = VISEMES.get(w, VISEMES["a"])
        i0 = int(tm["t"] * FPS)
        i1 = int((tm["t"] + tm["dur"]) * FPS) + 1
        for i in range(i0, min(i1, n)):
            f = (i / FPS - tm["t"]) / tm["dur"]
            j, wd, pk = key_interp(keys, np.clip(f, 0, 1))
            jaw[i] = j
            width[i] = wd
            pucker[i] = pk
    # jaw rides the true loudness envelope
    rr = np.pad(rms, (0, max(0, n - len(rms))))[:n]
    jaw = jaw * (0.55 + 0.45 * rr / (rr.max() + 1e-9))
    kern = np.array([0.2, 0.6, 0.2])
    for tr in (jaw, width, pucker):
        tr[:] = np.convolve(tr, kern, mode="same")
    # end smile
    smile_i = int(6.3 * FPS)
    width[smile_i:] = np.maximum(width[smile_i:], np.linspace(0, 0.38, n - smile_i))
    jaw[smile_i:] = np.maximum(jaw[smile_i:], 0.05)
    return total, n, jaw, width, pucker, rr


def blink_val(t, centers, dur=0.22):
    v = 0.0
    for c in centers:
        if abs(t - c) < dur / 2:
            v = max(v, 1 - abs(t - c) / (dur / 2))
    return v


def prm_at(t, fi, tracks):
    total, n, jaw, width, pucker, rr = tracks
    i = min(fi, n - 1)
    bl = blink_val(t, BLINKS)
    wink = 1.0 if WINK_T < t < WINK_T + 0.55 else blink_val(t, [WINK_T - 0.06], 0.24)
    brow = 0.0
    for bh in BROW_HITS:
        if bh - 0.1 < t < bh + 0.45:
            brow = max(brow, np.sin((t - bh + 0.1) / 0.55 * np.pi) * 0.9)
    if t > 6.4:
        brow = max(brow, 0.5)
    # head: nods into the loudness, gentle drift
    lp = rr[max(0, i - 3):i + 1].mean() if i > 0 else 0
    return {
        "jaw": float(jaw[i]), "width": float(width[i]), "pucker": float(pucker[i]),
        "blink": float(bl), "blinkR": float(max(bl, wink)), "blinkL": float(bl),
        "browup": float(brow),
        "headrx": float(-0.045 * lp + 0.012 * np.sin(t * 0.9)),
        "headry": float(0.05 * np.sin(t * 0.43) + 0.018 * np.sin(t * 1.31)),
        "eyex": float(0.05 + (-0.2 if 3.1 < t < 3.5 else 0)),
        "eyey": 0.02,
    }


def cam_at(t, total):
    p = t / total
    wob = np.array([0.020 * np.sin(t * 1.7) + 0.012 * np.sin(t * 3.1),
                    0.014 * np.sin(t * 2.3 + 1) + 0.008 * np.sin(t * 4.7),
                    0.05 * np.sin(t * 0.9)])
    pos = np.array([0.22 - 0.16 * p, -0.26, -13.0 + 1.5 * p]) + wob
    tgt = np.array([0.0, -0.30, 0.0]) + wob * 0.4
    return tuple(pos), tuple(tgt), 35.0, float(-pos[2] - 1.55)


def main(out_name="hyper_silent.mp4", stride=1):
    tracks = build_tracks()
    total, n = tracks[0], tracks[1]
    out_path = os.path.join(HERE, "out", out_name)
    log = open(os.path.join(HERE, "out", "ffmpeg_hyper.log"), "w")
    cmd = [FFMPEG, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{OW}x{OH}",
           "-r", str(FPS // stride if stride > 1 else FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=log)
    for fi in range(0, n, stride):
        t = fi / FPS
        prm = prm_at(t, fi, tracks)
        cp, ct, fov, focus = cam_at(t, total)
        img, depth = hyper.render_frame(prm, W=RW, H=RH, cam_pos=cp, cam_tgt=ct,
                                        fov=fov, focus=focus)
        out = hyper.post(img, depth, focus=focus, grain_seed=fi)
        up = np.asarray(Image.fromarray(out).resize((OW, OH), Image.LANCZOS))
        proc.stdin.write(np.ascontiguousarray(up, dtype=np.uint8).tobytes())
        if fi % 24 == 0:
            print(f"frame {fi}/{n} ({t:.1f}s)", flush=True)
    proc.stdin.close()
    proc.wait()
    log.close()
    print("done:", out_path)


if __name__ == "__main__":
    import sys
    main(*(sys.argv[1:] or []))
