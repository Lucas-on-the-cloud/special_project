# Experiments

Each experiment owns its code, protocol, compact results, and selected portable
artifacts. Datasets and generated face crops remain outside Git.

| ID | Purpose | Status |
|---|---|---|
| [EXP-001-DFD-HR](EXP-001-DFD-HR/) | DFD-HR reproduction planning | Deferred |
| [EXP-002-WGN](EXP-002-WGN/) | Independent WGN reproduction and frozen reference checkpoint | Main/cross-dataset/cross-manipulation reproduction complete |
| [EXP-003-IMPROVEMENT-WGN](EXP-003-IMPROVEMENT-WGN/) | WGN generalization improvements and ablations | Completed candidates retained as project context |
| [EXP-004-ADVERSARIAL-WGN](EXP-004-ADVERSARIAL-WGN/) | Jia FAA plus FGSM/PGD controls on frozen EXP-002 WGN | Four full cohorts complete; audits and published result tables available |
| [EXP-005-STATATTACK-WGN](EXP-005-STATATTACK-WGN/) | Hou StatAttack/MStatAttack plus matched initialization controls | Four full cohorts complete; audits pass; five-method comparison published in results folder |

## Research dependency

EXP-002 is the frozen reproduced baseline. EXP-003 explores generalization
improvements. EXP-004 and EXP-005 challenge the frozen WGN with attacks from
two papers on the same four full processed cohorts. EXP-005's former RCWG
defense draft is archived at [ARCHIVE-NOTE](../docs/archive/exp005-rcwg-draft/ARCHIVE-NOTE.md). Any future defense study should be based on both
attack evaluations and state its own validated protocol.

Raw datasets, generated crops and checkpoints are never stored in ordinary Git
history; follow the repository checkpoint/data handoff policies.
