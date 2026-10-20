# temporal_control_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `temporal_control` |
| Completed epochs | 25 |
| Best epoch | 7 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `98bf801d146c1d3195bde3f57f6e488590f4a654` |
| Training manifest SHA-256 | `0ea54ffe80127c14320f6e0fe369e395ae8bff1f74d1fb6fa88cedc68c3a8907` |
| Checkpoint SHA-256 | `4f94e5147783d103ff058ca8f805f289a8938060f5a6fdab94f6cc3351750c92` |

The selected `best.pt` is stored in the public Hugging Face model repository. Download it from [Hugging Face](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_control_final/best.pt) without authentication, then verify the SHA-256 above. `CHECKPOINT.json` records the stable remote path and download URL. `last.pt` remains local unless an unfinished run must be moved.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
