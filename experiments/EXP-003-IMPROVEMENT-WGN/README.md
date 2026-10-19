# EXP-003 — WGN improvement experiments

This experiment tests changes intended to improve the cross-dataset and
compression generalization of the WGN model reproduced in EXP-002.

## Layout

```text
EXP-003-IMPROVEMENT-WGN/
├── code/       training, evaluation, queue, configs, and verification
├── docs/       protocol and operating notes
├── results/    comparison reports and machine-readable summaries
├── artifacts/  final improvement checkpoints and run metadata
└── PLAN.md     hypotheses, protocol, and selection rule
```

The common reference checkpoint is owned by
[`../EXP-002-WGN/reproduction/artifacts/baseline_final/`](../EXP-002-WGN/reproduction/artifacts/baseline_final/).
EXP-003 stores only candidate and ablation checkpoints in its own `artifacts/`
directory.

Completed candidates: gradient, curriculum, temporal consistency, and the
temporal sampling control. Degradation control and degradation consistency are
currently queued. See
[`results/THREE-EXPERIMENT-COMPARISON.md`](results/THREE-EXPERIMENT-COMPARISON.md)
for the completed comparison.
