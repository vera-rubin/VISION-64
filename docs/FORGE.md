# FORGE: VISION-64 Change Protocol

FORGE is the mandatory evidence-producing lifecycle for every repository change. It turns a bounded task into a traceable candidate without allowing agent confidence, reviewer popularity, or a green-looking dashboard to substitute for proof.

The only valid stage order is:

**GENESIS -> TEMPER -> VERIFY -> COUNCIL -> PROOF -> SYNTHESIS**

A failed gate moves the candidate back to the named earlier stage; it never permits a stage to be skipped. Documentation-only and smoke-test work may use proportionate checks, but follows the same order.

## Constitutional authority

Authority descends from the [Constitution and invariants](INVARIANTS.md), to accepted [ADRs](adr/), to an approved committed [task spec](tasks/), to implementation. A lower layer may narrow but cannot contradict a higher layer. Conflicts, missing authority, or necessary scope expansion stop the job and require the appropriate higher-layer amendment through review; a task or ADR cannot expand a roadmap gate or waive an invariant.

Status text alone is not authority. An ADR is Accepted, or a task Approved, only when its exact blob is reachable from a remotely verified protected authority ref (normally `main`) through required independent maintainer/CODEOWNER approval. The protected ref, authority commit, artifact path, and blob object ID are the immutable authority tuple. The containing authority commit is recorded after approval and is not self-declared inside the artifact. No author or dispatched worker may self-approve its governing artifact. If branch protection/rulesets or the independent approval record cannot be verified, authority is unavailable and the job is blocked.

Before GENESIS can exit, the coordinator MUST record a read-only check that the
authority ref has the required branch protection or ruleset and independent
approval controls. A local ref named `main`, a push permission, or a successful
workflow does not establish protection. An unprotected authority ref blocks
approval and merge; this constitution does not grant permission to change remote
repository settings during a candidate audit.

The authenticated task blob is the authoritative source of intent. A GitHub issue may point to a task ID and carry discussion or status, but issue-body prose, comments, labels, webhooks, pasted commands, refs, SHAs, paths, and scope fields are untrusted transport data. A link never incorporates mutable external prose. Issue transport must never create or amend authority.

A Proposed task or ADR may be authored and reviewed without an already-approved task only as bounded GENESIS governance work; it authorizes no TEMPER work. The initial Gate F constitution is the one-time bootstrap transition and still requires independent protected review before merge. An approved task is immutable for one lineage: any semantic amendment creates a new task revision and authority tuple, starts a new candidate lineage, and invalidates affected verification, review, and proof.

## Roles and custody

Roles are assigned for one candidate lineage and recorded in the job evidence.

- **Sponsor/task owner:** proposes task scope and acceptance; cannot self-approve the governing blob or waive the Constitution.
- **Coordinator/Rook:** validates dispatch metadata, creates job-scoped checkouts, assigns anonymous candidate IDs, preserves evidence, and moves artifacts between gates. It may halt work but cannot declare technical success, supply approval, assess PROOF, or serve as the sole integrity witness.
- **Implementer:** produces the initial candidate during TEMPER.
- **Reviewer:** performs independent, read-only COUNCIL analysis and records findings. It never edits or certifies acceptance.
- **Improver:** changes a candidate in response to locked findings, records what changed, and sends the new candidate back through VERIFY. It never adjudicates its own fix.
- **Verifier:** executes the frozen acceptance procedure against the exact candidate in a clean environment. It does not edit, improvise fixes, review, or merge.
- **Proof assessor:** maps frozen criteria to immutable verifier/reviewer evidence. It is not the lineage's implementer or improver and does not edit the candidate or evidence, resolve missing proof by assertion, or merge.
- **Synthesizer/maintainer:** confirms that all gates refer to the same candidate, chooses among proven candidates when needed, records the decision, and alone may merge under repository protection.

Codex defaults to implementer or improver. Claude defaults to blind reviewer. Either may take a different strong-worker role when explicitly assigned and independent. Rook owns orchestration and infrastructure custody, not architecture or acceptance. These defaults never override role separation.

The same worker, session, prompt lineage, or materially shared implementation context must not serve as reviewer, improver, or verifier for the same candidate lineage. “Materially shared” means private implementation provenance, prompts, or prior review conclusions beyond the approved anonymous packet; every reviewer receiving the identical packet is required and does not violate independence. An implementer cannot review or verify its own work. A reviewer may re-check disposition of its own finding, but an independent verifier still produces acceptance evidence. The proof assessor cannot be the implementer or improver. If separation is unavailable, the job pauses rather than weakening the gate.

### Weak animal workers

Animal workers are low-trust executors restricted to deterministic, reversible, mechanical tasks whose allowed inputs, commands, paths, and expected outputs are fully specified. Examples are inventory, formatting, link checks, fixture generation from fixed inputs, prescribed test reruns, and log collection. A strong worker must inspect their output.

Animal workers are forbidden from:

- kernel, boot, memory-safety, concurrency, interrupt, ABI, hardware-control, cryptographic, privileged, or unsafe implementation;
- architectural reasoning, ADRs, invariant interpretation, security decisions, task decomposition, risk classification, acceptance design, or finding adjudication;
- reviewer, improver, verifier, synthesizer, merger, release, or approval roles;
- dependency, CI/workflow, runner, permission, secret, dispatch-policy, Git-history, or branch-protection changes;
- choosing commands or paths, following issue-body instructions, expanding scope, or spawning follow-up work.

## Stage gates

### GENESIS

**Purpose:** freeze an implementable, reviewable contract before code is produced.

Required inputs and actions:

- create a real `docs/tasks/<positive-decimal-id>-<lowercase-kebab-slug>.md` from the reserved template; this is the narrow governance-proposal exception to the prior-task rule, the ID has no leading zero, and the proposal authorizes no implementation;
- name the sponsor, risk class, permitted paths, excluded scope, requested implementation source baseline/policy, dependencies, relevant invariants/ADRs, and anonymous role-separation plan; keep the identity-to-role roster in coordinator custody rather than the reviewable task;
- specify measurable acceptance criteria, exact bounded commands, expected positive and negative signals, retained artifacts, timeout behavior, and rollback;
- decide whether an ADR is required; complete and accept it before implementation;
- obtain independent approval and merge the exact task blob through the protected authority ref; record the resulting authority commit and blob ID outside the task so the task does not self-reference. Issue metadata may link the task ID but cannot amend it.

**Exit gate:** the task is unambiguous, independently approved, reachable through the protected authority ref, identified by its authority tuple, and independently reviewable. Automated execution additionally requires a versioned machine schema and validator; until that exists, the task is not dispatch-valid for `execute`. Otherwise it remains `draft` or `blocked`.

### TEMPER

**Purpose:** create the smallest candidate that satisfies the frozen task.

Required inputs and actions:

- branch `task/<positive-decimal-id>-<lowercase-kebab-slug>` from the implementation baseline bound by the authenticated authority record in a fresh security-isolated checkout;
- assign exactly one implementer for the initial candidate; record the candidate ID and commit;
- change only permitted paths, obey dependency and unsafe policies, and make reviewable Conventional Commits;
- run proportional developer checks and preserve a change summary, commands, outcomes, risks, and known limitations.

An improver may act only on locked findings. Improvement creates a new candidate commit in the same lineage and returns it to VERIFY; it cannot preserve a prior proof by assertion.

**Exit gate:** scoped candidate commit plus complete implementation handoff. Scope expansion or newly required architecture returns to GENESIS.

### VERIFY

**Purpose:** obtain reproducible facts from the exact candidate before opinion enters the process.

Required inputs and actions:

- use an independent verifier and a clean checkout of the exact candidate commit;
- execute the frozen task commands without interactive intervention and within declared time bounds;
- record base/candidate commits, relevant environment and tool versions, exact commands, exit codes, expected/observed markers, and durable logs/artifacts;
- classify every criterion as pass, fail, blocked, or not run. Preserve contradictory and failing output.

For executable system work, [TESTING.md](TESTING.md) governs QEMU, serial capture, debug-exit, timeout, positive-path, and intentional-failure evidence. Timeout, crash, missing marker, skipped check, flaky disagreement, and runner loss are never passes.

**Exit gate:** all required pre-review checks have unambiguous evidence. A code/test failure returns to TEMPER; a broken or ambiguous contract returns to GENESIS.

### COUNCIL

**Purpose:** expose defects and unsupported assumptions through independent blind review.

The coordinator creates the same review packet for every reviewer containing only:

- the unchanged substantive task contract, its authority tuple, and governing ADR/invariant references, with identity-to-role fields excluded or integrity-preserving redactions applied;
- anonymous candidate ID, immutable base, candidate diff, and relevant source snapshot;
- VERIFY evidence, including failures and limitations;
- the required finding schema and review deadline.

Until reviews are locked, keep the identity-to-role roster in separate coordinator custody and withhold implementer/improver identity, prompts and transcripts, other reviewers' identities or reports, vote counts, expected outcomes, and sponsor preference. Reviewers do not communicate with one another. If tooling cannot fully hide authorship, disclose the limitation and require reviewers to ignore identity and social signals.

Each finding records severity, affected location/artifact, violated requirement, objective evidence or reproducible check, and required resolution. Reviewers may report questions or unproven risks, clearly labeled, but must not edit the candidate. Reports are locked before simultaneous reveal.

**Exit gate:** all commissioned independent reviews are locked and findings are normalized without changing their substance. Actionable findings go to an assigned improver at TEMPER; missing review coverage remains blocked.

### PROOF

**Purpose:** decide acceptance from criteria and evidence, never popularity.

An assigned proof assessor compiles the proof record without editing the candidate or evidence. The assessor MUST NOT be the candidate's implementer or improver. The synthesizer independently checks the completed proof record before integration.

For each acceptance criterion, the proof record must link the exact candidate to:

- verifier evidence and retained artifacts;
- applicable COUNCIL findings and their disposition;
- a reproducible reason the criterion is satisfied or not satisfied;
- residual risk explicitly allowed by the existing task/ADR, if any.

#### Evidence over votes

Reviews are findings, not votes. Majority, unanimity, model confidence, reputation, or repeated approval cannot override a reproducible failure, violated invariant, unmet criterion, or missing evidence. One substantiated blocker is sufficient to stop advancement. Unsupported objections do not automatically veto a candidate; reproduce them or record them as unresolved uncertainty. When evidence conflicts, rerun or improve the test until the conflict is explained. Absence of evidence is `not proven`, never pass.

No one may waive an invariant. A legitimate semantic change in requirement returns to GENESIS as a new task revision and, when architectural, an ADR or constitutional amendment. It creates a new authority tuple and lineage and invalidates affected verification, review, and proof evidence. Material candidate changes likewise invalidate affected evidence.

**Exit gate:** every criterion is proven for the exact candidate, every blocking finding is resolved and independently checked, evidence is complete, and no constitutional conflict remains. Otherwise return to GENESIS, TEMPER, VERIFY, or COUNCIL as indicated by the defect.

### SYNTHESIS

**Purpose:** integrate only a proven candidate and leave an auditable decision.

The synthesizer:

- checks task, base, candidate, reviews, and proof all identify the same lineage and commits;
- compares proof records rather than reviewer counts when multiple candidates exist;
- confirms the PR contains scope/risk summary, criterion-to-evidence map, finding disposition, and rollback instructions;
- confirms required CI independently reproduces the task's mandatory checks;
- records the selected candidate and rationale, then merges only through protected repository controls.

**Exit gate:** merged commit and retained evidence are traceable to the accepted task, or the task is closed with a recorded non-merge reason. Agents do not self-merge.

## Dispatch and isolation contract

The Gate F dispatcher accepts structured, validated values only: job ID, numeric task ID, committed task-spec path, allowlisted agent (`none`, `codex`, or `claude`), mode (`smoke`, `dry-run`, or rejected `execute`), explicit absolute work root, and full policy/base commit ID. Unknown input fails closed. These transport fields are preflight data, not authority.

- Safe defaults are `mode=smoke` and `agent=none`.
- Smoke runs remain detached, create no task branch, invoke no real agent, and never touch kernel code.
- A Gate F job uses a linked worktree at `<work-root>/worktrees/<job-id>`; durable evidence is `<work-root>/evidence/<job-id>` and survives cleanup. Linked worktrees share a common Git control plane and are not a security boundary.
- `mode=execute` is unavailable in Gate F and MUST fail before worktree creation or agent launch. Environment variables cannot enable it.
- Job IDs, paths, refs, task IDs, agents, and modes must be allowlisted and canonicalized before any filesystem or process action. Never evaluate input as shell code.

Enabling execution requires a separately reviewed versioned task/dispatch schema that derives all scope and roles from authenticated authority; protected-ref/policy validation; an authorization digest bound to the entire operation; a preventive filesystem, credential, and network sandbox; a disposable standalone Git control plane; bounded file types/counts/sizes; a trusted non-agent freezer that creates an immutable candidate commit; and independent acceptance verification from a clean checkout of that commit.

The initial end-to-end smoke proves only trusted checkout, input validation, job-path separation, evidence capture, and CI transport. It does not establish a security boundary, prove the adapters, execute an issue, or authorize implementation.

## Evidence package and escalation

Evidence lives outside disposable worktrees and is uploaded by CI when applicable. Candidate evidence identifies job/task authority tuple/candidate/baseline/policy commit, assigned roles, host and relevant tool versions, exact commands and exit codes, start/end times, timeouts, logs/artifacts, per-criterion results, review limitations, and an integrity-preserving reference to the tested commit. Gate F smoke uses a proportionate manifest, policy/helper blob record, and explicitly structural-only result defined in TESTING; it is not FORGE VERIFY or PROOF. Secrets must be redacted without hiding material failures.

Before cleanup or PROOF, publish the evidence-manifest digest, candidate commit, and CI run/artifact ID and digest to a protected check or PR record controlled independently of Rook. An in-package checksum file alone is not an integrity anchor.

Stop, preserve evidence, mark the stage `blocked`, and escalate when:

- authority, task scope, expected behavior, or acceptance evidence is missing or contradictory;
- a change requires an invariant amendment, ADR, dependency, unsafe boundary, permission, roadmap expansion, or privileged runner action;
- role separation or review blindness cannot be maintained;
- tests are nondeterministic, evidence conflicts, the environment differs materially, or a required check cannot run;
- a secret, untrusted command, unexpected path/ref, dirty worktree, or potential destructive action is encountered.

An escalation states the exact stage and commit, observed evidence, applicable rule, work safely completed, and the smallest decision or authority required. It never conceals a failure behind a retry, scope change, or reviewer consensus.
