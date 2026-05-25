# Bug 2016362 Diagnosis

Generated: 2026-05-25T22:43:47+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2016362
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox

## Bug Metadata

- Summary: Typing/Deleting issues on Coursera.org
- Product / Component: Web Compatibility / Site Reports
- Status: UNCONFIRMED
- Severity / Priority: S3 / P2
- Platform / OS: ARM64 / macOS

## Bugzilla Evidence

- Inferred Firefox versions: 147
- Selected target URL: https://www.coursera.org/
- Target URL candidates:
- https://www.coursera.org/ (bug.url)
- https://github.com/mozilla/bugbug/ (comment 17888718)
- https://support.mozilla.org/en-US/kb/diagnose-firefox-issues-using-troubleshoot-mode (comment 17890893)
- Attachment metadata count: 1

## Firefox Version Selection

- Requested major version: 147
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/147.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 147.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/147.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/147.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 147.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: go to Coursera, enroll in the Microsoft Back-End Developer Professional Certificate, open a specific guided lab, type long text, delete it, and separately leave a video tab open for about 12 hours.
- Firefox 147 evidence: Coursera homepage loaded, but the guided lab was not reachable without account/enrollment state.
- Chrome 148 evidence: Coursera homepage loaded and course cards populated, but the guided lab was not reached.
- Classification: blocked/partial. The required enrolled course/lab and 12-hour video condition were not available in this controlled run.

## Actual-vs-Expected Comparison

- Expected from comment 0: text can be entered/deleted without overlap; long-idle videos keep playing without lag.
- Actual from comment 0: text deletion/typing becomes visually confused; videos become choppy after long idle.
- Observed: neither browser reached the editor or long-idle video condition.

## Diagnosis

No live reproduction conclusion. The bug requires a logged-in, enrolled Coursera lab and a long-duration video test.

## Cause Analysis

Not performed because the reported behavior was not reproduced. Bugzilla discussion suspects a contenteditable/code-editor issue, possibly an editor with syntax highlighting, but the current evidence does not identify the site implementation.

## Confidence

Low for behavior diagnosis; high that the current run is blocked before the relevant workflow.

## Suggested Next Steps

- Reproduce with an enrolled account or a temporary free trial and capture the guided lab editor DOM.
- Compare Firefox and Chrome input, beforeinput, composition, selectionchange, and mutation behavior while typing/deleting long text.
- Split the video choppiness issue into a separate performance/media diagnosis if it is still in scope.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2016362/chrome
