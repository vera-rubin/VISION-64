# VISION-64 Verification and Testing Standard

## Purpose and authority

Testing exists to produce reproducible evidence about one exact candidate, not
to create confidence by activity. This document governs acceptance tests, host
tooling, QEMU execution, serial evidence, debug-exit classification, and CI. It
implements the evidence and failure obligations in
[INVARIANTS.md](INVARIANTS.md), especially V64-GOV-003, V64-GOV-004,
V64-BLD-001, V64-FAIL-001, V64-OBS-001, and V64-PANIC-001.

An Accepted ADR selects any architectural mechanism used by a test. An approved
[task specification](tasks/0000-template.md) freezes the exact acceptance
procedure for its candidate. Neither this document nor a passing harness
authorizes kernel functionality outside [ROADMAP.md](ROADMAP.md).

Normative terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY**
follow RFC 2119.

## Acceptance contract

Before implementation, every task MUST give each acceptance criterion a stable
ID and record all of the following:

- the invariant, Accepted ADR, or requirement that the criterion demonstrates;
- the immutable base revision and permitted paths;
- exact noninteractive commands, working directory, declared inputs, toolchain
  versions, features, target, and configuration;
- preconditions and fixtures, including a negative fixture where false-positive
  resistance matters;
- literal expected markers or a fully anchored parser rule, expected process and
  guest terminal statuses, and the complete pass predicate;
- wall-clock timeout, heartbeat deadline when applicable, repetition count, and
  retry policy;
- exact artifact names and the evidence fields that must be retained;
- an objective pass/fail rule and the rollback or stop condition.

Words such as “boots,” “works,” “looks correct,” or “tests pass” are not an
acceptance contract. Commands MUST be copied literally into the task spec or
name a versioned repository script with all arguments fixed. A verifier MUST NOT
invent flags, repair the checkout, select a different tool version, or weaken an
expected result during a run.

Every criterion receives one of four states: `pass`, `fail`, `blocked`, or
`not-run`. Only `pass` advances. A skipped check, absent artifact, stale result,
runner loss, unexplained retry, or ambiguous observation is never a pass.

## Evidence package

Evidence MUST identify the candidate independently of a branch name. At minimum
the package contains:

- base and candidate commit object IDs and a clean-checkout status;
- task ID, criterion IDs, assigned implementer and independent verifier roles;
- host operating system, relevant hardware/virtualization facts, and exact
  versions of Rust, Cargo, QEMU, the linker, and orchestration tools;
- exact commands in execution order, sanitized environment/configuration, start
  and finish times, duration, and exit status for every command;
- unedited stdout, stderr, serial bytes, parser/classifier output, and timeout or
  signal information;
- hashes of the boot artifact, test fixtures, configuration, and evidence files;
- a criterion-to-artifact result map, including failures and contradictory
  observations.

Evidence is written outside disposable worktrees, uses stable filenames, and is
immutable after the verifier signs off. Secrets MUST be omitted or redacted at
capture; redaction MUST NOT hide behavior material to the result. Failed runs are
retained alongside successful runs. Rerunning a failure creates a new attempt;
it does not replace the first evidence package.

For Sprint 0 QEMU cases, the canonical package layout is:

```text
evidence/<task-id>/<candidate-commit>/<case-id>/run-<NN>/
  build.log
  build-result.env
  tool-versions.txt
  artifact.sha256
  qemu.argv
  qemu.stdout.log
  qemu.stderr.log
  serial.log
  terminal.env
  classification.env
  SHA256SUMS
```

The task spec MAY require additional files but MUST NOT rename or omit these.
`qemu.argv` records one shell-escaped argument per line; it is evidence, never a
string to execute with `eval`.

## Test layers

Checks are cumulative and proportional to risk:

1. **Static repository checks:** formatting, documentation links, dependency and
   license policy, generated-file drift, shell syntax/lint, workflow lint, and
   invariant/ADR/task references.
2. **Host unit tests:** pure parsers, state machines, arithmetic, encoders, and
   harness classification run without privileged target execution.
3. **Compile-time checks:** all supported targets/configurations build from a
   clean checkout; warnings and lints follow the task's frozen policy.
4. **Component tests:** boundary behavior, invalid inputs, error paths, and
   ownership/lifecycle transitions are exercised with controlled fixtures.
5. **Emulated-system tests:** a clean artifact boots in the pinned QEMU
   configuration, emits required serial evidence, and terminates through the
   approved test-exit mechanism.
6. **Fault and regression tests:** intentional panic/fatal behavior, missing or
   malformed markers, unexpected exit, and timeout paths prove that the harness
   cannot manufacture success.

A compile is not a boot test. A boot heartbeat is not clean completion. A unit
test of a host-side model is not proof of a privileged target operation.

Changes containing `unsafe`, assembly, privileged instructions, ABI boundaries,
interrupt context, or MMIO require focused tests of every documented
precondition and failure edge plus a line-by-line safety review. Tests cannot
prove Rust soundness; the `SAFETY:` argument and boundary contract remain
mandatory.

## QEMU execution standard

The canonical harness MUST construct an argument array directly and launch QEMU
without `eval`, an interactive shell, or text copied from an issue. The approved
task and ADR freeze the QEMU binary/version and every argument, including machine,
CPU, memory, firmware/boot artifact, serial sink, and debug-exit device.

Sprint 0 launches MUST:

- be headless and noninteractive (`-display none` and `-monitor none`, or a
  reviewed equivalent);
- dedicate an un-multiplexed serial channel to a raw artifact;
- disable automatic reboot and shutdown so reset cannot masquerade as progress;
- configure no network device or host sharing;
- use read-only inputs or a fresh per-run writable overlay;
- run from a clean checkout with no undeclared host files;
- be enclosed by a host-side TERM-then-KILL timeout independent of the guest;
- preserve QEMU stdout, stderr, serial output, argv, process status, and timeout
  state even when launch fails.

The Sprint 0 default hard timeout is 30 seconds per QEMU invocation, with the
heartbeat due within 10 seconds. A task MAY tighten these values. It MAY lengthen
them only with a recorded reason and review. Positive boot and intentional-fatal
cases each run three consecutive times in CI; any disagreement makes the case
fail as nondeterministic. There are no automatic success-only retries.

The harness MUST distinguish these terminal classes from captured evidence:

| Class | Required observation | Acceptance meaning |
| --- | --- | --- |
| `build-failure` | Build command fails or required artifact/hash is absent | Fail |
| `launch-failure` | QEMU cannot start or rejects its configuration | Fail |
| `no-boot` | Hard timeout before the required heartbeat | Fail |
| `heartbeat-hang` | Heartbeat occurs, then hard timeout before a terminal result | Fail |
| `panic` | Panic/fatal marker outside an intentional-fatal fixture | Fail |
| `expected-panic` | Intentional-fatal fixture emits its complete bounded panic evidence and assigned failing guest status | Pass only for that negative criterion |
| `explicit-failure` | Failure marker or assigned failing guest status | Fail |
| `clean-success` | Required ordered markers and assigned success status agree, with no failure/panic/timeout | Pass |
| `contradictory` | Success and failure evidence disagree, duplicate terminal markers conflict, or status is unassigned | Fail |
| `runner-loss` | Job cancellation, runner disconnect, or evidence truncation prevents classification | Blocked or fail; never pass |

Unknown output and unknown exit codes fail closed. Classification is computed
after process termination from preserved raw evidence. A log parser crashing or
accepting a partial line is a harness failure.

## Serial evidence standard

Serial is the primary Sprint 0 observation channel. The Accepted diagnostics ADR
and task spec MUST freeze the literal byte encoding, line terminator, protocol
version, ordered heartbeat/success/failure/panic markers, and any escaping or
field grammar before implementation. Until that decision is Accepted, no serial
marker is canonical and Sprint 0 runtime acceptance cannot begin.

The frozen format MUST satisfy these constraints:

- ASCII-compatible, line-delimited, bounded records suitable for byte-for-byte
  capture without terminal control sequences;
- an unambiguous protocol/version prefix and event class;
- exactly one terminal class per run; duplicate identical terminal records are a
  protocol error unless the ADR explicitly proves idempotence;
- deterministic fields for acceptance decisions; addresses, timing, and other
  unstable diagnostics may be additional fields but cannot be required for a
  byte-identical pass;
- heartbeat precedes terminal success; panic/fatal is distinguishable from an
  ordinary test failure and remains useful if later diagnostics are truncated;
- a streaming parser with bounded line and file sizes. Oversized, malformed,
  out-of-order, or truncated records fail closed.

The harness MUST search complete parsed records, not substring-match prose.
Serial output alone cannot prove completion because the guest may print a marker
and then hang; it must agree with the terminal mechanism.

## Debug-exit standard

Sprint 0 uses QEMU's test-only debug-exit mechanism only after an Accepted ADR
fixes the device, I/O address/width, write semantics, guest status values, and
host status mapping. The mapping table is copied verbatim into each applicable
task. Production control flow MUST NOT depend on this emulator-only mechanism.

For `isa-debug-exit`, QEMU reports host process status `(guest_value << 1) | 1`,
subject to host exit-status width. The selected guest values MUST yield distinct
success and failure statuses and MUST avoid collision with the harness's launch,
timeout, and signal statuses. The harness decodes the configured mapping; it
MUST NOT assume that process status zero means guest success.

A `clean-success` requires all of the following:

1. the expected artifact was launched;
2. the ordered heartbeat and success records were captured completely;
3. no panic or failure record was observed;
4. QEMU terminated before the hard timeout;
5. the decoded debug-exit status is the single assigned success value.

An intentional-fatal test passes only when the required panic evidence and the
assigned non-success debug-exit status agree. A success marker followed by a
failure status, a pass status without complete serial evidence, a normal QEMU
exit without debug-exit proof, or any unassigned status is `contradictory` and
fails.

## Continuous integration

Required checks MUST run against the exact candidate commit and report that
object ID. CI definitions and executable actions are part of the trusted build
surface and require review. Workflows MUST use:

- least-privilege `GITHUB_TOKEN` permissions, job timeouts, bounded concurrency,
  and immutable full-SHA pins for third-party actions;
- `persist-credentials: false` unless a separately authorized publishing job
  needs a credential;
- environment variables for validated event metadata rather than direct shell
  interpolation, and arrays rather than assembled command strings;
- artifact upload on failure as well as success, with an explicit retention
  period and no secrets in captured logs;
- separate credentials and jobs for patch production versus any PR publication.

Repository-controlled build/test code MUST NOT receive repository, cloud, SSH,
signing, or deployment secrets. A persistent self-hosted runner MUST NOT execute
untrusted fork/PR code or a mutable foreign ref. `pull_request_target` MUST NOT
check out or run contributor code. Privileged runner access, nested
virtualization, network access, or secret-bearing publication requires a
separate reviewed threat model and workflow.

The required Sprint 0 CI sequence is static policy checks, clean reproducible
build, host tests, three positive QEMU runs, three intentional-fatal QEMU runs,
classifier negative fixtures, evidence integrity verification, and an
independent scope/unsafe review. Later jobs MUST NOT turn a failed earlier gate
green by skipping it.

## Gate F orchestration smoke

The harmless factory smoke is deliberately smaller than a Sprint 0 test. It
proves checkout, input validation, worktree isolation, structural verification,
cleanup, and artifact transport only. It MUST be detached, branchless,
agentless, mutation-free, and must not build, boot, or edit kernel code.

The canonical entry point is:

```text
./scripts/forge-dispatch.sh --repo-root <absolute-repository-root> --work-root <absolute-temporary-root-outside-repository> --job-id <safe-unique-id> --base-ref <full-commit-id> --mode smoke --agent none
```

The deterministic local positive/negative check is `bash
scripts/test-forge-dispatch.sh`. It creates only a verified temporary work root,
never invokes an agent, checks the evidence hashes, and proves that repository
status, local branches, and the worktree registry are unchanged afterward.

The workflow `.github/workflows/forge-dispatch-smoke.yml` fixes these values from
trusted workflow metadata, runs only for this repository's default branch, has a
ten-minute job timeout, grants contents read only, persists no checkout
credential, and invokes neither agent adapter. The pre-existing
`vision-runner-smoke.yml` remains an independent runner-capability check and its
behavior is not replaced.

Each smoke attempt retains these deterministic evidence files:

```text
dispatch-manifest.env
environment.txt
create-worktree.stderr.txt
git-status.txt
candidate.patch
changed-paths.txt
diff-check.txt
verification.env
verification-output.txt
verification-stderr.txt
dispatch-result.env
SHA256SUMS
```

The empty status, patch, and changed-path files plus `head_state=detached`, equal
base/head commits, `agent=none`, successful cleanup, and matching checksums are
the Gate F proof. Missing evidence fails the smoke.

Before enabling issue-triggered execution, negative tests MUST also prove that
unknown flags, malformed IDs, symbolic refs, path traversal, work roots that
overlap the repository, pre-existing worktree/evidence paths, noncanonical task
specs, mode/agent mismatches, and absent per-job execution gates all fail before
an agent starts. Issue bodies and comments remain data and are never evaluated.
During the current bootstrap gate, the dispatcher and both adapters accept only
documentation-path allowlists (`docs/`, `AGENTS.md`, `CLAUDE.md`, or
`README.md`); every implementation path fails before agent launch. Enabling
Sprint 0 implementation requires a separately reviewed dispatch-policy change
after its entry gate and tasks are approved.

## Sprint 0 acceptance and exit

Sprint 0 may begin only after the required diagnostics and debug-exit ADRs are
Accepted and their exact commands, marker registry, status mapping, fixtures,
and artifact hashes are frozen in approved tasks. Its complete evidence set MUST
demonstrate:

1. a clean declared-input build of the expected artifact;
2. a bounded noninteractive QEMU launch;
3. the earliest approved serial heartbeat;
4. three clean-success repetitions;
5. three bounded intentional-panic/fatal repetitions;
6. classifier rejection of no-boot, heartbeat-hang, missing marker, malformed or
   contradictory marker, unexpected exit, launch failure, timeout, and truncated
   evidence fixtures;
7. panic-path independence from allocation, scheduler progress, and unsafe lock
   acquisition, supported by review and focused tests;
8. traceability of every unsafe/privileged operation to its `SAFETY:` argument,
   boundary contract, invariant, ADR, and acceptance evidence;
9. CI reproduction with intact hashes and no manual intervention;
10. a final diff review proving that memory management, interrupts/APIC, timers,
    scheduling, processes/userspace, general drivers, storage, networking, and
    other post-Sprint-0 architecture were not implemented.

Sprint 0 exits only when every approved task criterion passes for the same exact
candidate, every required review finding is resolved, and captured evidence
alone lets an independent reader distinguish build failure, launch failure, no
boot, heartbeat then hang, panic, explicit failure, and clean success. Votes,
agent confidence, an unrelated green job, or compilation alone cannot close the
milestone.
