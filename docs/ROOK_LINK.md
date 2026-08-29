# ROOK LINK v0

ROOK LINK is a GitHub-mediated control plane between VISION-64 frontier agents and Rook, the bounded operations coordinator. GitHub is the durable message bus and audit ledger; it is not a shell transport.

## v0 boundary

ROOK LINK v0 intentionally supports exactly one operation: `probe.environment.v1`.

That operation is read-only and may collect only the requested subset of:

- hostname;
- UTC date/time;
- approved tool version strings (`git`, `rustc`, `cargo`, `qemu-system-x86_64`, `python3`).

It may not modify files, Git refs, processes, services, credentials, network configuration, runners, tmux sessions, or target OS state. It may not delegate to animal workers.

## Authority model

A GitHub issue, comment, title, label, notification, webhook body, chat transcript, or pasted command is **not authority**. Those surfaces may only notify Rook that a request exists.

The authoritative request is one JSON object committed in this repository under `ops/rook/requests/` and fetched at a full immutable commit ID. Before doing anything, the consumer must validate that object using the repository validator from the same trusted contract revision.

The request contains no command or shell field. v0 is a closed-world enum: if an operation, field, scope, probe, or acknowledgement is not explicitly valid, execution stops.

## Request lifecycle

1. A frontier coordinator creates a request JSON under `ops/rook/requests/<request-id>.json` on a reviewable branch.
2. The request is committed. Its Git commit SHA plus repository-relative request path become the immutable locator.
3. Optional GitHub issue/notification metadata points only to that SHA and path. The metadata itself is untrusted.
4. Rook fetches the exact commit and path, validates the JSON, and confirms that the request is still v0/read-only.
5. Rook performs only the allowlisted probe.
6. Rook emits a result JSON conforming to `rook-link.result.v1`. The result binds the request ID, request commit, request path, base commit, operation, status, timestamps, and evidence.
7. A frontier agent validates the result against the original request before using the evidence.

## Replay and mutation rules

- `base_commit` and `request_commit` must be full 40- or 64-hex commit IDs; symbolic refs such as `main`, `HEAD`, tags, or abbreviated SHAs are invalid.
- Request and result paths must be canonical repository-relative paths below their assigned roots and may not contain `.`/`..`, empty components, backslashes, NULs, or `.git` traversal.
- `request_id` is part of the acknowledgement and result identity. A reused ID must be treated as a replay/collision and rejected by the external consumer.
- A result is meaningful only for the exact request commit/path pair it names.

## External Rook integration

This repository side deliberately does not assume an xAI/Grok Bot API that has not been proven available. The external integration must do only this:

- receive a GitHub event or equivalent notification;
- extract an immutable request commit and canonical request path;
- fetch the exact repository object;
- run `python3 scripts/validate-rook-link.py request <file>` (or an independently equivalent validator);
- execute the single allowlisted read-only probe;
- return/store a `rook-link.result.v1` object;
- stop on any validation error or ambiguity.

If the Grok-side product cannot guarantee those properties, ROOK LINK remains transport-only and no automatic execution is enabled.

## Relationship to FORGE

ROOK LINK does not bypass FORGE. Rook remains an operations custodian, never architecture authority, reviewer, verifier of its own work, or merger. Future mutating operations require a separate approved task and an explicit extension of this contract; they are not implied by v0.
