# Bug 2042322 Diagnosis

Finalized: 2026-05-28T10:55:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2042322

## Bug Metadata

- Summary: www.tiktok.com - Mouse scrolling is unresponsive if up/down navigation arrows are not displayed on the page
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S4 / P2
- Platform / OS: Desktop / Windows
- Target URL: https://www.tiktok.com/de-DE/

## Bugzilla Evidence

Comment 0 reports Windows 10 with Firefox ESR 140.10.1 and Firefox Nightly 153.0a1. Steps: open TikTok, resize or zoom until the up/down navigation arrows disappear, then use the mouse wheel. Expected: mouse scrolling changes videos. Actual: mouse scrolling is unresponsive in Firefox; Chrome reportedly works. Attachment 9589656 (`tiktok-scroll.mp4`) was downloaded and frame-captured under `output/bug_2042322/attachments/frames/`.

## Browser Versions

- Firefox used by helper/focused probe: `/Applications/Firefox Nightly.app/Contents/MacOS/firefox` (`Mozilla Firefox 153.0a1`)
- Chrome used for comparison: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`)

## Controlled Browser Reproduction Evidence

- Firefox baseline: `output/bug_2042322/firefox/state_firefox_1280x900.json`
- Chrome baseline: `output/bug_2042322/chrome/state_chrome_1280x900.json`
- Narrow Firefox wheel probe: `output/bug_2042322/probe_firefox_narrow_clean2/probe_state.json`
- Narrow Chrome wheel probe: `output/bug_2042322/probe_chrome_narrow_clean2/probe_state.json`

At a 620x900 viewport after dismissing visible consent/notice UI, four mouse-wheel events did not change the visible TikTok video in either Firefox or Chrome. In both probes, `scrollY` stayed `0` and the visible `<video>` `currentSrc` stayed the same; only playback time changed.

## Actual-vs-Expected Comparison

Not reproduced as a Firefox-only issue. The current live page showed unresponsive wheel navigation in both Firefox Nightly and Chrome under the narrow no-arrow condition used by the probe.

## Diagnosis

The current behavior is not the reported Firefox-vs-Chrome split. It is either current TikTok site behavior in this environment/headless automation, or the reporter's exact window/zoom/content state is no longer matched by the live page.

## Cause Analysis

Not determined. Because Chrome did not satisfy the reported expected behavior in the controlled probe, there is no confirmed Firefox-only implementation difference to reduce.

## Cause-Validation Test Cases

Not generated because the issue was not reproduced as Firefox-only.

## Confidence

Medium. The narrow controlled probe directly exercised mouse-wheel input, but TikTok is highly dynamic and the result may depend on account, consent state, viewport, A/B bucket, or headed browser behavior.

## Suggested Next Steps

- Re-test manually in a headed browser with the exact reporter zoom/window size and record whether Chrome still advances videos when the arrows are hidden.
- If Chrome works manually, capture the wheel event target, active scroll container, and TikTok route/feed state in both browsers.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2042322/firefox/bugzilla_payload.json`
- Reporter video and frame captures: `output/bug_2042322/attachments/`
- Firefox/Chrome baseline and wheel artifacts: `output/bug_2042322/firefox/`, `output/bug_2042322/chrome/`, `output/bug_2042322/probe_firefox_narrow_clean2/`, `output/bug_2042322/probe_chrome_narrow_clean2/`
