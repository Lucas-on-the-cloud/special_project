# curriculum_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `curriculum` |
| Completed epochs | 25 |
| Best epoch | 20 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `b8ede7ccca3f64179c39ad9d2cdd2974700ed31c` |
| Training manifest SHA-256 | `0ea54ffe80127c14320f6e0fe369e395ae8bff1f74d1fb6fa88cedc68c3a8907` |
| Checkpoint SHA-256 | `3af3ee3e3b8fe283a105d1b31eb8a62df90ef5c1be387a5df5d7ed8a1794da7f` |

Use `best.pt` for inference and final evaluation. `last.pt` is intentionally not committed to normal Git history because it contains optimizer state and would create large repeated blobs; use a GitHub Release asset when an unfinished run must be moved and resumed.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
