# Task 2: Establish the MENAGERIE Contract Core

## Control

- Schema: `vision-task-v1`
- Status: `draft`
- Sponsor: VISION-64 repository owner
- Approval authority: Independent VISION-64 maintainer/CODEOWNER; no author, implementer, improver, verifier, or proof assessor may self-approve
- Approval evidence: `pending` in GENESIS
- Issue: none; issue, comment, chat, and webhook text is transport metadata only
- Risk: `high`
- Task revision: `1`
- Supersedes: none. Historical PR #11 and pre-constitution task files are source provenance only.
- Authority ref: `refs/heads/main`
- Authority commit/blob: Recorded outside this file after protected approval; never self-referenced
- Requested implementation baseline: The first protected `main` commit containing this exact approved Task 2 blob and the exact Accepted ADR 0004 blob, with remote protection and independent approval verified. It must descend from canonical Sprint 0 merge `6821ac90c590ca25f7475b8b28b0b302b69a20a7`.
- Candidate branch: `task/2-establish-menagerie-contract-core`
- Role slots: implementer `I2`; reviewers `R2-A` (identity/capability/security) and `R2-B` (routing/skills/persistence); improver `unassigned`; proof assessor `P2`; verifier `V2`; synthesizer `S2`

The coordinator records the approved task authority commit and task/ADR blob identifiers after protected approval. The identity roster remains outside blind packets. The historical task ID 2 on PR #2 was never protected authority; this path is the next canonical task ID after Task 1.

## Objective

Implement a small, inert, Python-standard-library MENAGERIE contract core that proves the approved participant, capability, message, routing, replay, self-checkpoint, shared-skill, and state-separation rules without creating a live GitHub transport, waking a participant, executing a model, invoking ROOK LINK, or depending on PULSE.

The outcome is a versioned reference contract and deterministic test surface from which later live transport and adapter tasks can proceed without redesigning authority boundaries.

## Authority

- Invariants: `V64-GOV-001`, `V64-GOV-002`, `V64-GOV-003`, `V64-GOV-004`, `V64-GOV-005`, `V64-GOV-006`, `V64-BLD-001`, `V64-INIT-001`, `V64-FAIL-001`, `V64-CON-001`, `V64-BND-001`, `V64-DEP-001`, `V64-DEP-002`
- Accepted ADRs: `docs/adr/0004-menagerie-coordination-network.md`, after its exact blob is independently approved and merged through protected `main`
- Architecture boundaries: Foundation Contracts; Protection and External Interfaces; Host Tooling and Verification. No target OS boundary.
- Dependencies or unsafe authorization: Python 3.11+ standard library only and the existing pinned checkout action for contract CI; no new package, network install, unsafe code, privilege, secret, runner, target, ABI, or firmware authorization

Task 2 cannot enter TEMPER until ADR 0004 and this exact task blob are protected authority and their tuple is recorded.

## Scope

Allowed paths:

- `.github/workflows/menagerie-contract.yml`
- `docs/MENAGERIE.md`
- `ops/menagerie/examples/README.md`
- `ops/menagerie/examples/message-manager-multicast-v1.json`
- `ops/menagerie/examples/message-worker-return-v1.json`
- `ops/menagerie/examples/message-self-checkpoint-v1.json`
- `ops/menagerie/examples/message-status-v1.json`
- `ops/menagerie/examples/message-reaction-v1.json`
- `ops/menagerie/policy/policy-v1.json`
- `schemas/menagerie/message-v1.schema.json`
- `schemas/menagerie/policy-v1.schema.json`
- `schemas/menagerie/skill-manifest-v1.schema.json`
- `skills/README.md`
- `skills/examples/mechanical-link-check/SKILL.md`
- `skills/examples/mechanical-link-check/skill.json`
- `scripts/validate-menagerie.py`
- `scripts/test-menagerie.py`

Required changes:

1. Define closed-world `menagerie.message.v1`, `menagerie.policy.v1`, and `menagerie.skill-manifest.v1` schemas.
2. Freeze a deterministic canonical-JSON/digest algorithm for messages and policy objects and test it with fixed vectors.
3. Provide an inert protected-policy candidate containing manager/director identities `sol.gpt`, `opus`, and `fable`; worker/specialist identities/classes `rook.grok`, `gemini.antigravity`, and `zoo.worker.*`; a non-model `menagerie.router` system principal limited to validation and receipt authorship; capability definitions; authorized routes/groups; delegation ceilings; fan-out/hop/wake/message budgets; and all adapter bindings disabled.
4. Enforce authorization as the intersection of protected participant ceiling, adapter binding, task/FORGE scope, delegation, route policy, and remaining budget/expiry.
5. Keep communication, multicast/group routing, workflow composition, delegation/subdelegation, wake delivery, skill delivery, and machine execution as separate capabilities.
6. Accept the positive manager/director examples supplied by ADR 0004 while rejecting worker self-promotion, overall workflow composition, unauthorized manager invocation, arbitrary group/whole-Zoo fan-out, and undelegated subdelegation.
7. Define stable message/thread/reply/recipient/mention/type/pointer/digest/expiry/budget fields and append-only request, response, finding, claim, status, reaction, checkpoint, and receipt semantics.
8. Implement a pure deterministic router simulation with no network or platform I/O. It validates policy identity, freezes group expansion, selects only explicit recipients, enforces budgets/TTL, returns structured receipts, and never launches or wakes anything.
9. Enforce replay rules: exact identity/digest replay returns the prior receipt; identity/digest collision rejects; sender/thread idempotency dedupes; per-recipient delivery dedupes.
10. Prove self-addressed checkpoints and minimal context manifests without a hidden-memory or automatic full-history field.
11. Define canonical shared skills at `skills/<skill-id>/skill.json` and `skills/<skill-id>/SKILL.md`. Exact skill references bind full commit plus manifest/entrypoint paths and blobs. Manifest capability requirements never grant capability.
12. Document thin native Work/Codex, Claude, Antigravity, Rook, and optional PULSE adapter responsibilities without implementing any adapter.
13. Document the strict MENAGERIE/FORGE/repository/ROOK LINK/Work/PULSE boundaries and that MENAGERIE prose is never execution or architectural authority.
14. Provide a fail-closed test suite with named positive and negative groups plus a read-only, GitHub-hosted, pinned, bounded contract workflow.

Excluded work:

- modifying `docs/adr/0001-temporary-bios-boot-contract.md`, `docs/adr/0002-early-diagnostics-protocol.md`, `docs/adr/0003-qemu-terminal-status.md`, `docs/tasks/1-establish-observable-boot-heartbeat.md`, or Sprint 0 implementation;
- merging, rebasing, rewriting, or importing PR #11 or historical PRs #1 through #9 as parents;
- importing historical task specs as authority;
- porting or modifying ROOK LINK schemas, validators, requests, result bus, webhook, bootstrap, or live consumer;
- porting or modifying `tools/pulse-lite/`;
- creating a GitHub issue, comment, discussion, webhook, watcher, ledger writer, repository-dispatch event, or live transport;
- implementing any Work/Codex, Claude, Antigravity, Rook, Zoo, browser, or PULSE adapter;
- waking, launching, messaging, or executing Sol/GPT, Opus, Fable, Rook/Grok, Gemini/Antigravity, Zoo, Codex, Claude, or any other model/agent;
- enabling Gate F `execute` or changing FORGE, dispatch, runner policy, sandbox, credentials, secrets, workflow permissions, branch protection, or remote configuration;
- allowing a message, skill, participant, group, or model to grant capability, tier, task scope, approval, or FORGE success;
- automatically injecting complete MENAGERIE history, all skills, private/session memory, hidden prompts, or model reasoning into another participant;
- assigning or revealing Zoo personalities;
- adding kernel, boot, memory, interrupt, scheduler, ABI, driver, firmware, target, unsafe, hardware, or privileged code;
- adding any third-party dependency or network fetch.

## Risks and rollback

- **Capability inflation:** a participant or message could request more than protected policy permits.

  **Mitigation:** intersection-based authorization and negative tests for every tier/escalation edge.
- **Communication/execution confusion:** the ability to address Rook or another model could be mistaken for execution authority.

  **Mitigation:** no execution capability or adapter exists in Task 2; docs and tests require separate ROOK LINK/task authority.
- **Context homogenization:** adapters could deliver full history or the complete skill library.

  **Mitigation:** explicit context/skill references and negative schema checks prohibit implicit all-context modes.
- **Replay or duplicate wake:** duplicate transport could repeat work.

  **Mitigation:** deterministic digest, idempotency, recipient receipts, and collision failure are part of the core.
- **Mutable transport confusion:** an edited GitHub comment could be accepted as the original message.

  **Mitigation:** exact content digest and transport identity are required; Task 2 only simulates transport.
- **Policy drift:** group membership or capability changes could retroactively reroute a message.

  **Mitigation:** routing binds to and records the exact policy blob and frozen recipient expansion.
- **Skill substitution:** a platform adapter could use a divergent copy.

  **Mitigation:** full commit/path/blob references for manifest and entrypoint; cache by blob only.
- **Accidental activation:** a workflow or helper could perform network writes or launch an agent.

  **Mitigation:** explicit path scope, stdlib-only pure code, read-only CI, static forbidden-surface checks.
- **Historical authority confusion:** old task IDs and green checks could appear current.

  **Mitigation:** current protected authority tuple controls; historical SHAs are provenance only.

Rollback is a protected revert of the Task 2 candidate. All deliverables are inert contracts, fixtures, documentation, and tests, so rollback requires no message migration, agent stop, credential rotation, remote deletion, or target recovery. Authority ADR/task records remain immutable; semantic change returns to GENESIS.

## Acceptance contract

All commands run once from a clean standalone checkout of the exact candidate. The coordinator supplies these values from protected records, never message or issue prose:

- `MENAGERIE_BASE=<protected implementation baseline>`
- `MENAGERIE_CANDIDATE=<exact candidate commit>`
- `MENAGERIE_AUTHORITY_PR=<GENESIS PR number>`
- `MENAGERIE_AUTHORITY_HEAD=<exact GENESIS PR head>`
- `MENAGERIE_TASK_PATH=docs/tasks/2-establish-menagerie-contract-core.md`
- `MENAGERIE_ADR_PATH=docs/adr/0004-menagerie-coordination-network.md`
- `MENAGERIE_TASK_BLOB=<authority-recorded blob>`
- `MENAGERIE_ADR_BLOB=<authority-recorded blob>`
- `MENAGERIE_EVIDENCE=<external evidence directory>`

No automatic retry converts failure, timeout, missing marker, skipped check, crash, or ambiguous output into success. A rerun is a separate evidence attempt.

| ID | Criterion | Authority | Exact command/check | Expected result | Evidence | Timeout/heartbeat |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | Protected authority and baseline are exact | `V64-GOV-005`, `V64-GOV-006` | Command block AC-01 | Protection, independent approval, ancestry, task blob, and ADR blob match coordinator records | Protection/PR JSON and blob record | 90s; no heartbeat |
| AC-02 | Candidate scope is closed and authority artifacts are immutable | `V64-GOV-001`, ADR 0004 | Command block AC-02 | Changed paths equal a subset of the exact allowlist; task/ADR blobs do not change during TEMPER | Changed-path and immutability output | 60s; no heartbeat |
| AC-03 | Contract JSON set is complete and parseable | `V64-BLD-001`, `V64-BND-001` | Command block AC-03 | Exact expected JSON files exist and parse; no undeclared JSON appears under MENAGERIE/skill example paths | JSON inventory/parse log | 60s; no heartbeat |
| AC-04 | Canonical policy, skill, and positive messages validate | ADR 0004 | Command block AC-04 | Policy, skill manifest, and five positive messages exit `0` with stable valid markers | Validator log | 60s; no heartbeat |
| AC-05 | Tier, capability, route, and delegation escalation fail closed | `V64-GOV-001`, `V64-BND-001`, ADR 0004 | `python3 scripts/test-menagerie.py --group authorization` | Exit `0`; named manager flows pass and every worker/self-promotion/group/subdelegation negative is rejected | Authorization-suite log | 90s; no heartbeat |
| AC-06 | Routing, budgets, replay, and self-addressing are deterministic | `V64-CON-001`, `V64-FAIL-001`, ADR 0004 | `python3 scripts/test-menagerie.py --group routing` | Exit `0` with named recipient, fan-out, TTL, digest replay/collision, receipt dedupe, and self-checkpoint markers | Routing-suite log | 90s; no heartbeat |
| AC-07 | Skills and context remain exact, least-privilege, and separate | `V64-BLD-001`, `V64-BND-001`, ADR 0004 | `python3 scripts/test-menagerie.py --group skills-memory` | Exit `0`; exact pointers pass; blob mismatch, capability grant, all-skills, all-history, and hidden-memory cases reject | Skill/memory-suite log | 90s; no heartbeat |
| AC-08 | Documentation preserves all system boundaries | `V64-GOV-002`, `V64-DEP-001`, ADR 0004 | Command block AC-08 | Required separation statements exist and authority/PULSE/ROOK/context-collapse statements are absent | Documentation-policy log | 60s; no heartbeat |
| AC-09 | Core has no external dependency or execution/network surface | `V64-DEP-002`, exclusions | Command block AC-09 | Imports are standard library; forbidden process, shell, network, browser, GitHub-write, and agent-launch primitives are absent | AST/static log | 60s; no heartbeat |
| AC-10 | Contract CI is inert and bounded | `V64-GOV-001`, `V64-BLD-001`, `V64-FAIL-001` | Command block AC-10 | actionlint 1.7.12 is asserted; workflow is pinned, read-only, GitHub-hosted, bounded, and has no live event/write/secret/agent path | Version/lint/static output | 90s; no heartbeat |
| AC-11 | Exact candidate diff and CI succeed | `V64-GOV-003`, `V64-BLD-001` | Command block AC-11 | `git diff --check` passes and exact-head MENAGERIE contract workflow succeeds | Diff log and CI URL | 10m; workflow timeout 5m |
| AC-12 | Evidence is independently anchored | `V64-GOV-004`, `V64-GOV-006` | Command block AC-12 | Manifest digest and candidate SHA appear together in an independent protected record | Manifest, digest, protected record | 90s; no heartbeat |

## Frozen acceptance command definitions

### AC-01 — authority and baseline

~~~bash
test "$(gh api repos/vera-rubin/VISION-64/branches/main/protection \
  --jq '(.required_pull_request_reviews.required_approving_review_count >= 1 and .enforce_admins.enabled == true and .allow_force_pushes.enabled == false and .allow_deletions.enabled == false)')" = true

git cat-file -e "$MENAGERIE_BASE^{commit}"
git cat-file -e "$MENAGERIE_CANDIDATE^{commit}"
git merge-base --is-ancestor "$MENAGERIE_BASE" "$MENAGERIE_CANDIDATE"

test "$(git rev-parse "$MENAGERIE_BASE:$MENAGERIE_TASK_PATH")" = "$MENAGERIE_TASK_BLOB"
test "$(git rev-parse "$MENAGERIE_BASE:$MENAGERIE_ADR_PATH")" = "$MENAGERIE_ADR_BLOB"

gh pr view "$MENAGERIE_AUTHORITY_PR" \
  --repo vera-rubin/VISION-64 \
  --json state,mergedAt,mergeCommit,headRefOid,reviews,author
~~~

Pass requires a merged authority PR, exact authority head/blob records, and at least one approving reviewer who is not the proposal author.

### AC-02 — scope and authority immutability

~~~bash
python3 - "$MENAGERIE_BASE" "$MENAGERIE_CANDIDATE" "$MENAGERIE_TASK_PATH" "$MENAGERIE_ADR_PATH" <<'PY'
import subprocess
import sys

base, candidate, task_path, adr_path = sys.argv[1:]
allowed = {
    ".github/workflows/menagerie-contract.yml",
    "docs/MENAGERIE.md",
    "ops/menagerie/examples/README.md",
    "ops/menagerie/examples/message-manager-multicast-v1.json",
    "ops/menagerie/examples/message-worker-return-v1.json",
    "ops/menagerie/examples/message-self-checkpoint-v1.json",
    "ops/menagerie/examples/message-status-v1.json",
    "ops/menagerie/examples/message-reaction-v1.json",
    "ops/menagerie/policy/policy-v1.json",
    "schemas/menagerie/message-v1.schema.json",
    "schemas/menagerie/policy-v1.schema.json",
    "schemas/menagerie/skill-manifest-v1.schema.json",
    "skills/README.md",
    "skills/examples/mechanical-link-check/SKILL.md",
    "skills/examples/mechanical-link-check/skill.json",
    "scripts/validate-menagerie.py",
    "scripts/test-menagerie.py",
}

def lines(*args):
    return subprocess.check_output(args, text=True).splitlines()

changed = set(lines("git", "diff", "--name-only", base, candidate))
unexpected = changed - allowed
if unexpected:
    raise SystemExit("unexpected changed paths: " + ", ".join(sorted(unexpected)))

for path in (task_path, adr_path):
    before = subprocess.check_output(
        ["git", "rev-parse", f"{base}:{path}"], text=True
    ).strip()
    after = subprocess.check_output(
        ["git", "rev-parse", f"{candidate}:{path}"], text=True
    ).strip()
    if before != after:
        raise SystemExit(f"authority artifact changed during TEMPER: {path}")

print("scope and authority immutability passed")
PY
~~~

### AC-03 — JSON inventory and parse

~~~bash
python3 - <<'PY'
import json
from pathlib import Path

expected = {
    "ops/menagerie/examples/message-manager-multicast-v1.json",
    "ops/menagerie/examples/message-worker-return-v1.json",
    "ops/menagerie/examples/message-self-checkpoint-v1.json",
    "ops/menagerie/examples/message-status-v1.json",
    "ops/menagerie/examples/message-reaction-v1.json",
    "ops/menagerie/policy/policy-v1.json",
    "schemas/menagerie/message-v1.schema.json",
    "schemas/menagerie/policy-v1.schema.json",
    "schemas/menagerie/skill-manifest-v1.schema.json",
    "skills/examples/mechanical-link-check/skill.json",
}
roots = [
    Path("ops/menagerie"),
    Path("schemas/menagerie"),
    Path("skills/examples/mechanical-link-check"),
]
actual = {
    path.as_posix()
    for root in roots
    for path in root.rglob("*.json")
}
if actual != expected:
    raise SystemExit(
        "JSON inventory mismatch: missing="
        + repr(sorted(expected - actual))
        + " unexpected="
        + repr(sorted(actual - expected))
    )
for name in sorted(actual):
    json.loads(Path(name).read_text(encoding="utf-8"))
    print("parsed", name)
PY
~~~

### AC-04 — canonical positives

~~~bash
python3 scripts/validate-menagerie.py policy \
  ops/menagerie/policy/policy-v1.json
python3 scripts/validate-menagerie.py skill \
  skills/examples/mechanical-link-check/skill.json

for message in \
  ops/menagerie/examples/message-manager-multicast-v1.json \
  ops/menagerie/examples/message-worker-return-v1.json \
  ops/menagerie/examples/message-self-checkpoint-v1.json \
  ops/menagerie/examples/message-status-v1.json \
  ops/menagerie/examples/message-reaction-v1.json
do
  python3 scripts/validate-menagerie.py message "$message" \
    --policy ops/menagerie/policy/policy-v1.json
done
~~~

Each command must exit `0` and emit exactly one `valid <schema> <identity>` line.

### AC-05 through AC-07 — named test groups

~~~bash
python3 scripts/test-menagerie.py --group authorization
python3 scripts/test-menagerie.py --group routing
python3 scripts/test-menagerie.py --group skills-memory
~~~

Each command must exit `0`, print its exact `PASS <group>` terminal marker, report every required named negative as rejected, and report zero skipped/expected-failure cases.

### AC-08 — documentation boundaries

~~~bash
python3 - <<'PY'
from pathlib import Path

text = Path("docs/MENAGERIE.md").read_text(encoding="utf-8")
required = [
    "MENAGERIE is a model-neutral coordination network, not a centralized agent or shared consciousness.",
    "Protected repository authority, FORGE, durable MENAGERIE state, canonical skills, and private/session memory are distinct.",
    "Work/Codex surfaces participate directly and do not depend on PULSE.",
    "PULSE is an optional compatibility adapter.",
    "ROOK LINK is a separate operational execution boundary.",
    "A MENAGERIE message is not architectural or execution authority.",
    "Communication permission does not imply delegation or execution permission.",
    "Skills are prerequisites and knowledge, not capability grants.",
]
for phrase in required:
    if phrase not in text:
        raise SystemExit(f"missing boundary statement: {phrase}")

forbidden = [
    "PULSE is required for MENAGERIE",
    "MENAGERIE may execute message prose",
    "A valid message grants the requested capability",
    "All participants share private memory",
    "Every participant receives the complete history",
    "Every participant receives every skill",
]
for phrase in forbidden:
    if phrase in text:
        raise SystemExit(f"forbidden boundary statement: {phrase}")

print("MENAGERIE documentation boundaries passed")
PY
~~~

### AC-09 — dependency and execution-surface guard

~~~bash
python3 - <<'PY'
import ast
import sys
from pathlib import Path

for name in ("scripts/validate-menagerie.py", "scripts/test-menagerie.py"):
    text = Path(name).read_text(encoding="utf-8")
    tree = ast.parse(text, filename=name)
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules = [item.name.split(".", 1)[0] for item in node.names]
        elif isinstance(node, ast.ImportFrom):
            modules = [node.module.split(".", 1)[0]] if node.module else []
        else:
            continue
        for module in modules:
            if module not in sys.stdlib_module_names:
                raise SystemExit(f"non-stdlib import {module} in {name}")

    for token in (
        "subprocess",
        "os.system",
        "shell=True",
        "socket",
        "urllib",
        "http.client",
        "requests",
        "webbrowser",
        "playwright",
        "gh api",
        "issue_comment",
        "repository_dispatch",
    ):
        if token in text:
            raise SystemExit(f"forbidden execution/network token {token} in {name}")

print("dependency and execution-surface guard passed")
PY
~~~

### AC-10 — workflow safety and actionlint

~~~bash
actionlint -version | tee "$MENAGERIE_EVIDENCE/actionlint-version.txt"
grep -Eq '(^|[^0-9])1\.7\.12([^0-9]|$)' \
  "$MENAGERIE_EVIDENCE/actionlint-version.txt"

actionlint -config-file .github/actionlint.yaml \
  .github/workflows/menagerie-contract.yml

python3 - <<'PY'
import re
from pathlib import Path

text = Path(".github/workflows/menagerie-contract.yml").read_text(encoding="utf-8")
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

for pattern in (
    r"(?m)^\s*runs-on:\s*self-hosted",
    r"pull_request_target",
    r"workflow_dispatch",
    r"issue_comment",
    r"discussion",
    r"repository_dispatch",
    r"schedule:",
    r"permissions:\s*write",
    r"secrets\.",
    r"\bcurl\b",
    r"\bwget\b",
    r"\bgh\s",
    r"ROOK_LINK",
    r"PULSE",
):
    if re.search(pattern, text):
        raise SystemExit(f"forbidden workflow construct: {pattern}")

print("MENAGERIE workflow safety passed")
PY
~~~

### AC-11 — exact candidate and CI

~~~bash
git diff --check "$MENAGERIE_BASE" "$MENAGERIE_CANDIDATE"

gh run list \
  --repo vera-rubin/VISION-64 \
  --workflow menagerie-contract.yml \
  --commit "$MENAGERIE_CANDIDATE" \
  --json databaseId,headSha,status,conclusion,url
~~~

Pass requires at least one completed successful run whose `headSha` equals `MENAGERIE_CANDIDATE`.

### AC-12 — independent evidence anchor

The verifier retains:

~~~text
<MENAGERIE_EVIDENCE>/manifest.json
<MENAGERIE_EVIDENCE>/commands.log
<MENAGERIE_EVIDENCE>/criterion-results.json
<MENAGERIE_EVIDENCE>/SHA256SUMS
~~~

The manifest records task/ADR authority tuples, base/candidate SHAs, exact commands and exit codes, input/blob hashes, tool versions, opaque role slots, AC-01 through AC-11 results, start/end times, and clean-checkout state.

~~~bash
sha256sum "$MENAGERIE_EVIDENCE/manifest.json"
~~~

An independent protected PR review or check must record both the exact candidate SHA and this manifest digest. A checksum stored only beside the evidence is insufficient.

## FORGE plan

- GENESIS exit evidence: Accepted ADR 0004 and this exact Task 2 blob, independently approved and merged through protected `main` with authority tuples recorded
- TEMPER handoff: One implementer in a fresh standalone checkout; only allowed paths; pure contract core; developer runs AC-02 through AC-10
- VERIFY environment: Independent verifier, clean exact-candidate checkout, Ubuntu 24.04 or declared equivalent, Python 3.11+, Git, `gh`, and actionlint 1.7.12; no browser, model account, secret, self-hosted runner, or network write required
- COUNCIL blind packet/review coverage: Independent identity/capability/security reviewer and routing/skill/persistence reviewer; implementation provenance and other reports withheld
- PROOF assessor and record: Independent `P2` maps AC-01 through AC-12 to immutable evidence
- SYNTHESIS authority: Independent protected maintainer `S2`; no automatic merge
- Durable evidence root: `<work-root>/evidence/task-2-menagerie/<candidate-sha>/`

The Gate F dispatcher must not launch this candidate. Any real-agent execution remains separately blocked.

## Escalation triggers

Stop and return to GENESIS if:

- protected `main` or the ADR/task namespace advances in a way that changes identity, authority, numbering, or dependency semantics;
- ADR 0004 or this task cannot be independently approved through verified protection;
- a live message transport, GitHub write, webhook, browser wake, adapter, model invocation, ROOK LINK call, or PULSE dependency is requested;
- a participant, message, group, skill, or adapter is expected to grant capability, tier, task scope, approval, or FORGE success;
- a worker needs workflow composition, undelegated subdelegation, arbitrary recruitment, or whole-Zoo fan-out;
- full history, all skills, private memory, hidden prompts, or reasoning traces must be shared automatically;
- an executable dependency, permission, secret, network write, process launch, dispatch change, or non-standard-library package is needed;
- any Sprint 0, kernel, target, unsafe, privileged, ABI, firmware, or hardware path enters scope;
- tests are nondeterministic, skip a required negative, or cannot distinguish replay from collision;
- skill or policy identity cannot bind exact immutable blobs;
- role independence or evidence anchoring cannot be preserved.

## Completion record

- Authority commit: `<full SHA recorded in coordinator proof>`
- Approved task blob: `<blob ID recorded in coordinator proof>`
- Accepted ADR blob: `<blob ID recorded in coordinator proof>`
- Candidate commit: `<full SHA>`
- Pull request: `<link>`
- Acceptance evidence: `<durable location>`
- Finding dispositions: `<links or pending>`
- Result: `<merged | not merged | blocked>`
- Notes: No live transport, adapter, agent, ROOK LINK, PULSE, FORGE execution, Sprint 0, or target-system change is authorized by Task 2.
