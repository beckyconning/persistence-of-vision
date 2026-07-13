// ============ LEVEL HELPERS + LOBBY + MEADOWS + LAVA ============
const LVL = (() => {
  function mat(tex, rx = 1, ry = 1, opts = {}) {
    const t = tex.clone(); t.needsUpdate = true; t.repeat.set(rx, ry);
    return new THREE.MeshLambertMaterial(Object.assign({ map: t }, opts));
  }
  function box(scene, world, x, y, z, w, h, d, m, solid = true) {
    const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, d), m);
    mesh.position.set(x, y + h / 2, z);
    scene.add(mesh);
    const b = { x0: x - w / 2, x1: x + w / 2, y0: y, y1: y + h, z0: z - d / 2, z1: z + d / 2, mesh };
    if (solid) world.boxes.push(b);
    return b;
  }
  function cyl(scene, world, x, y, z, r, h, m, seg = 10, solid = true) {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(r, r, h, seg), m);
    mesh.position.set(x, y + h / 2, z);
    scene.add(mesh);
    if (solid) world.cyls.push({ x, z, r, y0: y, y1: y + h, mesh });
    return mesh;
  }
  function cone(scene, x, y, z, r, h, color) {
    const mesh = new THREE.Mesh(new THREE.CylinderGeometry(0.05, r, h, 10),
      new THREE.MeshLambertMaterial({ color }));
    mesh.position.set(x, y + h / 2, z);
    scene.add(mesh);
    return mesh;
  }
  function gaussTerrain(hills, base = 0) {
    return (x, z) => {
      let y = base;
      for (const [hx, hz, r, h] of hills) {
        const d2 = ((x - hx) ** 2 + (z - hz) ** 2) / (r * r);
        y += h * Math.exp(-d2);
      }
      return y;
    };
  }
  function terrainMesh(scene, fn, size, seg, m) {
    const geo = new THREE.PlaneGeometry(size, size, seg, seg);
    geo.rotateX(-Math.PI / 2);
    const pos = geo.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      pos.setY(i, fn(pos.getX(i), pos.getZ(i)));
    }
    geo.computeVertexNormals();
    const mesh = new THREE.Mesh(geo, m);
    scene.add(mesh);
    return mesh;
  }
  function tree(scene, world, x, z, gy, s = 1) {
    cyl(scene, world, x, gy, z, 0.35 * s, 2.4 * s, mat(TEX.wood, 1, 2));
    const leaves = new THREE.Mesh(new THREE.SphereGeometry(1.5 * s, 8, 6),
      new THREE.MeshLambertMaterial({ color: 0x3f8c2c }));
    leaves.position.set(x, gy + 3.1 * s, z); leaves.scale.y = 0.85;
    scene.add(leaves);
  }
  function skyDome(scene, top, bottom) {
    const geo = new THREE.SphereGeometry(300, 16, 10);
    const cols = [];
    const pos = geo.attributes.position;
    const cT = new THREE.Color(top), cB = new THREE.Color(bottom);
    for (let i = 0; i < pos.count; i++) {
      const t = Math.max(0, Math.min(1, pos.getY(i) / 220 + 0.35));
      const c = cB.clone().lerp(cT, t);
      cols.push(c.r, c.g, c.b);
    }
    geo.setAttribute('color', new THREE.Float32BufferAttribute(cols, 3));
    const m = new THREE.MeshBasicMaterial({ vertexColors: true, side: THREE.BackSide, fog: false });
    scene.add(new THREE.Mesh(geo, m));
  }
  function addStar(ctx, id, x, y, z, hidden = false) {
    const s = CHARS.star();
    s.position.set(x, y, z);
    s.visible = !hidden && !GAME.save.stars[id];
    ctx.scene.add(s);
    ctx.stars.push({ id, mesh: s, x, y, z, hidden });
    return s;
  }
  function addToken(ctx, x, y, z) {
    const t = CHARS.token();
    t.position.set(x, y, z);
    ctx.scene.add(t);
    ctx.tokens.push({ mesh: t, got: false });
  }
  function addBug(ctx, x, z, opts = {}) {
    const b = CHARS.bug(opts.scale || 1, opts.ghost);
    ctx.scene.add(b);
    ctx.enemies.push({
      mesh: b, x, z, home: [x, z], t: Math.random() * 7, dead: 0,
      speed: opts.speed || 2.2, radius: opts.radius || 5, ghost: !!opts.ghost, gy: opts.gy,
    });
  }

  // ---------- LOBBY ----------
  const PAINTINGS = [
    { id: 'meadow', name: 'TOKEN MEADOWS', tex: () => TEX.paint_meadow, need: 0 },
    { id: 'lava', name: 'COMPACTION CORE', tex: () => TEX.paint_lava, need: 1 },
    { id: 'ice', name: 'FROZEN CACHE', tex: () => TEX.paint_ice, need: 2 },
    { id: 'sky', name: 'CONTEXT WINDOW', tex: () => TEX.paint_sky, need: 3 },
    { id: 'legacy', name: 'LEGACY CODEBASE', tex: () => TEX.paint_legacy, need: 4 },
  ];

  const lobby = {
    name: 'CASTLE CLAUDIO', sub: 'lobby', song: 'lobby',
    sky: [0x88b8f0, 0xd8ecff], fog: [0xc8b8a0, 30, 90],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x88b8f0, 0xd8ecff);
      world.killY = -20;
      // floor
      box(scene, world, 0, -1, 0, 44, 1, 34, mat(TEX.checker, 11, 8));
      box(scene, world, 0, 0, -3, 6, 0.12, 26, mat(TEX.carpet, 1, 6));
      // walls (south wall has the exit-door gap)
      const wallM = mat(TEX.castle, 8, 3);
      box(scene, world, 0, 0, -17.5, 44, 12, 1, wallM);
      box(scene, world, -13.2, 0, 17.5, 17.6, 12, 1, wallM);
      box(scene, world, 13.2, 0, 17.5, 17.6, 12, 1, wallM);
      box(scene, world, 0, 6.5, 17.5, 9, 5.5, 1, wallM);
      box(scene, world, -22.5, 0, 0, 1, 12, 35, mat(TEX.castle, 6, 3));
      box(scene, world, 22.5, 0, 0, 1, 12, 35, mat(TEX.castle, 6, 3));
      box(scene, world, 0, 11.5, 0, 46, 1, 36, new THREE.MeshLambertMaterial({ color: 0x8a7660 }), false);
      // columns
      for (const sx of [-1, 1]) for (const sz of [-1, 1])
        cyl(scene, world, sx * 14, 0, sz * 9, 1.1, 11, mat(TEX.castle, 2, 3), 8);
      // back staircase to boss door
      for (let i = 0; i < 5; i++)
        box(scene, world, 0, i * 0.55, -12.5 - i * 1.1, 14 - i * 1.2, 0.55, 1.4, mat(TEX.castle, 4, 1));
      box(scene, world, 0, 2.75, -16.4, 10, 0.55, 2.5, mat(TEX.carpet, 3, 1));
      // BOSS DOOR
      const door = new THREE.Mesh(new THREE.BoxGeometry(4.4, 6.2, 0.4), mat(TEX.door, 1, 1));
      door.position.set(0, 6.3, -16.9); scene.add(door);
      ctx.bossDoor = { x: 0, z: -16.4, y: 3.3, need: 6 };
      const starIcon = CHARS.star(); starIcon.scale.setScalar(0.7);
      starIcon.position.set(0, 10, -16.6); scene.add(starIcon);
      ctx.decor.push(t => { starIcon.rotation.y = t; });
      // EXIT DOOR to the castle grounds (south)
      const exdoor = new THREE.Mesh(new THREE.BoxGeometry(4.2, 6.5, 0.4), mat(TEX.door, 1, 1));
      exdoor.position.set(0, 3.2, 17.2); scene.add(exdoor);
      ctx.exitDoor = { x: 0, z: 16.9 };
      // paintings
      const spots = [
        [-21.9, 3.9, -6, Math.PI / 2], [-21.9, 3.9, 7, Math.PI / 2],
        [21.9, 3.9, -6, -Math.PI / 2], [21.9, 3.9, 7, -Math.PI / 2],
        [-8.5, 4.6, -17, 0],
      ];
      ctx.paintings = [];
      PAINTINGS.forEach((p, i) => {
        const [px, py, pz, ry] = spots[i];
        const frame = new THREE.Mesh(new THREE.BoxGeometry(6.6, 5.2, 0.3),
          new THREE.MeshLambertMaterial({ color: 0xb08828 }));
        frame.position.set(px, py, pz); frame.rotation.y = ry; scene.add(frame);
        const art = new THREE.Mesh(new THREE.PlaneGeometry(5.8, 4.4),
          new THREE.MeshBasicMaterial({ map: p.tex() }));
        art.position.set(px, py, pz); art.rotation.y = ry;
        art.translateZ(0.18);
        scene.add(art);
        ctx.paintings.push({ def: p, x: px, y: py, z: pz, ry, art });
        ctx.decor.push(t => { art.position.y = py + Math.sin(t * 1.7 + i) * 0.05; });
      });
      // secret lobby star on a ledge above the door
      box(scene, world, 8, 7.5, -16, 3, 0.5, 2.5, mat(TEX.castle, 1, 1));
      addStar(ctx, 'lobby_secret', 8, 9, -16);
      ctx.spawn = new THREE.Vector3(0, 0.2, 13);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- TOKEN MEADOWS (enlarged) ----------
  const MX = 12, MZ = -44;   // the mountain
  const meadow = {
    name: 'TOKEN MEADOWS', sub: 'a suspiciously cheerful place', song: 'meadow',
    sky: [0x68a8f0, 0xc8e8ff], fog: [0xb8d8f0, 55, 190],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x68a8f0, 0xc8e8ff);
      const terr = gaussTerrain([
        [0, 0, 34, 1.3], [-32, -20, 15, 3.6], [34, 12, 18, 3.0],
        [MX, MZ, 19, 13.5],           // THE MOUNTAIN
        [-24, 32, 13, 2.4], [30, -30, 12, 2.2], [-38, 6, 10, 2.8],
      ], 0);
      world.terrain = terr;
      world.killY = -25;
      terrainMesh(scene, terr, 150, 72, mat(TEX.grass, 30, 30));
      // mountain spiral platforms
      for (let i = 0; i < 9; i++) {
        const a = i * 0.92 + 0.6, r = 13.5 - i * 0.95;
        const x = MX + Math.cos(a) * r, z = MZ + Math.sin(a) * r;
        const y = 2.6 + i * 1.5;
        box(scene, world, x, y, z, 3.6, 0.6, 3.6, mat(TEX.brickTop, 2, 2));
      }
      addStar(ctx, 'meadow_peak', MX, terr(MX, MZ) + 1.6, MZ);
      // trees
      for (const [tx, tz, ts] of [[-14, 10, 1], [20, 20, 1.3], [-28, -6, 0.9], [30, -12, 1],
                                   [-8, 28, 1.1], [38, 2, 0.9], [-34, 20, 1.2], [8, -16, 0.8],
                                   [-20, -30, 1], [44, 22, 1.1]])
        tree(scene, world, tx, tz, terr(tx, tz), ts);
      // floating ring of platforms with tokens (wider)
      for (let i = 0; i < 8; i++) {
        const a = i / 8 * Math.PI * 2;
        const x = Math.cos(a) * 22, z = 8 + Math.sin(a) * 22;
        if (i % 2 === 0) box(scene, world, x, terr(x, z) + 2.4, z, 2.8, 0.5, 2.8, mat(TEX.brickTop, 2, 2));
        addToken(ctx, x, terr(x, z) + (i % 2 === 0 ? 3.9 : 1.2), z);
      }
      ctx.tokenStar = { id: 'meadow_tokens', x: 0, y: terr(0, 8) + 2, z: 8 };
      // a lake
      const lake = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 0.25, 18),
        new THREE.MeshLambertMaterial({ color: 0x4088c8, transparent: true, opacity: 0.85 }));
      lake.position.set(-32, 0.5, 24); scene.add(lake);
      // bugs
      addBug(ctx, -8, -10); addBug(ctx, 22, -4); addBug(ctx, -26, 18, { speed: 2.8 });
      addBug(ctx, 6, 24, { radius: 7 }); addBug(ctx, 36, 16, {}); addBug(ctx, -16, -24, { speed: 3 });
      ctx.spawn = new THREE.Vector3(0, terr(0, 34) + 0.3, 34);
      ctx.spawnYaw = Math.PI;
    }
  };

  // ---------- COMPACTION CORE (enlarged) ----------
  const lava = {
    name: 'COMPACTION CORE', sub: 'where deleted context goes', song: 'lava',
    sky: [0x28080c, 0x701818], fog: [0x501010, 40, 130],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x28080c, 0x701818);
      world.killY = -12;
      const lavaMesh = new THREE.Mesh(new THREE.PlaneGeometry(240, 240, 1, 1), mat(TEX.lava, 38, 38));
      lavaMesh.rotation.x = -Math.PI / 2; lavaMesh.position.y = -2;
      scene.add(lavaMesh);
      ctx.lavaY = -1.6;
      ctx.decor.push(t => { lavaMesh.material.map.offset.set(Math.sin(t * 0.25) * 0.1, t * 0.015); });
      const bas = () => mat(TEX.basalt, 3, 3);
      // islands (a longer archipelago)
      box(scene, world, 0, -1, 26, 14, 1.4, 12, bas());
      box(scene, world, 0, -1, 6, 7, 1.2, 7, bas());
      box(scene, world, -16, -0.8, -4, 8, 1.2, 8, bas());
      box(scene, world, 16, -0.6, -8, 8, 1.4, 8, bas());
      box(scene, world, -8, -0.7, -22, 7, 1.3, 7, bas());
      box(scene, world, 10, -0.5, -30, 7, 1.4, 7, bas());
      box(scene, world, 0, -0.4, -44, 12, 1.7, 10, bas());
      // moving platforms
      const mv1 = box(scene, world, -8, 0.4, -12, 3.4, 0.5, 3.4, mat(TEX.basalt, 2, 2));
      const mv2 = box(scene, world, 10, 0.6, -18, 3.4, 0.5, 3.4, mat(TEX.basalt, 2, 2));
      const mv3 = box(scene, world, 0, 0.8, -36, 3.4, 0.5, 3.4, mat(TEX.basalt, 2, 2));
      ctx.movers.push({ b: mv1, fn: t => [-8 + Math.sin(t * 0.7) * 7, 0.4, -12] });
      ctx.movers.push({ b: mv2, fn: t => [10, 0.6 + Math.sin(t * 0.9) * 1.8 + 1.8, -18 + Math.cos(t * 0.7) * 5] });
      ctx.movers.push({ b: mv3, fn: t => [Math.sin(t * 0.6) * 8, 0.8, -36] });
      // crates to pound
      ctx.crates = [];
      for (const [cx, cz, island] of [[-16, -4, 0.4], [16, -8, 0.8], [3, 26, 0.4]]) {
        const c = box(scene, world, cx, island, cz, 2, 2, 2, mat(TEX.wood, 2, 2));
        ctx.crates.push({ b: c, broken: false });
      }
      ctx.crateStar = { id: 'lava_crates', x: 0, y: 1.6, z: 6 };
      addStar(ctx, 'lava_far', 0, 1.9, -44);
      // bubbling spouts
      for (const [bx, bz] of [[-26, 10], [24, 6], [8, -48], [-8, 34], [-30, -20], [30, -28]]) {
        const bub = new THREE.Mesh(new THREE.SphereGeometry(0.8, 7, 5),
          new THREE.MeshLambertMaterial({ color: 0xff7818, emissive: 0x802000 }));
        bub.position.set(bx, -1.6, bz); scene.add(bub);
        ctx.decor.push(t => {
          const c = (t * 0.7 + bx * 0.13) % 1;
          bub.position.y = -2 + c * 3; bub.scale.setScalar(1 - c * 0.7);
        });
      }
      ctx.spawn = new THREE.Vector3(0, 1, 29);
      ctx.spawnYaw = Math.PI;
    }
  };

  return { mat, box, cyl, cone, gaussTerrain, terrainMesh, tree, skyDome, addStar, addToken, addBug, PAINTINGS, defs: { lobby, meadow, lava } };
})();
