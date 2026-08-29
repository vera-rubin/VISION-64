# Task 2: Prove ROOK LINK Webhook Delivery

## Control

- Status: `approved`
- Sponsor: `repository owner`
- Issue: `none; transport metadata is not executable authority`
- Risk: `low`
- Immutable base ref: `a1e9c49e6e7808e2582e7a74dce9146124457f1f`
- Candidate branch: `task/2-rook-link-webhook-smoke`
- Roles: implementer `ChatGPT`; reviewer(s) `unassigned`; improver `unassigned`; verifier `Rook plus GitHub Actions evidence`; synthesizer `repository owner`

## Objective

Prove the first GitHub-to-Rook ROOK LINK v0 wake-up using the already configured repository Actions secrets and Rook webhook. The request must remain the existing v0 `probe.environment.v1` read-only operation.

## Authority

- Invariants: `V64-GOV-001`, `V64-GOV-003`, `V64-GOV-004`, `V64-BLD-001`, `V64-FAIL-001`, `V64-BND-001`, `V64-DEP-002`
- Contract base: `task/1-rook-link-v0` at `a1e9c49e6e7808e2582e7a74dce9146124457f1f`
- Dependencies or unsafe authorization: `none; GitHub Actions and Python standard library only`

## Scope

Allowed paths:

- `docs/tasks/2-rook-link-webhook-smoke.md`
- `ops/rook/requests/rook-link-smoke-001.json`
- `.github/workflows/rook-link-webhook-smoke.yml`

Required changes:

- add one canonical immutable ROOK LINK v0 smoke request;
- add one tightly scoped same-repository PR workflow that POSTs only an immutable request SHA/path pointer to the preconfigured Rook webhook;
- use `ROOK_LINK_WEBHOOK_URL` and `ROOK_LINK_BEARER_TOKEN` only from GitHub Actions secrets;
- never print the URL or token;
- reject wrong repository, actor, head/base branch, malformed commit, or noncanonical request path;
- prohibit redirects and restrict delivery to HTTPS on `api2.cursor.sh` under `/automations/webhook`;
- send no shell command, issue prose, local-PC instruction, or mutable ref.

Excluded work:

- changing the v0 request/result schema or validator;
- enabling mutation or delegation;
- writing to the local PC, runner, tmux, or VISION repo from Rook;
- merging either task branch;
- exposing or rotating the webhook secrets.

## Acceptance contract

| ID | Criterion | Exact check | Expected result | Evidence | Timeout |
| --- | --- | --- | --- | --- | --- |
| AC-01 | smoke request validates under pinned v0 validator | `python3 scripts/validate-rook-link.py request ops/rook/requests/rook-link-smoke-001.json` | exit `0` | workflow log | 30s |
| AC-02 | delivery job is tightly gated | inspect workflow `if:` and endpoint checks | exact repo/actor/head/base; HTTPS `api2.cursor.sh`; no redirects | workflow diff | 30s |
| AC-03 | secrets are not exposed | inspect workflow/logs | secrets referenced only via `${{ secrets.* }}` and never printed | workflow diff/log | 30s |
| AC-04 | Rook webhook accepts immutable pointer | PR workflow run | 2xx response and `ROOK LINK webhook accepted immutable pointer` | Actions run | 2m |
| AC-05 | Rook wakes and treats request as v0 read-only | Rook routine report | request SHA/path consumed; validation succeeds; only requested environment probe runs | Rook report/result | 5m |

## FORGE plan

- GENESIS: this committed task.
- TEMPER: add request + delivery workflow only.
- VERIFY: GitHub-hosted workflow plus Rook routine evidence.
- COUNCIL: optional independent review before any future privilege expansion.
- PROOF: map AC-01..AC-05 to Actions/Rook evidence.
- SYNTHESIS: repository owner; do not merge yet.

## Escalation triggers

Stop if the webhook requires any additional credential, redirect, arbitrary command payload, broader event listener, local-computer permission, mutation, delegation, or contract widening.

## Completion record

- Candidate commit: `<full SHA>`
- Pull request: `<link or none>`
- Acceptance evidence: `<Actions run + Rook routine evidence>`
- Result: `<not merged | blocked>`
