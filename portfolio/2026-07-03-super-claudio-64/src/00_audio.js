// ============ AUDIO: chiptune tracker + SFX (all procedural WebAudio) ============
const AUDIO = (() => {
  let ctx = null, master = null, musicGain = null, sfxGain = null;
  let curSong = null, songTimer = null;

  function init() {
    if (ctx) return;
    ctx = new (window.AudioContext || window.webkitAudioContext)();
    master = ctx.createGain(); master.gain.value = 0.5; master.connect(ctx.destination);
    musicGain = ctx.createGain(); musicGain.gain.value = 0.55; musicGain.connect(master);
    sfxGain = ctx.createGain(); sfxGain.gain.value = 0.9; sfxGain.connect(master);
  }
  const NOTE = n => 440 * Math.pow(2, (n - 69) / 12);

  let noiseBuf = null;
  function getNoise() {
    if (!noiseBuf) {
      noiseBuf = ctx.createBuffer(1, ctx.sampleRate, ctx.sampleRate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    return noiseBuf;
  }

  // one voice: square/triangle/sine/noise with decay envelope
  function voice(when, freq, dur, type, vol, dest, opts = {}) {
    const g = ctx.createGain();
    g.connect(dest || sfxGain);
    const a = opts.attack || 0.005;
    g.gain.setValueAtTime(0, when);
    g.gain.linearRampToValueAtTime(vol, when + a);
    g.gain.setTargetAtTime(0, when + (opts.hold || dur * 0.55), (opts.rel || dur * 0.28));
    let src;
    if (type === 'noise') {
      src = ctx.createBufferSource(); src.buffer = getNoise(); src.loop = true;
      if (opts.lp) {
        const f = ctx.createBiquadFilter(); f.type = 'lowpass'; f.frequency.value = opts.lp;
        src.connect(f); f.connect(g);
      } else src.connect(g);
    } else {
      src = ctx.createOscillator();
      src.type = type || 'square';
      src.frequency.setValueAtTime(freq, when);
      if (opts.slideTo) src.frequency.exponentialRampToValueAtTime(Math.max(20, opts.slideTo), when + dur);
      if (opts.vib) {
        const lfo = ctx.createOscillator(), lg = ctx.createGain();
        lfo.frequency.value = 5.6; lg.gain.value = freq * opts.vib;
        lfo.connect(lg); lg.connect(src.frequency); lfo.start(when); lfo.stop(when + dur + 0.4);
      }
      src.connect(g);
    }
    src.start(when);
    src.stop(when + dur + 0.5);
  }

  // ---- tracker: song = {bpm, loopBeats, tracks:[{type, vol, notes:[[beat, midi, beats], ...]}], drums:[[beat, kind], ...]}
  function scheduleSong(song, t0, loopN) {
    const spb = 60 / song.bpm;
    for (const tr of song.tracks || []) {
      for (const [b, n, len] of tr.notes) {
        voice(t0 + b * spb, NOTE(n + (tr.trans || 0)), len * spb * 0.95, tr.type, tr.vol, musicGain,
          { vib: tr.vib || 0, hold: len * spb * (tr.holdF || 0.6), rel: len * spb * 0.25 });
      }
    }
    for (const [b, kind] of song.drums || []) {
      const w = t0 + b * spb;
      if (kind === 'k') voice(w, 0, 0.09, 'noise', 0.5, musicGain, { lp: 220, hold: 0.03, rel: 0.04 });
      else if (kind === 's') voice(w, 0, 0.12, 'noise', 0.34, musicGain, { lp: 2600, hold: 0.03, rel: 0.06 });
      else voice(w, 0, 0.04, 'noise', 0.14, musicGain, { lp: 9000, hold: 0.01, rel: 0.02 });
    }
  }

  function playSong(song) {
    stopSong();
    if (!ctx || !song) return;
    curSong = song;
    const spb = 60 / song.bpm, loopDur = song.loopBeats * spb;
    let next = ctx.currentTime + 0.08, n = 0;
    scheduleSong(song, next, n++);
    songTimer = setInterval(() => {
      if (!curSong) return;
      const ahead = next + loopDur - ctx.currentTime;
      if (ahead < 1.2) { next += loopDur; scheduleSong(curSong, next, n++); }
    }, 300);
  }
  function stopSong() {
    curSong = null;
    if (songTimer) { clearInterval(songTimer); songTimer = null; }
    if (musicGain) { // hard-stop by rebuilding the music bus
      musicGain.disconnect(); musicGain = ctx.createGain();
      musicGain.gain.value = 0.55; musicGain.connect(master);
    }
  }

  // ---- SFX bank ----
  const S = {};
  S.jump = () => { voice(ctx.currentTime, 300, 0.22, 'square', 0.22, sfxGain, { slideTo: 760 }); };
  S.jump2 = () => { voice(ctx.currentTime, 380, 0.24, 'square', 0.22, sfxGain, { slideTo: 980 }); };
  S.jump3 = () => { // the YAHOO arpeggio
    const t = ctx.currentTime;
    [523, 659, 784, 1046].forEach((f, i) => voice(t + i * 0.05, f, 0.14, 'square', 0.2, sfxGain));
  };
  S.longjump = () => { voice(ctx.currentTime, 250, 0.3, 'square', 0.22, sfxGain, { slideTo: 620 }); };
  S.land = () => voice(ctx.currentTime, 0, 0.07, 'noise', 0.16, sfxGain, { lp: 700, hold: 0.02, rel: 0.03 });
  S.pound = () => {
    const t = ctx.currentTime;
    voice(t, 320, 0.18, 'square', 0.3, sfxGain, { slideTo: 60 });
    voice(t + 0.1, 0, 0.16, 'noise', 0.4, sfxGain, { lp: 500, hold: 0.05, rel: 0.06 });
  };
  S.token = () => { const t = ctx.currentTime; voice(t, NOTE(95), 0.07, 'square', 0.2, sfxGain); voice(t + 0.06, NOTE(100), 0.34, 'square', 0.18, sfxGain); };
  S.stomp = () => { const t = ctx.currentTime; voice(t, 260, 0.16, 'square', 0.26, sfxGain, { slideTo: 90 }); voice(t, 0, 0.1, 'noise', 0.24, sfxGain, { lp: 1800, hold: 0.03, rel: 0.05 }); };
  S.hurt = () => { const t = ctx.currentTime; voice(t, 220, 0.3, 'sawtooth', 0.24, sfxGain, { slideTo: 90 }); };
  S.warp = () => { const t = ctx.currentTime; for (let i = 0; i < 10; i++) voice(t + i * 0.045, 300 + i * 130, 0.09, 'triangle', 0.16, sfxGain); };
  S.warpout = () => { const t = ctx.currentTime; for (let i = 0; i < 8; i++) voice(t + i * 0.04, 1400 - i * 140, 0.08, 'triangle', 0.14, sfxGain); };
  S.starspawn = () => { const t = ctx.currentTime; [72, 76, 79, 84, 88, 91, 96].forEach((n, i) => voice(t + i * 0.09, NOTE(n), 0.22, 'square', 0.16, sfxGain)); };
  S.starget = () => { // the fanfare
    const t = ctx.currentTime;
    const mel = [[0, 72, .18], [.14, 76, .18], [.28, 79, .18], [.42, 84, .4], [.66, 79, .18], [.8, 84, .7]];
    mel.forEach(([d, n, l]) => { voice(t + d, NOTE(n), l, 'square', 0.22, sfxGain); voice(t + d, NOTE(n - 12), l, 'triangle', 0.2, sfxGain); });
  };
  S.select = () => voice(ctx.currentTime, 880, 0.08, 'square', 0.16, sfxGain);
  S.denied = () => { const t = ctx.currentTime; voice(t, 200, 0.14, 'square', 0.2, sfxGain); voice(t + 0.13, 150, 0.22, 'square', 0.2, sfxGain); };
  S.bosshit = () => { const t = ctx.currentTime; voice(t, 180, 0.3, 'sawtooth', 0.32, sfxGain, { slideTo: 50 }); voice(t, 0, 0.2, 'noise', 0.3, sfxGain, { lp: 900, hold: 0.06, rel: 0.09 }); };
  S.bossroar = () => { const t = ctx.currentTime; voice(t, 90, 0.7, 'sawtooth', 0.3, sfxGain, { slideTo: 55, vib: 0.02 }); };
  S.charge = () => voice(ctx.currentTime, 0, 0.5, 'noise', 0.2, sfxGain, { lp: 1200, hold: 0.3, rel: 0.15 });
  S.crack = () => voice(ctx.currentTime, 0, 0.2, 'noise', 0.4, sfxGain, { lp: 3000, hold: 0.04, rel: 0.08 });
  S.pause = () => { const t = ctx.currentTime; voice(t, NOTE(84), 0.1, 'square', 0.16, sfxGain); voice(t + 0.09, NOTE(89), 0.18, 'square', 0.16, sfxGain); };

  return { init, playSong, stopSong, S, get ctx() { return ctx; } };
})();
