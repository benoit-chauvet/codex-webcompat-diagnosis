# Diagnosis Summary

## Bug [2005492](https://bugzilla.mozilla.org/show_bug.cgi?id=2005492)

### Diagnosis

Reproduced. Firefox 146 renders the Block news card headlines with squeezed vertical spacing while Chrome 148 renders the same text correctly. The text column widths and line counts match across browsers; the difference is line spacing. For example, the first 5-line title is 96px tall in Firefox but 143.13px tall in Chrome.

### Cause Analysis

The card title markup places a heading-size decorator inside `h3.headline`; the decorator carries the real `font-size`, `font-family`, and `line-height: 115%`, but it is styled with `display: contents`. In Firefox, the large Cash Sans glyph metrics are applied, but the multi-line layout is packed using the parent `h3` default 16px/normal line-height cadence. Chrome uses the decorator's computed line-height. A Firefox probe confirmed that changing the decorator to `display: block` makes the headline height match Chrome, so the likely cause is a Firefox layout bug/difference for `display: contents` descendants contributing line-height to heading line boxes. The reduced testcase in `output/bug_2005492/testcase/` validates this with controls: Firefox 146 squeezes only the `display: contents` path to a 19.2px line cadence, while Firefox's `display:block` control and Chrome's `display:contents` path both use the intended 28.6px cadence. The minimal standalone testcase in `output/bug_2005492/minimal-testcase/` reduces the same browser difference to one `h3` and one `display: contents` child.
