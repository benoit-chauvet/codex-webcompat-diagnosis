# Bug 2012085 Diagnosis

Generated: 2026-05-30T17:06:35+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2012085
Artifacts: output/bug_2012085/

## Bug Metadata

- Summary: Firefox fails to select email addresses in BT email
- Product / Component: Web Compatibility / Site Reports
- Status: NEW 
- Severity / Priority: S2 / P1
- Platform / OS: Unspecified / Unspecified
- Bug URL: https://email.bt.com/mail/index-rui.jsp?v=MX_3.11.0.7

## Bugzilla Evidence

Comment 0 was used as the source of truth for the reported steps, expected result, actual result, and environment. Public attachment metadata:

- None

## Browser Versions

- Reported: Firefox 147 on Windows.
- Firefox used: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`); version mismatch, exploratory only.
- Chrome used: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`).

## Controlled Browser Reproduction Evidence

- Firefox probe: `output/bug_2012085/probe_firefox151/probe_state.json`.
- Chrome probe: `output/bug_2012085/probe_chrome148/probe_state.json`.

Both browsers navigated from the BT mail URL to the BT email OAuth/login page and showed the same login form. The reported bug requires a BT email account, composing mail, typing in the To field, and selecting an autocomplete contact.

## Actual-vs-Expected Comparison

Blocked/partial. The mail UI and autocomplete contact picker were not reachable without credentials.

## Diagnosis

Partial diagnosis only. The login entry point works in both browsers, but the affected To-field autocomplete behavior is account-gated.

## Cause Analysis

Not determined. No authenticated composer DOM or autocomplete widget was available for inspection.

## Cause-Validation Test Cases

Not generated because the issue depends on a private BT email account and saved/autocomplete contact data.

## Confidence

Low for root cause; high for the credential blocker.

## Suggested Next Steps

- Reproduce with a test BT email account containing at least one saved contact.
- Capture the selected autocomplete option's DOM events and the resulting recipient token value in Firefox and Chrome.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2012085/firefox/bugzilla_payload.json`
- Login probes: `output/bug_2012085/probe_firefox151/`, `output/bug_2012085/probe_chrome148/`
