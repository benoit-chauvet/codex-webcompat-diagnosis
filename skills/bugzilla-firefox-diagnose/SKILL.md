---
name: bugzilla-firefox-diagnose
description: Fetch Mozilla Bugzilla web compatibility bugs, extract the first comment's steps/expected/actual behavior, run a controlled Firefox-versus-Chrome reproduction, inspect public Bugzilla artifacts, analyze the page when the bug reproduces, write Markdown diagnoses, and generate an aggregate summary. Use when the user asks Codex to diagnose a Bugzilla bug, reproduce a webcompat issue, compare Firefox behavior with Chrome, generate an output bug ID diagnosis report from Bugzilla evidence, or summarize completed Bugzilla diagnoses.
---

# Bugzilla Firefox Diagnose

## Workflow

Start with the bundled helper for repeatable Bugzilla fetching and Firefox setup:

```bash
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py <bug_id> --output-dir output
```

If working from a local copy of this skill, run the script from that skill path instead.

The helper:

- Fetches the Bugzilla REST payload for the bug, comments, attachment metadata, and history.
- Infers the Firefox version from Bugzilla fields and comments.
- Infers the target URL from the Bugzilla `url` field and comments.
- Selects a Firefox binary whose reported major version matches the bug when possible.
- Can download a matching archived Firefox release on macOS into a temp cache when `--download-firefox` is provided.
- Captures Firefox screenshots at common desktop and mobile-ish viewport sizes.
- Writes `output/bug_<id>_diagnosis.md` and supporting artifacts under `output/bug_<id>_firefox/`.
- Updates `summary.md` next to the output directory with linked Bugzilla bug headings and each report's Diagnosis and Cause Analysis sections.

The helper output is only a starting point. A completed diagnosis must execute the reported reproduction steps and compare Firefox with Chrome.

## Required Reproduction Process

For each bug:

1. Read comment 0 from `output/bug_<id>_firefox/bugzilla_payload.json`.
2. Extract the first-comment preconditions, steps to reproduce, expected behavior, actual behavior, environment, and notes. Do not rely only on the bug summary.
3. Inspect public Bugzilla artifacts, including attachment metadata and any available screenshots/videos, to understand the reporter's Firefox-vs-Chrome claim.
4. Execute the first-comment steps in Firefox and Chrome under controlled conditions.
5. Compare Firefox behavior against Chrome behavior and compare both browsers against the expected and actual results from comment 0.
6. If Firefox reproduces the reported actual behavior while Chrome satisfies the expected behavior, analyze the page to identify the likely cause.
7. If reproduction cannot be completed, write a partial diagnosis that clearly names the blocker, what evidence was collected, and what still needs to be done.

## Controlled Browser Comparison

Use comparable conditions for Firefox and Chrome:

- Use the Firefox version specified in Bugzilla when available.
- Record exact Firefox and Chrome version outputs.
- Use clean browser profiles, the same URL, viewport, locale/device mode when relevant, and comparable tracking-protection/privacy settings.
- Perform the same user interactions in both browsers, including clicks, typing, clipboard actions, zooming, scrolling, navigation, or reload/new-tab behavior required by the first-comment steps.
- Capture evidence for both browsers: screenshots or video, console errors, network failures, DOM state, and relevant command logs.
- If a step requires credentials, a free trial, private account data, a device capability, or a manual action that cannot be automated, attempt the accessible portion and mark the remaining reproduction as blocked/partial.

Classify the comparison explicitly:

- **Reproduced cross-browser issue**: Firefox shows the reported actual result and Chrome shows the expected result under the same controlled steps.
- **Not reproduced**: Firefox and Chrome both match expected behavior, or Firefox no longer shows the reported actual result.
- **Site/environment drift**: the target URL, content, login flow, feature, or public behavior has changed enough that live reproduction no longer matches the Bugzilla artifacts.
- **Blocked/partial**: required credentials, unavailable target content, inaccessible browser version, missing device capability, or non-automatable setup prevents a full comparison.

## Firefox Version Rules

Use the Firefox version specified in Bugzilla when the helper can identify one. Do not silently substitute another version.

If no matching Firefox binary is installed:

- Check whether the user provided `FIREFOX_BIN` or pass `--firefox-bin /path/to/firefox`.
- On macOS, pass `--download-firefox` to fetch the matching release from Mozilla's archive into the helper's temp cache.
- If a non-matching local Firefox is useful only for exploratory evidence, pass `--allow-version-mismatch` and state the mismatch in the report.
- If the exact version is required and unavailable, write the report with a clear blocked/partial diagnosis instead of pretending reproduction happened.

## Diagnosis Process

After running the helper:

1. Read `output/bug_<id>_diagnosis.md`.
2. Read comment 0 from the Bugzilla payload and extract its steps, expected result, and actual result.
3. Inspect public Bugzilla artifacts and Firefox helper screenshots in `output/bug_<id>_firefox/`.
4. Execute the comment-0 steps in Firefox and Chrome, collecting comparable evidence for both browsers.
5. Compare Firefox vs Chrome and actual vs expected. State whether the bug is reproduced, not reproduced, blocked/partial, or affected by site/environment drift.
6. If reproduced, inspect the page implementation enough to identify the likely cause. Use DevTools-style evidence where possible: console exceptions, network errors, event handlers, DOM/CSS differences, feature detection, URL/fragment handling, storage/cookie state, or minimized page code.
7. Update the Markdown report if the helper only produced a scaffold. Keep evidence tied to Bugzilla fields, comment 0, attachments, browser version output, screenshots/videos, command logs, and browser observations.
8. After all per-bug reports are finalized, regenerate the aggregate summary from the completed reports without rerunning diagnosis:

```bash
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py --summary-only --output-dir output
```

This writes `summary.md` next to `output/` by default. Use `--summary-path path/to/summary.md` when the summary should live elsewhere. The summary format is:

- `# Diagnosis Summary`
- `## Bug [<id>](https://bugzilla.mozilla.org/show_bug.cgi?id=<id>)`
- `### Diagnosis`
- `### Cause Analysis`

Keep the final report concise and include:

- Bug metadata
- Bugzilla evidence
- Firefox version selection
- Chrome version selection
- Controlled browser reproduction evidence
- Actual-vs-expected comparison
- Diagnosis
- Cause analysis, when reproduced
- Confidence
- Suggested next steps
- Sources and artifacts

## Useful Options

```bash
# Use a specific Firefox binary.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --firefox-bin /Applications/Firefox.app/Contents/MacOS/firefox

# Download the requested Firefox release when no local match is installed.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --download-firefox

# Capture a specific URL if Bugzilla has no usable target URL.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --url https://example.com/

# Gather Bugzilla evidence and write a report without launching Firefox.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --skip-browser

# Refresh only the aggregate summary from existing reports; do not fetch Bugzilla data or launch browsers.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py --summary-only --output-dir output

# Write a diagnosis report without updating the aggregate summary.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --no-summary
```
