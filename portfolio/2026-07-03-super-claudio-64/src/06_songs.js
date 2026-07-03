// ============ SOUNDTRACK: note-table songs ============
const SONGS = (() => {
  // helpers to build note lists
  function seq(startBeat, step, notes, len) { // notes: midi or null
    const out = [];
    notes.forEach((n, i) => { if (n !== null) out.push([startBeat + i * step, n, len || step]); });
    return out;
  }
  function drums4(bars, pat = 'basic', startBar = 0) {
    const d = [];
    for (let b = 0; b < bars; b++) {
      const t = (startBar + b) * 4;
      if (pat === 'basic') {
        d.push([t, 'k'], [t + 2, 'k'], [t + 1, 's'], [t + 3, 's']);
        for (let i = 0; i < 8; i++) d.push([t + i * 0.5, 'h']);
      } else if (pat === 'half') {
        d.push([t, 'k'], [t + 2.5, 'k'], [t + 2, 's']);
        d.push([t, 'h'], [t + 1, 'h'], [t + 2, 'h'], [t + 3, 'h']);
      } else if (pat === 'drive') {
        d.push([t, 'k'], [t + 1, 'k'], [t + 1.75, 'k'], [t + 2, 's'], [t + 3, 'k'], [t + 3.5, 's']);
        for (let i = 0; i < 8; i++) d.push([t + i * 0.5, 'h']);
      }
    }
    return d;
  }

  const S = {};

  // ---- LOBBY: floaty castle waltz (3/4, dreamy) ----
  {
    const arp = [];
    const chords = [[57, 60, 64], [55, 59, 62], [53, 57, 60], [55, 59, 62]];
    for (let bar = 0; bar < 8; bar++) {
      const ch = chords[bar % 4];
      for (let i = 0; i < 3; i++) arp.push([bar * 3 + i, ch[i % 3] + 12, 0.9]);
    }
    const mel = seq(0, 1.5, [76, 79, 77, 76, 74, 72, 74, null, 72, 71, 72, 74, 72, null, null, null], 1.4);
    S.lobby = {
      bpm: 100, loopBeats: 24,
      tracks: [
        { type: 'triangle', vol: 0.16, notes: arp, holdF: 0.8 },
        { type: 'square', vol: 0.07, vib: 0.006, notes: mel, holdF: 0.85 },
        { type: 'triangle', vol: 0.2, notes: seq(0, 3, [45, 43, 41, 43, 45, 43, 41, 43], 2.8), holdF: 0.9 },
      ],
      drums: [],
    };
  }

  // ---- MEADOW: the bouncy overworld ----
  {
    const lead = [
      ...seq(0, 0.5, [64, 67, 69, 67, 64, 60, 62, 64], 0.48),
      [4, 64, 1], [5, 62, 0.5], [5.5, 64, 0.5], [6, 65, 0.5], [6.5, 67, 1.4],
      ...seq(8, 0.5, [69, 72, 74, 72, 69, 67, 65, 64], 0.48),
      [12, 62, 0.9], [13, 64, 0.9], [14, 60, 1.8],
    ];
    const harm = lead.map(([b, n, l]) => [b, n - 12, l]);
    const bass = [];
    const roots = [48, 43, 45, 41];
    for (let bar = 0; bar < 4; bar++) {
      bass.push([bar * 4, roots[bar], 1.2], [bar * 4 + 2, roots[bar] + 7, 1.2], [bar * 4 + 3, roots[bar] + 12, 0.8]);
    }
    S.meadow = {
      bpm: 132, loopBeats: 16,
      tracks: [
        { type: 'square', vol: 0.12, notes: lead, holdF: 0.7 },
        { type: 'square', vol: 0.05, notes: harm, holdF: 0.7 },
        { type: 'triangle', vol: 0.22, notes: bass, holdF: 0.8 },
      ],
      drums: drums4(4, 'basic'),
    };
  }

  // ---- LAVA: menacing ostinato ----
  {
    const riff = [];
    for (let bar = 0; bar < 4; bar++) {
      const tr = bar === 3 ? 1 : 0;
      riff.push(...seq(bar * 4, 0.5, [38 + tr, 38 + tr, 45 + tr, 38 + tr, 44 + tr, 38 + tr, 43 + tr, 41 + tr], 0.45));
    }
    const stabs = [[2, 62, 0.4], [3.5, 61, 0.4], [6, 62, 0.4], [10, 65, 0.4], [11.5, 64, 0.4], [14, 62, 1.6]];
    S.lava = {
      bpm: 118, loopBeats: 16,
      tracks: [
        { type: 'triangle', vol: 0.26, notes: riff, holdF: 0.55 },
        { type: 'square', vol: 0.08, vib: 0.01, notes: stabs, holdF: 0.6 },
      ],
      drums: drums4(4, 'half'),
    };
  }

  // ---- ICE: music box ----
  {
    const box_ = [];
    const pat = [81, 76, 79, 74, 77, 72, 76, 71];
    for (let bar = 0; bar < 4; bar++) {
      for (let i = 0; i < 4; i++) box_.push([bar * 4 + i, pat[(bar * 4 + i) % 8] + (bar % 2 ? -2 : 0), 0.9]);
    }
    S.ice = {
      bpm: 88, loopBeats: 16,
      tracks: [
        { type: 'square', vol: 0.09, notes: box_, holdF: 0.5 },
        { type: 'triangle', vol: 0.16, notes: seq(0, 4, [57, 53, 55, 52], 3.6), holdF: 0.9 },
        { type: 'sine', vol: 0.1, vib: 0.008, notes: [[2, 88, 1.6], [10, 86, 1.6], [14, 84, 1.8]], holdF: 0.8 },
      ],
      drums: [],
    };
  }

  // ---- SKY: airy 6/8 ----
  {
    const arp = [];
    const chords = [[60, 64, 67, 71], [57, 60, 64, 67], [62, 65, 69, 72], [55, 59, 62, 67]];
    for (let bar = 0; bar < 4; bar++) {
      const ch = chords[bar];
      for (let i = 0; i < 6; i++) arp.push([bar * 6 + i, ch[i % 4] + 12 * Math.floor(i / 4), 0.9]);
    }
    S.sky = {
      bpm: 150, loopBeats: 24,
      tracks: [
        { type: 'triangle', vol: 0.17, notes: arp, holdF: 0.75 },
        { type: 'square', vol: 0.07, vib: 0.007, notes: seq(0, 3, [79, 76, 81, 79, 74, 76, 72, null], 2.8), holdF: 0.85 },
        { type: 'triangle', vol: 0.18, notes: seq(0, 6, [48, 45, 50, 43], 5.6), holdF: 0.92 },
      ],
      drums: [],
    };
  }

  // ---- LEGACY: haunted organ ----
  {
    const chords = [];
    const prog = [[45, 48, 52], [44, 47, 52], [45, 48, 53], [41, 45, 50]];
    prog.forEach((ch, bar) => ch.forEach(n => chords.push([bar * 4, n, 3.6], [bar * 4, n + 12, 3.6])));
    const creep = seq(0, 1, [69, 68, 69, 71, 69, 68, 66, 68, 69, 72, 71, 68, 69, null, null, null], 0.95);
    S.legacy = {
      bpm: 78, loopBeats: 16,
      tracks: [
        { type: 'triangle', vol: 0.14, notes: chords, holdF: 0.95 },
        { type: 'square', vol: 0.055, vib: 0.012, notes: creep, holdF: 0.8 },
      ],
      drums: [],
    };
  }

  // ---- BOSS: the phrygian drive ----
  {
    const riff = [];
    for (let bar = 0; bar < 4; bar++) {
      const t = bar === 2 ? 3 : (bar === 3 ? -2 : 0);
      riff.push(...seq(bar * 4, 0.5, [40 + t, 41 + t, 40 + t, 47 + t, 40 + t, 46 + t, 47 + t, 41 + t], 0.42));
    }
    const lead = [
      [0, 64, 0.4], [0.5, 65, 0.4], [1, 64, 0.9], [2.5, 71, 0.4], [3, 70, 0.9],
      [8, 76, 0.4], [8.5, 77, 0.4], [9, 76, 0.9], [10.5, 72, 0.4], [11, 71, 1.8],
    ];
    S.boss = {
      bpm: 152, loopBeats: 16,
      tracks: [
        { type: 'sawtooth', vol: 0.14, notes: riff, holdF: 0.5 },
        { type: 'square', vol: 0.1, notes: lead, holdF: 0.6 },
        { type: 'square', vol: 0.045, notes: lead.map(([b, n, l]) => [b, n + 7, l]), holdF: 0.6 },
      ],
      drums: drums4(4, 'drive'),
    };
  }

  // ---- VICTORY: post-boss loop ----
  S.victory = {
    bpm: 112, loopBeats: 16,
    tracks: [
      { type: 'square', vol: 0.11, vib: 0.006, notes: [[0, 72, 1], [1, 76, 1], [2, 79, 1], [3, 84, 2.6], [8, 81, 1], [9, 84, 1], [10, 88, 3.4]], holdF: 0.8 },
      { type: 'triangle', vol: 0.2, notes: seq(0, 2, [48, 52, 53, 55, 48, 52, 53, 43], 1.8), holdF: 0.85 },
    ],
    drums: drums4(4, 'half'),
  };

  return S;
})();
