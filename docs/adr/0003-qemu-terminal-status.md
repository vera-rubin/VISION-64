# ADR 0003: Define QEMU Terminal Status for Sprint 0

- **Status:** Proposed
- **Date:** 2026-08-29
- **Owners:** VISION-64 maintainer
- **Decision scope:** QEMU-only terminal signaling, host status mapping, bounded
  execution, and evidence classification for Sprint 0
- **Related task(s):**
  [`docs/tasks/1-establish-observable-boot-heartbeat.md`](../tasks/1-establish-observable-boot-heartbeat.md)
- **Related invariants:** V64-GOV-002, V64-GOV-003, V64-GOV-004,
  V64-GOV-006, V64-BLD-001, V64-FAIL-001, V64-OBS-001,
  V64-PANIC-001, V64-ARCH-001, V64-SAFE-002, V64-SAFE-003
- **Supersedes:** None
- **Superseded by:** None
- **Approval authority:** Independent VISION-64 maintainer; no author or
  implementation worker may self-approve
- **Approval evidence:** Pending independent review and protected-main merge;
  this proposed blob has no authority on its branch

## Decision summary

Sprint 0 uses QEMU's `isa-debug-exit` device at I/O port `0x00f4` with a
32-bit guest write. Guest value `0x10` maps to host process status `33` and is
the sole success status; guest value `0x11` maps to host status `35` and is the
intentional-panic/failure status. These statuses are accepted only when they
agree with the exact serial protocol in ADR 0002. Each QEMU process is enclosed
by a host-side 30-second TERM-then-KILL boundary, with heartbeat due by 10
seconds, and all unknown, normal, signaled, or timed-out terminations fail
closed.

## Context and problem

A serial success record does not prove that the guest reached a terminal state;
it could print and hang. Conversely, a QEMU process status without the expected
serial history does not prove which guest path ran. Sprint 0 therefore needs an
explicit emulator-only terminal signal, a collision-free host mapping, and a
classifier that requires both independent observations to agree.

The current constitution explicitly requires a debug-exit ADR before Sprint 0
TEMPER. It also requires headless, isolated, bounded QEMU execution and rejects
timeout, launch failure, unexpected exit, missing evidence, and contradictory
evidence. Task 1 does not yet have an interrupt controller, ACPI shutdown path,
triple-fault classifier, or production power-management contract.

## Constraints and decision drivers

In priority order:

1. Produce distinct explicit host statuses for clean success and intentional
   panic without treating process status zero as guest success.
2. Require terminal status and complete ordered serial records to agree.
3. Bound hangs independently of all guest code and preserve evidence on every
   exit path.
4. Keep the mechanism test-only and architecture-contained so production
   control flow cannot depend on QEMU.
5. Freeze a deterministic, noninteractive, offline QEMU configuration with no
   network, host sharing, writable boot input, or shell re-parsing.

Non-goals include hardware shutdown, ACPI, reboot policy, watchdogs, production
exit codes, other emulators, hardware acceleration, SMP, and CI workflow design.

## Options considered

### Option A — QEMU `isa-debug-exit` plus serial agreement

- **Description:** Write fixed guest values to the configured QEMU test device
  and require the resulting host status to agree with exact serial records.
- **Benefits:** Explicit and fast terminal proof; distinct success/failure
  statuses; small guest mechanism; deterministic under TCG.
- **Costs and risks:** Emulator-specific port I/O; QEMU encodes rather than
  directly returns the guest value; ordinary host exit statuses must be rejected.
- **Invariant impact:** Adds a narrow V64-ARCH-001/V64-SAFE-002 mechanism and
  directly supports V64-FAIL-001 and V64-OBS-001.
- **Evidence required:** Mapping tests, exact argv, raw process status, serial
  logs, timeout state, and negative classifier fixtures.

### Option B — Serial marker followed by halt or timeout

- **Description:** Print a terminal record and leave the guest halted until the
  host timeout kills QEMU.
- **Benefits:** No test-exit device or guest I/O operation.
- **Costs and risks:** Makes clean completion indistinguishable from a hang and
  treats timeout as expected behavior.
- **Invariant impact:** Violates V64-FAIL-001 and the TESTING requirement that
  clean success terminate through an assigned status.
- **Evidence required:** Cannot provide the missing terminal distinction.

### Option C — Guest poweroff, reset, or fault as status

- **Description:** Use ACPI shutdown, reset, triple fault, or another ordinary
  machine termination.
- **Benefits:** Could resemble later machine lifecycle behavior.
- **Costs and risks:** Prematurely requires unowned platform mechanisms; QEMU's
  ordinary termination can also result from an unrelated fault or configuration
  error.
- **Invariant impact:** Expands privileged scope and permits false positives.
- **Evidence required:** Platform initialization and fault-disambiguation proof
  outside Task 1.

## Decision

Choose Option A with the following frozen mapping:

| Guest action | Guest value | QEMU mapping `(value << 1) \| 1` | Meaning |
| --- | ---: | ---: | --- |
| 32-bit `out` to port `0x00f4` | `0x10` | `33` | Assigned clean-success status |
| 32-bit `out` to port `0x00f4` | `0x11` | `35` | Assigned intentional-panic/failure status |

The verification host input is Debian package `qemu-system-x86`
`1:10.0.11+ds-0+deb13u1`; `/usr/bin/qemu-system-x86_64` must have SHA-256
`184914c77ba4074281a6e7bd5d1959f0115abb553688a8c8f02940627ad197fa`.
The explicit firmware is package `seabios` `1.16.3-2` at
`/usr/share/seabios/bios-256k.bin`, SHA-256
`fc6d2ea888862e6b26d53fb877ab712324726eb8f44eb6baf076c64a31f1c3fb`.
The corresponding official Debian package archives have SHA-256
`ffc742bf02b818376f67ebd2bdb73b5add6239a6ea8d09557f6519b4ff0bb746`
and `2b590534250b940f43222eeab9a8f57f337a9d9a73fc412a43ab8cd07a7e56f6`.
Any mismatch blocks VERIFY rather than selecting another host input.

The QEMU binary receives this exact argument array, with the three named
per-run values resolved before launch:

```text
/usr/bin/qemu-system-x86_64
-no-user-config
-nodefaults
-machine
pc,accel=tcg
-cpu
qemu64
-smp
1
-m
64M
-display
none
-vga
none
-monitor
none
-serial
file:$VISION_SERIAL_LOG_ABS
-no-reboot
-net
none
-L
$VISION_QEMU_DATA_DIR_ABS
-bios
/usr/share/seabios/bios-256k.bin
-drive
if=ide,format=raw,readonly=on,file=$VISION_IMAGE_ABS
-boot
order=c,strict=on
-device
isa-debug-exit,iobase=0xf4,iosize=0x04
```

`VISION_SERIAL_LOG_ABS`, `VISION_IMAGE_ABS`, and
`VISION_QEMU_DATA_DIR_ABS` name per-run values that the harness has already
resolved and validated as absolute paths. Each real path must match
`^/[A-Za-z0-9._/-]+$`, remain below its declared run root, and contain no comma,
whitespace, control byte, backslash, or symlink component. The QEMU data
directory is newly created and empty. These names are not environment strings
evaluated by a shell. The safe alphabet also makes the retained one-argument-
per-line `qemu.argv` representation unambiguous and prevents comma-delimited
`-drive` option injection. The harness launches this array directly. It must
not use `eval`, interpolate
issue or comment text, add a network or host-share device, or mutate the disk
image. QEMU stdout and stderr are separately retained.

QEMU runs under an empty environment except fixed `HOME` and `XDG_CONFIG_HOME`
directories below the run root and `LANG=C.UTF-8`, `LC_ALL=C.UTF-8`, and
`TZ=UTC`. Both configuration homes are newly created and empty. Preflight
records and hashes the QEMU binary, firmware, `--version`, Debian package
versions, dynamic-library paths/hashes, and the empty data/config directories.

Each invocation has a 30-second hard host timeout. The heartbeat is due within
10 seconds. At the hard timeout the harness records the timeout, sends TERM,
waits only its fixed cleanup grace interval, sends KILL if needed, reaps the
process, retains all partial evidence, and fails the case. No retry can convert
that result into success. Positive and intentional-panic cases each run three
consecutive times.

The positive case accepts status `33` only with exactly heartbeat then success
and no panic. The intentional-panic case accepts status `35` only with exactly
heartbeat then panic and no success. Any other status—including zero, an
unassigned odd value, a signal-derived value, launch failure, or ordinary QEMU
shutdown—is failure or contradiction. Marker/status disagreement is always
failure.

Task 1 uses `-no-reboot` and deliberately omits `-no-shutdown`. The latter
causes QEMU to pause instead of terminating when `isa-debug-exit` requests
shutdown, which would erase the mapped host status and turn explicit completion
into timeout. TESTING explicitly requires that omission for `isa-debug-exit`
while preserving its fail-closed purpose: only the two mapped debug-exit
statuses can pass, and every ordinary, missing, or unassigned shutdown status
is rejected.

The guest exit module is compiled only under the `qemu-test-exit` feature. The
intentional-panic fixture requires that feature. Normal production control flow
must neither import nor require the device.

## Contract and boundary impact

- **Host tooling and verification:** Owns process launch, time measurement,
  TERM/KILL containment, status decoding, serial parsing, and evidence retention.
- **Architecture mechanisms:** Owns the fixed-width port write under
  `kernel/src/arch/x86_64/test_exit.rs` and exposes only the two terminal
  operations while the test feature is active.
- **Diagnostics and recovery:** Supplies records under ADR 0002; it does not
  decide pass/fail by itself.
- **Boot and composition:** Supplies the read-only image under ADR 0001; it does
  not own QEMU status interpretation.
- **Ownership/lifecycle:** The terminal operation is single-use and divergent;
  after the guest write, any continued execution enters a halt loop until the
  independent host timeout contains it.
- **Allocation/blocking/concurrency:** Target operation allocates and locks
  nowhere. Host waits are bounded. Task 1 remains one CPU with interrupts off.
- **Errors/partial progress:** Every incomplete, conflicting, unknown, or
  signaled observation is retained and classified non-success.

## Safety, security, and unsafe-code impact

The guest mechanism performs one privileged 32-bit x86 port output. Its private
`outl` primitive is owned by this ADR and implemented in the feature-gated test
exit module; it does not reuse or widen ADR 0002's byte-I/O authorization. It
documents that the port/device exists only in the frozen QEMU test configuration
and is unavailable without the test feature. A safe caller
cannot select the port, write an arbitrary value, or return after a claimed
terminal operation.

The host treats the candidate image, serial bytes, process status, environment,
and all paths as untrusted inputs. It constructs arguments from validated local
paths, never evaluates captured text, creates fresh per-run evidence locations,
and rejects symlinks or paths outside the declared roots. QEMU receives no
network or host filesystem sharing. No output can expand task scope or authority.

## Verification and acceptance evidence

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| Guest values map distinctly | Host classifier unit tests and three QEMU runs per case | `0x10` produces status 33 and only clean-success; `0x11` produces status 35 and only expected-panic |
| Serial and terminal observations agree | Raw `serial.log`, `terminal.env`, and `classification.env` | Exact assigned marker sequence and status agree; every mismatch is non-success |
| Execution is bounded | Start/finish times, timeout state, process status, and heartbeat timestamp | Heartbeat by 10 seconds and exit before 30 seconds; timeout preserves evidence and fails |
| Launch is isolated and reproducible | `qemu.argv`, sanitized environment, binary/firmware/package/library hashes, image hash, and clean-checkout record | Exact array and pinned hashes above; TCG, one CPU, empty config/data roots, explicit BIOS, no network/share/default devices, read-only image |
| False terminal evidence is rejected | Fixtures for zero, unassigned status, signal, launch failure, timeout, and contradictory/truncated evidence | Every fixture returns nonzero with the expected non-success class |
| Test-only mechanism is contained | Feature/build inspection and architecture review | Exit module absent without `qemu-test-exit`; no production dependency; fixed port/value API only |

## Consequences

### Positive

- Completion is explicit, bounded, and cross-checked against raw guest output.
- The mapping cannot confuse process status zero with guest success.
- Test-only privileged code is small and removable.

### Negative and tradeoffs

- The status contract is QEMU-specific and depends on its encoded process exit.
- The harness must preserve raw process state carefully before shell or signal
  handling can alter it.
- The mechanism requires QEMU to terminate for its explicit mapped status, so
  ordinary shutdown rejection belongs to the classifier rather than the
  `-no-shutdown` flag.

### Follow-up work

- Later machine shutdown, watchdog, and production fatal behavior require new
  tasks and decisions; this ADR supplies no precedent for them.

## Rollout, compatibility, and reversal

Task 1 introduces the feature-gated guest exit module, host classifier, and
QEMU harness together. Rollback reverts that task and removes per-run generated
evidence from its explicitly scoped evidence root. No on-disk or user-facing
format remains. A different emulator, device, port, width, mapping, QEMU
version, timeout, or production use requires GENESIS and an ADR amendment or
superseding ADR.

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Roadmap](../ROADMAP.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)
- [Temporary BIOS boot contract](0001-temporary-bios-boot-contract.md)
- [Early diagnostics protocol](0002-early-diagnostics-protocol.md)
- [Debian QEMU package](https://packages.debian.org/trixie/amd64/qemu-system-x86/download)
- [Debian SeaBIOS package](https://packages.debian.org/trixie/all/seabios/download)

## Decision log

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| 2026-08-29 | Proposed | Defines the bounded QEMU-only terminal contract required by Task 1 | Pending |
