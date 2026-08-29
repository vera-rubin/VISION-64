# VISION-64 Architecture Constitution

## Status and scope

This document defines the architectural constitution for VISION-64. It records
mission, design principles, logical subsystem boundaries, dependency direction,
and the process by which concrete architecture is selected. It deliberately does
not select a boot protocol, firmware interface, kernel organization, allocator,
paging model, interrupt controller, timer, scheduler, ABI, driver model, or file
system. Each such choice requires an accepted architecture decision record (ADR)
before implementation depends on it.

The boundaries below are contracts, not a prescribed source-tree, crate, address
space, or process layout. A future ADR MAY map several boundaries into one crate
or split one boundary across several crates, provided the contracts and
dependency rules remain intact.

Normative terms **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are
used as described by RFC 2119.

## Mission

VISION-64 exists to build a trustworthy 64-bit systems platform incrementally in
Rust. Its engineering process has three equal outputs:

1. a system whose behavior is understandable and testable;
2. explicit safety and architectural arguments that reviewers can challenge;
3. reproducible evidence that the implementation satisfies its stated contract.

Shipping more mechanisms is not progress if the mechanisms cannot be explained,
observed, or verified. VISION-64 therefore favors small auditable increments,
sharp interfaces, deterministic failure, and evidence over breadth or novelty.

## Design philosophy

### Contracts before mechanisms

A task MUST state the externally observable behavior and the invariants it must
preserve before selecting an implementation. Concrete mechanisms belong in ADRs
and task specifications, not in assumptions hidden in code.

### Evidence before confidence

Claims of correctness MUST be supported by reviewable evidence. A successful
build, a vote, or an agent's confidence is not proof of runtime behavior. The
required evidence is defined in [TESTING.md](TESTING.md) and the applicable task
specification.

### Minimize the trusted surface

Unsafe code, privileged instructions, raw hardware access, foreign interfaces,
and early-boot code form a high-risk boundary. They MUST be kept small, expose a
safe contract where one is possible, and carry explicit proof obligations. See
[INVARIANTS.md](INVARIANTS.md#unsafe-rust-policy).

### Make failure observable

Boot, panic, and test paths MUST produce enough out-of-band evidence to
distinguish success, assertion failure, panic, hang, emulator failure, and runner
failure. A timeout is containment, never a success signal.

### Prefer reversible increments

Changes SHOULD be small enough to review, test, and revert independently.
Temporary compatibility layers MUST name their removal condition. Irreversible
interfaces require stronger evidence and an ADR.

### Separate mechanism from policy

Low-level code SHOULD provide the smallest mechanism needed to uphold a contract.
Selection, fairness, allocation strategy, retry behavior, and other policy SHOULD
remain above that mechanism unless an ADR demonstrates that the separation is
unsafe or impractical.

### Isolate platform assumptions

Even when only one platform is supported, architecture-, firmware-, board-, and
emulator-specific facts MUST be contained behind explicit contracts. This is an
auditability rule, not a promise of portability.

## Sources of authority

Repository artifacts have the following precedence:

1. the constitutional rules in this document,
   [INVARIANTS.md](INVARIANTS.md), [ROADMAP.md](ROADMAP.md),
   [TESTING.md](TESTING.md), [FORGE.md](FORGE.md), and the repository-wide role
   restrictions in [AGENTS.md](../AGENTS.md);
2. accepted ADRs in `docs/adr/`;
3. approved task specifications in `docs/tasks/`;
4. implementation and tests.

The narrower artifact may refine the broader one but MUST NOT contradict it. On
a conflict, work stops until the broader artifact is amended or the narrower
artifact is corrected. Silence is not permission to invent an architectural
choice.

Status text in a branch or candidate is not authority. An ADR becomes Accepted,
or a task Approved, only when its exact blob is reachable from a remotely
verified protected authority ref (normally `main`) through the required
independent maintainer/CODEOWNER approval. The protected ref, authority commit,
artifact path, and blob object ID form the immutable authority tuple. Authors and
dispatched workers MUST NOT self-approve their governing artifact. If remote
branch protection/rulesets or the independent approval record cannot be verified,
authority is unavailable and work is blocked.

Role-specific guidance, including [CLAUDE.md](../CLAUDE.md), may further restrict
a worker but cannot weaken this order. Operational agent and review rules are in
[AGENTS.md](../AGENTS.md) and [FORGE.md](FORGE.md). Delivery gates and the
currently authorized scope are in [ROADMAP.md](ROADMAP.md).

## Logical subsystem boundaries

Each boundary owns a class of contracts. The table intentionally avoids naming
concrete implementations.

| Boundary | Owns | Must not silently own |
| --- | --- | --- |
| Foundation contracts | Minimal shared types and contracts needed to express identity, lifecycle, errors, capabilities, and effects | Device policy, scheduling policy, platform registers, or global service discovery |
| Boot and composition | Entry validation, ordered construction of initialized capabilities, and transfer into the steady-state system | General memory policy, long-lived device policy, or hidden fallback initialization |
| Architecture mechanisms | CPU state transitions, privileged operations, context representation, and architecture-defined barriers behind documented preconditions | Scheduling, allocation policy, device policy, or architecture-independent service semantics |
| Memory | Ownership and lifecycle of physical resources, address mappings, permissions, and safe access contracts | Process policy, device-specific allocation policy, or implicit ownership transfer |
| Interrupts and time | Interrupt delivery/dispatch contracts and clock/timer mechanisms | Scheduler fairness, device business logic, or wall-clock policy |
| Execution and synchronization | Units of execution, state transitions, blocking/waking contracts, and synchronization primitives | Interrupt-controller programming, device register access, or address-space policy not required by its contract |
| Device I/O | Discovery and access contracts, transport adapters, drivers, and explicit ownership of device resources | Scheduler policy, global memory policy, or undocumented access to platform internals |
| Protection and external interfaces | Validation and translation at trust, privilege, ABI, and user/kernel boundaries | Trusting caller-provided lengths, pointers, discriminants, permissions, or object lifetimes |
| Diagnostics and recovery | Structured observations, panic reporting, and terminal test signaling through narrow sinks | Normal control flow, hidden recovery policy, or a required dependency on fallible allocation during failure reporting |
| Host tooling and verification | Builds, image assembly, emulator control, evidence capture, and test orchestration | Production kernel policy or test-only behavior in production paths |

These are responsibility boundaries. They do not assert that every listed
capability exists today or authorize its implementation.

### Boundary contract requirements

Every cross-boundary contract MUST state, as applicable:

- who owns each resource and when ownership transfers;
- valid lifecycle states and initialization prerequisites;
- whether the operation may allocate, block, sleep, or fail;
- whether it is safe in interrupt, panic, or concurrent context;
- required ordering, atomicity, memory-ordering, and reentrancy properties;
- how errors and partial progress are represented;
- which invariants and accepted ADRs justify the contract.

Callers MUST depend on the declared contract, not on the callee's private layout,
global variables, register choices, or incidental ordering. A concrete
platform/driver type MUST NOT leak through a general contract unless an ADR makes
that coupling intentional.

## Dependency direction

In the rules below, “A depends on B” means A imports, calls, assumes the layout
of, or requires initialization side effects from B.

1. Foundation contracts MUST NOT depend on concrete subsystem implementations.
2. Architecture-independent policy MAY depend on subsystem contracts but MUST
   NOT depend directly on architecture, firmware, board, or emulator adapters.
3. Platform and device adapters MAY depend on foundation contracts and the
   minimum architecture mechanisms they implement or consume. General contracts
   MUST NOT depend back on those adapters.
4. Higher-level policy MAY depend on lower-level mechanisms. Lower-level
   mechanisms MUST NOT depend on higher-level policy.
5. The boot/composition boundary MAY know concrete implementations solely to
   construct, validate, and connect them. That knowledge MUST NOT become an
   implicit service locator used by other boundaries.
6. Diagnostics users MUST depend on a narrow observation contract. A concrete
   serial, emulator, or device-backed sink MAY depend on lower-level I/O; the
   observation contract MUST NOT.
7. Host tooling and test harnesses MAY depend on public artifacts and explicit
   test interfaces. Production code MUST NOT depend on host tooling or on
   test-only behavior.
8. Dependency cycles between logical subsystems are forbidden. An apparent cycle
   MUST be broken by extracting a smaller contract or the proposed boundary must
   return to constitutional review. An ADR may redraw boundaries only when the
   resulting dependency graph remains acyclic; it cannot waive acyclicity.

Hidden dependencies through mutable globals, linker side effects, build scripts,
environment variables, or initialization order count as dependencies and MUST be
documented.

## Third-party and tool dependency policy

Every new runtime, build, or CI dependency MUST have a reviewable reason. Its PR
MUST record:

- the capability it provides and why a smaller in-tree contract is insufficient;
- whether it executes on the host, is linked into the target, or both;
- its version/source pin and relevant feature flags;
- its `no_std`, target, license, maintenance, and supply-chain suitability;
- the presence and scope of transitive unsafe code, build scripts, procedural
  macros, native code, and network access;
- how the dependency is tested, updated, replaced, or removed.

Target-side code MUST NOT rely on a hosted standard library unless an ADR makes
that environment part of the architecture. Default features SHOULD be disabled
when they add unused capability. Git dependencies MUST use an immutable revision;
floating branches and unpinned downloadable executables are forbidden.

Executable dependencies—build scripts, procedural macros, installer scripts,
workflow actions, and downloaded tools—receive the same scrutiny as runtime
code. A convenience dependency MUST NOT expand the trusted surface without an
explicitly accepted tradeoff.

## Architectural decision records

An ADR is required before a change:

- selects or changes a system-wide mechanism, trust boundary, public ABI, boot
  contract, persistence format, or cross-subsystem contract;
- adds a new class of privileged or unsafe operation;
- proposes an amendment or retirement of an invariant or constitutional
  dependency rule (the ADR alone creates no exception);
- introduces an externally maintained target-side dependency;
- makes a choice that would be expensive or risky to reverse.

Use [0000-template.md](adr/0000-template.md). ADR filenames MUST be
`NNNN-short-kebab-title.md` with a monotonically assigned four-digit number. The
allowed states are **Proposed**, **Accepted**, **Rejected**, **Superseded**, and
**Deprecated**. Only Accepted ADRs authorize implementation.

Acceptance requires the exact ADR blob to be merged through the protected
authority ref with the configured independent approval. A status edit on an
untrusted branch, issue, or candidate commit has no authority. Proposed ADRs may
be authored as bounded GENESIS governance work without a prior task, but they
authorize no TEMPER work until Accepted.

An accepted ADR is an immutable decision record. Corrections that do not change
meaning MAY be made in place; a changed decision requires a new ADR that links to
and supersedes the old one. Rejected numbers are never reused. Each ADR MUST link
to affected invariants, contracts, task specs, and evidence. A prototype may
inform an ADR, but MUST remain isolated and MUST NOT become production architecture
before acceptance.

## Intentionally undecided

Until accepted ADRs say otherwise, VISION-64 makes no constitutional commitment
about kernel organization, boot/firmware protocol, address-space layout,
allocation algorithms, interrupt/timer hardware, execution or scheduling model,
userspace ABI, capability model, driver topology, storage model, networking
stack, or source-tree/crate topology.

Sprint 0 may create only the minimum scaffolding permitted by
[ROADMAP.md](ROADMAP.md). Discovering that Sprint 0 needs one of the decisions
above is a reason to write an ADR, not permission to decide it in code.
