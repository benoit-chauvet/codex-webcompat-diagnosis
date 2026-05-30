# Bug 2035136 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2035136
Artifacts: output/bug_2035136/

## Bug Metadata

- Summary: Anthropic's Claude Design "Linking Code from your computer" requires Chrome / Edge
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Unspecified / Unspecified
- Bug URL: https://claude.ai/design

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9574009 `image.png` (image/png): image.png
- 9575368 `image.png` (image/png): Full option panel

## Browser Versions

- Reported: Claude Design setup flow, no specific Firefox version in comment 0.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`).
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox probe: `output/bug_2035136/probe_firefox151/probe_state.json`.
- Chrome probe: `output/bug_2035136/probe_chrome148/probe_state.json`.
- Reporter screenshots: `output/bug_2035136/attachments/9574009_image.png`, `9575368_image.png`.

The live `/design` URL requires login in Firefox and was served a Cloudflare HTTP 403 page in Chrome automation, so the setup panel could not be reached. The reporter screenshots show the relevant UI: "Link code from your computer - requires Chrome or Edge" and the design-system setup screen.

Feature probing also shows a likely compatibility reason: Firefox 151 does not expose `showOpenFilePicker`, while Chrome 148 does. That API is a common basis for local-folder/file-linking UX.

## Actual-vs-Expected Comparison

Blocked/partial. The authenticated Claude Design setup workflow was not reachable, but reporter screenshots document the browser requirement.

## Diagnosis

Partial diagnosis. The "Link code from your computer" feature appears intentionally limited to Chromium-family browsers in Claude's UI. The likely functional dependency is Chromium's File System Access API or related local-file picker capabilities.

## Cause Analysis

Likely browser capability/allowlist gating for local code linking. Firefox lacks `showOpenFilePicker` in the controlled probe, while Chrome supports it. The exact Claude code path was not inspected because login was required.

## Cause-Validation Test Cases

Not generated because the issue is an authenticated product feature and the live setup panel was not reachable.

## Confidence

Medium for File System Access / browser-gating cause; low for exact Claude implementation details.

## Suggested Next Steps

- Reproduce in an authenticated Claude account and inspect the feature flag or capability check that labels the option "requires Chrome or Edge".
- If the feature needs directory access, determine whether a Firefox fallback using `<input type=file webkitdirectory>` or uploaded archive is possible.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2035136/firefox/bugzilla_payload.json`
- Reporter screenshots: `output/bug_2035136/attachments/`
- Public probes: `output/bug_2035136/probe_firefox151/`, `output/bug_2035136/probe_chrome148/`
