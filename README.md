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
    ├── EXP-004-ADVERSARIAL-WGN/    Jia FAA evaluation of frozen WGN
    └── EXP-005-STATATTACK-WGN/     Hou StatAttack/MStatAttack evaluation
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

### EXP-004 / EXP-005 — adversarial evaluation

[`EXP-004`](experiments/EXP-004-ADVERSARIAL-WGN/) evaluates the frozen WGN
with Jia FAA reconstruction and pixel controls. Full FF++ c23, DFDC and
Celeb-DF-v2 official-direct and WildDeepfake are complete with audits passed.
See the [four-dataset overview](experiments/EXP-004-ADVERSARIAL-WGN/results/cross-dataset-overview.md).

[`EXP-005`](experiments/EXP-005-STATATTACK-WGN/) applies Hou2023
StatAttack/MStatAttack to the same four full processed test cohorts; all runs
and audits are complete. The attacks achieved 92.12–95.21% ASR, conditional
on clean-correct Fake frames. The complete [five-method comparison](experiments/EXP-005-STATATTACK-WGN/results/five-method-comparison.md)
includes EXP-004 FGSM, PGD and Jia FAA alongside both EXP-005 methods, with
budget and fidelity qualifications. Per-dataset results, source, tests,
configuration and [execution plan](experiments/EXP-005-STATATTACK-WGN/PLAN.md)
are in the experiment folder. The former RCWG architecture draft is preserved
in [the archive](docs/archive/exp005-rcwg-draft/ARCHIVE-NOTE.md). Both studies keep
EXP-002 weights frozen; future defense design follows the evidence rather
than the archived prototype.

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
