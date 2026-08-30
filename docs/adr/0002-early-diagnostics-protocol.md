# ADR 0002: Define the Early Diagnostics Protocol

- **Status:** Proposed
- **Date:** 2026-08-29
- **Owners:** VISION-64 maintainer
- **Decision scope:** Early diagnostics, panic observability, and x86-64 serial
  mechanism containment for Sprint 0
- **Related task(s):**
  [`docs/tasks/1-establish-observable-boot-heartbeat.md`](../tasks/1-establish-observable-boot-heartbeat.md)
- **Related invariants:** V64-GOV-002, V64-BLD-001, V64-INIT-001,
  V64-OWN-001, V64-FAIL-001, V64-OBS-001, V64-PANIC-001,
  V64-BND-002, V64-ARCH-001, V64-DEP-001, V64-SAFE-001,
  V64-SAFE-002, V64-SAFE-003
- **Supersedes:** None
- **Superseded by:** None
- **Approval authority:** Independent VISION-64 maintainer; no author or
  implementation worker may self-approve
- **Approval evidence:** Pending independent review and protected-main merge;
  this proposed blob has no authority on its branch

## Decision summary

Task 1 owns one allocation-free, polling COM1 diagnostics channel. After a
fixed initialization sequence, VISION emits only three exact, line-feed
terminated ASCII records: `VISION64/1 HEARTBEAT`, `VISION64/1 SUCCESS`, and
`VISION64/1 PANIC`. The positive path emits heartbeat then success; the
intentional-failure path emits heartbeat then panic. Each transmitted byte has
a fixed polling bound. Panic output uses no allocator, formatting engine, lock,
interrupt, or later kernel service and then transfers to the separate bounded
terminal mechanism in ADR 0003.

## Context and problem

Sprint 0 treats observability as part of correctness. A booting guest that
hangs silently cannot distinguish entry failure, diagnostics failure, panic,
or completion. The first slice therefore needs a minimal channel that works
before an allocator, interrupt controller, scheduler, framebuffer, or general
logging framework exists. Its success and failure records must be impossible
to confuse with bootloader output or partial progress.

Task 1 runs on one virtual CPU with interrupts left disabled. That permits a
small single-owner polling implementation without prematurely selecting a
locking, interrupt-safety, buffering, or multi-CPU logging design. The protocol
is deliberately narrower than a future diagnostics subsystem.

## Constraints and decision drivers

In priority order:

1. Make entry, successful completion, and intentional panic objectively
   distinguishable in raw retained evidence.
2. Keep panic observability independent of allocation, formatting, locks,
   interrupts, scheduling, and framebuffer state.
3. Bound all hardware polling so a broken serial device cannot make a claimed
   terminal path unbounded.
4. Contain privileged x86-64 port I/O behind the architecture boundary with a
   complete unsafe justification.
5. Avoid creating a general logger, stable public kernel API, or future
   concurrency policy in Task 1.

Non-goals are formatted panic details, log levels, buffering, timestamps,
Unicode, input, runtime device discovery, multiple serial devices, interrupt-
driven I/O, SMP safety, and non-x86-64 transport.

## Options considered

### Option A — Fixed polling COM1 records

- **Description:** Initialize the legacy COM1 UART directly, poll transmitter
  readiness with a fixed bound, and emit exact protocol records.
- **Benefits:** Available at the first Rust instruction; tiny state and proof
  surface; raw output is easy to retain and classify; panic has no service
  dependencies.
- **Costs and risks:** x86-64 and QEMU-specific; polling is slow; real hardware
  discovery and concurrency are intentionally absent.
- **Invariant impact:** Creates a small V64-SAFE-002/V64-SAFE-003 proof surface
  under V64-ARCH-001 and directly supports V64-OBS-001/V64-PANIC-001.
- **Evidence required:** Unsafe inventory, register-sequence review, exact raw
  serial logs, negative fixtures, and bounded-failure tests.

### Option B — Use bootloader diagnostics

- **Description:** Accept bootloader serial or framebuffer output as the boot
  heartbeat and failure channel.
- **Benefits:** Less VISION code in the first slice.
- **Costs and risks:** Does not prove VISION kernel entry, gives a dependency
  ownership of canonical evidence, and cannot provide the required independent
  panic path.
- **Invariant impact:** Cannot establish V64-OBS-001 or V64-PANIC-001 for
  VISION-owned code.
- **Evidence required:** No available evidence can make bootloader text prove
  that the Rust entry executed.

### Option C — Introduce a general logging framework now

- **Description:** Add formatting, levels, global synchronization, multiple
  sinks, and a reusable logging API.
- **Benefits:** More features for later development.
- **Costs and risks:** Prematurely selects allocation, ownership, concurrency,
  and failure behavior; expands the panic dependency graph.
- **Invariant impact:** Adds unnecessary V64-OWN-001, V64-CON-001, and
  V64-PANIC-001 obligations.
- **Evidence required:** Broader proof than the first heartbeat needs.

## Decision

Choose Option A with this exact Task 1 contract:

- Device: COM1 at x86 I/O base `0x03f8`, divisor `1` for 115200 baud, eight
  data bits, no parity, one stop bit (8N1).
- Initialization writes, in order: interrupt-enable `0x00`; line-control
  `0x80`; divisor low `0x01`; divisor high `0x00`; line-control `0x03`;
  FIFO-control `0xc7`; modem-control `0x03`. Task 1 does not enable UART or CPU
  interrupts.
- A byte may be written only after line-status bit `0x20` is observed. Each byte
  receives at most 65,536 line-status reads. Exhaustion is an error, never
  success, and no unbounded retry is allowed.
- Records are literal ASCII bytes with one LF byte (`0x0a`) and no CR:

  ```text
  VISION64/1 HEARTBEAT\n
  VISION64/1 SUCCESS\n
  VISION64/1 PANIC\n
  ```

- A positive guest emits exactly `HEARTBEAT` then `SUCCESS`. The intentional-
  panic guest emits exactly `HEARTBEAT` then `PANIC`. Missing, extra,
  duplicated, reordered, malformed, truncated, or contradictory protocol
  records fail classification.
- `HEARTBEAT` means VISION reached the Rust kernel entry and completed COM1
  initialization. Firmware or bootloader output cannot satisfy it; ADR 0001
  disables bootloader serial and framebuffer logging.
- The normal entry path uniquely owns diagnostics until it intentionally
  invokes panic. The panic handler then takes terminal ownership. Because Task
  1 is single-CPU and never enables interrupts, no concurrent caller exists.
  The implementation uses no mutable static and no lock; the private call graph
  and terminal control transfer enforce this bounded ownership model.
- The panic handler emits only the fixed panic record. It does not format panic
  payloads, allocate, lock, recurse, unwind, or call a non-terminal service.
- If initialization or any serial write fails, the guest must not emit a
  success record. It attempts the ADR 0003 failure exit and otherwise remains
  in a bounded halt loop; host timeout and incomplete serial remain failure.

The architecture-specific `in`/`out` mechanism lives only under
`kernel/src/arch/x86_64/`. Safe higher-level code cannot choose arbitrary ports
or fabricate an initialized UART.

## Contract and boundary impact

- **Diagnostics and recovery:** Owns initialization and the three records. It
  exposes only the operations needed for Task 1, not a general logger.
- **Architecture mechanisms:** Owns COM1 register constants and minimal x86-64
  port-I/O wrappers. No architecture-neutral module contains inline assembly or
  port numbers.
- **Boot and composition:** Calls diagnostics once after Rust entry; it does not
  supply output itself.
- **Panic path:** Takes terminal diagnostics ownership and never returns.
- **Ownership/lifecycle:** One statically known device is initialized once and
  has one sequential owner for the life of Task 1.
- **Allocation/blocking/concurrency:** No allocation or locks. Polling is
  bounded. One CPU is used and interrupts remain disabled.
- **Errors/partial progress:** Serial failure is observable to the classifier as
  a missing or truncated required record and can never be promoted to success.

## Safety, security, and unsafe-code impact

The only VISION-owned unsafe operations authorized by this ADR are one-byte
port input/output primitives implemented with minimal inline x86-64 assembly.
ADR 0003 separately owns its 32-bit debug-exit output. Each byte operation
must document that the caller supplies a port whose access width and device
semantics are valid, and must use compiler options that preserve volatile I/O
ordering. Arbitrary port access is not exposed through a safe public API.

The UART driver is safe only because it fixes the device, register widths,
initialization order, private call sites, single ownership, interrupt state,
absence of mutable static state, and polling bound. A
focused reviewer must verify the unsafe block, generated instruction width,
register offsets, assembly options, and all safe call sites. The task does not
claim soundness for later concurrency, interrupts, SMP, or physical hardware.
Unwinding is disabled and no panic crosses a subsystem or boot boundary.

## Verification and acceptance evidence

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| VISION owns the first canonical record | Raw `serial.log`, image configuration, and kernel entry review | First and only positive-path records are exact heartbeat then success; bootloader output is disabled |
| Panic remains independently observable | Raw intentional-panic `serial.log` and focused call-graph review | Exact heartbeat then panic; no success; panic path has no allocator, formatting, lock, interrupt, or scheduler dependency |
| Polling is bounded | Source review plus classifier fixtures and timed QEMU runs | Every byte has the 65,536-read limit; incomplete output or 30-second host timeout fails |
| Architecture-specific unsafe is contained | Unsafe inventory and x86-64 I/O review | No port I/O outside `kernel/src/arch/x86_64`; every unsafe operation has a local SAFETY proof; safe callers cannot select ports |
| False positives are rejected | Host classifier unit and fixture tests | Missing, extra, reordered, malformed, contradictory, and truncated records all return nonzero |

## Consequences

### Positive

- The first kernel progress and panic are visible without depending on any
  later kernel service.
- Exact small records make positive and negative evidence mechanically
  classifiable.
- Hardware-specific unsafe remains narrow and replaceable.

### Negative and tradeoffs

- This protocol is intentionally sparse and COM1/QEMU-specific.
- Polling consumes CPU while transmitting, though the work is fixed and tiny.
- The single-owner assumption is valid only for the bounded Task 1 execution
  model.

### Follow-up work

- A later accepted task may design a general diagnostics interface, richer
  records, concurrency, or another transport. None is authorized here.

## Rollout, compatibility, and reversal

Task 1 introduces the driver, exact records, classifier, and tests together.
Rollback reverts the Task 1 implementation and removes its generated evidence;
no persistent format or external compatibility promise remains. Any change to
record bytes, initialization sequence, polling bound, ownership model, or
transport requires GENESIS and an ADR update or superseding ADR.

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Roadmap](../ROADMAP.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)
- [Temporary BIOS boot contract](0001-temporary-bios-boot-contract.md)
- [QEMU terminal-status contract](0003-qemu-terminal-status.md)

## Decision log

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| 2026-08-29 | Proposed | Defines only the serial observability needed by bounded Task 1 | Pending |
