# EXP-003 — WGN improvement experiments

This experiment tests changes intended to improve the cross-dataset and
compression generalization of the WGN model reproduced in EXP-002.

## Layout

```text
EXP-003-IMPROVEMENT-WGN/
├── code/       training, evaluation, queue, configs, and verification
├── docs/       protocol and operating notes
├── results/    comparison reports and machine-readable summaries
├── artifacts/  private-checkpoint pointers and final-run metadata
└── PLAN.md     hypotheses, protocol, and selection rule
```

The common reference checkpoint is owned by
[`../EXP-002-WGN/reproduction/artifacts/baseline_final/`](../EXP-002-WGN/reproduction/artifacts/baseline_final/).
EXP-003 stores candidate and ablation metadata plus `CHECKPOINT.json` pointers
in its own `artifacts/` directory. The weight files are in the private Hugging
Face model repository `lucashwang0102/wgn-checkpoints`.

Every completed final run is packaged using the repository
[experiment backup and machine handoff policy](../../docs/experiment-backup-and-machine-handoff.md).
The portable run index is maintained in
[`results/EXPERIMENT-REGISTRY.md`](results/EXPERIMENT-REGISTRY.md).
The machine-readable finalist decision is maintained in
[`results/CANDIDATE-SELECTION.json`](results/CANDIDATE-SELECTION.json). A
separate resume-safe runner waits for the common sweep and the EXP-002 4 × 4
reproduction, then runs cross-manipulation only for the locked-criteria
finalists. If no candidate qualifies, it records that outcome without starting
an exploratory GPU run.

Completed candidates: gradient, curriculum, temporal consistency, and the
temporal sampling control. Degradation control and degradation consistency are
currently queued. See
[`results/THREE-EXPERIMENT-COMPARISON.md`](results/THREE-EXPERIMENT-COMPARISON.md)
for the completed comparison.
