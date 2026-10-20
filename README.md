# Generalizable Deepfake Detection

Research repository for reproducing WGN and testing changes intended to improve
generalization across datasets, manipulation methods, and compression levels.

## Repository layout

```text
special_project/
├── README.md
├── docs/                           project plans, literature, and research notes
└── experiments/
    ├── EXP-001-DFD-HR/             deferred DFD-HR reproduction work
    ├── EXP-002-WGN/                WGN reproduction and frozen reference
    └── EXP-003-IMPROVEMENT-WGN/    WGN improvement experiments
```

## Active experiments

### EXP-002 — WGN reproduction

[`experiments/EXP-002-WGN/`](experiments/EXP-002-WGN/) owns the independently
reproduced WGN reference. Its configuration, metrics, checksum, and checkpoint
pointer are stored with the experiment; the weights are in the private
Hugging Face model repository.

The main and cross-dataset rerun is complete. Cross-manipulation for this exact
current checkpoint remains pending. Results from the earlier RTX 5090 machine
are retained as historical evidence because its checkpoint was not preserved.

### EXP-003 — WGN improvement

[`experiments/EXP-003-IMPROVEMENT-WGN/`](experiments/EXP-003-IMPROVEMENT-WGN/)
contains all improvement code, configurations, reports, and candidate
checkpoints. Gradient fusion, curriculum learning, temporal consistency, and
the temporal sampling control are complete. Degradation robustness experiments
are running.

The current comparison is available in
[`THREE-EXPERIMENT-COMPARISON.md`](experiments/EXP-003-IMPROVEMENT-WGN/results/THREE-EXPERIMENT-COMPARISON.md).

## Artifact policy

Selected inference checkpoints are uploaded to the private Hugging Face model
repository [`lucashwang0102/wgn-checkpoints`](https://huggingface.co/lucashwang0102/wgn-checkpoints).
Each GitHub artifact directory contains `CHECKPOINT.json` with its remote path,
URL, size, and SHA-256, plus the configuration, environment, metrics, and
evaluation files. Raw datasets, videos, generated face crops, model weights,
and repeated optimizer-state snapshots are not stored in normal Git history.

The required backup, GitHub publication, and machine-restoration procedure is
defined in
[`docs/experiment-backup-and-machine-handoff.md`](docs/experiment-backup-and-machine-handoff.md).
Direct checkpoint links and restore commands are in
[`docs/private-checkpoint-handoff.md`](docs/private-checkpoint-handoff.md).
The separately stored processed datasets can be restored from the authorized
private Hugging Face backup by following
[`docs/private-processed-data-handoff.md`](docs/private-processed-data-handoff.md).

All active work is committed directly to `main`.
