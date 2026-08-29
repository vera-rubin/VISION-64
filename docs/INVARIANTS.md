# VISION-64 Non-Negotiable Invariants

## Purpose

An invariant is a condition that every accepted VISION-64 change preserves. It
is not an aspiration, an implementation suggestion, or something a passing test
may waive. If a proposed design cannot preserve an invariant, the design MUST be
rejected or this constitution MUST be amended explicitly before the code lands.

Identifiers are permanent. An identifier MUST NOT be renamed or reused for a
different rule. A retired rule remains in this file with its disposition and the
ADR that changed it. Normative terms follow RFC 2119.

The architectural context is in [ARCHITECTURE.md](ARCHITECTURE.md); verification
expectations are in [TESTING.md](TESTING.md).

## Governance and evidence

### V64-GOV-001 — Authorized scope

Every change MUST trace to an approved task specification with bounded scope,
acceptance tests, and explicit exclusions. An agent MUST NOT turn ambiguity into
new architecture or adjacent implementation.

### V64-GOV-002 — Decision traceability

A material architectural choice MUST be authorized by an Accepted ADR before
production code depends on it. Code and task specs MUST NOT silently override an
invariant or accepted ADR.

### V64-GOV-003 — Evidence over assertion

Acceptance MUST be based on reproducible evidence mapped to each acceptance
criterion. Agent confidence, reviewer count, majority vote, compilation alone,
and elapsed time MUST NOT substitute for evidence.

### V64-GOV-004 — Independent verification

The author or improver of a change MUST NOT be its sole verifier. Verification
MUST be repeatable from repository state without relying on undocumented
conversation context or mutable local state.

## Build and lifecycle

### V64-BLD-001 — Declared inputs

A supported build or test MUST derive from the checked-in source plus explicitly
declared toolchain, configuration, and inputs. Success MUST NOT depend on an
undeclared host file, interactive state, network-fetched mutable artifact, or
prior build output.

### V64-INIT-001 — No use before initialization

A subsystem or resource MUST NOT become accessible until its required
initialization and validation have completed. Partial failure MUST leave it
inaccessible or in an explicit, documented degraded state; it MUST NOT appear
fully initialized.

### V64-OWN-001 — Explicit unique ownership

Every exclusive hardware or memory resource MUST have one identifiable owner at
a time. Transfer, sharing, borrowing, and release MUST be explicit. The same
resource MUST NOT be independently handed out to multiple owners.

### V64-FAIL-001 — Bounded terminal behavior

Boot and automated test runs MUST have bounded execution and an observable
terminal classification. A timeout, missing signal, emulator crash, or runner
loss is indeterminate or failed, never passed.

### V64-OBS-001 — Observable boot and failure

The earliest supported boot path, normal test completion, and panic/fatal paths
MUST emit distinguishable evidence through the configured test channels. A
terminal status without the required diagnostic evidence MUST NOT be accepted as
a complete pass.

### V64-PANIC-001 — Panic-path independence

The panic/fatal path MUST be bounded and non-recursive. It MUST NOT require
fallible allocation, scheduler progress, or acquisition of a lock that may be
held by the failing context. It SHOULD attempt minimal diagnostic output and a
failure terminal signal, but failure of that best-effort output MUST NOT cause
undefined behavior or unbounded recursion.

## Memory, concurrency, and boundaries

These invariants apply as soon as code touches the relevant capability; their
presence here does not authorize implementing that capability during Sprint 0.

### V64-MEM-001 — Exclusive physical allocation

A live physical memory extent MUST NOT be allocated to two independent owners.
Reservation, allocation, aliasing, and release transitions MUST be explicit and
checked against the source of truth selected by an ADR.

### V64-MEM-002 — Valid mappings

Every live mapping MUST have valid alignment, bounds, lifetime, cacheability, and
access permissions for its declared use. Mapping creation, permission changes,
and removal MUST preserve the relevant architecture's ordering and invalidation
requirements.

### V64-MEM-003 — Rust reference validity

Every Rust reference MUST point to initialized memory of the correct type and
alignment for its full lifetime, with aliasing compatible with Rust's rules.
Memory-mapped I/O, foreign memory, packed fields, and potentially uninitialized
storage MUST NOT be treated as ordinary references unless those requirements are
proved.

### V64-CON-001 — Synchronized shared mutation

Mutable state reachable by more than one execution context MUST use a documented
exclusion or synchronization protocol. The protocol MUST state participating
contexts, ordering guarantees, and whether interrupt/preemption state is part of
the proof.

### V64-CON-002 — Interrupt progress

Interrupt context MUST NOT wait for work that can only be completed by the
interrupted or disabled context. Interrupt handlers MUST preserve the required
machine state and MUST NOT unwind across the interrupt boundary.

### V64-BND-001 — Validate untrusted boundary data

Values crossing a privilege, ABI, firmware, device, file-format, or host/target
boundary MUST be treated as untrusted until lengths, ranges, alignment,
discriminants, permissions, and ownership are validated. Malformed input MUST
produce a defined error or controlled failure, never undefined behavior.

### V64-BND-002 — No cross-boundary unwinding

Unwinding MUST NOT cross an `extern`, interrupt, naked-function, firmware,
assembly, or other boundary that does not explicitly guarantee Rust-compatible
unwinding. Boundary code MUST contain or terminate failure according to its
documented contract.

## Architecture and dependencies

### V64-ARCH-001 — Platform containment

Architecture-, firmware-, board-, and emulator-specific operations and constants
MUST remain within their declared adapter or mechanism boundary. General policy
MUST NOT rely on them through hidden globals, incidental layout, or undocumented
initialization effects.

### V64-DEP-001 — Acyclic dependency direction

Dependencies MUST follow [ARCHITECTURE.md](ARCHITECTURE.md#dependency-direction).
Logical subsystem cycles and reverse dependencies from mechanisms into
higher-level policy are forbidden unless a prior ADR changes the boundary and
explains initialization and failure behavior.

### V64-DEP-002 — Reviewable dependency closure

All project-selected code fetched or introduced for build, test, or target
runtime MUST come from declared, reviewable, immutably pinned sources.
Host-provided tools and runner images MUST be constrained by the applicable task
or CI policy and their exact versions MUST be captured in evidence. Dependency
features and transitive trusted code MUST be limited to what the accepted design
requires.

## Unsafe Rust policy

### V64-SAFE-001 — Safe interfaces are sound

A public safe interface MUST NOT permit undefined behavior for any input or call
sequence expressible by safe Rust. If soundness depends on a caller obligation
that safe Rust cannot enforce, the interface MUST be `unsafe` and document that
obligation.

### V64-SAFE-002 — Unsafe is necessary, local, and justified

Unsafe Rust MAY be used only where required to implement a reviewed boundary such
as privileged instructions, assembly/ABI integration, raw memory management, or
memory-mapped I/O. It MUST NOT be used merely to bypass ownership, lifetime,
thread-safety, initialization, or lint errors.

Every unsafe operation MUST:

1. appear in the smallest practical `unsafe` block even inside an `unsafe fn`;
2. have a nearby `SAFETY:` argument stating the exact preconditions, why each is
   established at that point, and which `V64-*` invariants it preserves;
3. use types and safe wrappers to prevent invalid repetition where practical;
4. avoid expanding the trusted surface beyond the operation being justified;
5. receive focused review and verification appropriate to its failure modes.

An `unsafe fn` MUST include a `# Safety` section describing every caller
obligation. An `unsafe trait` or `unsafe impl` MUST document the global contract
and why it holds. `unsafe` code MUST NOT infer safety from a passing runtime test;
tests demonstrate behavior, not absence of undefined behavior.

### V64-SAFE-003 — Foreign and hardware access preserves semantics

FFI and hardware-facing representations MUST use explicit layout where required,
validate foreign discriminants and pointers before conversion, and use volatile
access, atomics, barriers, or assembly options according to the applicable
accepted hardware/ABI contract. Ordinary loads and stores MUST NOT be assumed to
provide device or synchronization semantics.

### Enforcement

The target code SHOULD enable lints that expose unsafe operations inside unsafe
functions and SHOULD deny undocumented unsafe blocks once the build skeleton can
enforce those checks. A temporary inability to automate a lint does not weaken
the invariant; the PR MUST provide manual audit evidence until automation exists.

## Changing an invariant

An invariant change requires all of the following:

1. a dedicated ADR explaining the necessity, alternatives, affected threat and
   failure models, and migration plan;
2. explicit review from maintainers responsible for every affected boundary;
3. updated tests and evidence requirements before dependent implementation lands;
4. a retained history entry here. Removed identifiers MUST be marked retired and
   MUST NOT be reassigned.

No task specification, waiver label, reviewer vote, deadline, or prototype may
silently suspend an invariant.
