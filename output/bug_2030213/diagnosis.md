# Bug 2030213 Diagnosis

Generated: 2026-05-25T22:45:52+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2030213
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox

## Bug Metadata

- Summary: www.doubao.com - can't paste images from clipboard into chatbox
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P3
- Platform / OS: Desktop / Windows

## Bugzilla Evidence

- Inferred Firefox versions: 136, 149.0
- Selected target URL: https://www.doubao.com/chat/
- Target URL candidates:
- https://www.doubao.com/chat/38419942456505090?channel=bing_sem (bug.url)
- https://www.doubao.com/chat/ (comment 18000953)
- Attachment metadata count: 0

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

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox/screenshot_firefox_1280x900.png (not created)
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox/screenshot_firefox_1440x1000.png (not created)
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox/screenshot_firefox_390x844.png (not created)

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: open https://www.doubao.com/chat/, copy an image to the clipboard, and paste it into the chat box.
- Firefox 136 evidence: the helper selected the comment-0 URL but did not produce Firefox screenshots for this page; all three screenshot entries exited 0 but were marked not created.
- Chrome 148 evidence: Chrome captured a loading screen with the Doubao avatar only; the chat input was not ready in the headless clean profile.
- Classification: blocked/partial. The clipboard paste step was not reached in either browser.

## Actual-vs-Expected Comparison

- Expected from comment 0: image paste succeeds.
- Actual from comment 0: Firefox cannot paste the image.
- Observed: the controlled run did not reach an interactive chat editor, so the expected/actual clipboard behavior could not be compared.

## Diagnosis

No live reproduction conclusion. The available evidence confirms the target URL and Firefox version selection, but the browser automation did not reach the chat box or clipboard paste step.

## Cause Analysis

Not performed because the bug was not reproduced. A valid next diagnosis needs an interactive session that reaches the chat editor and records paste-event data, especially `ClipboardEvent.clipboardData.items` MIME types in Firefox and Chrome.

## Confidence

Low for behavior diagnosis; medium that the current run is blocked before the relevant paste handler.

## Suggested Next Steps

- Reproduce manually or with browser automation that can grant clipboard access, place an image on the system clipboard, focus the Doubao editor, and dispatch a real paste.
- Compare Firefox and Chrome paste events for image MIME types, file items, and any site-side feature detection around clipboard support.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2030213/chrome
