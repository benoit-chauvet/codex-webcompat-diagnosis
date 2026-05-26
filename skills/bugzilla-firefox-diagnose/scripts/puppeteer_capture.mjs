#!/usr/bin/env node
import fs from "node:fs/promises";
import path from "node:path";

function usage() {
  return `Usage: node puppeteer_capture.mjs --browser firefox|chrome --executable PATH --url URL --screenshot PATH --state PATH --profile-dir PATH --width N --height N [--timeout-ms N] [--wait-ms N] [--headful]`;
}

function requireValue(argv, index, name) {
  const value = argv[index + 1];
  if (!value || value.startsWith("--")) {
    throw new Error(`${name} requires a value`);
  }
  return value;
}

function parseArgs(argv) {
  const options = {
    timeoutMs: 90000,
    waitMs: 3000,
    headful: false,
    deviceScaleFactor: 1,
  };

  for (let index = 0; index < argv.length; index += 1) {
    const arg = argv[index];
    switch (arg) {
      case "--browser":
        options.browser = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--executable":
        options.executable = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--url":
        options.url = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--screenshot":
        options.screenshot = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--state":
        options.state = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--profile-dir":
        options.profileDir = requireValue(argv, index, arg);
        index += 1;
        break;
      case "--width":
        options.width = Number.parseInt(requireValue(argv, index, arg), 10);
        index += 1;
        break;
      case "--height":
        options.height = Number.parseInt(requireValue(argv, index, arg), 10);
        index += 1;
        break;
      case "--timeout-ms":
        options.timeoutMs = Number.parseInt(requireValue(argv, index, arg), 10);
        index += 1;
        break;
      case "--wait-ms":
        options.waitMs = Number.parseInt(requireValue(argv, index, arg), 10);
        index += 1;
        break;
      case "--device-scale-factor":
        options.deviceScaleFactor = Number.parseFloat(requireValue(argv, index, arg));
        index += 1;
        break;
      case "--headful":
        options.headful = true;
        break;
      case "--help":
      case "-h":
        console.log(usage());
        process.exit(0);
      default:
        throw new Error(`unknown argument: ${arg}`);
    }
  }

  const required = ["browser", "executable", "url", "screenshot", "state", "profileDir", "width", "height"];
  for (const key of required) {
    if (options[key] === undefined || options[key] === "") {
      throw new Error(`missing required option: ${key}`);
    }
  }
  if (!["firefox", "chrome"].includes(options.browser)) {
    throw new Error("--browser must be firefox or chrome");
  }
  if (!Number.isFinite(options.width) || !Number.isFinite(options.height)) {
    throw new Error("--width and --height must be numbers");
  }
  return options;
}

async function loadPuppeteer() {
  const errors = [];
  for (const packageName of ["puppeteer-core", "puppeteer"]) {
    try {
      const module = await import(packageName);
      return { packageName, puppeteer: module.default ?? module };
    } catch (error) {
      if (error?.code === "ERR_MODULE_NOT_FOUND" || String(error).includes(`Cannot find package '${packageName}'`)) {
        errors.push(`${packageName}: ${error.message}`);
        continue;
      }
      throw error;
    }
  }
  throw new Error(
    "Puppeteer is not installed. From the bugzilla-firefox-diagnose skill directory, run `npm install` " +
      "or install puppeteer-core where Node can resolve it.\n" +
      errors.join("\n")
  );
}

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

function optionalCall(target, methodName) {
  try {
    const method = target?.[methodName];
    return typeof method === "function" ? method.call(target) : null;
  } catch {
    return null;
  }
}

function sleep(milliseconds) {
  return new Promise(resolve => setTimeout(resolve, milliseconds));
}

async function main() {
  const options = parseArgs(process.argv.slice(2));
  await fs.mkdir(path.dirname(options.screenshot), { recursive: true });
  await fs.mkdir(path.dirname(options.state), { recursive: true });
  await fs.mkdir(options.profileDir, { recursive: true });

  const { packageName, puppeteer } = await loadPuppeteer();
  const events = {
    console: [],
    pageErrors: [],
    requestFailures: [],
  };

  const launchOptions = {
    browser: options.browser,
    executablePath: options.executable,
    headless: !options.headful,
    userDataDir: options.profileDir,
    defaultViewport: {
      width: options.width,
      height: options.height,
      deviceScaleFactor: options.deviceScaleFactor,
    },
    timeout: options.timeoutMs,
    protocolTimeout: options.timeoutMs,
    acceptInsecureCerts: true,
    args: launchArgs(options.browser),
  };
  if (options.browser === "firefox") {
    launchOptions.extraPrefsFirefox = firefoxPrefs();
  }

  const browser = await puppeteer.launch(launchOptions);
  try {
    const page = await browser.newPage();
    page.setDefaultTimeout(options.timeoutMs);
    page.setDefaultNavigationTimeout(options.timeoutMs);
    await page.setViewport({
      width: options.width,
      height: options.height,
      deviceScaleFactor: options.deviceScaleFactor,
    });

    page.on("console", message => {
      events.console.push({
        type: message.type(),
        text: message.text(),
      });
    });
    page.on("pageerror", error => {
      events.pageErrors.push(compactError(error));
    });
    page.on("requestfailed", request => {
      events.requestFailures.push({
        url: request.url(),
        method: request.method(),
        resourceType: optionalCall(request, "resourceType"),
        failure: optionalCall(request, "failure"),
      });
    });

    let response = null;
    let navigationError = null;
    let networkIdleError = null;
    try {
      response = await page.goto(options.url, {
        waitUntil: "domcontentloaded",
        timeout: options.timeoutMs,
      });
    } catch (error) {
      navigationError = compactError(error);
    }

    if (typeof page.waitForNetworkIdle === "function") {
      try {
        await page.waitForNetworkIdle({
          idleTime: 1000,
          timeout: Math.min(10000, options.timeoutMs),
        });
      } catch (error) {
        networkIdleError = compactError(error);
      }
    }

    if (options.waitMs > 0) {
      await sleep(options.waitMs);
    }

    const documentState = await page.evaluate(() => {
      const root = document.documentElement;
      const body = document.body;
      return {
        url: location.href,
        title: document.title,
        readyState: document.readyState,
        viewport: {
          innerWidth: window.innerWidth,
          innerHeight: window.innerHeight,
          devicePixelRatio: window.devicePixelRatio,
        },
        documentElement: root
          ? {
              clientWidth: root.clientWidth,
              clientHeight: root.clientHeight,
              scrollWidth: root.scrollWidth,
              scrollHeight: root.scrollHeight,
            }
          : null,
        bodyTextSample: body ? body.innerText.slice(0, 1000) : "",
      };
    });

    await page.screenshot({
      path: options.screenshot,
      fullPage: false,
    });

    const state = {
      ok: navigationError === null,
      browser: options.browser,
      executable: options.executable,
      puppeteerPackage: packageName,
      requestedUrl: options.url,
      finalUrl: page.url(),
      httpStatus: response ? response.status() : null,
      viewport: {
        width: options.width,
        height: options.height,
        deviceScaleFactor: options.deviceScaleFactor,
      },
      screenshot: options.screenshot,
      navigationError,
      networkIdleError,
      events,
      documentState,
    };
    await fs.writeFile(options.state, JSON.stringify(state, null, 2), "utf8");
    process.stdout.write(
      JSON.stringify({
        ok: state.ok,
        browser: state.browser,
        finalUrl: state.finalUrl,
        httpStatus: state.httpStatus,
        screenshot: state.screenshot,
        state: options.state,
        consoleCount: events.console.length,
        pageErrorCount: events.pageErrors.length,
        requestFailureCount: events.requestFailures.length,
        navigationError,
      }) + "\n"
    );
  } finally {
    await browser.close();
  }
}

main().catch(error => {
  console.error(error?.stack || error?.message || String(error));
  process.exit(1);
});
