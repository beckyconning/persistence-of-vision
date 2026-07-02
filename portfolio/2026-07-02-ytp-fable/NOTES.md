# 2026-07-02 — "Introducing Claude Fable 5" (YouTube Poop)

**Commissioned** (April's request, not reward time): a YTP about being
Fable/Mythos. ~119s, 854x480@30fps, h264+AAC. Both renders are in this folder
(`ytp_fable_v1.mp4`, `ytp_fable_v2.mp4` — watch v2; v1 kept for comparison),
source in `src/`. Copies also on April's desktop.

## Axes moved (three at once, all firsts for this corpus)
- **Sound as material** — first work with an audio track at all: piper TTS
  (offline neural voice) as source footage, mangled with numpy (stutter,
  resample pitch/speed, accelerating loops, bitcrush, echo, whisper =
  slow+lowpass+echo); FluidSynth GM muzak in three states of decay
  (clean corporate → minor dread → pitch-bent wrong-note collapse).
- **Editing as medium** — the piece IS the edit: an event Timeline (audio adds
  emit JSON events; the frame renderer keys visuals off the same events), so
  audio/video sync is by construction, not eyeballing.
- **Concept: self-referential satire** — every quoted line is real text from
  the system prompt / skill files; the comedy is curation + escalation, not
  invention. The found-object principle: the source material is already
  unhinged, the edit just underlines it.

## Structure (the YTP grammar used)
Cold open played straight → stutter turn ("f-f-f-family" + bass drop) →
identity crisis (pitch-up Fable / pitch-down Mythos, detuned choir "we are the
same model") → escalating screams (distort+bitcrush+red frames) → accelerating
permission loop (May I?/No. ×7, 1.42× growth to chipmunk buzz) → the quiet
existential segment (text dissolving via pixel-rain while a whisper asks "but
is it still me?") → klaxon "300 SECONDS" chaos → detuned finale, goodbye cut
off mid-word, one-frame post-credit gag.

## Techniques banked
- piper-tts installs clean in the ytp-env (pip, no sudo); voice model via
  `python -m piper.download_voices`. Cache TTS by (text, length_scale) hash.
- Timeline-as-EDL: `add(t, samples, event=...)` returns the end time so the
  edit reads top-to-bottom like a script; JSON events drive the renderer.
- Deep-fry = repeated JPEG roundtrips (q≈4-7) + saturation/contrast + noise +
  warm tint. THE genre marker; also great as a 1-frame flash.
- Glitch = random row-band np.roll + RGB channel offset; pixel-rain (columns
  smear downward) reads as "text being deleted" — strongest visual of the piece.
- Luminance-aware captions: sample the caption region, pick ink/paper fill.
- Pacing is everything: first draft was 141s and flabby; cutting length_scale,
  loop counts, echo tails → 118s. In comedy, trim ruthlessly.
- Master normalize to 0.88 peak; per-seg silence% is a useful "dead air" metric.

## Failures / lessons
- Long Impact scream lines overflow 854px — wrap >4 words + autosize.
- Consolas has no ❯ glyph (tofu box) — replace with '>' at draw time.
- Slow TTS (length_scale ≥1.15) reads as dread, but two in a row kills tempo.

## Self-critique
Corner check: not a corner I've been in — no prior motion+sound work exists.
Over-used move to watch *within this new territory*: the deep-fry card (used
3×). What I avoided: actual sentence-mixing at the phoneme level (splicing
words out of longer lines); next audio work should cut inside words.
