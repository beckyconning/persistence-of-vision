// ============ CASTLE GROUNDS (the outside) ============
(() => {
  const { mat, box, cyl, cone, gaussTerrain, terrainMesh, tree, skyDome, addStar } = LVL;

  LVL.defs.outside = {
    name: 'CASTLE GROUNDS', sub: 'welcome to a castle claudio', song: 'lobby',
    sky: [0x78b0f0, 0xd0e8ff], fog: [0xc0d8f0, 60, 200],
    build(ctx) {
      const { scene, world } = ctx;
      skyDome(scene, 0x78b0f0, 0xd0e8ff);
      const terr = gaussTerrain([
        [0, 40, 40, 0.8], [-40, 20, 16, 3.4], [42, 26, 18, 3.8],
        [-30, -34, 14, 4.5], [34, -38, 14, 5.0], [0, 70, 24, 2.2],
      ], 0);
      world.terrain = terr;
      world.killY = -25;
      terrainMesh(scene, terr, 170, 76, mat(TEX.grass, 34, 34));

      // ---- the castle (north) ----
      const castleM = () => mat(TEX.castle, 6, 4);
      // moat
      const moat = new THREE.Mesh(new THREE.PlaneGeometry(64, 10),
        new THREE.MeshLambertMaterial({ color: 0x3878c0, transparent: true, opacity: 0.9 }));
      moat.rotation.x = -Math.PI / 2; moat.position.set(0, 0.25, -16); scene.add(moat);
      // main keep
      box(scene, world, 0, 0, -34, 34, 15, 16, mat(TEX.castle, 10, 5));
      // battlement roof rim
      for (let i = -4; i <= 4; i++) box(scene, world, i * 4, 15, -27.2, 2, 1.4, 1.4, castleM());
      // door alcove front face
      box(scene, world, -9.6, 0, -25.4, 14.8, 15, 1.6, mat(TEX.castle, 5, 5));
      box(scene, world, 9.6, 0, -25.4, 14.8, 15, 1.6, mat(TEX.castle, 3, 3));
      box(scene, world, 0, 6.8, -25.4, 4.4, 8.2, 1.6, mat(TEX.castle, 2, 3));
      const door = new THREE.Mesh(new THREE.BoxGeometry(4.4, 6.6, 0.5), mat(TEX.door, 1, 1));
      door.position.set(0, 3.3, -24.5); scene.add(door);
      ctx.castleDoor = { x: 0, z: -24.9 };
      // star emblem above the door
      const starIcon = CHARS.star(); starIcon.scale.setScalar(1.1);
      starIcon.position.set(0, 9.4, -24.6); scene.add(starIcon);
      ctx.decor.push(t => { starIcon.rotation.y = t * 0.8; });
      // towers + cone roofs
      for (const sx of [-1, 1]) {
        cyl(scene, world, sx * 19, 0, -30, 4.2, 20, mat(TEX.castle, 4, 6), 10);
        cone(scene, sx * 19, 20, -30, 5.2, 7, 0xb03028);
        cyl(scene, world, sx * 9, 0, -40, 3.2, 24, mat(TEX.castle, 3, 7), 9);
        cone(scene, sx * 9, 24, -40, 4.0, 6.5, 0xb03028);
      }
      // central spire
      cyl(scene, world, 0, 15, -36, 3.4, 8, mat(TEX.castle, 3, 3), 9);
      cone(scene, 0, 23, -36, 4.4, 7.5, 0xb03028);
      // bridge over the moat
      box(scene, world, 0, 0.35, -16, 7, 0.7, 12, mat(TEX.wood, 3, 4));
      for (const sx of [-1, 1]) {
        box(scene, world, sx * 3.2, 1.0, -16, 0.5, 0.9, 12, mat(TEX.wood, 1, 4));
      }
      // climb to the roof: crates behind the east tower -> tower ledge -> roof
      box(scene, world, 26, 0, -36, 3, 2.2, 3, mat(TEX.wood, 2, 2));
      box(scene, world, 24, 0, -41, 3, 4.6, 3, mat(TEX.wood, 2, 3));
      box(scene, world, 21, 0, -45.5, 3, 7.2, 3, mat(TEX.wood, 2, 3));
      box(scene, world, 16, 0, -44, 3.4, 10.4, 3.4, castleM());
      box(scene, world, 10, 0, -41, 3.2, 13, 3.2, castleM());
      // roof star (on the keep roof)
      addStar(ctx, 'roof_star', 0, 16.8, -34);

      // ---- grounds decor ----
      for (const [tx, tz, ts] of [[-16, 8, 1.1], [17, 6, 1], [-26, 24, 1.3], [28, 18, 1.1],
                                   [-42, -6, 1], [44, -2, 1.2], [-10, 42, 1], [12, 46, 1.2],
                                   [-34, 44, 0.9], [36, 44, 1]])
        tree(scene, world, tx, tz, terr(tx, tz), ts);
      // hedges lining the path
      for (let i = 0; i < 5; i++) {
        for (const sx of [-1, 1]) {
          const h = new THREE.Mesh(new THREE.BoxGeometry(2.4, 1.4, 4),
            new THREE.MeshLambertMaterial({ color: 0x2f7a24 }));
          const hz = -6 + i * 8;
          h.position.set(sx * 6.5, terr(sx * 6.5, hz) + 0.7, hz);
          scene.add(h);
        }
      }
      // flowers (tiny bright boxes)
      const fl = new THREE.Group(); scene.add(fl);
      const cols = [0xffe040, 0xff6080, 0xffffff, 0xff9040];
      for (let i = 0; i < 40; i++) {
        const fx = (Math.sin(i * 127.1) * 43758.5453 % 1) * 90 - 45;
        const fz = (Math.sin(i * 311.7) * 12543.21 % 1) * 70 - 20;
        const f = new THREE.Mesh(new THREE.BoxGeometry(0.3, 0.3, 0.3),
          new THREE.MeshLambertMaterial({ color: cols[i % 4] }));
        f.position.set(fx, terr(fx, fz) + 0.35, fz);
        fl.add(f);
      }
      // butterflies
      for (let i = 0; i < 3; i++) {
        const b = new THREE.Mesh(new THREE.BoxGeometry(0.35, 0.08, 0.3),
          new THREE.MeshLambertMaterial({ color: 0xffd23c }));
        scene.add(b);
        ctx.decor.push(t => {
          const a = t * 0.7 + i * 2.1;
          b.position.set(Math.cos(a) * (10 + i * 6), 2 + Math.sin(t * 3 + i) * 0.8,
            10 + Math.sin(a * 0.8) * 14);
          b.rotation.y = a;
        });
      }
      ctx.spawn = new THREE.Vector3(0, terr(0, 30) + 0.3, 30);
      ctx.spawnYaw = Math.PI;
    }
  };
})();
