# Bug 2041371 Diagnosis

Finalized: 2026-05-28T10:55:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2041371

## Bug Metadata

- Summary: formatless paste (Ctrl+Shift+V) of formatted text should show 'Paste' menu at caret position in docs.google.com, not a mouse cursor one
- Product / Component: Core / DOM: Copy & Paste and Drag & Drop
- Status: NEW
- Severity / Priority: S3 / --
- Platform / OS: Unspecified / Unspecified
- Target URL: https://docs.google.com/

## Bugzilla Evidence

Comment 0 reports Firefox 151.0 and 153.0a1 on Windows 11. Steps: copy formatted text, focus a Google Docs document, and press Ctrl+Shift+V. Firefox shows a single-item "Paste" menu, but its position follows the mouse cursor or the edge of the screen containing the document. Expected: the menu should appear at the document caret where the clipboard content will be inserted.

## Browser Versions

- Firefox helper baseline: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`)
- Chrome baseline: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`)

## Controlled Browser Reproduction Evidence

- Firefox baseline: `output/bug_2041371/firefox/state_firefox_1280x900.json`
- Chrome baseline: `output/bug_2041371/chrome/state_chrome_1280x900.json`

Both browsers navigated from `https://docs.google.com/` to Google Account sign-in. The required Google Docs editor surface was not accessible without credentials. The reported symptom also involves a browser/OS paste permission menu and caret/mouse positioning, which is not captured by ordinary page DOM state.

## Actual-vs-Expected Comparison

Blocked/partial. The Google Docs editor and the system/browser paste menu could not be exercised from the unauthenticated automated session.

## Diagnosis

The report is a Core clipboard/menu-positioning issue rather than a normal page rendering issue. No live reproduction was possible because the test requires Google Docs sign-in, clipboard setup with formatted content, keyboard input, and observation of browser UI outside the web page.

## Cause Analysis

Not proven in this run. Based on comment 0, the likely implementation area is Firefox's paste permission/menu anchoring path for Google Docs' paste interception: the menu appears anchored to the mouse cursor/screen edge rather than the editable caret. This is an inference from the Bugzilla report, not a verified live cause.

## Cause-Validation Test Cases

Not generated because the browser UI behavior was not reproduced under automation.

## Confidence

High for blocker classification; medium that the bug belongs in Firefox clipboard/menu UI rather than Google Docs layout.

## Suggested Next Steps

- Reproduce manually in Firefox 151/153 on Windows 11 with a signed-in Google Docs document and a formatted clipboard payload.
- Capture the caret rect, mouse coordinates, monitor layout, and screenshot/video of the paste menu location.
- If a reduced test is needed, use a contenteditable page that triggers the same paste permission UI without Google Docs.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2041371/firefox/bugzilla_payload.json`
- Firefox/Chrome baseline artifacts: `output/bug_2041371/firefox/`, `output/bug_2041371/chrome/`
