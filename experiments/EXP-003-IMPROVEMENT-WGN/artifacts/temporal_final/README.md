# temporal_final

Portable final-run package for EXP-003. This directory contains the minimum state needed to understand the run and use its selected model on another machine.

| Field | Value |
|---|---|
| Method | `temporal` |
| Completed epochs | 25 |
| Best epoch | 16 |
| Selection metric | validation accuracy |
| GPU | NVIDIA GeForce RTX 5060 Ti |
| Precision | fp32 |
| Training source commit | `477caa29f35267ad48a97c765555e47a139db108` |
| Training manifest SHA-256 | `5a80c890733faacc2401ad774c740a8476a6c0f68dc3e5d9b9cad8ec9844fbe2` |
| Checkpoint SHA-256 | `9e8918e0721f57d15335be27f0739dc633797b8e191ac31447a9db9f4be58c65` |

The selected `best.pt` is stored in the public Hugging Face model repository. Download it from [Hugging Face](https://huggingface.co/lucashwang0102/wgn-checkpoints/blob/main/experiments/EXP-003-IMPROVEMENT-WGN/artifacts/temporal_final/best.pt) without authentication, then verify the SHA-256 above. `CHECKPOINT.json` records the stable remote path and download URL. `last.pt` remains local unless an unfinished run must be moved.

Read `resolved_config.yaml`, `environment.json`, and `summary.json` first. `training.log` records the executed training command and epoch output; `evaluation.log` collects the available locked-evaluation logs. `ARTIFACT-MANIFEST.json` inventories the package and its checksums.

Repository handoff policy: [`../../../../docs/experiment-backup-and-machine-handoff.md`](../../../../docs/experiment-backup-and-machine-handoff.md).
