# PULSE Lite

PULSE Lite is a deliberately small local helper for **bounded ChatGPT micro-loops**. It watches the canonical VISION-64 ROOK LINK result bus, identifies results that belong to one user-started micro-loop session, and wakes one exact user-selected ChatGPT conversation with a deterministic pointer-only prompt.

It is not an autonomous agent framework and does not use the OpenAI API or ChatGPT Work/Codex.

## Safety model

- The user starts the main task and explicitly starts the local PULSE session.
- PULSE only reacts to request IDs under the exact configured prefix.
- Remote result prose is never injected into ChatGPT.
- The wake prompt contains only local session metadata and a canonical GitHub pointer.
- The automatic wake budget is 1-3 turns; default 2.
- Existing user text in the composer always wins. PULSE never clears it.
- A busy/generating page blocks normal injection.
- Any uncertainty in ChatGPT UI detection fails closed.
- GitHub and ChatGPT credentials are not stored by PULSE.

## Frozen-turn recovery

PULSE also includes an **opt-in stuck-turn watchdog** for both sides of the tiny loop.

### ChatGPT-side recovery

When enabled, the browser adapter samples a small set of local UI liveness signals while ChatGPT appears to be generating. If the page remains in the same generating state for longer than the configured threshold and there has been no observed progress, PULSE marks the turn `suspected_stuck`.

Recovery is conservative and idempotency-aware:

1. do not click arbitrary UI;
2. do not submit a second task instruction immediately;
3. first reload the exact configured ChatGPT conversation URL and wait for the server-side conversation state to settle;
4. if the prior turn appears completed after reload, resume normally;
5. if the page remains idle but the expected continuation was never surfaced, PULSE may submit one deterministic recovery prompt **only if a recovery budget remains**;
6. that prompt tells ChatGPT to re-read canonical GitHub state and verify prior side effects before doing anything else;
7. if UI state is still ambiguous, stop automation and return control to the user.

The watchdog never attempts login/MFA/CAPTCHA recovery and never navigates outside `chatgpt.com`.

### Rook-side recovery

PULSE can also track a locally registered outstanding ROOK LINK request. If delivery was recorded but no matching result appears within the configured timeout, PULSE may request **one redelivery of the exact same immutable request pointer** through a user-configured local hook. It must not manufacture a new request ID or altered request body.

This depends on ROOK LINK replay/idempotency protections: duplicate delivery of the same immutable request must not repeat already-completed side effects. If no redelivery hook is configured, PULSE only reports the stall.

A later version can wire the hook to the existing GitHub/ROOK LINK delivery path. v0 keeps the interface local and fakeable so the policy can be tested without secrets or network mutation.

## Installation

Python 3.11+ is recommended.

```powershell
cd tools/pulse-lite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
python -m playwright install chromium
```

PULSE uses the already-authenticated `gh` CLI for GitHub reads. Check it first:

```powershell
gh auth status
```

## Dedicated browser

Launch a dedicated Chrome or Edge profile with loopback remote debugging. Do not point PULSE at your normal browser profile.

Example Chrome launch on Windows:

```powershell
& "$env:ProgramFiles\Google\Chrome\Application\chrome.exe" `
  --remote-debugging-address=127.0.0.1 `
  --remote-debugging-port=9223 `
  --user-data-dir="$env:LOCALAPPDATA\VISION64\pulse-lite\chrome-profile" `
  "https://chatgpt.com/"
```

Sign in manually once, open the exact ChatGPT conversation you want PULSE to use, then copy that conversation URL.

## CLI examples

```powershell
pulse doctor --conversation-url "https://chatgpt.com/c/..." --cdp-url "http://127.0.0.1:9223"

pulse start `
  --conversation-url "https://chatgpt.com/c/..." `
  --request-prefix "pulse-bootdiag-a13f-" `
  --budget 2 `
  --cdp-url "http://127.0.0.1:9223"

pulse run
pulse status
pulse pause
pulse resume
pulse dry-run
pulse once
pulse stop
```

To opt into frozen-turn recovery:

```powershell
pulse start `
  --conversation-url "https://chatgpt.com/c/..." `
  --request-prefix "pulse-bootdiag-a13f-" `
  --budget 2 `
  --cdp-url "http://127.0.0.1:9223" `
  --stuck-recovery `
  --stuck-seconds 180 `
  --recovery-budget 1
```

The normal automatic-wake budget and the recovery budget are independent. A successful recovery prompt consumes the recovery budget, not a normal task wake.

## Tests

```powershell
python -m pytest
```

Tests use fakes and do not require a real ChatGPT account or browser session.
