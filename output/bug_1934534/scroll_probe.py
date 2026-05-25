#!/usr/bin/env python3
from __future__ import annotations

import base64
import json
import os
import shutil
import socket
import struct
import subprocess
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parent
ARTIFACT_DIR = ROOT / "firefox"
CHROME_DIR = ROOT / "chrome"
URL = "https://zs.thnet.gov.cn/index"
FIREFOX_BIN = "/private/tmp/bug1934534_ff135_mnt/Firefox.app/Contents/MacOS/firefox"
CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
WIDTH = 1280
HEIGHT = 900
FIREFOX_OUTER_HEIGHT = 985


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method=method,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8") or "{}")


def wait_for_http(url: str, timeout: float = 15) -> dict[str, Any]:
    deadline = time.time() + timeout
    last_error: Exception | None = None
    while time.time() < deadline:
        try:
            return request_json("GET", url)
        except Exception as error:  # noqa: BLE001 - preserve the last startup error.
            last_error = error
            time.sleep(0.2)
    raise RuntimeError(f"timed out waiting for {url}: {last_error}")


def firefox_probe() -> dict[str, Any]:
    profile_root = CHROME_DIR / "profiles" / "firefox_webdriver_1280x900"
    if profile_root.exists():
        shutil.rmtree(profile_root)
    profile_root.mkdir(parents=True)

    log_path = ARTIFACT_DIR / "geckodriver_scroll_probe.log"
    gecko = subprocess.Popen(
        ["geckodriver", "--port", "4447"],
        stdout=log_path.open("w"),
        stderr=subprocess.STDOUT,
        text=True,
    )
    session_id = None
    try:
        wait_for_http("http://127.0.0.1:4447/status")
        payload = {
            "capabilities": {
                "alwaysMatch": {
                    "browserName": "firefox",
                    "acceptInsecureCerts": True,
                    "moz:firefoxOptions": {
                        "binary": FIREFOX_BIN,
                        "args": ["-headless"],
                        "prefs": {
                            "app.update.auto": False,
                            "app.update.enabled": False,
                            "browser.shell.checkDefaultBrowser": False,
                        },
                    },
                }
            }
        }
        session = request_json("POST", "http://127.0.0.1:4447/session", payload)
        session_id = session["value"]["sessionId"]
        base = f"http://127.0.0.1:4447/session/{session_id}"
        request_json("POST", f"{base}/window/rect", {"width": WIDTH, "height": FIREFOX_OUTER_HEIGHT})
        request_json("POST", f"{base}/url", {"url": URL})
        time.sleep(8)

        script = """
        const home = document.querySelector('#homePage');
        const frame = document.querySelector('#homePage .homePage');
        const container = document.querySelector('.homePage-body');
        return {
          href: location.href,
          title: document.title,
          scrollY: window.scrollY,
          docScrollTop: document.documentElement.scrollTop,
          bodyScrollTop: document.body ? document.body.scrollTop : null,
          bodyScrollHeight: document.body ? document.body.scrollHeight : null,
          innerHeight: window.innerHeight,
          homeOverflow: home ? getComputedStyle(home).overflow : null,
          frameOverflow: frame ? getComputedStyle(frame).overflow : null,
          containerInlineTransform: container ? container.style.transform : null,
          containerComputedTransform: container ? getComputedStyle(container).transform : null,
          activeText: document.body ? document.body.innerText.slice(0, 300) : '',
        };
        """
        before = request_json("POST", f"{base}/execute/sync", {"script": script, "args": []})["value"]
        png = request_json("GET", f"{base}/screenshot")["value"]
        (ARTIFACT_DIR / "screenshot_firefox135_webdriver_before_wheel.png").write_bytes(base64.b64decode(png))

        actions = {
            "actions": [
                {
                    "type": "wheel",
                    "id": "wheel",
                    "actions": [
                        {
                            "type": "scroll",
                            "x": WIDTH // 2,
                            "y": HEIGHT // 2,
                            "deltaX": 0,
                            "deltaY": 900,
                            "duration": 0,
                        }
                    ],
                }
            ]
        }
        action_error = None
        try:
            request_json("POST", f"{base}/actions", actions)
        except urllib.error.HTTPError as error:
            action_error = error.read().decode("utf-8", errors="replace")
            request_json(
                "POST",
                f"{base}/execute/sync",
                {
                    "script": "document.querySelector('.homePage-body')?.dispatchEvent(new WheelEvent('wheel',{deltaY:900,bubbles:true,cancelable:true}));",
                    "args": [],
                },
            )
        time.sleep(2)
        after = request_json("POST", f"{base}/execute/sync", {"script": script, "args": []})["value"]
        png = request_json("GET", f"{base}/screenshot")["value"]
        (ARTIFACT_DIR / "screenshot_firefox135_webdriver_after_wheel.png").write_bytes(base64.b64decode(png))
        return {
            "browser": "firefox",
            "binary": FIREFOX_BIN,
            "capabilities": session["value"].get("capabilities", {}),
            "before": before,
            "after": after,
            "action_error": action_error,
            "geckodriver_log": str(log_path),
        }
    finally:
        if session_id:
            try:
                request_json("DELETE", f"http://127.0.0.1:4447/session/{session_id}")
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
        self.sock = socket.create_connection((parsed.hostname, parsed.port), timeout=10)
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
            if opcode == 0x9:
                self._send_frame(payload.decode("utf-8", errors="ignore"))
                continue
            if opcode == 0x8:
                raise RuntimeError("websocket closed by peer")
            if opcode in (0x1, 0x0):
                return payload.decode("utf-8", errors="replace")

    def command(self, method: str, params: dict[str, Any] | None = None, timeout: float = 20) -> dict[str, Any]:
        message_id = self.next_id
        self.next_id += 1
        self._send_frame(json.dumps({"id": message_id, "method": method, "params": params or {}}))
        deadline = time.time() + timeout
        while time.time() < deadline:
            message = json.loads(self._recv_frame())
            if message.get("id") == message_id:
                if "error" in message:
                    raise RuntimeError(message["error"])
                return message.get("result", {})
        raise TimeoutError(method)


def chrome_probe() -> dict[str, Any]:
    profile = CHROME_DIR / "profiles" / "chrome_cdp_1280x900"
    if profile.exists():
        shutil.rmtree(profile)
    profile.mkdir(parents=True)
    CHROME_DIR.mkdir(parents=True, exist_ok=True)
    proc = subprocess.Popen(
        [
            CHROME_BIN,
            "--headless=new",
            "--no-first-run",
            "--disable-background-networking",
            "--remote-debugging-port=0",
            f"--user-data-dir={profile}",
            f"--window-size={WIDTH},{HEIGHT}",
            "about:blank",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    try:
        active_port = profile / "DevToolsActivePort"
        deadline = time.time() + 15
        while not active_port.exists() and time.time() < deadline:
            if proc.poll() is not None:
                raise RuntimeError(f"chrome exited early: {proc.stderr.read()}")
            time.sleep(0.2)
        lines = active_port.read_text().splitlines()
        port = int(lines[0])
        version = wait_for_http(f"http://127.0.0.1:{port}/json/version")
        tabs = wait_for_http(f"http://127.0.0.1:{port}/json/list")
        page = next(tab for tab in tabs if tab.get("type") == "page")
        cdp = CDP(page["webSocketDebuggerUrl"])
        try:
            cdp.command("Page.enable")
            cdp.command("Runtime.enable")
            cdp.command("Page.setViewport", {}) if False else None
            cdp.command("Emulation.setDeviceMetricsOverride", {"width": WIDTH, "height": HEIGHT, "deviceScaleFactor": 1, "mobile": False})
            cdp.command("Page.navigate", {"url": URL})
            time.sleep(8)
            expression = """
            (() => {
              const home = document.querySelector('#homePage');
              const frame = document.querySelector('#homePage .homePage');
              const container = document.querySelector('.homePage-body');
              return {
                href: location.href,
                title: document.title,
                scrollY: window.scrollY,
                docScrollTop: document.documentElement.scrollTop,
                bodyScrollTop: document.body ? document.body.scrollTop : null,
                bodyScrollHeight: document.body ? document.body.scrollHeight : null,
                innerHeight: window.innerHeight,
                homeOverflow: home ? getComputedStyle(home).overflow : null,
                frameOverflow: frame ? getComputedStyle(frame).overflow : null,
                containerInlineTransform: container ? container.style.transform : null,
                containerComputedTransform: container ? getComputedStyle(container).transform : null,
                activeText: document.body ? document.body.innerText.slice(0, 300) : ''
              };
            })()
            """
            before = cdp.command("Runtime.evaluate", {"expression": expression, "returnByValue": True})["result"]["value"]
            screenshot = cdp.command("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})["data"]
            (CHROME_DIR / "screenshot_chrome_1280x900_before_wheel.png").write_bytes(base64.b64decode(screenshot))
            cdp.command(
                "Input.dispatchMouseEvent",
                {"type": "mouseWheel", "x": WIDTH // 2, "y": HEIGHT // 2, "deltaX": 0, "deltaY": 900},
            )
            time.sleep(2)
            after = cdp.command("Runtime.evaluate", {"expression": expression, "returnByValue": True})["result"]["value"]
            screenshot = cdp.command("Page.captureScreenshot", {"format": "png", "captureBeyondViewport": False})["data"]
            (CHROME_DIR / "screenshot_chrome_1280x900_after_wheel.png").write_bytes(base64.b64decode(screenshot))
            return {
                "browser": "chrome",
                "binary": CHROME_BIN,
                "version": version,
                "before": before,
                "after": after,
            }
        finally:
            cdp.close()
    finally:
        proc.terminate()
        try:
            stdout, stderr = proc.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, stderr = proc.communicate()
        (CHROME_DIR / "chrome_cdp_stdout.txt").write_text(stdout)
        (CHROME_DIR / "chrome_cdp_stderr.txt").write_text(stderr)


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    CHROME_DIR.mkdir(parents=True, exist_ok=True)
    results = {
        "url": URL,
        "viewport": f"{WIDTH}x{HEIGHT}",
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "firefox": firefox_probe(),
        "chrome": chrome_probe(),
    }
    (ARTIFACT_DIR / "scroll_probe_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
