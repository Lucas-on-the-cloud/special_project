# Generalizable Deepfake Detection — Capstone Project

> A research-oriented computer-vision capstone on detecting manipulated visual media.

## Project status

- **Stage:** Semester 1, Week 4 literature review
- **Current direction:** Generalizable and bias-resilient deepfake detection
- **Compute environment:** Kaggle notebooks only
- **Scope status:** Provisional — the Week 4 review will select the first reproduction target and evaluation protocol
- **Previous direction:** Parking occupancy work has been removed from the active tree and remains recoverable through Git history

## Current objective

Build a reproducible deepfake-detection project that studies performance under compression, unseen manipulation methods, and dataset shift, while treating demographic fairness as an evaluation requirement when suitable metadata is available.

The project must include:

1. public data and preferably official/public code;
2. a clearly reproduced baseline;
3. an evaluation protocol that measures generalization rather than only in-dataset accuracy;
4. one evidence-driven improvement;
5. a Kaggle-runnable pipeline and a practical demonstration.

The current evidence favors image/frame-level classification and cross-dataset evaluation. This will be frozen only after the Week 4 code and dataset feasibility review.

## Project documents

- [`docs/project-plan-18-weeks.md`](docs/project-plan-18-weeks.md): the complete 18-week plan and checklist.
- [`docs/literature-review/README.md`](docs/literature-review/README.md): literature groups and review process.
- [`docs/literature-review/week-04-paper-matrix.md`](docs/literature-review/week-04-paper-matrix.md): comparison of the five papers assigned for Weeks 3–4.
- [`docs/weekly-logs/semester-1/`](docs/weekly-logs/semester-1/): evidence and progress recorded by week.

## Decisions that must be supported by sources

| Decision | Questions to resolve |
|---|---|
| Task unit | Image, sampled video frames, or full video? |
| Dataset | Which public datasets are accessible, licensed, and realistic for Kaggle? |
| Baseline | Which paper has runnable code, pretrained weights, and clear evaluation instructions? |
| Generalization | In-dataset, cross-manipulation, cross-dataset, or unseen-generator evaluation? |
| Improvement | Spatial artifacts, frequency cues, temporal cues, augmentation, domain generalization, or another justified method? |
| Metrics | Accuracy alone or also AUC, F1, EER, calibration, latency, and robustness? |
| Application | Upload-based detector, batch analysis, or another feasible demo? |

## Research workflow

```text
Review supplied sources
        ↓
Freeze problem and evaluation protocol
        ↓
Select code-first baseline and dataset
        ↓
Reproduce on Kaggle
        ↓
Analyze failure modes and generalization gap
        ↓
Select one justified improvement
        ↓
Ablation, robustness evaluation, and demo
```

## Current scope guardrails

### In scope now

- Deepfake detection research
- Public datasets and reproducible baselines
- Kaggle-only execution
- Evidence-based experiment design
- Compact metrics, plots, configs, and reports committed to GitHub

### Not yet approved

- A particular architecture or dataset
- Deepfake generation
- Localization or segmentation of manipulated regions
- Audio deepfake detection or audio-visual fusion
- Real-time deployment claims
- A final capstone title or novelty claim

These may be added only when the literature and available code justify them.

## Repository structure

```text
special_project/
├── configs/                     # Experiment configurations
├── docs/
│   ├── literature-review/       # Source intake and paper notes
│   ├── weekly-logs/             # Weekly decisions and evidence
│   ├── meetings/                # Advisor meeting records
│   └── project-scope.md         # Current boundaries and open decisions
├── experiments/                 # One documented folder per experiment
├── notebooks/                   # Kaggle notebooks
├── results/                     # Small metrics and figures only
├── src/                         # Reusable training/evaluation code
└── requirements.txt
```

## Kaggle-only workflow

1. Notebooks are authored and committed here.
2. Training and evaluation run on Kaggle.
3. Datasets and checkpoints stay on Kaggle or approved external storage.
4. Only compact JSON/CSV metrics, selected figures, and documentation return to GitHub.

Do not commit videos, extracted frames, datasets, checkpoints, Kaggle credentials, or large archives.

## Immediate next action

Finish reading the five papers assigned for Weeks 3–4, complete their structured notes, and then make a go/no-go decision for a small Kaggle reproduction. No reproduction has been claimed yet.
