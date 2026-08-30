# ADR 0002: Separate Protected Authority, ROOK LINK Transport, and PULSE Wake Delivery

- **Status:** Proposed
- **Date:** 2026-08-29
- **Owners:** Repository owner and host-orchestration maintainer
- **Decision scope:** VISION-64 host tooling, ROOK LINK request/result transport, PULSE local wake delivery, GitHub-backed operational messaging
- **Related task(s):** `docs/tasks/4-rook-link-v1-orchestration.md` revision 2; planned `docs/tasks/6-pulse-lite-micro-loop.md` revision 2
- **Related invariants:** `V64-GOV-001`, `V64-GOV-002`, `V64-GOV-003`, `V64-GOV-004`, `V64-GOV-005`, `V64-GOV-006`, `V64-BLD-001`, `V64-BND-001`, `V64-DEP-001`, `V64-DEP-002`, `V64-FAIL-001`
- **Supersedes:** None
- **Superseded by:** None
- **Approval authority:** Independent maintainer/CODEOWNER role; no self-approval
- **Approval evidence:** `pending`

## Decision summary

VISION-64 keeps protected repository authority, FORGE lifecycle control, ROOK LINK operational transport, and PULSE local wake delivery as separate layers. Only an exact task or ADR blob reachable through remotely verified protected `main` grants repository scope. ROOK LINK envelopes describe validated operational requests and results but are not authority by themselves. PULSE may deliver a bounded pointer to one user-selected ChatGPT conversation, but it cannot create objectives, interpret remote prose as commands, or bypass user input. This ADR authorizes no kernel work, live consumer adoption, automated agent execution, or MENAGERIE implementation.

## Context and problem

The pre-constitution ROOK LINK and PULSE stack was developed on branches descended from `e0f7dc7741af760199003499ec060659b76fb296`. The audited constitution and fail-closed factory foundation is now merged into protected `main` at `77efee07a3601dcbbfa4b539f442046099656d57`.

The existing Task 4 and Task 6 branches contain useful, tested transport and host-tooling content, but their task blobs are not reachable from protected `main` and therefore are not present-day authority. The repository currently has no real ADRs. A clean carry-forward needs to preserve the proven wire contracts and tests while binding future use to the current constitution.

The current Gate F dispatcher deliberately rejects `execute`. A validated ROOK LINK request must not be mistaken for permission to launch an agent, mutate a repository, or alter the execution policy.

## Constraints and decision drivers

1. Protected authority and independent approval outrank branch status, issue prose, comments, labels, workflow output, or candidate commits.
2. Every non-GENESIS implementation must have an approved task with bounded scope, exact acceptance checks, and explicit exclusions.
3. A material trust boundary, persistence format, or cross-system contract requires an Accepted ADR.
4. GitHub issues, comments, webhooks, chat transcripts, logs, websites, and worker output are untrusted transport data.
5. ROOK LINK v0 compatibility must remain intact.
6. ROOK LINK v1 capability names and result identity rules must not be redesigned during carry-forward.
7. A capability named in a ROOK LINK envelope is not an authenticated grant; current execution policy remains a separate prerequisite.
8. PULSE must remain explicit, finite, user-preemptible, exact-conversation, pointer-only, and fail-closed.
9. No repository or runner secret may be stored, printed, or inferred.
10. No target OS, kernel, unsafe, privileged, or ABI work is in scope.
11. Reuse of proven source blobs is preferred over speculative redesign, but historical task blobs must not become accidental authority.

## Options considered

### Option A — Merge the historical branches directly

- **Description:** Merge Task 4 or Task 6 directly into current `main`.
- **Benefits:** Minimal Git operations and preserved commit history.
- **Costs and risks:** Historical task blobs could appear to be authoritative; live webhook/bootstrap artifacts could be imported accidentally; the old constitution assumptions would be mixed with the current one.
- **Invariant impact:** Conflicts with `V64-GOV-005` and current FORGE authority binding.
- **Evidence available or required:** Existing branch checks only; insufficient for present-day authority.

### Option B — Rewrite ROOK LINK and PULSE from scratch

- **Description:** Reimplement the contracts and host tooling against current `main`.
- **Benefits:** Clean history and direct constitution alignment.
- **Costs and risks:** Unnecessary churn, loss of proven behavior, and increased regression surface.
- **Invariant impact:** Compatible in principle, but violates smallest-change and reversible-increment principles.
- **Evidence available or required:** New full implementation and review evidence.

### Option C — Port exact contract content under a new protected authority layer

- **Description:** Approve the boundary decision and a revised Task 4 specification through protected `main`; port only explicitly allowed ROOK LINK contract files from the exact historical source; preserve code/schema/example blobs where possible; reconcile documentation and contract-only CI; defer PULSE implementation to its own approved task.
- **Benefits:** Preserves proven behavior, prevents stale task blobs from becoming authority, keeps live execution disabled, and creates a reviewable current-baseline candidate.
- **Costs and risks:** New candidate SHAs and a second verification pass are required.
- **Invariant impact:** Preserves the governing invariants and strengthens fail-closed boundaries.
- **Evidence available or required:** Source-blob mapping, current-constitution checks, validator suite, workflow lint, independent review, and protected evidence anchoring.

### Option D — Defer adoption

- **Description:** Leave the historical branches untouched until a later design.
- **Benefits:** No immediate risk.
- **Costs and risks:** PULSE and future MENAGERIE work remain blocked on an uncanonical dependency.
- **Invariant impact:** Safe but does not meet the recovery objective.
- **Evidence available or required:** No implementation evidence.

## Decision

Select Option C.

### Protected authority

- The exact ADR and task blobs become authoritative only after independent approval and merge through remotely verified protected `main`.
- The immutable authority tuple is the protected ref, authority commit, artifact path, and blob ID.
- A historical source SHA is provenance only. It does not approve itself, establish the implementation baseline, or authorize execution.
- Any semantic amendment creates a new revision and invalidates affected evidence.

### ROOK LINK

- ROOK LINK remains the GitHub-mediated request/result transport between a frontier coordinator and Rook.
- `rook-link.request.v1` / `rook-link.result.v1` remain the read-only, non-mutating, non-delegating v0 wire pair.
- `rook-link.request.v2` / `rook-link.result.v2` remain the capability-scoped v1 wire pair.
- The closed-world validator remains the gate for envelope shape, identity, immutable pointers, capabilities, branch names, delegation bounds, and hard limits.
- A validated ROOK LINK envelope is transport data, not sufficient execution authority.
- Protected task authority, current execution policy, and any required authorization digest are separate prerequisites.
- Under the current Gate F policy, `execute` remains unavailable to the repository dispatcher and adapters.
- Issue bodies, issue comments, webhook payloads, result-bus comments, and objective prose cannot expand a request.

### PULSE

- PULSE remains a local, bounded wake-delivery mechanism, not an agent framework or architectural authority.
- It may wake only one explicitly selected user-authored conversation.
- It may inject only a deterministic pointer containing local session metadata and an immutable ROOK LINK result locator.
- It must preserve composer text, stop when the user is active, stop when the page is ambiguous, and consume budget only after a successful submission.
- PULSE must not interpret result prose, issue prose, logs, or worker output as commands.
- PULSE implementation and adoption require a later approved Task 6 revision and its own verification.

### Separation from FORGE and future MENAGERIE

- FORGE remains the authority, lifecycle, review, verification, proof, and synthesis process.
- ROOK LINK does not bypass FORGE.
- PULSE does not bypass FORGE.
- MENAGERIE, when proposed, must be a separate communication-plane decision and task. It cannot become a replacement for protected authority, FORGE, ROOK LINK validation, or user control.
- No Zoo personality, role assignment, or membership policy is selected here.

## Contract and boundary impact

| Category | Decision |
| --- | --- |
| Logical boundaries | Affects Host Tooling and Verification, Protection and External Interfaces, Diagnostics and Recovery, and Foundation Contracts. No target OS boundary changes. |
| Ownership | Protected repository owns authority; the frontier coordinator owns intent and acceptance; Rook owns only granted operational execution; PULSE owns local session/wake state. |
| Initialization | No consumer is active until configuration, identity, pointer, policy, and session validation complete. Partial validation leaves the operation inaccessible. |
| Persistence and transport | ROOK LINK **requests** are committed immutable commit/path-addressed objects. **Results** are structured objects returned through the configured GitHub result bus and validated against the exact immutable request identity. Neither transport surface is authority. PULSE runtime state remains local and credential-free. |
| Allocation/blocking | Host-side polling, browser connection, and GitHub reads may block and fail. No interrupt, panic, kernel, or target allocation behavior changes. |
| Concurrency | Rook must deduplicate request/result identities; PULSE supports one active session and one in-flight wake. Duplicate or edited transport records fail closed. |
| Errors | Malformed, ambiguous, stale, replayed, unauthorized, or policy-incompatible data is rejected or queued; it is never upgraded to authority. |
| Observability | Logs and evidence record IDs, pointers, statuses, hashes, and outcomes without secrets, cookies, tokens, or full remote prose. |
| Dependency direction | PULSE may depend on the ROOK LINK result-pointer contract; ROOK LINK does not depend on PULSE. Neither depends on kernel mechanisms. |
| External adoption | Live Rook/PULSE consumer changes remain separate, explicitly bootstrapped work. |

## Safety, security, and unsafe-code impact

No unsafe Rust, privileged operation, ABI, firmware, target-memory, or kernel boundary is introduced.

Threats addressed:

- prompt and shell injection through issue/comment prose;
- mutable or symbolic refs;
- request/result identity mismatch;
- replay and duplicate delivery;
- capability confusion;
- branch-protection bypass;
- accidental live webhook or bootstrap activation;
- user composer overwrite;
- credential or cookie exposure;
- treating a successful workflow as architectural authority.

Required controls:

- closed-world structured validation;
- immutable request commit/path pointers;
- exact source/candidate blob recording;
- protected authority verification;
- no secrets in repository artifacts or logs;
- no automatic dispatch enablement;
- user-priority and bounded-budget PULSE gates;
- independent verification and protected evidence anchoring.

## Verification and acceptance evidence

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| Protected authority is real | Remote branch-protection response and independent approval record | Required protection and one independent approval are verified against the exact authority commit |
| Historical content is not authority | Source/candidate blob map and revised task authority tuple | Only the protected task/ADR blobs govern the candidate |
| ROOK LINK compatibility is preserved | Existing v0/v1 examples, schemas, validator, and negative suite | All canonical positives pass and all fail-closed negatives remain rejected |
| Capability names are not upgraded into authority | Boundary documentation and static policy review | Docs explicitly require protected task/policy prerequisites |
| Gate F remains closed | Workflow and dispatcher inspection | No `execute` path, agent launch, live webhook, or bootstrap activation is introduced |
| PULSE remains a later dependent task | Task 4 scope and diff | No `tools/pulse-lite` file or PULSE implementation is changed |
| MENAGERIE remains separate | Scope review | No MENAGERIE schema, broker, storage, or routing implementation appears |
| No kernel work occurs | Candidate path and diff inspection | No target, kernel, unsafe, ABI, or privileged path changes |
| Evidence is independently anchored | Protected check or review containing candidate SHA and manifest digest | Candidate identity and evidence digest are recorded by an independent authority |

## Consequences

### Positive

- Proven ROOK LINK behavior can be retained without pretending its old branches are canonical.
- Current constitutional authority becomes explicit and auditable.
- PULSE remains bounded and user-controlled.
- Future MENAGERIE work has a clean dependency boundary.
- Live execution remains disabled until separately authorized.

### Negative and tradeoffs

- Historical checks must be rerun against a new protected-main candidate.
- Candidate commit IDs change even when file blobs are preserved.
- Task 4 and Task 6 require revised authority records.
- Live consumer adoption remains deferred.

### Follow-up work

1. Reserve ADR `0002` for this boundary proposal after the concurrent Sprint 0 GENESIS lane reserved ADR `0001`.
2. Approve and merge Task 4 revision 2 through protected `main`.
3. Port and independently verify the ROOK LINK contract.
4. Approve and merge a separate Task 6 revision 2 against canonical ROOK LINK.
5. Port and independently verify PULSE.
6. Draft and approve the separate MENAGERIE ADR and Task 7 specification.
7. Handle live Rook/PULSE adoption only through explicit later authority.

## Rollout, compatibility, and reversal

Rollout order is:

1. Protected ADR acceptance.
2. Protected Task 4 revision acceptance.
3. ROOK LINK content port and FORGE verification.
4. Protected ROOK LINK merge.
5. Task 6 revision acceptance.
6. PULSE content port and FORGE verification.
7. Protected PULSE merge.
8. Separate MENAGERIE GENESIS proposal.

The port must not merge the historical branch as a parent. It must select only task-authorized file content so obsolete task specs, live requests, webhook delivery, and bootstrap instructions do not become reachable authority artifacts.

Before live consumer adoption, reverting the contract candidate or disabling the external consumer must leave no target OS or protected-branch state dependent on the transport. Any change to this decision requires a new ADR revision; the original record remains immutable.

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)
- Planned ROOK LINK contract path: `docs/ROOK_LINK.md`
- [Task 4 revision 2](../tasks/4-rook-link-v1-orchestration.md)
- Planned Task 6 revision 2 path: `docs/tasks/6-pulse-lite-micro-loop.md`

## Decision log

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| 2026-08-29 | Proposed | Initial ADR `0002` GENESIS proposal; protected approval pending | |
