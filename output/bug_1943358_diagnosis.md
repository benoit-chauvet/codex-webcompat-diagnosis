# Bug 1943358 Diagnosis

Generated: 2026-05-25T22:44:05+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1943358
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox

## Bug Metadata

- Summary: notion.so - "Reposition" feature for images does not work
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S3 / P2
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

- Inferred Firefox versions: 136, 134.0
- Selected target URL: https://www.notion.so/
- Target URL candidates:
- https://www.notion.so/ (bug.url)
- https://wiki.mozilla.org/BugBot#missing_beta_status.py (comment 17312176)
- https://www.notion.so/_assets/73155-2def67dbe976f2b2.js (comment 17337542)
- https://www.notion.so/_assets/floatingTableOfContents-4211eca2e9c2929d.js (comment 17337542)
- https://www.notion.so/_assets/91852-b680287d52efaae9.js (comment 17337542)
- https://searchfox.org/firefox-main/rev/55aaa33f526ad11857e3f2e07a87daef1aa56ad4/dom/events/EventStateManager.cpp#915,4111,4129-4130 (comment 17802765)
- Attachment metadata count: 2

## Firefox Version Selection

- Requested major version: 136
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 136.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 136.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: log in to Notion, open or create a page, add a cover, click Reposition, drag the cover, and observe whether the position saves.
- Firefox 136 evidence: Notion public landing page loaded.
- Chrome 148 evidence: Notion public landing page loaded.
- Classification: blocked/partial. Login/account state is required to reach the page-cover reposition workflow.

## Actual-vs-Expected Comparison

- Expected from comment 0: cover position changes and can be saved.
- Actual from comment 0: cover position resets and editing mode cancels in Firefox.
- Observed: the live run did not reach a Notion page editor in either browser.

## Diagnosis

No live reproduction conclusion from this run. The public Bugzilla artifacts and comments contain substantial prior diagnosis, but the controlled browser comparison is blocked by account/login requirements.

## Cause Analysis

Public Bugzilla analysis points to a Firefox editor/selection behavior difference. The downloaded reduced testcase contains a `contenteditable=true` ancestor wrapping a `contenteditable=false; user-select:none` child with a non-draggable image. Bugzilla comments report that dragging over the image changes/collapses selection in Firefox, which changes Notion's internal `default.state.stores.length` path and resets cover position; Chrome focuses differently and does not move the caret/selection the same way.

## Confidence

Low for live reproduction in this run; medium-high for the likely root-cause direction because a public reduced testcase is available.

## Suggested Next Steps

- Reproduce with a logged-in Notion test account and capture selectionchange/focus events during the Reposition drag.
- Use the downloaded reduction to pursue a Core editor/event-handling issue around focusing editing hosts and selection movement when mousing down on non-editable descendants.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_chrome
- Public reduction artifact: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1943358_firefox/reduction_9532054.html
