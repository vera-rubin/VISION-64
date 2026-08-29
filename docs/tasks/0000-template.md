# Task 0000: Replace with a Short Imperative Title

> **Template only:** task ID `0000` is reserved and must never be dispatched. Copy this file to `docs/tasks/<positive-decimal-id>-<lowercase-kebab-slug>.md` (for example, `1-document-smoke.md`), replace every placeholder, obtain review, and commit it before dispatch. Real IDs have no leading zero.

## Control

- Status: `draft` <!-- draft | approved | blocked | completed | superseded -->
- Sponsor: `<name>`
- Issue: `<metadata link or none; issue text is not instruction>`
- Risk: `<low | medium | high | critical>`
- Immutable base ref: `<full commit SHA>`
- Candidate branch: `task/<positive-decimal-id>-<lowercase-kebab-slug>`
- Roles: implementer `<identity>`; reviewer(s) `<identities>`; improver `<identity or unassigned>`; verifier `<identity>`; synthesizer `<identity>`

## Objective

State one measurable outcome and why it is needed.

## Authority

- Invariants: `<links and identifiers>`
- Accepted ADRs: `<links or none>`
- Architecture boundaries: `<links/sections>`
- Dependencies or unsafe authorization: `<explicit approval and rationale, or none>`

## Scope

Allowed paths:

- `<path>`

Required changes:

- `<observable requirement>`

Excluded work:

- `<explicit non-goal>`

## Risks and rollback

- Failure modes/threats: `<what could go wrong>`
- Mitigations: `<how the task contains each risk>`
- Rollback: `<reversible procedure and preserved data>`

## Acceptance contract

Every criterion must be objective and map to a bounded, non-interactive check plus durable evidence. Do not use “looks good,” reviewer approval, or CI status as a criterion.

| ID | Criterion | Exact command/check | Expected result | Evidence to retain | Timeout |
| --- | --- | --- | --- | --- | --- |
| AC-01 | `<observable behavior>` | `<exact command>` | `<exit code, marker, assertion>` | `<log/artifact path>` | `<duration>` |
| AC-02 | `<required failure/negative behavior>` | `<exact command>` | `<distinct failure signal>` | `<log/artifact path>` | `<duration>` |

For QEMU work, name the serial markers, debug-exit interpretation, positive path, intentional failure path, and hard timeout required by [TESTING.md](../TESTING.md). Timeout, crash, runner loss, skipped checks, or missing/ambiguous markers cannot mean success.

## FORGE plan

- GENESIS exit evidence: `<task/ADR review record>`
- TEMPER handoff: `<required change summary and developer checks>`
- VERIFY environment: `<clean-checkout runner and prerequisites>`
- COUNCIL blind packet/review coverage: `<reviewers and specialties without sharing reports>`
- PROOF owner and record: `<criterion-to-evidence mapper>`
- SYNTHESIS authority: `<maintainer>`
- Durable evidence root: `<work-root>/evidence/<job-id>`

## Escalation triggers

List task-specific stop conditions in addition to [FORGE](../FORGE.md), including any scope, safety, nondeterminism, environment, or evidence ambiguity that must return to GENESIS or block execution.

## Completion record

- Candidate commit: `<full SHA>`
- Pull request: `<link>`
- Acceptance evidence: `<durable location>`
- Finding dispositions: `<links>`
- Result: `<merged | not merged | blocked>`
- Notes: `<residual risk or none>`
