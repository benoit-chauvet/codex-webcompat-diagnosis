#!/usr/bin/env python3
"""Fetch a Bugzilla bug, attempt Firefox reproduction, and write a diagnosis report."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urlparse
from urllib.request import Request, urlopen


BUGZILLA_BASE = "https://bugzilla.mozilla.org"
URL_RE = re.compile(r"https?://[^\s<>)\"']+", re.IGNORECASE)
REPORT_TITLE_RE = re.compile(r"^#\s+Bug\s+(\d+)\s+Diagnosis\s*$", re.MULTILINE)
SECTION_HEADING_RE = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
VERSION_PATTERNS = [
    re.compile(r"\bFirefox\s+(?:Nightly\s+|Release\s+|Beta\s+|version\s+)?([0-9]{2,3}(?:\.[0-9A-Za-z]+)*)", re.IGNORECASE),
    re.compile(r"\b(?:Fx|FF)\s*([0-9]{2,3}(?:\.[0-9A-Za-z]+)*)\b", re.IGNORECASE),
    re.compile(r"\bFirefox/([0-9]{2,3}(?:\.[0-9A-Za-z]+)*)", re.IGNORECASE),
]


@dataclass(frozen=True)
class FirefoxCandidate:
    path: Path
    version_text: str
    major: int | None


@dataclass(frozen=True)
class CaptureResult:
    viewport: str
    screenshot: Path
    returncode: int | None
    stdout: str
    stderr: str
    timed_out: bool


@dataclass(frozen=True)
class DownloadResult:
    candidate: FirefoxCandidate | None
    notes: list[str]


def normalize_bug_id(value: str) -> str:
    match = re.search(r"\d+", value)
    if not match:
        raise SystemExit(f"not a Bugzilla bug id: {value!r}")
    return match.group(0)


def bugzilla_url(bugzilla_base: str, path: str, params: dict[str, str] | None = None) -> str:
    url = f"{bugzilla_base.rstrip('/')}{path}"
    if params:
        return f"{url}?{urlencode(params)}"
    return url


def fetch_json(url: str) -> dict:
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "bugzilla-firefox-diagnose/1.0",
        },
    )
    try:
        with urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8", errors="replace"))
    except HTTPError as error:
        return {
            "_fetch_error": f"HTTP {error.code}: {error.reason}",
            "_body": error.read().decode("utf-8", errors="replace")[:4000],
        }
    except (URLError, TimeoutError, json.JSONDecodeError) as error:
        return {"_fetch_error": str(error)}


def fetch_bugzilla_payload(bug_id: str, bugzilla_base: str) -> dict:
    endpoints = {
        "bug": bugzilla_url(bugzilla_base, f"/rest/bug/{bug_id}"),
        "comments": bugzilla_url(bugzilla_base, f"/rest/bug/{bug_id}/comment"),
        "attachments": bugzilla_url(
            bugzilla_base,
            f"/rest/bug/{bug_id}/attachment",
            {"exclude_fields": "data"},
        ),
        "history": bugzilla_url(bugzilla_base, f"/rest/bug/{bug_id}/history"),
    }
    return {
        "bug_id": bug_id,
        "show_bug": bugzilla_url(bugzilla_base, "/show_bug.cgi", {"id": bug_id}),
        "fetched_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "endpoints": endpoints,
        "responses": {name: fetch_json(url) for name, url in endpoints.items()},
    }


def response_bug(payload: dict) -> dict:
    bugs = payload.get("responses", {}).get("bug", {}).get("bugs", [])
    return bugs[0] if bugs else {}


def response_comments(payload: dict) -> list[dict]:
    bug_id = str(payload.get("bug_id", ""))
    comments_by_bug = payload.get("responses", {}).get("comments", {}).get("bugs", {})
    comments = comments_by_bug.get(bug_id, {}).get("comments", [])
    return comments if isinstance(comments, list) else []


def response_attachments(payload: dict) -> list[dict]:
    bug_id = str(payload.get("bug_id", ""))
    attachments_by_bug = payload.get("responses", {}).get("attachments", {}).get("bugs", {})
    attachments = attachments_by_bug.get(bug_id, [])
    return attachments if isinstance(attachments, list) else []


def compact(value: object, limit: int = 500) -> str:
    if value is None:
        return ""
    text = str(value).replace("\r\n", "\n").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def add_unique(items: list[str], value: str) -> None:
    if value and value not in items:
        items.append(value)


def text_sources(payload: dict) -> list[tuple[str, str]]:
    bug = response_bug(payload)
    sources: list[tuple[str, str]] = []
    for key in (
        "summary",
        "version",
        "cf_user_story",
        "status_whiteboard",
        "whiteboard",
        "keywords",
        "platform",
        "op_sys",
        "url",
    ):
        value = bug.get(key)
        if isinstance(value, list):
            value = " ".join(str(item) for item in value)
        if value:
            sources.append((f"bug.{key}", str(value)))
    for comment in response_comments(payload):
        text = comment.get("text")
        if text:
            sources.append((f"comment {comment.get('id', '?')}", str(text)))
    return sources


def infer_firefox_versions(payload: dict) -> list[str]:
    versions: list[str] = []
    for source, text in text_sources(payload):
        for pattern in VERSION_PATTERNS:
            for match in pattern.finditer(text):
                version = match.group(1)
                if version:
                    add_unique(versions, version)

        if source == "bug.version":
            match = re.search(r"\b([0-9]{2,3}(?:\.[0-9A-Za-z]+)*)\b", text)
            if match:
                add_unique(versions, match.group(1))
    return versions


def major_version(version: str | None) -> int | None:
    if not version:
        return None
    match = re.search(r"\d+", version)
    return int(match.group(0)) if match else None


def clean_url(raw_url: str) -> str:
    return raw_url.rstrip(".,;:)]}\"'")


def is_target_url(raw_url: str, bugzilla_base: str) -> bool:
    parsed = urlparse(raw_url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return False
    bugzilla_host = urlparse(bugzilla_base).netloc.lower()
    return parsed.netloc.lower() != bugzilla_host


def infer_target_urls(payload: dict, bugzilla_base: str) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    seen: set[str] = set()
    bug = response_bug(payload)
    bug_url = str(bug.get("url") or "").strip()
    if bug_url and is_target_url(bug_url, bugzilla_base):
        urls.append((bug_url, "bug.url"))
        seen.add(bug_url)

    for source, text in text_sources(payload):
        for match in URL_RE.finditer(text):
            url = clean_url(match.group(0))
            if is_target_url(url, bugzilla_base) and url not in seen:
                urls.append((url, source))
                seen.add(url)
    return urls


def run_version(binary: Path) -> FirefoxCandidate:
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        return FirefoxCandidate(binary, f"version check failed: {error}", None)

    version_text = (result.stdout or result.stderr).strip()
    return FirefoxCandidate(binary, version_text, major_version(version_text))


def candidate_binary_paths(explicit: str | None, target_major: int | None) -> list[Path]:
    paths: list[Path] = []

    def add(value: str | Path | None) -> None:
        if not value:
            return
        path = Path(value).expanduser()
        if path not in paths:
            paths.append(path)

    add(explicit)
    add(os.environ.get("FIREFOX_BIN"))
    if target_major is not None:
        add(os.environ.get(f"FIREFOX_{target_major}_BIN"))

    for name in ("firefox", "firefox-nightly", "firefox-developer-edition"):
        found = shutil.which(name)
        if found:
            add(found)

    mac_apps = [
        "/Applications/Firefox.app/Contents/MacOS/firefox",
        "/Applications/Firefox Nightly.app/Contents/MacOS/firefox",
        "/Applications/Firefox Developer Edition.app/Contents/MacOS/firefox",
    ]
    if target_major is not None:
        mac_apps.insert(0, f"/Applications/Firefox {target_major}.app/Contents/MacOS/firefox")
    for path in mac_apps:
        add(path)

    return paths


def choose_firefox(
    explicit: str | None,
    target_major: int | None,
    allow_version_mismatch: bool,
) -> tuple[FirefoxCandidate | None, list[FirefoxCandidate]]:
    candidates = [
        run_version(path)
        for path in candidate_binary_paths(explicit, target_major)
        if path.exists() and os.access(path, os.X_OK)
    ]
    if target_major is not None:
        for candidate in candidates:
            if candidate.major == target_major:
                return candidate, candidates
        if not allow_version_mismatch:
            return None, candidates
    return (candidates[0] if candidates else None), candidates


def release_version_for_download(versions: list[str]) -> str | None:
    for version in versions:
        if re.fullmatch(r"\d{2,3}", version):
            return f"{version}.0"
        if re.fullmatch(r"\d{2,3}\.\d+(?:\.\d+)?", version):
            return version
    for version in versions:
        major = major_version(version)
        if major is not None:
            return f"{major}.0"
    return None


def archive_download_url(version: str, locale: str) -> str:
    filename = f"Firefox {version}.dmg"
    return (
        "https://archive.mozilla.org/pub/firefox/releases/"
        f"{quote(version)}/mac/{quote(locale)}/{quote(filename)}"
    )


def download_file(url: str, destination: Path) -> None:
    request = Request(
        url,
        headers={"User-Agent": "bugzilla-firefox-diagnose/1.0"},
    )
    destination.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = destination.with_suffix(destination.suffix + ".tmp")
    with urlopen(request, timeout=120) as response, tmp_path.open("wb") as output:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            output.write(chunk)
    tmp_path.replace(destination)


def install_firefox_from_dmg(dmg_path: Path, install_dir: Path) -> Path:
    if sys.platform != "darwin":
        raise RuntimeError("automatic Firefox archive installation is currently implemented for macOS only")

    install_dir.mkdir(parents=True, exist_ok=True)
    app_dir = install_dir / "Firefox.app"
    binary = app_dir / "Contents" / "MacOS" / "firefox"
    if binary.exists():
        return binary

    with tempfile.TemporaryDirectory(prefix="bugzilla-firefox-dmg-") as mount_root:
        mount_point = Path(mount_root) / "mnt"
        mount_point.mkdir()
        attached = False
        try:
            attach = subprocess.run(
                [
                    "hdiutil",
                    "attach",
                    "-nobrowse",
                    "-readonly",
                    "-mountpoint",
                    str(mount_point),
                    str(dmg_path),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
                check=False,
            )
            if attach.returncode != 0:
                raise RuntimeError(f"hdiutil attach failed: {attach.stderr.strip() or attach.stdout.strip()}")
            attached = True

            mounted_app = mount_point / "Firefox.app"
            if not mounted_app.exists():
                apps = sorted(mount_point.glob("*.app"))
                if not apps:
                    raise RuntimeError("mounted DMG did not contain a Firefox app bundle")
                mounted_app = apps[0]

            if app_dir.exists():
                shutil.rmtree(app_dir)
            shutil.copytree(mounted_app, app_dir, symlinks=True)
        finally:
            if attached:
                subprocess.run(
                    ["hdiutil", "detach", str(mount_point), "-quiet"],
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    timeout=60,
                    check=False,
                )

    if not binary.exists():
        raise RuntimeError(f"installed Firefox binary was not found at {binary}")
    return binary


def download_firefox_release(
    versions: list[str],
    cache_dir: Path,
    locale: str,
) -> DownloadResult:
    notes: list[str] = []
    version = release_version_for_download(versions)
    if not version:
        return DownloadResult(None, ["No Firefox release version could be inferred for archive download."])

    if sys.platform != "darwin":
        return DownloadResult(None, ["Automatic Firefox archive download is currently implemented for macOS only."])

    download_dir = cache_dir / version
    dmg_path = download_dir / f"Firefox {version}.dmg"
    install_dir = download_dir / "app"
    binary = install_dir / "Firefox.app" / "Contents" / "MacOS" / "firefox"
    url = archive_download_url(version, locale)

    try:
        if binary.exists():
            notes.append(f"Using cached Firefox archive install: {binary}")
        else:
            if not dmg_path.exists():
                notes.append(f"Downloading Firefox {version} from {url}")
                download_file(url, dmg_path)
            else:
                notes.append(f"Using cached Firefox DMG: {dmg_path}")
            binary = install_firefox_from_dmg(dmg_path, install_dir)
            notes.append(f"Installed Firefox archive build at {binary}")
        return DownloadResult(run_version(binary), notes)
    except Exception as error:
        notes.append(f"Firefox archive download/install failed: {error}")
        return DownloadResult(None, notes)


def parse_viewport(value: str) -> tuple[int, int]:
    match = re.fullmatch(r"\s*(\d{2,5})x(\d{2,5})\s*", value)
    if not match:
        raise argparse.ArgumentTypeError(f"invalid viewport {value!r}; use WIDTHxHEIGHT")
    return int(match.group(1)), int(match.group(2))


def capture_firefox(
    firefox: FirefoxCandidate,
    url: str,
    artifact_dir: Path,
    viewport: tuple[int, int],
    timeout: int,
) -> CaptureResult:
    width, height = viewport
    viewport_label = f"{width}x{height}"
    screenshot = artifact_dir / f"screenshot_firefox_{viewport_label}.png"
    profile = artifact_dir / "profiles" / viewport_label
    if profile.exists():
        shutil.rmtree(profile)
    profile.mkdir(parents=True)
    if screenshot.exists():
        screenshot.unlink()

    command = [
        str(firefox.path),
        "--headless",
        "--profile",
        str(profile),
        "--screenshot",
        str(screenshot),
        "--window-size",
        f"{width},{height}",
        url,
    ]
    try:
        result = subprocess.run(
            command,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
        wait_for_file(screenshot, 5)
        return CaptureResult(
            viewport_label,
            screenshot,
            result.returncode,
            result.stdout.strip(),
            result.stderr.strip(),
            False,
        )
    except subprocess.TimeoutExpired as error:
        return CaptureResult(
            viewport_label,
            screenshot,
            None,
            (error.stdout or "").strip() if isinstance(error.stdout, str) else "",
            (error.stderr or "").strip() if isinstance(error.stderr, str) else "",
            True,
        )


def wait_for_file(path: Path, timeout_seconds: float) -> bool:
    deadline = datetime.now().timestamp() + timeout_seconds
    while datetime.now().timestamp() < deadline:
        if path.exists() and path.stat().st_size > 0:
            return True
        time.sleep(0.1)
    return path.exists() and path.stat().st_size > 0


def markdown_list(items: list[str]) -> str:
    if not items:
        return "- None found"
    return "\n".join(f"- {item}" for item in items)


def report_bug_id(report_text: str, report_path: Path) -> str | None:
    match = REPORT_TITLE_RE.search(report_text)
    if match:
        return match.group(1)
    match = re.search(r"bug_(\d+)_diagnosis\.md$", report_path.name)
    if match:
        return match.group(1)
    match = re.search(r"bug_(\d+)$", report_path.parent.name)
    return match.group(1) if match else None


def report_bugzilla_url(report_text: str, bug_id: str, bugzilla_base: str) -> str:
    match = re.search(r"^Bugzilla:\s*(https?://\S+)\s*$", report_text, re.MULTILINE)
    if match:
        return match.group(1)
    return bugzilla_url(bugzilla_base, "/show_bug.cgi", {"id": bug_id})


def report_generated_at(report_text: str) -> str:
    match = re.search(r"^Generated:\s*(.+?)\s*$", report_text, re.MULTILINE)
    return match.group(1) if match else ""


def extract_markdown_section(report_text: str, heading: str) -> str:
    for match in SECTION_HEADING_RE.finditer(report_text):
        if match.group(1).strip().lower() != heading.lower():
            continue
        start = match.end()
        next_match = SECTION_HEADING_RE.search(report_text, start)
        end = next_match.start() if next_match else len(report_text)
        body = report_text[start:end].strip()
        return body or "Not documented."
    return "Not documented."


def existing_summary_order(summary_path: Path) -> list[tuple[str, str]]:
    if not summary_path.exists():
        return []
    try:
        text = summary_path.read_text(encoding="utf-8")
    except OSError:
        return []
    return re.findall(r"^##\s+Bug\s+(?:\[(\d+)\]\([^)]+\)|(\d+))\s*$", text, re.MULTILINE)


def flattened_existing_summary_order(summary_path: Path) -> list[str]:
    order: list[str] = []
    for linked, plain in existing_summary_order(summary_path):
        bug_id = linked or plain
        if bug_id:
            order.append(bug_id)
    return order


def default_summary_path(output_dir: Path) -> Path:
    return output_dir.parent / "summary.md"


def sort_summary_entries(entries: list[dict[str, str]], summary_path: Path) -> list[dict[str, str]]:
    existing_order = flattened_existing_summary_order(summary_path)
    if existing_order:
        rank = {bug_id: index for index, bug_id in enumerate(existing_order)}
        return sorted(
            entries,
            key=lambda entry: (
                rank.get(entry["bug_id"], len(rank)),
                entry["generated_at"],
                entry["bug_id"],
            ),
        )
    return sorted(entries, key=lambda entry: (entry["generated_at"], entry["bug_id"]))


def report_paths_for_summary(output_dir: Path) -> list[Path]:
    return sorted(
        {
            *output_dir.glob("bug_*_diagnosis.md"),
            *output_dir.glob("bug_*/diagnosis.md"),
        }
    )


def summary_entry(report_path: Path, bugzilla_base: str) -> dict[str, str] | None:
    report_text = report_path.read_text(encoding="utf-8")
    bug_id = report_bug_id(report_text, report_path)
    if not bug_id:
        return None
    return {
        "bug_id": bug_id,
        "bugzilla_url": report_bugzilla_url(report_text, bug_id, bugzilla_base),
        "generated_at": report_generated_at(report_text),
        "diagnosis": extract_markdown_section(report_text, "Diagnosis"),
        "cause_analysis": extract_markdown_section(report_text, "Cause Analysis"),
    }


def format_summary_entry(entry: dict[str, str]) -> str:
    lines = [
        f"## Bug [{entry['bug_id']}]({entry['bugzilla_url']})",
        "",
        "### Diagnosis",
        "",
        entry["diagnosis"],
        "",
        "### Cause Analysis",
        "",
        entry["cause_analysis"],
    ]
    return "\n".join(lines).rstrip()


def append_summary_entries(summary_path: Path, entries: list[dict[str, str]]) -> int:
    if not entries:
        return 0

    summary_path.parent.mkdir(parents=True, exist_ok=True)
    existing = summary_path.read_text(encoding="utf-8") if summary_path.exists() else ""
    additions = "\n\n".join(format_summary_entry(entry) for entry in entries)
    with summary_path.open("a", encoding="utf-8") as summary_file:
        if not existing.strip():
            summary_file.write("# Diagnosis Summary\n\n")
        elif existing.endswith("\n\n"):
            pass
        elif existing.endswith("\n"):
            summary_file.write("\n")
        else:
            summary_file.write("\n\n")
        summary_file.write(additions)
        summary_file.write("\n")
    return len(entries)


def append_missing_summary_entries(output_dir: Path, summary_path: Path, bugzilla_base: str) -> int:
    entries: list[dict[str, str]] = []
    existing_bug_ids = set(flattened_existing_summary_order(summary_path))
    for report_path in report_paths_for_summary(output_dir):
        entry = summary_entry(report_path, bugzilla_base)
        if not entry or entry["bug_id"] in existing_bug_ids:
            continue
        entries.append(entry)
        existing_bug_ids.add(entry["bug_id"])
    return append_summary_entries(summary_path, sort_summary_entries(entries, summary_path))


def append_summary_report(report_path: Path, summary_path: Path, bugzilla_base: str) -> int:
    entry = summary_entry(report_path, bugzilla_base)
    return append_summary_entries(summary_path, [entry] if entry else [])


def command_status(result: CaptureResult) -> str:
    if result.timed_out:
        return "timed out"
    return f"exit {result.returncode}"


def write_report(
    report_path: Path,
    artifact_dir: Path,
    payload: dict,
    versions: list[str],
    target_urls: list[tuple[str, str]],
    selected_url: str | None,
    firefox: FirefoxCandidate | None,
    candidates: list[FirefoxCandidate],
    download_notes: list[str],
    captures: list[CaptureResult],
    skipped_browser: bool,
    allow_version_mismatch: bool,
) -> None:
    bug = response_bug(payload)
    attachments = response_attachments(payload)
    target_version = versions[0] if versions else None
    target_major = major_version(target_version)

    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    metadata = [
        f"Summary: {compact(bug.get('summary')) or 'unknown'}",
        f"Product / Component: {compact(bug.get('product')) or 'unknown'} / {compact(bug.get('component')) or 'unknown'}",
        f"Status: {compact(bug.get('status')) or 'unknown'}",
        f"Severity / Priority: {compact(bug.get('severity')) or 'unknown'} / {compact(bug.get('priority')) or 'unknown'}",
        f"Platform / OS: {compact(bug.get('platform')) or 'unknown'} / {compact(bug.get('op_sys')) or 'unknown'}",
    ]
    url_lines = [f"{url} ({source})" for url, source in target_urls]
    candidate_lines = [
        f"{candidate.path} - {candidate.version_text or 'unknown version'}"
        for candidate in candidates
    ]
    capture_lines = []
    for capture in captures:
        exists = capture.screenshot.exists() and capture.screenshot.stat().st_size > 0
        file_note = str(capture.screenshot) if exists else f"{capture.screenshot} (not created)"
        capture_lines.append(f"{capture.viewport}: {command_status(capture)} - {file_note}")

    if skipped_browser:
        diagnosis = "Browser launch was skipped. The report contains Bugzilla evidence only."
        confidence = "Low for rendering diagnosis until Firefox evidence is collected."
    elif not selected_url:
        diagnosis = "No target site URL was found in the Bugzilla payload, so Firefox reproduction could not be attempted."
        confidence = "Low for rendering diagnosis until a target URL is supplied."
    elif not firefox:
        if target_major is None:
            diagnosis = "No usable Firefox version was inferred or found, so reproduction could not be attempted."
        else:
            diagnosis = f"No installed Firefox binary matching major version {target_major} was found, so reproduction could not be attempted."
        confidence = "Low for rendering diagnosis until the requested Firefox version is available."
    elif captures:
        mismatch = ""
        if target_major is not None and firefox.major != target_major:
            mismatch = " The selected Firefox version does not match the Bugzilla version, so treat the browser evidence as exploratory."
        diagnosis = (
            "Firefox browser evidence was captured. Inspect the screenshots and update this section with the visual or behavioral "
            f"finding tied to the Bugzilla expected/actual behavior.{mismatch}"
        )
        confidence = "Medium for evidence collection; final diagnosis depends on screenshot inspection."
    else:
        diagnosis = "Firefox was selected, but no browser captures were produced."
        confidence = "Low until the browser command succeeds."

    cause_analysis = (
        "Not determined by the helper scaffold. Replace this section after completing the controlled "
        "Firefox-vs-Chrome comparison and implementation analysis."
    )

    report = f"""# Bug {payload.get('bug_id')} Diagnosis

Generated: {generated_at}
Bugzilla: {payload.get('show_bug')}
Artifacts: {artifact_dir}

## Bug Metadata

{markdown_list(metadata)}

## Bugzilla Evidence

- Inferred Firefox versions: {', '.join(versions) if versions else 'none'}
- Selected target URL: {selected_url or 'none'}
- Target URL candidates:
{markdown_list(url_lines)}
- Attachment metadata count: {len(attachments)}

## Firefox Version Selection

- Requested major version: {target_major if target_major is not None else 'unknown'}
- Allow version mismatch: {allow_version_mismatch}
- Selected Firefox: {str(firefox.path) if firefox else 'none'}
- Selected Firefox version output: {firefox.version_text if firefox else 'none'}
- Firefox archive download notes:
{markdown_list(download_notes)}
- Candidate Firefox binaries:
{markdown_list(candidate_lines)}

## Browser Reproduction Evidence

{markdown_list(capture_lines)}

## Diagnosis

{diagnosis}

## Cause Analysis

{cause_analysis}

## Confidence

{confidence}

## Suggested Next Steps

- If screenshots were captured, inspect them and replace the scaffold diagnosis with the observed behavior.
- If the requested Firefox version was unavailable, install or point `--firefox-bin` at that version and rerun.
- If no target URL was inferred, rerun with `--url`.
- If the issue depends on interaction, rerun manually or with browser automation that performs the required steps.

## Sources and Artifacts

- Bugzilla REST payload: {artifact_dir / 'bugzilla_payload.json'}
- Screenshot/log artifact directory: {artifact_dir}
"""
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(report, encoding="utf-8")


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch a Bugzilla bug, attempt Firefox reproduction, and write a Markdown diagnosis report."
    )
    parser.add_argument("bug_id", nargs="?", help="Bugzilla bug id or URL containing a bug id")
    parser.add_argument("--output-dir", default="output", type=Path, help="Directory for reports and artifacts")
    parser.add_argument("--bugzilla-base", default=BUGZILLA_BASE, help="Bugzilla base URL")
    parser.add_argument("--firefox-bin", help="Path to a Firefox binary to use")
    parser.add_argument("--download-firefox", action="store_true", help="Download a matching archived Firefox release on macOS if it is not installed")
    parser.add_argument(
        "--firefox-cache-dir",
        default=Path(tempfile.gettempdir()) / "bugzilla-firefox-diagnose-cache",
        type=Path,
        help="Cache directory for archived Firefox downloads. Default: system temp cache",
    )
    parser.add_argument("--firefox-locale", default="en-US", help="Locale for archived Firefox downloads. Default: en-US")
    parser.add_argument("--url", help="Target URL override if Bugzilla does not contain the right URL")
    parser.add_argument("--allow-version-mismatch", action="store_true", help="Use another Firefox if the requested major version is unavailable")
    parser.add_argument("--skip-browser", action="store_true", help="Write Bugzilla evidence without launching Firefox")
    parser.add_argument("--summary-only", action="store_true", help="Append missing diagnosis reports to summary.md without fetching Bugzilla data or launching browsers")
    parser.add_argument("--no-summary", action="store_true", help="Do not update summary.md after writing a diagnosis report")
    parser.add_argument("--summary-path", type=Path, help="Path for the aggregate summary. Default: summary.md next to the output directory")
    parser.add_argument("--timeout", default=90, type=int, help="Per-screenshot timeout in seconds")
    parser.add_argument(
        "--viewport",
        action="append",
        type=parse_viewport,
        help="Viewport to capture as WIDTHxHEIGHT. May be repeated.",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(sys.argv[1:] if argv is None else argv)
    output_dir = args.output_dir.resolve()
    summary_path = (
        args.summary_path.expanduser().resolve()
        if args.summary_path
        else default_summary_path(output_dir)
    )
    if args.summary_only:
        count = append_missing_summary_entries(output_dir, summary_path, args.bugzilla_base)
        print(f"Appended {count} missing diagnosis summary entr{'y' if count == 1 else 'ies'} to {summary_path}")
        return 0
    if not args.bug_id:
        raise SystemExit("bug_id is required unless --summary-only is used")

    bug_id = normalize_bug_id(args.bug_id)
    bug_dir = output_dir / f"bug_{bug_id}"
    artifact_dir = bug_dir / "firefox"
    report_path = bug_dir / "diagnosis.md"
    artifact_dir.mkdir(parents=True, exist_ok=True)

    print(f"Fetching Bugzilla data for bug {bug_id}...")
    payload = fetch_bugzilla_payload(bug_id, args.bugzilla_base)
    (artifact_dir / "bugzilla_payload.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True),
        encoding="utf-8",
    )

    versions = infer_firefox_versions(payload)
    target_major = major_version(versions[0] if versions else None)
    target_urls = infer_target_urls(payload, args.bugzilla_base)
    selected_url = args.url or (target_urls[0][0] if target_urls else None)

    firefox: FirefoxCandidate | None = None
    candidates: list[FirefoxCandidate] = []
    download_notes: list[str] = []
    captures: list[CaptureResult] = []
    if not args.skip_browser:
        firefox, candidates = choose_firefox(args.firefox_bin, target_major, args.allow_version_mismatch)
        if not firefox and args.download_firefox and target_major is not None:
            download = download_firefox_release(versions, args.firefox_cache_dir.expanduser().resolve(), args.firefox_locale)
            download_notes = download.notes
            if download.candidate:
                candidates.append(download.candidate)
                if download.candidate.major == target_major or args.allow_version_mismatch:
                    firefox = download.candidate
        if firefox and selected_url:
            viewports = args.viewport or [(1280, 900), (1440, 1000), (390, 844)]
            for viewport in viewports:
                label = f"{viewport[0]}x{viewport[1]}"
                print(f"Capturing Firefox screenshot at {label}...")
                captures.append(capture_firefox(firefox, selected_url, artifact_dir, viewport, args.timeout))

    write_report(
        report_path,
        artifact_dir,
        payload,
        versions,
        target_urls,
        selected_url,
        firefox,
        candidates,
        download_notes,
        captures,
        args.skip_browser,
        args.allow_version_mismatch,
    )
    print(f"Wrote diagnosis report to {report_path}")
    if not args.no_summary:
        count = append_summary_report(report_path, summary_path, args.bugzilla_base)
        print(f"Appended diagnosis summary for {count} report(s) to {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
