import fs from "node:fs/promises";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const browser = await puppeteer.launch({
  browser: "chrome",
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
  headless: true,
  userDataDir: "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/style_tags_profile",
  defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 },
  args: ["--no-first-run", "--no-default-browser-check", "--disable-background-networking"],
});

try {
  const page = await browser.newPage();
  await page.goto("https://block.xyz/news", { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForNetworkIdle({ idleTime: 1000, timeout: 15000 }).catch(() => {});
  await new Promise(resolve => setTimeout(resolve, 1000));
  const state = await page.evaluate(() => {
    const rootStyle = getComputedStyle(document.documentElement);
    const bodyStyle = getComputedStyle(document.body);
    const headline = document.querySelector("h3.headline.svelte-12tp18c");
    const cardRoot = document.querySelector(".card-root.svelte-12tp18c");
    const cardRootStyle = cardRoot ? getComputedStyle(cardRoot) : null;
    const variables = [
      "--font-family-primary",
      "--font-family-secondary",
      "--theme-font-family",
      "--theme-line-height",
      "--twist-font-family-pilat-wide",
      "--twist-font-family-pilat-condensed",
      "--twist-font-family-pp-neue-machina",
    ];
    const styleTags = [...document.querySelectorAll("style")]
      .map((style, index) => ({ index, text: style.textContent || "" }))
      .filter(item => /(css-1g6k0uy|css-zh33qs|css-quuz67|css-s0hqca|headline|card-root|font-family-primary|theme-line-height)/.test(item.text))
      .map(item => ({
        index: item.index,
        length: item.text.length,
        snippets: ["css-1g6k0uy", "css-zh33qs", "css-quuz67", "css-s0hqca", "font-family-primary", "theme-line-height"]
          .map(needle => {
            const offset = item.text.indexOf(needle);
            if (offset < 0) {
              return null;
            }
            return {
              needle,
              offset,
              text: item.text.slice(Math.max(0, offset - 800), Math.min(item.text.length, offset + 1800)),
            };
          })
          .filter(Boolean),
      }));
    return {
      rootVars: Object.fromEntries(variables.map(name => [name, rootStyle.getPropertyValue(name)])),
      body: {
        font: bodyStyle.font,
        lineHeight: bodyStyle.lineHeight,
        fontFamily: bodyStyle.fontFamily,
      },
      cardRoot: cardRootStyle ? {
        font: cardRootStyle.font,
        lineHeight: cardRootStyle.lineHeight,
        fontFamily: cardRootStyle.fontFamily,
      } : null,
      headline: headline ? {
        outerHTML: headline.outerHTML,
        style: {
          font: getComputedStyle(headline).font,
          lineHeight: getComputedStyle(headline).lineHeight,
          fontFamily: getComputedStyle(headline).fontFamily,
        },
      } : null,
      styleTags,
    };
  });
  const out = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/style_tags_probe.json";
  await fs.writeFile(out, JSON.stringify(state, null, 2), "utf8");
  console.log(out);
} finally {
  await browser.close();
}
