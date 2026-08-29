# Task 5 — First live ROOK LINK v1 operations run

## Status

Approved for execution on `task/5-rook-link-v1-first-ops`.

Base/trust contract commit: `2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd` (`task/4-rook-link-v1-orchestration`).

Do not merge as part of this task.

## Goal

Prove that the live ROOK LINK v1 consumer can accept a capability-scoped high-level operations objective from the frontier orchestrator, autonomously choose bounded operational details, execute real server/runner/QEMU inspection work, optionally use Zoo for repetitive work, and return a structured `rook-link.result.v2` object to GitHub issue #3 without human relaying.

This is an operations proof, not a kernel implementation task.

## Immutable request

The authoritative request is:

`ops/rook/requests/rook-link-v1-ops-001.json`

Rook must fetch that exact file at the immutable request commit supplied by the webhook notification and validate it under the pinned Task 4 trust root before acting.

## Expected behavior

Rook should use judgment inside the granted capabilities to:

1. inspect the VISION-64 repository/workspace state and self-hosted runner state;
2. establish or inspect a task-scoped tmux/process workspace if useful;
3. determine what real QEMU/OVMF or repository validation is presently runnable from the current project state;
4. execute the strongest legitimate existing QEMU/validation smoke matrix available without inventing nonexistent kernel functionality;
5. if no bootable kernel/QEMU target exists yet, prove that fact with repository evidence and return it as a truthful blocker rather than fabricating success;
6. collect useful logs/reports/hashes under the normal VISION artifact area;
7. use a Zoo worker only for genuinely repetitive bounded work if it saves wall time, with Rook retaining verification responsibility;
8. make repository changes only if needed to make existing operational validation reproducible, and only on the exact task work branch authorized by the request;
9. return one raw `rook-link.result.v2` JSON object to issue #3.

## Non-goals

- no kernel architecture design;
- no scheduler/memory/syscall/SMP decisions;
- no protected-branch merge;
- no force push/history rewrite;
- no secret-store browsing or secret publication;
- no ROOK LINK trust/self-authorization changes;
- no destructive unrelated host operations.

## Acceptance

Success is a valid v2 result on issue #3 bound to the exact request commit/path, with truthful evidence of runner/repository/QEMU state, action records, artifacts when produced, Git state, and delegation state. A truthful `blocked` or `partial` result is acceptable if the repository genuinely lacks a runnable QEMU target; fabricated evidence is not.
