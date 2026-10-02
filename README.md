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

## 18-week timeline

| Week | Main work | Weekly deliverable | Status |
|---:|---|---|---|
| 01 | Begin the five papers cited in the progress report: Fairness Analysis, FaceForensics++, FreqDebias, Synergistic Fairness Optimization, and UCF | First-pass notes identifying each paper's problem, method, dataset, metrics, and limitations | ✅ Completed |
| 02 | Finish the same five cited papers; connect generalization, compression, spectral bias, and demographic fairness | Week 1–2 progress report | ✅ Completed |
| 03 | Begin the five sources newly assigned by the professor: NTIRE 2026, DFD-HR, VRAG-DFD, domain-incremental curriculum learning, and WGN | Initial notes plus code, checkpoint, dataset, and compute audit | ✅ Initial review completed |
| **04** | Continue reading the same five Week 3 sources; study DFD-HR and WGN more deeply | Five structured notes, comparison matrix, and Week 5 reproduction decision | 🚧 In progress |
| 05 | Select the first reproducible paper and inspect its repository, checkpoint, preprocessing, and dataset requirements | Kaggle environment, dataset-access record, and 10–50 sample inference test | ⬜ Pending |
| 06 | Study dataset protocol and leakage risks; reproduce pretrained inference or a short evaluation | `EXP-001` baseline smoke test and Kaggle notebook | ⬜ Pending |
| 07 | Run the selected baseline on a fixed validation subset | `EXP-002` baseline AUC, accuracy, runtime, seed, and sample-count table | ⬜ Pending |
| 08 | Study robustness literature and the NTIRE degradation setting | `EXP-003` JPEG/resize/blur robustness curves and failure analysis | ⬜ Pending |
| 09 | Study cross-dataset and cross-manipulation protocols | `EXP-004` source-domain versus held-out-domain result table | ⬜ Pending |
| 10 | Analyze false positives, false negatives, confidence, quality, and manipulation types | Error-analysis report and one frozen improvement hypothesis | ⬜ Pending |
| 11 | Deep-read the selected improvement paper; likely frequency/wavelet guidance if supported by Week 10 | `EXP-005` improvement v1 implementation and smoke test | ⬜ Pending |
| 12 | Train or tune the improvement using the same controlled baseline protocol | `EXP-006` baseline-versus-improvement comparison | ⬜ Pending |
| 13 | Study and run component ablations; repeat important runs when feasible | `EXP-007` ablation table with multiple seeds or an explicit single-run limitation | ⬜ Pending |
| 14 | Revisit fairness literature and verify whether trustworthy demographic metadata exists | `EXP-008` subgroup AUC/FPR/FNR audit, or a documented decision not to make demographic claims | ⬜ Pending |
| 15 | Evaluate efficiency, calibration, and practical deployment constraints | `EXP-009` accuracy–robustness–efficiency comparison | ⬜ Pending |
| 16 | Lock the protocol and run the final evaluation without tuning on test results | Final tables, plots, configs, and artifact manifest | ⬜ Pending |
| 17 | Build an application-oriented Kaggle demo and write the research report | End-to-end demo plus report draft | ⬜ Pending |
| 18 | Perform citation, claim, and reproducibility audits; prepare the defense | Final report, presentation, repository release, and clean-session verification | ⬜ Pending |

The detailed checklist and decision rules remain available in [`docs/project-plan-18-weeks.md`](docs/project-plan-18-weeks.md).

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
