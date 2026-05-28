#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

function arg(name, fallback = null) {
  const index = process.argv.indexOf(name);
  if (index === -1) {
    return fallback;
  }
  return process.argv[index + 1];
}

async function main() {
  const browserName = arg("--browser");
  const executablePath = arg("--executable");
  const pagePath = path.resolve(arg("--page", "index.html"));
  const outDir = path.resolve(arg("--out-dir", "artifacts"));
  await fs.mkdir(outDir, { recursive: true });

  const browser = await puppeteer.launch({
    browser: browserName,
    executablePath,
    headless: true,
    userDataDir: path.join(outDir, "profile"),
    defaultViewport: { width: 1280, height: 900, deviceScaleFactor: 1 },
    acceptInsecureCerts: true,
    args: browserName === "chrome" ? [
      "--no-first-run",
      "--no-default-browser-check",
      "--allow-file-access-from-files",
      "--autoplay-policy=no-user-gesture-required",
    ] : [],
    extraPrefsFirefox: browserName === "firefox" ? {
      "media.autoplay.default": 0,
      "browser.shell.checkDefaultBrowser": false,
      "browser.startup.page": 0,
    } : undefined,
  });

  try {
    const page = await browser.newPage();
    const events = { console: [], pageErrors: [] };
    page.on("console", message => events.console.push({ type: message.type(), text: message.text() }));
    page.on("pageerror", error => events.pageErrors.push({ name: error.name, message: error.message }));
    await page.goto(pathToFileURL(pagePath).href, { waitUntil: "domcontentloaded", timeout: 60000 });
    await page.evaluate(() => window.testcaseDone || new Promise(resolve => setTimeout(resolve, 4000))).catch(() => {});
    await new Promise(resolve => setTimeout(resolve, 2000));
    const state = await page.evaluate(() => ({
      url: location.href,
      title: document.title,
      testcaseResult: window.testcaseResult || null,
      videos: Array.from(document.querySelectorAll("video")).map((video, index) => ({
        index,
        currentSrc: video.currentSrc,
        readyState: video.readyState,
        networkState: video.networkState,
        paused: video.paused,
        currentTime: video.currentTime,
        duration: Number.isFinite(video.duration) ? video.duration : null,
        videoWidth: video.videoWidth,
        videoHeight: video.videoHeight,
        error: video.error ? {
          code: video.error.code,
          message: video.error.message,
        } : null,
      })),
      bodyText: document.body.innerText,
    }));
    const screenshot = path.join(outDir, `${browserName}.png`);
    await page.screenshot({ path: screenshot, fullPage: false });
    const result = { browser: browserName, executablePath, pagePath, screenshot, events, state };
    const statePath = path.join(outDir, `${browserName}.json`);
    await fs.writeFile(statePath, JSON.stringify(result, null, 2), "utf8");
    console.log(JSON.stringify({ browser: browserName, statePath, screenshot }));
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
