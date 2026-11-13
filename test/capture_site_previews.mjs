import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const sites = [
  ["anthropic", "https://www.anthropic.com/"],
  ["simon-willison", "https://simonwillison.net/"],
  ["lil-log", "https://lilianweng.github.io/"],
  ["hacker-news", "https://news.ycombinator.com/"],
  ["github-trending", "https://github.com/trending"],
  ["arxiv-cs-cl", "https://arxiv.org/list/cs.CL/recent"],
  ["looseleaf", "https://kevintngo.github.io/looseleaf/"],
  ["plopui", "https://plopui.com/"],
  ["inkra", "https://inkrajs.github.io/"],
  ["goopui", "https://goop.timmcmasters.work/docs/components"],
  ["solid-glass", "https://deeplethe.github.io/solid-glass/"],
  ["affectui", "https://affectui.com/"],
  ["prestige-ui", "https://prestigeui.com/"],
  ["boardui", "https://boardui.com/"],
  ["scrolltide", "https://www.scrolltide.co/"],
  ["navbar-gallery", "https://www.navbar.gallery/"],
  ["footer-design", "https://www.footer.design/"],
  ["cta-gallery", "https://cta.gallery/"],
  ["refero-design-styles", "https://styles.refero.design/"],
];

const outputDirectory = path.resolve("assets/img/sites");
await mkdir(outputDirectory, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  colorScheme: "light",
  reducedMotion: "reduce",
});

for (const [slug, url] of sites) {
  const page = await context.newPage();
  try {
    await page.goto(url, { waitUntil: "domcontentloaded", timeout: 30_000 });
    await page.waitForTimeout(2_000);
    await page.screenshot({
      path: path.join(outputDirectory, `${slug}.jpg`),
      type: "jpeg",
      quality: 72,
      clip: { x: 0, y: 0, width: 1440, height: 810 },
    });
    console.log(`captured ${slug}`);
  } catch (error) {
    console.error(`failed ${slug}: ${error.message}`);
  } finally {
    await page.close();
  }
}

await browser.close();
