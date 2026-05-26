# Bug 2005492 Diagnosis

Generated: 2026-05-26T21:35:37+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2005492
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/firefox

## Bug Metadata

- Summary: block.xyz - Text for titles inside cards is squeezed
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S3 / P3
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

Comment 0 reports Firefox 146.0 on Windows 10. The steps are:

1. Navigate to `https://block.xyz/news`.
2. Observe the cards that have only text, no other elements.

Expected: text is rendered correctly. Actual: text is rendered squeezed. The reporter notes that it reproduces regardless of ETP state, reproduces in Firefox Nightly and release, and does not reproduce in Chrome.

Bugzilla has one public attachment, `9532341` (`11.12.2025_14.50.38_REC.mp4`, summary `Chr vs ff`), downloaded locally as `attachment_9532341.mp4`. Later Bugzilla history marks Firefox 146, 147, and 148 affected, and user-story metadata says the issue is significant visual impact across Windows, macOS, Linux, and Android.

## Firefox Version Selection

- Requested major version: 146
- Allow version mismatch: False
- Selected Firefox: `/private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox`
- Selected Firefox version output: `Mozilla Firefox 146.0`
- Firefox archive download: `https://archive.mozilla.org/pub/firefox/releases/146.0/mac/en-US/Firefox%20146.0.dmg`
- Candidate local Firefox builds: Firefox 151.0.1, Firefox Nightly 153.0a1, Firefox Developer Edition 152.0b1

## Chrome Version Selection

- Selected Chrome: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Selected Chrome version output: `Google Chrome 148.0.7778.179`

## Controlled Browser Reproduction Evidence

The live page returned HTTP 200 in both browsers with clean profiles and no console, page, or request-failure events in the focused probe. The current content has drifted since the December 2025 report, but the same Svelte card component and title layout still render on `https://block.xyz/news`.

Desktop viewport `1280x900`:

- Firefox document scroll height: 7226px; Chrome document scroll height: 7921px.
- First news title, `Jack Dorsey on Intelligence, Velocity, and the Next Chapter for Block at J.P. Morgan`: same title width and same 5-line wrap in both browsers, but Firefox title height is 96px with 19.2px line spacing; Chrome title height is 143.13px with 28.62px line spacing.
- Long 8-line title, `Uber and Block Expand Global Partnership to Transform Restaurant Operations and Launch Cash App Pay`: Firefox height is 153.6px; Chrome height is 229px.

Mobile-sized viewport `390x844`:

- Firefox document scroll height: 27561px; Chrome document scroll height: 29556px.
- Matching titles again have the same text width and line count, but Firefox line spacing stays near 19.2px while Chrome uses about 32.2px.

The reproduction classification is **reproduced cross-browser issue**: Firefox 146 shows squeezed card title text while Chrome renders the same content with the intended vertical spacing.

## Diagnosis

Firefox reproduces the reported actual behavior. The issue is not that Firefox wraps the titles into narrower columns: title widths and line counts match Chrome. The visible squeeze is vertical. Firefox lays the large card headline glyphs on much smaller line boxes, so adjacent lines are packed tightly and the whole news grid becomes substantially shorter than in Chrome.

The issue is triggered by the page's card heading markup and CSS. A representative card title is:

```html
<h3 class="headline svelte-12tp18c">
  <div class="css-zh33qs h4 svelte-1c1tzhq">...</div>
</h3>
```

The inner heading-size decorator sets `display: contents`, `font-size: var(--font-size)`, `font-family: var(--font-family-primary)`, and `line-height: var(--theme-line-height, var(--line-height))`; the `.h4` decorator sets `--line-height: 115%`. The outer card headline only sets `font-size: inherit`, and otherwise falls back to the browser's default `h3` line-height context.

In Firefox, the inner `display: contents` element computes to `font: 500 24.8833px / 28.6167px "Cash Sans", sans-serif`, but the actual multi-line title is positioned with roughly 19.2px line spacing from the outer `h3` context. In Chrome, the same text uses the inner decorator's roughly 28.62px line spacing.

## Cause Analysis

The likely root cause is a Firefox layout difference/bug involving line box construction for text whose typography comes from a `display: contents` descendant inside an `h3`. Firefox applies the descendant's larger font metrics to the glyphs, but the multi-line inline layout uses the parent heading's default 16px/normal line-height cadence. Chrome uses the descendant's computed line-height, producing the expected spacing.

The site can work around the bug by moving the heading typography onto a real box or by avoiding `display: contents` for this heading decorator. A Firefox-only probe confirmed that changing:

```css
h3.headline.svelte-12tp18c > .svelte-1c1tzhq { display: block !important; }
```

changes the first Firefox title from 96px high to 143.08px high, matching Chrome's 143.13px for the same 5-line title. This confirms that the card grid and wrapping are not the primary problem; the `display: contents` typography wrapper is.

## Confidence

High. The behavior reproduces under controlled Firefox 146 versus Chrome 148 automation, matches the reporter's Firefox-only visual complaint, and the CSS workaround changes Firefox's title metrics to Chrome-equivalent values.

## Suggested Next Steps

- File or link this to a Firefox layout issue for `display: contents` descendants contributing font/line-height to inline line boxes inside headings.
- For the site, avoid `display: contents` on the heading typography decorator, or apply `font-family`, `font-size`, `font-weight`, and `line-height` directly to `.headline.svelte-12tp18c` or to a real child box.
- Keep an explicit `line-height` on the card headline instead of relying on inherited typography through a box-suppressed element.

## Sources and Artifacts

- Bugzilla REST payload: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/firefox/bugzilla_payload.json`
- Reporter video attachment: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/attachment_9532341.mp4`
- Helper Firefox captures: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/firefox/`
- Controlled comparison captures and JSON: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/comparison/`
- Live CSS assets: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/css_assets/`
- Style probe: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/style_tags_probe.json`
- Workaround probe: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_2005492/fix_probe.json`
