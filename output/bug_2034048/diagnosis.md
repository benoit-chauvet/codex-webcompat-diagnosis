# Bug 2034048 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2034048
Artifacts: output/bug_2034048/

## Bug Metadata

- Summary: Offline mode unsupported in Canva
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Unspecified / Unspecified
- Bug URL: https://www.canva.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- None

## Browser Versions

- Reported evidence: Canva offline-access support page.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`).
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox docs probe: `output/bug_2034048/probe_firefox151_docs/probe_state.json`.
- Chrome docs probe: `output/bug_2034048/probe_chrome148_docs/probe_state.json`.

The Canva help article loaded in Firefox and explicitly documented offline-editing support. The relevant text in the captured page says supported devices include "Chrome, Edge, or Safari (desktop browsers)" and "Firefox (versions below 149)", and says "Not supported" for "Firefox (versions 149 and above)" and mobile browsers. Chrome automation was served a Canva security page, but the Firefox docs capture was enough to confirm the current documented policy.

## Actual-vs-Expected Comparison

Not a live app reproduction; documentation confirms Firefox 149+ is intentionally unsupported for Canva offline editing.

## Diagnosis

Documentation-confirmed unsupported browser/version. The issue is not a transient rendering failure in the help page: Canva currently documents that Firefox 149 and above are not supported for offline editing.

## Cause Analysis

Likely product/browser-support gating for Canva's offline-editing implementation. The exact app implementation was not tested, but the support article is explicit about the support boundary.

## Cause-Validation Test Cases

Not generated because this diagnosis is based on vendor support documentation rather than a reproduced app failure.

## Confidence

High that Canva currently documents Firefox 149+ as unsupported; low for the internal technical reason.

## Suggested Next Steps

- Ask Canva whether Firefox 149+ was disabled because of a specific storage/service-worker/offline regression or as a product support decision.
- If a technical Firefox regression is suspected, test the authenticated offline-editing flow in Firefox 148 versus 149+ with service-worker/storage logging.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2034048/firefox/bugzilla_payload.json`
- Canva docs probe: `output/bug_2034048/probe_firefox151_docs/`
