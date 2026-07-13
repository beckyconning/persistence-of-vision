// ============ N64-grade textures painted on tiny canvases ============
const TEX = (() => {
  function make(w, h, fn) {
    const c = document.createElement('canvas'); c.width = w; c.height = h;
    const x = c.getContext('2d');
    fn(x, w, h);
    const t = new THREE.CanvasTexture(c);
    t.magFilter = THREE.NearestFilter; t.minFilter = THREE.NearestFilter;
    t.wrapS = t.wrapT = THREE.RepeatWrapping;
    return t;
  }
  const R = (seed => () => (seed = (seed * 16807 + 11) % 2147483647) / 2147483647)(42);

  function speckle(x, w, h, base, spots, n, sz = 1) {
    x.fillStyle = base; x.fillRect(0, 0, w, h);
    for (let i = 0; i < n; i++) {
      x.fillStyle = spots[Math.floor(R() * spots.length)];
      x.fillRect(Math.floor(R() * w), Math.floor(R() * h), sz, sz);
    }
  }

  const T = {};
  T.grass = make(32, 32, (x, w, h) => speckle(x, w, h, '#58a83c', ['#4c9834', '#68bc48', '#3f8c2c', '#74c454'], 190));
  T.dirt = make(32, 32, (x, w, h) => speckle(x, w, h, '#8a5c34', ['#7a4e2a', '#9a6c40', '#6e4424'], 160));
  T.castle = make(32, 32, (x, w, h) => {
    x.fillStyle = '#d8cfc0'; x.fillRect(0, 0, w, h);
    x.fillStyle = '#b9ad9a';
    for (let r = 0; r < 4; r++) for (let c = 0; c < 4; c++)
      x.fillRect(c * 8 + (r % 2) * 4 + 1 - 4, r * 8 + 1, 7, 7);
    x.fillStyle = '#cfc5b4';
    for (let i = 0; i < 40; i++) x.fillRect(Math.floor(R() * w), Math.floor(R() * h), 1, 1);
  });
  T.carpet = make(32, 32, (x, w, h) => {
    speckle(x, w, h, '#b03028', ['#a02820', '#c03830', '#982018'], 120);
    x.fillStyle = '#d8b048'; x.fillRect(0, 0, w, 2); x.fillRect(0, h - 2, w, 2);
  });
  T.checker = make(32, 32, (x) => {
    x.fillStyle = '#2c2620'; x.fillRect(0, 0, 32, 32);
    x.fillStyle = '#e8e0d0'; x.fillRect(0, 0, 16, 16); x.fillRect(16, 16, 16, 16);
  });
  T.lava = make(32, 32, (x, w, h) => {
    speckle(x, w, h, '#e84a10', ['#ff7818', '#c83008', '#ffb028', '#a82404'], 240, 2);
  });
  T.basalt = make(32, 32, (x, w, h) => speckle(x, w, h, '#3a3038', ['#2e2630', '#463a44', '#241e28'], 170));
  T.ice = make(32, 32, (x, w, h) => {
    speckle(x, w, h, '#a8d8f0', ['#c0e8fc', '#90c8e8', '#d8f4ff'], 120, 2);
    x.strokeStyle = '#e8faff'; x.beginPath(); x.moveTo(4, 28); x.lineTo(14, 12); x.lineTo(26, 20); x.stroke();
  });
  T.snow = make(32, 32, (x, w, h) => speckle(x, w, h, '#eef4fa', ['#ffffff', '#dce8f2', '#e6eef8'], 90, 2));
  T.cloud = make(32, 32, (x, w, h) => speckle(x, w, h, '#f4f0fa', ['#ffffff', '#e6e0f2', '#eee8f8'], 80, 3));
  T.wood = make(32, 32, (x, w, h) => {
    x.fillStyle = '#7a5230'; x.fillRect(0, 0, w, h);
    x.fillStyle = '#684424';
    for (let i = 0; i < 6; i++) x.fillRect(0, i * 6 + Math.floor(R() * 2), w, 2);
    x.fillStyle = '#8a6240';
    for (let i = 0; i < 30; i++) x.fillRect(Math.floor(R() * w), Math.floor(R() * h), 2, 1);
  });
  T.books = make(64, 32, (x, w, h) => {
    x.fillStyle = '#3a2c22'; x.fillRect(0, 0, w, h);
    const cols = ['#8a3030', '#30608a', '#3a7a3a', '#8a7a30', '#6a3a8a', '#a05828'];
    let bx = 1;
    while (bx < w - 2) {
      const bw = 3 + Math.floor(R() * 4);
      const bh = 22 + Math.floor(R() * 8);
      x.fillStyle = cols[Math.floor(R() * cols.length)];
      x.fillRect(bx, h - bh, bw, bh);
      x.fillStyle = 'rgba(255,255,255,0.25)'; x.fillRect(bx, h - bh + 2, bw, 1);
      bx += bw + 1;
    }
  });
  T.door = make(32, 32, (x, w, h) => {
    x.fillStyle = '#6a4426'; x.fillRect(0, 0, w, h);
    x.fillStyle = '#573618'; x.fillRect(2, 2, w - 4, h - 2);
    x.fillStyle = '#7a5230'; x.fillRect(4, 4, w - 8, h - 4);
    x.fillStyle = '#d8b048'; x.fillRect(24, 16, 3, 3);
  });
  T.brickTop = make(32, 32, (x, w, h) => speckle(x, w, h, '#c89858', ['#b8884a', '#d8a868', '#a87838'], 140));

  // painting canvases: little scene previews (128x96)
  function painting(fn) {
    const c = document.createElement('canvas'); c.width = 128; c.height = 96;
    const x = c.getContext('2d');
    fn(x);
    const t = new THREE.CanvasTexture(c);
    t.magFilter = THREE.NearestFilter; t.minFilter = THREE.LinearFilter;
    return t;
  }
  T.paint_meadow = painting(x => {
    const g = x.createLinearGradient(0, 0, 0, 96); g.addColorStop(0, '#78b8f8'); g.addColorStop(1, '#b8e0ff');
    x.fillStyle = g; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#58a83c'; x.beginPath(); x.ellipse(30, 96, 55, 38, 0, Math.PI, 2 * Math.PI); x.fill();
    x.beginPath(); x.ellipse(100, 96, 60, 30, 0, Math.PI, 2 * Math.PI); x.fill();
    x.fillStyle = '#fff'; x.beginPath(); x.ellipse(30, 22, 14, 7, 0, 0, 7); x.fill();
    x.fillStyle = '#965cbe'; x.beginPath(); x.ellipse(96, 74, 9, 6, 0, 0, 7); x.fill();
    x.fillStyle = '#ffd23c';
    x.beginPath(); x.arc(108, 16, 7, 0, 7); x.fill();
  });
  T.paint_lava = painting(x => {
    x.fillStyle = '#301018'; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#e84a10'; x.fillRect(0, 66, 128, 30);
    x.fillStyle = '#ffb028'; for (let i = 0; i < 12; i++) x.fillRect(i * 11, 66 + (i % 3) * 3, 6, 2);
    x.fillStyle = '#3a3038'; x.fillRect(20, 30, 28, 40); x.fillRect(76, 22, 30, 48);
    x.fillStyle = '#ff7818'; x.fillRect(52, 10, 8, 8);
  });
  T.paint_ice = painting(x => {
    const g = x.createLinearGradient(0, 0, 0, 96); g.addColorStop(0, '#284868'); g.addColorStop(1, '#78a8d8');
    x.fillStyle = g; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#eef4fa'; x.beginPath(); x.moveTo(0, 96); x.lineTo(34, 40); x.lineTo(64, 96); x.fill();
    x.beginPath(); x.moveTo(50, 96); x.lineTo(92, 26); x.lineTo(128, 96); x.fill();
    x.fillStyle = '#a8d8f0'; x.fillRect(0, 88, 128, 8);
    x.fillStyle = '#fff'; x.fillRect(20, 20, 2, 2); x.fillRect(100, 12, 2, 2); x.fillRect(60, 8, 2, 2);
  });
  T.paint_sky = painting(x => {
    const g = x.createLinearGradient(0, 0, 0, 96); g.addColorStop(0, '#4868c8'); g.addColorStop(1, '#a8c8f8');
    x.fillStyle = g; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#f4f0fa';
    for (const [cx, cy, r] of [[26, 60, 16], [70, 40, 20], [108, 70, 14], [50, 80, 12]]) {
      x.beginPath(); x.ellipse(cx, cy, r, r * 0.45, 0, 0, 7); x.fill();
    }
    x.fillStyle = '#ffd23c'; x.beginPath(); x.arc(64, 18, 6, 0, 7); x.fill();
  });
  T.paint_legacy = painting(x => {
    x.fillStyle = '#181020'; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#3a2c22'; x.fillRect(8, 20, 30, 76); x.fillRect(50, 12, 30, 84); x.fillRect(92, 24, 30, 72);
    const cols = ['#8a3030', '#30608a', '#3a7a3a', '#8a7a30'];
    for (let s = 0; s < 3; s++) for (let i = 0; i < 5; i++) {
      x.fillStyle = cols[(s + i) % 4];
      x.fillRect(10 + s * 42 + i * 5, 30 + s * 4, 4, 18);
    }
    x.fillStyle = 'rgba(190,170,255,0.7)'; x.beginPath(); x.ellipse(64, 60, 8, 10, 0, 0, 7); x.fill();
    x.fillStyle = '#181020'; x.fillRect(60, 56, 3, 3); x.fillRect(66, 56, 3, 3);
  });
  T.paint_boss = painting(x => {
    x.fillStyle = '#1a0c14'; x.fillRect(0, 0, 128, 96);
    x.fillStyle = '#34323a'; x.beginPath(); x.moveTo(34, 96); x.lineTo(48, 14); x.lineTo(80, 14); x.lineTo(94, 96); x.fill();
    x.fillStyle = '#c81e1e'; x.fillRect(56, 30, 6, 6); x.fillRect(68, 30, 6, 6);
    x.fillStyle = '#96282e'; x.fillRect(52, 44, 26, 8);
    x.fillStyle = '#ffb028';
    for (let i = 0; i < 5; i++) { x.fillRect(10 + i * 4, 88 - i * 3, 3, 8 + i * 3); x.fillRect(115 - i * 4, 88 - i * 3, 3, 8 + i * 3); }
  });

  return T;
})();
