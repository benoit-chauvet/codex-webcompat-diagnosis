#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const root = path.resolve(new URL(".", import.meta.url).pathname);
const outDir = path.join(root, "artifacts", "firefox");
await fs.mkdir(outDir, { recursive: true });
const browser = await puppeteer.launch({
  browser: "firefox",
  executablePath: "/Applications/Firefox.app/Contents/MacOS/firefox",
  headless: true,
  userDataDir: path.join(outDir, "profile"),
  defaultViewport: { width: 640, height: 420, deviceScaleFactor: 1 },
});
try {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(path.join(root, "index.html")).href, { waitUntil: "domcontentloaded" });
  const state = await page.evaluate(() => JSON.parse(document.getElementById("state").textContent));
  await page.screenshot({ path: path.join(outDir, "firefox.png"), fullPage: false });
  await fs.writeFile(path.join(outDir, "firefox.json"), JSON.stringify(state, null, 2), "utf8");
  await fs.writeFile(path.join(root, "artifacts", "summary.json"), JSON.stringify({ firefox: state }, null, 2), "utf8");
  console.log(JSON.stringify({ firefox: state }, null, 2));
} finally {
  await browser.close();
}
