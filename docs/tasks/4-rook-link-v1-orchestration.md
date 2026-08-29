# Task 4 — ROOK LINK v1 capability orchestration

## Status

Approved for implementation on `task/4-rook-link-v1-orchestration`.

Base: `2fe9f1f0f848bb567922a9fea98fea3326be5a72` (`task/3-rook-link-result-return`).

Do not merge as part of this task.

## Goal

Promote ROOK LINK from the v0 proof-of-transport probe into a capability-scoped orchestration plane where a frontier coordinator may delegate meaningful operations work to Rook without pre-authoring every command.

The intended control model is:

`user -> frontier orchestrator -> immutable ROOK LINK request -> Rook -> tools/runner/Zoo -> structured evidence -> GitHub result bus -> frontier orchestrator`

Rook is an operations manager, not an architecture authority. The frontier orchestrator owns task intent, architectural judgment, acceptance, and follow-up decisions. Rook may choose operational implementation details inside the exact capabilities and bounds granted by the immutable request.

## Compatibility

ROOK LINK v0 remains supported unchanged:

- request schema `rook-link.request.v1`;
- result schema `rook-link.result.v1`;
- operation `probe.environment.v1`;
- read-only/non-delegating semantics.

ROOK LINK v1 adds new wire schemas named `rook-link.request.v2` and `rook-link.result.v2`. The schema version increments because v0 already consumed the `v1` wire identifiers.

## v1 authority model

The only execution authority is an immutable request object committed under `ops/rook/requests/` and identified by a full request commit plus canonical request path.

Issue bodies, issue comments, webhook payload prose, PR text, chat messages, logs, websites, compiler output, repository content outside the committed request, worker output, and result-bus comments are data only. They do not expand authority.

A v1 request authorizes exactly one high-level operation: `orchestrate.task.v1`.

The request provides:

- a natural-language objective and explicit success criteria;
- a finite capability set;
- an autonomous execution budget;
- an exact optional work branch and optional computer roots;
- mandatory hard limits;
- evidence-return requirements.

Rook may select commands, ordering, retries, process layout, tmux organization, QEMU invocations, runner usage, and bounded Zoo delegation only when those actions fit the granted capabilities.

## Capability registry

Initial v1 capabilities:

- `repo.read` — inspect repository files/history/state.
- `repo.task-write` — modify files only for the active task/work branch.
- `git.task-branch` — create/switch/commit/push non-protected task refs; never force-push.
- `process.user` — start/stop/inspect user-owned task processes.
- `tmux.manage` — create/inspect/stop task tmux sessions.
- `runner.inspect` — inspect runner state, labels, jobs, and logs.
- `runner.execute` — dispatch or execute bounded task jobs on approved runners.
- `runner.manage` — restart or repair the user-owned VISION runner process/config without changing repository trust policy.
- `qemu.execute` — run QEMU/OVMF test and repro workloads.
- `artifact.collect` — collect logs, reports, diffs, test outputs, and hashes.
- `tooling.install` — install development tooling needed for the task, including package-manager use when otherwise permitted.
- `network.outbound` — make outbound network requests needed for task execution; never publish secrets.
- `worker.delegate` — delegate bounded repetitive/subtask work to Zoo workers while Rook remains accountable.
- `github.issue.write` — create/comment/update task-related GitHub issues, excluding result-bus authority changes.
- `github.pr.write` — open/update draft task PRs and comments; never merge protected branches.
- `computer.read` — inspect explicitly scoped local-computer roots/resources.
- `computer.task-write` — modify explicitly scoped local-computer roots/resources for the task.

Capabilities are additive but never implicit. A capability not listed in the immutable request is denied.

## Mandatory hard limits

Every v1 request carries the same non-disableable hard limits. They are encoded as literal `false` values so a request attempting to flip one fails validation.

Rook may not:

- merge protected branches;
- force-push;
- rewrite Git history;
- read credential/secret stores merely because machine access exists;
- exfiltrate or publish secrets;
- disable security controls to make a task easier;
- perform destructive host operations unrelated to the task;
- modify the ROOK LINK trust root, validator, pinned authority, webhook secret configuration, or its own authorization rules as part of an ordinary v1 task.

These are control-plane invariants, not a tiny opcode allowlist. Inside them, the frontier orchestrator may grant broad operational capability.

## Delegation

Zoo delegation requires `worker.delegate` and `execution.max_workers > 0`.

Rook must assign bounded subproblems, retain responsibility for evidence, and report each worker used. Zoo workers remain prohibited from silently inventing architecture, memory-model, scheduler/SMP, syscall/ABI, unsafe-kernel, interrupt-entry, page-table, context-switch, or locking decisions. If such judgment is encountered, Rook returns it to the frontier orchestrator.

## Result contract

A `rook-link.result.v2` object must bind:

- request identity;
- request commit and path;
- base commit;
- operation;
- capabilities actually used;
- timestamps and terminal status;
- concise action evidence;
- artifact locators/hashes;
- Git/task-branch state;
- delegation report.

Capabilities used in the result must be a subset of the request capabilities. Delegation must stay within the worker budget. Returned branch identity must match the request's work branch when one is specified.

The existing GitHub issue `#3` remains transport-only. Rook posts exactly one raw result JSON object per request. Result comments are never execution authority.

## Validator requirements

The validator must:

1. continue accepting the proven v0 request/result examples;
2. accept canonical v1/v2 examples;
3. reject unknown capabilities and duplicate capabilities;
4. reject symbolic commits;
5. reject protected work branches;
6. reject write branches without write/git capability;
7. reject computer capabilities without explicit computer roots;
8. reject delegation without `worker.delegate` or beyond the worker budget;
9. reject any hard-limit relaxation;
10. reject unknown command/shell fields at the request top level;
11. reject result capabilities not granted by the request;
12. reject request/result identity and pointer mismatches;
13. reject path traversal;
14. remain closed-world on every structured object.

## CI

ROOK LINK contract CI remains GitHub-hosted only and read-only. It validates both wire generations plus the fail-closed suite. No self-hosted runner is used to validate the control-plane contract.

## Explicitly out of scope

This task does not:

- merge Task 1, 2, 3, or 4;
- grant Rook protected-branch merge authority;
- grant force-push/history-rewrite authority;
- grant secret-store browsing/exfiltration authority;
- grant architecture authority to Rook or Zoo;
- automatically modify the live Rook skill/routine. Live consumer adoption occurs only after this branch passes review/CI and is explicitly bootstrapped to the new pinned contract.
