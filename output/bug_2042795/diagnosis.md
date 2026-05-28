# Bug 2042795 Diagnosis

Finalized: 2026-05-28T10:55:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2042795

## Bug Metadata

- Summary: www.gsmarena.com - The embedded videos fail to load due to "No video with supported format and MIME type found" error
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P2
- Platform / OS: Desktop / Windows
- Target URL: https://www.gsmarena.com/google_android_17_continue_on-news-72910.php

## Bugzilla Evidence

Comment 0 reports a clean-profile Windows reproduction in Firefox 151.0 release and Firefox Nightly 153.0a1. The steps are to open the GSMArena article, scroll to the embedded videos, and observe that Firefox shows "No video with supported format and MIME type found"; Chrome is reported to play the videos. Attachment 9590355 (`gsmarena-mime.mp4`) shows the same split-screen behavior: Firefox shows the unsupported-format panel while Chrome plays the article videos.

## Browser Versions

- Firefox used by helper/focused probe: `/Applications/Firefox Nightly.app/Contents/MacOS/firefox` (`Mozilla Firefox 153.0a1`)
- Chrome used for comparison: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`)
- Helper also found local Firefox 151.0.2 and Firefox Developer Edition 152.0b1.

## Controlled Browser Reproduction Evidence

- Firefox baseline screenshots: `output/bug_2042795/firefox/screenshot_firefox_1280x900.png`, `screenshot_firefox_1440x1000.png`, `screenshot_firefox_390x844.png`
- Focused Firefox probe: `output/bug_2042795/probe_firefox/gsmarena_videos.png` and `probe_state.json`
- Focused Chrome probe: `output/bug_2042795/probe_chrome/gsmarena_videos.png` and `probe_state.json`
- Downloaded site media inspected: `output/bug_2042795/site_video/gsmarena_001.mp4`, `gsmarena_002.mp4`

The focused probe scrolled to the article videos and called `load()` plus muted `play()` on both `<video>` elements. Firefox showed the unsupported-format panel. Chrome decoded and displayed both videos. In Firefox, the GSMArena videos did not advance to playable state; in Chrome both reached `readyState: 4`, `networkState: 1`, with nonzero `currentTime`.

## Actual-vs-Expected Comparison

Reproduced as a Firefox-only compatibility issue. Firefox matches the reported actual behavior. Chrome matches the expected behavior.

## Diagnosis

GSMArena serves the embedded videos as MP4 files with `Content-Type: video/mp4`, but the H.264 stream is encoded with profile `0xf4` (`avc1.f4001f`, High 4:4:4 Predictive / YUV444). Firefox rejects this stream, while Chrome on this machine decodes it.

## Cause Analysis

The MP4 container is valid and the response headers are not the failing condition: `curl -I` showed `content-type: video/mp4` and `accept-ranges: bytes`. The failing condition is the video codec profile/chroma format. The `avcC` box in both GSMArena MP4s advertises profile byte `0xf4`; the reduced testcase records Firefox's media error:

`Decoder may not have the capability to handle the requested video format with YUV444 chroma subsampling.`

This explains the page-level symptom: the site provides only `video/mp4` sources for those embeds, with no lower-profile H.264 or WebM fallback, so Firefox has no playable source.

## Cause-Validation Test Cases

- Reduced testcase: `output/bug_2042795/testcase/index.html`
- Reduced testcase probe: `output/bug_2042795/testcase/testcase_probe.mjs`
- Reduced testcase artifacts:
  - Firefox: `output/bug_2042795/testcase/artifacts/firefox/firefox.json`, `firefox.png`
  - Chrome: `output/bug_2042795/testcase/artifacts/chrome/chrome.json`, `chrome.png`
- Minimal testcase: `output/bug_2042795/minimal-testcase/index.html`
- Minimal artifacts:
  - Firefox: `output/bug_2042795/minimal-testcase/artifacts/firefox/firefox.json`, `firefox.png`
  - Chrome: `output/bug_2042795/minimal-testcase/artifacts/chrome/chrome.json`, `chrome.png`

Pass/fail criteria: the failing sample (`avc1.f4001f`) should fail in Firefox and play in Chrome; the control sample (`avc1.64001f`) should play in both. Results matched that criterion. Firefox failed only the YUV444/High 4:4:4 sample and played the normal H.264 High-profile control.

## Confidence

High. The live site reproduction, reporter video, MP4 header inspection, and reduced testcase all point to unsupported H.264 YUV444 media as the cause.

## Suggested Next Steps

- Site fix: re-encode the embedded videos as broadly supported H.264 4:2:0, e.g. `avc1.64001f`, and/or provide WebM fallback sources.
- Browser-side triage: this is also useful evidence for whether Firefox should improve the user-facing error or support path for H.264 YUV444 streams.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2042795/firefox/bugzilla_payload.json`
- Reporter attachment and frames: `output/bug_2042795/attachments/gsmarena-mime.mp4`, `output/bug_2042795/attachments/frames/`
- Firefox/Chrome focused probe artifacts: `output/bug_2042795/probe_firefox/`, `output/bug_2042795/probe_chrome/`
- Reduced and minimal test cases: `output/bug_2042795/testcase/`, `output/bug_2042795/minimal-testcase/`
