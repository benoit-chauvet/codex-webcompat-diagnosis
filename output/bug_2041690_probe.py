#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlparse


ROOT = Path(__file__).resolve().parent
ARTIFACT_DIR = ROOT / os.environ.get("ARTIFACT_DIR_NAME", "bug_2041690_comparison")
URL = "https://www.theaa.com/route-planner/route?from=g74%204xt&to=FK10%203SA"
FIREFOX_BIN = os.environ.get("FIREFOX_BIN", "/Applications/Firefox Nightly.app/Contents/MacOS/firefox")
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
VIEWPORTS = [(1440, 1000), (1280, 900)]


STATE_JS = r"""
(() => {
  const textOf = el => ((el && (el.innerText || el.textContent || el.value)) || '').trim();
  const rectOf = el => {
    const rect = el.getBoundingClientRect();
    return {
      x: Math.round(rect.x),
      y: Math.round(rect.y),
      width: Math.round(rect.width),
      height: Math.round(rect.height),
      visible: rect.width > 0 && rect.height > 0
    };
  };
  const computedOf = el => {
    const style = getComputedStyle(el);
    return {
      display: style.display,
      visibility: style.visibility,
      opacity: style.opacity,
      backgroundColor: style.backgroundColor,
      transform: style.transform,
      zIndex: style.zIndex
    };
  };
  const bodyText = document.body ? document.body.innerText : '';
  const buttons = [...document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"], a')]
    .map(textOf)
    .filter(Boolean)
    .slice(0, 80);
  const mapCandidates = [...document.querySelectorAll(
    '[id*="map" i], [class*="map" i], [id*="route" i], [class*="route" i], canvas, svg'
  )].slice(0, 140).map(el => ({
    tag: el.tagName,
    id: el.id || '',
    className: typeof el.className === 'string' ? el.className : String(el.className || ''),
    rect: rectOf(el),
    style: computedOf(el),
    text: textOf(el).slice(0, 120)
  }));
  const visibleImages = [...document.images].filter(img => {
    const rect = img.getBoundingClientRect();
    return rect.width > 0 && rect.height > 0;
  }).slice(0, 120).map(img => ({
    src: img.currentSrc || img.src,
    complete: img.complete,
    naturalWidth: img.naturalWidth,
    naturalHeight: img.naturalHeight,
    rect: rectOf(img)
  }));
  const canvases = [...document.querySelectorAll('canvas')].map(canvas => ({
    width: canvas.width,
    height: canvas.height,
    rect: rectOf(canvas),
    style: computedOf(canvas)
  }));
  const svgs = [...document.querySelectorAll('svg')].slice(0, 80).map(svg => ({
    rect: rectOf(svg),
    className: typeof svg.className === 'string' ? svg.className : String(svg.className || ''),
    pathCount: svg.querySelectorAll('path').length,
    polylineCount: svg.querySelectorAll('polyline').length
  }));
  return {
    href: location.href,
    title: document.title,
    readyState: document.readyState,
    viewport: { innerWidth, innerHeight, devicePixelRatio },
    bodyTextSample: bodyText.slice(0, 1200),
    hasRouteDistance: /38\.8 miles|47\.0 miles|Via M73|Via M8/i.test(bodyText),
    hasDirections: /Head north|Merlin Wynd|Print|Plan route/i.test(bodyText),
    hasConsentText: /We Care About Your Privacy|Accept All|Decline All/i.test(bodyText),
    visibleImageCount: visibleImages.length,
    visibleImages,
    canvasCount: canvases.length,
    canvases,
    svgCount: svgs.length,
    svgs,
    mapCandidates,
    buttons
  };
})()
"""


CLICK_CONSENT_JS = r"""
(() => {
  const textOf = el => ((el && (el.innerText || el.textContent || el.value)) || '').trim();
  const controls = [...document.querySelectorAll('button, [role="button"], input[type="button"], input[type="submit"], a')];
  const target = controls.find(el => /^(Accept All|Accept all|Accept)$/i.test(textOf(el)));
  if (target) {
    target.click();
    return textOf(target);
  }
  return null;
})()
"""


def run_version(binary: str) -> str:
  result = subprocess.run(
    [binary, "--version"],
    text=True,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    timeout=20,
    check=False,
  )
  return (result.stdout or result.stderr).strip()


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
  body = None if payload is None else json.dumps(payload).encode("utf-8")
  request = urllib.request.Request(
    url,
    data=body,
    method=method,
    headers={"Content-Type": "application/json"},
  )
  with urllib.request.urlopen(request, timeout=25) as response:
    raw = response.read()
  return json.loads(raw.decode("utf-8") or "{}")


def wait_for_http(url: str, timeout: float = 15) -> dict[str, Any]:
  deadline = time.time() + timeout
  last_error: Exception | None = None
  while time.time() < deadline:
    try:
      return request_json("GET", url)
    except Exception as error:  # noqa: BLE001 - preserve startup details.
      last_error = error
      time.sleep(0.2)
  raise RuntimeError(f"timed out waiting for {url}: {last_error}")


def free_port() -> int:
  with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.bind(("127.0.0.1", 0))
    return int(sock.getsockname()[1])


def clean_dir(path: Path) -> None:
  if path.exists():
    shutil.rmtree(path)
  path.mkdir(parents=True)


def firefox_probe(width: int, height: int) -> dict[str, Any]:
  label = f"{width}x{height}"
  out_dir = ARTIFACT_DIR / "firefox" / label
  clean_dir(out_dir)
  profile = ARTIFACT_DIR / "profiles" / f"firefox_{label}"
  clean_dir(profile)

  port = free_port()
  log_path = out_dir / "geckodriver.log"
  gecko = subprocess.Popen(
    ["geckodriver", "--port", str(port)],
    stdout=log_path.open("w"),
    stderr=subprocess.STDOUT,
    text=True,
  )
  session_id = None
  try:
    wait_for_http(f"http://127.0.0.1:{port}/status")
    payload = {
      "capabilities": {
        "alwaysMatch": {
          "browserName": "firefox",
          "acceptInsecureCerts": True,
          "moz:firefoxOptions": {
            "binary": FIREFOX_BIN,
            "args": ["-headless", "-profile", str(profile)],
            "prefs": {
              "app.update.auto": False,
              "app.update.enabled": False,
              "browser.shell.checkDefaultBrowser": False,
            },
          },
        }
      }
    }
    session = request_json("POST", f"http://127.0.0.1:{port}/session", payload)
    session_id = session["value"]["sessionId"]
    base = f"http://127.0.0.1:{port}/session/{session_id}"
    request_json("POST", f"{base}/window/rect", {"width": width, "height": height})
    request_json("POST", f"{base}/url", {"url": URL})
    time.sleep(10)
    clicked = request_json("POST", f"{base}/execute/sync", {"script": f"return {CLICK_CONSENT_JS.strip()}", "args": []})["value"]
    time.sleep(12)
    state = request_json("POST", f"{base}/execute/sync", {"script": f"return {STATE_JS.strip()}", "args": []})["value"]
    png = request_json("GET", f"{base}/screenshot")["value"]
    screenshot = out_dir / f"screenshot_firefox_{label}.png"
    screenshot.write_bytes(base64.b64decode(png))
    state_path = out_dir / f"state_firefox_{label}.json"
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    return {
      "browser": "firefox",
      "viewport": label,
      "binary": FIREFOX_BIN,
      "version": run_version(FIREFOX_BIN),
      "clickedConsent": clicked,
      "screenshot": str(screenshot),
      "state": str(state_path),
      "capabilities": session["value"].get("capabilities", {}),
      "geckodriverLog": str(log_path),
      "summary": summarize_state(state),
    }
  finally:
    if session_id:
      try:
        request_json("DELETE", f"http://127.0.0.1:{port}/session/{session_id}")
      except Exception:
        pass
    gecko.terminate()
    try:
      gecko.wait(timeout=5)
    except subprocess.TimeoutExpired:
      gecko.kill()


class CDP:
  def __init__(self, ws_url: str):
    parsed = urlparse(ws_url)
    self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=15)
    self.sock.settimeout(30)
    key = base64.b64encode(os.urandom(16)).decode("ascii")
    path = parsed.path
    if parsed.query:
      path += "?" + parsed.query
    request = (
      f"GET {path} HTTP/1.1\r\n"
      f"Host: {parsed.hostname}:{parsed.port}\r\n"
      "Upgrade: websocket\r\n"
      "Connection: Upgrade\r\n"
      f"Sec-WebSocket-Key: {key}\r\n"
      "Sec-WebSocket-Version: 13\r\n\r\n"
    )
    self.sock.sendall(request.encode("ascii"))
    response = b""
    while b"\r\n\r\n" not in response:
      response += self.sock.recv(4096)
    if b" 101 " not in response.split(b"\r\n", 1)[0]:
      raise RuntimeError(response.decode("utf-8", errors="replace"))
    self.next_id = 1
    self.events: list[dict[str, Any]] = []
    self.requests: dict[str, str] = {}
    self.failures: list[dict[str, Any]] = []

  def close(self) -> None:
    self.sock.close()

  def _send_frame(self, text: str) -> None:
    payload = text.encode("utf-8")
    header = bytearray([0x81])
    length = len(payload)
    if length < 126:
      header.append(0x80 | length)
    elif length < 65536:
      header.append(0x80 | 126)
      header.extend(struct.pack("!H", length))
    else:
      header.append(0x80 | 127)
      header.extend(struct.pack("!Q", length))
    mask = os.urandom(4)
    header.extend(mask)
    masked = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
    self.sock.sendall(header + masked)

  def _recv_exact(self, count: int) -> bytes:
    chunks = []
    remaining = count
    while remaining:
      chunk = self.sock.recv(remaining)
      if not chunk:
        raise RuntimeError("websocket closed")
      chunks.append(chunk)
      remaining -= len(chunk)
    return b"".join(chunks)

  def _recv_frame(self) -> str:
    while True:
      first, second = self._recv_exact(2)
      opcode = first & 0x0F
      masked = bool(second & 0x80)
      length = second & 0x7F
      if length == 126:
        length = struct.unpack("!H", self._recv_exact(2))[0]
      elif length == 127:
        length = struct.unpack("!Q", self._recv_exact(8))[0]
      mask = self._recv_exact(4) if masked else b""
      payload = self._recv_exact(length)
      if masked:
        payload = bytes(byte ^ mask[index % 4] for index, byte in enumerate(payload))
      if opcode == 1:
        return payload.decode("utf-8", errors="replace")
      if opcode == 8:
        raise RuntimeError("websocket closed")

  def _record_event(self, message: dict[str, Any]) -> None:
    self.events.append(message)
    method = message.get("method")
    params = message.get("params", {})
    if method == "Network.requestWillBeSent":
      request_id = params.get("requestId")
      url = params.get("request", {}).get("url")
      if request_id and url:
        self.requests[str(request_id)] = str(url)
    elif method == "Network.loadingFailed":
      request_id = str(params.get("requestId", ""))
      self.failures.append({
        "url": self.requests.get(request_id, ""),
        "errorText": params.get("errorText", ""),
        "blockedReason": params.get("blockedReason", ""),
        "type": params.get("type", ""),
      })

  def call(self, method: str, params: dict[str, Any] | None = None, timeout: float = 30) -> dict[str, Any]:
    message_id = self.next_id
    self.next_id += 1
    self._send_frame(json.dumps({"id": message_id, "method": method, "params": params or {}}))
    deadline = time.time() + timeout
    old_timeout = self.sock.gettimeout()
    self.sock.settimeout(max(0.1, min(1.0, timeout)))
    try:
      while time.time() < deadline:
        try:
          message = json.loads(self._recv_frame())
        except socket.timeout:
          continue
        if "id" in message and message["id"] == message_id:
          if "error" in message:
            raise RuntimeError(f"{method} failed: {message['error']}")
          return message
        if "method" in message:
          self._record_event(message)
    finally:
      self.sock.settimeout(old_timeout)
    raise TimeoutError(f"timed out waiting for {method}")

  def pump_for(self, seconds: float) -> None:
    deadline = time.time() + seconds
    old_timeout = self.sock.gettimeout()
    self.sock.settimeout(0.2)
    try:
      while time.time() < deadline:
        try:
          message = json.loads(self._recv_frame())
          if "method" in message:
            self._record_event(message)
        except socket.timeout:
          continue
    finally:
      self.sock.settimeout(old_timeout)


def chrome_probe(width: int, height: int) -> dict[str, Any]:
  label = f"{width}x{height}"
  out_dir = ARTIFACT_DIR / "chrome" / label
  clean_dir(out_dir)
  profile = ARTIFACT_DIR / "profiles" / f"chrome_{label}"
  clean_dir(profile)

  port = free_port()
  log_path = out_dir / "chrome.log"
  command = [
    CHROME_BIN,
    "--headless=new",
    f"--remote-debugging-port={port}",
    "--remote-allow-origins=*",
    f"--user-data-dir={profile}",
    f"--window-size={width},{height}",
    "--no-first-run",
    "--no-default-browser-check",
    "--disable-background-networking",
    "about:blank",
  ]
  chrome = subprocess.Popen(command, stdout=log_path.open("w"), stderr=subprocess.STDOUT, text=True)
  cdp = None
  try:
    version = wait_for_http(f"http://127.0.0.1:{port}/json/version")
    page = request_json("PUT", f"http://127.0.0.1:{port}/json/new?{quote(URL, safe=':/?=&%')}")
    cdp = CDP(page["webSocketDebuggerUrl"])
    cdp.call("Page.enable")
    cdp.call("Runtime.enable")
    cdp.call("Network.enable")
    cdp.call("Emulation.setDeviceMetricsOverride", {
      "width": width,
      "height": height,
      "deviceScaleFactor": 1,
      "mobile": False,
    })
    cdp.call("Page.navigate", {"url": URL})
    cdp.pump_for(12)
    clicked = cdp.call("Runtime.evaluate", {
      "expression": CLICK_CONSENT_JS,
      "returnByValue": True,
      "awaitPromise": True,
    }).get("result", {}).get("result", {}).get("value")
    cdp.pump_for(12)
    state = cdp.call("Runtime.evaluate", {
      "expression": STATE_JS,
      "returnByValue": True,
      "awaitPromise": True,
    }).get("result", {}).get("result", {}).get("value")
    screenshot_result = cdp.call("Page.captureScreenshot", {
      "format": "png",
      "captureBeyondViewport": False,
    })
    screenshot = out_dir / f"screenshot_chrome_{label}.png"
    screenshot.write_bytes(base64.b64decode(screenshot_result["result"]["data"]))
    state_path = out_dir / f"state_chrome_{label}.json"
    state_path.write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    network_path = out_dir / f"network_chrome_{label}.json"
    network_path.write_text(json.dumps({
      "failures": cdp.failures,
      "failureCount": len(cdp.failures),
      "eventCount": len(cdp.events),
    }, indent=2, sort_keys=True), encoding="utf-8")
    return {
      "browser": "chrome",
      "viewport": label,
      "binary": CHROME_BIN,
      "version": run_version(CHROME_BIN),
      "reportedVersion": version,
      "clickedConsent": clicked,
      "screenshot": str(screenshot),
      "state": str(state_path),
      "network": str(network_path),
      "networkFailureCount": len(cdp.failures),
      "summary": summarize_state(state),
    }
  finally:
    if cdp:
      cdp.close()
    chrome.terminate()
    try:
      chrome.wait(timeout=5)
    except subprocess.TimeoutExpired:
      chrome.kill()


def summarize_state(state: dict[str, Any] | None) -> dict[str, Any]:
  if not isinstance(state, dict):
    return {"state": "missing"}
  map_candidates = [
    item for item in state.get("mapCandidates", [])
    if item.get("rect", {}).get("visible") and item.get("rect", {}).get("width", 0) >= 200
  ]
  return {
    "readyState": state.get("readyState"),
    "title": state.get("title"),
    "hasRouteDistance": state.get("hasRouteDistance"),
    "hasDirections": state.get("hasDirections"),
    "hasConsentText": state.get("hasConsentText"),
    "visibleImageCount": state.get("visibleImageCount"),
    "canvasCount": state.get("canvasCount"),
    "svgCount": state.get("svgCount"),
    "largeMapCandidateCount": len(map_candidates),
    "largeMapCandidates": map_candidates[:8],
  }


def download_bugzilla_attachment() -> str | None:
  target = ARTIFACT_DIR / "bugzilla_attachment_9588885.png"
  if target.exists() and target.stat().st_size > 0:
    return str(target)
  request = urllib.request.Request(
    "https://bugzilla.mozilla.org/attachment.cgi?id=9588885",
    headers={"User-Agent": "bugzilla-firefox-diagnose/1.0"},
  )
  try:
    with urllib.request.urlopen(request, timeout=30) as response:
      target.write_bytes(response.read())
    return str(target)
  except (urllib.error.URLError, TimeoutError, OSError) as error:
    return f"download failed: {error}"


def main() -> None:
  ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
  results: dict[str, Any] = {
    "url": URL,
    "bugzillaAttachment": download_bugzilla_attachment(),
    "firefoxVersion": run_version(FIREFOX_BIN),
    "chromeVersion": run_version(CHROME_BIN),
    "runs": [],
  }
  for width, height in VIEWPORTS:
    results["runs"].append(firefox_probe(width, height))
    results["runs"].append(chrome_probe(width, height))
  output = ARTIFACT_DIR / "probe_results.json"
  output.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
  print(json.dumps(results, indent=2, sort_keys=True))


if __name__ == "__main__":
  main()
