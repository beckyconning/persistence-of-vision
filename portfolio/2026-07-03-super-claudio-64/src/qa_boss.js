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
  await page.waitForTimeout(1500);
  await page.evaluate(() => { for (let i = 0; i < 6; i++) GAME.save.stars['dbg' + i] = true; GAME.debugWarp('boss'); });
  await page.waitForTimeout(2500);

  for (let round = 0; round < 3; round++) {
    // wait for stunned
    await page.waitForFunction(() => GAME.ctx.boss && GAME.ctx.boss.state === 'stunned', null, { timeout: 30000 });
    // hop above him and pound
    await page.evaluate(() => {
      const B = GAME.ctx.boss;
      GAME.player.pos.set(B.pos.x, 5.5, B.pos.z);
      GAME.player.vel.set(0, 0, 0);
      GAME.player.grounded = false;
    });
    await page.waitForTimeout(80);
    await page.keyboard.press('KeyC');
    await page.waitForTimeout(1200);
    const st = await page.evaluate(() => ({ hits: GAME.ctx.boss.hits, state: GAME.ctx.boss.state }));
    console.log('round', round + 1, JSON.stringify(st));
  }
  // wait for grand star + grab it
  await page.waitForFunction(() => GAME.ctx.stars.some(s => s.id === 'grand_star' && s.mesh.visible), null, { timeout: 15000 });
  await page.screenshot({ path: 'out/qa3_grandstar.png' });
  await page.evaluate(() => { GAME.player.pos.set(0, 2.4, 0); });
  await page.waitForTimeout(1000);
  const s1 = await page.evaluate(() => GAME.state);
  console.log('after grand star grab:', s1);
  await page.waitForTimeout(4200);
  const s2 = await page.evaluate(() => GAME.state);
  await page.screenshot({ path: 'out/qa3_victory.png' });
  console.log('final state:', s2, '(should be victory)');
  console.log('ERRORS:', errors.length ? errors : 'none');
  await browser.close();
})();
