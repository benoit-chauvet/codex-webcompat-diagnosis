# Codex WebCompat Diagnosis

This repository contains a Codex skill and helper script for diagnosing Mozilla Bugzilla web compatibility bugs with Firefox evidence.

## What It Does

The `bugzilla-firefox-diagnose` skill fetches a Bugzilla bug, extracts the target site and Firefox version from the bug data, attempts to reproduce the issue in that Firefox version, and writes a Markdown diagnosis report.
When a Firefox-only reproduction is confirmed, the completed diagnosis also includes a reduced test case that validates the cause analysis and a minimal standalone test case.

The bundled script:

- Fetches Bugzilla REST data for the bug, comments, attachment metadata, and history.
- Infers the Firefox version from Bugzilla fields and comments.
- Infers the target URL from the Bugzilla `url` field and comment text.
- Selects a local Firefox binary whose major version matches the bug.
- On macOS, can download a matching archived Firefox release with `--download-firefox`.
- Captures headless Firefox screenshots and page state with Puppeteer at desktop and mobile-ish viewport sizes.
- Writes a diagnosis report and supporting artifacts under `output/`.
- Requires reproduced diagnoses to include a focused cause-validation test case under `output/bug_<id>/testcase/` and a minimal standalone test case under `output/bug_<id>/minimal-testcase/`.

## Main Files

- `skills/bugzilla-firefox-diagnose/SKILL.md`: Codex skill instructions.
- `skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py`: helper script used by the skill.
- `skills/bugzilla-firefox-diagnose/scripts/puppeteer_capture.mjs`: Puppeteer capture helper used by the Python script.
- `output/bug_<id>/diagnosis.md`: generated diagnosis report.
- `output/bug_<id>/firefox/`: Bugzilla payload and Firefox screenshot artifacts.
- `output/bug_<id>/chrome/`: Chrome comparison artifacts when collected.
- `output/bug_<id>/testcase/`: reduced test case and artifacts validating the cause analysis for reproduced issues.
- `output/bug_<id>/minimal-testcase/`: smallest standalone reproduction for reproduced issues.
- `summary.md`: Summary of the diagnosed bugs

The installed skill copy lives at:

```bash
~/.codex/skills/bugzilla-firefox-diagnose
```

## Usage

Install the skill's Node dependency once if it is not already present:

```bash
cd ~/.codex/skills/bugzilla-firefox-diagnose
npm install
```

Run the installed skill helper:

```bash
python3 ~/.codex/skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --output-dir output --download-firefox
```

Run the source copy from this repo:

```bash
python3 skills/bugzilla-firefox-diagnose/scripts/diagnose_bugzilla_firefox.py 1905304 --output-dir output --download-firefox
```

## Useful Options

- `--download-firefox`: on macOS, download the matching Firefox release from Mozilla's archive if it is not installed.
- `--firefox-bin /path/to/firefox`: force a specific Firefox binary.
- `--firefox-cache-dir /path/to/cache`: choose where archived Firefox builds are cached.
- `--url https://example.com/`: override the target URL from Bugzilla.
- `--allow-version-mismatch`: allow exploratory capture with a non-matching Firefox version.
- `--skip-browser`: fetch Bugzilla data and write a report without launching Firefox.
- `--viewport WIDTHxHEIGHT`: add a screenshot viewport. May be repeated.

## Output

For bug `1905304`, the script writes:

```text
output/bug_1905304/diagnosis.md
output/bug_1905304/firefox/bugzilla_payload.json
output/bug_1905304/firefox/screenshot_firefox_1280x900.png
output/bug_1905304/firefox/state_firefox_1280x900.json
output/bug_1905304/firefox/screenshot_firefox_1440x1000.png
output/bug_1905304/firefox/screenshot_firefox_390x844.png
```

The report includes bug metadata, Bugzilla evidence, Firefox version selection, browser capture results, diagnosis, cause analysis, reduced and minimal test case details when reproduced, confidence, next steps, and artifact paths.

## Validation

Validate the installed skill:

```bash
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py ~/.codex/skills/bugzilla-firefox-diagnose
```

The validator requires `PyYAML` in the active Python environment.
