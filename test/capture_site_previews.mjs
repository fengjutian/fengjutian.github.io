import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";

const sites = [
  ["opennana-prompt-gallery", "https://opennana.com/awesome-prompt-gallery/"],
  ["youmind-nano-banana", "https://youmind.com/zh-CN/nano-banana-pro-prompts"],
  ["local-banana", "https://localbanana.io/"],
  ["tihub-ai-prompt", "https://tihubb.com/ai-prompt/"],
  ["chatgpt-image-art", "https://chatgptimage.art/"],
  ["nano-banana-showcase", "https://nanobanana-showcase.com/"],
  ["nano-banana-prompt", "https://nanobananaprompt.org/"],
  ["nano-banana-art", "https://nanobananaart.net/prompts"],
  ["fotor-nano-banana", "https://www.fotor.com/blog/nano-banana-model-prompts/"],
  ["x-dotey", "https://x.com/dotey"],
  ["x-op7418", "https://x.com/op7418"],
  ["x-berryxia", "https://x.com/berryxia"],
  ["x-zho", "https://x.com/ZHO_ZHO_ZHO"],
  ["curated-design", "https://www.curated.design/"],
  ["one-page-love", "https://onepagelove.com/"],
  ["component-gallery", "https://component.gallery/"],
  ["app-motion", "https://appmotion.design/"],
  ["mobbin", "https://mobbin.com/"],
  ["rebrand-gallery", "https://www.rebrand.gallery/"],
  ["finviz", "https://finviz.com/"],
  ["stockanalysis", "https://stockanalysis.com/"],
  ["seeking-alpha", "https://seekingalpha.com/"],
  ["etf-database", "https://etfdb.com/"],
  ["companies-market-cap", "https://companiesmarketcap.com/"],
  ["koyfin", "https://koyfin.com/"],
  ["macromicro", "https://en.macromicro.me/"],
  ["fred", "https://fred.stlouisfed.org/"],
  ["reddit", "https://www.reddit.com/"],
  ["analysis-site", "https://analysissite.vercel.app/"],
  ["hn-buzzing", "https://hn.buzzing.cc/"],
  ["ars-technica", "https://arstechnica.com/"],
  ["the-atlantic", "https://www.theatlantic.com/"],
  ["the-economist", "https://www.economist.com/"],
  ["phys-org", "https://phys.org/"],
  ["github", "https://github.com/"],
  ["news-on-japan", "https://newsonjapan.com/"],
  ["upi", "https://www.upi.com/"],
  ["drive", "https://www.drive.com.au/"],
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
const requestedSites = new Set(process.argv.slice(2));

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 1440, height: 900 },
  deviceScaleFactor: 1,
  colorScheme: "light",
  reducedMotion: "reduce",
});

for (const [slug, url] of sites) {
  if (requestedSites.size > 0 && !requestedSites.has(slug)) continue;
  const page = await context.newPage();
  page.setDefaultTimeout(60_000);
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
