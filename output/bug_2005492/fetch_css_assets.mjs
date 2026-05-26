import fs from "node:fs/promises";
import path from "node:path";

const probePath = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/css_probe.json";
const outDir = "/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/css_assets";
const probe = JSON.parse(await fs.readFile(probePath, "utf8"));
const urls = [...new Set([
  ...probe.firefox.resourceUrls,
  ...probe.chrome.resourceUrls,
])].filter(url => /\.css(\?|$)/i.test(url));

await fs.mkdir(outDir, { recursive: true });
const matches = [];
for (const url of urls) {
  const response = await fetch(url);
  const text = await response.text();
  const name = path.basename(new URL(url).pathname);
  const filePath = path.join(outDir, name);
  await fs.writeFile(filePath, text, "utf8");
  const needles = [
    "headline",
    "svelte-12tp18c",
    "card-root",
    "imageTopElement",
    "line-height",
    "font-family",
    "--line-height",
    "font-size",
  ];
  for (const needle of needles) {
    let index = text.indexOf(needle);
    while (index !== -1) {
      matches.push({
        url,
        filePath,
        needle,
        offset: index,
        snippet: text.slice(Math.max(0, index - 500), Math.min(text.length, index + 1200)),
      });
      index = text.indexOf(needle, index + needle.length);
    }
  }
}

const matchPath = path.join(outDir, "matches.json");
await fs.writeFile(matchPath, JSON.stringify(matches, null, 2), "utf8");
console.log(JSON.stringify({ cssCount: urls.length, matchPath }, null, 2));
