# gradient_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `gradient` |
| Completed epochs | 25 |
| Best epoch | 24 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `393ecbf5f9c80e8c967b5f2e4565a0d642b02262` |
| Training manifest SHA-256 | `0ea54ffe80127c14320f6e0fe369e395ae8bff1f74d1fb6fa88cedc68c3a8907` |
| Checkpoint SHA-256 | `9b372bb10f8244e3635c9c00e4d310382535cebd04b59399d34e0a054e0f52aa` |

The selected `best.pt` is stored in the private Hugging Face model repository. Download it from [Hugging Face](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/gradient_final/best.pt) after authentication, then verify the SHA-256 above. `CHECKPOINT.json` records the stable remote path and download URL. `last.pt` remains local unless an unfinished run must be moved.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
