// ============ CHARACTERS: Claudio, Grokio, bugs ============
const CHARS = (() => {
  function lam(color) { return new THREE.MeshLambertMaterial({ color }); }

  function buildPlumber(pal) {
    const g = new THREE.Group();
    const J = {};
    const M = {
      cap: lam(pal.cap), shirt: lam(pal.shirt), overalls: lam(pal.overalls),
      skin: lam(pal.skin), glove: lam(pal.glove), shoe: lam(pal.shoe),
      stache: lam(pal.stache), eye: lam(0xffffff), pupil: lam(pal.pupil), gold: lam(pal.button),
    };
    // legs
    for (const [nm, sx] of [['hipL', -1], ['hipR', 1]]) {
      const hip = new THREE.Group(); hip.position.set(sx * 0.22, 0.72, 0); g.add(hip); J[nm] = hip;
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.17, 0.15, 0.55, 7), M.overalls);
      leg.position.y = -0.28; hip.add(leg);
      const shoe = new THREE.Mesh(new THREE.SphereGeometry(0.22, 7, 5), M.shoe);
      shoe.scale.set(1, 0.62, 1.35); shoe.position.set(0, -0.58, 0.08); hip.add(shoe);
    }
    // torso
    const torso = new THREE.Group(); torso.position.y = 0.85; g.add(torso); J.torso = torso;
    const belly = new THREE.Mesh(new THREE.SphereGeometry(0.58, 10, 8), M.overalls);
    belly.scale.set(1, 0.85, 0.88); belly.position.y = 0.15; torso.add(belly);
    const chest = new THREE.Mesh(new THREE.SphereGeometry(0.5, 10, 8), M.shirt);
    chest.scale.set(1, 0.75, 0.85); chest.position.y = 0.52; torso.add(chest);
    const bib = new THREE.Mesh(new THREE.BoxGeometry(0.46, 0.34, 0.1), M.overalls);
    bib.position.set(0, 0.55, -0.38); torso.add(bib);
    for (const sx of [-1, 1]) {
      const btn = new THREE.Mesh(new THREE.SphereGeometry(0.065, 6, 5), M.gold);
      btn.position.set(sx * 0.14, 0.62, -0.44); torso.add(btn);
    }
    // arms
    for (const [nm, sx] of [['shL', -1], ['shR', 1]]) {
      const sh = new THREE.Group(); sh.position.set(sx * 0.54, 0.62, 0); torso.add(sh); J[nm] = sh;
      const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.12, 0.5, 7), M.shirt);
      arm.position.y = -0.26; arm.rotation.z = -sx * 0.2; sh.add(arm);
      const hand = new THREE.Mesh(new THREE.SphereGeometry(0.19, 7, 5), M.glove);
      hand.position.set(sx * 0.1, -0.55, 0); sh.add(hand);
    }
    // head
    const head = new THREE.Group(); head.position.y = 1.02; torso.add(head); J.head = head;
    const skull = new THREE.Mesh(new THREE.SphereGeometry(0.55, 11, 9), M.skin);
    skull.position.y = 0.08; head.add(skull);
    const nose = new THREE.Mesh(new THREE.SphereGeometry(0.19, 8, 6), M.skin);
    nose.position.set(0, -0.02, -0.55); head.add(nose);
    for (const sx of [-1, 1]) {
      const ear = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 5), M.skin);
      ear.position.set(sx * 0.54, 0.03, 0); head.add(ear);
      const stp = new THREE.Mesh(new THREE.SphereGeometry(0.21, 8, 5), M.stache);
      stp.scale.set(1, 0.4, 0.55); stp.position.set(sx * 0.17, -0.19, -0.5);
      stp.rotation.z = pal.evil ? sx * 0.45 : -sx * 0.12; head.add(stp);
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.13, 7, 6), M.eye);
      eye.scale.set(1, 1.25, 0.7); eye.position.set(sx * 0.19, 0.2, -0.45); head.add(eye);
      const pup = new THREE.Mesh(new THREE.SphereGeometry(0.06, 6, 5), M.pupil);
      pup.position.set(sx * 0.18, 0.19, -0.55); head.add(pup);
      if (pal.evil) {
        const brow = new THREE.Mesh(new THREE.BoxGeometry(0.28, 0.07, 0.08), M.stache);
        brow.position.set(sx * 0.19, 0.38, -0.47); brow.rotation.z = sx * 0.5; head.add(brow);
      }
      const burn = new THREE.Mesh(new THREE.SphereGeometry(0.12, 6, 5), M.stache);
      burn.position.set(sx * 0.45, 0.02, -0.15); head.add(burn);
    }
    const backhair = new THREE.Mesh(new THREE.SphereGeometry(0.38, 8, 6), M.stache);
    backhair.scale.set(1, 0.6, 0.8); backhair.position.set(0, 0.05, 0.3); head.add(backhair);
    // cap
    const dome = new THREE.Mesh(new THREE.SphereGeometry(0.62, 10, 7), M.cap);
    dome.scale.set(1, 0.62, 1); dome.position.y = 0.42; head.add(dome);
    const brim = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.07, 10), M.cap);
    brim.scale.set(1.05, 1, 1.3); brim.position.set(0, 0.34, -0.5); head.add(brim);
    const emb = new THREE.Mesh(new THREE.CylinderGeometry(0.15, 0.15, 0.06, 8), lam(0xf5f2e8));
    emb.rotation.x = Math.PI / 2 - 0.5; emb.position.set(0, 0.55, -0.52); head.add(emb);
    for (const rz of [0, Math.PI / 2]) {
      const slat = new THREE.Mesh(new THREE.BoxGeometry(0.05, 0.2, 0.04), M.cap);
      slat.rotation.set(-0.5, 0, rz + (pal.evil ? Math.PI / 4 : 0));
      slat.position.set(0, 0.56, -0.55); head.add(slat);
    }
    g.userData.joints = J;
    return g;
  }

  const CLAUDIO_PAL = {
    cap: 0xeb7630, shirt: 0xd97757, overalls: 0x604232, skin: 0xf7cda5,
    glove: 0xf8f6f0, shoe: 0x4a3226, stache: 0x38261c, pupil: 0x28203c, button: 0xfac83c,
  };
  const GROKIO_PAL = {
    cap: 0x26242a, shirt: 0x96282e, overalls: 0x34323a, skin: 0xe8be96,
    glove: 0x1e1c22, shoe: 0x1c1a1e, stache: 0x181410, pupil: 0xc81e1e, button: 0xc8c8d2,
    evil: true,
  };

  function buildBug(scale = 1, ghost = false) {
    const g = new THREE.Group();
    const bodyM = new THREE.MeshLambertMaterial({
      color: ghost ? 0xbfaaff : 0x965cbe, transparent: ghost, opacity: ghost ? 0.55 : 1,
    });
    const darkM = new THREE.MeshLambertMaterial({
      color: 0x5a3278, transparent: ghost, opacity: ghost ? 0.5 : 1,
    });
    const body = new THREE.Mesh(new THREE.SphereGeometry(0.62, 9, 7), bodyM);
    body.scale.set(1, 0.78, 1.1); body.position.y = 0.5; g.add(body);
    for (const sx of [-1, 1]) {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.17, 7, 5), lam(0xffffff));
      eye.position.set(sx * 0.22, 0.72, -0.48); g.add(eye);
      const pup = new THREE.Mesh(new THREE.SphereGeometry(0.075, 5, 4), lam(0x201430));
      pup.position.set(sx * 0.2, 0.7, -0.62); g.add(pup);
      const ant = new THREE.Mesh(new THREE.BoxGeometry(0.06, 0.5, 0.06), darkM);
      ant.position.set(sx * 0.18, 1.05, -0.3); ant.rotation.z = -sx * 0.3; g.add(ant);
      for (let i = 0; i < 3; i++) {
        const leg = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.45, 0.1), darkM);
        leg.position.set(sx * 0.6, 0.28, -0.35 + i * 0.35);
        leg.rotation.z = -sx * 0.55; g.add(leg);
        if (!g.userData.legs) g.userData.legs = [];
        g.userData.legs.push(leg);
      }
    }
    g.scale.setScalar(scale);
    return g;
  }

  function buildStar() {
    const g = new THREE.Group();
    const m = new THREE.MeshLambertMaterial({ color: 0xffd23c, emissive: 0x8a6a10 });
    const shape = new THREE.Shape();
    for (let i = 0; i < 10; i++) {
      const a = i * Math.PI / 5 - Math.PI / 2;
      const r = i % 2 === 0 ? 0.62 : 0.27;
      if (i === 0) shape.moveTo(Math.cos(a) * r, Math.sin(a) * r);
      else shape.lineTo(Math.cos(a) * r, Math.sin(a) * r);
    }
    const geo = new THREE.ExtrudeGeometry(shape, { depth: 0.18, bevelEnabled: false });
    const star = new THREE.Mesh(geo, m);
    star.position.z = -0.09; g.add(star);
    for (const sx of [-1, 1]) {
      const e = new THREE.Mesh(new THREE.SphereGeometry(0.07, 5, 4), lam(0x201830));
      e.position.set(sx * 0.12, 0.16, 0.12); g.add(e);
    }
    return g;
  }

  function buildToken() {
    const m = new THREE.MeshLambertMaterial({ color: 0xd97757, emissive: 0x5a2410 });
    const t = new THREE.Mesh(new THREE.CylinderGeometry(0.34, 0.34, 0.09, 10), m);
    t.rotation.x = Math.PI / 2;
    const g = new THREE.Group(); g.add(t);
    return g;
  }

  return {
    claudio: () => buildPlumber(CLAUDIO_PAL),
    grokio: () => { const m = buildPlumber(GROKIO_PAL); m.scale.set(1.35, 1.42, 1.35); return m; },
    bug: buildBug, star: buildStar, token: buildToken,
  };
})();
