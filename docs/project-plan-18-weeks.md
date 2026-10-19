# 18-Week Research and Experiment Plan

**Current week:** Week 5  
**Compute:** Hosted GPU Docker; a new rental is planned for WGN improvement experiments  
**Working direction:** Generalizable and bias-resilient deepfake detection  
**Status key:** `[x]` completed, `[ ]` pending/in progress

## Weekly operating rule

Every week should leave three small artifacts in the repository:

1. a paper note or comparison update;
2. an experiment record, code audit, or hosted-GPU result;
3. a weekly log stating evidence, problems, and the next decision.

Reading and coding run in parallel. A week is complete only when its evidence is recorded; merely downloading papers or starting a notebook does not count.

## Checklist

| Week | Reading and research | Experiment or coding | Required deliverable | Status |
|---:|---|---|---|---|
| 01 | Begin the five papers cited in the progress report: Fairness Analysis, FaceForensics++, FreqDebias, Synergistic Fairness Optimization, and UCF | Extract each paper's problem, dataset, method, metric, and limitation; no model training yet | First-pass notes for all five cited papers | [x] Five-paper reading started<br>[x] Core problems identified |
| 02 | Finish the same five cited papers and connect them through generalization, compression, spectral bias, and demographic fairness | Build the comparison and convert the literature findings into research questions | Progress report covering the five cited papers | [x] Five-paper review completed at report level<br>[x] Report completed |
| 03 | Begin the five newly assigned sources: NTIRE 2026, DFD-HR, VRAG-DFD, domain-incremental curriculum learning, and WGN | Verify official links; inspect task, method, datasets, code, checkpoints, and compute requirements | Initial notes and source-verification record for the new five-paper set | [x] Sources received and verified<br>[x] Initial reading/code audit started |
| **04** | Continue and deepen the same five papers assigned in Week 3, with priority on DFD-HR and WGN | Complete the comparison matrix and rented-GPU feasibility analysis; do not full-train all methods | Five structured notes, paper matrix, and one justified Week 5 reproduction candidate | [ ] Finish five structured paper notes<br>[x] Initial code/compute triage<br>[ ] Confirm Week 5 target |
| **05** | Read the three selected 2026 improvement papers and freeze the WGN improvement hypotheses | Run GPU preflight; verify processed FF++ paths; prepare gradient, curriculum, and temporal pilot configs | WGN improvement plan, pre-rental checklist, and pilot commands | [x] Plan committed; [ ] GPU pilots pending |
| 06 | Read SGFF-Net in depth and implement the gradient-fusion candidate | Run the EXP-003 gradient smoke test, pilot, and final training | EXP-003 gradient variant | [x] Complete |
| 07 | Read difficulty-aware curriculum paper and implement training-only difficulty ranking | Run the EXP-003 curriculum pilot and final training; ensure validation/test data never affect ranking | EXP-003 curriculum variant | [x] Complete |
| 08 | Read temporal consistency paper and implement same-video frame pairing | Run the EXP-003 temporal smoke test, control ablation, pilot, and final training | EXP-003 temporal variant | [x] Complete |
| 09 | Compare the three WGN candidates | Compare full 25-epoch runs under the frozen protocol | Reproduced-reference-versus-candidate screening table | [x] Complete |
| 10 | Review improvement results and failure cases | Evaluate cross-dataset, compression, and degradation robustness | Cross-dataset improvement table | [ ] Degradation variants running |
| 11 | Select the strongest single WGN improvement | Run cross-manipulation and lock the final improvement hypothesis | Error analysis and selected-method decision | [ ] |
| 12 | Read supporting literature for the selected method | Train the selected improvement with the locked 25-epoch protocol | Final candidate checkpoint and metrics | [ ] |
| 13 | Read ablation and reproducibility guidance | Run component ablations and repeat the key comparison with additional seeds when feasible | `EXP-007` ablation table | [ ] |
| 14 | Revisit fairness literature and confirm whether demographic metadata is valid and licensed | If metadata exists, report subgroup AUC/FPR/FNR and gaps; otherwise document why demographic claims cannot be made | `EXP-008` fairness audit or a documented no-claim decision | [ ] |
| 15 | Read deployment/efficiency and calibration references | Measure parameters, inference time, GPU memory, calibration, and robustness of final candidates | `EXP-009` accuracy–robustness–efficiency comparison | [ ] |
| 16 | Review all cited experimental protocols | Run the final locked evaluation without changing settings after seeing test results | Final result tables, plots, configs, and artifact manifest | [ ] |
| 17 | Read related work needed to position the contribution honestly | Build a hosted-GPU batch inference demo; draft methods, experiments, and limitations | Draft report and end-to-end demonstration | [ ] |
| 18 | Final citation and claim audit | Re-run a small reproducibility check from a clean hosted-GPU session; fix documentation only | Final report, presentation, repository release, and reproducibility checklist | [ ] |

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

## Reproduction priority update (Week 5)

The five sources do not receive equal implementation priority:

- **Current execution target:** WGN improvement experiments in `experiments/EXP-003-IMPROVEMENT-WGN/`. The active reproduced WGN reference and checkpoint are stored in `experiments/EXP-002-WGN/reproduction/`; cross-manipulation for that current checkpoint is still pending.
- **Three candidates:** gradient-aware fusion, difficulty-aware curriculum learning, and lightweight temporal consistency.
- **First priority:** gradient-aware fusion because it is the closest architectural extension of WGN's wavelet-guided features.
- **Second priority:** curriculum learning because it changes training only and adds no inference cost.
- **Third priority:** temporal consistency if same-video frame pairing is reliable.
- **Deferred:** DFD-HR and NTIRE reproduction remain future work after the WGN improvement decision.

All runs are gated on environment, data-layout, and legal-access checks. Record every deviation in the weekly log.

## Minimum Week 4 definition of done

- [ ] Write one structured note for each of the five assigned sources.
- [x] Record method, data, metrics, code/weights, and compute requirements in the comparison matrix.
- [ ] Read DFD-HR and WGN in depth; skim the remaining three for problem, method, experiments, and limitations.
- [ ] Confirm legal access to the required dataset on the rented storage.
- [x] Complete the independent WGN reproduction and document its generalization gap.
- [x] Commit the detailed WGN improvement plan.
- [ ] Run the three WGN pilot experiments on the rented GPU.
- [ ] Write `week-04.md` conclusions in the student's own words.

## Scope guardrails

- Do not claim reproduction until the official training/evaluation pipeline runs end to end and exports metrics.
- Do not compare AUC values from different protocols as if they were directly equivalent.
- Do not use demographic labels inferred from appearance as ground truth.
- Do not train an MLLM or a three-model ensemble merely because the paper reports strong results.
- Keep datasets, videos, frames, and checkpoints outside GitHub.
