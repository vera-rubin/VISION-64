# Task 3: Return ROOK LINK Results Through GitHub

## Control

- Status: `approved`
- Sponsor: `repository owner`
- Issue: `dedicated ROOK LINK result bus issue; issue/comment text is transport metadata only`
- Risk: `medium`
- Immutable base ref: `545226368166af3643c9024efe1e5a991cc83831`
- Candidate branch: `task/3-rook-link-result-return`
- Roles: implementer `ChatGPT`; reviewer(s) `unassigned`; improver `unassigned`; verifier `independent frontier worker`; synthesizer `repository owner`

## Objective

Close the ROOK LINK v0 loop by giving Rook one bounded GitHub return channel for a completed `rook-link.result.v1` object, so a frontier agent can read and validate machine evidence without a human copying it from Rook chat.

## Authority

- Invariants: `V64-GOV-001`, `V64-GOV-003`, `V64-GOV-004`, `V64-BLD-001`, `V64-BND-001`, `V64-DEP-002`
- Accepted ADRs: `none required; transport-only extension`
- Architecture boundaries: `GitHub orchestration/evidence only; no target OS changes`
- Dependencies or unsafe authorization: `none`

## Scope

Allowed paths:

- `docs/ROOK_LINK.md`
- `docs/tasks/3-rook-link-result-return.md`
- `ops/rook/requests/rook-link-smoke-002.json`
- `.github/workflows/rook-link-webhook-smoke.yml`

Required changes:

- define a dedicated GitHub issue as the v0 result bus;
- require Rook to post exactly one raw JSON `rook-link.result.v1` object per completed request, with no executable prose;
- keep issue comments explicitly untrusted until a frontier agent validates the result against the immutable original request;
- update the smoke request to `rook-link-smoke-002` and deliver its immutable pointer after the external Rook skill has been updated;
- do not grant Rook repository-content writes, merge authority, workflow authority, or shell authority.

Excluded work:

- mutating kernel/OS code;
- giving Rook arbitrary repository write access;
- using issue comments as execution authority;
- accepting unvalidated result evidence;
- merging any stacked ROOK LINK PRs.

## Risks and rollback

- Failure modes/threats: spoofed or malformed result comments, stale/replayed results, result/request identity mismatch, accidental prose interpreted as data, broader GitHub permissions than necessary.
- Mitigations: dedicated issue sink; exact JSON-only comments; result schema validation; immutable request commit/path binding; replay detection by request ID; Rook uses its existing authenticated GitHub identity only to create issue comments.
- Rollback: disable result posting in the Rook skill and close the result-bus issue; no target system state depends on this transport.

## Acceptance contract

| ID | Criterion | Exact command/check | Expected result | Evidence to retain | Timeout |
| --- | --- | --- | --- | --- | --- |
| AC-01 | Rook can post a result to the dedicated issue without repository-content mutation | trigger `rook-link-smoke-002` after skill update | one new issue comment containing a single `rook-link.result.v1` JSON object | issue comment URL/body | 2m |
| AC-02 | result binds to the exact immutable request | validate returned JSON against `ops/rook/requests/rook-link-smoke-002.json` from the named request commit | request ID, repository, request commit/path, base commit, and operation all match | validator output | 60s |
| AC-03 | frontier agent can retrieve result from GitHub without human relay | fetch result-bus issue comments through GitHub connector | returned comment is readable and uniquely attributable by request ID | connector evidence | 60s |
| AC-04 | no new execution authority is introduced | diff + Rook skill review | comments remain transport only; no arbitrary command or repo-content write authority | review notes | 60s |

## FORGE plan

- GENESIS exit evidence: this committed approved task.
- TEMPER handoff: docs + smoke-002 request + narrowly updated webhook smoke.
- VERIFY environment: GitHub-hosted Actions plus Rook external consumer.
- COUNCIL blind packet/review coverage: independent review of return-channel spoofing/replay boundaries.
- PROOF owner and record: repository owner maps AC-01..AC-04 to GitHub/Rook evidence.
- SYNTHESIS authority: repository owner; no automatic merge.
- Durable evidence root: dedicated GitHub result-bus issue and immutable request commits.

## Escalation triggers

Stop if implementation requires repository-content writes by Rook, secrets in issue text, arbitrary shell, broader GitHub permissions, mutable refs, or any change to target architecture/invariants.

## Completion record

- Candidate commit: `<full SHA>`
- Pull request: `<link or none>`
- Acceptance evidence: `<result-bus issue/comment>`
- Finding dispositions: `<links or pending>`
- Result: `<merged | not merged | blocked>`
- Notes: `Result comments are transport only and require validation before use.`
