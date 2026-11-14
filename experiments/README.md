# Experiments

Each experiment owns its code, protocol, compact results, and selected portable
artifacts. Datasets and generated face crops remain outside Git.

| ID | Purpose | Status |
|---|---|---|
| [EXP-001-DFD-HR](EXP-001-DFD-HR/) | DFD-HR reproduction planning | Deferred |
| [EXP-002-WGN](EXP-002-WGN/) | Independent WGN reproduction and frozen reference checkpoint | Main/cross-dataset/cross-manipulation reproduction complete |
| [EXP-003-IMPROVEMENT-WGN](EXP-003-IMPROVEMENT-WGN/) | WGN generalization improvements and ablations | Completed candidates retained as project context |
| [EXP-004-ADVERSARIAL-WGN](EXP-004-ADVERSARIAL-WGN/) | Apply prior-paper adversarial mechanisms to frozen EXP-002 WGN and measure vulnerability/mechanism | V2 protocol/code/tests prepared; laboratory GPU evaluation pending |
| [EXP-005-ROBUST-WGSA](EXP-005-ROBUST-WGSA/) | Candidate adversarial-defense module integrated with WGSA | Prototype/hypothesis only; blocked on EXP-004 evidence |

## Research dependency

EXP-002 is the frozen reproduced baseline. EXP-003 explores generalization
improvements. EXP-004 opens a separate adversarial-resilience branch by
challenging EXP-002 with paper-grounded attacks. EXP-005 is conditional: a
defense architecture should be developed and claimed only after EXP-004
establishes a reproducible vulnerability and mechanism worth targeting.

Raw datasets, generated crops and checkpoints are never stored in ordinary Git
history; follow the repository checkpoint/data handoff policies.
