# Bug 1961790 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1961790
Artifacts: output/bug_1961790/

## Bug Metadata

- Summary: translate.google.com - Voice input  is not supported
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Desktop / Windows 10
- Bug URL: https://translate.google.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9480247 `image.png` (image/png): Firefox.png

## Browser Versions

- Reported: Firefox 137/139 on Windows 10.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`); version mismatch, but current Firefox still lacks the required API.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox Translate probe: `output/bug_1961790/probe2_firefox151/probe_state.json`.
- Chrome Translate probe: `output/bug_1961790/probe2_chrome148/probe_state.json`.
- Reporter screenshot: `output/bug_1961790/attachments/9480247_image.png`.

Both browsers reached Google Translate after consent. The microphone button was present in both. Firefox feature support was `SpeechRecognition: false` and `webkitSpeechRecognition: false`; clicking the mic produced no listening state. Chrome feature support was `SpeechRecognition: true` and `webkitSpeechRecognition: true`; clicking the mic changed the UI to a listening/permission path and the captured text included "Stopped listening" after headless permission denial.

## Actual-vs-Expected Comparison

Reproduced cross-browser issue. Firefox cannot activate Google Translate voice input; Chrome can enter the voice-recognition flow.

## Diagnosis

Firefox reproduces the reported unsupported voice-input behavior because Google Translate's voice input depends on the Web Speech recognition API, exposed in Chrome as `SpeechRecognition` / `webkitSpeechRecognition`. Firefox does not expose that API in the tested release.

## Cause Analysis

This is a web-platform API support gap or site fallback gap. Google Translate uses browser speech-recognition constructors to implement microphone translation. Chrome provides them; Firefox does not. The site does not provide a Firefox-compatible fallback, so voice input cannot start.

## Cause-Validation Test Cases

- Reduced testcase: `output/bug_1961790/testcase/`. It checks the speech-recognition constructors and attempts to start recognition.
- Minimal testcase: `output/bug_1961790/minimal-testcase/`. It disables the voice button when the constructors are absent.
- Probe artifacts: `output/bug_1961790/testcase/artifacts/summary.json` and `output/bug_1961790/minimal-testcase/artifacts/summary.json`.

Validation results: Firefox reports both constructors absent and the testcase returns `unsupported`; Chrome reports both present and calls `start()`, then headless Chrome returns `not-allowed` because microphone permission is unavailable.

## Confidence

High. The live site and local testcases agree on the required browser API difference.

## Suggested Next Steps

- For Google, provide a Firefox fallback or a clearer unsupported-message path tied to Web Speech API availability.
- For Firefox platform work, this depends on Web Speech recognition API support/compatibility.

## Sources and Artifacts

- Bugzilla payload: `output/bug_1961790/firefox/bugzilla_payload.json`
- Reporter screenshot: `output/bug_1961790/attachments/9480247_image.png`
- Live probes: `output/bug_1961790/probe2_firefox151/`, `output/bug_1961790/probe2_chrome148/`
- Testcases: `output/bug_1961790/testcase/`, `output/bug_1961790/minimal-testcase/`
