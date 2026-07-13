// ============ ICE + SKY + LEGACY + BOSS (enlarged) ============
(() => {
  const { mat, box, cyl, gaussTerrain, terrainMesh, skyDome, addStar, addToken, addBug } = LVL;

  // ---------- FROZEN CACHE ----------
  LVL.defs.ice = {
    name: 'FROZEN CACHE', sub: 'cold storage', song: 'ice',
    sky: [0x284868, 0x98c0e0], fog: [0x9cc0dc, 50, 150],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x284868, 0x98c0e0);
      const terr = gaussTerrain([[0, 0, 40, 0.9], [-34, -26, 15, 5.0], [28, -28, 18, 7.5],
                                 [30, 22, 13, 2.6], [-30, 18, 12, 3.0]], 0);
      world.terrain = terr; world.killY = -20;
      terrainMesh(scene, terr, 140, 66, mat(TEX.snow, 28, 28));
      // frozen lake (slippery)
      const lake = new THREE.Mesh(new THREE.CylinderGeometry(16, 16, 0.3, 22), mat(TEX.ice, 10, 10));
      lake.position.set(-10, 0.95, 12); scene.add(lake);
      world.cyls.push({ x: -10, z: 12, r: 16, y0: -1, y1: 1.1 });
      ctx.iceZones = [{ x: -10, z: 12, r: 16, y: 1.1 }];
      // ice pillar stack (star 1)
      const steps = [[18, 2, -2, 2.4], [22, 3.4, -7, 2.2], [18, 4.8, -12, 2.0],
                     [23, 6.4, -16, 1.8], [19, 8.2, -20, 1.7], [23, 10.0, -24, 1.6]];
      for (const [sx, sy, sz, sr] of steps) cyl(scene, world, sx, 0, sz, sr, sy + 0.4, mat(TEX.ice, 3, 2), 8);
      addStar(ctx, 'ice_pillar', 23, 12.1, -24);
      // the LONG slide with token trail
      for (let i = 0; i < 13; i++) {
        const y = 10.5 - i * 0.82, z = -34 + i * 3.6;
        box(scene, world, -26, y, z, 5.5, 0.5, 4.2, mat(TEX.ice, 3, 2));
        if (i > 0 && i % 3 !== 0) addToken(ctx, -26 + Math.sin(i * 1.3) * 1.4, y + 1.2, z);
      }
      ctx.iceZones.push({ box: [-30, -20, -36, 8], y: 11.2 });
      ctx.tokenStar = { id: 'ice_tokens', x: -26, y: 1.8, z: 12 };
      // snowmen
      for (const [sx2, sz2] of [[8, 18], [-20, -10], [10, -16], [-6, 32], [24, 8]]) {
        const gy = terr(sx2, sz2);
        const b1 = new THREE.Mesh(new THREE.SphereGeometry(1.1, 9, 7), mat(TEX.snow, 3, 3));
        b1.position.set(sx2, gy + 0.9, sz2); scene.add(b1);
        const b2 = new THREE.Mesh(new THREE.SphereGeometry(0.7, 8, 6), mat(TEX.snow, 2, 2));
        b2.position.set(sx2, gy + 2.1, sz2); scene.add(b2);
        const nose = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.5, 6),
          new THREE.MeshLambertMaterial({ color: 0xe87820 }));
        nose.rotation.x = Math.PI / 2; nose.position.set(sx2, gy + 2.15, sz2 + 0.7); scene.add(nose);
      }
      // frozen trees
      for (const [tx, tz] of [[14, 26], [-26, 2], [34, -8], [-14, -30]]) {
        const gy = terr(tx, tz);
        cyl(scene, world, tx, gy, tz, 0.3, 2.2, mat(TEX.wood, 1, 2));
        const c = new THREE.Mesh(new THREE.ConeGeometry(1.6, 3.2, 7), mat(TEX.snow, 2, 2));
        c.position.set(tx, gy + 3.6, tz); scene.add(c);
      }
      addBug(ctx, 5, 5, { speed: 3.4 }); addBug(ctx, -5, 22, { speed: 3.0 });
      addBug(ctx, 15, 12, {}); addBug(ctx, -24, 24, { speed: 2.6 });
      ctx.spawn = new THREE.Vector3(2, terr(2, 32) + 0.3, 32);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- CONTEXT WINDOW (sky) ----------
  LVL.defs.sky = {
    name: 'CONTEXT WINDOW', sub: 'do not look down (it is compacted)', song: 'sky',
    sky: [0x3858c0, 0xb8d0f8], fog: [0xa8c0ec, 50, 160],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x3858c0, 0xb8d0f8);
      world.terrain = null; world.killY = -14;
      const cloudM = () => mat(TEX.cloud, 3, 3);
      const P = [
        [0, 0, 30, 8, 6], [0, 1.1, 16, 5.5, 4.5], [-10, 2.4, 5, 4.5, 4.5], [-18, 3.7, -6, 4.5, 4],
        [-9, 4.8, -16, 4.5, 4], [3, 5.9, -24, 5, 4.5], [16, 7, -18, 4.5, 4],
        [23, 8, -6, 5.5, 4.5], [16, 9.4, 6, 4, 3.5], [26, 10.6, 16, 4.5, 4],
        [12, 12, 22, 4, 3.5],
      ];
      P.forEach(([x, y, z, w, d], i) => {
        box(scene, world, x, y, z, w, 0.9, d, cloudM());
        if (i > 0 && i < 9) addToken(ctx, x, y + 1.5, z);
      });
      ctx.tokenStar = { id: 'sky_tokens', x: 0, y: 2.6, z: 16 };
      // moving cloud to the far star
      const mv = box(scene, world, 2, 13, 16, 3.4, 0.7, 3.4, cloudM());
      ctx.movers.push({ b: mv, fn: t => [2 + Math.sin(t * 0.55) * 10, 13, 16 + Math.cos(t * 0.55) * 5] });
      box(scene, world, -14, 14.6, 24, 4.5, 0.9, 4.5, cloudM());
      addStar(ctx, 'sky_far', -14, 16.4, 24);
      // wind zone
      ctx.windZones = [{ x0: -4, x1: 12, z0: -28, z1: -12, fx: 5.5, fz: 0 }];
      // birds
      for (let i = 0; i < 5; i++) {
        const bird = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.9, 4),
          new THREE.MeshLambertMaterial({ color: 0xffffff }));
        bird.rotation.z = Math.PI / 2; scene.add(bird);
        ctx.decor.push(t => {
          const a = t * 0.4 + i * 1.3;
          bird.position.set(Math.cos(a) * 30, 9 + Math.sin(t + i) * 3, Math.sin(a) * 30);
        });
      }
      ctx.spawn = new THREE.Vector3(0, 1.6, 33);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- LEGACY CODEBASE ----------
  LVL.defs.legacy = {
    name: 'LEGACY CODEBASE', sub: 'nobody remembers why this works', song: 'legacy',
    sky: [0x100c1c, 0x241c30], fog: [0x181226, 16, 70],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x100c1c, 0x241c30);
      world.killY = -15;
      box(scene, world, 0, -1, 0, 76, 1, 76, mat(TEX.wood, 19, 19));
      const shelfM = () => mat(TEX.books, 3, 2);
      const shelves = [
        [0, -14, 26, 5.5], [-19, 2, 5, 7.5], [19, 2, 5, 7.5], [0, 10, 16, 5],
        [-11, 24, 13, 6.5], [13, 21, 10, 5.5], [-27, -16, 8, 8.5], [27, -16, 8, 8.5],
        [0, -30, 40, 6.5], [-32, 8, 6, 6], [32, 8, 6, 6], [0, 34, 30, 7],
      ];
      for (const [x, z, w, h] of shelves) box(scene, world, x, 0, z, w, h, 2.4, shelfM());
      // stacked book platforms up to the central shelf star
      const bookM = c => new THREE.MeshLambertMaterial({ color: c });
      const stack = [[-23, 1.2, -10, 0x8a3030], [-19, 2.6, -7, 0x30608a], [-15, 4.0, -10, 0x3a7a3a],
                     [-11, 5.4, -13, 0x8a7a30], [-7, 6.8, -11, 0x6a3a8a], [-3, 8.0, -12, 0xa05828]];
      for (const [x, y, z, c] of stack) box(scene, world, x, y, z, 2.8, 0.5, 2.0, bookM(c));
      addStar(ctx, 'legacy_top', 0, 10.2, -14);
      // tokens through the maze
      const tok = [[-19, 1.2, 12], [19, 1.2, 12], [0, 1.2, 18], [-11, 7.8, 24], [13, 6.8, 21],
                   [-27, 9.8, -16], [27, 9.8, -16], [0, 7.8, -30]];
      for (const [x, y, z] of tok) addToken(ctx, x, y, z);
      ctx.tokenStar = { id: 'legacy_tokens', x: 0, y: 1.6, z: 0 };
      // TWO ghost bugs now — it is a bigger library
      addBug(ctx, 0, -18, { ghost: true, speed: 3.2, scale: 1.6, gy: 1.2 });
      addBug(ctx, -20, 18, { ghost: true, speed: 2.6, scale: 1.3, gy: 1.0 });
      // candles
      for (const [cx2, cz2] of [[-13, 8], [15, -6], [5, 26], [-24, -24], [26, 20], [-30, 0]]) {
        cyl(scene, world, cx2, 0, cz2, 0.3, 1.6, new THREE.MeshLambertMaterial({ color: 0xe8e0c8 }), 6, false);
        const flame = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 5),
          new THREE.MeshLambertMaterial({ color: 0xffb028, emissive: 0xa06010 }));
        flame.position.set(cx2, 2.0, cz2); scene.add(flame);
        ctx.decor.push(t => { flame.scale.setScalar(1 + 0.25 * Math.sin(t * 9 + cx2)); });
        const l = new THREE.PointLight(0xffa030, 0.7, 16);
        l.position.set(cx2, 2.4, cz2); scene.add(l);
      }
      ctx.spawn = new THREE.Vector3(0, 0.3, 34);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- GROKIO'S TOWER (boss, bigger arena) ----------
  LVL.defs.boss = {
    name: "GROKIO'S TOWER", sub: 'the final compaction', song: 'boss',
    sky: [0x180810, 0x481018], fog: [0x381018, 40, 130],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x180810, 0x481018);
      world.terrain = null; world.killY = -10;
      const arenaM = mat(TEX.basalt, 10, 10);
      cyl(scene, world, 0, -2, 0, 21, 2, arenaM, 24);
      for (let i = 0; i < 10; i++) {
        const a = i / 10 * Math.PI * 2;
        const px = Math.cos(a) * 19, pz = Math.sin(a) * 19;
        cyl(scene, world, px, 0, pz, 0.95, 3.8, mat(TEX.castle, 2, 2), 7);
        const orb = new THREE.Mesh(new THREE.SphereGeometry(0.55, 8, 6),
          new THREE.MeshLambertMaterial({ color: 0xff5030, emissive: 0x701808 }));
        orb.position.set(px, 4.6, pz); scene.add(orb);
        ctx.decor.push(t => { orb.position.y = 4.6 + Math.sin(t * 2 + i) * 0.2; });
      }
      const flash = new THREE.AmbientLight(0x606080, 0);
      scene.add(flash);
      ctx.decor.push(t => { flash.intensity = (Math.sin(t * 0.5) > 0.985) ? 1.2 : 0; });
      const gk = CHARS.grokio();
      gk.position.set(0, 0, -10);
      scene.add(gk);
      ctx.boss = {
        mesh: gk, state: 'intro', t: 0, hits: 0, stun: 0,
        chargeDir: new THREE.Vector3(), pos: new THREE.Vector3(0, 0, -10), speed: 13,
      };
      ctx.fireballs = [];
      ctx.spawn = new THREE.Vector3(0, 0.3, 15);
      ctx.spawnYaw = Math.PI;
    }
  };
})();
