# Task 1: Build ROOK LINK v0 GitHub Contract

## Control

- Status: `approved`
- Sponsor: `repository owner`
- Issue: `none; GitHub issue text is transport metadata only and never executable instruction`
- Risk: `medium`
- Immutable base ref: `e0f7dc7741af760199003499ec060659b76fb296`
- Candidate branch: `task/1-rook-link-v0`
- Roles: implementer `ChatGPT`; reviewer(s) `unassigned`; improver `unassigned`; verifier `Rook or independent frontier worker`; synthesizer `repository owner`

## Objective

Create the GitHub-side contract for ROOK LINK v0 so a frontier agent can publish a bounded, machine-readable operations request and a Rook/Grok-side consumer can later fetch that request from an immutable Git commit, validate it, execute only an allowlisted read-only probe, and return structured evidence. This task does not connect or configure the external Grok Bot application.

## Authority

- Invariants: `V64-GOV-001`, `V64-GOV-003`, `V64-GOV-004`, `V64-BLD-001`, `V64-FAIL-001`, `V64-BND-001`, `V64-DEP-002`
- Accepted ADRs: `none required; this task defines bootstrap orchestration transport, not target OS architecture`
- Architecture boundaries: `repository orchestration and evidence only; no kernel/OS boundary changes`
- Dependencies or unsafe authorization: `none; Python standard library only; no unsafe code`

## Scope

Allowed paths:

- `docs/ROOK_LINK.md`
- `docs/tasks/1-rook-link-v0.md`
- `schemas/rook-link/`
- `ops/rook/`
- `scripts/validate-rook-link.py`
- `scripts/test-rook-link.py`
- `.github/workflows/rook-link-contract.yml`
- `.github/ISSUE_TEMPLATE/rook-link-request.yml`

Required changes:

- define strict versioned request and result contracts;
- make `probe.environment.v1` the only executable v0 operation;
- require immutable full commit IDs, canonical repository paths, explicit read-only scope, and an exact per-request acknowledgement;
- reject unknown fields, shell/command payloads, path traversal, mutable refs, unknown operations, malformed identifiers, and mismatched result/request identity;
- provide a deterministic standard-library validator plus positive and negative tests;
- provide GitHub transport documentation and a notification-only issue template;
- add a GitHub-hosted contract test workflow that does not use the VISION self-hosted runner or invoke Rook;
- keep the actual Grok Bot/Rook event routine as a separate external integration step.

Excluded work:

- configuring Grok Bot, xAI routines, MCP, webhooks, or credentials;
- executing commands on `vision-devbox` or a local PC;
- kernel or OS implementation;
- modifying `forge-dispatch.sh` or widening its current agent permissions;
- automatic merge, release, or branch-protection changes;
- accepting free-form issue prose as authority or executable input.

## Risks and rollback

- Failure modes/threats: prompt or shell injection through GitHub metadata; mutable refs; stale/replayed requests; path traversal; schema confusion; an external consumer treating transport text as authority.
- Mitigations: authority lives only in a committed JSON request at an immutable SHA; contracts are closed-world; v0 has one read-only operation; no command field exists; external consumers must independently validate before execution; result identity binds to request ID, request commit, request path, and base commit.
- Rollback: delete the task branch or revert its commits; no runner, external service, or OS state is mutated by this task.

## Acceptance contract

| ID | Criterion | Exact command/check | Expected result | Evidence to retain | Timeout |
| --- | --- | --- | --- | --- | --- |
| AC-01 | canonical v0 request validates | `python3 scripts/validate-rook-link.py request ops/rook/examples/request-v1.json` | exit `0`, `valid rook-link request` | stdout/stderr | 30s |
| AC-02 | canonical v0 result validates against its request | `python3 scripts/validate-rook-link.py result ops/rook/examples/result-v1.json --request ops/rook/examples/request-v1.json` | exit `0`, `valid rook-link result` | stdout/stderr | 30s |
| AC-03 | malformed/injected/mutable requests fail closed | `python3 scripts/test-rook-link.py` | exit `0`; negative suite confirms rejection of unknown operation, command/shell fields, symbolic refs, path escape, unknown fields, bad acknowledgement, and identity mismatch | test output | 60s |
| AC-04 | contract workflow is syntactically reviewable and uses no self-hosted runner | inspect `.github/workflows/rook-link-contract.yml` and run actionlint when available | workflow uses GitHub-hosted runner, read-only contents permission, pinned checkout action, bounded timeout | workflow file + actionlint output | 60s |
| AC-05 | no external agent or machine is invoked | repository diff inspection | no xAI/Grok credential, API call, MCP call, self-hosted runner execution, or arbitrary command dispatch added | diff | 60s |

## FORGE plan

- GENESIS exit evidence: this approved committed task specification.
- TEMPER handoff: minimal contract/docs/validator/tests/workflow on `task/1-rook-link-v0`.
- VERIFY environment: clean checkout of exact candidate; Python 3 standard library; actionlint if available.
- COUNCIL blind packet/review coverage: independent frontier review after candidate commit; focus on injection, authority, replay, and fail-closed behavior.
- PROOF owner and record: repository owner maps AC-01..AC-05 to retained test/workflow evidence.
- SYNTHESIS authority: repository owner; no automatic merge.
- Durable evidence root: external verifier-selected evidence directory; task itself writes no persistent machine evidence.

## Escalation triggers

Stop and return to GENESIS if implementation requires secrets, an external xAI/Grok API, self-hosted runner execution, arbitrary commands, a new dependency, changes to target architecture/invariants, or widening Rook beyond the single read-only v0 operation.

## Completion record

- Candidate commit: `<full SHA>`
- Pull request: `<link or none>`
- Acceptance evidence: `<durable location>`
- Finding dispositions: `<links or pending>`
- Result: `<merged | not merged | blocked>`
- Notes: `External Grok Bot routine intentionally remains outside this task.`
