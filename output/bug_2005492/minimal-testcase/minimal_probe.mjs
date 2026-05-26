import fs from "node:fs/promises";
import os from "node:os";
import path from "node:path";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const testcaseDir = path.dirname(fileURLToPath(import.meta.url));
const artifactDir = path.join(testcaseDir, "artifacts");
const testcaseUrl = pathToFileURL(path.join(testcaseDir, "index.html")).href;

const browsers = [
  {
    name: "firefox",
    browser: "firefox",
    executablePath: process.env.FIREFOX_BIN || "/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox",
    extraPrefsFirefox: {
      "app.update.auto": false,
      "app.update.enabled": false,
      "browser.shell.checkDefaultBrowser": false,
      "browser.startup.homepage_override.mstone": "ignore",
      "browser.startup.page": 0,
    },
  },
  {
    name: "chrome",
    browser: "chrome",
    executablePath: process.env.CHROME_BIN || "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    args: [
      "--no-first-run",
      "--no-default-browser-check",
      "--disable-background-networking",
    ],
  },
];

const viewport = { width: 1280, height: 900, deviceScaleFactor: 1 };

function round(value) {
  return Number.isFinite(value) ? Number(value.toFixed(3)) : null;
}

function parsePx(value) {
  const number = Number.parseFloat(value);
  return Number.isFinite(number) ? number : null;
}

function median(values) {
  const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
  if (!sorted.length) {
    return null;
  }
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
}

function summarizeMetrics(state) {
  const childLineHeight = parsePx(state.decorator.computed.lineHeight);
  const topDelta = state.textLineTopDeltaMedian;
  return {
    childLineHeightPx: round(childLineHeight),
    headlineHeightPx: round(state.headline.rect.height),
    textLineCount: state.textLineCount,
    textLineTopDeltaMedianPx: round(topDelta),
    gapToChildLineHeightRatio: round(topDelta / childLineHeight),
  };
}

function validationFor(results) {
  const firefox = results.find(item => item.browserName === "firefox");
  const chrome = results.find(item => item.browserName === "chrome");
  const firefoxSqueezed = firefox.summary.gapToChildLineHeightRatio < 0.8;
  const chromeUnsqueezed = chrome.summary.gapToChildLineHeightRatio > 0.9 && chrome.summary.gapToChildLineHeightRatio < 1.1;
  return {
    passed: firefoxSqueezed && chromeUnsqueezed,
    criteria: {
      firefoxSqueezed,
      chromeUnsqueezed,
    },
    explanation: "The minimal testcase passes when Firefox lays out the display: contents child with a line gap below the child line-height while Chrome uses the child line-height.",
  };
}

async function measurePage(page) {
  return await page.evaluate(() => {
    function roundedRect(rect) {
      return {
        x: Number(rect.x.toFixed(3)),
        y: Number(rect.y.toFixed(3)),
        width: Number(rect.width.toFixed(3)),
        height: Number(rect.height.toFixed(3)),
        top: Number(rect.top.toFixed(3)),
        right: Number(rect.right.toFixed(3)),
        bottom: Number(rect.bottom.toFixed(3)),
        left: Number(rect.left.toFixed(3)),
      };
    }

    function computedSubset(element) {
      const style = getComputedStyle(element);
      return {
        display: style.display,
        font: style.font,
        fontFamily: style.fontFamily,
        fontSize: style.fontSize,
        fontWeight: style.fontWeight,
        lineHeight: style.lineHeight,
      };
    }

    function textLineRects(element) {
      const walker = document.createTreeWalker(element, NodeFilter.SHOW_TEXT, {
        acceptNode(node) {
          return node.nodeValue.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT;
        },
      });
      const rects = [];
      while (walker.nextNode()) {
        const range = document.createRange();
        range.selectNodeContents(walker.currentNode);
        rects.push(...[...range.getClientRects()].map(roundedRect));
        range.detach();
      }
      return rects;
    }

    function median(values) {
      const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
      if (!sorted.length) {
        return null;
      }
      const middle = Math.floor(sorted.length / 2);
      return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
    }

    const headline = document.querySelector("#headline");
    const decorator = document.querySelector("#decorator");
    const textRects = textLineRects(headline);
    const lineTops = [...new Set(textRects.map(rect => rect.top))].sort((a, b) => a - b);
    const topDeltas = lineTops.slice(1).map((top, index) => Number((top - lineTops[index]).toFixed(3)));

    return {
      url: location.href,
      title: document.title,
      viewport: {
        innerWidth,
        innerHeight,
        devicePixelRatio,
      },
      headline: {
        rect: roundedRect(headline.getBoundingClientRect()),
        computed: computedSubset(headline),
      },
      decorator: {
        computed: computedSubset(decorator),
      },
      text: headline.textContent.trim().replace(/\s+/g, " "),
      textLineRects: textRects,
      textLineCount: textRects.length,
      textLineTopDeltas: topDeltas,
      textLineTopDeltaMedian: median(topDeltas),
    };
  });
}

async function runBrowser(config) {
  const outputDir = path.join(artifactDir, config.name);
  await fs.mkdir(outputDir, { recursive: true });
  const userDataDir = await fs.mkdtemp(path.join(os.tmpdir(), `bug-2005492-minimal-${config.name}-`));
  const browser = await puppeteer.launch({
    browser: config.browser,
    executablePath: config.executablePath,
    headless: true,
    userDataDir,
    defaultViewport: viewport,
    acceptInsecureCerts: true,
    timeout: 90000,
    protocolTimeout: 90000,
    args: config.args || [],
    extraPrefsFirefox: config.extraPrefsFirefox,
  });
  try {
    const page = await browser.newPage();
    await page.goto(testcaseUrl, { waitUntil: "load", timeout: 30000 });
    await page.waitForFunction(() => document.fonts ? document.fonts.status === "loaded" : true, { timeout: 5000 }).catch(() => {});
    const state = await measurePage(page);
    const version = await browser.version();
    const screenshot = path.join(outputDir, "screenshot.png");
    const statePath = path.join(outputDir, "state.json");
    await page.screenshot({ path: screenshot, fullPage: true });
    const result = {
      browserName: config.name,
      browserVersion: version,
      testcaseUrl,
      screenshot,
      statePath,
      state,
      summary: summarizeMetrics(state),
    };
    await fs.writeFile(statePath, JSON.stringify(result, null, 2), "utf8");
    return result;
  } finally {
    await browser.close();
  }
}

await fs.mkdir(artifactDir, { recursive: true });
const results = [];
for (const browserConfig of browsers) {
  results.push(await runBrowser(browserConfig));
}

const summary = {
  generatedAt: new Date().toISOString(),
  testcaseUrl,
  results: results.map(result => ({
    browserName: result.browserName,
    browserVersion: result.browserVersion,
    screenshot: result.screenshot,
    statePath: result.statePath,
    summary: result.summary,
  })),
  validation: validationFor(results),
};

const summaryPath = path.join(artifactDir, "summary.json");
await fs.writeFile(summaryPath, JSON.stringify(summary, null, 2), "utf8");
console.log(summaryPath);
if (!summary.validation.passed) {
  process.exitCode = 1;
}
