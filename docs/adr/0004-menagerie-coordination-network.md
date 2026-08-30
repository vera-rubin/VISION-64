# ADR 0004: Define MENAGERIE as a Capability-Governed Coordination Network

- **Status:** Proposed
- **Date:** 2026-08-30
- **Owners:** VISION-64 repository owner and orchestration maintainer
- **Decision scope:** Host-side multi-agent coordination, participant identity and capability policy, transport-neutral durable message/thread contracts, shared skill references, and platform adapter boundaries
- **Related task(s):** `docs/tasks/2-establish-menagerie-contract-core.md`
- **Related invariants:** `V64-GOV-001`, `V64-GOV-002`, `V64-GOV-003`, `V64-GOV-004`, `V64-GOV-005`, `V64-GOV-006`, `V64-BLD-001`, `V64-INIT-001`, `V64-FAIL-001`, `V64-CON-001`, `V64-BND-001`, `V64-DEP-001`, `V64-DEP-002`
- **Supersedes:** None. Draft PR #11 was never protected authority and remains historical provenance only.
- **Superseded by:** None
- **Approval authority:** Independent VISION-64 maintainer/CODEOWNER; no self-approval
- **Approval evidence:** `pending` while Proposed

## Decision summary

VISION-64 will implement MENAGERIE as a model-neutral, transport-neutral, capability-governed coordination network. Participants retain separate identities, private/session memory, prompts, reasoning, and failure modes. They exchange only validated, explicitly addressed messages and exact pointers to protected authority, evidence, Git objects, and canonical repository-backed skills. A protected participant policy sets tier and capability ceilings independently of model self-claims. Work/Codex and other native tool surfaces participate directly through thin adapters. ROOK LINK remains a separate operational execution boundary, and PULSE is an optional later browser-conversation compatibility adapter rather than a MENAGERIE dependency. MENAGERIE messages coordinate work but never create architectural, execution, or repository authority.

## Context and problem

Protected `main` at `6821ac90c590ca25f7475b8b28b0b302b69a20a7` contains the independently approved Sprint 0 GENESIS record from PR #12, including ADRs 0001 through 0003 and Task 1. Those artifacts remain outside this decision.

Draft PR #11 attempted to reauthorize ROOK LINK and PULSE before MENAGERIE. It is invalid as a merge candidate because its proposed ADR number now collides with canonical ADR 0002 and because its rollout makes PULSE part of the MENAGERIE prerequisite path. PR #11 and historical PRs #1 through #9 remain useful provenance but are not current authority.

VISION-64 needs coordination among several model and tool surfaces without constructing one centralized agent, copying the full project context into every model, or treating conversation prose as authority. Main and subsystem Work/Codex surfaces already have native tool access, so ordinary MENAGERIE participation does not require browser wake automation. Historical ROOK LINK schemas, fixtures, validators, immutable request pointers, and result identity rules remain relevant to a later Rook adapter, but host execution remains separately governed and Gate F `execute` remains unavailable.

## Constraints and decision drivers

1. Protected repository authority, Accepted ADRs/tasks, FORGE evidence, and independent approval remain controlling.
2. MENAGERIE must preserve distinct model identities, private/session memory, independent reasoning, prompts, context, and failure modes.
3. Shared context must be explicit and bounded; no participant automatically receives the complete message history or skill library.
4. Participant tier and capabilities come from protected policy, never from model self-description or message prose.
5. Communication, workflow composition, delegation, wake delivery, and machine execution are separate capabilities.
6. Manager/director participants may coordinate complex workflows only within protected task authority, FORGE role rules, route policy, and finite budgets.
7. Worker/specialist participants default to narrow assigned operations and cannot promote themselves, create a project workflow, or recursively recruit agents.
8. Routing must wake only explicit, authorized recipients and must enforce group, fan-out, hop, expiry, and budget limits.
9. Issue, comment, chat, webhook, log, website, and worker prose is untrusted unless present inside a validated MENAGERIE envelope; envelope validation still does not create authority.
10. Canonical skills must be stored once in the protected repository and referenced by immutable Git identity.
11. Durable MENAGERIE state, shared skills, private/session memory, and protected repository authority must remain distinct.
12. MENAGERIE core must not depend on ROOK LINK or PULSE.
13. No kernel, target, unsafe, privileged, branch-protection, secret, live-agent, or repository-dispatch change is authorized here.

## Options considered

### Option A — One shared agent or automatically shared context

- **Description:** Treat all models as one logical consciousness and inject a common transcript, memory, and skill library into every turn.
- **Benefits:** Simple conversational illusion and low explicit routing overhead.
- **Costs and risks:** Homogenizes models, leaks irrelevant context, destroys independence, increases cost, creates hidden-memory assumptions, and weakens blind review.
- **Invariant impact:** Conflicts with bounded scope, independent verification, declared inputs, and explicit trust boundaries.
- **Evidence available or required:** No evidence can make implicit shared memory auditable.

### Option B — PULSE- or ROOK-centric orchestration chain

- **Description:** Require every participant message to flow through Rook and wake ordinary browser conversations through PULSE.
- **Benefits:** Reuses historical operational work.
- **Costs and risks:** Makes optional browser automation a critical dependency, centralizes routing in a worker, conflates communication with machine execution, and blocks native Work/Codex surfaces.
- **Invariant impact:** Creates unnecessary dependency and authority coupling.
- **Evidence available or required:** Historical PULSE and ROOK LINK tests prove bounded components, not this system-wide dependency.

### Option C — Capability-governed model-neutral network

- **Description:** Define a deterministic message, policy, routing, skill-reference, and adapter contract. Native participant surfaces communicate directly; optional adapters attach without changing the core.
- **Benefits:** Preserves model diversity, supports one-to-one, multicast, group, self, sequential, and bounded parallel workflows, and keeps authority explicit.
- **Costs and risks:** Requires a participant policy, closed-world validator, durable dedupe state, and more explicit context selection.
- **Invariant impact:** Preserves governing invariants when validation and authority binding fail closed.
- **Evidence available or required:** Contract schemas, policy fixtures, deterministic routing tests, negative escalation tests, skill-pointer checks, and independent review.

### Option D — Use FORGE itself as the chat network

- **Description:** Add conversation routing and memory semantics directly to FORGE.
- **Benefits:** One named orchestration system.
- **Costs and risks:** Collapses engineering lifecycle authority into communication transport and makes ordinary discussion look like stage progression or approval.
- **Invariant impact:** Weakens decision traceability and role separation.
- **Evidence available or required:** Rejected on boundary grounds.

## Decision

Select Option C.

### State-domain separation

MENAGERIE preserves four independent domains:

| Domain | Owns | Must not become |
| --- | --- | --- |
| Protected repository authority | Constitution, invariants, Accepted ADRs, approved tasks, participant policy, canonical skill artifacts, tests, and authority tuples | Conversation memory, model confidence, or a mutable message |
| Canonical shared skills and knowledge | Versioned reusable instructions/reference material stored once in the repository | A capability grant, task approval, hidden memory, or automatic full-context injection |
| Durable MENAGERIE conversation state | Validated messages, threads, receipts, checkpoints, statuses, reactions, and transport/evidence locators | Architectural authority, FORGE proof, or private model memory |
| Agent-private/session memory | One participant instance's private prompt, working context, and ephemeral reasoning state | Shared project truth or an input another participant may silently assume |

A future session reconstructs only explicit context selected from protected repository state, addressed MENAGERIE messages, evidence pointers, and exact skills. MENAGERIE never claims to persist hidden model memory.

### Participant identity and tiers

A protected, versioned participant policy binds stable participant IDs to a tier, adapter class, capability ceiling, allowed routes/groups, delegation ceiling, and finite budgets. A runtime adapter separately authenticates a platform principal and binds an ephemeral instance/session ID to the stable participant ID. Missing, ambiguous, stale, or mismatched bindings fail closed.

Initial manager/director participants are:

- `sol.gpt`;
- `opus`;
- `fable`.

They receive equivalent MENAGERIE orchestration ceilings. Equivalence permits the same classes of routing and workflow construction; it does not create shared memory, identical judgment, or a voting rule.

Initial worker/specialist participants or classes are:

- `rook.grok`;
- `gemini.antigravity`;
- `zoo.worker.*` without enumerating or assigning Zoo personalities.

Later participants are added by protected policy with identity, adapter, tier, capabilities, and route rules; the MENAGERIE protocol does not change.

### Capability authorization

The effective capability set is the intersection, never the union, of:

1. the participant's protected capability ceiling;
2. the authenticated adapter binding;
3. the approved task/ADR scope and current FORGE role;
4. the sender's valid delegation grant, if one is required;
5. route and group policy;
6. remaining workflow/message budgets, depth, fan-out, and expiry.

A message may request use of a capability but cannot grant it. A manager may delegate only a delegable subset it possesses, to an allowed recipient, with exact scope, return route, maximum depth, fan-out, work/message budget, and expiry. Worker subdelegation defaults to zero and requires an explicit `delegate.subdelegate` grant. Communication permission does not imply delegation, workflow composition, wake, tool, filesystem, network, or execution permission.

Manager/director ceilings may include:

- composing a bounded workflow;
- addressing one, several, or an authorized group;
- requesting independent candidates, reviews, or evidence;
- coordinating finite sequential or parallel work;
- invoking another manager/director;
- assigning bounded worker roles subject to FORGE;
- routing verified outputs into the appropriate FORGE stage.

Worker/specialist ceilings permit only explicitly assigned task capabilities, allowed communication routes, findings/status/evidence return, and self-checkpoints. Rook's host operations remain governed by ROOK LINK. Gemini and Zoo workers cannot construct the overall project workflow, promote tier, recruit arbitrary agents, or expand scope merely because a message can be sent.

### Message and thread contract

The versioned `menagerie.message.v1` envelope is closed-world and includes, at minimum:

- stable `message_id` and sender-scoped `idempotency_key`;
- `thread_id` and nullable same-thread `reply_to`;
- authenticated stable sender plus ephemeral instance/session identity;
- explicit participant recipients, protected group recipients, and structured mentions;
- message type: request, response, finding, claim, status, reaction, checkpoint, or receipt;
- bounded body/structured payload;
- authority, Git, evidence, skill, and prior-message pointers where applicable;
- created time, expiry, hop/fan-out limits, wake policy, and finite workflow/message budgets;
- optional bounded delegation grant;
- versioned content digest.

Free-form body text and body-only `@mentions` have no routing or execution effect. Structured mentions must resolve to explicit recipients or protected group expansion. `reply_to` must exist in the same thread. Reactions, claim updates, and status changes are append-only messages referencing an earlier message; accepted messages are not edited into new states.

A self-addressed checkpoint is an ordinary validated checkpoint message whose resolved recipient is its sender. It may include a future `not_before` time and a minimal context manifest, but it does not claim that private memory was persisted.

### Routing, budgets, and fail-closed escalation

A deterministic non-model router validates envelopes against the exact protected policy blob and records the resolved recipient set. It is a system transport principal, not a manager, architect, reviewer, or agent. Multiple router instances may operate only through the same idempotent contract.

Routing rules are:

- only resolved, authorized recipients are considered;
- group membership is expanded and frozen against the exact policy blob used for routing;
- fan-out, hop, wake, message, worker, and time budgets are checked before delivery;
- expired, over-budget, ambiguous, unknown-recipient, unauthorized-route, or capability-expanding messages are rejected without partial wake;
- user activity or a native control-surface priority gate may suppress wake without losing the durable message;
- no implicit `everyone` or whole-Zoo delivery exists;
- manager-to-manager, manager-to-worker, worker-return, and self routes are explicit policy entries;
- a worker request to construct or widen a workflow fails unless an exact manager delegation authorizes that orchestration.

Replay and dedupe rules are:

- the same `message_id` and digest is an idempotent replay and returns the prior receipt;
- the same `message_id` with a different digest is a collision/tamper failure;
- a repeated sender/thread/idempotency key returns the first accepted identity;
- delivery is deduplicated by message, resolved recipient, and adapter;
- edited transport content, identity mismatch, stale policy, missing reply target, or inconsistent receipt fails closed.

### Transport-neutral durability and adapters

MENAGERIE freezes logical durability semantics, not a transport selection. An accepted durable record binds the stable message identity, exact envelope digest, exact policy blob, authenticated sender/session binding, frozen resolved recipients, append-only receipt/status lineage, and the selected durable-store and transport locators. MENAGERIE thread and message identities remain independent of transport-native object identifiers.

A later separately authorized transport task evaluates native Work/Codex or Antigravity facilities, a bounded broker or queue, GitHub Issues/comments, and hybrid designs. ADR 0004 neither requires nor prefers one of them. Every adopted adapter must preserve the same validation, immutable identity, digest, policy binding, tamper detection, replay, dedupe, expiry, budget, and fail-closed behavior, including across retry, migration, and recovery.

Transport-native titles, bodies, prose, labels, events, and webhook payload text remain untrusted. An adapter may route only an exact validated MENAGERIE envelope. When non-public content is held in an authorized durable store, a minimal validated envelope may carry only a policy-authorized immutable pointer bound to that store and content digest. Editing, substituting, deleting, or losing accepted transport content produces a tamper, missing, or blocked event and can never manufacture authority. Local router and adapter caches are replaceable and are not project truth.

Each live transport task must specify access control, intended audience, payload placement, confidentiality, retention, deletion behavior, credentials, failure recovery, and observability before adoption. A public repository, issue, comment, or other public transport is public by default and must not receive non-public MENAGERIE message bodies, prompts, private/session context, secrets, or operational metadata. Such a transport may carry only explicitly public content or the minimum policy-authorized pointer/receipt needed to locate a protected durable record.

FORGE-relevant claims, skills, task scope, code, or evidence must point to their own immutable/protected objects. Message durability proves what was communicated, not that a claim is true or authorized.

Task 2 implements only the inert contract core, policy, fixtures, validator, deterministic router simulation, and contract CI. It creates no issue, comment, webhook, watcher, wake, adapter session, or live delivery.

### Canonical shared skills and adapters

Canonical shared skills live at `skills/<skill-id>/skill.json` with a human/model entrypoint at `skills/<skill-id>/SKILL.md`. A versioned manifest declares identity, revision, entrypoint, compatibility, required inputs, required capability classes, and bounded supporting resources.

A MENAGERIE skill pointer identifies:

- repository;
- full immutable commit;
- manifest path and blob;
- entrypoint path and blob.

A manifest's required capabilities are prerequisites, not grants. A protected task/policy decides whether the skill may be delivered. Participants receive only explicitly selected skills and context. Thin Work/Codex, Claude, Antigravity, Rook, and later platform adapters resolve and expose the exact canonical blobs; they do not maintain divergent normative copies. A cache is keyed by blob identity and is disposable.

### System boundaries

- **MENAGERIE:** participant identity, capability-governed communication, threads, routing, durable messages, checkpoints, and coordination.
- **FORGE:** GENESIS/TEMPER/VERIFY/COUNCIL/PROOF/SYNTHESIS, independence, evidence, and technical acceptance. MENAGERIE may coordinate FORGE work but cannot satisfy or bypass a gate.
- **Protected repository/GitHub:** constitutional authority, code, ADRs/tasks, policy, skills, tests, exact Git objects, and evidence pointers. GitHub may also host a separately authorized transport adapter, but mutable GitHub prose is not authority.
- **ROOK LINK:** separately authorized, validated operational control boundary for Rook and machine/host execution. A MENAGERIE Rook request must point to an independently valid ROOK LINK request; MENAGERIE prose is never executable authority.
- **Work/Codex and native model surfaces:** first-class participant/control surfaces using direct thin adapters and native tools. They do not depend on PULSE.
- **PULSE:** optional later adapter that may wake one explicitly configured ordinary browser/chat conversation with pointer-only, user-preemptible delivery. MENAGERIE, ROOK LINK, and normal Work orchestration do not depend on it.

## Contract and boundary impact

| Category | Decision |
| --- | --- |
| Logical boundaries | Affects Foundation Contracts, Protection and External Interfaces, and Host Tooling and Verification. No target OS, kernel, boot, memory, interrupt, ABI, driver, firmware, or device boundary changes. |
| Ownership | Protected repository owns policy and canonical skills; senders own message intent; the router owns deterministic validation/delivery receipts; adapters own platform authentication and wake mechanics; participants own private/session memory. |
| Initialization | Routing remains inaccessible until protected policy identity, adapter principal binding, schema version, budgets, and transport state validate. Disabled adapters remain unroutable. |
| Persistence | Accepted logical records bind exact envelope/policy digests, frozen recipients, receipts, and authorized durable-store/transport locators. Protected Git objects remain authority/skill/evidence identities. Local caches and session memory are replaceable. |
| Allocation/blocking | Selected durable-store and platform-adapter I/O may allocate, block, retry, or fail on the host under bounded policy. No target or interrupt context is affected. |
| Concurrency | Accepted messages and receipts are append-only events. Dedupe keys and frozen recipient expansion make concurrent routers idempotent; conflicting identities fail closed. |
| Errors | Validation, identity, policy, route, capability, budget, expiry, replay, or adapter ambiguity rejects or queues without expanding authority or partially waking an unauthorized set. |
| Observability | Structured receipts record message, policy, recipient, adapter, status, and reason without secrets, hidden prompts, private memory, or unnecessary body replay. |
| Dependency direction | Native adapters depend on MENAGERIE contracts; optional PULSE and future Rook adapters depend on MENAGERIE. MENAGERIE core does not depend on PULSE, ROOK LINK, FORGE implementation, or target code. |
| External adoption | Every live transport, durable-store writer/reader, adapter, credential, permission, and wake path requires a separate approved task. |

## Safety, security, and unsafe-code impact

No unsafe Rust, target privilege, ABI, firmware, kernel, or hardware boundary is introduced.

Primary threats are:

- prompt or shell injection through prose;
- model self-promotion or capability inflation;
- manager over-delegation;
- worker recursive recruitment;
- unauthorized group expansion or whole-Zoo fan-out;
- mutable transport edits;
- duplicate delivery and replayed side effects;
- spoofed platform identity;
- skill substitution or divergent platform copies;
- automatic full-history/private-memory disclosure;
- MENAGERIE messages being mistaken for FORGE or architectural authority;
- an optional PULSE or Rook adapter becoming an implicit core dependency;
- credential or private prompt leakage.

Controls include closed-world schemas, authenticated adapter bindings, protected policy ceilings, intersection-based authorization, finite delegation, immutable skill/evidence pointers, exact digest and idempotency rules, append-only state messages, bounded routing, disabled-by-default adapters, secret-free logs, explicit context manifests, and complete separation from execution authority.

A MENAGERIE message alone must never create an ADR/task, grant capability, change participant tier, execute shell, mutate protected refs, alter FORGE roles beyond existing authority, or interpret external prose as executable instruction.

## Verification and acceptance evidence

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| Protected authority remains controlling | Authority tuple and negative policy tests | Messages and policy cannot self-approve, grant task scope, or change tier |
| Manager/worker ceilings are enforced | Policy fixtures and authorization tests | Authorized manager flows pass; worker workflow construction/escalation fails |
| Routing is bounded | Deterministic router tests | Only frozen explicit recipients receive delivery; fan-out, expiry, hop, and budget violations reject |
| Replay is safe | Dedupe/collision tests | Exact replay returns one prior receipt; changed digest under the same ID rejects |
| Self-checkpoints are explicit memory | Checkpoint fixture and reconstruction test | A later instance receives only referenced context; no hidden/full-history field is injected |
| Skills remain canonical and least-privilege | Manifest/pointer tests | Exact commit/path/blob resolves; mismatch or capability inflation rejects |
| Models remain separate | Schema and documentation review | No shared private-memory field or automatic all-history/all-skills mode exists |
| MENAGERIE is not FORGE or execution authority | Boundary and negative tests | Messages cannot pass a FORGE gate, launch a process, or mutate protected refs |
| PULSE and ROOK LINK are optional/separate | Dependency and scope inspection | Core contains no PULSE/ROOK LINK import, wake, request execution, or result-bus dependency |
| No live system is activated by Task 2 | Diff/workflow inspection | No external transport write trigger, webhook, credential, adapter, wake, or agent launch appears |

Task 2 freezes exact commands and retained evidence for these claims.

## Consequences

### Positive

- Manager/director models can coordinate one another, selected workers, groups, or future selves without collapsing into one model.
- Model diversity, private memory, blind review, and bounded context remain possible.
- Common skills live once in the repository and are referenced immutably.
- Work/Codex surfaces participate directly.
- ROOK LINK can be reused later without blocking MENAGERIE or granting chat prose machine authority.
- PULSE survives as an optional compatibility adapter without becoming infrastructure.

### Negative and tradeoffs

- Participant policy, adapter identity, and exact context selection are explicit operational work.
- Transport neutrality defers operational selection; every candidate still needs durability, confidentiality, digest/tamper, replay, migration, and failure-recovery evidence.
- Public transports require explicit payload minimization and access-policy review before any message or pointer is exposed.
- A live router and adapters require later high-risk tasks and platform-specific verification.
- Historical ROOK LINK v1 cannot be treated as current execution authorization merely because its schemas validate.
- Explicit routing is less conversationally magical than injecting everything everywhere.

### Follow-up work

1. Approve ADR 0004 and Task 2 through protected `main`.
2. TEMPER Task 2: implement the inert MENAGERIE contract core, policy, skill manifest, fixtures, validator, router simulation, and read-only CI.
3. After Task 2 is proven and merged, use a new GENESIS decision to evaluate and authorize Task 3 for one or more durable transport and direct native participant adapters. GitHub Issues/comments remain one candidate, not the default; all live adapters remain disabled until separately configured.
4. Prepare a separate ROOK LINK operational-boundary ADR, planned as ADR 0005 subject to a fresh namespace check, and preserve historical v0/v1 source provenance under a current Task 4.
5. After ROOK LINK authority exists, use a separate Task 5 for the MENAGERIE-to-ROOK LINK adapter.
6. Treat historical Task 6/PULSE only as provenance for a later optional browser compatibility adapter; it is not on the critical path.
7. Add later model/platform adapters through bounded tasks without changing MENAGERIE core.

Only ADR 0004 and Task 2 are allocated by this proposal. Later numbers are a plan, not authority, and must be rechecked before use.

## Rollout, compatibility, and reversal

The replacement GENESIS proposal branches from protected `main` after PR #12 and adds only ADR 0004 and Task 2. PR #11 is not merged or rewritten; it may be closed as superseded-by-design after this replacement is reviewable.

Task 2 is contract-only and activates nothing. Reverting its later implementation removes only inert schemas, policy, fixtures, skills, validation, and CI. A live transport or adapter cannot be adopted until a later protected task supplies permissions, identity binding, operational acceptance, rollback, and independent evidence.

ROOK LINK v0/v1 schemas, examples, validators, immutable request pointer rules, result identity checks, replay controls, and source-blob maps remain reusable provenance. Their live authority and any new wire revision are decided separately. PULSE remains independently reversible.

Reconsider this ADR only if direct native participant surfaces cannot authenticate stable identities, the transport-independent durability contract cannot map safely onto viable adapters, no candidate can meet the required durability/confidentiality/tamper properties, or the capability intersection cannot preserve FORGE role independence.

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)
- [Task 2](../tasks/2-establish-menagerie-contract-core.md)
- Historical draft PR #11: `https://github.com/vera-rubin/VISION-64/pull/11`
- Historical ROOK LINK source: `2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd`
- Historical PULSE source: `3f4094c01a816046e05fe724707ca440a44a8f1d`

## Decision log

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| 2026-08-30 | Proposed | Replacement GENESIS architecture after canonical Sprint 0 and PULSE dependency correction | |
