# Bug 2042375 Diagnosis

Finalized: 2026-05-28T10:55:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2042375

## Bug Metadata

- Summary: gitlab.com - 2FA auth for login fails with Yubikey Security Key on Firefox for Android
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S4 / P2
- Platform / OS: ARM / Android
- Target URL: https://gitlab.com/users/sign_in

## Bugzilla Evidence

Comment 0 reports Android 15 with Firefox Mobile 151.0. The failure requires GitLab login with security-key 2FA using a USB or NFC Yubikey. Expected: the 2FA flow should use the security key/passkey path. Actual: USB asks for a PIN even though the reporter says the 2FA security-key flow has no PIN, and NFC returns an unknown error. QA also noted that it could not reproduce without the required Yubikey setup.

## Browser Versions

- Firefox helper baseline: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`)
- Chrome baseline: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`)

## Controlled Browser Reproduction Evidence

- Firefox baseline: `output/bug_2042375/firefox/state_firefox_1280x900.json`
- Chrome baseline: `output/bug_2042375/chrome/state_chrome_1280x900.json`

The desktop public sign-in page could not be used for the reported flow. Both Firefox and Chrome received the Cloudflare "Performing security verification" page with HTTP 403. More importantly, the reported bug requires Firefox for Android, a GitLab account with security-key 2FA enabled, and a physical USB/NFC Yubikey.

## Actual-vs-Expected Comparison

Blocked/partial. The required mobile hardware-authentication flow could not be executed.

## Diagnosis

The report remains plausible but unreproduced. The blocker is external setup: Android 15, Firefox Mobile, a GitLab 2FA account, and USB/NFC Yubikey access.

## Cause Analysis

Not determined. The likely area to inspect is the Android WebAuthn/FIDO2 security-key path and how GitLab classifies the credential request, but no credential ceremony could be initiated from this environment.

## Cause-Validation Test Cases

Not generated because the issue was not reproduced.

## Confidence

High for blocker classification; low for root cause.

## Suggested Next Steps

- Reproduce on Android 15 with Firefox Mobile 151+ and a test GitLab account configured for security-key 2FA.
- Capture WebAuthn request options, authenticator transport (`usb` vs `nfc`), and Firefox Android prompts/errors.
- Compare with Chrome Android or another working browser on the same device and Yubikey.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2042375/firefox/bugzilla_payload.json`
- Firefox/Chrome baseline artifacts: `output/bug_2042375/firefox/`, `output/bug_2042375/chrome/`
