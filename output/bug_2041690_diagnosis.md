# Bug 2041690 Diagnosis

Generated: 2026-05-26T10:48:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2041690
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_firefox

## Bug Metadata

- Summary: www.theaa.com - Map with route does not render correctly
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P3
- Platform / OS: Desktop / Windows
- Target URL: https://www.theaa.com/route-planner/route?from=g74%204xt&to=FK10%203SA

## Bugzilla Evidence

- Comment 0 environment: Windows, Firefox 151.0 release and Firefox 153.
- Comment 0 precondition: clean profile.
- Comment 0 steps: navigate to the AA route-planner result URL and observe the map.
- Expected: the map is displayed without issues.
- Actual: the route is not visible and black tiles are displayed over it.
- Notes from comment 0: reproducible in Firefox Release and Nightly, reproducible regardless of ETP, works in Chrome.
- Public attachment 9588885 shows Firefox with large black rectangular map areas that hide parts of the route, while the adjacent Chrome comparison shows the full route and tiles.

## Firefox Version Selection

- Helper-selected Firefox: /Applications/Firefox Nightly.app/Contents/MacOS/firefox
- Firefox Nightly version: Mozilla Firefox 153.0a1
- Additional local release run: /Applications/Firefox.app/Contents/MacOS/firefox
- Firefox release version: Mozilla Firefox 151.0.1
- Note: both controlled local Firefox runs were macOS/headless. The original report was Windows desktop, so a Windows/GPU-specific rendering path remains untested.

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Chrome version: Google Chrome 148.0.7778.179

## Controlled Browser Reproduction Evidence

- Firefox Nightly 153, 1440x1000 and 1280x900: clean profile, accepted the consent banner, waited after load, route summary text was present, Google map tiles and route rendered.
- Firefox 151.0.1, 1440x1000 and 1280x900: clean profile, accepted the consent banner, waited after load, route summary text was present, Google map tiles and route rendered.
- Chrome 148, 1440x1000 and 1280x900: clean profile, accepted the consent banner, waited after load, route summary text was present, Google map tiles and route rendered.
- DOM state in both browsers showed the route results (`Via M73 - 51 mins - 38.8 miles`, `Via M8 - 58 mins - 47.0 miles`), visible map containers, Google Maps tile image requests from `maps.googleapis.com/maps/vt`, and four visible 256x256 map canvas elements.
- Chrome network failures observed during the run were analytics/ad/telemetry requests (`google-analytics.com`, `quantummetric.com`, `adswizz.com`, `adnxs.com`) and did not block the map.

## Actual-vs-Expected Comparison

- Expected from comment 0: route map displays normally.
- Reporter actual from comment 0 and attachment: Firefox displays black map tiles and the route is partly hidden; Chrome displays the route normally.
- Local observed result: Firefox 153, Firefox 151.0.1, and Chrome 148 all displayed the map and blue route normally after consent acceptance and wait.
- Classification: not reproduced in the controlled local macOS/headless comparison. The original Windows desktop behavior is not disproven.

## Diagnosis

Not reproduced locally. The live AA route planner currently renders the Google map tiles and route correctly in both tested Firefox versions and in Chrome under matching clean-profile automation. The Bugzilla attachment remains valid evidence that Firefox showed a black-tile map rendering failure on the reporter's Windows desktop environment, but the failure did not reproduce here.

## Cause Analysis

No confirmed site-side cause was identified because the local Firefox runs did not reproduce the black tiles. The attachment's black rectangles are confined to the Google Maps viewport and align with the map tile/canvas rendering area, while the surrounding AA route-planner UI continues to work. Combined with the current DOM evidence showing Google Maps tile images and 256x256 canvas layers, the most plausible unconfirmed direction is a Firefox graphics/compositing issue in the Google Maps rendering path, potentially Windows/GPU-dependent, rather than a route-calculation or AA form logic failure.

## Confidence

Medium that the live site is currently not reproducing in this macOS/headless environment. Low to medium on the cause, because the original Windows desktop/GPU path could not be exercised.

## Suggested Next Steps

- Re-test on Windows with Firefox 151 or current Nightly using a normal, hardware-accelerated window rather than headless mode.
- If black tiles reproduce, capture `about:support` graphics details and compare with WebRender/software rendering toggles.
- Inspect Google Maps canvas/tile layers at the moment of failure and record whether tile images loaded but compositor output is black.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_firefox/bugzilla_payload.json
- Helper Firefox screenshots: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_firefox
- Browser probe script: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_probe.py
- Firefox 153 / Chrome comparison: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_comparison
- Firefox 151.0.1 / Chrome comparison: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_comparison_ff151
- Downloaded Bugzilla attachment: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_2041690_comparison/bugzilla_attachment_9588885.png
