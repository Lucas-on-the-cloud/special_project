# 18-Week Research and Experiment Plan

**Current week:** Week 4  
**Compute:** Kaggle only  
**Working direction:** Generalizable and bias-resilient deepfake detection  
**Status key:** `[x]` completed, `[ ]` pending/in progress

## Weekly operating rule

Every week should leave three small artifacts in the repository:

1. a paper note or comparison update;
2. an experiment record, code audit, or Kaggle result;
3. a weekly log stating evidence, problems, and the next decision.

Reading and coding run in parallel. A week is complete only when its evidence is recorded; merely downloading papers or starting a notebook does not count.

## Checklist

| Week | Reading and research | Experiment or coding | Required deliverable | Status |
|---:|---|---|---|---|
| 01 | Begin the five papers cited in the progress report: Fairness Analysis, FaceForensics++, FreqDebias, Synergistic Fairness Optimization, and UCF | Extract each paper's problem, dataset, method, metric, and limitation; no model training yet | First-pass notes for all five cited papers | [x] Five-paper reading started<br>[x] Core problems identified |
| 02 | Finish the same five cited papers and connect them through generalization, compression, spectral bias, and demographic fairness | Build the comparison and convert the literature findings into research questions | Progress report covering the five cited papers | [x] Five-paper review completed at report level<br>[x] Report completed |
| 03 | Begin the five newly assigned sources: NTIRE 2026, DFD-HR, VRAG-DFD, domain-incremental curriculum learning, and WGN | Verify official links; inspect task, method, datasets, code, checkpoints, and compute requirements | Initial notes and source-verification record for the new five-paper set | [x] Sources received and verified<br>[x] Initial reading/code audit started |
| **04** | Continue and deepen the same five papers assigned in Week 3, with priority on DFD-HR and WGN | Complete the comparison matrix and Kaggle feasibility analysis; do not full-train all methods | Five structured notes, paper matrix, and one justified Week 5 reproduction candidate | [ ] Finish five structured paper notes<br>[x] Initial code/compute triage<br>[ ] Confirm Week 5 target |
| 05 | Read the selected repository documentation and its closest baseline paper | Obtain approved datasets/weights; build a minimal Kaggle environment and run 10–50 samples | Environment record, dataset-access log, first predictions, go/no-go decision | [ ] |
| 06 | Study the selected dataset protocol and leakage risks | Reproduce pretrained inference or a short smoke evaluation; export AUC/accuracy and runtime | `EXP-001` baseline smoke test and reproducible Kaggle notebook | [ ] |
| 07 | Read the evaluation sections of DFD-HR, WGN, and the chosen baseline | Run the baseline on a fixed validation subset; verify labels and video/frame aggregation | `EXP-002` baseline table with AUC, accuracy, sample count, seed, and timing | [ ] |
| 08 | Read compression/real-world robustness work, including the NTIRE method | Evaluate JPEG/H.264-equivalent image degradation, resize, and blur without retraining | `EXP-003` corruption curve and short failure analysis | [ ] |
| 09 | Read cross-dataset and cross-manipulation protocols | Train/evaluate on the selected source domain and test on at least one held-out domain | `EXP-004` generalization gap table | [ ] |
| 10 | Review errors and the most relevant method family | Stratify false positives/negatives by quality, manipulation, and confidence; select exactly one improvement | Error-analysis report and frozen improvement hypothesis | [ ] |
| 11 | Deep-read the chosen improvement paper; likely WGN/frequency guidance if supported by Week 10 | Implement improvement v1 behind a config flag; run unit and smoke tests | `EXP-005` implementation validation and architecture note | [ ] |
| 12 | Read one supporting paper about the chosen mechanism | Train/tune improvement v1 on a controlled subset using the same baseline protocol | `EXP-006` baseline-vs-improvement result | [ ] |
| 13 | Read ablation and reproducibility guidance | Run ablations that isolate each new component; repeat the key comparison with multiple seeds when feasible | `EXP-007` ablation table with mean/spread or explicit single-run limitation | [ ] |
| 14 | Revisit fairness literature and confirm whether demographic metadata is valid and licensed | If metadata exists, report subgroup AUC/FPR/FNR and gaps; otherwise document why demographic claims cannot be made | `EXP-008` fairness audit or a documented no-claim decision | [ ] |
| 15 | Read deployment/efficiency and calibration references | Measure parameters, inference time, GPU memory, calibration, and robustness of final candidates | `EXP-009` accuracy–robustness–efficiency comparison | [ ] |
| 16 | Review all cited experimental protocols | Run the final locked evaluation without changing settings after seeing test results | Final result tables, plots, configs, and artifact manifest | [ ] |
| 17 | Read related work needed to position the contribution honestly | Build a Kaggle demo or upload/batch inference notebook; draft methods, experiments, limitations | Draft report and end-to-end demonstration | [ ] |
| 18 | Final citation and claim audit | Re-run a small reproducibility check from a clean Kaggle session; fix documentation only | Final report, presentation, repository release, and reproducibility checklist | [ ] |

## Weeks 1–4 literature structure

### Weeks 1–2: five papers cited in the progress report

1. Analyzing Fairness in Deepfake Detection With Massively Annotated Databases
2. FaceForensics++: Learning to Detect Manipulated Facial Images
3. FreqDebias: Towards Generalizable Deepfake Detection via Consistency-Driven Frequency Debiasing
4. Decoupling Bias, Aligning Distributions: Synergistic Fairness Optimization for Deepfake Detection
5. UCF: Unsupervised Cross-domain Deepfake Detection

### Weeks 3–4: five sources newly assigned by the professor

1. NTIRE 2026 Robust Deepfake Detection repository and paper
2. DFD-HR
3. VRAG-DFD
4. Efficient Domain-Incremental Deepfake Detection via Difficulty-Aware Curriculum Learning
5. WGN

## Week 4 decision policy

The five sources do not receive equal implementation priority:

- **Preferred reproduction candidate:** DFD-HR checkpoint evaluation on a small, approved dataset subset.
- **Secondary inference candidate:** NTIRE 2026 ensemble, only if its CUDA/MMCV/FlashAttention environment installs reliably on Kaggle.
- **Preferred improvement candidate:** a WGN-inspired wavelet-guided module, subject to baseline error evidence.
- **Background/future-work sources:** VRAG-DFD and domain-incremental curriculum learning because their full settings are substantially heavier than the first reproduction milestone.

This policy can change after the Week 5 smoke test, but the reason must be recorded in the weekly log.

## Minimum Week 4 definition of done

- [ ] Write one structured note for each of the five assigned sources.
- [x] Record method, data, metrics, code/weights, and compute requirements in the comparison matrix.
- [ ] Read DFD-HR and WGN in depth; skim the remaining three for problem, method, experiments, and limitations.
- [ ] Select one dataset subset that can legally and practically be used on Kaggle.
- [ ] Confirm the Week 5 reproduction target with a fallback.
- [ ] Write `week-04.md` conclusions in the student's own words.

## Scope guardrails

- Do not claim reproduction until a Kaggle notebook runs end to end and exports metrics.
- Do not compare AUC values from different protocols as if they were directly equivalent.
- Do not use demographic labels inferred from appearance as ground truth.
- Do not train an MLLM or a three-model ensemble merely because the paper reports strong results.
- Keep datasets, videos, frames, and checkpoints outside GitHub.
