# Bug 1957422 Diagnosis

Generated: 2026-05-25T22:46:10+02:00
Bugzilla: https://bugzilla.mozilla.org/show_bug.cgi?id=1957422
Artifacts: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox

## Bug Metadata

- Summary: Lidl LiA Assistant - Support chat does not load completely, unable to send messages
- Product / Component: Web Compatibility / Site Reports
- Status: NEW
- Severity / Priority: S2 / P2
- Platform / OS: Unspecified / All

## Bugzilla Evidence

- Inferred Firefox versions: 136.0, 152.0a1
- Selected target URL: https://assistenza-clienti.lidl.it/SelfServiceIT/s/?initChatbot=true
- Target URL candidates:
- https://informace-pro-zakazniky.lidl.cz/SelfServiceCZ/s/?initChatbot=true (bug.url)
- https://assistenza-clienti.lidl.it/SelfServiceIT/s/?initChatbot=true (comment 17420934)
- https://github.com/webcompat/web-bugs/issues/150440 (comment 17420934)
- https://github.com/salesforce/near-membrane (comment 17458099)
- https://github.com/salesforce/near-membrane/blob/3b4fdf15ba636108be8fbba8c5f46d7f2973a1d0/packages/near-membrane-base/src/membrane.ts#L944 (comment 17458099)
- https://assistenza-clienti.lidl.it/SelfServiceIT/resource/1743369242000/CCC_VCA_4_10_3/chat-widget.min.js (comment 17458099)
- https://kundenservice.lidl.de/SelfServiceDE/s/ (comment 17477044)
- https://customer-service.lidl.co.uk (comment 17682559)
- https://informace-pro-zakazniky.lidl.cz (comment 17682559)
- https://kundenservice.lidl.de/SelfServiceDE (comment 17682559)
- https://apoio-ao-cliente.lidl.pt/SelfServicePT/s/?utm_source=chatgpt.com (comment 18083140)
- Attachment metadata count: 2

## Firefox Version Selection

- Requested major version: 136
- Allow version mismatch: False
- Selected Firefox: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox
- Selected Firefox version output: Mozilla Firefox 136.0
- Firefox archive download notes:
- Using cached Firefox archive install: /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox
- Candidate Firefox binaries:
- /Applications/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 151.0.1
- /Applications/Firefox Nightly.app/Contents/MacOS/firefox - Mozilla Firefox 153.0a1
- /Applications/Firefox Developer Edition.app/Contents/MacOS/firefox - Mozilla Firefox 152.0b1
- /private/var/folders/ms/_ys5hmhs7zzfhpwwzzs_h78m0000gn/T/bugzilla-firefox-diagnose-cache/136.0/app/Firefox.app/Contents/MacOS/firefox - Mozilla Firefox 136.0

## Browser Reproduction Evidence

- 1280x900: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox/screenshot_firefox_1280x900.png
- 1440x1000: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox/screenshot_firefox_1440x1000.png
- 390x844: exit 0 - /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox/screenshot_firefox_390x844.png

## Chrome Version Selection

- Selected Chrome: /Applications/Google Chrome.app/Contents/MacOS/Google Chrome
- Selected Chrome version output: Google Chrome 148.0.7778.179
- Chrome artifacts:
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_chrome/screenshot_chrome_1280x900.png
- /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_chrome/screenshot_chrome_390x844.png

## Controlled Browser Comparison

- Comment 0 steps: open the Lidl LiA Assistant URL, click CONTINUA inside the chat window, type a message, and try to send it.
- Firefox 136 evidence: the first-comment Italian URL loads with a cookie dialog; behind it, the chat entry point is only a floating chat bubble and the full chat panel is not visible.
- Chrome 148 evidence: the same URL loads with the cookie dialog, but the full "Assistente Virtuale Interattiva" chat panel is already visible behind it with a CONTINUA button.
- Classification: reproduced for the "chat window does not load completely" part; blocked/partial for the final send-message step because the consent dialog blocked interaction in both headless captures.

## Actual-vs-Expected Comparison

- Expected from comment 0: chat window loads completely and messages can be sent.
- Actual from comment 0: chat window does not load completely and messages cannot be sent.
- Observed: Firefox does not show the complete chat panel that Chrome shows under the same clean-profile URL load.

## Diagnosis

The load-completeness part of the bug reproduces. Chrome reaches the LiA chat panel; Firefox remains at a less complete chat state.

## Cause Analysis

Public Bugzilla analysis and the downloaded reduction point at the Salesforce/Lidl chat widget integration rather than the isolated Svelte widget itself. The reduction includes the Svelte-style `ChatWidget` code and the send button class toggle `I(C, "scw-active", t[13])`. Bugzilla comments report that the isolated widget can apply `scw-active`, but the live site does not do so in Firefox, likely because the Salesforce `near-membrane` sandbox/proxy layer or surrounding integration prevents the expected state mutation/event propagation from reaching the widget.

## Confidence

Medium-high for reproduction of incomplete chat loading; medium for cause because the exact live near-membrane failure was not instrumented in this run.

## Suggested Next Steps

- Reproduce with the consent dialog accepted and record DOM mutations under `#sit-chat-widget` in both browsers.
- Instrument input events and the `scw-active` class toggle on `.scw-btn-send`.
- Escalate to the Lidl/Salesforce widget owners with the reduction and evidence that the standalone widget behaves differently from the live near-membrane integration.

## Sources and Artifacts

- Bugzilla REST payload: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox/bugzilla_payload.json
- Screenshot/log artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox
- Chrome artifact directory: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_chrome
- Public reduction artifact: /Users/bchauvet/codex-webcompat-diagnosis/output/bug_1957422_firefox/reduction_9485774.html
