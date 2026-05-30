# Bug 2031963 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2031963
Artifacts: output/bug_2031963/

## Bug Metadata

- Summary: www.temu.com - Scrolls the page when dragging the captcha elements
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: ARM / Android
- Bug URL: https://www.temu.com/pl/ul/kuiper/un3.html?_bg_fs=1

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9570128 `FF-vs-Chrome.mp4` (video/mp4): FF vs Chrome.mp4
- 9588270 `phabricator-D301665-url.txt` (text/x-phabricator-request): WIP: Bug 2031963 - Fast-path notify APZ on non-passive APZ-aware listener registration.

## Browser Versions

- Reported: Firefox Mobile 149/151 on Android 16.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`) with Android Firefox UA and mobile viewport. This is desktop Firefox emulation, not a physical Android/APZ environment.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`) with Android Chrome UA and mobile viewport.

## Controlled Browser Reproduction Evidence

- Firefox mobile-emulation probe: `output/bug_2031963/probe_firefox151_mobile/probe_state.json`.
- Chrome mobile-emulation probe: `output/bug_2031963/probe_chrome148_mobile/probe_state.json`.
- Reporter video frames: `output/bug_2031963/attachments/frames/`.
- Public Phabricator attachment: `output/bug_2031963/attachments/9588270_phabricator-D301665-url.txt`.

The current Temu CAPTCHA URL redirects both browsers to the Temu shopping homepage. No CAPTCHA was presented in either controlled probe, and the simulated drag produced no scroll delta. The reporter video does show the CAPTCHA dragging experience, and the attached Mozilla patch reference is titled around fast-path APZ notification for non-passive listener registration.

## Actual-vs-Expected Comparison

Site/environment drift plus device limitation. The live URL no longer exposes the CAPTCHA state in automation, and this environment is not a real Android APZ/touch stack.

## Diagnosis

Partial diagnosis. The original report likely involved Firefox Android's async pan/zoom handling of touch listeners on the CAPTCHA overlay, but the current site did not present that CAPTCHA and could not be reproduced here.

## Cause Analysis

Inferred from the Bugzilla attachment only: the suspected platform cause is late/non-passive touch listener registration not reaching APZ quickly enough, allowing background page panning while the CAPTCHA element is dragged. This inference is consistent with the attached Phabricator title, but it was not validated against the live page.

## Cause-Validation Test Cases

Not generated because the live CAPTCHA did not appear and the relevant behavior depends on Firefox Android APZ, not desktop browser emulation.

## Confidence

Medium for site drift/blocker; low-medium for inferred APZ cause.

## Suggested Next Steps

- Re-test on a physical Android device with Firefox 151/Nightly and Chrome, using the exact CAPTCHA variant from the reporter video.
- If reproduced, capture touch-event listener registration timing and APZ scroll handoff logs.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2031963/firefox/bugzilla_payload.json`
- Reporter video: `output/bug_2031963/attachments/9570128_FF-vs-Chrome.mp4`
- Phabricator attachment: `output/bug_2031963/attachments/9588270_phabricator-D301665-url.txt`
- Mobile-emulation probes: `output/bug_2031963/probe_firefox151_mobile/`, `output/bug_2031963/probe_chrome148_mobile/`
