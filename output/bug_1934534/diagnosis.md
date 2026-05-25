# Bug 1934534 Diagnosis

Generated: 2026-05-25T23:38:24+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1934534
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox

## Bug Metadata

- Summary: thnet.gov.cn - Scrolling does not work
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P3
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

- Inferred Firefox versions: 135, 132.0.2
- Selected target URL: https://zs.thnet.gov.cn/index
- Target URL candidates:
- https://zs.thnet.gov.cn/index (bug.url)
- https://wiki.mozilla.org/BugBot#missing_beta_status.py (comment 17240531)
- Comment 0 environment: Windows 10, Firefox 132.0.2 release / 133 / 135.
- Comment 0 precondition: clean profile.
- Comment 0 steps: navigate to `https://zs.thnet.gov.cn/index`, then try scrolling with the mouse wheel.
- Comment 0 expected result: the page can be scrolled.
- Comment 0 actual result: unable to scroll the page.
- Comment 0 notes: reproducible in Firefox release and Nightly, independent of ETP, works in Chrome.
- Public attachments: none.

## Firefox Version Selection

- Requested major version: 135
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/135.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 135.0
- Firefox archive download notes:
- Downloading Firefox 135.0 from https://archive.mozilla.org/pub/firefox/releases/135.0/mac/en-US/Firefox%20135.0.dmg
- Installed Firefox archive build at /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/135.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/135.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 135.0
- Note: after the helper run, the writable cached app bundle was observed reporting Firefox 151.0.1. To avoid relying on a cache that could be updated by Firefox, the controlled interaction evidence below was rerun from the downloaded Firefox 135.0 DMG mounted read-only.
- Controlled interaction probe used the downloaded Firefox 135.0 DMG mounted read-only at `/private/tmp/bug1934534_ff135_mnt/Firefox.app/Contents/MacOS/firefox`; WebDriver capabilities report `browserVersion: 135.0`, build ID `20250130195129`, and user agent `Firefox/135.0`.

## Chrome Version Selection

- Selected Chrome: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Controlled interaction probe used HeadlessChrome/148.0.0.0 with Chrome DevTools Protocol 1.3.

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/screenshot_firefox_390x844.png
- Controlled 1280x900 Firefox 135 before wheel: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/screenshot_firefox135_webdriver_before_wheel.png`
- Controlled 1280x900 Firefox 135 after wheel: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/screenshot_firefox135_webdriver_after_wheel.png`
- Controlled 1280x900 Chrome before wheel: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/chrome/screenshot_chrome_1280x900_before_wheel.png`
- Controlled 1280x900 Chrome after wheel: `/Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/chrome/screenshot_chrome_1280x900_after_wheel.png`
- Firefox scroll probe before wheel: `scrollY = 0`, `documentElement.scrollTop = 0`, `.homePage-body` computed transform `none`, `#homePage` overflow `hidden`, `.homePage` overflow `hidden`.
- Firefox scroll probe after wheel: unchanged, with `scrollY = 0`, `documentElement.scrollTop = 0`, and `.homePage-body` computed transform `none`.
- Chrome scroll probe before wheel: `scrollY = 0`, `documentElement.scrollTop = 0`, `.homePage-body` computed transform `none`, `#homePage` overflow `hidden`, `.homePage` overflow `hidden`.
- Chrome scroll probe after wheel: page section advanced via `.homePage-body` inline transform `translateY(-900px)` and computed transform `matrix(1, 0, 0, 1, 0, -900)`.
- Screenshot diff check: Firefox before/after changed only 512 pixels near the bottom edge; Chrome before/after changed 1,128,201 pixels across the viewport.

## Actual-vs-Expected Comparison

- Firefox 135 matches comment 0 actual behavior: mouse-wheel input does not advance the page, and native page scroll remains at zero.
- Chrome 148 matches comment 0 expected behavior: the same wheel input advances the full-screen page to the next section.
- Classification: reproduced cross-browser issue.

## Diagnosis

Reproduced. The page implements a custom full-screen section scroller and disables native overflow. In Firefox 135, wheel input leaves the page at the initial section; in Chrome 148, wheel input advances the section container by one viewport height. This matches the reporter's Firefox-broken / Chrome-working result.

## Cause Analysis

The site relies on the legacy non-standard `mousewheel` event for desktop wheel navigation. The downloaded app bundle attaches the handler as `on:{mousewheel:function(e){ e.preventDefault(); t.mouseWheel(...) }}` on `.homePage-body`. That handler increments/decrements `itemIndex` and calls `handleMove()`, which sets `.homePage-body.style.transform` to `translateY(...)`.

Firefox does not dispatch the legacy `mousewheel` event for normal wheel input; it dispatches the standard `wheel` event. Because the page also sets the full-screen wrapper to `height:100vh; overflow:hidden` and keeps `#homePage` overflow hidden, there is no native scrolling fallback. Chrome still dispatches the legacy compatibility event, so the custom `mouseWheel` handler runs and moves the section container.

Likely site fix: listen for the standard `wheel` event, preferably with a non-passive listener only if `preventDefault()` is required, and keep the existing `mousewheel` listener only as a legacy fallback. The handler should read `deltaY` from the `WheelEvent`.

## Confidence

High. The controlled probe reproduces the Firefox-vs-Chrome behavior with the requested Firefox major version, and the page bundle directly explains the browser difference.

## Suggested Next Steps

- Ask the site to replace `mousewheel`-only handling with standard `wheel` handling.
- A reduced testcase can be built from a `height:100vh; overflow:hidden` container plus `mousewheel`-only section transform logic.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/chrome
- Scroll probe results: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/scroll_probe_results.json
- Scroll probe script: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/scroll_probe.py
- Downloaded page assets inspected:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/app.bd8a8f0c.js
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1934534/firefox/app.cdd6f78f.css
