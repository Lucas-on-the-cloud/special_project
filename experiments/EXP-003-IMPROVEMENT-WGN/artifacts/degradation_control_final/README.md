# degradation_control_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `degradation_control` |
| Completed epochs | 25 |
| Best epoch | 9 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `b5e84a649a0c1aad1d8d81604f58cb04aa0b044c` |
| Training manifest SHA-256 | `f401d2b1ca01ee745b5c6d7b7020344e9cf4a7320afbbdab4658f86ed560efbe` |
| Checkpoint SHA-256 | `0873737be16e0d35f28a60498aae7f639294e8f32bc1a6869b90e8ca893b07ec` |

The selected `best.pt` is stored in the public Hugging Face model repository. Download it from [Hugging Face](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/degradation_control_final/best.pt) without authentication, then verify the SHA-256 above. `CHECKPOINT.json` records the stable remote path and download URL. `last.pt` remains local unless an unfinished run must be moved.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
