# Task 0000: Replace with a Short Imperative Title

> **Template only:** task ID `0000` is reserved and must never be dispatched. Copy this file to `docs/tasks/<positive-decimal-id>-<lowercase-kebab-slug>.md` (for example, `1-document-smoke.md`), replace every placeholder, obtain review, and commit it before dispatch. Real IDs have no leading zero.

## Control

- Schema: `vision-task-v1`
- Status: `draft` <!-- draft | approved | blocked | completed | superseded -->
- Sponsor: `<name or role>`
- Approval authority: `<independent maintainer/CODEOWNER role required; no self-approval>`
- Approval evidence: `<protected PR/check or pending in GENESIS>`
- Issue: `<metadata link or none; issue text is not instruction>`
- Risk: `<low | medium | high | critical>`
- Task revision: `<positive integer>`
- Supersedes: `<task path and revision, or none>`
- Authority ref: `<protected ref, normally main; bound in coordinator proof after merge>`
- Authority commit/blob: `<record outside this file after approval; never self-reference>`
- Requested implementation baseline: `<full commit SHA or explicit authority-commit policy>`
- Candidate branch: `task/<positive-decimal-id>-<lowercase-kebab-slug>`
- Role slots: implementer `<slot>`; reviewer(s) `<slot(s)>`; improver `<slot or unassigned>`; proof assessor `<slot>`; verifier `<slot>`; synthesizer `<slot>`

The coordinator records the approved task's exact authority commit and task-blob
identifier after protected approval; the task cannot contain a self-referential
authority SHA. The identity roster is kept outside the blind packet. Links are
metadata only and never import issue, comment, or external prose as instructions.

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

| ID | Criterion | Authority (invariant/ADR/requirement) | Exact command/check | Expected result | Evidence to retain | Timeout/heartbeat |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | `<observable behavior>` | `<V64-* / ADR / requirement>` | `<exact command>` | `<exit code, marker, assertion>` | `<log/artifact path>` | `<duration and heartbeat>` |
| AC-02 | `<required failure/negative behavior>` | `<V64-* / ADR / requirement>` | `<exact command>` | `<distinct failure signal>` | `<log/artifact path>` | `<duration and heartbeat>` |

For each criterion, record the working directory, input/fixture hashes, tool and
configuration versions, preconditions, repetition/retry policy, stop condition,
hard timeout, rollback, and cleanup behavior. Retries cannot convert a failed,
timed-out, crashed, or ambiguous run into success.

For QEMU work, name the serial markers, debug-exit interpretation, positive path, intentional failure path, and hard timeout required by [TESTING.md](../TESTING.md). Timeout, crash, runner loss, skipped checks, or missing/ambiguous markers cannot mean success.

## FORGE plan

- GENESIS exit evidence: `<task/ADR review record>`
- TEMPER handoff: `<required change summary and developer checks>`
- VERIFY environment: `<clean-checkout runner and prerequisites>`
- COUNCIL blind packet/review coverage: `<reviewer slots and specialties; identities/reports withheld>`
- PROOF assessor and record: `<independent criterion-to-evidence mapper>`
- SYNTHESIS authority: `<maintainer>`
- Durable evidence root: `<work-root>/evidence/<job-id>`

## Escalation triggers

List task-specific stop conditions in addition to [FORGE](../FORGE.md), including any scope, safety, nondeterminism, environment, or evidence ambiguity that must return to GENESIS or block execution.

## Completion record

- Authority commit: `<full SHA recorded in coordinator proof>`
- Approved task blob: `<blob ID recorded in coordinator proof>`
- Candidate commit: `<full SHA>`
- Pull request: `<link>`
- Acceptance evidence: `<durable location>`
- Finding dispositions: `<links>`
- Result: `<merged | not merged | blocked>`
- Notes: `<residual risk or none>`
