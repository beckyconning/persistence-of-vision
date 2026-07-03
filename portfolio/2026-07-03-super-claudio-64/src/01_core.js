// ============ INPUT / PHYSICS / CAMERA ============
const INPUT = (() => {
  const down = {}, pressed = {};
  window.addEventListener('keydown', e => {
    if (!down[e.code]) pressed[e.code] = true;
    down[e.code] = true;
    if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) e.preventDefault();
  });
  window.addEventListener('keyup', e => { down[e.code] = false; });
  return {
    down, pressed,
    clear() { for (const k in pressed) pressed[k] = false; },
    axis() { // camera-relative move intent
      let x = 0, z = 0;
      if (down.KeyW || down.ArrowUp) z -= 1;
      if (down.KeyS || down.ArrowDown) z += 1;
      if (down.KeyA || down.ArrowLeft) x -= 1;
      if (down.KeyD || down.ArrowRight) x += 1;
      const l = Math.hypot(x, z);
      return l > 0 ? [x / l, z / l] : [0, 0];
    }
  };
})();

// ---- physics world ----
class World {
  constructor() {
    this.boxes = [];      // {x0,x1,y0,y1,z0,z1, deadly?, id?}
    this.cyls = [];       // {x,z,r,y0,y1}
    this.movers = [];     // boxes with .prev = [x,z,y] and mesh
    this.terrain = null;  // (x,z) => height or -Infinity
    this.killY = -30;
  }
  groundAt(x, z, feetY) {
    let g = this.terrain ? this.terrain(x, z) : -Infinity;
    let mover = null;
    const eps = 0.32;
    for (const b of this.boxes) {
      if (x > b.x0 - 0.2 && x < b.x1 + 0.2 && z > b.z0 - 0.2 && z < b.z1 + 0.2) {
        if (b.y1 <= feetY + eps && b.y1 > g) { g = b.y1; mover = b.mover ? b : null; }
      }
    }
    for (const c of this.cyls) {
      if (Math.hypot(x - c.x, z - c.z) < c.r + 0.2) {
        if (c.y1 <= feetY + eps && c.y1 > g) { g = c.y1; mover = null; }
      }
    }
    return { g, mover };
  }
  collideHoriz(p, r) {
    // push a vertical capsule (feet p.y .. p.y+1.5) out of solids
    for (const b of this.boxes) {
      if (p.y + 1.4 < b.y0 || p.y + 0.25 > b.y1) continue;
      const nx = Math.max(b.x0, Math.min(p.x, b.x1));
      const nz = Math.max(b.z0, Math.min(p.z, b.z1));
      const dx = p.x - nx, dz = p.z - nz;
      const d2 = dx * dx + dz * dz;
      if (d2 < r * r) {
        if (d2 > 1e-9) {
          const d = Math.sqrt(d2);
          p.x = nx + dx / d * r; p.z = nz + dz / d * r;
        } else { // inside: push to nearest face
          const pushW = Math.min(p.x - b.x0 + r, b.x1 - p.x + r);
          const pushD = Math.min(p.z - b.z0 + r, b.z1 - p.z + r);
          if (pushW < pushD) p.x = (p.x - b.x0 < b.x1 - p.x) ? b.x0 - r : b.x1 + r;
          else p.z = (p.z - b.z0 < b.z1 - p.z) ? b.z0 - r : b.z1 + r;
        }
      }
    }
    for (const c of this.cyls) {
      if (p.y + 1.4 < c.y0 || p.y + 0.25 > c.y1) continue;
      const dx = p.x - c.x, dz = p.z - c.z;
      const d = Math.hypot(dx, dz), rr = c.r + r;
      if (d < rr && d > 1e-9) { p.x = c.x + dx / d * rr; p.z = c.z + dz / d * rr; }
    }
  }
  ceilingAt(x, z, headY) {
    let c = Infinity;
    for (const b of this.boxes) {
      if (x > b.x0 && x < b.x1 && z > b.z0 && z < b.z1) {
        if (b.y0 >= headY - 0.4 && b.y0 < c) c = b.y0;
      }
    }
    return c;
  }
}

// ---- SM64-ish character controller ----
class Player {
  constructor(mesh) {
    this.mesh = mesh;
    this.pos = new THREE.Vector3();
    this.vel = new THREE.Vector3();
    this.yaw = 0;
    this.grounded = false;
    this.jumpChain = 0;         // 0/1/2 for single/double/triple
    this.chainTimer = 0;
    this.coyote = 0;
    this.pounding = false;
    this.poundWind = 0;
    this.longjumping = false;
    this.hp = 3;
    this.invuln = 0;
    this.rideDelta = new THREE.Vector3();
    this.anim = { t: 0, mode: 'idle' };
    this.frozen = false;
  }
  spawn(p) {
    this.pos.copy(p); this.vel.set(0, 0, 0); this.grounded = false;
    this.pounding = false; this.longjumping = false; this.hp = 3;
  }
  hurt(game, n = 1) {
    if (this.invuln > 0) return;
    this.hp -= n; this.invuln = 1.4;
    AUDIO.S.hurt();
    game.flashHearts();
    // knockback
    this.vel.y = 6; this.vel.x *= -0.6; this.vel.z *= -0.6;
    if (this.hp <= 0) game.playerDied();
  }
  update(dt, world, camYaw, game) {
    if (this.frozen) { this.animate(dt, 0); return; }
    const WALK = 9.2, ACCEL = 46, AIR_ACCEL = 22, GRAV = -30, FRICTION = this.ice ? 2.2 : 26;
    const [ix, iz] = INPUT.axis();
    // camera-relative intent
    const s = Math.sin(camYaw), c = Math.cos(camYaw);
    const wx = ix * c - iz * s, wz = ix * s + iz * c;
    const moving = (ix !== 0 || iz !== 0);

    if (this.pounding) {
      this.poundWind -= dt;
      if (this.poundWind > 0) { this.vel.set(0, 2, 0); }
      else this.vel.y = -34;
    } else {
      const acc = this.grounded ? ACCEL : AIR_ACCEL;
      this.vel.x += wx * acc * dt;
      this.vel.z += wz * acc * dt;
      const hs = Math.hypot(this.vel.x, this.vel.z);
      const maxs = this.longjumping ? 15 : WALK;
      if (hs > maxs) { this.vel.x *= maxs / hs; this.vel.z *= maxs / hs; }
      if (!moving && this.grounded) {
        const f = Math.max(0, 1 - FRICTION * dt / Math.max(hs, 0.001));
        this.vel.x *= f; this.vel.z *= f;
      }
      if (moving) this.yaw = Math.atan2(this.vel.x, this.vel.z);
    }
    // timers
    this.chainTimer -= dt; this.coyote -= dt; this.invuln -= dt;

    // JUMPS
    const wantJump = INPUT.pressed.Space;
    if (wantJump && (this.grounded || this.coyote > 0) && !this.pounding) {
      const hs = Math.hypot(this.vel.x, this.vel.z);
      if ((INPUT.down.ShiftLeft || INPUT.down.ShiftRight) && hs > 5) {
        // LONG JUMP
        this.vel.y = 9.5;
        const bx = this.vel.x / hs, bz = this.vel.z / hs;
        this.vel.x = bx * 15; this.vel.z = bz * 15;
        this.longjumping = true; this.jumpChain = 0;
        AUDIO.S.longjump();
      } else {
        const chain = (this.chainTimer > 0) ? this.jumpChain : 0;
        const vy = [11, 12.6, 15.5][chain];
        if (chain === 2 && Math.hypot(this.vel.x, this.vel.z) < 4) { this.vel.y = 11; this.jumpChain = 0; AUDIO.S.jump(); }
        else {
          this.vel.y = vy;
          [AUDIO.S.jump, AUDIO.S.jump2, AUDIO.S.jump3][chain]();
          this.jumpChain = (chain + 1) % 3;
        }
      }
      this.grounded = false; this.coyote = 0;
    }
    // GROUND POUND
    if ((INPUT.pressed.ControlLeft || INPUT.pressed.KeyC) && !this.grounded && !this.pounding) {
      this.pounding = true; this.poundWind = 0.16;
      AUDIO.S.charge();
    }

    // integrate
    this.vel.y += GRAV * dt;
    if (this.vel.y < -40) this.vel.y = -40;
    this.pos.x += (this.vel.x + this.rideDelta.x / dt * 0) * dt + this.rideDelta.x;
    this.pos.z += this.vel.z * dt + this.rideDelta.z;
    this.pos.y += this.vel.y * dt + Math.max(0, this.rideDelta.y);
    this.rideDelta.set(0, 0, 0);

    // collide
    world.collideHoriz(this.pos, 0.48);
    const { g, mover } = world.groundAt(this.pos.x, this.pos.z, this.pos.y);
    const wasAir = !this.grounded;
    if (this.pos.y <= g && this.vel.y <= 0.01) {
      this.pos.y = g;
      if (wasAir) {
        if (this.pounding) { AUDIO.S.pound(); game.onPound(this.pos); }
        else if (this.vel.y < -18) AUDIO.S.land();
        this.chainTimer = 0.30;
      }
      this.grounded = true; this.coyote = 0.12;
      this.pounding = false; this.longjumping = false;
      this.vel.y = 0;
      this.standingOn = mover;
    } else {
      if (this.grounded) this.coyote = 0.12;
      this.grounded = false;
      this.standingOn = null;
    }
    const ceil = world.ceilingAt(this.pos.x, this.pos.z, this.pos.y + 1.55);
    if (this.pos.y + 1.55 > ceil && this.vel.y > 0) { this.pos.y = ceil - 1.55; this.vel.y = 0; }

    if (this.pos.y < world.killY) game.playerFell();

    // drive mesh
    this.mesh.position.copy(this.pos);
    this.mesh.rotation.y = this.yaw;
    this.mesh.visible = !(this.invuln > 0 && Math.floor(this.invuln * 14) % 2 === 0);
    this.animate(dt, Math.hypot(this.vel.x, this.vel.z));
  }
  animate(dt, speed) {
    const a = this.anim;
    a.t += dt * (2 + speed * 1.15);
    const J = this.mesh.userData.joints;
    if (!J) return;
    const sw = Math.sin(a.t * 4);
    if (this.pounding) {
      J.hipL.rotation.x = J.hipR.rotation.x = -2.0;
      J.shL.rotation.z = -2.4; J.shR.rotation.z = 2.4;
      this.mesh.rotation.x = 0;
    } else if (!this.grounded) {
      const up = this.vel.y > 0;
      J.hipL.rotation.x = up ? 1.0 : 0.35; J.hipR.rotation.x = up ? 0.25 : 0.5;
      J.shL.rotation.z = up ? -1.9 : -0.7; J.shR.rotation.z = up ? 1.9 : 0.7;
      J.shL.rotation.x = J.shR.rotation.x = 0;
      this.mesh.rotation.x = this.longjumping ? 0.5 : 0;
      if (this.jumpChain === 0 && this.vel.y > 8) this.mesh.rotation.x = 0; // triple spin handled below
    } else if (speed > 0.6) {
      J.hipL.rotation.x = sw * 0.85; J.hipR.rotation.x = -sw * 0.85;
      J.shL.rotation.x = -sw * 0.8; J.shR.rotation.x = sw * 0.8;
      J.shL.rotation.z = -0.18; J.shR.rotation.z = 0.18;
      this.mesh.rotation.x = 0.06;
    } else {
      J.hipL.rotation.x = J.hipR.rotation.x = 0;
      J.shL.rotation.x = J.shR.rotation.x = 0;
      J.shL.rotation.z = -0.1 + 0.04 * Math.sin(a.t);
      J.shR.rotation.z = 0.1 - 0.04 * Math.sin(a.t);
      this.mesh.rotation.x = 0;
    }
  }
}

// ---- lakitu-ish camera ----
class GameCamera {
  constructor(cam) {
    this.cam = cam;
    this.yaw = 0; this.dist = 11; this.height = 4.4;
    this.target = new THREE.Vector3();
  }
  update(dt, playerPos, world) {
    if (INPUT.pressed.KeyQ) this.yaw += Math.PI / 4;
    if (INPUT.pressed.KeyE) this.yaw -= Math.PI / 4;
    if (INPUT.down.KeyR) this.dist = Math.max(6, this.dist - 8 * dt);
    if (INPUT.down.KeyF) this.dist = Math.min(16, this.dist + 8 * dt);
    this.target.lerp(new THREE.Vector3(playerPos.x, playerPos.y + 1.4, playerPos.z), Math.min(1, dt * 6));
    const cx = this.target.x + Math.sin(this.yaw) * this.dist;
    const cz = this.target.z + Math.cos(this.yaw) * this.dist;
    let cy = this.target.y + this.height;
    this.cam.position.lerp(new THREE.Vector3(cx, cy, cz), Math.min(1, dt * 5));
    this.cam.lookAt(this.target);
  }
}
