# Bug 2028875 Diagnosis

Generated: 2026-05-25T22:43:09+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2028875
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox

## Bug Metadata

- Summary: swagtime.net -  Blank page is loaded
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P2
- Platform / OS: Desktop / Windows

## Bugzilla Evidence

- Inferred Firefox versions: 151, 148.0.2, 151.0a1
- Selected target URL: https://swagtime.net/
- Target URL candidates:
- https://swagtime.net/ (bug.url)
- https://wiki.mozilla.org/BugBot#missing_beta_status.py (comment 17988912)
- Attachment metadata count: 1

## Firefox Version Selection

- Requested major version: 151
- Allow version mismatch: False
- Selected Firefox: /Applications/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 151.0.1
- Firefox archive download notes:
- None found
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: open https://swagtime.net/ in a clean profile and observe whether the page loads.
- Firefox 151 evidence: the 1440x1000 and 390x844 screenshots are a uniform dark blank page, matching the reported Firefox actual result.
- Chrome 148 evidence: the 1280x900 and 390x844 screenshots show the SwagTime landing page with logo, navigation, content, and play CTA, matching the expected behavior.
- Classification: reproduced cross-browser issue.

## Actual-vs-Expected Comparison

- Expected from comment 0: the page loads accordingly.
- Actual from comment 0: blank page in Firefox.
- Observed: Firefox remains blank while Chrome renders the page.

## Diagnosis

The blank-page issue reproduces. The page shell loads an external module from `https://s3.swagtime.net/frontend-main/Ny42MzBa/assets/COmpH26D.js`; Firefox renders only the dark background, while Chrome completes the Vue app rendering.

## Cause Analysis

The current JavaScript bundle contains `nI=""` and later calls `new WebSocket(nI)`. Bugzilla comment 2 reported `DOMException: An invalid or illegal string was specified` during WebSocket creation, which is consistent with Firefox rejecting the empty WebSocket URL. Chrome continues rendering the app despite that construction, while Firefox appears to stop before the Vue app reaches the visible rendered state.

## Confidence

High for reproduction and likely cause. Medium for exact failure propagation because console capture was not available from the helper run.

## Suggested Next Steps

- Replace the empty WebSocket endpoint with an explicit `wss://...` URL or gate WebSocket creation until a valid endpoint is configured.
- Add a defensive `try/catch` around WebSocket creation so a connection setup failure cannot prevent app rendering.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2028875_chrome
