# Bug 2042173 Diagnosis

Finalized: 2026-05-28T10:55:00+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=2042173

## Bug Metadata

- Summary: www.amazon.com - Previews only one image from the gallery when there are multiple images on a review
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S3 / P2
- Platform / OS: Desktop / Windows
- Target URL: https://www.amazon.com/dp/B0FD9Z9FSF/?coliid=I3MQ3BARFOSOEE&colid=105SCGC0NK0ET&th=1&psc=1

## Bugzilla Evidence

Comment 0 reports Firefox 151.0 release on Windows. Steps: open the Amazon product, scroll to "Reviews with images", click an image, use the next arrow until a review with multiple images appears, and observe switching between images. Expected: all images in the review are shown when switched. Actual: only one image from the gallery is shown. Attachment 9589431 (`Release-vs-Nightly.mp4`) was downloaded and frame-captured under `output/bug_2042173/attachments/frames/`.

## Browser Versions

- Firefox used by helper and focused probe: `/Applications/Firefox.app/Contents/MacOS/firefox` (`Mozilla Firefox 151.0.2`)
- Chrome used for comparison: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome` (`Google Chrome 148.0.7778.179`)

## Controlled Browser Reproduction Evidence

- Firefox baseline: `output/bug_2042173/firefox/state_firefox_1280x900.json`
- Chrome baseline: `output/bug_2042173/chrome/state_chrome_1280x900.json`
- Firefox interaction probe: `output/bug_2042173/probe_firefox151/probe_state.json`
- Chrome interaction probe: `output/bug_2042173/probe_chrome/probe_state.json`

The product page loaded in both browsers. The interaction probe scrolled to the reviews area and clicked a review image. The current Amazon UI did not expose the same preview-pane/gallery flow shown in the reporter video; after image/next interactions, both Firefox 151 and Chrome were in inline review content rather than a multi-image preview pane with the reported switching behavior.

## Actual-vs-Expected Comparison

Site/UI drift. The exact reported gallery preview state could not be reached in either browser, so the Firefox 151-only preview bug was not reproduced on the current page.

## Diagnosis

Partial diagnosis only. The reporter attachment supports that a previous Amazon review-gallery UI differed between Firefox release and other browsers/builds, but the live Amazon page behavior has changed enough that the controlled steps no longer reach the failing pane.

## Cause Analysis

Not determined. The current DOM did not expose the failing preview-pane state, so there was no reliable implementation surface to inspect for the reported single-image gallery behavior.

## Cause-Validation Test Cases

Not generated because the issue was not reproduced against the current live page.

## Confidence

Medium for site/UI drift; low for root cause.

## Suggested Next Steps

- Re-test with the exact region/account state used by the reporter, or with a saved DOM/HAR from the failing Amazon gallery.
- If the preview pane is reachable again, compare the selected review's image list, carousel state, and click handlers between Firefox 151 and Chrome.

## Sources and Artifacts

- Bugzilla payload: `output/bug_2042173/firefox/bugzilla_payload.json`
- Reporter video and frames: `output/bug_2042173/attachments/`
- Firefox/Chrome baseline and interaction artifacts: `output/bug_2042173/firefox/`, `output/bug_2042173/chrome/`, `output/bug_2042173/probe_firefox151/`, `output/bug_2042173/probe_chrome/`
