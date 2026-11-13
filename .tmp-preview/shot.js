// Preview harness: load the deployed post page, optionally inject override CSS,
// then screenshot it at a given CSS viewport size.
const { chromium } = require("playwright");
const fs = require("fs");
const path = require("path");

(async () => {
  const url = process.argv[2];
  const out = process.argv[3];
  const cssFile = process.argv[4];
  const width = Number(process.argv[5] || 2040);
  const height = Number(process.argv[6] || 1100);

  const browser = await chromium.launch({
    executablePath:
      "C:\\Users\\Charles.feng\\AppData\\Local\\ms-playwright\\chromium-1248\\chrome-win64\\chrome.exe",
  });
  const page = await browser.newPage({
    viewport: { width, height },
    deviceScaleFactor: 1.25,
  });
  await page.goto(url, { waitUntil: "load", timeout: 60000 });
  await page.waitForTimeout(2500);
  if (cssFile && fs.existsSync(cssFile)) {
    const css = fs.readFileSync(cssFile, "utf8");
    await page.addStyleTag({ content: css });
    await page.waitForTimeout(400);
  }
  await page.screenshot({ path: out });
  // report some measurements
  const metrics = await page.evaluate(() => {
    const pick = (sel) => {
      const el = document.querySelector(sel);
      if (!el) return null;
      const r = el.getBoundingClientRect();
      return { w: Math.round(r.width), h: Math.round(r.height), left: Math.round(r.left) };
    };
    return {
      container: pick(".container"),
      articleCol: pick(".container > .row > .col-sm-9"),
      tocCol: pick(".container > .row > .col-sm-3"),
      toc: pick("#toc-sidebar"),
      tocScrollH: document.querySelector("#toc-sidebar")
        ? {
            scrollHeight: document.querySelector("#toc-sidebar").scrollHeight,
            clientHeight: document.querySelector("#toc-sidebar").clientHeight,
          }
        : null,
      docH: document.documentElement.scrollHeight,
    };
  });
  console.log(JSON.stringify(metrics, null, 2));
  await browser.close();
})();
