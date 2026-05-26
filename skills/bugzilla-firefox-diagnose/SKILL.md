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
The helper uses `scripts/puppeteer_capture.mjs` for browser automation. If Node cannot resolve Puppeteer, run `npm install` in the `bugzilla-firefox-diagnose` skill directory before rerunning the helper.

The helper:

- Fetches the Bugzilla REST payload for the bug, comments, attachment metadata, and history.
- Infers the Firefox version from Bugzilla fields and comments.
- Infers the target URL from the Bugzilla `url` field and comments.
- Selects a Firefox binary whose reported major version matches the bug when possible.
- Can download a matching archived Firefox release on macOS into a temp cache when `--download-firefox` is provided.
- Captures Firefox screenshots and page state with Puppeteer at common desktop and mobile-ish viewport sizes.
- Writes `output/bug_<id>/diagnosis.md` and supporting Firefox artifacts under `output/bug_<id>/firefox/`.
- For reproduced issues, the completed diagnosis must add a reduced cause-validation test case under `output/bug_<id>/testcase/` and a minimal standalone test case under `output/bug_<id>/minimal-testcase/`.
- Appends to `summary.md` next to the output directory with linked Bugzilla bug headings and each report's Diagnosis and Cause Analysis sections.

The helper output is only a starting point. A completed diagnosis must execute the reported reproduction steps and compare Firefox with Chrome.

## Required Reproduction Process

For each bug:

1. Read comment 0 from `output/bug_<id>/firefox/bugzilla_payload.json`.
2. Extract the first-comment preconditions, steps to reproduce, expected behavior, actual behavior, environment, and notes. Do not rely only on the bug summary.
3. Inspect public Bugzilla artifacts, including attachment metadata and any available screenshots/videos, to understand the reporter's Firefox-vs-Chrome claim.
4. Execute the first-comment steps in Firefox and Chrome under controlled conditions.
5. Compare Firefox behavior against Chrome behavior and compare both browsers against the expected and actual results from comment 0.
6. If Firefox reproduces the reported actual behavior while Chrome satisfies the expected behavior, analyze the page to identify the likely cause.
7. For reproduced issues, create a focused reduced test case that demonstrates the cause analysis is true, not just that the original site still fails, and also create a minimal standalone test case.
8. If reproduction cannot be completed, write a partial diagnosis that clearly names the blocker, what evidence was collected, and what still needs to be done.

## Controlled Browser Comparison

Use comparable conditions for Firefox and Chrome:

- Use Puppeteer as the default browser automation tool for Firefox and Chrome probes. Prefer short `.mjs` scripts using `puppeteer-core` with explicit `executablePath` values for the selected browser binaries.
- Do not use Selenium, `geckodriver` HTTP calls, or hand-rolled Chrome DevTools Protocol clients unless Puppeteer cannot perform a required capability. If a fallback is required, document the limitation in the report.
- For simple navigation captures, reuse `scripts/puppeteer_capture.mjs`; for interaction-heavy bugs, create a task-specific Puppeteer probe under the bug output directory and collect screenshots, console events, failed requests, and DOM/page state from the same scripted steps in both browsers.
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

## Cause-Validation Test Cases

When the comparison is classified as **Reproduced cross-browser issue**, add both a reduced cause-validation test case and a minimal standalone test case before finalizing the diagnosis:

- Create `output/bug_<id>/testcase/` with the smallest practical HTML/CSS/JS assets needed to isolate the suspected cause.
- Make the causal condition observable and, when practical, controllable: include a failing path and a control/fixed path, mode switch, or equivalent assertion that distinguishes the suspected cause from the symptom.
- Prefer self-contained static files such as `index.html`, `style.css`, and `testcase_probe.mjs`. Avoid external dependencies unless the bug specifically depends on them.
- Run the test case in Firefox and Chrome with comparable Puppeteer steps, collecting screenshots, console output, DOM state, and command logs under `output/bug_<id>/testcase/artifacts/`.
- Record objective pass/fail criteria in the report so the reader can see why the test case validates the cause analysis.
- Create `output/bug_<id>/minimal-testcase/` with the smallest standalone reproduction that still demonstrates the browser difference. Prefer a single `index.html`; omit controls, explanatory UI, fixtures, and instrumentation unless they are required to trigger or observe the bug.
- Run the minimal test case in Firefox and Chrome as well, collecting artifacts under `output/bug_<id>/minimal-testcase/artifacts/` when practical.
- If the issue cannot be reduced because it depends on credentials, private APIs, server behavior, anti-bot checks, or unavailable proprietary code, create the smallest mock or instrumented live-site probe possible and clearly document the remaining limitation.

## Firefox Version Rules

Use the Firefox version specified in Bugzilla when the helper can identify one. Do not silently substitute another version.

If no matching Firefox binary is installed:

- Check whether the user provided `FIREFOX_BIN` or pass `--firefox-bin /path/to/firefox`.
- On macOS, pass `--download-firefox` to fetch the matching release from Mozilla's archive into the helper's temp cache.
- If a non-matching local Firefox is useful only for exploratory evidence, pass `--allow-version-mismatch` and state the mismatch in the report.
- If the exact version is required and unavailable, write the report with a clear blocked/partial diagnosis instead of pretending reproduction happened.

## Diagnosis Process

After running the helper:

1. Read `output/bug_<id>/diagnosis.md`.
2. Read comment 0 from the Bugzilla payload and extract its steps, expected result, and actual result.
3. Inspect public Bugzilla artifacts and Firefox helper screenshots/page state in `output/bug_<id>/firefox/`.
4. Execute the comment-0 steps in Firefox and Chrome with Puppeteer, collecting comparable evidence for both browsers.
5. Compare Firefox vs Chrome and actual vs expected. State whether the bug is reproduced, not reproduced, blocked/partial, or affected by site/environment drift.
6. If reproduced, inspect the page implementation enough to identify the likely cause. Use Puppeteer evidence where possible: console exceptions, network errors, event handlers, DOM/CSS differences, feature detection, URL/fragment handling, storage/cookie state, or minimized page code.
7. If reproduced, create and run the reduced cause-validation test case and the minimal standalone test case, then cite their files and artifacts in the report.
8. Update the Markdown report if the helper only produced a scaffold. Keep evidence tied to Bugzilla fields, comment 0, attachments, browser version output, screenshots/videos, command logs, browser observations, and the test cases.
9. After all per-bug reports are finalized, append missing entries to the aggregate summary without rerunning diagnosis:

```bash
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py --summary-only --output-dir output
```

This appends missing entries to `summary.md` next to `output/` by default. Use `--summary-path path/to/summary.md` when the summary should live elsewhere. The summary format is:

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
- Cause-validation test cases, when reproduced
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

# Append missing entries to the aggregate summary from existing reports; do not fetch Bugzilla data or launch browsers.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py --summary-only --output-dir output

# Write a diagnosis report without updating the aggregate summary.
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --no-summary
```
