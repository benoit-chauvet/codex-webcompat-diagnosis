# Bug 2038198 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2038198
Artifacts: output/bug_2038198/

## Bug Metadata

- Summary: wise.com: ID confirmation doesn't work on Firefox for iOS
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Unspecified / iOS
- Bug URL: https://wise.com

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9584519 `image(1).png` (image/png): image(1).png

## Browser Versions

- Reported environment: Firefox for iOS, Wise signup identity confirmation.
- Desktop exploratory Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`).
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Wise/FaceTec reporter screenshot: `output/bug_2038198/attachments/9584519_image_1_.png`.
- Public FaceTec compatibility probe: `output/bug_2038198/probe_firefox151_facetec/probe_state.json` and `output/bug_2038198/probe_chrome148_facetec/probe_state.json`.

The reported Wise flow requires signup state, ID-confirmation state, camera access, and Firefox for iOS. I could not execute the ID check without account/private identity data and an iOS browser environment. The public FaceTec compatibility page loaded in both desktop browsers and states that the Browser SDK is compatible only on supported browsers, with browser compatibility delegated to the matrix on that page.

## Actual-vs-Expected Comparison

Blocked/partial. The reporter attachment shows the failure screen on Wise: the user is instructed to use Chrome or Safari. A controlled Firefox-for-iOS versus Chrome/Safari ID-confirmation run was not possible in this environment.

## Diagnosis

Partial diagnosis. The evidence supports a Wise/FaceTec browser-support gate in the identity-check provider rather than a generic page-load failure. The flow cannot be completed in Firefox for iOS per the reporter screenshot, while Chrome reportedly completes it.

## Cause Analysis

Likely site/provider browser allowlisting or unsupported-device logic in the FaceTec-powered check. The precise check was not reachable without the private signup flow and iOS device context.

## Cause-Validation Test Cases

Not generated because the issue depends on a private ID-verification flow, camera capture, and Firefox for iOS.

## Confidence

Medium for provider allowlisting based on the screenshot; low for exact implementation cause.

## Suggested Next Steps

- Reproduce on a physical iOS device with Firefox and Safari/Chrome using a test Wise signup account.
- Capture the FaceTec browser-detection result and user agent/feature checks at the point where the Wise page shows the unsupported-browser message.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2038198/firefox/bugzilla_payload.json`
- Reporter screenshot: `output/bug_2038198/attachments/9584519_image_1_.png`
- FaceTec probes: `output/bug_2038198/probe_firefox151_facetec/`, `output/bug_2038198/probe_chrome148_facetec/`
