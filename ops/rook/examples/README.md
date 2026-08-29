# ROOK LINK examples

`request-v1.json` / `result-v1.json` are the proven v0 read-only probe wire examples.

`request-v2.json` / `result-v2.json` are the v1 capability-orchestration wire examples. The `111...` request commit and `222...` result head commit are deterministic full-length fixture IDs used only by contract tests; they are not live repository refs.

Live requests belong under `ops/rook/requests/` and must be located by their actual immutable commit and canonical path before Rook executes them.
