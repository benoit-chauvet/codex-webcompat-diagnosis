#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const browsers = [
  { name: "firefox", executablePath: "/Applications/Firefox.app/Contents/MacOS/firefox" },
  { name: "chrome", executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" },
];

async function sleep(ms) {
  await new Promise(resolve => setTimeout(resolve, ms));
}

async function run(browserInfo, filePath, outDir) {
  await fs.mkdir(outDir, { recursive: true });
  const browser = await puppeteer.launch({
    browser: browserInfo.name,
    executablePath: browserInfo.executablePath,
    headless: true,
    userDataDir: path.join(outDir, "profile"),
    defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 },
    acceptInsecureCerts: true,
    args: browserInfo.name === "chrome" ? ["--no-first-run", "--no-default-browser-check"] : [],
  });
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(filePath).href, { waitUntil: "domcontentloaded" });
    await sleep(3500);
    const state = await page.evaluate(() => JSON.parse(document.getElementById("state").textContent));
    const screenshot = path.join(outDir, `${browserInfo.name}.png`);
    await page.screenshot({ path: screenshot, fullPage: false });
    await fs.writeFile(path.join(outDir, `${browserInfo.name}.json`), JSON.stringify(state, null, 2), "utf8");
    return { browser: browserInfo.name, state, screenshot };
  } finally {
    await browser.close();
  }
}

const root = path.resolve(new URL(".", import.meta.url).pathname);
const artifacts = path.join(root, "artifacts");
const results = [];
for (const browserInfo of browsers) {
  results.push(await run(browserInfo, path.join(root, "index.html"), path.join(artifacts, browserInfo.name)));
}
await fs.writeFile(path.join(artifacts, "summary.json"), JSON.stringify(results, null, 2), "utf8");
console.log(JSON.stringify(results.map(result => ({ browser: result.browser, state: result.state })), null, 2));
