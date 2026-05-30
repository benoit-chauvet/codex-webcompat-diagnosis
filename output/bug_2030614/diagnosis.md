# Bug 2030614 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2030614
Artifacts: output/bug_2030614/

## Bug Metadata

- Summary: www.aol.com - News hero carousels are missing context (title, description, links)
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Desktop / Windows 10
- Bug URL: https://www.aol.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9568137 `09.04.2026_11.37.10_REC.mp4` (video/mp4): Chr vs ff

## Browser Versions

- Reported: Firefox 149 on Windows 10.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`). This is a version mismatch from the original report, but it is the installed Firefox release and the reporter said Firefox release and Nightly were affected.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox live probe: `output/bug_2030614/probe2_firefox151/probe_state.json`, screenshot `aol_home_top.png`.
- Chrome live probe: `output/bug_2030614/probe_chrome148/probe_state.json`, screenshot `aol_home_top.png`.
- Reporter video frames: `output/bug_2030614/attachments/frames/`.

Firefox 151 loaded `https://www.aol.com/` with HTTP 200 after the consent dialog was accepted. The top carousel stayed as a grey skeleton: the probe found no visible hero title/image context in the carousel area, and the screenshot shows the large hero slot blank. Chrome 148 loaded the same URL with HTTP 200 and showed the hero image, source label, headline, secondary link, and slide controls.

Firefox also logged live-site JavaScript failures that Chrome did not log, including `window.wafer.controllers is undefined`, `window.wafer.ready is not a function`, and missing Wafer helper methods. Those failures match the blank skeleton state.

## Actual-vs-Expected Comparison

Reproduced cross-browser issue. Firefox shows the reported actual behavior, with the news hero context missing. Chrome shows the expected populated carousel context.

## Diagnosis

Firefox still reproduces the AOL hero-carousel failure on the current site. The carousel data is present lower in the page, but the top hero does not hydrate from placeholder state to populated image/title/link state.

## Cause Analysis

The most likely cause is a Firefox-only failure in AOL/Yahoo's Wafer bootstrap path. The live Firefox page throws before Wafer-dependent modules can initialize the hero carousel, while Chrome does not. The observed failure is sufficient to leave the carousel in its initial skeleton state.

This is based on live runtime evidence rather than source-map-level AOL code ownership: the proprietary page bundles are minified, and the exact ordering or feature-detection branch that makes Wafer undefined only in Firefox was not isolated.

## Cause-Validation Test Cases

- Reduced mock: `output/bug_2030614/testcase/`. Broken mode leaves the hero skeleton blank when `window.wafer.controllers.WaferBaseController` is missing; fixed mode defines the Wafer bootstrap and the title context appears.
- Minimal mock: `output/bug_2030614/minimal-testcase/`. It reduces the failure to unguarded `window.wafer.ready()` access leaving the hero unloaded.
- Probe artifacts: `output/bug_2030614/testcase/artifacts/summary.json` and `output/bug_2030614/minimal-testcase/artifacts/summary.json`.

The mock validates the failure mechanism seen on the live site, but it is not a standalone Firefox engine testcase because the proprietary AOL bundle branch that makes Wafer undefined was not reduced.

## Confidence

Medium-high for reproduction and failure mechanism; medium for root cause because the precise minified AOL script branch was not isolated.

## Suggested Next Steps

- Debug the AOL/Yahoo Wafer bootstrap order in Firefox, especially modules that call `window.wafer.ready` and `window.wafer.controllers.WaferBaseController` without guards.
- Add defensive guards or defer carousel/lazyload module startup until Wafer is initialized.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2030614/firefox/bugzilla_payload.json`
- Reporter video: `output/bug_2030614/attachments/9568137_09.04.2026_11.37.10_REC.mp4`
- Live probes: `output/bug_2030614/probe2_firefox151/`, `output/bug_2030614/probe_chrome148/`
- Testcases: `output/bug_2030614/testcase/`, `output/bug_2030614/minimal-testcase/`
