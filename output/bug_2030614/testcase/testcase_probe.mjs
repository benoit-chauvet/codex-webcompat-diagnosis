#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

async function run(mode) {
  const root = path.resolve(new URL(".", import.meta.url).pathname);
  const outDir = path.join(root, "artifacts", mode);
  await fs.mkdir(outDir, { recursive: true });
  const browser = await puppeteer.launch({
    browser: "firefox",
    executablePath: "/Applications/Firefox.app/Contents/MacOS/firefox",
    headless: true,
    userDataDir: path.join(outDir, "profile"),
    defaultViewport: { width: 1000, height: 680, deviceScaleFactor: 1 },
  });
  try {
    const page = await browser.newPage();
    await page.goto(`${pathToFileURL(path.join(root, "index.html")).href}?mode=${mode}`, { waitUntil: "domcontentloaded" });
    await new Promise(resolve => setTimeout(resolve, 1000));
    const state = await page.evaluate(() => JSON.parse(document.getElementById("state").textContent));
    await page.screenshot({ path: path.join(outDir, `${mode}.png`), fullPage: false });
    await fs.writeFile(path.join(outDir, `${mode}.json`), JSON.stringify(state, null, 2), "utf8");
    return state;
  } finally {
    await browser.close();
  }
}

const results = { broken: await run("broken"), fixed: await run("fixed") };
await fs.writeFile(path.join(path.resolve(new URL(".", import.meta.url).pathname), "artifacts", "summary.json"), JSON.stringify(results, null, 2), "utf8");
console.log(JSON.stringify(results, null, 2));
