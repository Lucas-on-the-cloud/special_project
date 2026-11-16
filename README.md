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
    ├── EXP-003-IMPROVEMENT-WGN/    WGN improvement experiments
    └── EXP-004-ADVERSARIAL-WGN/    Frozen-WGN adversarial evaluation
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

### EXP-004 — adversarial evaluation of frozen WGN

[EXP-004](experiments/EXP-004-ADVERSARIAL-WGN/) completed four methods on all
325,554 processed test frames across FF++ c23, DFDC, Celeb-DF-v2 official-direct
and WildDeepfake. The frozen checkpoint and attack settings are recorded with
clean-reference gates, source/cohort checksums and completed audits.

| Full test dataset | FAA flips / eligible Fake | FAA ASR |
|---|---:|---:|
| FF++ c23 | 2,731/5,333 | 51.21% |
| DFDC | 36,072/42,932 | 84.02% |
| Celeb-DF-v2 official-direct | 7,946/8,278 | 95.99% |
| WildDeepfake | 82,059/88,521 | 92.70% |

[Complete tables and full-precision CSV](experiments/EXP-004-ADVERSARIAL-WGN/results/tables/README.md)
cover all 16 dataset/method combinations, frame/video metrics, quality, compute,
manipulations and mechanism diagnostics. See the
[overview](experiments/EXP-004-ADVERSARIAL-WGN/results/cross-dataset-overview.md)
and [validation bundle](experiments/EXP-004-ADVERSARIAL-WGN/validation/README.md).
FAA is an explicit Jia reconstruction, not author-verified exact reproduction;
ASR conditions on clean-correct Fake. Pixel/DCT budgets are different units,
and feature drift alone does not establish causal WGSA weakness.

## Artifact policy

Selected inference checkpoints are uploaded to the public Hugging Face model
repository [`lucashwang0102/wgn-checkpoints`](https://huggingface.co/lucashwang0102/wgn-checkpoints).
Each GitHub artifact directory contains `CHECKPOINT.json` with its remote path,
URL, size, and SHA-256, plus the configuration, environment, metrics, and
evaluation files. Raw datasets, videos, generated face crops, model weights,
and repeated optimizer-state snapshots are not stored in normal Git history.

The required backup, GitHub publication, and machine-restoration procedure is
defined in
[`docs/experiment-backup-and-machine-handoff.md`](docs/experiment-backup-and-machine-handoff.md).
Direct checkpoint links and restore commands are in
[`docs/checkpoint-handoff.md`](docs/checkpoint-handoff.md).
The separately stored processed datasets can be restored from the authorized
private Hugging Face backup by following
[`docs/private-processed-data-handoff.md`](docs/private-processed-data-handoff.md).

All active work is committed directly to `main`.
