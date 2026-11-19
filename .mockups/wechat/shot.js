const { chromium } = require("playwright");
const path = require("path");

(async () => {
  const file = path.join(__dirname, "cognitive-game-wechat.html");
  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: 720, height: 1200 },
    deviceScaleFactor: 1,
  });
  await page.goto("file:///" + file.replace(/\\/g, "/"));
  await page.waitForTimeout(700);
  const out = path.join(__dirname, "full.png");
  await page.screenshot({ path: out, fullPage: true });
  const h = await page.evaluate(() => document.body.scrollHeight);
  console.log("wrote", out, "height", h);
  await browser.close();
})();
