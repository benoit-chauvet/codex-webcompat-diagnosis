# Bug 1852768 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1852768
Artifacts: output/bug_1852768/

## Bug Metadata

- Summary: The PiP option is missing from the video player at vimeo.com
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Other / Android
- Bug URL: https://vimeo.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9352689 `Screenshot_1.png` (image/png): Screenshot_1.png

## Browser Versions

- Reported: Firefox Android Nightly 119 and release, Android 12, login required.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`) with Android Firefox UA and mobile viewport. This is not a physical Android browser.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`) with Android Chrome UA and mobile viewport.

## Controlled Browser Reproduction Evidence

- Firefox mobile-emulation probe: `output/bug_1852768/probe_firefox151_mobile/probe_state.json`.
- Chrome mobile-emulation probe: `output/bug_1852768/probe_chrome148_mobile/probe_state.json`.
- Reporter screenshot: `output/bug_1852768/attachments/9352689_Screenshot_1.png`.

The target Vimeo video currently shows "This video contains mature content" and requires joining/logging in to watch. No `<video>` element was exposed in either browser probe. Feature probing with mobile UAs showed Chrome exposing `requestPictureInPicture`, while Firefox did not expose it in this desktop-emulated environment.

## Actual-vs-Expected Comparison

Blocked/partial. The video player controls were not reachable without Vimeo login/age gate, and this was not a physical Android test.

## Diagnosis

Partial diagnosis only. The reporter screenshot supports that Vimeo's player showed a PiP option in Chrome/another browser but not Firefox Android. The live controlled run could not reach the player.

## Cause Analysis

Likely related to Vimeo's player detecting Picture-in-Picture API/browser support and hiding the option when the API is unavailable. This is suggested by the controlled feature probe (`requestPictureInPicture` absent in Firefox, present in Chrome), but it was not validated on the actual player.

## Cause-Validation Test Cases

Not generated because the issue depends on authenticated/age-gated Vimeo playback on Android.

## Confidence

Medium for access blocker; low-medium for PiP API gating as cause.

## Suggested Next Steps

- Reproduce on physical Android with a Vimeo account that can play the target video.
- Compare Vimeo player capability checks and PiP button rendering in Firefox Android and Chrome Android.

## Sources and Artifacts

- Bugzilla payload: `output/bug_1852768/firefox/bugzilla_payload.json`
- Reporter screenshot: `output/bug_1852768/attachments/9352689_Screenshot_1.png`
- Mobile-emulation probes: `output/bug_1852768/probe_firefox151_mobile/`, `output/bug_1852768/probe_chrome148_mobile/`
