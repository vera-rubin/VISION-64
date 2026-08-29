# ADR NNNN: Short decision title

<!--
Copy this file to docs/adr/NNNN-short-kebab-title.md. Assign the next unused
four-digit number; never renumber or reuse an ADR number. Remove instructional
comments before requesting acceptance. A prototype does not make an ADR Accepted.

A Proposed ADR may be authored during GENESIS. It becomes Accepted only when
the exact blob is merged through the protected authority with independent
maintainer/CODEOWNER approval and a durable protected record. An ADR may propose
an invariant amendment or retirement; it never waives an invariant.
-->

- **Status:** Proposed
- **Date:** YYYY-MM-DD
- **Owners:** Names or roles accountable for the decision
- **Decision scope:** Subsystems and interfaces affected
- **Related task(s):** `docs/tasks/<positive-decimal-id>-short-kebab-title.md`
- **Related invariants:** `V64-...`
- **Supersedes:** None
- **Superseded by:** None
- **Approval authority:** Independent maintainer/CODEOWNER role (no self-approval)
- **Approval evidence:** Protected PR/check and merged commit, or `pending` while Proposed

## Decision summary

<!-- One paragraph stating the decision without repeating the analysis. -->

## Context and problem

<!--
Describe the concrete problem, current state, triggering requirements, and why a
decision is needed now. Separate observed facts from assumptions. Do not use this
section to smuggle in unrelated architecture.
-->

## Constraints and decision drivers

<!--
List measurable constraints, relevant threat/failure models, constitutional
rules, V64-* invariants, compatibility requirements, and explicitly non-goals.
Rank drivers where tradeoffs exist.
-->

## Options considered

### Option A — Name

- Description:
- Benefits:
- Costs and risks:
- Invariant impact:
- Evidence available or required:

### Option B — Name

- Description:
- Benefits:
- Costs and risks:
- Invariant impact:
- Evidence available or required:

<!-- Include “do nothing/defer” when it is a legitimate option. -->

## Decision

<!--
State the selected option and the reasons tied to the ranked drivers and evidence.
Record dissent or unresolved uncertainty; reviewer count is not evidence.
-->

## Contract and boundary impact

<!--
Name affected logical boundaries from docs/ARCHITECTURE.md. Specify ownership,
lifecycle, initialization, blocking/allocation behavior, concurrency/interrupt
safety, errors, observability, and dependency direction that change. State “None”
for an unaffected category rather than omitting it.
-->

## Safety, security, and unsafe-code impact

<!--
Describe new trusted inputs, privilege or ABI boundaries, unsafe operations,
proof obligations, failure containment, and affected V64-* invariants. Explain
how safe callers are prevented from violating the contract.
-->

## Verification and acceptance evidence

<!--
For every material claim, name a reproducible check, analysis, benchmark, trace,
or review artifact and its pass/fail rule. Link the task-spec acceptance criteria.
A successful build alone is insufficient for runtime claims.
-->

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| Replace with a claim | Replace with a command or artifact | Replace with an objective condition |

## Consequences

### Positive

-

### Negative and tradeoffs

-

### Follow-up work

-

## Rollout, compatibility, and reversal

<!--
Describe ordering, migration, compatibility window, rollback/recovery plan, and
the observable condition that would cause the decision to be reconsidered.
-->

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)

## Decision log

<!-- Append status transitions; do not rewrite history. -->

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| YYYY-MM-DD | Proposed | Initial proposal | |
