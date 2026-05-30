# Bug 2036757 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2036757
Artifacts: output/bug_2036757/

## Bug Metadata

- Summary: chatgpt.com - "Use voice" feature shows spinner stuck in a loading state, even though it's working
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Desktop / Windows 10
- Bug URL: https://chatgpt.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9582374 `04.05.2026_15.58.06_REC.mp4` (video/mp4): Chr vs ff

## Browser Versions

- Reported: Firefox 150 on Windows 10 with microphone permission granted.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`); version mismatch, exploratory only.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox public ChatGPT probe: `output/bug_2036757/probe_firefox151/probe_state.json`.
- Chrome public ChatGPT probe: `output/bug_2036757/probe_chrome148/probe_state.json`.
- Reporter video frames: `output/bug_2036757/attachments/frames/`.

Firefox reached the public logged-out ChatGPT UI. Chrome automation was served a 403/security verification page. The reported voice-mode bug requires a logged-in account and microphone permission, then clicking the voice icon.

## Actual-vs-Expected Comparison

Blocked/partial. The authenticated voice mode was not reachable in a clean automated profile.

## Diagnosis

Partial diagnosis only. The reporter video supports a Firefox-only spinner state after voice is activated, but the controlled environment could not enter the logged-in voice workflow.

## Cause Analysis

Not determined. Possible areas to inspect when credentials are available include microphone permission state, WebRTC/media capture startup, voice-mode WebSocket/WebRTC setup, and UI state transitions after the voice button click.

## Cause-Validation Test Cases

Not generated because the issue depends on a private authenticated ChatGPT session and microphone permission.

## Confidence

Low for root cause; medium for reproduction blocker and reporter evidence.

## Suggested Next Steps

- Reproduce with a test ChatGPT account and granted microphone permission in Firefox and Chrome.
- Capture console/network/media-device events from click through voice-mode activation, including spinner state transitions.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2036757/firefox/bugzilla_payload.json`
- Reporter video: `output/bug_2036757/attachments/9582374_04.05.2026_15.58.06_REC.mp4`
- Public probes: `output/bug_2036757/probe_firefox151/`, `output/bug_2036757/probe_chrome148/`
