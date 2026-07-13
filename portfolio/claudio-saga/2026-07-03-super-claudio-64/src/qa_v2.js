const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  await page.goto('file://' + path.resolve('claudio64.html'));
  await page.waitForTimeout(900);
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2600);
  await page.screenshot({ path: 'out/v2_outside.png' });

  // facing test: walk TOWARD camera (S) — should show his face
  await page.keyboard.down('KeyS');
  await page.waitForTimeout(650);
  await page.keyboard.up('KeyS');
  await page.waitForTimeout(300);
  await page.screenshot({ path: 'out/v2_facing.png' });

  // mouse orbit test
  const yaw0 = await page.evaluate(() => GAME.player.yaw);
  await page.mouse.move(480, 360);
  await page.mouse.down({ button: 'right' });
  await page.mouse.move(680, 320, { steps: 10 });
  await page.mouse.up({ button: 'right' });
  await page.waitForTimeout(400);
  await page.screenshot({ path: 'out/v2_orbit.png' });
  console.log('mouse orbit ok (no crash)');

  // door into lobby
  await page.evaluate(() => { GAME.player.pos.set(0, 1, -22.5); });
  await page.keyboard.down('KeyW');
  await page.waitForTimeout(700);
  await page.keyboard.up('KeyW');
  await page.waitForTimeout(2400);
  console.log('after castle door, level =', await page.evaluate(() => GAME.levelId));
  await page.screenshot({ path: 'out/v2_lobby.png' });

  // lobby exit back out
  await page.evaluate(() => { GAME.player.pos.set(0, 0.5, 14.5); });
  await page.keyboard.down('KeyS');
  await page.waitForTimeout(800);
  await page.keyboard.up('KeyS');
  await page.waitForTimeout(2400);
  console.log('after exit door, level =', await page.evaluate(() => GAME.levelId));

  // bigger level spot checks
  for (const lvl of ['meadow', 'ice', 'sky']) {
    await page.evaluate(l => GAME.debugWarp(l), lvl);
    await page.waitForTimeout(2600);
    await page.screenshot({ path: 'out/v2_' + lvl + '.png' });
  }
  console.log('ERRORS:', errors.length ? errors : 'none');
  await browser.close();
})();
