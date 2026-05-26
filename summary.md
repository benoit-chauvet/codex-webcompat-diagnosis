# Diagnosis Summary

## Bug [1905304](https://bugzilla.mozilla.org/show_bug.cgi?id=1905304)

### Diagnosis

The original visual issue cannot be diagnosed from the current live URL. The Bugzilla attachment remains evidence that the issue existed on the previous page, but the controlled live comparison only demonstrates page drift.

### Cause Analysis

Not performed because the original bug was not reproduced. The current cross-browser difference appears to be WebMD's current 404-page behavior, not the reported icon alignment issue.

## Bug [2028875](https://bugzilla.mozilla.org/show_bug.cgi?id=2028875)

### Diagnosis

The blank-page issue reproduces. The page shell loads an external module from `https://s3.swagtime.net/frontend-main/Ny42MzBa/assets/COmpH26D.js`; Firefox renders only the dark background, while Chrome completes the Vue app rendering.

### Cause Analysis

The current JavaScript bundle contains `nI=""` and later calls `new WebSocket(nI)`. Bugzilla comment 2 reported `DOMException: An invalid or illegal string was specified` during WebSocket creation, which is consistent with Firefox rejecting the empty WebSocket URL. Chrome continues rendering the app despite that construction, while Firefox appears to stop before the Vue app reaches the visible rendered state.

## Bug [2030213](https://bugzilla.mozilla.org/show_bug.cgi?id=2030213)

### Diagnosis

No live reproduction conclusion. The available evidence confirms the target URL and Firefox version selection, but the browser automation did not reach the chat box or clipboard paste step.

### Cause Analysis

Not performed because the bug was not reproduced. A valid next diagnosis needs an interactive session that reaches the chat editor and records paste-event data, especially `ClipboardEvent.clipboardData.items` MIME types in Firefox and Chrome.

## Bug [2007320](https://bugzilla.mozilla.org/show_bug.cgi?id=2007320)

### Diagnosis

The SVG rendering issue reproduces. The Firefox screenshot shows the base raster/physical map and labels, but boundary-line layers are missing in the viewport where Chrome draws them.

### Cause Analysis

The saved SVG source contains Inkscape-generated boundary layers such as `Rift / Spreading ridge`, `Transform fault`, and `Non-subducting plate boundaries`, made of many `polyline` elements with very large source coordinates and `stroke-width:36788.72265625`, scaled back into the visible map by a tiny transform matrix such as `matrix(1.4948461e-4,0,0,-1.4952008e-4,2451.4803,1498.0059)`. The likely cause is a Firefox SVG painting/culling issue for transformed large-coordinate polylines with huge pre-transform stroke widths; Chrome keeps those shapes in the painted display list and renders them.

## Bug [2016362](https://bugzilla.mozilla.org/show_bug.cgi?id=2016362)

### Diagnosis

No live reproduction conclusion. The bug requires a logged-in, enrolled Coursera lab and a long-duration video test.

### Cause Analysis

Not performed because the reported behavior was not reproduced. Bugzilla discussion suspects a contenteditable/code-editor issue, possibly an editor with syntax highlighting, but the current evidence does not identify the site implementation.

## Bug [2038886](https://bugzilla.mozilla.org/show_bug.cgi?id=2038886)

### Diagnosis

The local run is partial. Bugzilla public comments provide a plausible direction: Discourse appears to mutate history/URL state during load, and Firefox loses or fails to apply the text-fragment highlight on fresh navigation while same-tab navigation can work.

### Cause Analysis

Not confirmed locally. Bugzilla comment 3 suggests the site may `pushState` over the anchor/text fragment; comment 4 notes a simple `pushState` testcase also breaks Chrome, so the real Discourse behavior likely has an additional timing or navigation-state factor. A real diagnosis needs instrumentation of `history.pushState`, `location.hash`, and text-fragment highlight timing in both browsers during a fresh load.

## Bug [1943358](https://bugzilla.mozilla.org/show_bug.cgi?id=1943358)

### Diagnosis

No live reproduction conclusion from this run. The public Bugzilla artifacts and comments contain substantial prior diagnosis, but the controlled browser comparison is blocked by account/login requirements.

### Cause Analysis

Public Bugzilla analysis points to a Firefox editor/selection behavior difference. The downloaded reduced testcase contains a `contenteditable=true` ancestor wrapping a `contenteditable=false; user-select:none` child with a non-draggable image. Bugzilla comments report that dragging over the image changes/collapses selection in Firefox, which changes Notion's internal `default.state.stores.length` path and resets cover position; Chrome focuses differently and does not move the caret/selection the same way.

## Bug [1957422](https://bugzilla.mozilla.org/show_bug.cgi?id=1957422)

### Diagnosis

The load-completeness part of the bug reproduces. Chrome reaches the LiA chat panel; Firefox remains at a less complete chat state.

### Cause Analysis

Public Bugzilla analysis and the downloaded reduction point at the Salesforce/Lidl chat widget integration rather than the isolated Svelte widget itself. The reduction includes the Svelte-style `ChatWidget` code and the send button class toggle `I(C, "scw-active", t[13])`. Bugzilla comments report that the isolated widget can apply `scw-active`, but the live site does not do so in Firefox, likely because the Salesforce `near-membrane` sandbox/proxy layer or surrounding integration prevents the expected state mutation/event propagation from reaching the widget.

## Bug [1934534](https://bugzilla.mozilla.org/show_bug.cgi?id=1934534)

### Diagnosis

Reproduced. The page implements a custom full-screen section scroller and disables native overflow. In Firefox 135, wheel input leaves the page at the initial section; in Chrome 148, wheel input advances the section container by one viewport height. This matches the reporter's Firefox-broken / Chrome-working result.

### Cause Analysis

The site relies on the legacy non-standard `mousewheel` event for desktop wheel navigation. The downloaded app bundle attaches the handler as `on:{mousewheel:function(e){ e.preventDefault(); t.mouseWheel(...) }}` on `.homePage-body`. That handler increments/decrements `itemIndex` and calls `handleMove()`, which sets `.homePage-body.style.transform` to `translateY(...)`.

Firefox does not dispatch the legacy `mousewheel` event for normal wheel input; it dispatches the standard `wheel` event. Because the page also sets the full-screen wrapper to `height:100vh; overflow:hidden` and keeps `#homePage` overflow hidden, there is no native scrolling fallback. Chrome still dispatches the legacy compatibility event, so the custom `mouseWheel` handler runs and moves the section container.

Likely site fix: listen for the standard `wheel` event, preferably with a non-passive listener only if `preventDefault()` is required, and keep the existing `mousewheel` listener only as a legacy fallback. The handler should read `deltaY` from the `WheelEvent`.


## Bug [2041690](https://bugzilla.mozilla.org/show_bug.cgi?id=2041690)

### Diagnosis

Not reproduced locally. The live AA route planner currently renders the Google map tiles and route correctly in both tested Firefox versions and in Chrome under matching clean-profile automation. The Bugzilla attachment remains valid evidence that Firefox showed a black-tile map rendering failure on the reporter's Windows desktop environment, but the failure did not reproduce here.

### Cause Analysis

No confirmed site-side cause was identified because the local Firefox runs did not reproduce the black tiles. The attachment's black rectangles are confined to the Google Maps viewport and align with the map tile/canvas rendering area, while the surrounding AA route-planner UI continues to work. Combined with the current DOM evidence showing Google Maps tile images and 256x256 canvas layers, the most plausible unconfirmed direction is a Firefox graphics/compositing issue in the Google Maps rendering path, potentially Windows/GPU-dependent, rather than a route-calculation or AA form logic failure.

## Bug [2042167](https://bugzilla.mozilla.org/show_bug.cgi?id=2042167)

### Diagnosis

Firefox browser evidence was captured with Puppeteer. Inspect the screenshots and update this section with the visual or behavioral finding tied to the Bugzilla expected/actual behavior.

### Cause Analysis

Not determined by the helper scaffold. Replace this section after completing the controlled Firefox-vs-Chrome comparison and implementation analysis.

## Bug [1859289](https://bugzilla.mozilla.org/show_bug.cgi?id=1859289)

### Diagnosis

No installed Firefox binary matching major version 120 was found, so reproduction could not be attempted.

### Cause Analysis

Not determined by the helper scaffold. Replace this section after completing the controlled Firefox-vs-Chrome comparison and implementation analysis.

## Bug [1859289](https://bugzilla.mozilla.org/show_bug.cgi?id=1859289)

### Diagnosis

Firefox browser evidence was captured with Puppeteer. Inspect the screenshots and update this section with the visual or behavioral finding tied to the Bugzilla expected/actual behavior.

### Cause Analysis

Not determined by the helper scaffold. Replace this section after completing the controlled Firefox-vs-Chrome comparison and implementation analysis.

## Bug [2005492](https://bugzilla.mozilla.org/show_bug.cgi?id=2005492)

### Diagnosis

Reproduced. Firefox 146 renders the Block news card headlines with squeezed vertical spacing while Chrome 148 renders the same text correctly. The text column widths and line counts match across browsers; the difference is line spacing. For example, the first 5-line title is 96px tall in Firefox but 143.13px tall in Chrome.

### Cause Analysis

The card title markup places a heading-size decorator inside `h3.headline`; the decorator carries the real `font-size`, `font-family`, and `line-height: 115%`, but it is styled with `display: contents`. In Firefox, the large Cash Sans glyph metrics are applied, but the multi-line layout is packed using the parent `h3` default 16px/normal line-height cadence. Chrome uses the decorator's computed line-height. A Firefox probe confirmed that changing the decorator to `display: block` makes the headline height match Chrome, so the likely cause is a Firefox layout bug/difference for `display: contents` descendants contributing line-height to heading line boxes. The reduced testcase in `output/bug_2005492/testcase/` validates this with controls: Firefox 146 squeezes only the `display: contents` path to a 19.2px line cadence, while Firefox's `display:block` control and Chrome's `display:contents` path both use the intended 28.6px cadence. The minimal standalone testcase in `output/bug_2005492/minimal-testcase/` reduces the same browser difference to one `h3` and one `display: contents` child.
