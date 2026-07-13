const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--use-gl=angle', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'] });
  const page = await browser.newPage();
  page.on('console', m => console.log('CONSOLE:', m.text()));
  page.on('pageerror', e => console.log('PAGEERROR:', e.message));
  const html = `<!DOCTYPE html><html><body><script>${require('fs').readFileSync('three.min.js','utf8')}</script>
  <script>
    const r = new THREE.WebGLRenderer(); r.setSize(320,240); document.body.appendChild(r.domElement);
    const s = new THREE.Scene(); s.background = new THREE.Color(0x88aaff);
    const c = new THREE.PerspectiveCamera(60, 320/240, 0.1, 100); c.position.set(0,1,3);
    const m = new THREE.Mesh(new THREE.BoxGeometry(1,1,1), new THREE.MeshLambertMaterial({color:0xff8800}));
    s.add(m); s.add(new THREE.DirectionalLight(0xffffff,1));
    r.render(s,c); console.log('WEBGL OK', r.getContext().getParameter(r.getContext().RENDERER));
  </script></body></html>`;
  await page.setContent(html);
  await page.waitForTimeout(1500);
  await page.screenshot({ path: 'out_webgl_test.png' });
  await browser.close();
})();
