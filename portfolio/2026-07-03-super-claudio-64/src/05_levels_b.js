// ============ ICE + SKY + LEGACY + BOSS ============
(() => {
  const { mat, box, cyl, gaussTerrain, terrainMesh, skyDome, addStar, addToken, addBug } = LVL;

  // ---------- FROZEN CACHE ----------
  LVL.defs.ice = {
    name: 'FROZEN CACHE', sub: 'cold storage', song: 'ice',
    sky: [0x284868, 0x98c0e0], fog: [0x9cc0dc, 40, 110],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x284868, 0x98c0e0);
      const terr = gaussTerrain([[0, 0, 30, 0.8], [-24, -18, 12, 4.2], [20, -20, 14, 6.5], [22, 16, 10, 2.2]], 0);
      world.terrain = terr; world.killY = -20;
      terrainMesh(scene, terr, 100, 50, mat(TEX.snow, 20, 20));
      // frozen lake (slippery zone)
      const lake = new THREE.Mesh(new THREE.CylinderGeometry(13, 13, 0.3, 20), mat(TEX.ice, 8, 8));
      lake.position.set(-8, 0.95, 10); scene.add(lake);
      world.cyls.push({ x: -8, z: 10, r: 13, y0: -1, y1: 1.1 });
      ctx.iceZones = [{ x: -8, z: 10, r: 13, y: 1.1 }];
      // ice pillar stack (star 1)
      const steps = [[14, 2, -2, 2.2], [17, 3.4, -6, 2.0], [14, 4.8, -10, 1.8], [18, 6.4, -13, 1.6], [15, 8.2, -16, 1.5]];
      for (const [sx, sy, sz, sr] of steps) cyl(scene, world, sx, 0, sz, sr, sy + 0.4, mat(TEX.ice, 3, 2), 8);
      addStar(ctx, 'ice_pillar', 15, 10.2, -16);
      // the slide: long sloped ramp with token trail
      for (let i = 0; i < 9; i++) {
        const y = 7.5 - i * 0.85, z = -26 + i * 3.4;
        box(scene, world, -20, y, z, 5, 0.5, 3.8, mat(TEX.ice, 3, 2));
        if (i > 0) addToken(ctx, -20 + Math.sin(i * 1.3) * 1.2, y + 1.2, z);
      }
      ctx.iceZones.push({ box: [-23.5, -16.5, -28, 6], y: 8.2 }); // whole slide slippery
      ctx.tokenStar = { id: 'ice_tokens', x: -20, y: 2.4, z: 6 };
      // snowmen decor
      for (const [sx2, sz2] of [[6, 14], [-16, -8], [8, -12]]) {
        const gy = terr(sx2, sz2);
        const b1 = new THREE.Mesh(new THREE.SphereGeometry(1.1, 9, 7), mat(TEX.snow, 3, 3));
        b1.position.set(sx2, gy + 0.9, sz2); scene.add(b1);
        const b2 = new THREE.Mesh(new THREE.SphereGeometry(0.7, 8, 6), mat(TEX.snow, 2, 2));
        b2.position.set(sx2, gy + 2.1, sz2); scene.add(b2);
        const nose = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.5, 6),
          new THREE.MeshLambertMaterial({ color: 0xe87820 }));
        nose.rotation.x = -Math.PI / 2; nose.position.set(sx2, gy + 2.15, sz2 - 0.7); scene.add(nose);
      }
      addBug(ctx, 4, 4, { speed: 3.4 }); addBug(ctx, -4, 18, { speed: 3.0 }); addBug(ctx, 12, 10, {});
      ctx.spawn = new THREE.Vector3(2, terr(2, 26) + 0.3, 26);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- CONTEXT WINDOW (sky) ----------
  LVL.defs.sky = {
    name: 'CONTEXT WINDOW', sub: 'do not look down (it is compacted)', song: 'sky',
    sky: [0x3858c0, 0xb8d0f8], fog: [0xa8c0ec, 40, 120],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x3858c0, 0xb8d0f8);
      world.terrain = null; world.killY = -14;
      const cloudM = () => mat(TEX.cloud, 3, 3);
      const P = [
        [0, 0, 24, 7, 5], [0, 1, 12, 5, 4], [-8, 2.2, 2, 4, 4], [-14, 3.5, -8, 4, 3.5],
        [-6, 4.5, -16, 4, 3.5], [4, 5.5, -22, 4.5, 4], [14, 6.5, -16, 4, 3.5],
        [18, 7.5, -4, 5, 4], [10, 9, 4, 3.5, 3],
      ];
      P.forEach(([x, y, z, w, d], i) => {
        const b = box(scene, world, x, y, z, w, 0.9, d, cloudM());
        b.mesh.scale.y = 1; // puffy sides
        if (i > 0 && i < 8) addToken(ctx, x, y + 1.5, z);
      });
      ctx.tokenStar = { id: 'sky_tokens', x: 0, y: 2.4, z: 12 };
      // moving cloud to the far star
      const mv = box(scene, world, 2, 9.6, 12, 3.2, 0.7, 3.2, cloudM());
      ctx.movers.push({ b: mv, fn: t => [2 + Math.sin(t * 0.55) * 8, 9.6, 12 + Math.cos(t * 0.55) * 4] });
      box(scene, world, -10, 11, 18, 4, 0.9, 4, cloudM());
      addStar(ctx, 'sky_far', -10, 12.8, 18);
      // wind zone between platforms 5-7 (pushes +x)
      ctx.windZones = [{ x0: -2, x1: 10, z0: -26, z1: -12, fx: 5.5, fz: 0 }];
      // decorative birds (triangles orbiting)
      for (let i = 0; i < 4; i++) {
        const bird = new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.9, 4),
          new THREE.MeshLambertMaterial({ color: 0xffffff }));
        bird.rotation.z = Math.PI / 2; scene.add(bird);
        ctx.decor.push(t => {
          const a = t * 0.4 + i * 1.6;
          bird.position.set(Math.cos(a) * 24, 8 + Math.sin(t + i) * 2, Math.sin(a) * 24);
        });
      }
      ctx.spawn = new THREE.Vector3(0, 8.5, 26);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- LEGACY CODEBASE ----------
  LVL.defs.legacy = {
    name: 'LEGACY CODEBASE', sub: 'nobody remembers why this works', song: 'legacy',
    sky: [0x100c1c, 0x241c30], fog: [0x181226, 14, 55],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x100c1c, 0x241c30);
      world.killY = -15;
      box(scene, world, 0, -1, 0, 56, 1, 56, mat(TEX.wood, 14, 14));
      const shelfM = () => mat(TEX.books, 3, 2);
      // shelf maze walls (tall bookcases)
      const shelves = [
        [0, -10, 20, 5], [-14, 2, 4, 7], [14, 2, 4, 7], [0, 8, 12, 4.5],
        [-8, 18, 10, 6], [10, 16, 8, 5], [-20, -12, 6, 8], [20, -12, 6, 8],
        [0, -22, 30, 6],
      ];
      for (const [x, z, w, h] of shelves) box(scene, world, x, 0, z, w, h, 2.2, shelfM());
      // stacked book platforms up the tall shelf
      const bookM = c => new THREE.MeshLambertMaterial({ color: c });
      const stack = [[-17, 1.2, -8, 0x8a3030], [-14, 2.6, -5, 0x30608a], [-11, 4.0, -8, 0x3a7a3a],
                     [-8, 5.4, -11, 0x8a7a30], [-5, 6.8, -8, 0x6a3a8a]];
      for (const [x, y, z, c] of stack) box(scene, world, x, y, z, 2.6, 0.5, 1.8, bookM(c));
      addStar(ctx, 'legacy_top', 0, 9.4, -10); // on the big central shelf... reachable from stack
      box(scene, world, -2, 7.6, -10, 3, 0.5, 2, bookM(0xa05828));
      // tokens through the maze
      const tok = [[-14, 1.2, 10], [14, 1.2, 10], [0, 1.2, 14], [-8, 7.2, 18], [10, 6.2, 16],
                   [-20, 9.2, -12], [20, 9.2, -12], [0, 7.2, -22]];
      for (const [x, y, z] of tok) addToken(ctx, x, y, z);
      ctx.tokenStar = { id: 'legacy_tokens', x: 0, y: 1.6, z: 0 };
      // THE GHOST BUG (only moves when you're not looking)
      addBug(ctx, 0, -14, { ghost: true, speed: 3.2, scale: 1.6, gy: 1.2 });
      // candles
      for (const [cx2, cz2] of [[-10, 6], [12, -4], [4, 20], [-18, -18]]) {
        const cd = cyl(scene, world, cx2, 0, cz2, 0.3, 1.6, new THREE.MeshLambertMaterial({ color: 0xe8e0c8 }), 6, false);
        const flame = new THREE.Mesh(new THREE.SphereGeometry(0.22, 6, 5),
          new THREE.MeshLambertMaterial({ color: 0xffb028, emissive: 0xa06010 }));
        flame.position.set(cx2, 2.0, cz2); scene.add(flame);
        ctx.decor.push(t => { flame.scale.setScalar(1 + 0.25 * Math.sin(t * 9 + cx2)); });
        const l = new THREE.PointLight(0xffa030, 0.7, 14);
        l.position.set(cx2, 2.4, cz2); scene.add(l);
      }
      ctx.spawn = new THREE.Vector3(0, 0.3, 26);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- GROKIO'S TOWER (boss) ----------
  LVL.defs.boss = {
    name: "GROKIO'S TOWER", sub: 'the final compaction', song: 'boss',
    sky: [0x180810, 0x481018], fog: [0x381018, 35, 110],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x180810, 0x481018);
      world.terrain = null; world.killY = -10;
      // circular arena
      const arenaM = mat(TEX.basalt, 8, 8);
      cyl(scene, world, 0, -2, 0, 17, 2, arenaM, 22);
      // rim + pylons
      for (let i = 0; i < 8; i++) {
        const a = i / 8 * Math.PI * 2;
        const px = Math.cos(a) * 15.2, pz = Math.sin(a) * 15.2;
        cyl(scene, world, px, 0, pz, 0.9, 3.6, mat(TEX.castle, 2, 2), 7);
        const orb = new THREE.Mesh(new THREE.SphereGeometry(0.55, 8, 6),
          new THREE.MeshLambertMaterial({ color: 0xff5030, emissive: 0x701808 }));
        orb.position.set(px, 4.4, pz); scene.add(orb);
        ctx.decor.push(t => { orb.position.y = 4.4 + Math.sin(t * 2 + i) * 0.2; });
      }
      // lightning sky flicker
      const flash = new THREE.AmbientLight(0x606080, 0);
      scene.add(flash);
      ctx.decor.push(t => { flash.intensity = (Math.sin(t * 0.5) > 0.985) ? 1.2 : 0; });
      // grokio
      const gk = CHARS.grokio();
      gk.position.set(0, 0, -8);
      scene.add(gk);
      ctx.boss = {
        mesh: gk, state: 'intro', t: 0, hits: 0, stun: 0,
        chargeDir: new THREE.Vector3(), pos: new THREE.Vector3(0, 0, -8), speed: 13,
      };
      ctx.fireballs = [];
      ctx.spawn = new THREE.Vector3(0, 0.3, 12);
      ctx.spawnYaw = Math.PI;
    }
  };
})();
