# Bug 2007320 Diagnosis

Generated: 2026-05-25T22:43:40+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2007320
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox

## Bug Metadata

- Summary: Lines missing in an SVG image on the left and right side, only ones on center get displayed
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S4 / P3
- Platform / OS: Desktop / Windows 10

## Bugzilla Evidence

- Inferred Firefox versions: 146.0
- Selected target URL: https://upload.wikimedia.org/wikipedia/commons/a/aa/Tectonic_plates_boundaries_physical_World_map_Wt_180degE_centered-en.svg
- Target URL candidates:
- https://upload.wikimedia.org/wikipedia/commons/a/aa/Tectonic_plates_boundaries_physical_World_map_Wt_180degE_centered-en.svg (bug.url)
- https://github.com/webcompat/web-bugs/issues/196553 (comment 17817711)
- Attachment metadata count: 1

## Firefox Version Selection

- Requested major version: 146
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 146.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/146.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 146.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: open the Wikimedia SVG, zoom out or scroll the map, and observe the left and right side boundary lines.
- Firefox 146 evidence: the visible map area lacks the colored plate-boundary polylines that Chrome displays in the same region.
- Chrome 148 evidence: Chrome renders the red, green, purple, gray, and blue boundary lines over the physical map.
- Classification: reproduced cross-browser issue.

## Actual-vs-Expected Comparison

- Expected from comment 0: lines/continental boundaries are displayed.
- Actual from comment 0: lines/continental boundaries are missing on the right and left side in Firefox.
- Observed: Firefox omits many boundary polylines visible in Chrome.

## Diagnosis

The SVG rendering issue reproduces. The Firefox screenshot shows the base raster/physical map and labels, but boundary-line layers are missing in the viewport where Chrome draws them.

## Cause Analysis

The saved SVG source contains Inkscape-generated boundary layers such as `Rift / Spreading ridge`, `Transform fault`, and `Non-subducting plate boundaries`, made of many `polyline` elements with very large source coordinates and `stroke-width:36788.72265625`, scaled back into the visible map by a tiny transform matrix such as `matrix(1.4948461e-4,0,0,-1.4952008e-4,2451.4803,1498.0059)`. The likely cause is a Firefox SVG painting/culling issue for transformed large-coordinate polylines with huge pre-transform stroke widths; Chrome keeps those shapes in the painted display list and renders them.

## Confidence

High for reproduction; medium for the precise graphics-engine cause without a minimized SVG.

## Suggested Next Steps

- Reduce the SVG to one missing transformed polyline and its transform.
- File or link a Core SVG/graphics bug if a minimized testcase confirms display-list culling or transformed-stroke bounds calculation.
- As a site/content workaround, normalize the coordinates/stroke widths in the SVG instead of relying on very large coordinates scaled down by a tiny transform.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_chrome
- SVG source artifact: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2007320_firefox/source.svg
