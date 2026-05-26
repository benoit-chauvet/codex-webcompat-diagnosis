import fs from "node:fs/promises";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const OUT = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/fix_probe.json";
const firefox = "/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox";

const browser = await puppeteer.launch({
  browser: "firefox",
  executablePath: firefox,
  headless: true,
  userDataDir: "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/fix_probe_profile",
  defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 },
  acceptInsecureCerts: true,
  timeout: 90000,
  protocolTimeout: 90000,
  extraPrefsFirefox: {
    "app.update.auto": false,
    "app.update.enabled": false,
    "browser.shell.checkDefaultBrowser": false,
    "browser.startup.homepage_override.mstone": "ignore",
    "browser.startup.page": 0,
  },
});

function extractor() {
  const h3 = document.querySelector("h3.headline.svelte-12tp18c");
  const child = h3?.querySelector(".svelte-1c1tzhq");
  const lineRectsFor = element => {
    const range = document.createRange();
    range.selectNodeContents(element);
    return [...range.getClientRects()].map(rect => ({
      x: Number(rect.x.toFixed(2)),
      y: Number(rect.y.toFixed(2)),
      width: Number(rect.width.toFixed(2)),
      height: Number(rect.height.toFixed(2)),
    }));
  };
  const styleMap = element => {
    const style = getComputedStyle(element);
    return {
      display: style.display,
      font: style.font,
      fontFamily: style.fontFamily,
      fontSize: style.fontSize,
      lineHeight: style.lineHeight,
      fontWeight: style.fontWeight,
      marginTop: style.marginTop,
      marginBottom: style.marginBottom,
      height: style.height,
    };
  };
  return {
    h3: h3 ? {
      rect: h3.getBoundingClientRect().toJSON(),
      styles: styleMap(h3),
      lineRects: lineRectsFor(h3),
    } : null,
    child: child ? {
      text: child.textContent,
      rect: child.getBoundingClientRect().toJSON(),
      styles: styleMap(child),
      lineRects: lineRectsFor(child),
    } : null,
  };
}

try {
  const page = await browser.newPage();
  await page.goto("https://block.xyz/news", { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForNetworkIdle({ idleTime: 1000, timeout: 15000 }).catch(() => {});
  await page.waitForFunction(() => document.fonts ? document.fonts.status === "loaded" : true, { timeout: 15000 }).catch(() => {});
  await new Promise(resolve => setTimeout(resolve, 1000));
  const before = await page.evaluate(extractor);
  await page.addStyleTag({ content: "h3.headline.svelte-12tp18c > .svelte-1c1tzhq { display: block !important; }" });
  await new Promise(resolve => setTimeout(resolve, 250));
  const displayBlock = await page.evaluate(extractor);
  await page.addStyleTag({ content: "h3.headline.svelte-12tp18c { line-height: 115% !important; }" });
  await new Promise(resolve => setTimeout(resolve, 250));
  const h3LineHeight = await page.evaluate(extractor);
  const output = { before, displayBlock, h3LineHeight };
  await fs.writeFile(OUT, JSON.stringify(output, null, 2), "utf8");
  console.log(OUT);
} finally {
  await browser.close();
}
