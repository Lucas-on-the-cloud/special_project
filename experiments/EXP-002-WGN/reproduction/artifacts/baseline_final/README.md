# baseline_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `baseline` |
| Completed epochs | 25 |
| Best epoch | 20 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `deb2f4793b98927134404523eca2bae3782b3d9f` |
| Training manifest SHA-256 | `0ea54ffe80127c14320f6e0fe369e395ae8bff1f74d1fb6fa88cedc68c3a8907` |
| Checkpoint SHA-256 | `a914832d67de66edce3841259e03ebb85aea536e58b4d7a626ec1769acfe45e6` |

Use `best.pt` for inference and final evaluation. `last.pt` is intentionally not committed to normal Git history because it contains optimizer state and would create large repeated blobs; use a GitHub Release asset when an unfinished run must be moved and resumed.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
