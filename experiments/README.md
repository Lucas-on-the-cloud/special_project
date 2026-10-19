# Experiments

Each experiment owns its code, protocol, compact results, and selected portable
artifacts. Datasets and generated face crops remain outside Git.

| ID | Purpose | Status |
|---|---|---|
| [`EXP-001-DFD-HR`](EXP-001-DFD-HR/) | DFD-HR reproduction planning | Deferred |
| [`EXP-002-WGN`](EXP-002-WGN/) | Independent WGN reproduction and frozen reference checkpoint | Main/cross-dataset rerun complete; current 4 × 4 cross-manipulation queued |
| [`EXP-003-IMPROVEMENT-WGN`](EXP-003-IMPROVEMENT-WGN/) | WGN generalization improvements and ablations | Gradient, curriculum, and temporal complete; degradation experiments running |

EXP-003 compares every candidate against the reproduced WGN checkpoint owned by
EXP-002. A runtime name such as `baseline_final` does not create a second
baseline experiment.
