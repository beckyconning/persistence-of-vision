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
  await page.waitForTimeout(2200);
  await page.evaluate(() => { GAME.player.pos.set(0, 1, -21.5); });
  for (let i = 0; i < 6; i++) {
    await page.keyboard.down('KeyW');
    await page.waitForTimeout(250);
    await page.keyboard.up('KeyW');
    const s = await page.evaluate(() => ({ z: GAME.player.pos.z.toFixed(2), lvl: GAME.levelId, st: GAME.state }));
    console.log(i, JSON.stringify(s));
    if (s.lvl === 'lobby') break;
    await page.waitForTimeout(150);
  }
  await page.waitForTimeout(2200);
  console.log('final:', await page.evaluate(() => GAME.levelId));
  await page.screenshot({ path: 'out/v3_afterdoor.png' });
  console.log('ERRORS:', errors.length ? errors : 'none');
  await browser.close();
})();
