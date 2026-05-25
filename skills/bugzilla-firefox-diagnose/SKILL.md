---
name: bugzilla-firefox-diagnose
description: Fetch Mozilla Bugzilla web compatibility bugs, identify the Firefox version and target site from the bug data, attempt browser reproduction in that Firefox version, inspect the gathered browser evidence, and write a Markdown diagnosis to an output directory. Use when the user asks Codex to diagnose a Bugzilla bug, reproduce a webcompat issue in Firefox, or generate an output bug ID diagnosis report from Bugzilla evidence.
---

# Bugzilla Firefox Diagnose

## Workflow

Use the bundled helper for the repeatable work:

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
2. Inspect screenshots in `output/bug_<id>_firefox/`, using local image-viewing tools when available.
3. Compare what Firefox actually rendered against the Bugzilla expected/actual text and attachments metadata.
4. Update the Markdown report if the helper only produced a scaffold. Keep evidence tied to Bugzilla fields, comments, Firefox version output, screenshots, command logs, and any browser observations.

Keep the final report concise and include:

- Bug metadata
- Bugzilla evidence
- Firefox version selection
- Browser reproduction evidence
- Diagnosis
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
```
