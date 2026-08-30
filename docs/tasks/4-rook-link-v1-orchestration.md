# Task 4 — Reauthorize ROOK LINK v1 Under Protected Authority

## Control

- **Schema:** `vision-task-v1`
- **Status:** `draft`
- **Sponsor:** repository owner
- **Approval authority:** Independent maintainer/CODEOWNER role; no self-approval
- **Approval evidence:** `pending` in GENESIS
- **Issue:** none; issue text and comments are transport metadata only
- **Risk:** `high`
- **Task revision:** `2`
- **Supersedes:** none as authority; the pre-constitution Task 4 blob is source provenance only
- **Authority ref:** protected `main`; exact authority tuple recorded after merge
- **Authority commit/blob:** recorded outside this file after protected approval; never self-reference
- **Requested implementation baseline:** the first protected `main` commit whose tree contains the exact approved Task 4 revision 2 blob and the Accepted boundary ADR blob, with remote protection and independent approval verified
- **Candidate branch:** `task/4-rook-link-v1-orchestration-r2`
- **Role slots:** implementer `<opaque slot>`; reviewers `<opaque slots>`; improver unassigned initially; proof assessor `<opaque slot>`; verifier `<opaque slot>`; synthesizer independent protected maintainer

The coordinator records the approved task’s authority commit and task-blob identifier after protected approval. Identity-to-role mappings remain outside blind review packets.

## Objective

Carry forward the proven ROOK LINK v0/v1 wire contracts, examples, validator, documentation, notification-only issue template, and contract-only CI from exact historical source commit `2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd` onto the current constitutional lineage without redesigning the wire contract, enabling live execution, importing obsolete task authority, or changing PULSE, MENAGERIE, kernel, or target-system code.

The historical source commit is provenance only. It is not the implementation baseline, an approval record, or execution authority.

## Authority

- **Invariants:** `V64-GOV-001`, `V64-GOV-002`, `V64-GOV-003`, `V64-GOV-004`, `V64-GOV-005`, `V64-GOV-006`, `V64-BLD-001`, `V64-BND-001`, `V64-DEP-001`, `V64-DEP-002`, `V64-FAIL-001`
- **Accepted ADR:** `docs/adr/0002-rook-link-pulse-boundaries.md`, after its exact blob is independently approved and merged through protected `main`
- **Architecture boundaries:** Host Tooling and Verification; Protection and External Interfaces; Diagnostics and Recovery; Foundation Contracts. No target OS boundary.
- **Dependencies or unsafe authorization:** Python standard library only; existing pinned GitHub Actions checkout; no new runtime dependency; no unsafe code; no privilege, ABI, firmware, runner, or target authorization.

This task cannot enter TEMPER until the referenced ADR is Accepted through protected authority and the authority tuple is recorded.

## Scope

### GENESIS-only authority artifacts

The GENESIS proposal contains only:

- `docs/adr/0002-rook-link-pulse-boundaries.md`
- `docs/tasks/4-rook-link-v1-orchestration.md`

Those files become immutable authority artifacts after protected approval. They are not edited during TEMPER.

### TEMPER-allowed paths

- `.github/ISSUE_TEMPLATE/rook-link-request.yml`
- `.github/workflows/rook-link-contract.yml`
- `docs/ROOK_LINK.md`
- `ops/rook/examples/README.md`
- `ops/rook/examples/request-v1.json`
- `ops/rook/examples/request-v2.json`
- `ops/rook/examples/result-v1.json`
- `ops/rook/examples/result-v2.json`
- `schemas/rook-link/request-v1.schema.json`
- `schemas/rook-link/request-v2.schema.json`
- `schemas/rook-link/result-v1.schema.json`
- `schemas/rook-link/result-v2.schema.json`
- `scripts/test-rook-link.py`
- `scripts/validate-rook-link.py`

### Required changes

1. Preserve the v0 and v1 wire identifiers, field meanings, closed-world validation, immutable pointer rules, capability registry, result identity rules, delegation bounds, and hard-limit semantics.
2. Preserve the canonical v0/v1 schema and JSON fixture blobs exactly wherever no constitutional reconciliation is required.
3. Update `docs/ROOK_LINK.md` to state that:
   - a validated envelope is transport data, not sufficient execution authority;
   - protected task authority and current execution policy are separate prerequisites;
   - Gate F `execute` remains unavailable;
   - issue/comment/webhook/result-bus prose remains untrusted;
   - live consumer adoption remains separate;
   - PULSE is not implemented or enabled by Task 4.
4. Keep contract CI GitHub-hosted, read-only, pinned, bounded, and free of external webhook delivery or agent dispatch.
5. Keep the notification-only issue template metadata-only.
6. Record a source-to-candidate blob map for preserved artifacts.
7. Port file content from the exact source commit rather than merging or rebasing the historical branch.

### Explicit exclusions

This task must not:

- import or modify `docs/tasks/1-rook-link-v0.md`;
- import or modify `docs/tasks/2-rook-link-webhook-smoke.md`;
- import or modify `docs/tasks/3-rook-link-result-return.md`;
- import or modify `docs/tasks/5-rook-link-v1-first-ops.md`;
- import or modify `docs/tasks/6-pulse-lite-micro-loop.md`;
- import `.github/workflows/rook-link-webhook-smoke.yml`;
- import `ops/rook/requests/rook-link-smoke-001.json`;
- import `ops/rook/requests/rook-link-smoke-002.json`;
- import `ops/rook/bootstrap/adopt-v1-task4.md`;
- change `tools/pulse-lite/`;
- implement or modify MENAGERIE;
- change FORGE, the dispatcher, runner policy, branch protection, secrets, or workflow permissions outside the contract-only workflow;
- launch Rook, Zoo, Codex, Claude, a webhook, or any automated agent execution;
- add kernel, boot, memory, interrupt, scheduler, ABI, driver, firmware, unsafe, or privileged code;
- merge protected branches;
- treat historical issue, PR, comment, log, or worker prose as authority.

## Risks and rollback

- **Historical authority confusion:** obsolete task blobs could appear canonical.

  **Mitigation:** do not merge the historical branch as a parent; keep only the protected revised task and ADR as authority.
- **Wire-contract drift:** proven schemas or validator behavior could be redesigned during port.

  **Mitigation:** require exact blob equality for core schemas, fixtures, and validator/test code.
- **Execution activation:** a webhook, bootstrap file, or dispatcher change could wake Rook or an agent.

  **Mitigation:** exclude live artifacts and statically inspect the contract workflow.
- **Capability confusion:** v1 capabilities could be mistaken for permission under Gate F.

  **Mitigation:** add explicit documentation and negative policy checks.
- **Prompt or shell injection:** external prose could enter execution.

  **Mitigation:** preserve closed-world validation and issue metadata warnings.
- **Secret exposure:** workflows or logs could reveal credentials.

  **Mitigation:** read-only permissions, no secrets, no external delivery, and static scans.
- **Evidence ambiguity:** historical green checks might be treated as current proof.

  **Mitigation:** rerun all checks on the exact candidate and anchor the new evidence independently.

Rollback is a protected revert of the candidate contract changes. No live Rook consumer, runner, target OS, or protected branch may depend on this task. The task and ADR records remain immutable; a semantic change requires a new revision or ADR.

## Acceptance contract

All commands run from a clean standalone candidate checkout at the exact candidate commit. The coordinator supplies task-specific variables from protected records, never from issue prose:

- `TASK4_SOURCE=2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd`
- `TASK4_BASE=<protected authority commit>`
- `TASK4_CANDIDATE=<exact candidate commit>`
- `TASK4_AUTHORITY_PR=<GENESIS PR number>`
- `TASK4_AUTHORITY_HEAD=<exact GENESIS PR head>`
- `TASK4_CANDIDATE_PR=<candidate PR number>`
- `TASK4_TASK_PATH=docs/tasks/4-rook-link-v1-orchestration.md`
- `TASK4_ADR_PATH=docs/adr/0002-rook-link-pulse-boundaries.md`
- `TASK4_TASK_BLOB=<authority-recorded blob>`
- `TASK4_ADR_BLOB=<authority-recorded blob>`
- `TASK4_EVIDENCE=<external evidence directory>`

No automatic retries convert a failure, timeout, crash, missing artifact, or ambiguous result into success. A rerun creates a separate evidence attempt.

| ID | Criterion | Authority | Exact command/check | Expected result | Evidence | Timeout/heartbeat |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | Protected authority and baseline are verified | `V64-GOV-005`, `V64-GOV-006` | Command block AC-01 | Protection is enabled with independent approval controls; baseline, task blob, ADR blob, and candidate ancestry match coordinator records | Protection JSON, authority PR JSON, blob record | 90s; no heartbeat |
| AC-02 | Candidate scope is closed and authority files are immutable | `V64-GOV-001`, `V64-GOV-005` | Command block AC-02 | Changed paths are a subset of the explicit allowlist; historical branch is not an ancestor; task/ADR blobs are unchanged | `changed-paths.txt`, scope output | 60s; no heartbeat |
| AC-03 | Core source content is preserved | `V64-BLD-001`, ADR 0002 | Command block AC-03 | Each listed schema, fixture, validator, test, and issue-template blob equals the exact source blob | Source/candidate blob map | 60s; no heartbeat |
| AC-04 | All schemas and fixtures parse | `V64-BND-001`, `V64-BLD-001` | Command block AC-04 | Every ROOK LINK schema and example parses as JSON with no undeclared file | Parse log | 60s; no heartbeat |
| AC-05 | Canonical v0 and v1 positives still validate | ROOK LINK contract, ADR 0002 | Command block AC-05 | v0 request/result and v1 request/result commands exit `0` with expected valid markers | Validator logs | 60s; no heartbeat |
| AC-06 | Fail-closed negative suite remains complete | `V64-BND-001`, ROOK LINK contract | `python3 scripts/test-rook-link.py` | Exit `0`; every named malformed, mutable, unknown, identity-mismatch, capability, delegation, branch, and artifact case is rejected | Negative-suite output | 90s; no heartbeat |
| AC-07 | Documentation binds transport to protected authority | `V64-GOV-005`, ADR 0002 | Command block AC-07 | Required boundary statements exist and old authority-bypassing language is absent | Documentation-policy output | 60s; no heartbeat |
| AC-08 | Contract CI is inert and constitution-compliant | `V64-GOV-001`, `V64-BLD-001`, `V64-FAIL-001` | Command block AC-08 | Required actionlint version is asserted; lint passes; workflow is GitHub-hosted, read-only, pinned, bounded, concurrent, and contains no webhook, secret, target, or agent dispatch | Workflow version/lint/static output | 90s; no heartbeat |
| AC-09 | No dependency, shell, unsafe, or target-scope expansion occurs | `V64-DEP-001`, `V64-DEP-002`, exclusions | Command block AC-09 | Python imports remain standard-library-only; no forbidden execution primitive or out-of-scope path appears | AST/static output | 60s; no heartbeat |
| AC-10 | Exact candidate CI and diff checks pass | `V64-GOV-003`, `V64-BLD-001` | Command block AC-10 | `git diff --check` passes and contract workflow succeeds for exact candidate SHA | CI URL, diff log | 10m; workflow timeout 5m |
| AC-11 | Evidence is independently anchored | `V64-GOV-004`, `V64-GOV-006` | Command block AC-11 | External manifest identifies task/base/source/candidate/roles/commands/results; its SHA-256 and candidate SHA appear in a protected independent record | Manifest, digest, protected record | 90s; no heartbeat |

## Frozen acceptance command definitions

### AC-01 — authority and baseline

```bash
test "$(gh api repos/vera-rubin/VISION-64/branches/main/protection \
  --jq '(.required_pull_request_reviews.required_approving_review_count >= 1 and .enforce_admins.enabled == true and .allow_force_pushes.enabled == false and .allow_deletions.enabled == false)')" = true

git cat-file -e "$TASK4_BASE^{commit}"
git cat-file -e "$TASK4_CANDIDATE^{commit}"
git merge-base --is-ancestor "$TASK4_BASE" "$TASK4_CANDIDATE"

test "$(git rev-parse "$TASK4_BASE:$TASK4_TASK_PATH")" = "$TASK4_TASK_BLOB"
test "$(git rev-parse "$TASK4_BASE:$TASK4_ADR_PATH")" = "$TASK4_ADR_BLOB"

gh pr view "$TASK4_AUTHORITY_PR" \
  --repo vera-rubin/VISION-64 \
  --json state,mergedAt,mergeCommit,headRefOid,reviews,author
```

Pass requires protected `main`, merged authority PR, exact authority head/blob records, and an approving reviewer who is not the proposal author.

### AC-02 — scope and immutability

```bash
python3 - "$TASK4_BASE" "$TASK4_CANDIDATE" "$TASK4_SOURCE" "$TASK4_TASK_PATH" "$TASK4_ADR_PATH" <<'PY'
import subprocess
import sys

base, candidate, source, task_path, adr_path = sys.argv[1:]

allowed = {
    ".github/ISSUE_TEMPLATE/rook-link-request.yml",
    ".github/workflows/rook-link-contract.yml",
    "docs/ROOK_LINK.md",
    "ops/rook/examples/README.md",
    "ops/rook/examples/request-v1.json",
    "ops/rook/examples/request-v2.json",
    "ops/rook/examples/result-v1.json",
    "ops/rook/examples/result-v2.json",
    "schemas/rook-link/request-v1.schema.json",
    "schemas/rook-link/request-v2.schema.json",
    "schemas/rook-link/result-v1.schema.json",
    "schemas/rook-link/result-v2.schema.json",
    "scripts/test-rook-link.py",
    "scripts/validate-rook-link.py",
}

def run(*args):
    return subprocess.check_output(args, text=True).splitlines()

changed = set(run("git", "diff", "--name-only", base, candidate))
unexpected = changed - allowed
if unexpected:
    raise SystemExit("unexpected changed paths: " + ", ".join(sorted(unexpected)))

if subprocess.run(
    ["git", "merge-base", "--is-ancestor", source, candidate],
    check=False,
).returncode == 0:
    raise SystemExit("historical source branch must not be a candidate ancestor")

for path in (task_path, adr_path):
    before = subprocess.check_output(
        ["git", "rev-parse", f"{base}:{path}"], text=True
    ).strip()
    after = subprocess.check_output(
        ["git", "rev-parse", f"{candidate}:{path}"], text=True
    ).strip()
    if before != after:
        raise SystemExit(f"authority file changed during TEMPER: {path}")

print("scope and authority immutability passed")
PY
```

### AC-03 — source blob preservation

```bash
python3 - "$TASK4_SOURCE" "$TASK4_CANDIDATE" <<'PY'
import subprocess
import sys

source, candidate = sys.argv[1:]
paths = [
    ".github/ISSUE_TEMPLATE/rook-link-request.yml",
    "ops/rook/examples/request-v1.json",
    "ops/rook/examples/request-v2.json",
    "ops/rook/examples/result-v1.json",
    "ops/rook/examples/result-v2.json",
    "schemas/rook-link/request-v1.schema.json",
    "schemas/rook-link/request-v2.schema.json",
    "schemas/rook-link/result-v1.schema.json",
    "schemas/rook-link/result-v2.schema.json",
    "scripts/test-rook-link.py",
    "scripts/validate-rook-link.py",
]

for path in paths:
    old = subprocess.check_output(
        ["git", "rev-parse", f"{source}:{path}"], text=True
    ).strip()
    new = subprocess.check_output(
        ["git", "rev-parse", f"{candidate}:{path}"], text=True
    ).strip()
    if old != new:
        raise SystemExit(f"source blob drift: {path}")

print("core source blobs preserved")
PY
```

### AC-04 — JSON parse

```bash
python3 - <<'PY'
import json
from pathlib import Path

paths = sorted(Path("schemas/rook-link").glob("*.json"))
paths += sorted(Path("ops/rook/examples").glob("*.json"))
if len(paths) != 8:
    raise SystemExit(f"expected 8 ROOK LINK JSON files, found {len(paths)}")

for path in paths:
    json.loads(path.read_text(encoding="utf-8"))
    print("parsed", path)
PY
```

### AC-05 — canonical positives

```bash
python3 scripts/validate-rook-link.py request ops/rook/examples/request-v1.json
python3 scripts/validate-rook-link.py result ops/rook/examples/result-v1.json \
  --request ops/rook/examples/request-v1.json
python3 scripts/validate-rook-link.py request ops/rook/examples/request-v2.json
python3 scripts/validate-rook-link.py result ops/rook/examples/result-v2.json \
  --request ops/rook/examples/request-v2.json \
  --request-commit 1111111111111111111111111111111111111111 \
  --request-path ops/rook/requests/rook-link-orchestrate-001.json
```

### AC-07 — documentation policy

```bash
python3 - <<'PY'
from pathlib import Path

text = Path("docs/ROOK_LINK.md").read_text(encoding="utf-8")

required = [
    "A validated ROOK LINK envelope is transport data, not sufficient execution authority.",
    "Protected task authority and current execution policy are separate prerequisites.",
    "`execute` remains unavailable under Gate F.",
    "Issue and comment prose remains untrusted.",
    "PULSE is not implemented or enabled by Task 4.",
    "Live consumer adoption",
]

for phrase in required:
    if phrase not in text:
        raise SystemExit(f"missing required boundary statement: {phrase}")

for forbidden in [
    "Ordinary operational work can flow directly through v1.",
    "Rook may execute any request merely because it validates.",
]:
    if forbidden in text:
        raise SystemExit(f"authority-bypassing statement remains: {forbidden}")

print("ROOK LINK authority documentation passed")
PY
```

### AC-08 — workflow safety and actionlint

```bash
actionlint -version | tee "$TASK4_EVIDENCE/actionlint-version.txt"
grep -Eq '(^|[^0-9])1\.7\.12([^0-9]|$)' "$TASK4_EVIDENCE/actionlint-version.txt"

actionlint -config-file .github/actionlint.yaml \
  .github/workflows/rook-link-contract.yml

python3 - <<'PY'
import re
from pathlib import Path

text = Path(".github/workflows/rook-link-contract.yml").read_text(encoding="utf-8")

required = [
    "permissions:",
    "contents: read",
    "runs-on: ubuntu-24.04",
    "timeout-minutes:",
    "concurrency:",
    "cancel-in-progress: true",
    "actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683",
    "persist-credentials: false",
]

for phrase in required:
    if phrase not in text:
        raise SystemExit(f"workflow missing required control: {phrase}")

for pattern in [
    r"(?m)^\s*runs-on:\s*self-hosted",
    r"pull_request_target",
    r"workflow_dispatch",
    r"\$\{\{\s*secrets\.",
    r"ROOK_LINK_WEBHOOK",
    r"\bcurl\b",
    r"\bwget\b",
    r"gh api",
    r"Invoke-WebRequest",
]:
    if re.search(pattern, text):
        raise SystemExit(f"forbidden workflow construct: {pattern}")

print("contract workflow safety passed")
PY
```

### AC-09 — dependency and execution-surface guard

```bash
python3 - <<'PY'
import ast
from pathlib import Path

allowed = {
    "argparse",
    "copy",
    "importlib",
    "json",
    "pathlib",
    "re",
    "sys",
}

for name in ("scripts/test-rook-link.py", "scripts/validate-rook-link.py"):
    tree = ast.parse(Path(name).read_text(encoding="utf-8"), filename=name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names = [item.name.split(".", 1)[0] for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            names = [node.module.split(".", 1)[0]] if node.module else []
        else:
            continue
        for imported in names:
            if imported not in allowed:
                raise SystemExit(f"undeclared import {imported} in {name}")

for name in ("scripts/test-rook-link.py", "scripts/validate-rook-link.py"):
    text = Path(name).read_text(encoding="utf-8")
    for token in ("shell=True", "os.system(", "eval(", "exec("):
        if token in text:
            raise SystemExit(f"forbidden execution primitive {token} in {name}")

print("dependency and execution-surface guard passed")
PY
```

### AC-10 — exact candidate and CI

```bash
git diff --check "$TASK4_BASE" "$TASK4_CANDIDATE"

gh run list \
  --repo vera-rubin/VISION-64 \
  --workflow rook-link-contract.yml \
  --commit "$TASK4_CANDIDATE" \
  --json databaseId,headSha,status,conclusion,url
```

Pass requires at least one completed successful contract run whose `headSha` equals `TASK4_CANDIDATE`.

### AC-11 — evidence anchor

The verifier writes an external manifest at:

```text
<TASK4_EVIDENCE>/manifest.json
<TASK4_EVIDENCE>/commands.log
<TASK4_EVIDENCE>/criterion-results.json
<TASK4_EVIDENCE>/SHA256SUMS
```

The manifest must contain:

- task ID `4`;
- revision `2`;
- protected authority ref;
- authority commit and task/ADR blob IDs;
- historical source SHA;
- candidate SHA and candidate PR;
- opaque role slots with implementer, reviewer, verifier, proof assessor, and synthesizer distinct;
- exact command IDs, exit codes, timestamps, and output hashes;
- AC-01 through AC-10 statuses;
- tool versions and clean-checkout state.

The coordinator computes:

```bash
sha256sum "$TASK4_EVIDENCE/manifest.json"
```

An independent protected PR review or check must record both the exact candidate SHA and this manifest digest. A checksum stored only beside the manifest is insufficient.

## FORGE plan

- **GENESIS exit evidence:** Accepted boundary ADR and this exact Task 4 revision 2 blob, both merged through remotely verified protected `main` with independent approval.
- **TEMPER handoff:** Fresh standalone candidate checkout from the authenticated protected baseline; content-addressed port of only the allowed ROOK LINK paths; no historical branch merge; developer checks AC-02 through AC-09.
- **VERIFY environment:** Independent verifier, clean checkout of the exact candidate, Ubuntu 24.04 or equivalent declared host, Python 3.11+, Git, `gh`, and actionlint 1.7.12. Missing tools block verification.
- **COUNCIL blind packet/review coverage:** Independent reviewers for trust/authority boundaries and workflow/dependency safety. Withhold implementer identity, prompts, and other reports.
- **PROOF assessor and record:** Independent assessor maps AC-01 through AC-11 to immutable evidence and protected evidence anchor.
- **SYNTHESIS authority:** Independent protected maintainer; no automatic merge.
- **Durable evidence root:** `<work-root>/evidence/task-4-r2/<candidate-sha>/`

The current Gate F dispatcher must not be used to launch this TEMPER candidate. If automated real-agent execution is desired later, it requires a separate protected dispatch-policy task.

## Escalation triggers

Stop and return to GENESIS if:

- the remote protected ADR namespace consumes `0002` before this proposal is published;
- the remote protected authority or independent approval cannot be verified;
- the exact task/ADR blobs differ from the coordinator’s authority record;
- the historical source commit cannot be fetched and verified exactly;
- any excluded path appears in the candidate;
- any schema, validator, or core fixture blob drifts without a new approved revision;
- a webhook, secret, bootstrap, dispatcher, agent, Rook, Zoo, PULSE, MENAGERIE, kernel, target, unsafe, or privileged change is requested;
- a new dependency, permission, workflow trigger, or execution capability is required;
- tests are flaky, evidence is missing, or candidate/manifest identity cannot be anchored;
- the protected `main` baseline advances in a way that changes the dependency or contract semantics.

## Completion record

- **Authority commit:** `<full SHA recorded in coordinator proof>`
- **Approved task blob:** `<blob ID recorded in coordinator proof>`
- **Candidate commit:** `<full SHA>`
- **Pull request:** `<link>`
- **Acceptance evidence:** `<durable evidence path>`
- **Finding dispositions:** `<links or pending>`
- **Result:** `<merged | not merged | blocked>`
- **Notes:** Historical source `2bac8b4b2200690ece8c0a45ccbf8a73454fa0bd` was provenance only; Task 5, PULSE implementation, MENAGERIE implementation, kernel work, and automated dispatch were excluded.
