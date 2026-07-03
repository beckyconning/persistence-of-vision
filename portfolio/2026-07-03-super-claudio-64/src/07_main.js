// ============ GAME: state machine, HUD, loop ============
const GAME = {
  save: { stars: {} },
  state: 'title',
  levelId: null,
  ctx: null,
  starCount() { return Object.keys(this.save.stars).length; },
};

(() => {
  // ---- save ----
  try {
    const s = localStorage.getItem('claudio64_save');
    if (s) GAME.save = JSON.parse(s);
  } catch (e) { /* fresh */ }
  function persist() { try { localStorage.setItem('claudio64_save', JSON.stringify(GAME.save)); } catch (e) {} }

  // ---- renderer (N64 internal res, pixel upscale) ----
  const RW = 480, RH = 360;
  const renderer = new THREE.WebGLRenderer({ antialias: false });
  renderer.setSize(RW, RH, false);
  document.getElementById('game').appendChild(renderer.domElement);
  const camera = new THREE.PerspectiveCamera(55, RW / RH, 0.1, 400);
  let scene = new THREE.Scene();

  // ---- HUD ----
  const $ = id => document.getElementById(id);
  const hud = { stars: $('hud-stars'), tokens: $('hud-tokens'), hearts: $('hud-hearts'),
    banner: $('banner'), msg: $('msg'), fade: $('fade'), title: $('title'),
    starget: $('starget'), pausebox: $('pausebox'), boss: $('bosshp') };
  let bannerTimer = 0, msgTimer = 0;
  function banner(text, sub = '', dur = 3) {
    hud.banner.innerHTML = text + (sub ? `<div class="sub">${sub}</div>` : '');
    hud.banner.style.opacity = 1; bannerTimer = dur;
  }
  function msg(text, dur = 2.4) { hud.msg.textContent = text; hud.msg.style.opacity = 1; msgTimer = dur; }
  GAME.flashHearts = () => { hud.hearts.classList.remove('flash'); void hud.hearts.offsetWidth; hud.hearts.classList.add('flash'); };
  function refreshHUD() {
    hud.stars.textContent = '★×' + GAME.starCount();
    const ctx = GAME.ctx;
    if (ctx && ctx.tokens.length) {
      const got = ctx.tokens.filter(t => t.got).length;
      hud.tokens.textContent = '◉ ' + got + '/' + ctx.tokens.length;
      hud.tokens.style.display = 'block';
    } else hud.tokens.style.display = 'none';
    hud.hearts.textContent = '♥'.repeat(Math.max(0, player.hp)) + '♡'.repeat(Math.max(0, 3 - player.hp));
  }

  // ---- player ----
  const claudioMesh = CHARS.claudio();
  const player = new Player(claudioMesh);
  const gcam = new GameCamera(camera);
  GAME.player = player;

  // ---- level loading ----
  let world = new World();
  let fadeTo = null, fadeAlpha = 0, fadeDir = 0, pendingLevel = null;
  function setFade(a) { fadeAlpha = a; hud.fade.style.opacity = a; }

  function loadLevel(id, fromPainting) {
    GAME.levelId = id;
    const def = LVL.defs[id];
    scene = new THREE.Scene();
    world = new World();
    scene.fog = new THREE.Fog(def.fog[0], def.fog[1], def.fog[2]);
    const amb = new THREE.AmbientLight(0xffffff, id === 'legacy' ? 0.35 : 0.62);
    scene.add(amb);
    const sun = new THREE.DirectionalLight(0xfff2dc, id === 'legacy' ? 0.35 : 0.85);
    sun.position.set(30, 60, 20); scene.add(sun);
    const ctx = {
      scene, world, stars: [], tokens: [], enemies: [], movers: [], decor: [],
      paintings: null, crates: null, boss: null, fireballs: [], t: 0,
    };
    def.build(ctx);
    GAME.ctx = ctx;
    scene.add(claudioMesh);
    player.spawn(ctx.spawn);
    player.yaw = ctx.spawnYaw || 0;
    gcam.yaw = player.yaw + Math.PI;
    gcam.target.copy(player.pos);
    camera.position.set(player.pos.x + Math.sin(gcam.yaw) * 11, player.pos.y + 5, player.pos.z + Math.cos(gcam.yaw) * 11);
    AUDIO.playSong(SONGS[def.song]);
    banner(def.name, def.sub, 3.4);
    refreshHUD();
  }
  function warpTo(id) {
    AUDIO.S.warp();
    GAME.state = 'warp'; fadeDir = 1; pendingLevel = id;
  }
  GAME.exitToLobby = () => warpTo('lobby');
  GAME.debugWarp = warpTo;  // headless QA hook
  GAME.playerFell = () => { if (GAME.state === 'play') { player.hp = 0; GAME.playerDied(); } };
  GAME.playerDied = () => {
    if (GAME.state !== 'play') return;
    GAME.state = 'dead'; fadeDir = 1; AUDIO.S.hurt();
  };

  // ---- ground pound world reactions ----
  GAME.onPound = (pos) => {
    const ctx = GAME.ctx;
    if (!ctx) return;
    if (ctx.crates) {
      for (const c of ctx.crates) {
        if (c.broken) continue;
        const cx = (c.b.x0 + c.b.x1) / 2, cz = (c.b.z0 + c.b.z1) / 2;
        if (Math.hypot(pos.x - cx, pos.z - cz) < 2.6 && Math.abs(pos.y - c.b.y1) < 1.5) {
          c.broken = true;
          c.b.mesh.visible = false;
          world.boxes.splice(world.boxes.indexOf(c.b), 1);
          AUDIO.S.crack();
          if (ctx.crates.every(k => k.broken) && !GAME.save.stars[ctx.crateStar.id]) {
            spawnStar(ctx.crateStar); msg('A STAR HAS APPEARED!');
          } else msg(ctx.crates.filter(k => k.broken).length + '/3 CRATES COMPACTED');
        }
      }
    }
    // pound near stunned boss = hit (checked in boss logic via flag)
    ctx.poundedAt = { x: pos.x, z: pos.z, t: ctx.t };
  };
  function spawnStar(spec) {
    AUDIO.S.starspawn();
    LVL.addStar(GAME.ctx, spec.id, spec.x, spec.y, spec.z);
  }

  // ---- star collection ----
  let stargetTimer = 0, gotStarId = null;
  function collectStar(st) {
    GAME.save.stars[st.id] = true; persist();
    st.mesh.visible = false;
    AUDIO.stopSong(); AUDIO.S.starget();
    GAME.state = 'starget'; stargetTimer = 3.6; gotStarId = st.id;
    hud.starget.style.opacity = 1;
    hud.starget.innerHTML = '★ STAR GET! ★<div class="sub">' + (GAME.starCount()) + ' / 12</div>';
    player.frozen = true;
  }

  // ---- boss logic ----
  function updateBoss(ctx, dt) {
    const B = ctx.boss;
    if (!B) return;
    const m = B.mesh, P = player.pos;
    B.t += dt;
    const J = m.userData.joints;
    const distToP = Math.hypot(P.x - B.pos.x, P.z - B.pos.z);
    hud.boss.style.display = B.state === 'dead' ? 'none' : 'block';
    hud.boss.textContent = 'GROKIO ' + '♥'.repeat(3 - B.hits) + '♡'.repeat(B.hits);

    switch (B.state) {
      case 'intro':
        if (B.t > 1.2 && !B.roared) { AUDIO.S.bossroar(); banner('SUPER GROKIO', 'the evil brother demands a rematch'); B.roared = true; }
        if (B.t > 3) { B.state = 'walk'; B.t = 0; B.thrown = 0; }
        break;
      case 'walk': {
        const dx = (P.x - B.pos.x) / (distToP || 1), dz = (P.z - B.pos.z) / (distToP || 1);
        B.pos.x += dx * 4.2 * dt; B.pos.z += dz * 4.2 * dt;
        m.rotation.y = Math.atan2(dx, dz);
        if (J) { J.hipL.rotation.x = Math.sin(B.t * 7) * 0.7; J.hipR.rotation.x = -Math.sin(B.t * 7) * 0.7; }
        if (B.t > 1.6) {
          B.t = 0; B.thrown++;
          if (B.thrown > 2) { B.state = 'telegraph'; AUDIO.S.bossroar(); }
          else { // lob a fireball
            const fb = new THREE.Mesh(new THREE.SphereGeometry(0.55, 8, 6),
              new THREE.MeshLambertMaterial({ color: 0x9632c8, emissive: 0x501878 }));
            fb.position.set(B.pos.x, 3.2, B.pos.z);
            scene.add(fb);
            const d = Math.max(distToP, 4), fx = (P.x - B.pos.x) / distToP, fz = (P.z - B.pos.z) / distToP;
            ctx.fireballs.push({ mesh: fb, vx: fx * d * 0.55, vy: 8, vz: fz * d * 0.55, alive: true });
            AUDIO.S.charge();
          }
        }
        break;
      }
      case 'telegraph':
        m.position.x = B.pos.x + (Math.random() - 0.5) * 0.24;
        m.position.z = B.pos.z + (Math.random() - 0.5) * 0.24;
        if (B.t > 0.9) {
          B.state = 'charge'; B.t = 0;
          const d = Math.hypot(P.x - B.pos.x, P.z - B.pos.z) || 1;
          B.chargeDir.set((P.x - B.pos.x) / d, 0, (P.z - B.pos.z) / d);
          AUDIO.S.charge();
        }
        break;
      case 'charge': {
        B.pos.x += B.chargeDir.x * (B.speed + B.hits * 2.5) * dt;
        B.pos.z += B.chargeDir.z * (B.speed + B.hits * 2.5) * dt;
        m.rotation.y = Math.atan2(B.chargeDir.x, B.chargeDir.z);
        m.rotation.x = 0.35;
        if (Math.hypot(B.pos.x, B.pos.z) > 13.6) {  // CRASH into the rim
          B.pos.multiplyScalar(13.6 / Math.hypot(B.pos.x, B.pos.z));
          B.state = 'stunned'; B.t = 0; m.rotation.x = 0;
          AUDIO.S.crack(); msg('NOW! GROUND POUND HIM! (C mid-air)');
        }
        break;
      }
      case 'stunned':
        m.rotation.z = Math.sin(B.t * 9) * 0.18;
        if (J) { J.head.rotation.z = Math.sin(B.t * 12) * 0.3; }
        // pounded near him?
        if (ctx.poundedAt && ctx.t - ctx.poundedAt.t < 0.25 &&
            Math.hypot(ctx.poundedAt.x - B.pos.x, ctx.poundedAt.z - B.pos.z) < 3.0) {
          ctx.poundedAt = null;
          B.hits++; B.state = 'hitreact'; B.t = 0; m.rotation.z = 0;
          AUDIO.S.bosshit();
          if (B.hits >= 3) { B.state = 'dying'; B.t = 0; AUDIO.stopSong(); AUDIO.S.bossroar(); }
          else banner(['', 'ONE MORE ART THOU', 'HE WOBBLES! FINISH HIM'][B.hits] || '', '', 2);
        }
        if (B.t > 4.2) { B.state = 'walk'; B.t = 0; B.thrown = 0; m.rotation.z = 0; }
        break;
      case 'hitreact':
        m.rotation.z = Math.sin(B.t * 30) * 0.3;
        if (B.t > 0.8) { B.state = 'walk'; B.t = 0; B.thrown = 0; m.rotation.z = 0; }
        break;
      case 'dying': {
        B.pos.y = (B.pos.y || 0) + (8 + B.t * 14) * dt;
        m.rotation.y += dt * 14; m.rotation.z += dt * 6;
        const s = Math.max(0.05, 1.35 - B.t * 0.5);
        m.scale.set(s, s * 1.05, s);
        if (B.t > 2.2 && !B.gone) {
          B.gone = true; m.visible = false;
          AUDIO.S.starspawn();
          LVL.addStar(GAME.ctx, 'grand_star', 0, 2.4, 0);
          GAME.ctx.stars[GAME.ctx.stars.length - 1].grand = true;
          const gs = GAME.ctx.stars[GAME.ctx.stars.length - 1].mesh;
          gs.scale.setScalar(2.2);
          banner('THE GRAND STAR', 'claim what is a yours');
        }
        if (B.gone && B.t > 2.6) B.state = 'dead';
        break;
      }
      case 'dead': break;
    }
    if (B.state !== 'dying') m.position.set(B.pos.x, B.pos.y || 0, B.pos.z);
    else m.position.set(B.pos.x, B.pos.y, B.pos.z);
    // contact damage
    if (['walk', 'charge', 'telegraph'].includes(B.state) && distToP < 2.2 && Math.abs(P.y - (B.pos.y || 0)) < 2.4) {
      player.hurt(GAME);
    }
    // fireballs
    for (const f of ctx.fireballs) {
      if (!f.alive) continue;
      f.vy -= 22 * dt;
      f.mesh.position.x += f.vx * dt; f.mesh.position.y += f.vy * dt; f.mesh.position.z += f.vz * dt;
      if (f.mesh.position.y <= 0.4) {
        f.alive = false;
        if (Math.hypot(f.mesh.position.x - P.x, f.mesh.position.z - P.z) < 2.4 && P.y < 2) player.hurt(GAME);
        scene.remove(f.mesh);
      }
    }
  }

  // ---- main loop ----
  let last = performance.now();
  function frame(now) {
    requestAnimationFrame(frame);
    let dt = Math.min(0.05, (now - last) / 1000);
    last = now;
    const ctx = GAME.ctx;

    if (bannerTimer > 0) { bannerTimer -= dt; if (bannerTimer <= 0) hud.banner.style.opacity = 0; }
    if (msgTimer > 0) { msgTimer -= dt; if (msgTimer <= 0) hud.msg.style.opacity = 0; }

    switch (GAME.state) {
      case 'title':
        if (INPUT.pressed.Enter || INPUT.pressed.Space) {
          AUDIO.init();
          hud.title.style.display = 'none';
          loadLevel('lobby');
          GAME.state = 'play';
        }
        break;
      case 'play': {
        ctx.t += dt;
        // pause
        if (INPUT.pressed.Escape) { GAME.state = 'pause'; hud.pausebox.style.display = 'block'; AUDIO.S.pause(); break; }
        // movers first (they feed rideDelta)
        for (const mv of ctx.movers) {
          const [nx, ny, nz] = mv.fn(ctx.t);
          const b = mv.b;
          const w = b.x1 - b.x0, h = b.y1 - b.y0, d = b.z1 - b.z0;
          const dx = nx - (b.x0 + w / 2), dy = ny - b.y0, dz = nz - (b.z0 + d / 2);
          b.x0 += dx; b.x1 += dx; b.y0 += dy; b.y1 += dy; b.z0 += dz; b.z1 += dz;
          b.mesh.position.set(nx, ny + h / 2, nz);
          b.mover = true;
          if (player.standingOn === b) player.rideDelta.set(dx, dy, dz);
        }
        // zones
        player.ice = false;
        if (ctx.iceZones) for (const z of ctx.iceZones) {
          const inR = z.r ? (Math.hypot(player.pos.x - z.x, player.pos.z - z.z) < z.r)
            : (player.pos.x > z.box[0] && player.pos.x < z.box[0] + z.box[3] * 8);
          if (inR && Math.abs(player.pos.y - z.y) < 1.6) player.ice = true;
        }
        if (ctx.windZones) for (const w of ctx.windZones) {
          if (player.pos.x > w.x0 && player.pos.x < w.x1 && player.pos.z > w.z0 && player.pos.z < w.z1) {
            player.vel.x += w.fx * dt; player.vel.z += w.fz * dt;
          }
        }
        player.update(dt, world, gcam.yaw, GAME);
        if (ctx.lavaY != null && player.pos.y <= ctx.lavaY && GAME.state === 'play') {
          player.hurt(GAME); player.vel.y = 14; player.pos.y = ctx.lavaY + 0.1;
        }
        gcam.update(dt, player.pos, world);
        // stars
        for (const st of ctx.stars) {
          if (!st.mesh.visible) continue;
          st.mesh.rotation.y += dt * 2.2;
          st.mesh.position.y = st.y + Math.sin(ctx.t * 2 + st.x) * 0.15;
          if (player.pos.distanceTo(st.mesh.position) < (st.grand ? 2.8 : 1.5)) collectStar(st);
        }
        // tokens
        if (ctx.tokens.length) {
          let all = true;
          for (const tk of ctx.tokens) {
            if (tk.got) continue;
            all = false;
            tk.mesh.rotation.y += dt * 3.4;
            if (player.pos.distanceTo(tk.mesh.position) < 1.3) {
              tk.got = true; tk.mesh.visible = false; AUDIO.S.token(); refreshHUD();
              const left = ctx.tokens.filter(t => !t.got).length;
              if (left > 0 && left <= 3) msg(left + ' TOKENS REMAIN');
            }
          }
          if (all && ctx.tokenStar && !ctx.tokenStarSpawned) {
            ctx.tokenStarSpawned = true;
            if (!GAME.save.stars[ctx.tokenStar.id]) { spawnStar(ctx.tokenStar); msg('A STAR HAS APPEARED!'); }
          }
        }
        // enemies
        for (const e of ctx.enemies) {
          const m = e.mesh;
          if (e.dead > 0) {
            e.dead -= dt; m.scale.y = 0.15;
            if (e.dead <= 0) m.visible = false;
            continue;
          }
          e.t += dt;
          const toP = Math.hypot(player.pos.x - e.x, player.pos.z - e.z);
          if (e.ghost) {
            // moves only when unwatched
            const camDir = new THREE.Vector3(); camera.getWorldDirection(camDir);
            const toG = new THREE.Vector3(e.x - camera.position.x, 0, e.z - camera.position.z).normalize();
            const watched = camDir.x * toG.x + camDir.z * toG.z > 0.55;
            m.children.forEach(ch => { if (ch.material) ch.material.opacity = watched ? 0.16 : 0.6; });
            if (!watched && toP > 0.5) {
              e.x += (player.pos.x - e.x) / toP * e.speed * dt;
              e.z += (player.pos.z - e.z) / toP * e.speed * dt;
            }
          } else if (toP < 6.5) {
            e.x += (player.pos.x - e.x) / toP * e.speed * dt;
            e.z += (player.pos.z - e.z) / toP * e.speed * dt;
          } else {
            e.x = e.home[0] + Math.cos(e.t * 0.55) * e.radius * 0.5;
            e.z = e.home[1] + Math.sin(e.t * 0.4) * e.radius * 0.5;
          }
          const gy = e.gy != null ? e.gy : (world.groundAt(e.x, e.z, 30).g);
          m.position.set(e.x, (isFinite(gy) ? gy : 0) + Math.abs(Math.sin(e.t * 10)) * 0.06, e.z);
          m.rotation.y = Math.atan2(player.pos.x - e.x, player.pos.z - e.z);
          if (m.userData.legs) m.userData.legs.forEach((l, i) => { l.rotation.x = Math.sin(e.t * 12 + i) * 0.5; });
          // interactions
          const vd = player.pos.y - m.position.y;
          if (toP < 1.15 && vd < 2.2) {
            if (!e.ghost && vd > 0.5 && player.vel.y < -2) {
              e.dead = 1.4; AUDIO.S.stomp(); player.vel.y = 9.5; msg('BUG FIXED!', 1.4);
            } else if (vd < 1.4 && !e.ghost) player.hurt(GAME);
            else if (e.ghost && vd < 1.4) player.hurt(GAME);
          }
        }
        // lobby interactions
        if (ctx.paintings) {
          for (const p of ctx.paintings) {
            const dx = player.pos.x - p.x, dz = player.pos.z - p.z;
            const lat = Math.abs(p.ry) > 1 ? Math.abs(dz) : Math.abs(dx);   // along wall
            const pen = Math.abs(p.ry) > 1 ? Math.abs(dx) : Math.abs(dz);   // toward wall
            if (lat < 2.7 && pen < 1.15 && Math.abs(player.pos.y + 1 - p.y) < 4.2) {
              if (GAME.starCount() >= p.def.need) warpTo(p.def.id);
              else {
                AUDIO.S.denied();
                player.vel.x = dx * 4; player.vel.z = dz * 4;
                const away = Math.abs(p.ry) > 1 ? Math.sign(-p.x) : Math.sign(-p.z + 0.001);
                if (Math.abs(p.ry) > 1) player.vel.x = away * 8; else player.vel.z = away * 8;
                msg('NEEDS ' + p.def.need + ' STARS');
              }
            }
          }
          const bd = ctx.bossDoor;
          if (Math.abs(player.pos.x - bd.x) < 2.6 && Math.abs(player.pos.z - bd.z) < 1.6 && player.pos.y > 2) {
            if (GAME.starCount() >= bd.need) warpTo('boss');
            else { AUDIO.S.denied(); player.vel.z = 9; msg('THE DOOR DEMANDS ' + bd.need + ' STARS'); }
          }
        }
        if (ctx.boss) updateBoss(ctx, dt);
        for (const fn of ctx.decor) fn(ctx.t);
        refreshHUD();
        break;
      }
      case 'pause':
        if (INPUT.pressed.Escape) { GAME.state = 'play'; hud.pausebox.style.display = 'none'; }
        if (INPUT.pressed.KeyB && GAME.levelId !== 'lobby') {
          hud.pausebox.style.display = 'none'; warpTo('lobby');
        }
        break;
      case 'warp':
        setFade(Math.min(1, fadeAlpha + dt * 2.2));
        if (fadeAlpha >= 1 && pendingLevel) {
          loadLevel(pendingLevel); pendingLevel = null;
          GAME.state = 'warpin'; AUDIO.S.warpout();
        }
        break;
      case 'warpin':
        setFade(Math.max(0, fadeAlpha - dt * 1.8));
        if (fadeAlpha <= 0) GAME.state = 'play';
        break;
      case 'dead':
        setFade(Math.min(1, fadeAlpha + dt * 1.6));
        if (fadeAlpha >= 1) {
          player.spawn(GAME.ctx.spawn); refreshHUD();
          GAME.state = 'warpin';
        }
        break;
      case 'starget':
        stargetTimer -= dt;
        player.animate(dt, 0);
        claudioMesh.rotation.y += dt * 5;
        if (stargetTimer < 1.2) hud.starget.style.opacity = 0;
        if (stargetTimer <= 0) {
          player.frozen = false;
          claudioMesh.rotation.x = 0;
          if (gotStarId === 'grand_star') {
            GAME.state = 'victory';
            AUDIO.playSong(SONGS.victory);
            banner('CONGRATURATION!', 'you are winner of a SUPER CLAUDIO 64 — thank you for a to playing', 12);
          } else warpTo('lobby');
        }
        break;
      case 'victory': {
        GAME.ctx.t += dt;
        player.update(dt, world, gcam.yaw, GAME);
        gcam.update(dt, player.pos, world);
        for (const fn of GAME.ctx.decor) fn(GAME.ctx.t);
        if (INPUT.pressed.Escape) warpTo('lobby');
        break;
      }
    }
    INPUT.clear();
    renderer.render(scene, camera);
  }
  requestAnimationFrame(frame);
})();
