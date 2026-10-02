# Project Scope — Deepfake Detection

## Status

This document remains provisional. Weeks 1–2 reviewed the five papers cited in the progress report. Weeks 3–4 review the five newer sources assigned by the professor. Only after this two-stage literature review will the project select the exact dataset, baseline, and first reproducible experiment.

## Working title

**Generalizable and Bias-Resilient Deepfake Detection under Compression and Domain Shift**

This is a working title, not a novelty claim or final title.

## Locked constraints

- The capstone direction is deepfake detection.
- All compute-intensive work runs on Kaggle.
- Public data and papers with code are preferred because advisor support is limited.
- The first milestone must be a reproduced baseline, not a new architecture.
- Final claims must include the dataset split and evaluation setting.
- Compression or another explicit domain shift must be evaluated.
- Demographic fairness is evaluated only with valid metadata; it is not inferred from appearance.
- Large datasets, videos, extracted frames, and checkpoints remain outside GitHub.

## Open decisions

The source review must answer:

1. Is the task image-, frame-, or video-level classification?
2. Which manipulation families are included?
3. Which public dataset is the primary training benchmark?
4. Which dataset or manipulation family is held out for generalization testing?
5. Is DFD-HR checkpoint evaluation practical on Kaggle, and is the NTIRE ensemble a viable fallback or only a reference?
6. Which metrics are required by the selected literature?
7. What deployment/demo assumption is realistic?
8. Which single improvement is justified by baseline failure analysis?

## Candidate evaluation layers

These are evaluation categories to investigate, not committed experiments:

- **In-domain:** train and test under the same benchmark protocol.
- **Cross-manipulation:** test on manipulation methods excluded from training.
- **Cross-dataset:** train on one dataset and test on a different dataset.
- **Robustness:** compression, resizing, blur, noise, social-media processing, or other relevant corruptions.
- **Efficiency:** latency, throughput, model size, and memory when relevant to the application.

## Scope exclusions until approved

- Deepfake generation or face swapping
- Audio-only deepfake detection
- Audio-visual multimodal training
- Pixel-level manipulation localization
- Continuous live surveillance
- Production/security guarantees
- Training a large foundation model from scratch

## Minimum viable capstone

After the scope is frozen, a complete project should contain:

- one paper/repository reproduced on Kaggle;
- one documented dataset audit and leakage-resistant split;
- one maintained baseline;
- at least one generalization or robustness evaluation;
- one failure-driven improvement and ablation;
- an application-oriented demonstration;
- reproducible configs, compact results, and honest limitations.

## Decision gates

| Gate | Evidence required | Current status |
|---|---|---|
| D1 | Supplied sources are catalogued and compared | Initial audit complete; deep reading in progress |
| D2 | Dataset, task unit, and evaluation protocol are selected | Pending |
| D3 | Baseline runs end to end on Kaggle | Pending |
| D4 | A measurable failure/generalization gap is established | Pending |
| D5 | One improvement is selected from evidence | Pending |
| D6 | Final comparison and demo are complete | Pending |

## Current candidate hierarchy

| Role | Candidate | Rationale | Status |
|---|---|---|---|
| First reproduction | DFD-HR checkpoint evaluation | Official code, released checkpoint, and documented single-GPU test path | Provisional |
| Robustness reference | NTIRE 2026 complementary ensemble | Directly addresses compound degradation and releases inference code/weights, but setup is heavy | Reference / fallback |
| Improvement direction | WGN-style frequency guidance | Lightweight, compression-aware, and reported on a 12 GB GPU | Provisional |
| Future work | Domain-incremental curriculum | Relevant to evolving generators but uses DF40 plus continual-learning machinery | Deferred |
| Interpretability reference | VRAG-DFD | Strong RAG/MLLM reasoning direction but full reproduction requires multi-stage alignment, SFT, and GRPO | Background |

## Rule for the next decision

Do not lock a final method, dataset, or accuracy target before the Week 5 smoke test. Every choice must cite the supplied literature, confirm resource availability, and fit Kaggle constraints.
