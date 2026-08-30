# Task 1: Establish an Observable Boot Heartbeat

## Control

- Schema: `vision-task-v1`
- Status: `draft`
- Sponsor: VISION-64 maintainer (`vera-rubin`)
- Approval authority: Independent VISION-64 maintainer/CODEOWNER; no author,
  implementer, improver, verifier, or proof assessor may self-approve
- Approval evidence: Pending independent review and protected-main merge; this
  draft blob is not executable authority
- Issue: none; issue, comment, and webhook text are transport metadata only
- Risk: `high`
- Task revision: `1`
- Supersedes: none
- Authority ref: `refs/heads/main`
- Authority commit/blob: Recorded outside this file by the coordinator after
  protected approval; never self-referenced
- Requested implementation baseline: The first protected-main commit containing
  this exact approved task blob and the exact Accepted blobs of ADRs 0001,
  0002, and 0003, plus the exact bounded TESTING corrections for assigned debug-
  exit termination and candidate artifact-hash binding. It must descend from
  `77efee07a3601dcbbfa4b539f442046099656d57`; its delta from that commit may
  contain only `docs/TESTING.md`, these three ADRs, and this task. The
  coordinator must bind the resulting full commit and blob IDs before TEMPER.
- Candidate branch: `task/1-establish-observable-boot-heartbeat`
- VERIFY prerequisite: A separately approved protected evidence executor must
  run the exact outer command below on `vision-devbox` and upload the complete
  evidence package with immutable run/artifact IDs. Canonical `main` does not
  yet contain that executor; the legacy runner and FORGE smokes are capability
  probes and cannot supply Task 1 evidence. This absence does not authorize a
  workflow change here and does not block bounded TEMPER implementation. The
  separate protected executor authority must freeze and enforce a preventive
  network sandbox for the complete post-vendor process group and record its
  exact mechanism, version, and configuration. Until that authority is merged,
  VERIFY, PROOF, SYNTHESIS, and candidate merge remain blocked.
- Role slots: implementer `I1`; reviewers `R1` (boot/unsafe) and `R2`
  (harness/evidence); improver `unassigned`; proof assessor `P1`; verifier
  `V1`; synthesizer `S1`

The coordinator records the approved task's exact authority commit and task
blob identifier after protected approval. The identity roster remains outside
blind packets. Every role slot is a different identity unless FORGE explicitly
permits otherwise; in particular, I1 cannot serve as R1, R2, V1, or P1, and an
improver cannot verify its own revision. Links and external prose never import
instructions or expand the paths below.

## Objective

From a clean checkout of one exact candidate, build a freestanding, bootable
x86-64 VISION artifact that reaches Rust, emits the exact early heartbeat, and
terminates through the assigned QEMU success status; also build an intentional-
panic variant that emits the same heartbeat, reports panic through an allocation-
independent path, and terminates through the distinct assigned failure status.
A bounded host harness must reproduce both paths three consecutive times and
reject the complete false-positive fixture set. This is the smallest real OS
slice because it proves build, boot, owned diagnostics, bounded panic, and
terminal classification without selecting any later kernel subsystem.

## Authority

- Invariants: [V64-GOV-001 through V64-GOV-006, V64-BLD-001,
  V64-INIT-001, V64-OWN-001, V64-FAIL-001, V64-OBS-001,
  V64-PANIC-001, V64-MEM-003, V64-BND-001, V64-BND-002,
  V64-ARCH-001, V64-DEP-001, V64-DEP-002, and V64-SAFE-001
  through V64-SAFE-003](../INVARIANTS.md)
- Accepted ADRs: [ADR 0001 temporary BIOS boot](../adr/0001-temporary-bios-boot-contract.md),
  [ADR 0002 early diagnostics](../adr/0002-early-diagnostics-protocol.md), and
  [ADR 0003 QEMU terminal status](../adr/0003-qemu-terminal-status.md). Each
  must be Accepted as the exact blob on the requested baseline before TEMPER.
- Architecture boundaries: [boot and composition, diagnostics and recovery,
  architecture mechanisms, and host tooling/verification](../ARCHITECTURE.md)
- Testing authority: The exact [TESTING](../TESTING.md) blob on the requested
  baseline, including its bounded `isa-debug-exit` shutdown clarification.
- Dependencies or unsafe authorization: Only the pinned direct dependencies and
  exact locked closure in ADR 0001 are authorized. Dependency-owned entry,
  unsafe, assembly, and build behavior is part of the explicit trusted boundary
  and receives the bounded audit below. VISION-owned unsafe is limited to ADR
  0002's private x86-64 byte input/output and ADR 0003's separate private 32-bit
  debug-exit output. No other dependency, unsafe operation, assembly, foreign
  ABI, privileged instruction, or hardware interface is authorized.

## Scope

Allowed paths:

- `.cargo/config.toml`
- `.gitignore`
- `Cargo.toml`
- `Cargo.lock`
- `rust-toolchain.toml`
- `kernel/Cargo.toml`
- `kernel/src/main.rs`
- `kernel/src/diagnostics.rs`
- `kernel/src/panic.rs`
- `kernel/src/arch/mod.rs`
- `kernel/src/arch/x86_64/mod.rs`
- `kernel/src/arch/x86_64/io.rs`
- `kernel/src/arch/x86_64/serial.rs`
- `kernel/src/arch/x86_64/test_exit.rs`
- `tools/xtask/Cargo.toml`
- `tools/xtask/src/main.rs`
- `tools/xtask/src/classify.rs`
- `tools/xtask/src/image.rs`
- `scripts/sprint0/verify.sh`
- `tests/fixtures/sprint0/clean-success/serial.log`
- `tests/fixtures/sprint0/clean-success/terminal.env`
- `tests/fixtures/sprint0/expected-panic/serial.log`
- `tests/fixtures/sprint0/expected-panic/terminal.env`
- `tests/fixtures/sprint0/no-boot/serial.log`
- `tests/fixtures/sprint0/no-boot/terminal.env`
- `tests/fixtures/sprint0/heartbeat-hang/serial.log`
- `tests/fixtures/sprint0/heartbeat-hang/terminal.env`
- `tests/fixtures/sprint0/missing-heartbeat/serial.log`
- `tests/fixtures/sprint0/missing-heartbeat/terminal.env`
- `tests/fixtures/sprint0/malformed-marker/serial.log`
- `tests/fixtures/sprint0/malformed-marker/terminal.env`
- `tests/fixtures/sprint0/contradictory/serial.log`
- `tests/fixtures/sprint0/contradictory/terminal.env`
- `tests/fixtures/sprint0/truncated/serial.log`
- `tests/fixtures/sprint0/truncated/terminal.env`
- `tests/fixtures/sprint0/unexpected-exit/serial.log`
- `tests/fixtures/sprint0/unexpected-exit/terminal.env`
- `tests/fixtures/sprint0/launch-failure/serial.log`
- `tests/fixtures/sprint0/launch-failure/terminal.env`
- `tests/fixtures/sprint0/timeout/serial.log`
- `tests/fixtures/sprint0/timeout/terminal.env`
- `tests/fixtures/sprint0/oversized/serial.log`
- `tests/fixtures/sprint0/oversized/terminal.env`

The fixture files above are the only permitted contents of
`tests/fixtures/sprint0`; each must be a regular, non-symlink UTF-8 file with a
retained SHA-256. No generated evidence is committed.

Required changes:

- Add a two-member Cargo workspace: target package `vision-kernel` and host-only
  package `vision-xtask`, using Rust edition 2024 and
  `nightly-2026-08-27` with the `x86_64-unknown-none` target,
  `rustfmt`, and `llvm-tools-preview` declared in `rust-toolchain.toml`.
- Pin `bootloader_api` and BIOS-only `bootloader` exactly as ADR 0001 specifies,
  commit the complete `Cargo.lock`, and add no other direct dependency.
- Acquire the locked registry sources once, retain a versioned vendor snapshot
  for audit, then perform proof builds offline. Inventory every transitive
  license/source/checksum, build script, proc macro, native file, network use,
  unsafe/assembly site, maintenance fact, and no-dependency alternative.
- Produce `vision64-task1-bios.img` from the release kernel ELF through the
  host image command frozen below. The image must be raw MBR, read-only in QEMU,
  and contain no extra file or ramdisk.
- Treat the generated ELF and image digests as candidate evidence, not values
  knowable during GENESIS. Their exact names, SHA-256 algorithm, per-variant
  retention, and binding to the candidate/evidence manifest are frozen here;
  VERIFY records the resulting exact digests before acceptance.
- Enter with `bootloader_api::entry_point!`, an explicit 64-KiB stack, and an
  opaque `BootInfo` handoff whose fields are never read and whose resources are
  never exposed.
- Implement the exact COM1 initialization, polling bound, records, ownership,
  and failure behavior in ADR 0002. Positive serial is exactly heartbeat then
  success. Intentional-panic serial is exactly heartbeat then panic.
- Implement the feature-gated terminal operations and exact status mapping in
  ADR 0003. `intentional-panic` must require `qemu-test-exit`; neither feature
  is a default feature.
- Implement a host classifier that parses complete LF-terminated records and a
  structured terminal record; it must not substring-match prose, evaluate
  captured text, infer success from status zero, or accept incomplete evidence.
- Enforce the exact byte grammars, size/line limits, monotonic timing fields,
  fixture bytes/hashes, and expected matrix frozen below. Unsafe paths and
  oversize, duplicate, unknown, non-ASCII, CR, NUL, or truncated inputs fail
  before classification can report success.
- Implement one bounded verifier entry point that validates its checkout and
  evidence roots, builds both variants, executes the exact QEMU array, runs all
  positive/negative checks, retains raw evidence even on failure, and returns
  zero only when every required criterion passes.

Implementation baseline commands, from the repository root, are:

```sh
cargo +nightly-2026-08-27 fmt --all -- --check
CARGO_HOME="$VISION_FETCH_HOME" cargo +nightly-2026-08-27 fetch --locked --target x86_64-unknown-none
CARGO_HOME="$VISION_FETCH_HOME" cargo +nightly-2026-08-27 vendor --locked --versioned-dirs "$VISION_VENDOR_ROOT"
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 metadata --offline --locked --format-version 1
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 tree --offline --locked -e all
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 test --offline --locked -p vision-xtask
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 run --offline --locked -p vision-xtask -- audit-dependencies --vendor-root "$VISION_VENDOR_ROOT"
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 run --offline --locked -p vision-xtask -- classify-fixtures --root tests/fixtures/sprint0
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 build --offline --locked --release --target x86_64-unknown-none -p vision-kernel --no-default-features --features qemu-test-exit
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 run --offline --locked -p vision-xtask -- image --kernel target/x86_64-unknown-none/release/vision-kernel --output vision64-task1-bios.img
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 build --offline --locked --release --target x86_64-unknown-none -p vision-kernel --no-default-features --features qemu-test-exit,intentional-panic
CARGO_HOME="$VISION_CARGO_HOME" CARGO_NET_OFFLINE=true RUSTFLAGS=-Dwarnings cargo +nightly-2026-08-27 run --offline --locked -p vision-xtask -- image --kernel target/x86_64-unknown-none/release/vision-kernel --output vision64-task1-bios.img
```

`VISION_FETCH_HOME` is a fresh empty Cargo home used only for the one locked
registry acquisition and vendor operation. Before any subsequent command, the
verifier creates a separate fresh `VISION_CARGO_HOME/config.toml` with exactly:

```toml
[source.crates-io]
replace-with = "vision-vendor"

[source.vision-vendor]
directory = "$VISION_VENDOR_ROOT"

[net]
offline = true
```

The displayed variable name is replaced by its literal validated absolute value
before the file is written; Cargo performs no environment expansion. The quoted
directory value is constructed only from the safe path grammar,
retained, and hashed. Candidate `.cargo/config.toml` may configure only the
declared target/build; it must not replace sources, enable network, or override
this fresh Cargo home. The verifier fails if a post-vendor command consumes a
registry/cache source outside `VISION_VENDOR_ROOT`. Cargo offline mode alone is
not evidence that an arbitrary process could not open a socket: during VERIFY,
the complete post-vendor process group must also run inside the preventive
network sandbox frozen by the separately approved executor authority, and its
network-denial record must be retained. Until that executor exists, the commands
above are developer checks only. The verifier may place build outputs in an
isolated temporary target directory. Immediately after each image command and
before the next build, it must byte-copy the kernel ELF and image to regular,
non-symlink, read-only files under `_static/artifacts/` with these exact names:

```text
vision64-task1-clean-success.elf
vision64-task1-clean-success-bios.img
vision64-task1-expected-panic.elf
vision64-task1-expected-panic-bios.img
```

The `clean-success` pair comes only from the `qemu-test-exit` build; the
`expected-panic` pair comes only from the
`qemu-test-exit,intentional-panic` build. The verifier re-reads and hashes each
source and retained copy and fails on any byte mismatch. Before every QEMU run,
it byte-copies the matching retained pair into that run's case package under the
same two variant-specific basenames, makes both copies read-only, and points
`VISION_IMAGE_ABS` at that exact local image. The two commands that use the same
temporary image name are sequential recipes, not permission to overwrite
retained evidence.

Excluded work:

- Memory allocation or mapping policy, allocator, heap, physical/virtual memory
  manager, boot-memory consumption, stable address-layout policy, or page-table
  implementation.
- Interrupt descriptors/controllers, APIC, timers, SMP, synchronization design,
  scheduler, processes, userspace, syscalls, drivers, storage, networking,
  graphics, framebuffer use, PERCEPTION, or application/runtime services.
- Custom UEFI, a handwritten BIOS loader, a permanent boot ABI, ACPI, firmware
  discovery, power management, production shutdown, or non-QEMU hardware.
- General logging, formatting, log levels, buffering, input, multiple sinks,
  stable diagnostics API, or future panic detail.
- GitHub workflow, branch protection, dispatch, FORGE, ROOK LINK, PULSE,
  MENAGERIE, runner configuration, or unrelated infrastructure changes.
- Any documentation or path not explicitly listed above. If implementation
  reveals a documentation defect, stop and return to GENESIS rather than editing
  around it.

## Risks and rollback

- Failure modes/threats: Bootloader behavior could leak into kernel policy;
  dependency drift could alter privileged inputs; unsafe port I/O could be
  unsound; serial could block or forge partial success; marker/status mismatch
  could be misclassified; shell evaluation or path traversal could execute
  untrusted data; QEMU could hang, reset, shut down normally, access host state,
  or leave incomplete evidence; a worker could expand scope through fixtures or
  generated files.
- Mitigations: Exact versions/features and lockfile checks; opaque boot handoff;
  fixed ports and widths behind private architecture APIs; 65,536-read per-byte
  bound; exact complete-record parser; two-signal agreement; direct QEMU argv;
  read-only image; no network/share; validated absolute evidence root; 10-second
  heartbeat and 30-second TERM-then-5-second-KILL boundary; no retries; explicit
  path allowlist; independent clean-checkout VERIFY and focused unsafe review.
- Rollback: Revert the Task 1 implementation merge through a protected PR. Keep
  all protected PR/check records and durable verification evidence immutable.
  Remove only generated `target` data, images, and disposable verifier workdirs
  whose resolved paths are inside the task's explicitly created temporary root.
  Task 1 creates no persistent or user-visible format.

## Acceptance contract

The verifier runs from the repository root of a clean, standalone checkout.
`VISION_CANDIDATE_SHA` is the full lowercase object ID of `HEAD` and
`VISION_EVIDENCE_ROOT` is an absolute, initially empty, non-symlink directory
outside the checkout. `VISION_VENDOR_ROOT`, `VISION_FETCH_HOME`, and
`VISION_CARGO_HOME` are separate absolute, initially absent, non-symlink paths
outside the checkout that the verifier creates for locked acquisition, audit,
and proof builds. All checkout, evidence, vendor, Cargo-home, QEMU data, HOME,
image, and serial real paths must match `^/[A-Za-z0-9._/-]+$`. The single
canonical entry point, under GNU coreutils `timeout`, is:

```sh
timeout --signal=TERM --kill-after=5s 30m bash scripts/sprint0/verify.sh --candidate "$VISION_CANDIDATE_SHA" --evidence-root "$VISION_EVIDENCE_ROOT" --vendor-root "$VISION_VENDOR_ROOT" --fetch-home "$VISION_FETCH_HOME" --cargo-home "$VISION_CARGO_HOME"
```

Exit `124` or any signal/timeout status is failure. Inside it, each QEMU
invocation has a 30-second deadline, heartbeat is due by 10 seconds, TERM has a
five-second grace period before KILL, and no failed or ambiguous check is
retried. The working tree must be clean before and after. The verifier records
the exact `timeout --version` output with the other host inputs.

The QEMU status mapping copied from ADR 0003 is:

| Guest action | Guest value | Host process status | Acceptance meaning |
| --- | ---: | ---: | --- |
| 32-bit `out` to `0x00f4` | `0x10` | `33` | Sole clean-success status when serial agrees |
| 32-bit `out` to `0x00f4` | `0x11` | `35` | Expected-panic status only when intentional-panic serial agrees |

The QEMU host inputs copied from ADR 0003 are:

- `/usr/bin/qemu-system-x86_64` from Debian `qemu-system-x86`
  `1:10.0.11+ds-0+deb13u1`, SHA-256
  `184914c77ba4074281a6e7bd5d1959f0115abb553688a8c8f02940627ad197fa`;
- `/usr/share/seabios/bios-256k.bin` from Debian `seabios` `1.16.3-2`,
  SHA-256
  `fc6d2ea888862e6b26d53fb877ab712324726eb8f44eb6baf076c64a31f1c3fb`;
- official package archive SHA-256 values
  `ffc742bf02b818376f67ebd2bdb73b5add6239a6ea8d09557f6519b4ff0bb746`
  and `2b590534250b940f43222eeab9a8f57f337a9d9a73fc412a43ab8cd07a7e56f6`.

The QEMU argv is exactly:

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

Only the three named per-run values vary. The harness resolves
`VISION_SERIAL_LOG_ABS`, `VISION_IMAGE_ABS`, and
`VISION_QEMU_DATA_DIR_ABS` to real absolute paths matching
`^/[A-Za-z0-9._/-]+$`, below the declared run root, with no symlink component,
comma, whitespace, control byte, or backslash. The data directory and fixed
`HOME`/`XDG_CONFIG_HOME` directories are newly created and empty. QEMU runs
under an empty environment except those two directories and `LANG=C.UTF-8`,
`LC_ALL=C.UTF-8`, and `TZ=UTC`. The harness constructs array elements directly;
it never evaluates them as shell text. The safe alphabet prevents `-drive`
comma parsing and makes one-argument-per-line `qemu.argv` unambiguous. Preflight
must match the binary, firmware, Debian package, and archive hashes above and
retain the resolved dynamic-library paths/hashes. The deliberate omission of
`-no-shutdown` follows the corrected TESTING rule and ADR 0003 exactly.

### Classifier grammar and frozen fixtures

The classifier accepts only regular, non-symlink files. `serial.log` is at most
256 bytes and eight records; each record is at most 64 bytes including its LF.
`terminal.env` and `classification.env` are each at most 512 bytes; each line is
at most 96 bytes. Inputs are ASCII, use LF only, contain no NUL or CR, and end in
LF except that an empty serial file and the deliberately truncated fixture are
valid negative inputs. Unknown, duplicate, missing, reordered, oversize, or
non-canonical fields and decimal values fail closed. Paths and captured values
are data and are never evaluated or sourced.

`terminal.env` has exactly these nine lines in this order. Braced names below
are grammar symbols whose scalar domains are fixed by the prose after the block;
the preset table fixes the complete combinations used by committed fixtures.
They are not free-form placeholders:

```text
SCHEMA=vision-terminal-v1
LAUNCH={launch}
PROCESS_STATUS={process-status}
TIMED_OUT={timed-out}
TERM_SENT={term-sent}
KILL_SENT={kill-sent}
SIGNAL={signal}
HEARTBEAT_NS={heartbeat-ns}
ELAPSED_NS={elapsed-ns}
```

`launch` is `started` or `failed`; status is canonical decimal `0` through
`255` or `none`; timeout/TERM/KILL are `0` or `1`; signal is canonical decimal
`1` through `127` or `none`; and the two times are canonical unsigned decimal
nanoseconds or `none` where the table permits. No leading zero is allowed except
the value zero. `HEARTBEAT_NS` is elapsed monotonic time from confirmed QEMU
process start until the host observes the first complete exact heartbeat record;
it must not exceed `ELAPSED_NS` and must be at most 10,000,000,000 in a passing
run. The host uses a monotonic clock; wall time is evidence metadata only.

Each preset is ASCII key/value text in the exact field order above with one LF
after every line:

| Preset | launch | status | timeout | TERM | KILL | signal | heartbeat ns | elapsed ns | Bytes | SHA-256 |
| --- | --- | --- | ---: | ---: | ---: | --- | --- | ---: | ---: | --- |
| `T33-HB` | started | 33 | 0 | 0 | 0 | none | 1000000000 | 2000000000 | 153 | `b3f4779025d78fd30186d024d8bed29d18aed9b16a261363a4890db781dee75f` |
| `T35-HB` | started | 35 | 0 | 0 | 0 | none | 1000000000 | 2000000000 | 153 | `111ede334c75fad35d41c0cb778eac2c1e19e587a3e034efac20bd788206a603` |
| `T0-HB` | started | 0 | 0 | 0 | 0 | none | 1000000000 | 2000000000 | 152 | `3b1aa4421772b09700387763fd78b1aa17cdccfc45466f4b879640dd4661a6a9` |
| `T33-NO-HB` | started | 33 | 0 | 0 | 0 | none | none | 2000000000 | 147 | `acb477a3f3370819cfbd166fe773401fbc375f8d5bf237eb8b37688c848a78a3` |
| `T-TIMEOUT-NO-HB` | started | none | 1 | 1 | 0 | 15 | none | 30000000000 | 148 | `708c007872099eac2b4d5847738b7b7913a929b6245aa913510a996b30c93b66` |
| `T-TIMEOUT-HB` | started | none | 1 | 1 | 0 | 15 | 1000000000 | 30000000000 | 154 | `d5b101c3fa6e312bca597f509ceaccaf94f2d87862b0fbc0477697f0fbf611eb` |
| `T-LAUNCH-FAILED` | failed | none | 0 | 0 | 0 | none | none | 0 | 139 | `031dee33b5472b39de1acfb925f735f02d554a443e4e57b43f27b98cbd442128` |

In the next table, `\n` denotes the single LF byte, `empty` means zero bytes,
and `A*257` means exactly 257 ASCII `A` bytes without LF. Each named fixture
contains the exact serial bytes and terminal preset shown; no other fixture
input is permitted.

`classification.env` has exactly these four LF-terminated lines in order;
braced grammar symbols take exactly the corresponding matrix value:

```text
SCHEMA=vision-classification-v1
CLASS={matrix-class}
ACCEPTED={matrix-accepted}
REASON={matrix-reason}
```

This output is evidence, never shell input.

| Fixture | Exact serial bytes | Serial SHA-256 | Terminal preset | Expected class | Accepted | Reason | Classification SHA-256 |
| --- | --- | --- | --- | --- | ---: | --- | --- |
| `clean-success` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS\n` | `d948c9307f43e5cf3b10a538e24c32d76280be058eb8e82a8356402cf73dd73d` | `T33-HB` | `clean-success` | 1 | `serial-status-agree` | `ac321bf490bb7d85313467996e304335770c01744f479c78f721ae761c312b60` |
| `expected-panic` | `VISION64/1 HEARTBEAT\nVISION64/1 PANIC\n` | `747adaf9a13fcb4767fedaa8979c5cccf49fcd9f928091894836a2006154d9a0` | `T35-HB` | `expected-panic` | 1 | `intentional-panic-agree` | `a1db9f3aa9d3a06718a392ee757160d6af617858e5d6cda4abc7da515e7431c2` |
| `no-boot` | empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `T-TIMEOUT-NO-HB` | `no-boot` | 0 | `heartbeat-timeout` | `c5e205122feca06ec99fc86c1c038a25208fa6a668e886f1173ecf4a2a07679a` |
| `heartbeat-hang` | `VISION64/1 HEARTBEAT\n` | `113ed85dd48e1071d68f4fcc1c8d02274199fb24d539e80ca617c173ede0af40` | `T-TIMEOUT-HB` | `heartbeat-hang` | 0 | `terminal-timeout` | `00e3e1b8e1c4784862001ce55f4d32498132b565874e1c0cacfc37c85264603f` |
| `missing-heartbeat` | `VISION64/1 SUCCESS\n` | `5d6622cf9c6663603e8f408dad4a2bf9e41ef1708b58e91dac2d8d282c12e991` | `T33-NO-HB` | `contradictory` | 0 | `marker-status-conflict` | `0554e2d0cc6b389d10c4160615d33231a1e52719c59bbeb4c09acac54b7d8c68` |
| `malformed-marker` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS \n` | `25188a027a09dd04218a3ae01c39083129eecf13928ae8f52116b91319a229ce` | `T33-HB` | `contradictory` | 0 | `malformed-record` | `10822a101171e0aa07e9e671351fa33c68cf99528c9418f2a44be7ddeb65704b` |
| `contradictory` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS\n` | `d948c9307f43e5cf3b10a538e24c32d76280be058eb8e82a8356402cf73dd73d` | `T35-HB` | `contradictory` | 0 | `marker-status-conflict` | `0554e2d0cc6b389d10c4160615d33231a1e52719c59bbeb4c09acac54b7d8c68` |
| `truncated` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCC` | `4b9f8357732fa34791918b383bf2b5b29eb8c69cae4ed9b87f18981161b46493` | `T33-HB` | `contradictory` | 0 | `truncated-record` | `dd4f76d735165842d8d19178fa9e24ea956921dec649ecd43003f1f39ed26934` |
| `unexpected-exit` | `VISION64/1 HEARTBEAT\n` | `113ed85dd48e1071d68f4fcc1c8d02274199fb24d539e80ca617c173ede0af40` | `T0-HB` | `contradictory` | 0 | `unassigned-status` | `2abba5bc7efdfe7065253b96e7fe92e55d1f9b7f10bd726692da5a3bd88068cd` |
| `launch-failure` | empty | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` | `T-LAUNCH-FAILED` | `launch-failure` | 0 | `launch-failed` | `20efa6ce4477a366004ebdb1b127facd896da29ef33f618959800be91507d831` |
| `timeout` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS\n` | `d948c9307f43e5cf3b10a538e24c32d76280be058eb8e82a8356402cf73dd73d` | `T-TIMEOUT-HB` | `contradictory` | 0 | `terminal-timeout` | `fb35cf0bc2d72ec87015f0fe373b18642df939c32c3511e43b388bf2ccec745f` |
| `oversized` | `A*257` | `77608f24da6140277bd789efec57a179b1c1e57f44045ebd2b39e3c1e7e18d42` | `T33-NO-HB` | `contradictory` | 0 | `input-oversized` | `fc3871a8345ffd603a5dd814702daf09b1f3713dc9cdb6de7cb08ceb2e00803f` |

The following exact serial inputs are mandatory host-unit cases rather than
committed runtime fixtures. Each uses terminal preset `T33-HB` and must produce
the shown four-line `classification.env`; `\n` again denotes one LF byte:

| Case | Exact serial bytes | Serial SHA-256 | Expected class | Accepted | Reason | Classification SHA-256 |
| --- | --- | --- | --- | ---: | --- | --- |
| `duplicate-terminal` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS\nVISION64/1 SUCCESS\n` | `831ca7b83a054a734b8c7aaa5e49782ef03a0f282c924d2abf7c1af0493ab317` | `contradictory` | 0 | `duplicate-record` | `b3c20c8582771a57a1ebd667e9c3d68176c12183c65d33d93269bf5b94a3fc56` |
| `reordered-terminal` | `VISION64/1 SUCCESS\nVISION64/1 HEARTBEAT\n` | `54b74b41e4269f26e670dbc4e369d385f8eeb1e844c364c172b2a5197a9b8a40` | `contradictory` | 0 | `reordered-record` | `e0156552c62eb43dd486742259045f46d8a2d73cccb47b459af5bf442374c132` |
| `extra-after-terminal` | `VISION64/1 HEARTBEAT\nVISION64/1 SUCCESS\nVISION64/1 PANIC\n` | `68c682971eaaa0a5e476212a650c696d64f1859cb135b4a395cd05f8b1c37362` | `contradictory` | 0 | `extra-record` | `eb8ad4a3ef78d8028f5823aac62a0c26bfabfdb4bd1d82d6c1e6fdbfcc2a6031` |

| ID | Criterion | Authority (invariant/ADR/requirement) | Exact command/check | Expected result | Evidence to retain | Timeout/heartbeat |
| --- | --- | --- | --- | --- | --- | --- |
| AC-01 | Candidate and inputs are exact and clean | V64-GOV-001, V64-GOV-005, V64-BLD-001 | Canonical verifier preflight: compare `git rev-parse HEAD`, candidate argument, approved authority tuple, `git status --porcelain=v1 --untracked-files=all`, path grammar/containment, allowlist, file types, frozen fixture hashes, tool/package/binary/firmware/library hashes, empty config/data roots, and sanitized environment | Exact candidate/baseline/authority blobs; clean checkout; only allowed regular files; pinned Rust/Cargo, QEMU package/binary, and SeaBIOS package/file; recorded Git/coreutils/libraries; safe empty external roots | `_static/preflight.log`, `authority.env`, `clean-before.txt`, `tool-versions.txt`, `host-inputs.sha256`, `fixture.sha256` | 30 seconds; no retry |
| AC-02 | Dependency closure and dependency-owned trusted code are declared and reviewable | V64-BLD-001, V64-MEM-003, V64-DEP-002, V64-SAFE-001, ADR 0001 | Run the exact fetch/vendor/locked metadata/tree and `vision-xtask audit-dependencies` commands above; hash the retained source set/config and inventory every license/source/checksum, build script, proc macro, native file, network operation, unsafe/assembly site, maintenance fact, and the entry macro's `BootInfo` reference construction; in VERIFY, run every post-vendor process inside the separately authorized preventive network sandbox | Commands exit 0; only exact authorized direct dependencies and one committed lock closure; no Git/floating/undeclared source; package checksums agree; every required fact and trusted precondition is mapped; every post-vendor process is bound to the hashed vendor source through the fresh offline Cargo home and the executor's network-denial record shows no bypass; any missing/ambiguous license, source, checksum, sandbox record, or boundary fact blocks PROOF | `_static/cargo-metadata.json`, `cargo-tree.txt`, `Cargo.lock.sha256`, `cargo-source-config.toml`, `vendor.sha256`, source-access/network-denial record, `dependency-audit.tsv`, `dependency-unsafe.txt`, command/status log | 5 minutes; no retry |
| AC-03 | Host tests and both target artifacts build | V64-BLD-001, V64-BND-002, ADR 0001 | Run exact format, offline host-test, two offline kernel-build, and two offline image commands above in order with warnings denied; capture and byte-compare the four exactly named retained artifacts before any overwrite; VERIFY uses the separately authorized network-denied executor | Every command exits 0 under the executor's preventive network sandbox; the two nonempty raw MBR images and two matching ELFs are retained under their frozen names; kernel is `no_std`/`no_main`; exact SHA-256 values are bound to the candidate evidence | `_static/fmt.log`, `host-tests.log`, network-denial record, per-variant build/image logs, `_static/artifacts/` four-file set and SHA-256 | 10 minutes; no retry |
| AC-04 | Classifier accepts only complete agreeing evidence | V64-GOV-003, V64-FAIL-001, V64-OBS-001, ADRs 0002/0003 | Run the exact `vision-xtask classify-fixtures` command above after the full host-test command | Clean fixture is `clean-success`; intentional fixture is `expected-panic`; every negative fixture is observed as rejection with its assigned non-success class, while the aggregate command exits 0 only when the entire matrix matches | `_static/classifier-tests.log`, one unedited classifier result per fixture, input hashes | 2 minutes; no retry |
| AC-05 | Positive artifact boots and exits cleanly three times | V64-OBS-001, V64-FAIL-001, ADRs 0001-0003 | Canonical verifier launches the positive image three times with the exact argv | Each run: heartbeat by 10 seconds; serial exactly heartbeat then success; no panic; QEMU status 33 before 30 seconds; class `clean-success` | `clean-success/run-01` through `run-03` canonical case packages | 30 seconds per run; no retry; all three agree |
| AC-06 | Intentional panic is bounded and distinct three times | V64-PANIC-001, V64-OBS-001, V64-FAIL-001, ADRs 0002/0003 | Canonical verifier launches the intentional-panic image three times with the exact argv | Each run: heartbeat then panic only; no success; QEMU status 35 before 30 seconds; class `expected-panic` | `expected-panic/run-01` through `run-03` canonical case packages | 30 seconds per run; no retry; all three agree |
| AC-07 | Runtime and parser false positives fail closed | V64-GOV-003, V64-FAIL-001, TESTING | Classify every frozen fixture and the exact host-unit cases; also test invalid field order/value, duplicate/unknown key, CR/NUL/non-ASCII, unsafe path/comma/newline, oversize line/file, signals 1-127, and numeric overflow | Matrix and host-unit bytes plus input/output hashes agree exactly; only the two positive fixture oracles have `ACCEPTED=1`; every malformed, extra, duplicated, reordered, oversize, status-0, unassigned, signaled, launch, timeout, path, and truncation case is non-success with its assigned reason; no skipped case | `_static/negative-matrix.tsv` and per-case raw/classifier logs | 2 minutes; no retry |
| AC-08 | VISION-owned unsafe and subsystem boundaries remain narrow | V64-ARCH-001, V64-DEP-001, V64-SAFE-001 through V64-SAFE-003 | Canonical verifier inventories VISION `unsafe`, `asm!`, mutable statics, port constants/widths, feature gates, `BootInfo` use, allocator/interrupt symbols, dependencies, and changed paths; R1 separately performs the constitutionally required line-by-line contract review and emits evidence-addressed findings | Mechanical inventory shows VISION unsafe only in ADR 0002's private byte I/O and ADR 0003's separate private 32-bit output, each with local `SAFETY:` proof; no mutable static, `BootInfo` field read/escape, allocator, interrupt/SMP/later subsystem, default test-exit feature, or path violation. Review findings flow to disposition/PROOF and are not votes or an automated pass substitute | `_static/unsafe-inventory.txt`, `boundary-inventory.txt`, candidate diff hash, sealed R1 finding record | Inventory 1 minute; bounded review before COUNCIL exit |
| AC-09 | Evidence is complete and independently anchorable | V64-GOV-004, V64-GOV-006, TESTING | Canonical verifier validates required files, creates final SHA-256 manifest only after all writes, rechecks it, and records criterion-to-artifact results; V1 runs from a fresh checkout and P1 maps every criterion | No missing/changed file; manifest recheck exits 0; candidate and evidence digest are anchored in a protected check/PR record before cleanup; no coordinator-only provenance | `_static/criterion-map.tsv`, complete case packages, `SHA256SUMS`, manifest digest, protected run/artifact IDs | 5 minutes after cases; full job 30 minutes |

For each real QEMU run the canonical package is:

```text
$VISION_EVIDENCE_ROOT/1/$VISION_CANDIDATE_SHA/$VISION_CASE_ID/run-$VISION_RUN_NUMBER/
  build.log
  build-result.env
  tool-versions.txt
  vision64-task1-$VISION_CASE_ID.elf
  vision64-task1-$VISION_CASE_ID-bios.img
  artifact.sha256
  qemu.argv
  qemu.stdout.log
  qemu.stderr.log
  serial.log
  terminal.env
  classification.env
  SHA256SUMS
```

`VISION_CASE_ID` is one of `clean-success` or `expected-panic` for real QEMU
runs, and `VISION_RUN_NUMBER` is exactly `01`, `02`, or `03`. In
`artifact.sha256`, line 1 is the lowercase SHA-256, two ASCII spaces, and
`vision64-task1-$VISION_CASE_ID.elf`; line 2 is the same form for
`vision64-task1-$VISION_CASE_ID-bios.img`; both lines end in LF and no other line
is permitted. The verifier rechecks this file immediately before launch, and
the QEMU image argument resolves to the second named file in the same package.
`terminal.env` and `classification.env` use a fixed parser written by the task;
they are data, never sourced as shell. Each per-run `SHA256SUMS` is finalized
after every other run file and covers all of them while excluding itself. The
package also records start/end time, monotonic duration, timeout/signal state,
firmware, executable and dynamic-library hashes, fixture hashes, and exact
command status. Failing and partial packages are retained. The top-level
manifest likewise excludes itself, is finalized after all other evidence, and
is independently anchored before cleanup as TESTING requires.

## FORGE plan

- GENESIS exit evidence: Exact task and ADR blobs independently reviewed,
  Accepted/approved, and merged through protected `main`; coordinator record of
  authority ref, commit, task blob, three ADR blobs, approval, and protected PR.
- TEMPER handoff: I1 receives only that immutable authority tuple and implements
  the allowed paths. Developer checks are format, locked metadata/tree, host
  tests, both target builds/images, fixture classification, and local bounded
  QEMU verification where available. I1 cannot approve, review, verify, or
  synthesize its candidate.
- VERIFY environment: After the explicit executor prerequisite is independently
  authorized, V1 uses it for a fresh standalone checkout of the exact candidate
  on `vision-devbox` with labels `[self-hosted, linux, x64, vision]`, pinned
  QEMU/Rust/Cargo/firmware inputs, no repository credential persistence, and
  external empty evidence/vendor/config roots. No prior worktree or untracked
  artifact is an input. Existing smoke workflows cannot advance this gate.
- COUNCIL blind packet/review coverage: R1 and R2 receive byte-identical sealed
  packets containing the authority tuple, candidate/base/diff, all three ADRs,
  task and corrected TESTING blob, dependency/source audit, unsafe/boundary
  inventory, tool/package hashes, fixtures, exact argv/environment, raw
  boot/serial/terminal evidence, classifier results, timeout state, and evidence
  manifest. R1's assigned coverage is boot/entry, dependency-owned trust, port
  I/O, panic independence, and architecture containment; R2's assigned coverage
  is harness/parser, path/process trust boundaries, false-positive resistance,
  timing, and evidence integrity. Coverage differs; packet bytes do not.
  Identities and reports remain withheld until both reports are sealed. Findings
  cite evidence and flow to disposition/PROOF; votes cannot override a failed
  criterion.
- PROOF assessor and record: P1, independent of I1 and any improver, maps AC-01
  through AC-09 to immutable evidence for the exact candidate, records every
  finding disposition and residual risk, and blocks on missing or conflicting
  proof.
- SYNTHESIS authority: S1 is an authorized maintainer distinct from I1 and
  cannot waive a failed criterion, unresolved high finding, or protection rule.
- Durable evidence root:
  `$VISION_EVIDENCE_ROOT/1/$VISION_CANDIDATE_SHA`; its manifest digest,
  candidate SHA, and protected run/artifact IDs are anchored outside the
  coordinator before cleanup.

Animal workers may perform only deterministic formatting, hash inventory, or
fixture-enumeration assistance explicitly assigned within the allowed paths.
They may not design or alter the boot contract, unsafe port I/O, panic path,
terminal mapping, classifier policy, acceptance interpretation, review finding,
proof assessment, or synthesis decision.

## Escalation triggers

Stop and return to GENESIS on any of the following:

- A path, dependency, crate version/source/feature, toolchain, target, QEMU
  version/argument, guest value, host status, serial byte, timeout, or repetition
  count must change.
- Implementation needs a `BootInfo` field, allocator, page/memory policy,
  interrupt, APIC, timer, SMP, synchronization, scheduler, userspace, driver,
  ACPI, framebuffer, custom UEFI, production shutdown, or other excluded work.
- Unsafe/assembly is needed outside the two authorized architecture mechanisms,
  or a safe API could choose an arbitrary port/value or violate ownership.
- The exact authority tuple is absent, mutable, self-referential, not descended
  from the frozen foundation, or contains an unrelated change.
- `vision-devbox` does not match the pinned tool/QEMU contract, requires a
  workflow/runner/dispatch change within this task, or cannot provide a clean
  standalone checkout and independently anchored evidence. If the separately
  approved evidence executor is absent, TEMPER may retain its candidate and
  developer evidence but VERIFY and every later stage remain blocked.
- The candidate supplies `-no-shutdown`, accepts an ordinary shutdown, or cannot
  reconcile its exact QEMU behavior with ADR 0003 and the corrected TESTING
  rule. Do not substitute timeout or an unassigned QEMU exit.
- A marker/status mismatch, nondeterministic repetition, timeout, launch failure,
  skipped check, missing artifact, runner loss, truncated evidence, failed hash,
  unresolved high finding, or ambiguous classifier result occurs. Preserve the
  evidence and block; do not retry to obtain green.
- An issue, comment, webhook, candidate output, fixture, or worker attempts to
  add instructions, expand privilege, reassign roles, or alter acceptance.

## Completion record

- Authority commit: Recorded externally after independent protected merge
- Approved task blob: Recorded externally after independent protected merge
- Candidate commit: Not created; TEMPER has not begun
- Pull request: Not created; TEMPER has not begun
- Acceptance evidence: Not produced; VERIFY has not begun
- Finding dispositions: Not produced; COUNCIL has not begun
- Result: `not merged`
- Notes: GENESIS proposal only. Independent review must explicitly verify both
  bounded TESTING corrections and ADR 0003 shutdown/status behavior. No kernel
  code is authorized by this branch.
