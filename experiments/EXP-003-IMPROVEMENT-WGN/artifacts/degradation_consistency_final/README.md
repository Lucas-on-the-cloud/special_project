# degradation_consistency_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `degradation_consistency` |
| Completed epochs | 25 |
| Best epoch | 9 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `fda5760784306315d41718fb4022cfbd04529210` |
| Training manifest SHA-256 | `f401d2b1ca01ee745b5c6d7b7020344e9cf4a7320afbbdab4658f86ed560efbe` |
| Checkpoint SHA-256 | `ea4aa65d629f0f0aff515408c9f56f22ea743399c20a6ae7d25b352d1f1f4da0` |

The selected `best.pt` is stored in the public Hugging Face model repository. Download it from [Hugging Face](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/degradation_consistency_final/best.pt) without authentication, then verify the SHA-256 above. `CHECKPOINT.json` records the stable remote path and download URL. `last.pt` remains local unless an unfinished run must be moved.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
