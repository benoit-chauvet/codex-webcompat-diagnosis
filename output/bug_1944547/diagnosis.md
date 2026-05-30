# Bug 1944547 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1944547
Artifacts: output/bug_1944547/

## Bug Metadata

- Summary: notebooklm.google.com - Unable to speak, stuck loading whenever you try to join the discussion in "Interactive mode"
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P2
- Platform / OS: Desktop / Windows 10
- Bug URL: https://notebooklm.google.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9462501 `image.png` (image/png): FF vs Chrome.png

## Browser Versions

- Reported: Firefox 133/134/136 on Windows 10, authenticated Google account required.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`); version mismatch, exploratory only.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox NotebookLM probe: `output/bug_1944547/probe_firefox151/probe_state.json`.
- Chrome NotebookLM probe: `output/bug_1944547/probe_chrome148/probe_state.json`.
- Reporter screenshot: `output/bug_1944547/attachments/9462501_image.png`.

Both browsers were redirected to Google sign-in before NotebookLM notebooks or Interactive Mode could be reached. The reported STR require creating/opening a notebook, generating an Audio Overview, entering Interactive Mode, clicking Play, and clicking Join.

## Actual-vs-Expected Comparison

Blocked/partial. The authenticated NotebookLM workflow was not reachable.

## Diagnosis

Partial diagnosis only. The reporter screenshot supports a Firefox-only stuck-loading state in NotebookLM Interactive Mode, but the controlled probes could only verify that login is required.

## Cause Analysis

Not determined. Firefox feature probing shows Web Speech recognition constructors absent while Chrome exposes them, which may be relevant to a spoken-interaction feature, but the NotebookLM code path was not reached and this remains an unvalidated hypothesis.

## Cause-Validation Test Cases

Not generated because the issue depends on a private Google account and generated NotebookLM content.

## Confidence

Low for root cause; high for authentication blocker.

## Suggested Next Steps

- Reproduce with a test Google account and a disposable notebook.
- Capture microphone, WebRTC/WebAudio, and Web Speech API usage from Play/Join through the stuck-loading state in Firefox and Chrome.

## Sources and Artifacts

- Bugzilla payload: `output/bug_1944547/firefox/bugzilla_payload.json`
- Reporter screenshot: `output/bug_1944547/attachments/9462501_image.png`
- Login probes: `output/bug_1944547/probe_firefox151/`, `output/bug_1944547/probe_chrome148/`
