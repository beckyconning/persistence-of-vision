const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve('claudio64.html'));
  await page.waitForTimeout(800);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2000);
  await page.evaluate(() => GAME.debugWarp('lobby'));
  await page.waitForTimeout(2400);
  await page.screenshot({ path: 'out/qa2_lobby.png' });

  // 1) walk into meadow painting (need 0) -> should warp
  await page.evaluate(() => { GAME.player.pos.set(-19.5, 1, -6); });
  await page.keyboard.down('KeyA');  // camera-relative; just push toward wall
  await page.waitForTimeout(900);
  await page.keyboard.up('KeyA');
  await page.waitForTimeout(2200);
  const lvl1 = await page.evaluate(() => GAME.levelId);
  console.log('after painting walk, level =', lvl1);

  // 2) grab the peak star via teleport
  await page.evaluate(() => { const s = GAME.ctx.stars[0]; GAME.player.pos.set(s.x, s.y + 0.2, s.z); });
  await page.waitForTimeout(600);
  await page.screenshot({ path: 'out/qa2_starget.png' });
  const st = await page.evaluate(() => ({ state: GAME.state, stars: GAME.starCount() }));
  console.log('star grab:', JSON.stringify(st));
  await page.waitForTimeout(4500); // starget -> warp back to lobby
  const back = await page.evaluate(() => ({ lvl: GAME.levelId, state: GAME.state }));
  console.log('after starget:', JSON.stringify(back));

  // 3) denied painting (ice needs 2, have 1)
  await page.evaluate(() => { GAME.player.pos.set(21.5, 1, -6); });
  await page.waitForTimeout(300);
  await page.keyboard.down('KeyD');
  await page.waitForTimeout(800);
  await page.keyboard.up('KeyD');
  await page.waitForTimeout(600);
  await page.screenshot({ path: 'out/qa2_denied.png' });
  const still = await page.evaluate(() => GAME.levelId);
  console.log('after denied painting, level =', still, '(should be lobby)');

  // 4) boss: give 6 stars, warp, wait for charge->stun, screenshot
  await page.evaluate(() => { for (let i = 0; i < 6; i++) GAME.save.stars['dbg' + i] = true; GAME.debugWarp('boss'); });
  await page.waitForTimeout(2500);
  await page.waitForTimeout(9000); // intro + walk + fireballs + telegraph + charge
  await page.screenshot({ path: 'out/qa2_boss.png' });
  const bs = await page.evaluate(() => GAME.ctx.boss.state);
  console.log('boss state after 11.5s:', bs);
  console.log('ERRORS:', errors.length ? errors : 'none');
  await browser.close();
})();
