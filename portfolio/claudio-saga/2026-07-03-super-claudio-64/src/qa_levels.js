const { chromium } = require('playwright');
const path = require('path');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader', '--autoplay-policy=no-user-gesture-required'] });
  const page = await browser.newPage({ viewport: { width: 960, height: 720 } });
  const errors = [];
  page.on('pageerror', e => errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') errors.push(m.text()); });
  await page.goto('file://' + path.resolve('claudio64.html'));
  await page.waitForTimeout(1200);
  await page.screenshot({ path: 'out/qa_title.png' });
  await page.keyboard.press('Enter');
  await page.waitForTimeout(2500);
  await page.screenshot({ path: 'out/qa_lobby.png' });
  for (const lvl of ['meadow', 'lava', 'ice', 'sky', 'legacy', 'boss']) {
    await page.evaluate(l => GAME.debugWarp(l), lvl);
    await page.waitForTimeout(2600);
    // hold W for a moment so it's not just the spawn frame
    await page.keyboard.down('KeyW'); await page.waitForTimeout(700); await page.keyboard.up('KeyW');
    await page.waitForTimeout(400);
    await page.screenshot({ path: 'out/qa_' + lvl + '.png' });
  }
  console.log('ERRORS:', errors.length ? errors.slice(0, 12) : 'none');
  await browser.close();
})();
