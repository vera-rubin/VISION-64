# VISION-64 Roadmap and Delivery Gates

## Roadmap policy

The roadmap authorizes capability, not architecture. A milestone describes the
observable result that may be pursued and the evidence required to leave the
milestone. It does not select an implementation. [ARCHITECTURE.md](ARCHITECTURE.md),
[INVARIANTS.md](INVARIANTS.md), Accepted ADRs, and approved task specifications
remain authoritative.

Work MUST NOT begin merely because it appears in a later milestone. Each task
still requires bounded scope, acceptance tests, and any prerequisite ADRs. A gate
passes only when all criteria have evidence; partial completion, reviewer
consensus, or a green unrelated check does not lower the gate.

## Gate F — Constitution and factory qualification

This gate precedes kernel implementation. Its purpose is to make the development
factory safe enough for a harmless end-to-end dispatch exercise.

### In scope

- the project constitution, invariant registry, testing policy, FORGE process,
  and agent responsibilities;
- ADR and task-spec templates;
- minimal trusted structured-dispatch-to-job-worktree transport with explicit
  allowlists and fail-closed input validation; issue-triggered execution is not
  part of Gate F;
- preservation of the existing self-hosted runner smoke behavior;
- a harmless dispatch smoke limited to validation, isolation, and evidence
  capture in a detached worktree, with no agent launch or repository mutation.

### Gate F exit criteria

Gate F is complete only when:

1. the constitutional documents contain no operative placeholders and cross-link
   their sources of authority;
2. orchestration scripts reject missing, malformed, unauthorized, kernel-code,
   and every `execute` job before worktree creation or agent launch;
3. smoke dispatch uses a fresh isolated detached worktree, creates no branch,
   launches no agent, and leaves the repository unchanged;
4. negative and dry-run checks prove that execution is unavailable, task
   selection cannot fall through to an agent, and malformed control data fails
   closed; enabling real dispatch remains a separately reviewed future change;
5. the existing runner smoke check still passes;
6. the harmless dispatch smoke uses bounded permissions and retains validation,
   environment, and clean-worktree evidence sufficient to prove no kernel-code
   or repository change occurred;
7. no Codex, Claude, Rook, or animal worker has been dispatched to implement
   kernel behavior as part of this gate.

Passing Gate F means the repository is ready to exercise the agentless factory
smoke. It does not mean the adapters are proven or the factory is authorized to
dispatch Sprint 0 implementation automatically.

## Sprint 0 — Observable boot foundation

### Objective

Establish the smallest reproducible build-and-boot loop that can prove subsequent
kernel work starts, reports failure, and terminates automated tests
deterministically.

### Entry gate

Sprint 0 TEMPER implementation may begin only after all of the following are
true:

1. Gate F proof is accepted and the constitution is reachable from the protected
   authority ref;
2. the exact Approved Sprint 0 task blob and its authority tuple exist on that
   protected ref;
3. every architectural mechanism required by that task—including target and
   boot/firmware/artifact contracts, diagnostics and serial protocol, panic
   terminal behavior, and debug-exit mapping—has an Accepted ADR;
4. the task freezes the bounded acceptance contract required by TESTING and
   preserves every explicit exclusion below.

Missing any prerequisite blocks TEMPER and returns work to GENESIS. Passing this
entry gate authorizes only the scope of the exact task; it is not blanket Sprint
0 authority.

### Authorized scope

Sprint 0 is limited to:

- a documented target/build structure and pinned toolchain inputs;
- the minimum diagnostics abstraction required by early boot and tests;
- serial diagnostic output suitable for machine-captured evidence;
- a bounded, allocation-independent panic/fatal reporting path;
- a noninteractive QEMU launch and test harness;
- an emulator debug-exit mechanism for explicit terminal test status, with its
  concrete interface and status mapping chosen through the required ADR/task
  process;
- an earliest practical boot heartbeat;
- positive and negative acceptance fixtures for heartbeat, clean success, and an
  intentional panic/fatal path;
- CI wiring and evidence retention needed to exercise only those capabilities.

“Minimum” is binding: Sprint 0 work MUST NOT generalize a mechanism for imagined
future callers when the accepted tests do not require it.

### Explicitly out of scope

Sprint 0 MUST NOT implement:

- a general-purpose physical or virtual memory manager;
- interrupt-controller, timer, multiprocessor, or scheduler functionality;
- processes, userspace, a syscall ABI, or a security/capability model;
- general device discovery or drivers beyond the narrow diagnostic/test-exit
  adapter;
- storage, file systems, networking, graphics, or application services;
- performance tuning, broad portability layers, or speculative abstractions;
- production kernel work performed by the orchestration smoke test.

If a prerequisite appears to demand one of these, Sprint 0 is blocked and MUST
return to constitutional roadmap review or define a later gate. An ADR or task
alone cannot expand this milestone.

### Required Sprint 0 evidence

The exact commands, markers, exit mapping, timeouts, and artifact names belong in
[TESTING.md](TESTING.md) and the approved task specifications. Collectively they
MUST demonstrate:

1. **Clean build:** a documented command succeeds from a clean checkout using
   only declared inputs and produces the expected boot artifact.
2. **Bounded launch:** the QEMU command is noninteractive, has a finite external
   timeout, and records the command/configuration used.
3. **Heartbeat:** the supported boot path emits a deterministic, machine-readable
   early heartbeat on the captured serial channel.
4. **Success classification:** a positive fixture emits the required success
   evidence and an explicit successful terminal signal.
5. **Failure classification:** an intentional panic/fatal fixture emits bounded
   panic evidence and an explicit failing terminal signal.
6. **False-positive resistance:** missing markers, contradictory markers,
   timeout, QEMU launch failure, unexpected exit, and runner interruption cannot
   be classified as success.
7. **Repetition:** the positive and negative paths pass for the repetition count
   stated in their task specs without manual interaction.
8. **Auditability:** CI retains serial output, harness classification, relevant
   build metadata, and failing artifacts long enough for review.
9. **Safety review:** every unsafe operation and privileged/hardware boundary is
   mapped to its contract and relevant [invariants](INVARIANTS.md), with focused
   review evidence.
10. **Scope proof:** the final diff contains no out-of-scope subsystem
    implementation and no unresolved architectural decision hidden in code.

### Sprint 0 exit criteria

Each Sprint 0 task is proven against its own exact candidate. Sprint 0 exits only
when all task criteria are closed, all material choices have Accepted ADRs, and
the complete cumulative mandatory suite is rerun by the canonical local commands
and required CI jobs against one final integrated commit identified by every
milestone artifact. No known failure may be waived by vote. The resulting
foundation MUST allow a reviewer to distinguish build failure, launch failure,
no boot, heartbeat then hang, panic, explicit test failure, and clean success
from captured evidence alone.

## After Sprint 0

Post-Sprint 0 architecture and sequencing are intentionally uncommitted. Memory
management, interrupt/time facilities, execution, isolation, drivers, storage,
networking, and userspace each require their own evidence-backed proposals and
ADRs. Completion of Sprint 0 authorizes drafting those proposals; it does not
pre-approve any design or implementation.

This document SHOULD be extended one gated milestone at a time. New milestones
MUST state scope, exclusions, prerequisites, observable exit evidence, and stop
conditions before implementation begins.
