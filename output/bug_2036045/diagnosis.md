# Bug 2036045 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2036045
Artifacts: output/bug_2036045/

## Bug Metadata

- Summary: The video thumbnails from the AOL videos website are only loaded after a page refresh
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P2
- Platform / OS: Desktop / All
- Bug URL: https://www.aol.com/video/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9575428 `The videos from AOL are only loaded after a refresh.mp4` (video/mp4): The videos from AOL are only loaded after a refresh.mp4

## Browser Versions

- Reported: Firefox 151 beta/release family; affected across macOS, Windows, Ubuntu.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`).
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox live probe after consent: `output/bug_2036045/probe2_firefox151/probe_state.json`, screenshots `aol_video_first_load.png` and `aol_video_after_reload.png`.
- Chrome live probe: `output/bug_2036045/probe_chrome148/probe_state.json`.
- Reporter video frames: `output/bug_2036045/attachments/frames/`.

Firefox loaded `https://www.aol.com/video/` with HTTP 200, but video-card images stayed on AOL's 1x1 `lazyload/blank.gif` placeholder. Chrome loaded the same page and resolved the thumbnail image URLs to `s.aolcdn.com/images/dims?...` assets with natural width 600. In this run, Firefox still showed placeholders after reload, so the current behavior is at least as broken as the reported first-load-only symptom.

Firefox logged Wafer initialization errors including `window.wafer.controllers is undefined`, `window.wafer.ready is not a function`, and missing Wafer helper methods. Chrome did not log those Wafer errors.

## Actual-vs-Expected Comparison

Reproduced cross-browser issue. Firefox leaves AOL video thumbnails as placeholders; Chrome loads the thumbnails.

## Diagnosis

Firefox reproduces the AOL video thumbnail-loading failure. The page text and card structure load, but the lazyload step that swaps placeholder GIFs for real thumbnails does not run correctly in Firefox.

## Cause Analysis

The likely cause is the same AOL/Yahoo Wafer bootstrap failure seen on the AOL home page. Firefox throws in Wafer-dependent code before the lazy image loader can replace `blank.gif` placeholders with thumbnail URLs. Chrome executes the page without those Wafer bootstrap errors and the thumbnails load.

The exact minified AOL script branch that leaves Wafer undefined only in Firefox was not reduced.

## Cause-Validation Test Cases

- Reduced mock: `output/bug_2036045/testcase/`. Broken mode leaves thumbnail `src` values on a 1x1 GIF because `window.wafer.ready` is missing; fixed mode defines Wafer and swaps real thumbnail data URIs in.
- Minimal mock: `output/bug_2036045/minimal-testcase/`.
- Probe artifacts: `output/bug_2036045/testcase/artifacts/summary.json` and `output/bug_2036045/minimal-testcase/artifacts/summary.json`.

The testcase validates that the observed Wafer initialization failure is sufficient to produce the same placeholder-thumbnail symptom. It is a site-failure mock, not a standalone Firefox engine reduction.

## Confidence

High for reproduction; medium for root cause because the proprietary Wafer bundle was not fully reduced.

## Suggested Next Steps

- Fix or guard AOL's Wafer bootstrap so lazyload code only runs after `window.wafer.ready` and required controllers/helpers exist.
- Add telemetry/logging around image lazyload initialization to catch placeholder images that never swap to real thumbnails.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2036045/firefox/bugzilla_payload.json`
- Reporter video: `output/bug_2036045/attachments/9575428_The videos from AOL are only loaded after a refresh.mp4`
- Live probes: `output/bug_2036045/probe2_firefox151/`, `output/bug_2036045/probe_chrome148/`
- Testcases: `output/bug_2036045/testcase/`, `output/bug_2036045/minimal-testcase/`
