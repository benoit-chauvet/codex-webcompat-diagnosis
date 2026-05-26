import fs from "node:fs/promises";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const OUT = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/css_probe.json";
const URL = "https://block.xyz/news";
const firefox = "/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox";
const chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";

const configs = [
  { browser: "firefox", executable: firefox, product: "firefox" },
  { browser: "chrome", executable: chrome, product: "chrome" },
];

async function run(config) {
  const launchOptions = {
    browser: config.product,
    executablePath: config.executable,
    headless: true,
    userDataDir: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/css_probe_${config.browser}_profile`,
    defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 },
    acceptInsecureCerts: true,
    timeout: 90000,
    protocolTimeout: 90000,
    args: config.browser === "chrome" ? ["--no-first-run", "--no-default-browser-check", "--disable-background-networking"] : [],
  };
  if (config.browser === "firefox") {
    launchOptions.extraPrefsFirefox = {
      "app.update.auto": false,
      "app.update.enabled": false,
      "browser.shell.checkDefaultBrowser": false,
      "browser.startup.homepage_override.mstone": "ignore",
      "browser.startup.page": 0,
    };
  }
  const browser = await puppeteer.launch(launchOptions);
  try {
    const page = await browser.newPage();
    await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 90000 });
    await page.waitForNetworkIdle({ idleTime: 1000, timeout: 15000 }).catch(() => {});
    await page.waitForFunction(() => document.fonts ? document.fonts.status === "loaded" : true, { timeout: 15000 }).catch(() => {});
    await new Promise(resolve => setTimeout(resolve, 2000));
    return await page.evaluate(() => {
      const headline = document.querySelector("h3.headline.svelte-12tp18c");
      const content = document.querySelector(".content.svelte-12tp18c");
      const card = document.querySelector(".card-root.svelte-12tp18c, .card.svelte-12tp18c");
      const styleObject = element => {
        if (!element) {
          return null;
        }
        const style = getComputedStyle(element);
        const keys = [
          "font",
          "font-family",
          "font-size",
          "font-weight",
          "line-height",
          "margin-top",
          "margin-bottom",
          "padding-top",
          "padding-bottom",
          "height",
          "min-height",
          "max-height",
          "display",
          "overflow",
          "overflow-wrap",
          "grid-template-columns",
          "grid-template-rows",
          "grid-column",
          "grid-row",
        ];
        return Object.fromEntries(keys.map(key => [key, style.getPropertyValue(key)]));
      };
      const matchedRules = [];
      for (const sheet of [...document.styleSheets]) {
        let rules;
        try {
          rules = sheet.cssRules;
        } catch {
          continue;
        }
        for (const rule of [...rules]) {
          const text = rule.cssText || "";
          if (/(headline|svelte-12tp18c|card-root|imageTopElement|\\.content|h3|font-family|line-height)/i.test(text)) {
            matchedRules.push(text);
          }
        }
      }
      const resourceUrls = performance.getEntriesByType("resource")
        .map(entry => entry.name)
        .filter(name => /\.(css|woff2?|ttf|otf|js)(\?|$)/i.test(name));
      return {
        userAgent: navigator.userAgent,
        fontsStatus: document.fonts?.status || null,
        fontFaces: document.fonts ? [...document.fonts].map(face => ({
          family: face.family,
          style: face.style,
          weight: face.weight,
          stretch: face.stretch,
          status: face.status,
          loaded: String(face.loaded),
        })) : [],
        headline: headline ? {
          text: headline.innerText,
          rect: headline.getBoundingClientRect().toJSON(),
          styles: styleObject(headline),
        } : null,
        content: content ? {
          rect: content.getBoundingClientRect().toJSON(),
          styles: styleObject(content),
        } : null,
        card: card ? {
          rect: card.getBoundingClientRect().toJSON(),
          styles: styleObject(card),
        } : null,
        matchedRules,
        resourceUrls,
      };
    });
  } finally {
    await browser.close();
  }
}

const output = {};
for (const config of configs) {
  output[config.browser] = await run(config);
}
await fs.writeFile(OUT, JSON.stringify(output, null, 2), "utf8");
console.log(OUT);
