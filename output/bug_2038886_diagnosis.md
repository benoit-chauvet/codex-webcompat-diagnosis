# Bug 2038886 Diagnosis

Generated: 2026-05-25T22:43:57+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2038886
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox

## Bug Metadata

- Summary: devforum.roblox.com - "Copy Link to Highlight" fails to highlight the targeted text when opened in a newly loaded tab
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S4 / P3
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

- Inferred Firefox versions: 150.0, 152.0a1
- Selected target URL: https://devforum.roblox.com/t/beta-roplus-free-roblox-enhancement-extension/4369102/39
- Target URL candidates:
- https://devforum.roblox.com/t/beta-roplus-free-roblox-enhancement-extension/4369102/39 (bug.url)
- https://github.com/webcompat/web-bugs/issues/220599 (comment 18078769)
- https://wiki.mozilla.org/BugBot#missing_beta_status.py (comment 18078778)
- Attachment metadata count: 1

## Firefox Version Selection

- Requested major version: 150
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/150.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 150.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/150.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/150.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 150.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_text_fragment_chrome/screenshot_chrome_1280x900.png

## Controlled Browser Comparison

- Comment 0 steps: open the Roblox DevForum post, select text, use "Copy Link to Highlight", load the generated text-fragment URL in a new tab, and observe whether the selected text is highlighted.
- Firefox 150 evidence: the base page loaded and the target text was visible. The helper did not automate context-menu "Copy Link to Highlight" or a new-tab text-fragment navigation.
- Chrome 148 evidence: command-line Chrome captures of the base URL and a manually constructed text-fragment URL produced blank screenshots in this environment; a recapture with virtual time budget timed out without a screenshot.
- Classification: blocked/partial. The exact first-comment steps were not completed in a controlled Firefox-vs-Chrome comparison.

## Actual-vs-Expected Comparison

- Expected from comment 0: selected text appears highlighted when the copied text-fragment URL is opened in a new tab.
- Actual from comment 0: selected text does not appear highlighted in Firefox on a fresh load.
- Observed: no controlled highlight comparison was obtained.

## Diagnosis

The local run is partial. Bugzilla public comments provide a plausible direction: Discourse appears to mutate history/URL state during load, and Firefox loses or fails to apply the text-fragment highlight on fresh navigation while same-tab navigation can work.

## Cause Analysis

Not confirmed locally. Bugzilla comment 3 suggests the site may `pushState` over the anchor/text fragment; comment 4 notes a simple `pushState` testcase also breaks Chrome, so the real Discourse behavior likely has an additional timing or navigation-state factor. A real diagnosis needs instrumentation of `history.pushState`, `location.hash`, and text-fragment highlight timing in both browsers during a fresh load.

## Confidence

Low for local reproduction; medium that history/text-fragment handling is the right investigation area based on public Bugzilla analysis.

## Suggested Next Steps

- Reproduce interactively in both browsers using the native "Copy Link to Highlight" command.
- Capture the generated URL, then record fresh-tab navigation with `history.pushState` instrumentation and compare whether the text fragment remains available long enough for highlighting.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_chrome
- Chrome text-fragment artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2038886_text_fragment_chrome
