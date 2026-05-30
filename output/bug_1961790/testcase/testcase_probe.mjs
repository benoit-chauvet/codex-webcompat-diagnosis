#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

async function run(name, executablePath, root, file = "index.html") {
  const outDir = path.join(root, "artifacts", name);
  await fs.mkdir(outDir, { recursive: true });
  const browser = await puppeteer.launch({
    browser: name,
    executablePath,
    headless: true,
    userDataDir: path.join(outDir, "profile"),
    defaultViewport: { width: 900, height: 620, deviceScaleFactor: 1 },
    args: name === "chrome" ? ["--no-first-run", "--no-default-browser-check"] : [],
  });
  try {
    const page = await browser.newPage();
    await page.goto(pathToFileURL(path.join(root, file)).href, { waitUntil: "domcontentloaded" });
    await page.click("#mic").catch(() => {});
    await new Promise(resolve => setTimeout(resolve, 1500));
    const state = await page.evaluate(() => JSON.parse(document.getElementById("state").textContent));
    await page.screenshot({ path: path.join(outDir, `${name}.png`), fullPage: false });
    await fs.writeFile(path.join(outDir, `${name}.json`), JSON.stringify(state, null, 2), "utf8");
    return { browser: name, state };
  } finally {
    await browser.close();
  }
}

const root = path.resolve(new URL(".", import.meta.url).pathname);
const results = [
  await run("firefox", "/Applications/Firefox.app/Contents/MacOS/firefox", root),
  await run("chrome", "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", root),
];
await fs.writeFile(path.join(root, "artifacts", "summary.json"), JSON.stringify(results, null, 2), "utf8");
console.log(JSON.stringify(results, null, 2));
