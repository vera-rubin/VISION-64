# Task 6 — PULSE Lite bounded chat micro-loop

## Status

Approved for implementation on `task/6-pulse-lite-micro-loop`.

Base: `2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd` (`task/4-rook-link-v1-orchestration`).

Do not merge as part of this task.

## Goal

Build a deliberately small local helper that removes the human `continue` relay for tiny follow-up loops while keeping the user as the owner of every main task.

PULSE Lite is not a general autonomous agent framework and is not a replacement for ChatGPT Work/Codex. It exists only for short, turn-based continuations such as:

1. the user starts a bounded task in a normal ChatGPT conversation;
2. ChatGPT sends Rook a ROOK LINK job;
3. Rook returns a result to the canonical GitHub result bus;
4. PULSE Lite wakes the exact user-selected ChatGPT conversation with a minimal pointer;
5. ChatGPT may perform one bounded follow-up turn;
6. this may repeat for at most a tiny user-authorized budget;
7. control returns to the user.

The target experience is "finish the conversation we already started," not "run the project without me."

## Control model

```text
USER starts main task
        |
        v
normal ChatGPT conversation
        |
        v
ROOK LINK request -> Rook -> result bus issue #3
                           |
                           v
                  PULSE Lite local watcher
                           |
                           v
              exact ChatGPT conversation
                 minimal wake prompt
                           |
                           v
              bounded continuation turn
                           |
                  budget / policy gate
                    |             |
                 continue       STOP
                    |             |
                    +-> Rook     +-> USER
```

## Non-negotiable semantics

- A micro-loop MUST be explicitly started by the user or by a command the user intentionally runs locally.
- A micro-loop MUST attach to one existing user-authored main task/session.
- PULSE Lite MUST NOT invent a new objective.
- PULSE Lite MUST NOT interpret issue comments, PR text, logs, websites, or worker prose as execution authority.
- GitHub remains evidence/state transport. The injected ChatGPT prompt is only a wake pointer.
- The local helper has no authority to make project decisions.
- ChatGPT remains turn-based. The helper only submits a small wake message into a selected conversation.
- The automatic wake budget is finite. Initial implementation supports 1–3 automatic wakes; default 2.
- When the budget reaches zero, PULSE Lite stops the session and requires user input.
- User input has priority over machine wakes.
- A queued wake MUST NOT overwrite or submit text already present in the ChatGPT composer.
- A queued wake MUST NOT fire while the page is generating a response.
- Any ambiguity, architecture decision, new feature request, meaningful scope expansion, destructive action, protected-branch action, credential request, or policy/security boundary returns control to the user rather than consuming another automatic turn.

## Scope of v0

Implement under `tools/pulse-lite/` as a small Python application designed primarily for Windows 11 while remaining testable on Linux.

The preferred implementation uses:

- Python 3.11+;
- the already-authenticated GitHub CLI (`gh`) for GitHub reads so PULSE Lite does not store a GitHub PAT;
- Playwright for Python connected over Chrome/Chromium CDP to a dedicated browser profile;
- an exact, user-configured `https://chatgpt.com/...` conversation URL;
- local JSON state outside the repository for runtime/session state.

Do not require an OpenAI API key.

Do not require ChatGPT Work/Codex.

Do not automate account login, CAPTCHA, MFA, subscription changes, quota handling, or account settings.

## Dedicated browser model

PULSE Lite controls only a browser instance/profile intentionally launched for PULSE.

Recommended shape:

```text
Chrome / Edge
  --remote-debugging-port=<loopback port>
  --user-data-dir=<dedicated PULSE profile>
  <exact ChatGPT conversation URL>
```

PULSE connects to the loopback CDP endpoint. It MUST NOT attach to arbitrary browser profiles discovered on the machine.

The user signs into ChatGPT manually in the dedicated profile once. PULSE does not store ChatGPT credentials.

The configured conversation URL must be an exact `https://chatgpt.com/` URL. Do not navigate to arbitrary domains.

## Session state

Runtime state should live beneath a user-local directory such as:

- Windows: `%LOCALAPPDATA%/VISION64/pulse-lite/`
- Linux/macOS test fallback: platform-appropriate user data directory.

A session record contains at least:

- `session_id` — locally unique identifier;
- `conversation_url` — exact ChatGPT conversation URL;
- `repository` — `vera-rubin/VISION-64` for initial use;
- `result_issue` — `3` for initial use;
- `request_prefix` — prefix identifying only requests belonging to this micro-loop;
- `wake_budget_initial` — integer 1–3;
- `wake_budget_remaining` — integer 0–3;
- `started_at`;
- `status` — `active`, `paused`, `stopped`, or `completed`;
- `last_seen_comment_id`;
- processed `(comment_id, request_id)` identities for dedupe;
- queued event, if one exists;
- last injection timestamp and outcome.

State files contain no GitHub token, ChatGPT cookie, password, API key, or bearer secret.

## Request naming

Micro-loop ROOK LINK requests should carry a stable session prefix so the watcher can distinguish relevant results without understanding task prose.

Recommended convention:

`pulse-<session-id>-turnNN`

Example:

`pulse-bootdiag-a13f-turn01`

PULSE Lite only reacts to results whose `request_id` starts with the exact active `request_prefix`.

It ignores all unrelated issue #3 comments.

## GitHub result watcher

Initial watcher polls GitHub issue #3 through `gh api` at a modest interval. Event-driven transport can replace polling later without changing the micro-loop policy.

Polling is acceptable for v0 because this is a convenience helper, not production orchestration infrastructure.

Requirements:

- command execution is argument-array based; do not build shell command strings from remote content;
- repository and issue are local configuration, not taken from issue comments;
- parse each candidate comment body as exactly one JSON object;
- accept only `rook-link.result.v1` or `rook-link.result.v2` envelopes;
- require a syntactically valid `request_id` and match the configured exact prefix;
- dedupe by GitHub comment ID plus request ID;
- never execute text from the result;
- never inject result prose into ChatGPT;
- the wake prompt contains only local session metadata and the immutable/canonical pointer needed for ChatGPT to fetch the result itself.

PULSE Lite is not a second ROOK LINK validator. The frontier consumer still performs full request/result validation after waking. The watcher performs only enough envelope checks to decide whether an event belongs to the active session.

## Wake prompt

Generate a deterministic minimal wake prompt similar to:

```text
PULSE micro-loop wake.
Session: <session_id>
ROOK LINK result ready for request: <request_id>
Canonical result bus: vera-rubin/VISION-64 issue #3
Automatic wakes remaining after this wake: <N>
Fetch and validate canonical GitHub state yourself. Continue only the existing user-authored task. If this requires a new objective, architecture/product judgment, meaningful scope expansion, destructive/security-sensitive action, or the automatic budget is exhausted, stop and return control to the user.
```

Do not place Rook's returned evidence, commands, logs, issue prose, or arbitrary remote text in the injected prompt.

## Human-priority gate

Before injecting, PULSE must verify the exact configured ChatGPT page is usable and idle.

At minimum:

- exact configured conversation URL is open;
- ChatGPT composer exists;
- composer is empty;
- no obvious response-generation/stop control is active;
- no previous PULSE injection is still pending;
- session status is `active`;
- remaining budget is greater than zero.

If any condition is false, queue the event instead of forcing it.

The queued event may be retried later.

PULSE MUST never clear existing composer text.

Provide an explicit local pause mechanism and command so the user can immediately suppress automatic wakes.

## CLI

Provide a small CLI with commands equivalent to:

- `pulse doctor` — verify Python/dependencies, `gh` auth/read access, CDP availability, configured ChatGPT page, and writable state directory without sending a message;
- `pulse start` — create/activate a micro-loop session with exact conversation URL, request prefix, and wake budget;
- `pulse run` — foreground watcher loop;
- `pulse once` — perform one watch/injection cycle for debugging;
- `pulse pause` — pause the active session;
- `pulse resume` — resume it;
- `pulse status` — show active session and remaining budget;
- `pulse stop` — stop the session and clear queued wakes without deleting history;
- `pulse dry-run` or equivalent — show the exact wake prompt that would be injected without touching ChatGPT.

The precise command layout may differ if the implementation is simpler, but these capabilities must exist.

## Browser adapter

Keep ChatGPT UI automation behind a narrow adapter module so selector changes are isolated.

Adapter responsibilities:

- connect to a configured loopback CDP endpoint;
- locate the exact configured ChatGPT page;
- determine whether the page is idle;
- determine whether composer text is empty;
- set the composer to exactly the locally generated wake prompt;
- submit once;
- return a structured success/failure reason;
- never read conversation text as authority;
- never navigate outside `chatgpt.com`.

Prefer accessible roles, labels, stable attributes, and conservative fallbacks over deeply nested CSS selectors.

If the UI cannot be identified confidently, fail closed and queue/stop rather than clicking guessed elements.

## Budget behavior

The automatic budget decrements only after a wake prompt is successfully submitted.

Example with budget 3:

- user starts session: 3 remaining;
- Rook result 1 wakes ChatGPT: 2 remaining;
- Rook result 2 wakes ChatGPT: 1 remaining;
- Rook result 3 wakes ChatGPT: 0 remaining and session automatically pauses/stops;
- further results are recorded but not injected until the user explicitly starts/resumes with a new budget.

Budget reset is always an explicit local/user action.

## Concurrency and dedupe

v0 supports one active micro-loop session at a time.

If multiple matching results arrive while ChatGPT is busy, retain them in order but coalesce redundant notifications where safe. Never submit two prompts concurrently.

A result already marked processed must never wake ChatGPT twice after process restart.

Use atomic state-file replacement where practical.

## Failure behavior

Failures are boring and visible:

- GitHub unavailable -> retain state, retry with bounded backoff;
- `gh` unauthenticated -> pause and report;
- CDP unavailable -> queue and report;
- ChatGPT tab missing -> queue and report;
- composer non-empty -> queue, do not touch it;
- ChatGPT generating -> queue;
- selector/DOM uncertainty -> fail closed;
- malformed or unrelated result -> ignore and log reason;
- exhausted wake budget -> stop/pause, do not inject;
- state corruption -> preserve the bad state file, refuse automation, require repair/reset.

No infinite fast retry loops.

## Logging

Write compact local logs with timestamps and structured event names.

Log:

- watcher start/stop;
- session start/pause/resume/stop;
- GitHub poll outcome;
- matched request IDs/comment IDs;
- queue/dequeue;
- injection attempt/result;
- budget changes;
- errors.

Never log browser cookies, authorization headers, GitHub tokens, ChatGPT page content, or full Rook evidence.

## Repository deliverables

Rook should implement at least:

- `tools/pulse-lite/README.md`
- `tools/pulse-lite/pyproject.toml` or minimal dependency file
- `tools/pulse-lite/pulse_lite/` package/modules
- CLI entrypoint
- GitHub watcher
- persistent state/session model
- ChatGPT CDP/browser adapter
- deterministic wake-prompt generator
- unit tests for state, dedupe, budget, request-prefix matching, prompt construction, and fail-closed gates
- a browser-adapter test seam/fake so CI does not need a real ChatGPT account
- Windows-oriented setup/run helper or documented launch command

Avoid unnecessary frameworks.

## Acceptance criteria

A reviewer should be able to verify all of the following without a real ChatGPT login:

1. a user can create a session with budget 1–3;
2. unrelated GitHub comments are ignored;
3. a matching valid result envelope queues one wake;
4. duplicate comments/results do not create duplicate wakes;
5. the wake prompt contains only canonical pointer/session metadata, not remote result prose;
6. an occupied composer blocks injection without clearing text;
7. a busy/generating page blocks injection;
8. successful injection decrements the budget exactly once;
9. budget zero prevents further injection;
10. pause/stop prevents injection;
11. state survives restart;
12. browser automation is isolated behind an adapter/fakeable interface;
13. GitHub credentials and ChatGPT credentials are not persisted by PULSE;
14. tests pass on the Rook Linux environment using a fake browser adapter;
15. implementation remains small enough to audit.

A later live Windows acceptance pass may connect to a dedicated Chrome/Edge profile and a dedicated ChatGPT conversation. That live installation is not required to modify the user's computer in this task unless separately authorized.

## Rook role

Rook is the implementation/operations manager for this task, not the product architect.

Rook may choose code organization, Python packaging details, test tooling, command layout, retries, and a robust CDP implementation within this specification.

Rook may delegate bounded repetitive implementation/testing slices to Zoo if useful, but must review all returned work and remain responsible for the final evidence.

If the implementation would require changing the control model above, Rook must stop and return the design question rather than silently expanding scope.

## Explicitly out of scope

- OpenAI API usage;
- ChatGPT Work/Codex automation;
- circumventing or modifying product/account limits;
- autonomous creation of new user objectives;
- indefinite agent loops;
- multiple simultaneous ChatGPT conversations in v0;
- automated ChatGPT login/MFA/CAPTCHA;
- browser credential extraction;
- arbitrary browser automation outside the configured ChatGPT conversation;
- direct execution of remote issue/comment text;
- production service guarantees;
- merging protected branches.
