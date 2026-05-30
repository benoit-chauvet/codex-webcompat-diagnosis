# Bug 2042795 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2042795
Artifacts: output/bug_2042795/

## Bug Metadata

- Summary: www.gsmarena.com -  The embedded videos fail to load due to "No video with supported format and MIME type found" error
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P2
- Platform / OS: Desktop / Windows
- Bug URL: https://www.gsmarena.com/google_android_17_continue_on-news-72910.php

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9590355 `gsmarena-mime.mp4` (video/mp4): Unsupported video format Nightly vs Chrome

## Browser Versions

- Reported: Firefox 151 release and Firefox Nightly 153.0a1 on Windows.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`). Firefox Nightly 153 was installed but Puppeteer failed to launch it, so the controlled comparison uses release Firefox 151, which comment 0 also lists as affected.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox live probe: `output/bug_2042795/probe_firefox151/probe_state.json`.
- Chrome live probe: `output/bug_2042795/probe_chrome148/probe_state.json`.
- Downloaded media and codec probe: `output/bug_2042795/media/codec_probe.json`.
- Reporter video frames: `output/bug_2042795/attachments/frames/`.

On the live article, Chrome loaded and played both embedded MP4s (`readyState: 4`, no media errors). Firefox loaded the article but both embedded MP4s remained unplayable. The reduced testcase captured Firefox media errors saying the decoder may not handle the requested video format with YUV444 chroma subsampling.

The MP4 `avcC` boxes report H.264 `avcProfileIndication` 244, level 3.1 (`avc1.f4001f`) for both GSMArena videos. Chrome reports `canPlayType('video/mp4; codecs="avc1.f4001f"')` as `maybe`; Firefox returns an empty string.

## Actual-vs-Expected Comparison

Reproduced cross-browser issue. Firefox cannot play the embedded videos; Chrome can.

## Diagnosis

Firefox reproduces the reported "No video with supported format and MIME type found" failure because the article's MP4s are encoded with H.264 profile 244 / High 4:4:4 Predictive (`avc1.f4001f`), which Firefox's media pipeline rejects, while Chrome accepts and decodes them.

## Cause Analysis

The site serves H.264 profile-244 MP4s without a fallback encoding. Firefox's media support rejects that profile/chroma combination, producing media error code 3 in the testcase. Chrome supports or tolerates the encoding, so the same files play there. This is a content-encoding compatibility issue; serving normal H.264 High/Main profile 4:2:0, VP9, or AV1 fallback would avoid the Firefox failure.

## Cause-Validation Test Cases

- Reduced testcase: `output/bug_2042795/testcase/` with a control MP4 and both GSMArena profile-244 MP4s.
- Minimal testcase: `output/bug_2042795/minimal-testcase/` with one profile-244 MP4.
- Probe artifacts: `output/bug_2042795/testcase/artifacts/summary.json`, `output/bug_2042795/minimal-testcase/artifacts/summary.json`.

Validation results: Firefox plays the control MP4 but reports code 3 errors for both GSMArena MP4s; Chrome plays all three. The minimal testcase likewise fails in Firefox and plays in Chrome.

## Confidence

High. The live page reproduces, the media files were downloaded and probed, and the reduced/minimal testcases isolate the failing H.264 profile.

## Suggested Next Steps

- Ask GSMArena to transcode the embedded MP4s to broadly supported H.264 4:2:0 Main/High profile or provide a WebM/AV1 fallback.
- If Firefox intends to support this profile/chroma combination, file or link a Core media bug with the minimal testcase.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2042795/firefox/bugzilla_payload.json`
- Reporter video: `output/bug_2042795/attachments/9590355_gsmarena-mime.mp4`
- Live probes: `output/bug_2042795/probe_firefox151/`, `output/bug_2042795/probe_chrome148/`
- Downloaded MP4s and codec probe: `output/bug_2042795/media/`
- Testcases: `output/bug_2042795/testcase/`, `output/bug_2042795/minimal-testcase/`
