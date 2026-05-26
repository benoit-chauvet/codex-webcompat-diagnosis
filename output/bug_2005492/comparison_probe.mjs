import fs from "node:fs/promises";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire("/Users/bchauvet/.codex/skills/bugzilla-firefox-diagnose/package.json");
const puppeteer = require("puppeteer-core");

const URL = "https://block.xyz/news";
const OUT_DIR = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/comparison";

const browsers = [
  {
    name: "firefox",
    executable: "/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox",
    product: "firefox",
  },
  {
    name: "chrome",
    executable: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    product: "chrome",
  },
];

const viewports = [
  { width: 1280, height: 900, deviceScaleFactor: 1 },
  { width: 1440, height: 1000, deviceScaleFactor: 1 },
  { width: 390, height: 844, deviceScaleFactor: 1 },
];

function launchArgs(browserName) {
  if (browserName !== "chrome") {
    return [];
  }
  return [
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
  ];
}

function firefoxPrefs() {
  return {
    "app.update.auto": false,
    "app.update.enabled": false,
    "browser.shell.checkDefaultBrowser": false,
    "browser.startup.homepage_override.mstone": "ignore",
    "browser.startup.page": 0,
  };
}

function compactError(error) {
  if (!error) {
    return null;
  }
  return {
    name: error.name || "Error",
    message: error.message || String(error),
  };
}

async function autoScroll(page) {
  await page.evaluate(async () => {
    await new Promise(resolve => {
      let total = 0;
      const step = Math.max(400, Math.floor(window.innerHeight * 0.75));
      const timer = setInterval(() => {
        window.scrollBy(0, step);
        total += step;
        if (total >= document.documentElement.scrollHeight - window.innerHeight) {
          clearInterval(timer);
          window.scrollTo(0, 0);
          resolve();
        }
      }, 100);
    });
  });
}

async function extractPageState(page) {
  return await page.evaluate(() => {
    const px = value => {
      const parsed = Number.parseFloat(value);
      return Number.isFinite(parsed) ? parsed : null;
    };
    const rectOf = element => {
      const rect = element.getBoundingClientRect();
      return {
        x: Number(rect.x.toFixed(2)),
        y: Number(rect.y.toFixed(2)),
        width: Number(rect.width.toFixed(2)),
        height: Number(rect.height.toFixed(2)),
        top: Number(rect.top.toFixed(2)),
        bottom: Number(rect.bottom.toFixed(2)),
      };
    };
    const selectorFor = element => {
      if (!element || element.nodeType !== Node.ELEMENT_NODE) {
        return "";
      }
      const pieces = [];
      let current = element;
      while (current && current.nodeType === Node.ELEMENT_NODE && pieces.length < 5) {
        const tag = current.localName;
        const id = current.id ? `#${CSS.escape(current.id)}` : "";
        const classes = [...current.classList].slice(0, 3).map(cls => `.${CSS.escape(cls)}`).join("");
        pieces.unshift(`${tag}${id}${classes}`);
        current = current.parentElement;
      }
      return pieces.join(" > ");
    };
    const computedSubset = element => {
      const style = getComputedStyle(element);
      return {
        display: style.display,
        position: style.position,
        overflow: style.overflow,
        overflowX: style.overflowX,
        overflowY: style.overflowY,
        width: style.width,
        maxWidth: style.maxWidth,
        minWidth: style.minWidth,
        height: style.height,
        maxHeight: style.maxHeight,
        minHeight: style.minHeight,
        fontFamily: style.fontFamily,
        fontSize: style.fontSize,
        lineHeight: style.lineHeight,
        fontWeight: style.fontWeight,
        fontStretch: style.fontStretch,
        fontVariationSettings: style.fontVariationSettings,
        letterSpacing: style.letterSpacing,
        wordSpacing: style.wordSpacing,
        whiteSpace: style.whiteSpace,
        wordBreak: style.wordBreak,
        overflowWrap: style.overflowWrap,
        textWrap: style.textWrap || style.getPropertyValue("text-wrap"),
        textOverflow: style.textOverflow,
        writingMode: style.writingMode,
        transform: style.transform,
        scale: style.scale,
        flex: style.flex,
        flexBasis: style.flexBasis,
        flexShrink: style.flexShrink,
        flexGrow: style.flexGrow,
        gridColumn: style.gridColumn,
        gridTemplateColumns: style.gridTemplateColumns,
        aspectRatio: style.aspectRatio,
        WebkitLineClamp: style.webkitLineClamp,
      };
    };
    const textLines = element => element.innerText
      .split(/\n+/)
      .map(line => line.trim())
      .filter(Boolean);
    const titleSelector = [
      "h1",
      "h2",
      "h3",
      "h4",
      "[class*='title' i]",
      "[class*='heading' i]",
      "[class*='headline' i]",
      "[class*='card' i] a",
    ].join(",");
    const titles = [...document.querySelectorAll(titleSelector)]
      .filter(element => {
        const rect = element.getBoundingClientRect();
        const text = element.innerText?.trim() || "";
        return text.length > 8 && rect.width > 0 && rect.height > 0;
      })
      .map((element, index) => {
        const style = getComputedStyle(element);
        const range = document.createRange();
        range.selectNodeContents(element);
        const lineRects = [...range.getClientRects()].map(rect => ({
          x: Number(rect.x.toFixed(2)),
          y: Number(rect.y.toFixed(2)),
          width: Number(rect.width.toFixed(2)),
          height: Number(rect.height.toFixed(2)),
        }));
        return {
          index,
          selector: selectorFor(element),
          tag: element.localName,
          className: element.className,
          text: element.innerText.trim().replace(/\s+/g, " ").slice(0, 240),
          rect: rectOf(element),
          scrollWidth: element.scrollWidth,
          clientWidth: element.clientWidth,
          scrollHeight: element.scrollHeight,
          clientHeight: element.clientHeight,
          lineCount: lineRects.length,
          lineRects: lineRects.slice(0, 12),
          fontSizePx: px(style.fontSize),
          lineHeightPx: px(style.lineHeight),
          computed: computedSubset(element),
          parentComputed: element.parentElement ? computedSubset(element.parentElement) : null,
        };
      });

    const candidateCards = [...document.querySelectorAll("article, li, a, [class*='card' i], [class*='tile' i]")]
      .filter(element => {
        const rect = element.getBoundingClientRect();
        const lines = textLines(element);
        return rect.width > 80 && rect.height > 40 && lines.length >= 2;
      });
    const seen = new Set();
    const cards = candidateCards
      .map(element => {
        const target = element.closest("article, li, [class*='card' i], [class*='tile' i]") || element;
        return target;
      })
      .filter(element => {
        if (seen.has(element)) {
          return false;
        }
        seen.add(element);
        return true;
      })
      .map((element, index) => {
        const lines = textLines(element);
        const images = element.querySelectorAll("img, picture, video, svg").length;
        const title = element.querySelector("h1,h2,h3,h4,[class*='title' i],[class*='heading' i],[class*='headline' i]");
        return {
          index,
          selector: selectorFor(element),
          tag: element.localName,
          className: element.className,
          rect: rectOf(element),
          imageLikeDescendants: images,
          lineCount: lines.length,
          lines: lines.slice(0, 8),
          titleText: title ? title.innerText.trim().replace(/\s+/g, " ").slice(0, 240) : null,
          titleRect: title ? rectOf(title) : null,
          computed: computedSubset(element),
          titleComputed: title ? computedSubset(title) : null,
        };
      });

    const cssRules = [];
    for (const sheet of [...document.styleSheets]) {
      let rules;
      try {
        rules = sheet.cssRules;
      } catch {
        continue;
      }
      for (const rule of [...rules]) {
        const text = rule.cssText || "";
        if (/(font-stretch|font-variation|font-width|writing-mode|text-wrap|line-clamp|scale|transform|grid|card|news)/i.test(text)) {
          cssRules.push(text.slice(0, 800));
        }
      }
    }

    return {
      url: location.href,
      title: document.title,
      viewport: {
        innerWidth,
        innerHeight,
        devicePixelRatio,
      },
      documentElement: {
        clientWidth: document.documentElement.clientWidth,
        clientHeight: document.documentElement.clientHeight,
        scrollWidth: document.documentElement.scrollWidth,
        scrollHeight: document.documentElement.scrollHeight,
      },
      fontsReady: !!document.fonts,
      bodyTextSample: document.body?.innerText.slice(0, 1800) || "",
      titles,
      cards,
      textOnlyCards: cards.filter(card => card.imageLikeDescendants === 0),
      cssRules: cssRules.slice(0, 200),
    };
  });
}

async function runOne(browserConfig, viewport) {
  const label = `${browserConfig.name}_${viewport.width}x${viewport.height}`;
  const runDir = path.join(OUT_DIR, label);
  await fs.rm(runDir, { recursive: true, force: true });
  await fs.mkdir(runDir, { recursive: true });

  const events = { console: [], pageErrors: [], requestFailures: [] };
  const launchOptions = {
    browser: browserConfig.product,
    executablePath: browserConfig.executable,
    headless: true,
    userDataDir: path.join(runDir, "profile"),
    defaultViewport: viewport,
    timeout: 90000,
    protocolTimeout: 90000,
    acceptInsecureCerts: true,
    args: launchArgs(browserConfig.name),
  };
  if (browserConfig.name === "firefox") {
    launchOptions.extraPrefsFirefox = firefoxPrefs();
  }

  const browser = await puppeteer.launch(launchOptions);
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(90000);
    page.setDefaultNavigationTimeout(90000);
    await page.setViewport(viewport);
    page.on("console", message => events.console.push({ type: message.type(), text: message.text() }));
    page.on("pageerror", error => events.pageErrors.push(compactError(error)));
    page.on("requestfailed", request => {
      events.requestFailures.push({
        url: request.url(),
        method: request.method(),
        resourceType: typeof request.resourceType === "function" ? request.resourceType() : null,
        failure: typeof request.failure === "function" ? request.failure() : null,
      });
    });

    let response = null;
    let navigationError = null;
    let networkIdleError = null;
    try {
      response = await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 90000 });
    } catch (error) {
      navigationError = compactError(error);
    }
    try {
      await page.waitForNetworkIdle({ idleTime: 1000, timeout: 15000 });
    } catch (error) {
      networkIdleError = compactError(error);
    }
    await page.waitForFunction(() => document.fonts ? document.fonts.status === "loaded" : true, { timeout: 15000 }).catch(() => {});
    await autoScroll(page);
    await page.evaluate(() => window.scrollTo(0, 0));
    await new Promise(resolve => setTimeout(resolve, 1000));

    const state = await extractPageState(page);
    const screenshot = path.join(runDir, "viewport.png");
    const fullPageScreenshot = path.join(runDir, "fullpage.png");
    await page.screenshot({ path: screenshot, fullPage: false });
    await page.screenshot({ path: fullPageScreenshot, fullPage: true });
    const payload = {
      ok: !navigationError,
      browser: browserConfig.name,
      executable: browserConfig.executable,
      requestedUrl: URL,
      finalUrl: page.url(),
      httpStatus: response ? response.status() : null,
      viewport,
      screenshot,
      fullPageScreenshot,
      navigationError,
      networkIdleError,
      events,
      state,
    };
    const jsonPath = path.join(runDir, "state.json");
    await fs.writeFile(jsonPath, JSON.stringify(payload, null, 2), "utf8");
    return {
      label,
      jsonPath,
      screenshot,
      fullPageScreenshot,
      ok: payload.ok,
      httpStatus: payload.httpStatus,
      finalUrl: payload.finalUrl,
      consoleCount: events.console.length,
      pageErrorCount: events.pageErrors.length,
      requestFailureCount: events.requestFailures.length,
      titleCount: state.titles.length,
      cardCount: state.cards.length,
      textOnlyCardCount: state.textOnlyCards.length,
    };
  } finally {
    await browser.close();
  }
}

async function main() {
  await fs.mkdir(OUT_DIR, { recursive: true });
  const results = [];
  for (const browserConfig of browsers) {
    for (const viewport of viewports) {
      console.log(`Running ${browserConfig.name} ${viewport.width}x${viewport.height}`);
      results.push(await runOne(browserConfig, viewport));
    }
  }
  await fs.writeFile(path.join(OUT_DIR, "summary.json"), JSON.stringify(results, null, 2), "utf8");
  console.log(JSON.stringify(results, null, 2));
}

main().catch(error => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
