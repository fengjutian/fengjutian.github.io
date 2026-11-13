const path = require('path');
const { chromium } = require('D:/github/fengjutian.github.io/node_modules/playwright');

(async () => {
  const browser = await chromium.launch({
    executablePath:
      'C:\\Users\\Charles.feng\\AppData\\Local\\ms-playwright\\chromium-1248\\chrome-win64\\chrome.exe',
  });
  const page = await browser.newPage({
    viewport: { width: 1200, height: 1000 },
    deviceScaleFactor: 2,
  });
  const file = 'file:///D:/github/fengjutian.github.io/.mockups/blog-list-after.html';
  await page.goto(file, { waitUntil: 'networkidle' });
  await page.screenshot({
    path: path.join(__dirname, 'blog-list-after.png'),
    fullPage: true,
  });
  await browser.close();
  console.log('done');
})().catch((e) => {
  console.error(e);
  process.exit(1);
});
