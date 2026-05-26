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
    executablePath: "/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox",
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
    executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
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
  const casesById = Object.fromEntries(state.cases.map(item => [item.caseId, item]));
  const failing = casesById["display-contents"];
  const block = casesById["display-block"];
  const parent = casesById["parent-typography"];
  const childLineHeight = parsePx(failing.child.computed.lineHeight);
  const failingGap = failing.textLineTopDeltaMedian;
  const blockGap = block.textLineTopDeltaMedian;
  const parentGap = parent.textLineTopDeltaMedian;
  return {
    childLineHeightPx: round(childLineHeight),
    displayContents: {
      headlineHeightPx: round(failing.headline.rect.height),
      textLineTopDeltaMedianPx: round(failingGap),
      gapToChildLineHeightRatio: round(failingGap / childLineHeight),
    },
    displayBlock: {
      headlineHeightPx: round(block.headline.rect.height),
      textLineTopDeltaMedianPx: round(blockGap),
      gapToChildLineHeightRatio: round(blockGap / childLineHeight),
    },
    parentTypography: {
      headlineHeightPx: round(parent.headline.rect.height),
      textLineTopDeltaMedianPx: round(parentGap),
      gapToChildLineHeightRatio: round(parentGap / childLineHeight),
    },
  };
}

function validationFor(results) {
  const firefox = results.find(item => item.browserName === "firefox");
  const chrome = results.find(item => item.browserName === "chrome");
  const ffDisplayContentsRatio = firefox.summary.displayContents.gapToChildLineHeightRatio;
  const ffDisplayBlockRatio = firefox.summary.displayBlock.gapToChildLineHeightRatio;
  const chromeDisplayContentsRatio = chrome.summary.displayContents.gapToChildLineHeightRatio;
  const firefoxDisplayContentsSqueezed = ffDisplayContentsRatio < 0.8;
  const firefoxDisplayBlockUnsqueezed = ffDisplayBlockRatio > 0.9 && ffDisplayBlockRatio < 1.1;
  const chromeDisplayContentsUnsqueezed = chromeDisplayContentsRatio > 0.9 && chromeDisplayContentsRatio < 1.1;
  return {
    passed: firefoxDisplayContentsSqueezed && firefoxDisplayBlockUnsqueezed && chromeDisplayContentsUnsqueezed,
    criteria: {
      firefoxDisplayContentsSqueezed,
      firefoxDisplayBlockUnsqueezed,
      chromeDisplayContentsUnsqueezed,
    },
    explanation: "The cause is validated when Firefox squeezes only the display: contents path while Firefox's display:block control and Chrome's display:contents path both use the child line-height.",
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
        marginTop: style.marginTop,
        marginBottom: style.marginBottom,
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

    function deltas(rects) {
      const tops = [...new Set(rects.map(rect => rect.top))]
        .sort((a, b) => a - b);
      return tops.slice(1).map((top, index) => Number((top - tops[index]).toFixed(3)));
    }

    function median(values) {
      const sorted = values.filter(Number.isFinite).sort((a, b) => a - b);
      if (!sorted.length) {
        return null;
      }
      const middle = Math.floor(sorted.length / 2);
      return sorted.length % 2 ? sorted[middle] : (sorted[middle - 1] + sorted[middle]) / 2;
    }

    return {
      url: location.href,
      title: document.title,
      viewport: {
        innerWidth,
        innerHeight,
        devicePixelRatio,
      },
      cases: [...document.querySelectorAll(".testcase")].map(section => {
        const headline = section.querySelector(".headline");
        const child = section.querySelector(".decorator");
        const rects = textLineRects(headline);
        const topDeltas = deltas(rects);
        return {
          caseId: section.dataset.case,
          label: section.querySelector(".label").textContent.trim(),
          text: headline.textContent.trim().replace(/\s+/g, " "),
          headline: {
            rect: roundedRect(headline.getBoundingClientRect()),
            computed: computedSubset(headline),
          },
          child: {
            rect: roundedRect(child.getBoundingClientRect()),
            computed: computedSubset(child),
          },
          textLineRects: rects,
          textLineCount: rects.length,
          textLineTopDeltas: topDeltas,
          textLineTopDeltaMedian: median(topDeltas),
        };
      }),
    };
  });
}

async function runBrowser(config) {
  const outputDir = path.join(artifactDir, config.name);
  await fs.mkdir(outputDir, { recursive: true });
  const userDataDir = await fs.mkdtemp(path.join(os.tmpdir(), `bug-2005492-${config.name}-`));
  const launchOptions = {
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
  };
  const browser = await puppeteer.launch(launchOptions);
  try {
    const page = await browser.newPage();
    await page.goto(testcaseUrl, { waitUntil: "load", timeout: 30000 });
    await page.waitForFunction(() => document.fonts ? document.fonts.status === "loaded" : true, { timeout: 5000 }).catch(() => {});
    const state = await measurePage(page);
    const version = await browser.version();
    await page.screenshot({ path: path.join(outputDir, "screenshot.png"), fullPage: true });
    const result = {
      browserName: config.name,
      browserVersion: version,
      testcaseUrl,
      screenshot: path.join(outputDir, "screenshot.png"),
      statePath: path.join(outputDir, "state.json"),
      state,
      summary: summarizeMetrics(state),
    };
    await fs.writeFile(result.statePath, JSON.stringify(result, null, 2), "utf8");
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
