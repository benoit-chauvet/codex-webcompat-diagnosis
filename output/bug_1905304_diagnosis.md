# Bug 1905304 Diagnosis

Generated: 2026-05-25T22:43:01+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1905304
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox

## Bug Metadata

- Summary: Magnifying glass is misaligned in the search field on webmd.com
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S4 / P3
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

- Inferred Firefox versions: 129, 129.0a1
- Selected target URL: https://www.webmd.com/drugs/2/drug-8791-718/hydrocortisone-butyrate-cream/details
- Target URL candidates:
- https://www.webmd.com/drugs/2/drug-8791-718/hydrocortisone-butyrate-cream/details (bug.url)
- Attachment metadata count: 2

## Firefox Version Selection

- Requested major version: 129
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/129.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 129.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/129.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/129.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 129.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: open the WebMD drug-details URL and inspect the magnifying glass inside the search field below "Can we help you find something else?".
- Firefox 129 evidence: the URL now renders a WebMD 404 page. At 1280x900 the "Can we help you find something else?" search field is absent, so the reported search-icon alignment cannot be inspected.
- Chrome 148 evidence: the same URL also renders a WebMD 404 page, but Chrome shows a replacement-page search field and Search button rather than the original drug-details search field from the Bugzilla attachment.
- Classification: site/environment drift. The live page no longer matches the original page state described by comment 0, so the reported magnifying-glass misalignment was not reproduced in a controlled comparison.

## Actual-vs-Expected Comparison

- Expected from comment 0: magnifying glass centered in the WebMD search field.
- Actual from comment 0: magnifying glass aligned slightly lower in Firefox.
- Observed now: both browsers are on a 404 replacement page; Firefox and Chrome differ in the replacement page content, but neither exposes the original search field needed to validate the icon alignment bug.

## Diagnosis

The original visual issue cannot be diagnosed from the current live URL. The Bugzilla attachment remains evidence that the issue existed on the previous page, but the controlled live comparison only demonstrates page drift.

## Cause Analysis

Not performed because the original bug was not reproduced. The current cross-browser difference appears to be WebMD's current 404-page behavior, not the reported icon alignment issue.

## Confidence

Medium that the live site has drifted; low for root-cause diagnosis of the original alignment issue.

## Suggested Next Steps

- Ask for a current WebMD URL that still contains the affected "Can we help you find something else?" search field.
- If the old page can be restored from an archive or internal test case, compare computed styles for the search input icon container in Firefox and Chrome.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1905304_chrome
