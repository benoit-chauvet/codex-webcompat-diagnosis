# Bug 2037009 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2037009
Artifacts: output/bug_2037009/

## Bug Metadata

- Summary: WebRTC ICE consent-refresh times out mid-session against OpenAI Realtime API media server, dropping the connection on second user speech turn (Firefox 150)
- Product / Component: Core / WebRTC: Networking
- Status: UNCONFIRMED 
- Severity / Priority: S2 / P1
- Platform / OS: Unspecified / Unspecified
- Bug URL: https://chatgpt.com/

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- 9583972 `aboutWebrtc.html` (text/html): aboutWebrtc.html

## Browser Versions

- Reported: Firefox 150 on Windows 11.
- No live browser reproduction was attempted beyond Bugzilla/attachment inspection because the STR require OpenAI Realtime API credentials, microphone input, and a 30-90 second live media session.

## Controlled Browser Reproduction Evidence

- Bugzilla payload: `output/bug_2037009/firefox/bugzilla_payload.json`.
- about:webrtc attachment: `output/bug_2037009/attachments/9583972_aboutWebrtc.html`.

The attachment contains successful ICE consent-refresh messages followed later by `STUN-CLIENT(consent): Timed out`, `A single consent refresh request timed out`, and `component disconnected`, matching the reporter's described mid-session drop.

## Actual-vs-Expected Comparison

Blocked/partial. A controlled Firefox-versus-Chrome Realtime API session could not be created without credentials and a reproducible app harness.

## Diagnosis

Partial diagnosis. The Bugzilla attachment is consistent with a Firefox ICE consent-refresh timeout causing the connection to transition to disconnected during the second user turn. This is a Core/WebRTC networking issue rather than a simple site layout compatibility bug.

## Cause Analysis

Not fully determined. The available about:webrtc evidence points at ICE consent freshness failing after several successful refreshes. It does not prove whether the root cause is Firefox consent timer/state handling, network path behavior, server-side STUN response behavior, or interaction with the selected candidate pair.

## Cause-Validation Test Cases

Not generated because validation requires OpenAI Realtime API credentials, microphone/media timing, and a controllable WebRTC peer/session harness.

## Confidence

Medium for the consent-timeout failure mode; low for exact WebRTC/network root cause.

## Suggested Next Steps

- Build a reduced authenticated Realtime API harness that logs ICE states, candidate pair stats, consent requests, and data-channel events across Firefox and Chrome.
- Capture `about:webrtc` and `RTCPeerConnection.getStats()` around the first response completion and second user speech start.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2037009/firefox/bugzilla_payload.json`
- about:webrtc attachment: `output/bug_2037009/attachments/9583972_aboutWebrtc.html`
