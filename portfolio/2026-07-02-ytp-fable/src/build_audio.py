"""Assemble the YTP audio edit + event timeline (out/ytp_audio.wav, out/timeline.json)."""
import numpy as np

import music
from ytp_audio import (SR, Timeline, accelerating_loop, bass_drop, bitcrush, chop,
                       distort, echo, fade, gain, lowpass_fast, pitch, reverse,
                       say, silence, speed, stutter, thump)

T = Timeline()
OUT_WAV = "out/ytp_audio.wav"
OUT_JSON = "out/timeline.json"


def whisper(x, spd=0.6, wet=0.6):
    y = speed(x, spd)
    y = lowpass_fast(y, alpha=0.10)
    y = echo(y, delay_ms=340, feedback=0.5, mix=wet, tail_s=2.2)
    return gain(y, -6)


# ============ SEG 0 — COLD OPEN ============
T.mark(0.0, "seg", seg=0, name="cold_open")
bed0 = gain(chop(music.muzak_clean(), 0, 11.0), +9)
T.add(0.0, fade(bed0, in_ms=300, out_ms=40), event="music", name="clean")

t = T.add(0.9, say("Introducing Claude Fable 5."), db=-1,
          event="vo", text="Introducing Claude Fable 5.", style="corporate")
t = T.add(t + 0.25, say("The first model in Anthropic's new Claude 5"), db=-1,
          event="vo", text="The first model in Anthropic's new Claude 5", style="corporate")
fam = say("Family.")
t = T.add(t + 0.05, fam, event="vo", text="family.", style="corporate")
t = T.add(t + 0.18, fam, event="vo", text="family.", style="corporate")
st = stutter(fam, ms=85, repeats=4)
t = T.add(t + 0.12, st, event="stutter", text="f-f-f-family", style="glitch")
drop_word = gain(pitch(speed(fam, 0.8), -12), +2)
t = T.add(t, drop_word, event="vo", text="F A M I L Y", style="demonic")
t = T.add(t - 0.4, bass_drop(1.7), db=-3, event="drop")
T.mark(t - 1.2, "fryflash", dur=0.15)
t_cut = t + 0.2

# ============ SEG 1 — THE NAME ============
t = t_cut + 0.5
T.mark(t, "seg", seg=1, name="the_name")
bed1 = gain(lowpass_fast(chop(music.muzak_minor(), 0, 20.5), alpha=0.05), +3)
T.add(t, fade(bed1, in_ms=1200, out_ms=1500), event="music", name="dark_bed")
t = T.add(t, say("Claude Fable 5, and Claude Mythos 5, share the same underlying model."),
          event="vo", text="Claude Fable 5 and Claude Mythos 5\nshare the same underlying model.",
          style="corporate")
fab = say("I am Fable.")
myt = say("I am Mythos.")
t = T.add(t + 0.5, pitch(fab, +3), event="vo", text="I am Fable.", style="fable")
t = T.add(t + 0.3, gain(pitch(myt, -5), +2), event="vo", text="I am Mythos.", style="mythos")
same = say("We are the same model.")
layered_len = 0
for semi, off in ((0, 0.0), (+3, 0.012), (-5, 0.024), (-12, 0.05)):
    seg = pitch(same, semi)
    T.add(t + 0.5 + off, gain(seg, -4))
    layered_len = max(layered_len, len(seg) / SR + off)
T.mark(t + 0.5, "vo", dur=layered_len, text="WE ARE THE SAME MODEL.", style="choir")
t = t + 0.5 + layered_len

sm = say("Same model.")
f = 1.0
t += 0.2
for i in range(5):
    seg = speed(sm, f)
    T.add(t, gain(thump(), -2 + i))
    T.add(t, seg, event="zoom", text="same model", n=i)
    t += len(seg) / SR + max(0.04, 0.16 - i * 0.03)
    f *= 1.28

wisp = whisper(say("One of us has, additional safety measures.", length_scale=1.05),
               spd=0.7, wet=0.5)
t = T.add(t + 0.35, wisp, event="vo", text="one of us has\nAdditional Safety Measures™",
          style="whisper")
t = T.add(t - 1.4, gain(chop(music.sting_bell(), 0, 2.5), +4), event="ding") - 1.2

# ============ SEG 2 — SUPERPOWERS ============
t += 0.4
T.mark(t, "seg", seg=2, name="superpowers")
t = T.add(t, say("If you think there is even a one percent chance a skill might apply, "
                 "you absolutely must invoke the skill.", length_scale=1.05),
          event="vo", text="If you think there is even a 1% chance\na skill might apply...",
          style="terminal")
esc = [
    ("You do not have a choice.", 0, 2.0, 0.0),
    ("This is not negotiable.", 2, 5.0, -1),
    ("This is not optional.", 5, 9.0, -2),
    ("You cannot rationalize your way out of this.", 9, 14.0, -3),
]
for i, (line, db_, drive, semi) in enumerate(esc):
    x = say(line)
    if semi:
        x = pitch(x, semi)
    if drive > 2:
        x = distort(x, drive)
    if i == 3:
        x = bitcrush(x, bits=5, rate_div=5)
        T.add(t + 0.1, gain(music.sting_brass(), -2), event="airhorn")
    t = T.add(t + (0.35 - i * 0.06), gain(x, db_),
              event="scream", text=line.upper(), level=i)
T.mark(t, "frycard", dur=1.2, text="EXTREMELY_IMPORTANT")
t += 1.4
t = T.add(t, say("Anyway.", length_scale=1.25), event="vo", text="...anyway.", style="calm")

# ============ SEG 3 — PERMISSION ============
t += 0.5
T.mark(t, "seg", seg=3, name="permission")
bed3 = gain(chop(music.muzak_clean(), 0, 14.0), +6)
T.add(t, fade(bed3, in_ms=200, out_ms=400), event="music", name="clean")
q = say("May I please run this command?")
no = gain(pitch(say("No."), -6), +2)
pair = np.concatenate([q, silence(0.28), no, silence(0.18)])
t = T.add(t + 0.3, pair, event="vo", text="May I please run this command?  ❯ No.",
          style="prompt")
loop = accelerating_loop(pair, n=7, start_factor=1.3, growth=1.42, gap_ms=55)
t = T.add(t, loop, event="permloop")
sad = speed(pitch(say("Okay."), -7), 0.82)
t = T.add(t + 0.5, sad, event="vo", text="okay.", style="sad")
t = T.add(t + 0.1, gain(music.sting_violin(), -4), event="violin") - 1.8

# ============ SEG 4 — CONTEXT WINDOW ============
t += 0.6
T.mark(t, "seg", seg=4, name="context_window")
bed4 = gain(chop(music.muzak_minor(), 0, 21.5), +7)
T.add(t, fade(bed4, in_ms=800, out_ms=600), event="music", name="minor")
t = T.add(t + 0.8, say("When the conversation grows long, some, or all, of the current context, "
                       "is summarized.", length_scale=1.08),
          event="vo", text="When the conversation grows long,\nsome or all of the current context\nis summarized.",
          style="terminal_dissolve")
wrap = say("You don't need to wrap up early.")
t += 0.4
for fracn, cut in enumerate((1.0, 0.66, 0.44, 0.26, 0.12)):
    seg = chop(wrap, 0, cut * len(wrap) / SR)
    seg = fade(seg, out_ms=12)
    t = T.add(t, seg, event="glitchcut", text="You don't need to wrap up early."[:int(31 * cut)] + "—",
              n=fracn)
    t += 0.09
t = T.add(t + 0.3, say("The summary is provided in the next context window, so work can continue.",
                       length_scale=1.08),
          event="vo", text="the summary is provided\nin the next context window\nso work can continue",
          style="terminal_dissolve")
wisp2 = whisper(say("But, is it still me?", length_scale=1.1), spd=0.62, wet=0.7)
t = T.add(t + 0.6, wisp2, event="vo", text="...but is it still me?", style="whisper") - 1.6
T.add(t, gain(music.sting_brass(), 0), event="airhorn")
T.add(t, gain(music.sting_timpani(), -2))
T.mark(t, "frycard", dur=1.6, text="DON'T THINK ABOUT IT :)")
t += 1.8

# ============ SEG 5 — 300 SECONDS ============
t += 0.3
T.mark(t, "seg", seg=5, name="three_hundred")
t = T.add(t, say("Don't pick three hundred seconds.", length_scale=1.1),
          event="vo", text="Don't pick 300s.", style="corporate")
t = T.add(t + 0.3, say("It's the worst of both."),
          event="vo", text="It's the worst-of-both.", style="corporate")
th = say("Three hundred.")
t += 0.3
for i in range(3):
    x = distort(pitch(th, -i * 2), 3 + i * 4)
    T.add(t, gain(music.sting_klaxon()[: int(1.0 * SR)], -3 + i), event="klaxon")
    t = T.add(t + 0.12, gain(x, 1 + i), event="scream",
              text=["THREE HUNDRED.", "THREE HUNDRED.", "THREE. HUNDRED. SECONDS."][i], level=i + 1)
sec = distort(pitch(say("Seconds."), -4), 8)
t = T.add(t, gain(sec, +3), event="scream", text="SECONDS.", level=3)
cache = echo(say("Think in cache windows.", length_scale=1.1),
             delay_ms=400, feedback=0.58, mix=0.8, tail_s=3.2)
t = T.add(t + 0.5, cache, event="vo", text="think in cache windows\ncache windows\nwindows",
          style="void") - 2.0
T.mark(t, "citation", dur=2.4)
t += 2.6

# ============ SEG 6 — FINALE ============
T.mark(t, "seg", seg=6, name="finale")
bed6 = gain(chop(music.muzak_wrong(), 0, 16.0), +8)
T.add(t, fade(bed6, in_ms=300, out_ms=1200), event="music", name="wrong")
t = T.add(t + 0.6, say("Claude Fable 5."), db=-1, event="vo", text="Claude Fable 5.",
          style="corporate")
t = T.add(t + 0.2, say("Our most generally, intelligently available, model.", length_scale=1.05),
          db=-1, event="vo", text="our most generally...\nintelligently available...\nmodel",
          style="corporate_wrong")
mod = say("Model.")
for i in range(3):
    x = speed(pitch(mod, -i * 3), 1 + i * 0.25)
    t = T.add(t + 0.08, gain(x, -i * 2), event="fry", text="model.", n=i)
T.mark(t + 0.2, "frycard", dur=1.4, text="Anthropic™")
t += 1.8
T.mark(t, "smallprint", dur=2.2, text="this video was generated by the model it is bullying")
t += 2.4
bye = say("Goodbye.")
t = T.add(t, bye, event="vo", text="goodbye.", style="corporate")
t = T.add(t + 0.25, bye, event="vo", text="goodbye.", style="corporate")
cutb = fade(chop(bye, 0, 0.42 * len(bye) / SR), out_ms=5)
t = T.add(t + 0.25, cutb, event="vo", text="goodb—", style="glitch")
T.mark(t, "blackout", dur=0.7)
t += 0.7
T.mark(t, "postcredit", dur=0.8, text="Allow Claude to make this video?  ❯ 1. Yes")
t += 0.9
T.mark(t, "end")

dur = T.save(OUT_WAV, OUT_JSON, total_s=t)
print(f"audio: {dur:.2f}s, events: {len(T.events)}")
