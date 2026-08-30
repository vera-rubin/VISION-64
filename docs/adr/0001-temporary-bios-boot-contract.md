# ADR 0001: Use a Temporary BIOS Boot Contract for Sprint 0

- **Status:** Proposed
- **Date:** 2026-08-29
- **Owners:** VISION-64 maintainer
- **Decision scope:** Boot and composition, initial x86-64 target and entry
  contract, boot-artifact construction, and boot dependency boundary
- **Related task(s):**
  [`docs/tasks/1-establish-observable-boot-heartbeat.md`](../tasks/1-establish-observable-boot-heartbeat.md)
- **Related invariants:** V64-GOV-002, V64-BLD-001, V64-INIT-001,
  V64-OWN-001, V64-MEM-003, V64-BND-001, V64-BND-002, V64-ARCH-001,
  V64-DEP-001, V64-DEP-002, V64-SAFE-001, V64-SAFE-002
- **Supersedes:** None
- **Superseded by:** None
- **Approval authority:** Independent VISION-64 maintainer; no author or
  implementation worker may self-approve
- **Approval evidence:** Pending independent review and protected-main merge;
  this proposed blob has no authority on its branch

## Decision summary

The first Sprint 0 kernel artifact targets Rust's freestanding
`x86_64-unknown-none` target and enters through the exact `bootloader_api`
`0.11.17` handoff. A host-only image tool uses `bootloader` `0.11.17` with only
its `bios` feature to create a raw MBR disk image. QEMU boots that image through
legacy PC BIOS for this task only. The kernel accepts the bootloader-provided
stack and typed entry argument but does not inspect, retain, expose, or build
policy on the memory map, framebuffer, address layout, firmware tables, or any
other `BootInfo` field. Bootloader framebuffer and serial logging are disabled.

This is a reversible bring-up adapter, not the VISION-64 production boot design.
Custom UEFI, a permanent firmware protocol, and all post-entry memory policy
remain undecided.

## Context and problem

Sprint 0 must prove that VISION-64 code reaches a freestanding Rust entry point.
An ELF file that merely links is not boot evidence. Reaching that entry point
requires selecting a target, firmware path, bootable artifact format, entry ABI,
and the narrow third-party boundary that constructs and loads the artifact.
Those are material decisions under the architecture constitution and therefore
cannot be buried in Task 1 or its code.

The repository currently contains no kernel, linker layout, custom firmware
loader, memory manager, allocator, or accepted boot protocol. Implementing a
real-mode-to-long-mode loader now would make the temporary mechanism larger than
the heartbeat it exists to launch. The task also must not make a temporary
loader's memory map or address layout into permanent kernel architecture.

The known verification host is `vision-devbox`, whose retained runner evidence
records Rust `1.100.0-nightly (e457a7b0d 2026-08-27)`, Cargo
`1.100.0-nightly (e8cb624d5 2026-08-22)`, and QEMU `10.0.11`. The task freezes
those versions for its proof environment.

## Constraints and decision drivers

In priority order:

1. Produce a real bootable and inspectable x86-64 artifact with the smallest
   VISION-owned privileged surface.
2. Keep the kernel `#![no_std]`, `#![no_main]`, allocator-free, and independent
   of hosted runtime assumptions.
3. Make the temporary boot mechanism replaceable without changing the early
   diagnostics protocol or emulator terminal contract.
4. Avoid implementing a page-table policy, allocator, firmware parser, custom
   UEFI application, or handwritten multistage BIOS loader in Task 1.
5. Pin every selected dependency and feature, and retain its resolved closure.
6. Prevent bootloader logs or framebuffer behavior from contaminating the
   canonical serial evidence channel.

Non-goals include portability beyond the exact Sprint 0 QEMU machine, a stable
boot ABI, physical-memory ownership, framebuffer use, ACPI, SMP, interrupts,
drivers, and production firmware support.

## Options considered

### Option A — Rust `bootloader` crate, BIOS-only image

- **Description:** Compile a freestanding kernel ELF for
  `x86_64-unknown-none`, use `bootloader_api` for the typed entry wrapper, and
  use the host-side `bootloader` crate to construct a raw BIOS disk image.
- **Benefits:** Small VISION-owned boot surface; no handwritten mode switch;
  works with the pinned nightly toolchain; BIOS and UEFI features can be
  separated; the adapter can be removed later.
- **Costs and risks:** Introduces reviewed target and host dependencies, their
  transitive build code, and a temporary entry ABI. The bootloader establishes a
  stack and mappings before entry.
- **Invariant impact:** Requires a pinned dependency closure and strict
  containment of the bootloader contract. No invariant exception is created.
- **Evidence required:** Locked dependency graph, clean kernel build, image hash,
  QEMU boot proof, and scope review showing no `BootInfo` policy dependency.

### Option B — Handwritten BIOS loader

- **Description:** Add assembly and Rust stages for real mode, protected mode,
  long mode, disk loading, ELF loading, page tables, and entry transfer.
- **Benefits:** Complete in-tree control and no target-side boot dependency.
- **Costs and risks:** Large privileged and unsafe surface; prematurely selects
  address layout and mapping mechanisms; obscures the first heartbeat behind a
  disposable loader.
- **Invariant impact:** Greatly expands V64-SAFE-002, V64-MEM-002, and
  V64-BND-001 proof obligations.
- **Evidence required:** Far beyond the bounded first slice.

### Option C — GRUB/Multiboot or another host-installed loader

- **Description:** Construct an ISO or disk around the kernel using external
  host tools and a multiboot protocol.
- **Benefits:** Mature boot path and less in-tree loader code.
- **Costs and risks:** Adds a boot protocol plus mutable host tool/image inputs
  not currently declared on `vision-devbox`; still requires a linker/entry
  contract and later removal.
- **Invariant impact:** Expands the host dependency and artifact trust boundary.
- **Evidence required:** Immutable tool/image provenance and protocol validation
  not available in the repository today.

### Option D — Stop at a linked ELF

- **Description:** Establish only a freestanding build.
- **Benefits:** Smallest source change.
- **Costs and risks:** Does not prove boot, entry, diagnostics, or failure; it
  cannot satisfy the Sprint 0 observable-boot objective.
- **Invariant impact:** Would leave V64-OBS-001 unproved.

## Decision

Choose Option A with these frozen limits:

- Rust toolchain: `nightly-2026-08-27`, target
  `x86_64-unknown-none`, component `llvm-tools-preview`, Rust 2024 edition, and
  default target CPU/features.
- Kernel dependency: `bootloader_api = "=0.11.17"` with no optional features.
- Host image dependency: `bootloader = { version = "=0.11.17",
  default-features = false, features = ["bios"] }`.
- Cargo resolves exact transitive versions and checksums in committed
  `Cargo.lock`; no other direct third-party dependency is authorized.
- The image tool uses `BiosBoot`, creates one raw MBR image, disables bootloader
  serial logging and framebuffer logging, and supplies no ramdisk or extra file.
- The kernel entry uses `bootloader_api::entry_point!` with an explicit 64-KiB
  boot stack. It treats the `BootInfo` argument as an opaque proof of the typed
  handoff and does not read any field. The exact pinned dependency is trusted to
  construct a valid, aligned, live, and uniquely borrowed `&'static mut
  BootInfo`; Task 1 cannot validate those properties after a Rust reference
  already exists and therefore audits that dependency-owned unsafe boundary.
- The kernel does not enable an allocator, inspect mappings, request extra
  mappings, assume a virtual or physical address, or expose bootloader types
  beyond the private boot-composition module.
- The acceptance image is attached read-only to QEMU's legacy PC machine. The
  loader and its disk format are test scaffolding, not a public VISION ABI.

The exact crate source archives may be fetched through Cargo only at the locked
versions and verified checksums. Proof builds then run offline from the retained
locked source set. Verification records the full `cargo metadata` and
`cargo tree -e all` closure plus every license expression/file, source/checksum,
build script, proc macro, native source, network capability, unsafe/assembly
site, maintenance observation, and no-dependency alternative. A version,
feature, source, build-script, proc-macro, native-code, or transitive dependency
change returns to GENESIS.

## Contract and boundary impact

- **Boot and composition:** Owns the one-time typed handoff and constructs the
  diagnostics/test adapters. It must not become a service locator.
- **Architecture mechanisms:** The selected target guarantees the System V
  x86-64 calling convention without a red zone. No VISION code selects a page
  table or address-space policy.
- **Host tooling and verification:** Owns raw image construction. It may consume
  the kernel ELF but the kernel must not depend on the host tool.
- **Diagnostics and recovery:** Independent of this ADR except that bootloader
  serial logging is disabled before the VISION serial protocol begins.
- **Ownership/lifecycle:** Firmware and bootloader own machine bring-up until the
  typed entry call. Task 1 owns no boot-provided resource after entry and does
  not transfer any `BootInfo` resource to another subsystem.
- **Allocation/blocking/concurrency:** Target code allocates and blocks nowhere.
  Host image construction may allocate and perform file I/O outside target code.
- **Errors/partial progress:** Build or image-construction failure produces no
  accepted boot artifact. The harness hashes an artifact only after successful
  construction.

## Safety, security, and unsafe-code impact

VISION-owned unsafe code is not authorized by this ADR; the separate
architecture I/O operations are governed by ADRs 0002 and 0003. The entry macro
and bootloader contain dependency-owned unsafe/assembly that is part of the
trusted computing base and must be identified and reviewed in the dependency
audit; a passing boot does not prove that code sound.

The macro-provided `BootInfo` reference is foreign boundary data under
V64-BND-001. Task 1 avoids turning it into a VISION trust surface by reading no
field and deriving no resource, address, or policy from it. The macro-provided
signature is used unchanged, the reference never escapes the private entry
function, unwinding is disabled, and no panic may cross the entry boundary.
Nevertheless, V64-MEM-003 and V64-SAFE-001 require the pinned entry dependency
to uphold the reference's validity, alignment, lifetime, and uniqueness before
VISION receives it. That precondition is an explicit accepted dependency risk,
not discharged by leaving fields unread.

## Verification and acceptance evidence

| Claim / requirement | Evidence | Pass condition |
| --- | --- | --- |
| Target is freestanding | `rustc -vV`, Cargo metadata, kernel attributes, and ELF build log | Exact pinned nightly/target; `no_std`/`no_main`; no `std` target dependency |
| Dependency closure is fixed and reviewable | `Cargo.lock`, locked metadata/tree, retained source archive/vendor hashes, and dependency audit | Exact direct versions/features above; no Git/floating source or undeclared direct dependency; every transitive license/source/build script/proc macro/native/network/unsafe/assembly/maintenance fact is recorded and all proof builds are offline |
| BIOS artifact is bootable | Image-build log, image SHA-256, QEMU argv, and serial evidence | Read-only raw image reaches the Rust heartbeat under the exact Task 1 command |
| Boot contract remains narrow | Candidate diff and focused entry/dependency review | No `BootInfo` field read or escape, allocator, mapping policy, framebuffer, ACPI, UEFI, or handwritten loader; the dependency-owned reference precondition is traced to the exact pinned macro/loader source |
| Bootloader cannot forge VISION records | Image-tool configuration and raw serial artifact | Bootloader serial/framebuffer logging disabled; serial contains only Task 1 protocol records |

## Consequences

### Positive

- VISION reaches real freestanding Rust without first implementing disposable
  firmware and paging machinery.
- The temporary boot dependency is isolated from the lasting diagnostics and
  QEMU test contracts.
- The first implementation remains reversible and reviewable.

### Negative and tradeoffs

- Sprint 0 temporarily trusts the pinned bootloader dependency and its build
  closure.
- The resulting image is BIOS/QEMU-specific and is not a production boot path.
- No boot information is available to later kernel code until a later accepted
  task and ADR deliberately introduce a validated contract.

### Follow-up work

- A later, separately gated ADR may replace this adapter with custom UEFI.
- Any future need for boot memory data, framebuffer, firmware tables, or stable
  entry ABI requires a new ADR and is not implied here.

## Rollout, compatibility, and reversal

Task 1 introduces the adapter and its two pinned direct dependencies together.
Rollback is a revert of that task candidate, which removes the workspace,
kernel, image tool, lockfile entries, and generated image. No persistent format
or user-visible ABI survives.

This ADR must be superseded before a custom UEFI path or different boot protocol
is implemented. The trigger is an approved task whose acceptance requires boot
outside the exact BIOS/QEMU contract. Superseding this ADR need not change ADR
0002's serial protocol or ADR 0003's QEMU-only terminal contract.

## References

- [Architecture constitution](../ARCHITECTURE.md)
- [Invariant registry](../INVARIANTS.md)
- [Roadmap](../ROADMAP.md)
- [Testing policy](../TESTING.md)
- [FORGE process](../FORGE.md)
- [Rust `x86_64-unknown-none` target](https://doc.rust-lang.org/rustc/platform-support/x86_64-unknown-none.html)
- [`bootloader` 0.11.17](https://docs.rs/bootloader/0.11.17/bootloader/)
- [`bootloader_api` 0.11.17](https://docs.rs/bootloader_api/0.11.17/bootloader_api/)

## Decision log

| Date | Status | Reason / evidence | Approved by |
| --- | --- | --- | --- |
| 2026-08-29 | Proposed | Selected for independent review with bounded Task 1; effective only if this exact blob reaches protected `main` with the required approval | Pending |
