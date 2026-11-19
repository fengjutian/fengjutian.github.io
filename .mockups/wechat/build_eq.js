// Render the WeChat equations to PNG via MathJax + headless Chromium.
// WeChat's editor drops MathJax, so each formula has to arrive as an image.
const { chromium } = require("playwright");
const fs = require("fs");
const os = require("os");
const path = require("path");

const OUT = path.join(__dirname, "img");
const EQ = [
  ["eq-01-coupling", String.raw`a_B=\pi_B(b_B),\qquad b_B'=\tau_B\left(b_B,\ o_B(a_A,s)\right)`],
  ["eq-02-interactive-state", String.raw`\mathrm{IS}_{ij}=S\times M_j,\qquad M_j=\Theta_j\times B_j`],
  [
    "eq-03-belief-update",
    String.raw`b_i'(\mathrm{IS}')\ \propto\ O_i(o_i\mid \mathrm{IS}',a_i)\sum_{\mathrm{IS}}T(\mathrm{IS}'\mid \mathrm{IS},a_i,a_j)\,b_i(\mathrm{IS})`,
  ],
  ["eq-04-recursion", String.raw`a_k=\mathrm{BR}\left(a_{k-1}\right),\qquad a_{\mathrm{CH}}=\mathrm{BR}\left(\sum_{k\ge 1}p_k\,a_k\right)`],
  ["eq-05-mixture", String.raw`P(X_B\mid H_A)=\sum_{k=1}^{K}w_k\,\mathcal{N}(\mu_k,\Sigma_k)`],
  ["eq-06-performative", String.raw`\theta_{\mathrm{ps}}\in\arg\min_{\theta}\ \mathbb{E}_{z\sim D(\theta_{\mathrm{ps}})}\left[\ell(z;\theta)\right]`],
];

(async () => {
  fs.mkdirSync(OUT, { recursive: true });
  const body = EQ.map(([id, tex], i) => `<div class="row"><div class="eq" id="${id}">\\[${tex}\\]</div><div class="cap">${i + 1}</div></div>`).join(
    "\n"
  );

  const html = `<!DOCTYPE html><html><head><meta charset="utf-8">
<script>
window.MathJax = {
  tex: { displayMath: [['\\\\[', '\\\\]']], inlineMath: [] },
  svg: { fontCache: 'local' },
  startup: { typeset: true }
};
</script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-svg.js"></script>
<style>
  html, body { margin: 0; padding: 0; background: #ffffff; }
  body { font-family: 'Times New Roman', serif; }
  .row { padding: 12px 18px; display: inline-block; }
  .eq { font-size: 26px; color: #1a1a1a; }
  .cap { font-size: 1px; color: #ffffff; height: 1px; overflow: hidden; }
</style></head><body>${body}</body></html>`;

  const file = path.join(os.tmpdir(), "wechat-equations.html");
  fs.writeFileSync(file, html, "utf8");

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1100, height: 900 }, deviceScaleFactor: 3 });
  page.on("console", (m) => {
    if (m.type() === "error") console.log("[page]", m.text());
  });
  await page.goto("file:///" + file.replace(/\\/g, "/"), { waitUntil: "domcontentloaded", timeout: 60000 });
  await page.waitForFunction(() => window.MathJax && window.MathJax.startup && window.MathJax.startup.promise, null, { timeout: 60000 });
  await page.evaluate(() => window.MathJax.startup.promise);
  await page.waitForFunction(() => document.querySelectorAll("mjx-container").length >= 6, null, { timeout: 60000 });
  await page.waitForTimeout(300);

  for (const [id] of EQ) {
    const el = await page.$("#" + id);
    const box = await el.boundingBox();
    const out = path.join(OUT, id + ".png");
    await el.screenshot({ path: out, omitBackground: true });
    console.log(id, Math.round(box.width), "x", Math.round(box.height), "css px");
  }
  await browser.close();
})();
